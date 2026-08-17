"""Application orchestration for comparable quality and human indication."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Callable
from uuid import uuid4

from ...domain.adjustment import N08_FACTOR_KEYS, AdjustmentRunSnapshot, AdjustmentStep
from ...domain.common.numeric import to_decimal
from ...domain.common.rounding import RoundingPolicy, RoundingSource, UNIT_PRICE_TARGET
from ...domain.valuation import (
    ComparableQualityMetrics,
    ComparableReadinessResult,
    GuidanceResult,
    build_minimum_gross_guidance,
    calculate_comparable_quality,
    evaluate_15_percent_readiness,
)
from ...ports.adjustment_persistence import AdjustmentCalculationSnapshotRecord
from ...ports.persistence import AdjustmentDecisionRecord
from ...ports.valuation_persistence import (
    HumanIndicationSnapshotRecord,
    HumanIndicationSourceRecord,
    HumanIndicationUnitOfWork,
)


class ComparableQualityError(Exception):
    """Base application error for E1-PR-003."""


class ComparableQualityValidationError(ComparableQualityError, ValueError):
    pass


class ComparableQualityNotFoundError(ComparableQualityError, LookupError):
    pass


class ComparableQualityConflictError(ComparableQualityError):
    pass


class ComparableQualityPersistenceError(ComparableQualityError):
    pass


@dataclass(frozen=True, slots=True)
class CurrentComparableEvidence:
    comparable_property_id: str
    adjustment_snapshot_id: str
    adjustment_semantic_sha256: str
    quality: ComparableQualityMetrics


@dataclass(frozen=True, slots=True)
class ComparableQualityPreview:
    case_id: str
    comparables: tuple[CurrentComparableEvidence, ...]
    readiness: ComparableReadinessResult
    guidance: GuidanceResult


@dataclass(frozen=True, slots=True)
class PersistedHumanIndication:
    snapshot_id: str
    semantic_sha256: str
    raw_indicated_unit_price_vnd_per_m2: Decimal
    rounded_indicated_unit_price_vnd_per_m2: Decimal
    preview: ComparableQualityPreview


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _new_id() -> str:
    return str(uuid4())


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ComparableQualityValidationError(f"{field_name} must be non-empty")
    return value.strip()


def _json(payload: object) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _sha256_json(payload: object) -> str:
    return hashlib.sha256(_json(payload).encode("utf-8")).hexdigest()


def _decision_set_sha256(records: tuple[AdjustmentDecisionRecord, ...]) -> str:
    payload = [
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
    return _sha256_json(payload)


def _rounding_selected_at_text(rounding_policy: RoundingPolicy) -> str | None:
    if rounding_policy.selected_at is None:
        return None
    return rounding_policy.selected_at.isoformat()


def _run_from_record(record: AdjustmentCalculationSnapshotRecord) -> AdjustmentRunSnapshot:
    try:
        raw_steps = json.loads(record.ordered_steps_json)
    except Exception as exc:
        raise ComparableQualityConflictError(
            "Persisted adjustment snapshot steps are not valid canonical JSON"
        ) from exc
    if not isinstance(raw_steps, list) or len(raw_steps) != len(N08_FACTOR_KEYS):
        raise ComparableQualityConflictError(
            "Persisted adjustment snapshot does not contain the complete C1-C11 graph"
        )
    if tuple(item.get("factor_key") for item in raw_steps if isinstance(item, dict)) != N08_FACTOR_KEYS:
        raise ComparableQualityConflictError(
            "Persisted adjustment snapshot factor order does not match frozen C1-C11"
        )
    try:
        steps = tuple(
            AdjustmentStep(
                factor_key=item["factor_key"],
                selected_rate=to_decimal(
                    item["selected_rate_fraction"],
                    field_name=f"{item['factor_key']}.selected_rate_fraction",
                ),
                amount_base_vnd_per_m2=to_decimal(
                    item["amount_base_vnd_per_m2"],
                    field_name=f"{item['factor_key']}.amount_base_vnd_per_m2",
                ),
                adjustment_amount_vnd_per_m2=to_decimal(
                    item["adjustment_amount_vnd_per_m2"],
                    field_name=f"{item['factor_key']}.adjustment_amount_vnd_per_m2",
                ),
                running_price_vnd_per_m2=to_decimal(
                    item["running_price_vnd_per_m2"],
                    field_name=f"{item['factor_key']}.running_price_vnd_per_m2",
                ),
            )
            for item in raw_steps
        )
        return AdjustmentRunSnapshot(
            normalized_base_price_vnd_per_m2=to_decimal(
                record.normalized_base_price_vnd_per_m2,
                field_name="normalized_base_price_vnd_per_m2",
            ),
            property_adjustment_base_vnd_per_m2=to_decimal(
                record.property_adjustment_base_vnd_per_m2,
                field_name="property_adjustment_base_vnd_per_m2",
            ),
            steps=steps,
            indicated_unit_price_vnd_per_m2=to_decimal(
                record.indicated_unit_price_vnd_per_m2,
                field_name="indicated_unit_price_vnd_per_m2",
            ),
        )
    except ComparableQualityError:
        raise
    except Exception as exc:
        raise ComparableQualityConflictError(
            "Persisted adjustment snapshot contains invalid numeric evidence"
        ) from exc


def _quality_payload(metrics: tuple[ComparableQualityMetrics, ...]) -> list[dict[str, object]]:
    return [
        {
            "comparable_property_id": item.comparable_property_id,
            "indicated_unit_price_vnd_per_m2": format(item.indicated_unit_price_vnd_per_m2, "f"),
            "gross_adjustment_value_vnd_per_m2": format(item.gross_adjustment_value_vnd_per_m2, "f"),
            "net_adjustment_value_vnd_per_m2": format(item.net_adjustment_value_vnd_per_m2, "f"),
            "adjustment_count": item.adjustment_count,
            "min_abs_nonzero_rate": None if item.min_abs_nonzero_rate is None else format(item.min_abs_nonzero_rate, "f"),
            "max_abs_nonzero_rate": None if item.max_abs_nonzero_rate is None else format(item.max_abs_nonzero_rate, "f"),
            "amplitude_percentage_points": item.amplitude_percentage_points,
        }
        for item in metrics
    ]


def _readiness_payload(readiness: ComparableReadinessResult) -> dict[str, object]:
    return {
        "average_indicated_unit_price_vnd_per_m2": format(
            readiness.average_indicated_unit_price_vnd_per_m2, "f"
        ),
        "status": readiness.status,
        "items": [
            {
                "comparable_property_id": item.comparable_property_id,
                "indicated_unit_price_vnd_per_m2": format(item.indicated_unit_price_vnd_per_m2, "f"),
                "deviation_fraction": format(item.deviation_fraction, "f"),
                "within_15_percent": item.within_15_percent,
            }
            for item in readiness.items
        ],
    }


def _guidance_payload(guidance: GuidanceResult) -> dict[str, object]:
    return {
        "kind": guidance.kind,
        "candidate_comparable_ids": list(guidance.candidate_comparable_ids),
        "recommended_comparable_id": guidance.recommended_comparable_id,
        "proposed_indicated_unit_price_vnd_per_m2": (
            None
            if guidance.proposed_indicated_unit_price_vnd_per_m2 is None
            else format(guidance.proposed_indicated_unit_price_vnd_per_m2, "f")
        ),
        "reason_code": guidance.reason_code,
    }


def _source_payload(
    comparables: tuple[CurrentComparableEvidence, ...],
) -> list[dict[str, str]]:
    return [
        {
            "comparable_property_id": item.comparable_property_id,
            "adjustment_snapshot_id": item.adjustment_snapshot_id,
            "adjustment_semantic_sha256": item.adjustment_semantic_sha256,
        }
        for item in sorted(
            comparables,
            key=lambda current: current.comparable_property_id,
        )
    ]


class ComparableQualityService:
    """Derive guidance from current adjustment evidence and persist human authority."""

    def __init__(
        self,
        uow: HumanIndicationUnitOfWork,
        *,
        now: Callable[[], str] = _utc_now,
        new_id: Callable[[], str] = _new_id,
    ) -> None:
        self._uow = uow
        self._now = now
        self._new_id = new_id

    def preview(self, *, case_id: str) -> ComparableQualityPreview:
        case_id = _require_text(case_id, "case_id")
        try:
            with self._uow.atomic():
                return self._build_current_preview(case_id)
        except ComparableQualityError:
            raise
        except Exception as exc:
            raise ComparableQualityPersistenceError(
                "Comparable quality preview could not be read consistently"
            ) from exc

    def confirm_indication(
        self,
        *,
        case_id: str,
        selection_kind: str,
        selected_comparable_property_id: str | None,
        confirmed_by: str,
        reason: str,
        rounding_policy: RoundingPolicy,
    ) -> PersistedHumanIndication:
        case_id = _require_text(case_id, "case_id")
        confirmed_by = _require_text(confirmed_by, "confirmed_by")
        reason = _require_text(reason, "reason")
        if selection_kind not in {"COMPARABLE", "ZERO_GROSS_AVERAGE"}:
            raise ComparableQualityValidationError(
                "selection_kind must be COMPARABLE or ZERO_GROSS_AVERAGE"
            )
        if not isinstance(rounding_policy, RoundingPolicy):
            raise ComparableQualityValidationError("rounding_policy must be RoundingPolicy")
        if rounding_policy.target != UNIT_PRICE_TARGET:
            raise ComparableQualityValidationError(
                "human indicated-price selection requires UNIT_PRICE rounding target"
            )
        if (rounding_policy.profile_id is None) != (
            rounding_policy.profile_version is None
        ):
            raise ComparableQualityValidationError(
                "rounding profile_id/profile_version must be supplied together"
            )

        try:
            with self._uow.atomic():
                case = self._uow.cases.get(case_id)
                if case is None or case.archived_at is not None:
                    raise ComparableQualityNotFoundError("Appraisal case was not found")
                self._validate_rounding_policy_for_case(rounding_policy, case)
                preview = self._build_current_preview(case_id)
                quality_by_id = {
                    item.comparable_property_id: item.quality
                    for item in preview.comparables
                }
                if selection_kind == "COMPARABLE":
                    selected_id = _require_text(
                        selected_comparable_property_id,
                        "selected_comparable_property_id",
                    )
                    if selected_id not in quality_by_id:
                        raise ComparableQualityConflictError(
                            "Selected comparable is not one of the three current case comparables"
                        )
                    raw = quality_by_id[selected_id].indicated_unit_price_vnd_per_m2
                else:
                    if selected_comparable_property_id is not None:
                        raise ComparableQualityValidationError(
                            "ZERO_GROSS_AVERAGE must not carry a selected comparable ID"
                        )
                    if (
                        preview.guidance.kind != "ZERO_GROSS_AVERAGE"
                        or preview.guidance.proposed_indicated_unit_price_vnd_per_m2 is None
                    ):
                        raise ComparableQualityConflictError(
                            "Average indication is allowed only for the frozen zero-gross tie"
                        )
                    selected_id = None
                    raw = preview.guidance.proposed_indicated_unit_price_vnd_per_m2

                rounding = rounding_policy.apply(raw)
                timestamp = self._now()
                snapshot_id = self._new_id()
                metrics = tuple(item.quality for item in preview.comparables)
                quality_payload = _quality_payload(metrics)
                readiness_payload = _readiness_payload(preview.readiness)
                guidance_payload = _guidance_payload(preview.guidance)
                source_payload = _source_payload(preview.comparables)
                rounding_selected_at = _rounding_selected_at_text(rounding_policy)
                semantic_payload = {
                    "case_id": case_id,
                    "selection_kind": selection_kind,
                    "selected_comparable_property_id": selected_id,
                    "raw_indicated_unit_price_vnd_per_m2": format(rounding.raw_value, "f"),
                    "rounded_indicated_unit_price_vnd_per_m2": format(rounding.rounded_value, "f"),
                    "rounding": {
                        "target": rounding_policy.target.key,
                        "mode": rounding_policy.mode.value,
                        "increment_vnd": rounding_policy.increment_vnd,
                        "source": rounding_policy.source.value,
                        "profile_id": rounding_policy.profile_id,
                        "profile_version": rounding_policy.profile_version,
                        "selected_by": rounding_policy.selected_by,
                        "selected_at": rounding_selected_at,
                    },
                    "confirmed_by": confirmed_by,
                    "confirmed_at": timestamp,
                    "reason": reason,
                    "sources": source_payload,
                    "quality": quality_payload,
                    "readiness": readiness_payload,
                    "guidance": guidance_payload,
                }
                semantic_sha256 = _sha256_json(semantic_payload)
                record = HumanIndicationSnapshotRecord(
                    id=snapshot_id,
                    case_id=case_id,
                    selection_kind=selection_kind,
                    selected_comparable_property_id=selected_id,
                    raw_indicated_unit_price_vnd_per_m2=format(rounding.raw_value, "f"),
                    rounded_indicated_unit_price_vnd_per_m2=format(rounding.rounded_value, "f"),
                    rounding_target=rounding_policy.target.key,
                    rounding_mode=rounding_policy.mode.value,
                    rounding_increment_vnd=rounding_policy.increment_vnd,
                    rounding_source=rounding_policy.source.value,
                    rounding_profile_id=rounding_policy.profile_id,
                    rounding_profile_version=rounding_policy.profile_version,
                    rounding_selected_by=rounding_policy.selected_by,
                    rounding_selected_at=rounding_selected_at,
                    confirmed_by=confirmed_by,
                    confirmed_at=timestamp,
                    reason=reason,
                    quality_snapshot_json=_json(quality_payload),
                    readiness_snapshot_json=_json(readiness_payload),
                    guidance_snapshot_json=_json(guidance_payload),
                    semantic_sha256=semantic_sha256,
                )
                self._uow.human_indication_snapshots.add(record)
                for item in preview.comparables:
                    self._uow.human_indication_sources.add(
                        HumanIndicationSourceRecord(
                            indication_snapshot_id=snapshot_id,
                            case_id=case_id,
                            comparable_property_id=item.comparable_property_id,
                            adjustment_snapshot_id=item.adjustment_snapshot_id,
                            adjustment_semantic_sha256=item.adjustment_semantic_sha256,
                        )
                    )
                return PersistedHumanIndication(
                    snapshot_id=snapshot_id,
                    semantic_sha256=semantic_sha256,
                    raw_indicated_unit_price_vnd_per_m2=rounding.raw_value,
                    rounded_indicated_unit_price_vnd_per_m2=rounding.rounded_value,
                    preview=preview,
                )
        except ComparableQualityError:
            raise
        except Exception as exc:
            raise ComparableQualityPersistenceError(
                "Human indication confirmation could not be persisted atomically"
            ) from exc

    def resolve_current_indication(
        self, *, case_id: str
    ) -> HumanIndicationSnapshotRecord:
        """Return the latest human confirmation only when its bound evidence is current."""

        case_id = _require_text(case_id, "case_id")
        try:
            with self._uow.atomic():
                preview = self._build_current_preview(case_id)
                snapshots = self._uow.human_indication_snapshots.list_for_case(case_id)
                if not snapshots:
                    raise ComparableQualityNotFoundError(
                        "No human indicated-price confirmation exists for this case"
                    )
                latest = snapshots[-1]
                sources = self._uow.human_indication_sources.list_for_snapshot(latest.id)
                if len(sources) != 3:
                    raise ComparableQualityConflictError(
                        "Human indication snapshot does not bind exactly three sources"
                    )
                current_ids = {
                    item.comparable_property_id for item in preview.comparables
                }
                if {item.comparable_property_id for item in sources} != current_ids:
                    raise ComparableQualityConflictError(
                        "Human indication snapshot comparable lineage is no longer current"
                    )
                for source in sources:
                    revision, decision_sha = self._current_decision_state(
                        case_id, source.comparable_property_id
                    )
                    adjustment = self._uow.adjustment_calculation_snapshots.get(
                        source.adjustment_snapshot_id
                    )
                    if (
                        adjustment is None
                        or adjustment.case_id != case_id
                        or adjustment.comparable_property_id
                        != source.comparable_property_id
                        or adjustment.semantic_sha256
                        != source.adjustment_semantic_sha256
                        or adjustment.source_data_revision != revision
                        or adjustment.decision_set_sha256 != decision_sha
                    ):
                        raise ComparableQualityConflictError(
                            "Human indicated-price confirmation is stale; human reconfirmation is required"
                        )
                semantic_payload = {
                    "case_id": latest.case_id,
                    "selection_kind": latest.selection_kind,
                    "selected_comparable_property_id": latest.selected_comparable_property_id,
                    "raw_indicated_unit_price_vnd_per_m2": latest.raw_indicated_unit_price_vnd_per_m2,
                    "rounded_indicated_unit_price_vnd_per_m2": latest.rounded_indicated_unit_price_vnd_per_m2,
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
                    "confirmed_by": latest.confirmed_by,
                    "confirmed_at": latest.confirmed_at,
                    "reason": latest.reason,
                    "sources": [
                        {
                            "comparable_property_id": item.comparable_property_id,
                            "adjustment_snapshot_id": item.adjustment_snapshot_id,
                            "adjustment_semantic_sha256": item.adjustment_semantic_sha256,
                        }
                        for item in sorted(
                            sources,
                            key=lambda current: current.comparable_property_id,
                        )
                    ],
                    "quality": json.loads(latest.quality_snapshot_json),
                    "readiness": json.loads(latest.readiness_snapshot_json),
                    "guidance": json.loads(latest.guidance_snapshot_json),
                }
                if _sha256_json(semantic_payload) != latest.semantic_sha256:
                    raise ComparableQualityConflictError(
                        "Human indication semantic evidence hash does not verify"
                    )
                return latest
        except ComparableQualityError:
            raise
        except Exception as exc:
            raise ComparableQualityPersistenceError(
                "Current human indication could not be resolved consistently"
            ) from exc

    def _validate_rounding_policy_for_case(self, rounding_policy, case) -> None:
        case_profile = (case.template_profile_id, case.template_profile_version)
        policy_profile = (
            rounding_policy.profile_id,
            rounding_policy.profile_version,
        )
        if rounding_policy.source is RoundingSource.TEMPLATE_DEFAULT:
            if case_profile[0] is None or case_profile[1] is None:
                raise ComparableQualityConflictError(
                    "Template-default rounding requires a case template profile binding"
                )
            if policy_profile != case_profile:
                raise ComparableQualityConflictError(
                    "Template-default rounding policy does not match the case profile"
                )
        elif rounding_policy.source is RoundingSource.APPLICATION_DEFAULT:
            if case_profile[0] is not None or case_profile[1] is not None:
                raise ComparableQualityConflictError(
                    "Application-default rounding is not allowed when the case has a template profile"
                )
            if policy_profile != (None, None):
                raise ComparableQualityValidationError(
                    "Application-default rounding must not claim a template profile"
                )
        elif rounding_policy.source is RoundingSource.CASE_OVERRIDE:
            if policy_profile != (None, None) and policy_profile != case_profile:
                raise ComparableQualityConflictError(
                    "Case rounding override profile metadata does not match the case"
                )

    def _current_decision_state(
        self, case_id: str, comp_id: str
    ) -> tuple[str, str]:
        state = self._uow.adjustment_source_states.get(case_id, comp_id)
        if state is None:
            raise ComparableQualityConflictError(
                f"{comp_id} has no authoritative adjustment source state"
            )
        authoritative_revision = str(state.source_revision)
        decisions = self._uow.adjustment_decision_queries.list_for_comparable(
            case_id, comp_id
        )
        if tuple(item.factor_key for item in decisions) != N08_FACTOR_KEYS:
            raise ComparableQualityConflictError(
                f"{comp_id} does not have complete C1-C11 decisions"
            )
        for item in decisions:
            if (
                item.review_status != "CURRENT"
                or item.source_data_revision != authoritative_revision
                or not item.selected_explicitly
                or item.selected_rate_pct is None
            ):
                raise ComparableQualityConflictError(
                    f"{comp_id} adjustment decisions are stale or incomplete"
                )
        return authoritative_revision, _decision_set_sha256(decisions)

    def _build_current_preview(self, case_id: str) -> ComparableQualityPreview:
        case = self._uow.cases.get(case_id)
        if case is None or case.archived_at is not None:
            raise ComparableQualityNotFoundError("Appraisal case was not found")
        comparables = tuple(
            item
            for item in self._uow.comparables.list_for_case(case_id)
            if item.archived_at is None
        )
        if len(comparables) != 3 or tuple(item.comparable_order for item in comparables) != (1, 2, 3):
            raise ComparableQualityConflictError(
                "Walking Skeleton quality requires current TSSS01/TSSS02/TSSS03"
            )

        evidence: list[CurrentComparableEvidence] = []
        for comparable in comparables:
            comp_id = comparable.property_id
            authoritative_revision, current_sha = self._current_decision_state(
                case_id, comp_id
            )
            snapshots = self._uow.adjustment_calculation_snapshots.list_for_comparable(
                case_id, comp_id
            )
            eligible = tuple(
                item
                for item in snapshots
                if item.source_data_revision == authoritative_revision
                and item.decision_set_sha256 == current_sha
            )
            if not eligible:
                raise ComparableQualityConflictError(
                    f"{comp_id} requires a fresh adjustment calculation snapshot"
                )
            snapshot = eligible[-1]
            run = _run_from_record(snapshot)
            quality = calculate_comparable_quality(
                comparable_property_id=comp_id,
                run=run,
            )
            evidence.append(
                CurrentComparableEvidence(
                    comparable_property_id=comp_id,
                    adjustment_snapshot_id=snapshot.id,
                    adjustment_semantic_sha256=snapshot.semantic_sha256,
                    quality=quality,
                )
            )

        metrics = tuple(item.quality for item in evidence)
        readiness = evaluate_15_percent_readiness(metrics)
        guidance = build_minimum_gross_guidance(metrics)
        return ComparableQualityPreview(
            case_id=case_id,
            comparables=tuple(evidence),
            readiness=readiness,
            guidance=guidance,
        )
