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


class MarketAdjustmentService:
    """Persist human decisions, stale them on drift, and run frozen calculations."""

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

    def select_rate(
        self,
        *,
        case_id: str,
        comparable_property_id: str,
        factor_key: str,
        selected_rate: DecimalInput,
        selected_by: str,
        source_data_revision: str,
    ) -> AdjustmentDecisionRecord:
        case_id = _require_text(case_id, "case_id")
        comparable_property_id = _require_text(
            comparable_property_id, "comparable_property_id"
        )
        selected_by = _require_text(selected_by, "selected_by")
        source_data_revision = _require_text(
            source_data_revision, "source_data_revision"
        )
        if factor_key not in N08_FACTOR_KEYS:
            raise MarketAdjustmentValidationError(
                f"unsupported adjustment factor key: {factor_key!r}"
            )
        rate_text = _decimal_text(selected_rate, "selected_rate")
        self._require_case_and_comparable(case_id, comparable_property_id)

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
            source_data_revision=source_data_revision,
            review_status="CURRENT",
            suggested_rate_pct=existing.suggested_rate_pct if existing else None,
            selected_rate_pct=rate_text,
            approved_rate_pct=existing.approved_rate_pct if existing else None,
            selected_at=timestamp,
            version=(existing.version + 1) if existing else 1,
            archived_at=None,
        )
        audit = AdjustmentSelectionAuditRecord(
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
            source_data_revision=source_data_revision,
            review_status="CURRENT",
        )
        try:
            with self._uow.atomic():
                self._uow.adjustment_decisions.put(decision)  # type: ignore[attr-defined]
                self._uow.adjustment_selection_audit.add(audit)
        except Exception as exc:
            raise MarketAdjustmentPersistenceError(
                "Adjustment selection could not be persisted atomically"
            ) from exc
        return decision

    def mark_source_data_changed(
        self,
        *,
        case_id: str,
        comparable_property_id: str,
        new_source_data_revision: str,
    ) -> tuple[AdjustmentDecisionRecord, ...]:
        new_source_data_revision = _require_text(
            new_source_data_revision, "new_source_data_revision"
        )
        self._require_case_and_comparable(case_id, comparable_property_id)
        current = self._uow.adjustment_decision_queries.list_for_comparable(
            case_id, comparable_property_id
        )
        if not current:
            return ()
        timestamp = self._now()
        updated: list[AdjustmentDecisionRecord] = []
        audits: list[AdjustmentSelectionAuditRecord] = []
        for decision in current:
            if (
                decision.review_status == "SOURCE_DATA_CHANGED"
                and decision.source_data_revision != new_source_data_revision
            ):
                updated.append(decision)
                continue
            if decision.source_data_revision == new_source_data_revision:
                updated.append(decision)
                continue
            stale = replace(
                decision,
                review_status="SOURCE_DATA_CHANGED",
                version=decision.version + 1,
            )
            updated.append(stale)
            audits.append(
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
                    source_data_revision=new_source_data_revision,
                    review_status="SOURCE_DATA_CHANGED",
                )
            )
        try:
            with self._uow.atomic():
                for decision in updated:
                    self._uow.adjustment_decisions.put(decision)  # type: ignore[attr-defined]
                for audit in audits:
                    self._uow.adjustment_selection_audit.add(audit)
        except Exception as exc:
            raise MarketAdjustmentPersistenceError(
                "Adjustment source-drift state could not be persisted atomically"
            ) from exc
        return tuple(updated)

    def run_adjustment(
        self,
        *,
        case_id: str,
        comparable_property_id: str,
        source_data_revision: str,
        normalized_base_price_vnd_per_m2: DecimalInput,
    ) -> PersistedAdjustmentRun:
        source_data_revision = _require_text(
            source_data_revision, "source_data_revision"
        )
        self._require_case_and_comparable(case_id, comparable_property_id)
        records = self._uow.adjustment_decision_queries.list_for_comparable(
            case_id, comparable_property_id
        )
        if tuple(item.factor_key for item in records) != N08_FACTOR_KEYS:
            raise MarketAdjustmentConflictError(
                "Complete adjustment run requires current C1-C11 decisions in frozen order"
            )
        for item in records:
            if item.review_status != "CURRENT":
                raise MarketAdjustmentConflictError(
                    f"{item.factor_key} requires human review after source-data change"
                )
            if item.source_data_revision != source_data_revision:
                raise MarketAdjustmentConflictError(
                    f"{item.factor_key} is not bound to current source-data revision"
                )
            if not item.selected_explicitly or item.selected_rate_pct is None:
                raise MarketAdjustmentConflictError(
                    f"{item.factor_key} has no explicit human-selected decision"
                )

        decisions = tuple(
            SelectedAdjustmentDecision(
                item.factor_key,
                item.selected_rate_pct,
                selected_explicitly=item.selected_explicitly,
            )
            for item in records
        )
        result = calculate_adjustment_run(
            normalized_base_price_vnd_per_m2=normalized_base_price_vnd_per_m2,
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
                "amount_base_vnd_per_m2": format(
                    step.amount_base_vnd_per_m2, "f"
                ),
                "adjustment_amount_vnd_per_m2": format(
                    step.adjustment_amount_vnd_per_m2, "f"
                ),
                "running_price_vnd_per_m2": format(
                    step.running_price_vnd_per_m2, "f"
                ),
            }
            for step in result.steps
        ]
        semantic_payload = {
            "case_id": case_id,
            "comparable_property_id": comparable_property_id,
            "source_data_revision": source_data_revision,
            "normalized_base_price_vnd_per_m2": format(
                result.normalized_base_price_vnd_per_m2, "f"
            ),
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
        snapshot_id = self._new_id()
        snapshot = AdjustmentCalculationSnapshotRecord(
            id=snapshot_id,
            case_id=case_id,
            comparable_property_id=comparable_property_id,
            source_data_revision=source_data_revision,
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
        try:
            with self._uow.atomic():
                self._uow.adjustment_calculation_snapshots.add(snapshot)
        except Exception as exc:
            raise MarketAdjustmentPersistenceError(
                "Adjustment calculation snapshot could not be persisted"
            ) from exc
        return PersistedAdjustmentRun(
            snapshot_id=snapshot_id,
            semantic_sha256=semantic_sha256,
            decision_set_sha256=decision_set_sha256,
            result=result,
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
