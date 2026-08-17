"""Application orchestration for human-selected market adjustment runs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from decimal import Decimal
from typing import Callable
from uuid import uuid4

from ...domain.adjustment import (
    N08_FACTOR_KEYS,
    AdjustmentRunSnapshot,
    SelectedAdjustmentDecision,
    calculate_adjustment_run,
)
from ...domain.common.numeric import DecimalInput, to_decimal
from ...ports.adjustment_persistence import (
    AdjustmentCalculationSnapshotRecord,
    AdjustmentPersistenceUnitOfWork,
    AdjustmentSelectionAuditRecord,
)
from ...ports.adjustment_source import AdjustmentSourceStateRecord
from ...ports.persistence import AdjustmentDecisionRecord


class MarketAdjustmentError(Exception):
    """Base application error for E1-PR-002."""


class MarketAdjustmentValidationError(MarketAdjustmentError, ValueError):
    pass


class MarketAdjustmentNotFoundError(MarketAdjustmentError, LookupError):
    pass


class MarketAdjustmentConflictError(MarketAdjustmentError):
    pass


class MarketAdjustmentPersistenceError(MarketAdjustmentError):
    pass


@dataclass(frozen=True, slots=True)
class PersistedAdjustmentRun:
    snapshot_id: str
    semantic_sha256: str
    decision_set_sha256: str
    result: AdjustmentRunSnapshot


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _new_id() -> str:
    return str(uuid4())


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MarketAdjustmentValidationError(f"{field_name} must be non-empty")
    return value.strip()


def _decimal_text(value: DecimalInput, field_name: str) -> str:
    decimal_value = to_decimal(value, field_name=field_name)
    if isinstance(value, str):
        return value.strip()
    return format(decimal_value, "f")


def _sha256_json(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _decision_fingerprint(records: tuple[AdjustmentDecisionRecord, ...]) -> tuple[tuple[object, ...], ...]:
    return tuple(
        (
            item.id,
            item.case_id,
            item.comparable_property_id,
            item.factor_key,
            item.selected_rate_pct,
            item.selected_explicitly,
            item.source_data_revision,
            item.review_status,
            item.selected_at,
            item.version,
            item.archived_at,
        )
        for item in records
    )


class MarketAdjustmentService:
    """Persist human decisions and calculate only against authoritative source state."""

    def __init__(
        self,
        uow: AdjustmentPersistenceUnitOfWork,
        *,
        now: Callable[[], str] = _utc_now,
        new_id: Callable[[], str] = _new_id,
    ) -> None:
        self._uow = uow
        self._now = now
        self._new_id = new_id

    def bind_normalized_base(
        self,
        *,
        case_id: str,
        comparable_property_id: str,
        normalized_base_price_vnd_per_m2: DecimalInput,
        evidence_ref: str,
    ) -> AdjustmentSourceStateRecord:
        """Bind a supplied/derived P0 to the current authoritative source revision.

        E1-PR-002 does not invent the CTXD engine. P0 may therefore be supplied
        or derived upstream, but it must be persisted with explicit evidence and
        an exact authoritative source revision before any adjustment run.
        """

        case_id = _require_text(case_id, "case_id")
        comparable_property_id = _require_text(
            comparable_property_id, "comparable_property_id"
        )
        evidence_ref = _require_text(evidence_ref, "evidence_ref")
        base_text = _decimal_text(
            normalized_base_price_vnd_per_m2,
            "normalized_base_price_vnd_per_m2",
        )
        try:
            with self._uow.atomic():
                self._require_case_and_comparable(case_id, comparable_property_id)
                state = self._uow.adjustment_source_states.ensure(
                    case_id, comparable_property_id, self._now()
                )
                return self._uow.adjustment_source_states.bind_normalized_base(
                    case_id=case_id,
                    comparable_property_id=comparable_property_id,
                    expected_source_revision=state.source_revision,
                    normalized_base_price_vnd_per_m2=base_text,
                    evidence_ref=evidence_ref,
                    updated_at=self._now(),
                )
        except MarketAdjustmentError:
            raise
        except Exception as exc:
            raise MarketAdjustmentPersistenceError(
                "Normalized adjustment base could not be bound to current source state"
            ) from exc

    def select_rate(
        self,
        *,
        case_id: str,
        comparable_property_id: str,
        factor_key: str,
        selected_rate: DecimalInput,
        selected_by: str,
        source_data_revision: str | None = None,
    ) -> AdjustmentDecisionRecord:
        case_id = _require_text(case_id, "case_id")
        comparable_property_id = _require_text(
            comparable_property_id, "comparable_property_id"
        )
        selected_by = _require_text(selected_by, "selected_by")
        if factor_key not in N08_FACTOR_KEYS:
            raise MarketAdjustmentValidationError(
                f"unsupported adjustment factor key: {factor_key!r}"
            )
        rate_text = _decimal_text(selected_rate, "selected_rate")
        try:
            with self._uow.atomic():
                self._require_case_and_comparable(case_id, comparable_property_id)
                state = self._uow.adjustment_source_states.ensure(
                    case_id, comparable_property_id, self._now()
                )
                authoritative_revision = str(state.source_revision)
                if source_data_revision is not None and str(source_data_revision) != authoritative_revision:
                    raise MarketAdjustmentConflictError(
                        "Caller source-data revision does not match authoritative current revision"
                    )
                existing = next(
                    (
                        item
                        for item in self._uow.adjustment_decision_queries.list_for_comparable(
                            case_id, comparable_property_id
                        )
                        if item.factor_key == factor_key
                    ),
                    None,
                )
                timestamp = self._now()
                decision = AdjustmentDecisionRecord(
                    id=existing.id if existing else self._new_id(),
                    case_id=case_id,
                    comparable_property_id=comparable_property_id,
                    factor_key=factor_key,
                    selected_explicitly=True,
                    source_data_revision=authoritative_revision,
                    review_status="CURRENT",
                    suggested_rate_pct=existing.suggested_rate_pct if existing else None,
                    selected_rate_pct=rate_text,
                    approved_rate_pct=existing.approved_rate_pct if existing else None,
                    selected_at=timestamp,
                    version=(existing.version + 1) if existing else 1,
                    archived_at=None,
                )
                if existing is None:
                    self._uow.adjustment_decisions.put(decision)
                elif not self._uow.adjustment_decisions.put_if_version(
                    decision, expected_version=existing.version
                ):
                    raise MarketAdjustmentConflictError(
                        "Adjustment decision changed concurrently; re-read before selecting"
                    )
                self._uow.adjustment_selection_audit.add(
                    AdjustmentSelectionAuditRecord(
                        id=self._new_id(),
                        adjustment_decision_id=decision.id,
                        case_id=case_id,
                        comparable_property_id=comparable_property_id,
                        factor_key=factor_key,
                        event_kind="SELECTED",
                        selected_rate_pct=rate_text,
                        selected_explicitly=True,
                        selected_by=selected_by,
                        selected_at=timestamp,
                        source_data_revision=authoritative_revision,
                        review_status="CURRENT",
                    )
                )
                return decision
        except MarketAdjustmentError:
            raise
        except Exception as exc:
            raise MarketAdjustmentPersistenceError(
                "Adjustment selection could not be persisted atomically"
            ) from exc

    def mark_source_data_changed(
        self,
        *,
        case_id: str,
        comparable_property_id: str,
        new_source_data_revision: str | None = None,
    ) -> tuple[AdjustmentDecisionRecord, ...]:
        """Reconcile decisions with authoritative state; caller cannot advance revision.

        Canonical source writes advance ``adjustment_source_state`` through DB
        triggers in the same source transaction. This method only observes that
        authoritative revision and applies CAS staleness if a non-triggering
        adapter ever needs reconciliation.
        """

        case_id = _require_text(case_id, "case_id")
        comparable_property_id = _require_text(
            comparable_property_id, "comparable_property_id"
        )
        try:
            with self._uow.atomic():
                self._require_case_and_comparable(case_id, comparable_property_id)
                state = self._uow.adjustment_source_states.ensure(
                    case_id, comparable_property_id, self._now()
                )
                authoritative_revision = str(state.source_revision)
                if new_source_data_revision is not None and str(new_source_data_revision) != authoritative_revision:
                    raise MarketAdjustmentConflictError(
                        "Caller cannot set source-data revision; canonical source state is authoritative"
                    )
                current = self._uow.adjustment_decision_queries.list_for_comparable(
                    case_id, comparable_property_id
                )
                if not current:
                    return ()
                timestamp = self._now()
                output: list[AdjustmentDecisionRecord] = []
                for decision in current:
                    if (
                        decision.review_status == "CURRENT"
                        and decision.source_data_revision != authoritative_revision
                    ):
                        stale = replace(
                            decision,
                            review_status="SOURCE_DATA_CHANGED",
                            version=decision.version + 1,
                        )
                        if not self._uow.adjustment_decisions.put_if_version(
                            stale, expected_version=decision.version
                        ):
                            raise MarketAdjustmentConflictError(
                                "Adjustment decision changed concurrently during source-drift reconciliation"
                            )
                        self._uow.adjustment_selection_audit.add(
                            AdjustmentSelectionAuditRecord(
                                id=self._new_id(),
                                adjustment_decision_id=decision.id,
                                case_id=case_id,
                                comparable_property_id=comparable_property_id,
                                factor_key=decision.factor_key,
                                event_kind="SOURCE_DATA_CHANGED",
                                selected_rate_pct=decision.selected_rate_pct,
                                selected_explicitly=decision.selected_explicitly,
                                selected_by="SYSTEM_SOURCE_DRIFT",
                                selected_at=timestamp,
                                source_data_revision=authoritative_revision,
                                review_status="SOURCE_DATA_CHANGED",
                            )
                        )
                        output.append(stale)
                    else:
                        output.append(decision)
                return tuple(output)
        except MarketAdjustmentError:
            raise
        except Exception as exc:
            raise MarketAdjustmentPersistenceError(
                "Adjustment source-drift state could not be reconciled atomically"
            ) from exc

    def run_adjustment(
        self,
        *,
        case_id: str,
        comparable_property_id: str,
        source_data_revision: str | None = None,
        normalized_base_price_vnd_per_m2: DecimalInput | None = None,
    ) -> PersistedAdjustmentRun:
        case_id = _require_text(case_id, "case_id")
        comparable_property_id = _require_text(
            comparable_property_id, "comparable_property_id"
        )
        try:
            with self._uow.atomic():
                self._require_case_and_comparable(case_id, comparable_property_id)
                state = self._uow.adjustment_source_states.get(
                    case_id, comparable_property_id
                )
                if state is None:
                    raise MarketAdjustmentConflictError(
                        "Adjustment source state has not been established"
                    )
                authoritative_revision = str(state.source_revision)
                if source_data_revision is not None and str(source_data_revision) != authoritative_revision:
                    raise MarketAdjustmentConflictError(
                        "Caller source-data revision does not match authoritative current revision"
                    )
                if (
                    state.normalized_base_price_vnd_per_m2 is None
                    or state.normalized_base_bound_revision != state.source_revision
                    or not state.normalized_base_evidence_ref
                ):
                    raise MarketAdjustmentConflictError(
                        "Normalized adjustment base is not evidence-bound to current source revision"
                    )
                if normalized_base_price_vnd_per_m2 is not None:
                    supplied = to_decimal(
                        normalized_base_price_vnd_per_m2,
                        field_name="normalized_base_price_vnd_per_m2",
                    )
                    bound = to_decimal(
                        state.normalized_base_price_vnd_per_m2,
                        field_name="bound_normalized_base_price_vnd_per_m2",
                    )
                    if supplied != bound:
                        raise MarketAdjustmentConflictError(
                            "Caller normalized base does not match evidence-bound current P0"
                        )

                records = self._uow.adjustment_decision_queries.list_for_comparable(
                    case_id, comparable_property_id
                )
                self._validate_current_decisions(records, authoritative_revision)
                initial_fingerprint = _decision_fingerprint(records)

                decisions = tuple(
                    SelectedAdjustmentDecision(
                        item.factor_key,
                        item.selected_rate_pct,
                        selected_explicitly=item.selected_explicitly,
                    )
                    for item in records
                )
                result = calculate_adjustment_run(
                    normalized_base_price_vnd_per_m2=state.normalized_base_price_vnd_per_m2,
                    decisions=decisions,
                )
                decision_payload = [
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
                decision_set_sha256 = _sha256_json(decision_payload)
                step_payload = [
                    {
                        "factor_key": step.factor_key,
                        "selected_rate_fraction": format(step.selected_rate, "f"),
                        "amount_base_vnd_per_m2": format(step.amount_base_vnd_per_m2, "f"),
                        "adjustment_amount_vnd_per_m2": format(step.adjustment_amount_vnd_per_m2, "f"),
                        "running_price_vnd_per_m2": format(step.running_price_vnd_per_m2, "f"),
                    }
                    for step in result.steps
                ]
                semantic_payload = {
                    "case_id": case_id,
                    "comparable_property_id": comparable_property_id,
                    "source_data_revision": authoritative_revision,
                    "normalized_base_price_vnd_per_m2": format(
                        result.normalized_base_price_vnd_per_m2, "f"
                    ),
                    "normalized_base_evidence_ref": state.normalized_base_evidence_ref,
                    "property_adjustment_base_vnd_per_m2": format(
                        result.property_adjustment_base_vnd_per_m2, "f"
                    ),
                    "indicated_unit_price_vnd_per_m2": format(
                        result.indicated_unit_price_vnd_per_m2, "f"
                    ),
                    "decision_set_sha256": decision_set_sha256,
                    "steps": step_payload,
                }
                semantic_sha256 = _sha256_json(semantic_payload)

                # Re-read authoritative state and every decision immediately before
                # persistence. This catches fake/non-locking UoWs and complements
                # BEGIN IMMEDIATE serialization in SQLCipherUnitOfWork.
                state_now = self._uow.adjustment_source_states.get(
                    case_id, comparable_property_id
                )
                records_now = self._uow.adjustment_decision_queries.list_for_comparable(
                    case_id, comparable_property_id
                )
                if state_now != state or _decision_fingerprint(records_now) != initial_fingerprint:
                    raise MarketAdjustmentConflictError(
                        "Adjustment source or human decisions changed during calculation"
                    )
                self._validate_current_decisions(records_now, authoritative_revision)

                snapshot_id = self._new_id()
                self._uow.adjustment_calculation_snapshots.add(
                    AdjustmentCalculationSnapshotRecord(
                        id=snapshot_id,
                        case_id=case_id,
                        comparable_property_id=comparable_property_id,
                        source_data_revision=authoritative_revision,
                        normalized_base_price_vnd_per_m2=semantic_payload[
                            "normalized_base_price_vnd_per_m2"
                        ],
                        property_adjustment_base_vnd_per_m2=semantic_payload[
                            "property_adjustment_base_vnd_per_m2"
                        ],
                        indicated_unit_price_vnd_per_m2=semantic_payload[
                            "indicated_unit_price_vnd_per_m2"
                        ],
                        decision_set_sha256=decision_set_sha256,
                        ordered_steps_json=json.dumps(
                            step_payload,
                            ensure_ascii=False,
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                        semantic_sha256=semantic_sha256,
                        created_at=self._now(),
                    )
                )
                return PersistedAdjustmentRun(
                    snapshot_id=snapshot_id,
                    semantic_sha256=semantic_sha256,
                    decision_set_sha256=decision_set_sha256,
                    result=result,
                )
        except MarketAdjustmentError:
            raise
        except Exception as exc:
            raise MarketAdjustmentPersistenceError(
                "Adjustment calculation snapshot could not be persisted"
            ) from exc

    def _validate_current_decisions(
        self,
        records: tuple[AdjustmentDecisionRecord, ...],
        authoritative_revision: str,
    ) -> None:
        if tuple(item.factor_key for item in records) != N08_FACTOR_KEYS:
            raise MarketAdjustmentConflictError(
                "Complete adjustment run requires current C1-C11 decisions in frozen order"
            )
        for item in records:
            if item.review_status != "CURRENT":
                raise MarketAdjustmentConflictError(
                    f"{item.factor_key} requires human review after source-data change"
                )
            if item.source_data_revision != authoritative_revision:
                raise MarketAdjustmentConflictError(
                    f"{item.factor_key} is not bound to authoritative current source-data revision"
                )
            if not item.selected_explicitly or item.selected_rate_pct is None:
                raise MarketAdjustmentConflictError(
                    f"{item.factor_key} has no explicit human-selected decision"
                )

    def _require_case_and_comparable(
        self, case_id: str, comparable_property_id: str
    ) -> None:
        case = self._uow.cases.get(case_id)
        if case is None or case.archived_at is not None:
            raise MarketAdjustmentNotFoundError("Appraisal case was not found")
        comparable = self._uow.comparables.get(comparable_property_id)
        if comparable is None or comparable.archived_at is not None:
            raise MarketAdjustmentNotFoundError("Comparable property was not found")
        if comparable.case_id != case_id:
            raise MarketAdjustmentConflictError(
                "Comparable property does not belong to the appraisal case"
            )
