"""Framework-independent persistence contracts for E1-PR-002 adjustment evidence."""

from __future__ import annotations

from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Protocol

from .adjustment_source import AdjustmentSourceStateRepository
from .persistence import AdjustmentDecisionRecord, CaseRepository, ComparablePropertyRepository


@dataclass(frozen=True, slots=True)
class AdjustmentSelectionAuditRecord:
    id: str
    adjustment_decision_id: str
    case_id: str
    comparable_property_id: str
    factor_key: str
    event_kind: str
    selected_rate_pct: str | None
    selected_explicitly: bool
    selected_by: str
    selected_at: str
    source_data_revision: str
    review_status: str


@dataclass(frozen=True, slots=True)
class AdjustmentCalculationSnapshotRecord:
    id: str
    case_id: str
    comparable_property_id: str
    source_data_revision: str
    normalized_base_price_vnd_per_m2: str
    property_adjustment_base_vnd_per_m2: str
    indicated_unit_price_vnd_per_m2: str
    decision_set_sha256: str
    ordered_steps_json: str
    semantic_sha256: str
    created_at: str


class AdjustmentDecisionWriteRepository(Protocol):
    def put(self, record: AdjustmentDecisionRecord) -> None: ...

    def put_if_version(
        self, record: AdjustmentDecisionRecord, *, expected_version: int
    ) -> bool: ...


class AdjustmentDecisionQueryRepository(Protocol):
    def list_for_comparable(
        self, case_id: str, comparable_property_id: str
    ) -> tuple[AdjustmentDecisionRecord, ...]: ...


class AdjustmentSelectionAuditRepository(Protocol):
    def add(self, record: AdjustmentSelectionAuditRecord) -> None: ...

    def list_for_decision(
        self, adjustment_decision_id: str
    ) -> tuple[AdjustmentSelectionAuditRecord, ...]: ...


class AdjustmentCalculationSnapshotRepository(Protocol):
    def add(self, record: AdjustmentCalculationSnapshotRecord) -> None: ...

    def get(self, record_id: str) -> AdjustmentCalculationSnapshotRecord | None: ...

    def list_for_comparable(
        self, case_id: str, comparable_property_id: str
    ) -> tuple[AdjustmentCalculationSnapshotRecord, ...]: ...


class AdjustmentPersistenceUnitOfWork(Protocol):
    cases: CaseRepository
    comparables: ComparablePropertyRepository
    adjustment_decisions: AdjustmentDecisionWriteRepository
    adjustment_decision_queries: AdjustmentDecisionQueryRepository
    adjustment_selection_audit: AdjustmentSelectionAuditRepository
    adjustment_calculation_snapshots: AdjustmentCalculationSnapshotRepository
    adjustment_source_states: AdjustmentSourceStateRepository

    def atomic(self) -> AbstractContextManager[None]: ...
