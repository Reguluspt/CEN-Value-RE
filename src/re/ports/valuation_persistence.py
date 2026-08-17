"""Persistence contracts for E1-PR-003 human indication evidence."""

from __future__ import annotations

from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Protocol

from .adjustment_persistence import (
    AdjustmentCalculationSnapshotRepository,
    AdjustmentDecisionQueryRepository,
)
from .adjustment_source import AdjustmentSourceStateRepository
from .persistence import CaseRepository, ComparablePropertyRepository


@dataclass(frozen=True, slots=True)
class HumanIndicationSnapshotRecord:
    id: str
    case_id: str
    selection_kind: str
    selected_comparable_property_id: str | None
    raw_indicated_unit_price_vnd_per_m2: str
    rounded_indicated_unit_price_vnd_per_m2: str
    rounding_target: str
    rounding_increment_vnd: int | None
    rounding_source: str
    rounding_profile_id: str | None
    rounding_profile_version: str | None
    confirmed_by: str
    confirmed_at: str
    reason: str
    quality_snapshot_json: str
    readiness_snapshot_json: str
    guidance_snapshot_json: str
    semantic_sha256: str


@dataclass(frozen=True, slots=True)
class HumanIndicationSourceRecord:
    indication_snapshot_id: str
    case_id: str
    comparable_property_id: str
    adjustment_snapshot_id: str
    adjustment_semantic_sha256: str


class HumanIndicationSnapshotRepository(Protocol):
    def add(self, record: HumanIndicationSnapshotRecord) -> None: ...

    def get(self, record_id: str) -> HumanIndicationSnapshotRecord | None: ...

    def list_for_case(self, case_id: str) -> tuple[HumanIndicationSnapshotRecord, ...]: ...


class HumanIndicationSourceRepository(Protocol):
    def add(self, record: HumanIndicationSourceRecord) -> None: ...

    def list_for_snapshot(
        self, indication_snapshot_id: str
    ) -> tuple[HumanIndicationSourceRecord, ...]: ...


class HumanIndicationUnitOfWork(Protocol):
    cases: CaseRepository
    comparables: ComparablePropertyRepository
    adjustment_decision_queries: AdjustmentDecisionQueryRepository
    adjustment_calculation_snapshots: AdjustmentCalculationSnapshotRepository
    adjustment_source_states: AdjustmentSourceStateRepository
    human_indication_snapshots: HumanIndicationSnapshotRepository
    human_indication_sources: HumanIndicationSourceRepository

    def atomic(self) -> AbstractContextManager[None]: ...
