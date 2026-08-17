"""Persistence contracts for human indication and final valuation evidence."""

from __future__ import annotations

from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Protocol

from .adjustment_persistence import (
    AdjustmentCalculationSnapshotRepository,
    AdjustmentDecisionQueryRepository,
)
from .adjustment_source import AdjustmentSourceStateRepository
from .persistence import (
    CaseRepository,
    ComparablePropertyRepository,
    LandValuationComponentRepository,
    SubjectPropertyRepository,
)


@dataclass(frozen=True, slots=True)
class HumanIndicationSnapshotRecord:
    id: str
    case_id: str
    selection_kind: str
    selected_comparable_property_id: str | None
    raw_indicated_unit_price_vnd_per_m2: str
    rounded_indicated_unit_price_vnd_per_m2: str
    rounding_target: str
    rounding_mode: str
    rounding_increment_vnd: int | None
    rounding_source: str
    rounding_profile_id: str | None
    rounding_profile_version: str | None
    rounding_selected_by: str | None
    rounding_selected_at: str | None
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


@dataclass(frozen=True, slots=True)
class ConstructionAggregateInputRecord:
    id: str
    case_id: str
    revision: int
    amount_vnd: str
    evidence_ref: str
    source_kind: str
    supplied_by: str
    supplied_at: str
    semantic_sha256: str


@dataclass(frozen=True, slots=True)
class FinalValuationSnapshotRecord:
    id: str
    case_id: str
    subject_property_id: str
    appraisal_date: str
    human_indication_snapshot_id: str
    human_indication_semantic_sha256: str
    rounded_indicated_unit_price_vnd_per_m2: str
    land_components_json: str
    land_components_sha256: str
    compliant_residential_land_value_vnd: str
    other_recognized_land_value_vnd: str
    recognized_land_value_vnd: str
    construction_aggregate_input_id: str
    construction_aggregate_semantic_sha256: str
    construction_value_total_vnd: str
    total_value_before_rounding_vnd: str
    final_appraised_value_vnd: str
    rounding_target: str
    rounding_mode: str
    rounding_increment_vnd: int | None
    rounding_source: str
    rounding_profile_id: str | None
    rounding_profile_version: str | None
    rounding_selected_by: str | None
    rounding_selected_at: str | None
    composed_at: str
    semantic_sha256: str


@dataclass(frozen=True, slots=True)
class FinalValuationLandSourceRecord:
    valuation_snapshot_id: str
    case_id: str
    subject_property_id: str
    land_component_id: str
    component_semantic_sha256: str


class HumanIndicationSnapshotRepository(Protocol):
    def add(self, record: HumanIndicationSnapshotRecord) -> None: ...
    def get(self, record_id: str) -> HumanIndicationSnapshotRecord | None: ...
    def list_for_case(self, case_id: str) -> tuple[HumanIndicationSnapshotRecord, ...]: ...


class HumanIndicationSourceRepository(Protocol):
    def add(self, record: HumanIndicationSourceRecord) -> None: ...
    def list_for_snapshot(
        self, indication_snapshot_id: str
    ) -> tuple[HumanIndicationSourceRecord, ...]: ...


class ConstructionAggregateInputRepository(Protocol):
    def add(self, record: ConstructionAggregateInputRecord) -> None: ...
    def get(self, record_id: str) -> ConstructionAggregateInputRecord | None: ...
    def list_for_case(self, case_id: str) -> tuple[ConstructionAggregateInputRecord, ...]: ...
    def latest_for_case(self, case_id: str) -> ConstructionAggregateInputRecord | None: ...


class FinalValuationSnapshotRepository(Protocol):
    def add(self, record: FinalValuationSnapshotRecord) -> None: ...
    def get(self, record_id: str) -> FinalValuationSnapshotRecord | None: ...
    def list_for_case(self, case_id: str) -> tuple[FinalValuationSnapshotRecord, ...]: ...


class FinalValuationLandSourceRepository(Protocol):
    def add(self, record: FinalValuationLandSourceRecord) -> None: ...
    def list_for_snapshot(
        self, valuation_snapshot_id: str
    ) -> tuple[FinalValuationLandSourceRecord, ...]: ...


class HumanIndicationUnitOfWork(Protocol):
    cases: CaseRepository
    comparables: ComparablePropertyRepository
    adjustment_decision_queries: AdjustmentDecisionQueryRepository
    adjustment_calculation_snapshots: AdjustmentCalculationSnapshotRepository
    adjustment_source_states: AdjustmentSourceStateRepository
    human_indication_snapshots: HumanIndicationSnapshotRepository
    human_indication_sources: HumanIndicationSourceRepository

    def atomic(self) -> AbstractContextManager[None]: ...


class FinalValuationUnitOfWork(HumanIndicationUnitOfWork, Protocol):
    subjects: SubjectPropertyRepository
    land_valuation_components: LandValuationComponentRepository
    construction_aggregate_inputs: ConstructionAggregateInputRepository
    final_valuation_snapshots: FinalValuationSnapshotRepository
    final_valuation_land_sources: FinalValuationLandSourceRepository
