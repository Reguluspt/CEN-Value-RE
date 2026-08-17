"""Application orchestration for E1-PR-004 land and final valuation composition."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Callable
from uuid import uuid4

from ...domain.adjustment import N08_FACTOR_KEYS
from ...domain.common.numeric import to_decimal
from ...domain.common.rounding import RoundingPolicy, RoundingSource, TOTAL_VALUE_TARGET
from ...domain.valuation import LandComponentInput, compose_final_valuation
from ...ports.excel import TemplateRoundingDefaultResolver
from ...ports.persistence import AdjustmentDecisionRecord, LandValuationComponentRecord
from ...ports.valuation_persistence import (
    ConstructionAggregateInputRecord,
    FinalValuationLandSourceRecord,
    FinalValuationSnapshotRecord,
    FinalValuationUnitOfWork,
    HumanIndicationSnapshotRecord,
)


SUPPLIED_PRECOMPUTED = "SUPPLIED_PRECOMPUTED"


class FinalValuationError(Exception):
    """Base application error for E1-PR-004."""


class FinalValuationValidationError(FinalValuationError, ValueError):
    pass


class FinalValuationNotFoundError(FinalValuationError, LookupError):
    pass


class FinalValuationConflictError(FinalValuationError):
    pass


class FinalValuationPersistenceError(FinalValuationError):
    pass


@dataclass(frozen=True, slots=True)
class PersistedFinalValuation:
    snapshot_id: str
    semantic_sha256: str
    compliant_residential_land_value_vnd: Decimal
    other_recognized_land_value_vnd: Decimal
    recognized_land_value_vnd: Decimal
    construction_value_total_vnd: Decimal
    total_value_before_rounding_vnd: Decimal
    final_appraised_value_vnd: Decimal


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _new_id() -> str:
    return str(uuid4())


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FinalValuationValidationError(f"{field_name} must be non-empty")
    return value.strip()


def _json(payload: object) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _sha(payload: object) -> str:
    return hashlib.sha256(_json(payload).encode("utf-8")).hexdigest()


def _decision_sha(records: tuple[AdjustmentDecisionRecord, ...]) -> str:
    return _sha(
        [
            {
                "id": item.id,
                "factor_key": item.factor_key,
                "selected_rate_pct": item.selected_rate_pct,
                "selected_explicitly": item.selected_explicitly,
                "source_data_revision": item.source_data_revision,
                "review_status": item.review_status,
                "selected_at": item.selected_at,
                "version": item.version,
            }
            for item in records
        ]
    )


def _rounding_selected_at(policy: RoundingPolicy) -> str | None:
    return policy.selected_at.isoformat() if policy.selected_at is not None else None


def _component_source_payload(record: LandValuationComponentRecord) -> dict[str, object]:
    return {
        "id": record.id,
        "property_id": record.property_id,
        "parcel_id": record.parcel_id,
        "component_order": record.component_order,
        "planning_status": record.planning_status,
        "area_m2": record.area_m2,
        "valuation_basis": record.valuation_basis,
        "unit_price_vnd_per_m2": record.unit_price_vnd_per_m2,
        "include_in_final_value": record.include_in_final_value,
        "note": record.note,
        "policy_version": record.policy_version,
        "archived_at": record.archived_at,
    }


def _human_semantic_payload(snapshot, sources) -> dict[str, object]:
    return {
        "case_id": snapshot.case_id,
        "selection_kind": snapshot.selection_kind,
        "selected_comparable_property_id": snapshot.selected_comparable_property_id,
        "raw_indicated_unit_price_vnd_per_m2": snapshot.raw_indicated_unit_price_vnd_per_m2,
        "rounded_indicated_unit_price_vnd_per_m2": snapshot.rounded_indicated_unit_price_vnd_per_m2,
        "rounding": {
            "target": snapshot.rounding_target,
            "mode": snapshot.rounding_mode,
            "increment_vnd": snapshot.rounding_increment_vnd,
            "source": snapshot.rounding_source,
            "profile_id": snapshot.rounding_profile_id,
            "profile_version": snapshot.rounding_profile_version,
            "selected_by": snapshot.rounding_selected_by,
            "selected_at": snapshot.rounding_selected_at,
        },
        "confirmed_by": snapshot.confirmed_by,
        "confirmed_at": snapshot.confirmed_at,
        "reason": snapshot.reason,
        "sources": [
            {
                "comparable_property_id": item.comparable_property_id,
                "adjustment_snapshot_id": item.adjustment_snapshot_id,
                "adjustment_semantic_sha256": item.adjustment_semantic_sha256,
            }
            for item in sorted(sources, key=lambda current: current.comparable_property_id)
        ],
        "quality": json.loads(snapshot.quality_snapshot_json),
        "readiness": json.loads(snapshot.readiness_snapshot_json),
        "guidance": json.loads(snapshot.guidance_snapshot_json),
    }


class FinalValuationService:
    """Bind current valuation evidence and persist immutable final results."""

    def __init__(
        self,
        uow: FinalValuationUnitOfWork,
        *,
        template_rounding_defaults: TemplateRoundingDefaultResolver | None = None,
        now: Callable[[], str] = _utc_now,
        new_id: Callable[[], str] = _new_id,
    ) -> None:
        self._uow = uow
        self._template_rounding_defaults = template_rounding_defaults
        self._now = now
        self._new_id = new_id

    def bind_supplied_construction_aggregate(
        self,
        *,
        case_id: str,
        amount_vnd,
        evidence_ref: str,
        supplied_by: str,
    ) -> ConstructionAggregateInputRecord:
        case_id = _require_text(case_id, "case_id")
        evidence_ref = _require_text(evidence_ref, "evidence_ref")
        supplied_by = _require_text(supplied_by, "supplied_by")
        amount = to_decimal(amount_vnd, field_name="amount_vnd")
        if amount < 0:
            raise FinalValuationValidationError("amount_vnd must not be negative")
        amount_text = format(amount, "f")
        try:
            with self._uow.atomic():
                case = self._uow.cases.get(case_id)
                if case is None or case.archived_at is not None:
                    raise FinalValuationNotFoundError("Appraisal case was not found")
                current = self._uow.construction_aggregate_inputs.latest_for_case(case_id)
                if (
                    current is not None
                    and current.amount_vnd == amount_text
                    and current.evidence_ref == evidence_ref
                    and current.source_kind == SUPPLIED_PRECOMPUTED
                ):
                    return current
                revision = 1 if current is None else current.revision + 1
                timestamp = self._now()
                record_id = self._new_id()
                payload = {
                    "id": record_id,
                    "case_id": case_id,
                    "revision": revision,
                    "amount_vnd": amount_text,
                    "evidence_ref": evidence_ref,
                    "source_kind": SUPPLIED_PRECOMPUTED,
                    "supplied_by": supplied_by,
                    "supplied_at": timestamp,
                }
                record = ConstructionAggregateInputRecord(
                    id=record_id,
                    case_id=case_id,
                    revision=revision,
                    amount_vnd=amount_text,
                    evidence_ref=evidence_ref,
                    source_kind=SUPPLIED_PRECOMPUTED,
                    supplied_by=supplied_by,
                    supplied_at=timestamp,
                    semantic_sha256=_sha(payload),
                )
                self._uow.construction_aggregate_inputs.add(record)
                return record
        except FinalValuationError:
            raise
        except Exception as exc:
            raise FinalValuationPersistenceError(
                "Supplied construction aggregate could not be bound atomically"
            ) from exc

    def compose(
        self,
        *,
        case_id: str,
        total_value_rounding_policy: RoundingPolicy,
    ) -> PersistedFinalValuation:
        case_id = _require_text(case_id, "case_id")
        if not isinstance(total_value_rounding_policy, RoundingPolicy):
            raise FinalValuationValidationError(
                "total_value_rounding_policy must be RoundingPolicy"
            )
        if total_value_rounding_policy.target != TOTAL_VALUE_TARGET:
            raise FinalValuationValidationError(
                "final valuation requires TOTAL_VALUE rounding target"
            )
        try:
            with self._uow.atomic():
                case = self._uow.cases.get(case_id)
                if case is None or case.archived_at is not None:
                    raise FinalValuationNotFoundError("Appraisal case was not found")
                if not case.appraisal_date:
                    raise FinalValuationConflictError(
                        "Final valuation requires the persisted appraisal date"
                    )
                subject = self._uow.subjects.get_for_case(case_id)
                if subject is None or subject.archived_at is not None:
                    raise FinalValuationNotFoundError("Current subject property was not found")
                self._validate_rounding_policy_for_case(total_value_rounding_policy, case)
                human = self._resolve_current_human_indication(case_id)
                construction = self._uow.construction_aggregate_inputs.latest_for_case(case_id)
                if construction is None:
                    raise FinalValuationConflictError(
                        "Final valuation requires a supplied construction aggregate input"
                    )
                construction_payload = {
                    "id": construction.id,
                    "case_id": construction.case_id,
                    "revision": construction.revision,
                    "amount_vnd": construction.amount_vnd,
                    "evidence_ref": construction.evidence_ref,
                    "source_kind": construction.source_kind,
                    "supplied_by": construction.supplied_by,
                    "supplied_at": construction.supplied_at,
                }
                if _sha(construction_payload) != construction.semantic_sha256:
                    raise FinalValuationConflictError(
                        "Supplied construction aggregate semantic hash does not verify"
                    )

                persisted_components = tuple(
                    item
                    for item in self._uow.land_valuation_components.list_for_property(
                        subject.property_id
                    )
                    if item.archived_at is None and item.include_in_final_value
                )
                if not persisted_components:
                    raise FinalValuationConflictError(
                        "No included land valuation components exist for the subject"
                    )
                land_inputs = tuple(
                    LandComponentInput.build(
                        component_id=item.id,
                        component_order=item.component_order,
                        planning_status=item.planning_status,
                        area_m2=item.area_m2,
                        valuation_basis=item.valuation_basis,
                        include_in_final_value=item.include_in_final_value,
                        explicit_unit_price_vnd_per_m2=item.unit_price_vnd_per_m2,
                        policy_version=item.policy_version,
                        note=item.note,
                        parcel_id=item.parcel_id,
                    )
                    for item in persisted_components
                )
                composition = compose_final_valuation(
                    rounded_human_indication_vnd_per_m2=human.rounded_indicated_unit_price_vnd_per_m2,
                    land_components=land_inputs,
                    supplied_construction_aggregate_vnd=construction.amount_vnd,
                    total_value_rounding_policy=total_value_rounding_policy,
                )
                source_by_id = {item.id: item for item in persisted_components}
                land_payload = [
                    {
                        "component_id": item.component_id,
                        "component_order": item.component_order,
                        "planning_status": item.planning_status,
                        "area_m2": format(item.area_m2, "f"),
                        "valuation_basis": item.valuation_basis,
                        "effective_unit_price_vnd_per_m2": format(
                            item.effective_unit_price_vnd_per_m2, "f"
                        ),
                        "amount_vnd": format(item.amount_vnd, "f"),
                        "policy_version": item.policy_version,
                        "note": item.note,
                        "parcel_id": item.parcel_id,
                        "source_semantic_sha256": _sha(
                            _component_source_payload(source_by_id[item.component_id])
                        ),
                    }
                    for item in composition.land_components
                ]
                land_json = _json(land_payload)
                land_sha = hashlib.sha256(land_json.encode("utf-8")).hexdigest()
                timestamp = self._now()
                snapshot_id = self._new_id()
                rounding_selected_at = _rounding_selected_at(total_value_rounding_policy)
                semantic_payload = {
                    "case_id": case_id,
                    "subject_property_id": subject.property_id,
                    "appraisal_date": case.appraisal_date,
                    "human_indication_snapshot_id": human.id,
                    "human_indication_semantic_sha256": human.semantic_sha256,
                    "rounded_indicated_unit_price_vnd_per_m2": human.rounded_indicated_unit_price_vnd_per_m2,
                    "land_components": land_payload,
                    "land_components_sha256": land_sha,
                    "compliant_residential_land_value_vnd": format(
                        composition.compliant_residential_land_value_vnd, "f"
                    ),
                    "other_recognized_land_value_vnd": format(
                        composition.other_recognized_land_value_vnd, "f"
                    ),
                    "recognized_land_value_vnd": format(
                        composition.recognized_land_value_vnd, "f"
                    ),
                    "construction_aggregate_input_id": construction.id,
                    "construction_aggregate_semantic_sha256": construction.semantic_sha256,
                    "construction_value_total_vnd": format(
                        composition.construction_value_total_vnd, "f"
                    ),
                    "total_value_before_rounding_vnd": format(
                        composition.total_value_before_rounding_vnd, "f"
                    ),
                    "final_appraised_value_vnd": format(
                        composition.final_appraised_value_vnd, "f"
                    ),
                    "rounding": {
                        "target": total_value_rounding_policy.target.key,
                        "mode": total_value_rounding_policy.mode.value,
                        "increment_vnd": total_value_rounding_policy.increment_vnd,
                        "source": total_value_rounding_policy.source.value,
                        "profile_id": total_value_rounding_policy.profile_id,
                        "profile_version": total_value_rounding_policy.profile_version,
                        "selected_by": total_value_rounding_policy.selected_by,
                        "selected_at": rounding_selected_at,
                    },
                    "composed_at": timestamp,
                }
                semantic_sha = _sha(semantic_payload)
                record = FinalValuationSnapshotRecord(
                    id=snapshot_id,
                    case_id=case_id,
                    subject_property_id=subject.property_id,
                    appraisal_date=case.appraisal_date,
                    human_indication_snapshot_id=human.id,
                    human_indication_semantic_sha256=human.semantic_sha256,
                    rounded_indicated_unit_price_vnd_per_m2=human.rounded_indicated_unit_price_vnd_per_m2,
                    land_components_json=land_json,
                    land_components_sha256=land_sha,
                    compliant_residential_land_value_vnd=format(
                        composition.compliant_residential_land_value_vnd, "f"
                    ),
                    other_recognized_land_value_vnd=format(
                        composition.other_recognized_land_value_vnd, "f"
                    ),
                    recognized_land_value_vnd=format(
                        composition.recognized_land_value_vnd, "f"
                    ),
                    construction_aggregate_input_id=construction.id,
                    construction_aggregate_semantic_sha256=construction.semantic_sha256,
                    construction_value_total_vnd=format(
                        composition.construction_value_total_vnd, "f"
                    ),
                    total_value_before_rounding_vnd=format(
                        composition.total_value_before_rounding_vnd, "f"
                    ),
                    final_appraised_value_vnd=format(
                        composition.final_appraised_value_vnd, "f"
                    ),
                    rounding_target=total_value_rounding_policy.target.key,
                    rounding_mode=total_value_rounding_policy.mode.value,
                    rounding_increment_vnd=total_value_rounding_policy.increment_vnd,
                    rounding_source=total_value_rounding_policy.source.value,
                    rounding_profile_id=total_value_rounding_policy.profile_id,
                    rounding_profile_version=total_value_rounding_policy.profile_version,
                    rounding_selected_by=total_value_rounding_policy.selected_by,
                    rounding_selected_at=rounding_selected_at,
                    composed_at=timestamp,
                    semantic_sha256=semantic_sha,
                )
                self._uow.final_valuation_snapshots.add(record)
                for source in persisted_components:
                    if source.id not in {item.component_id for item in composition.land_components}:
                        continue
                    self._uow.final_valuation_land_sources.add(
                        FinalValuationLandSourceRecord(
                            valuation_snapshot_id=snapshot_id,
                            case_id=case_id,
                            subject_property_id=subject.property_id,
                            land_component_id=source.id,
                            component_semantic_sha256=_sha(
                                _component_source_payload(source)
                            ),
                        )
                    )
                return PersistedFinalValuation(
                    snapshot_id=snapshot_id,
                    semantic_sha256=semantic_sha,
                    compliant_residential_land_value_vnd=composition.compliant_residential_land_value_vnd,
                    other_recognized_land_value_vnd=composition.other_recognized_land_value_vnd,
                    recognized_land_value_vnd=composition.recognized_land_value_vnd,
                    construction_value_total_vnd=composition.construction_value_total_vnd,
                    total_value_before_rounding_vnd=composition.total_value_before_rounding_vnd,
                    final_appraised_value_vnd=composition.final_appraised_value_vnd,
                )
        except FinalValuationError:
            raise
        except Exception as exc:
            raise FinalValuationPersistenceError(
                "Final valuation could not be composed and persisted atomically"
            ) from exc

    def resolve_current(self, *, case_id: str) -> FinalValuationSnapshotRecord:
        case_id = _require_text(case_id, "case_id")
        try:
            with self._uow.atomic():
                human = self._resolve_current_human_indication(case_id)
                subject = self._uow.subjects.get_for_case(case_id)
                if subject is None or subject.archived_at is not None:
                    raise FinalValuationConflictError("Subject property is not current")
                construction = self._uow.construction_aggregate_inputs.latest_for_case(case_id)
                snapshots = self._uow.final_valuation_snapshots.list_for_case(case_id)
                if construction is None or not snapshots:
                    raise FinalValuationNotFoundError("No current final valuation exists")
                latest = snapshots[-1]
                if (
                    latest.subject_property_id != subject.property_id
                    or latest.human_indication_snapshot_id != human.id
                    or latest.human_indication_semantic_sha256 != human.semantic_sha256
                    or latest.construction_aggregate_input_id != construction.id
                    or latest.construction_aggregate_semantic_sha256 != construction.semantic_sha256
                ):
                    raise FinalValuationConflictError(
                        "Final valuation inputs changed; recomposition is required"
                    )
                current_components = tuple(
                    item
                    for item in self._uow.land_valuation_components.list_for_property(
                        subject.property_id
                    )
                    if item.archived_at is None and item.include_in_final_value
                )
                sources = self._uow.final_valuation_land_sources.list_for_snapshot(latest.id)
                expected = {
                    item.id: _sha(_component_source_payload(item))
                    for item in current_components
                }
                actual = {
                    item.land_component_id: item.component_semantic_sha256
                    for item in sources
                }
                if actual != expected:
                    raise FinalValuationConflictError(
                        "Land composition inputs changed; recomposition is required"
                    )
                try:
                    land_payload = json.loads(latest.land_components_json)
                except Exception as exc:
                    raise FinalValuationConflictError(
                        "Final valuation land snapshot is not valid JSON"
                    ) from exc
                if _sha(land_payload) != latest.land_components_sha256:
                    raise FinalValuationConflictError(
                        "Final valuation land snapshot hash does not verify"
                    )
                semantic_payload = {
                    "case_id": latest.case_id,
                    "subject_property_id": latest.subject_property_id,
                    "appraisal_date": latest.appraisal_date,
                    "human_indication_snapshot_id": latest.human_indication_snapshot_id,
                    "human_indication_semantic_sha256": latest.human_indication_semantic_sha256,
                    "rounded_indicated_unit_price_vnd_per_m2": latest.rounded_indicated_unit_price_vnd_per_m2,
                    "land_components": land_payload,
                    "land_components_sha256": latest.land_components_sha256,
                    "compliant_residential_land_value_vnd": latest.compliant_residential_land_value_vnd,
                    "other_recognized_land_value_vnd": latest.other_recognized_land_value_vnd,
                    "recognized_land_value_vnd": latest.recognized_land_value_vnd,
                    "construction_aggregate_input_id": latest.construction_aggregate_input_id,
                    "construction_aggregate_semantic_sha256": latest.construction_aggregate_semantic_sha256,
                    "construction_value_total_vnd": latest.construction_value_total_vnd,
                    "total_value_before_rounding_vnd": latest.total_value_before_rounding_vnd,
                    "final_appraised_value_vnd": latest.final_appraised_value_vnd,
                    "rounding": {
                        "target": latest.rounding_target,
                        "mode": latest.rounding_mode,
                        "increment_vnd": latest.rounding_increment_vnd,
                        "source": latest.rounding_source,
                        "profile_id": latest.rounding_profile_id,
                        "profile_version": latest.rounding_profile_version,
                        "selected_by": latest.rounding_selected_by,
                        "selected_at": latest.rounding_selected_at,
                    },
                    "composed_at": latest.composed_at,
                }
                if _sha(semantic_payload) != latest.semantic_sha256:
                    raise FinalValuationConflictError(
                        "Final valuation semantic evidence hash does not verify"
                    )
                return latest
        except FinalValuationError:
            raise
        except Exception as exc:
            raise FinalValuationPersistenceError(
                "Current final valuation could not be resolved consistently"
            ) from exc

    def _resolve_current_human_indication(
        self, case_id: str
    ) -> HumanIndicationSnapshotRecord:
        snapshots = self._uow.human_indication_snapshots.list_for_case(case_id)
        if not snapshots:
            raise FinalValuationConflictError(
                "Final valuation requires a current human indicated-price confirmation"
            )
        latest = snapshots[-1]
        sources = self._uow.human_indication_sources.list_for_snapshot(latest.id)
        if len(sources) != 3:
            raise FinalValuationConflictError(
                "Human indication snapshot does not bind exactly three sources"
            )
        for source in sources:
            state = self._uow.adjustment_source_states.get(
                case_id, source.comparable_property_id
            )
            if state is None:
                raise FinalValuationConflictError(
                    "Human indication source has no current adjustment source state"
                )
            decisions = self._uow.adjustment_decision_queries.list_for_comparable(
                case_id, source.comparable_property_id
            )
            if (
                len(decisions) != len(N08_FACTOR_KEYS)
                or tuple(item.factor_key for item in decisions) != N08_FACTOR_KEYS
                or any(
                    item.review_status != "CURRENT"
                    or not item.selected_explicitly
                    or item.selected_rate_pct is None
                    or item.source_data_revision != str(state.source_revision)
                    for item in decisions
                )
            ):
                raise FinalValuationConflictError(
                    "Human indication source decisions are no longer current"
                )
            adjustment = self._uow.adjustment_calculation_snapshots.get(
                source.adjustment_snapshot_id
            )
            if (
                adjustment is None
                or adjustment.case_id != case_id
                or adjustment.comparable_property_id != source.comparable_property_id
                or adjustment.semantic_sha256 != source.adjustment_semantic_sha256
                or adjustment.source_data_revision != str(state.source_revision)
                or adjustment.decision_set_sha256 != _decision_sha(decisions)
            ):
                raise FinalValuationConflictError(
                    "Human indication source evidence is stale"
                )
        if _sha(_human_semantic_payload(latest, sources)) != latest.semantic_sha256:
            raise FinalValuationConflictError(
                "Human indication semantic evidence hash does not verify"
            )
        return latest

    def _validate_rounding_policy_for_case(self, policy, case) -> None:
        case_profile = (case.template_profile_id, case.template_profile_version)
        policy_profile = (policy.profile_id, policy.profile_version)
        if policy.source is RoundingSource.TEMPLATE_DEFAULT:
            if case_profile[0] is None or case_profile[1] is None:
                raise FinalValuationConflictError(
                    "Template-default rounding requires a case template profile binding"
                )
            if policy_profile != case_profile:
                raise FinalValuationConflictError(
                    "Template-default rounding policy does not match the case profile"
                )
            if self._template_rounding_defaults is None:
                raise FinalValuationConflictError(
                    "Template-default rounding requires a trusted template-profile resolver"
                )
            trusted = self._template_rounding_defaults.resolve(
                profile_id=case_profile[0],
                profile_version=case_profile[1],
                target=TOTAL_VALUE_TARGET.key,
            )
            if trusted is None:
                raise FinalValuationConflictError(
                    "Case template profile does not declare a trusted TOTAL_VALUE rounding default"
                )
            if (
                policy.profile_id,
                policy.profile_version,
                policy.target.key,
                policy.mode.value,
                policy.increment_vnd,
            ) != (
                trusted.profile_id,
                trusted.profile_version,
                trusted.target,
                trusted.mode,
                trusted.increment_vnd,
            ):
                raise FinalValuationConflictError(
                    "TOTAL_VALUE template-default rounding does not match the trusted profile default"
                )
        elif policy.source is RoundingSource.APPLICATION_DEFAULT:
            if case_profile[0] is not None or case_profile[1] is not None:
                raise FinalValuationConflictError(
                    "Application-default rounding is not allowed for a profiled case"
                )
            if policy_profile != (None, None):
                raise FinalValuationValidationError(
                    "Application-default rounding must not claim a template profile"
                )
        elif policy.source is RoundingSource.CASE_OVERRIDE:
            if policy_profile != (None, None) and policy_profile != case_profile:
                raise FinalValuationConflictError(
                    "Case rounding override profile metadata does not match the case"
                )
