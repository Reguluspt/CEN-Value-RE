"""Framework-independent persistence contracts for CenValue RE."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class CaseRecord:
    id: str
    case_code: str
    status: str
    created_at: str
    updated_at: str
    appraisal_date: str | None = None
    client_name: str | None = None
    valuation_purpose: str | None = None
    include_in_historical_learning: bool = False
    active_subject_property_id: str | None = None
    current_approval_revision: int | None = None
    legacy_case_id: str | None = None
    version: int = 1
    archived_at: str | None = None


@dataclass(frozen=True, slots=True)
class SubjectPropertyRecord:
    property_id: str
    case_id: str
    legal_address: str
    current_address: str
    legal_review_status: str
    created_at: str
    updated_at: str
    source_certificate_id: str | None = None
    display_name: str | None = None
    version: int = 1
    archived_at: str | None = None


@dataclass(frozen=True, slots=True)
class ComparablePropertyRecord:
    property_id: str
    case_id: str
    legal_address: str
    current_address: str
    comparable_order: int
    completeness_status: str
    created_at: str
    updated_at: str
    market_observation_id: str | None = None
    display_name: str | None = None
    version: int = 1
    archived_at: str | None = None


@dataclass(frozen=True, slots=True)
class ConstructionAssetRecord:
    id: str
    property_id: str
    name: str
    legal_registration_status: str
    valuation_treatment: str
    created_at: str
    updated_at: str
    construction_type: str | None = None
    construction_area_m2: str | None = None
    gross_floor_area_m2: str | None = None
    replacement_cost_vnd: str | None = None
    remaining_quality_pct: str | None = None
    remaining_value_vnd: str | None = None
    version: int = 1
    archived_at: str | None = None


@dataclass(frozen=True, slots=True)
class AdjustmentDecisionRecord:
    id: str
    case_id: str
    comparable_property_id: str
    factor_key: str
    selected_explicitly: bool
    source_data_revision: str
    review_status: str
    suggested_rate_pct: str | None = None
    selected_rate_pct: str | None = None
    approved_rate_pct: str | None = None
    selected_at: str | None = None
    version: int = 1
    archived_at: str | None = None


@dataclass(frozen=True, slots=True)
class ApprovalSubmissionRecord:
    id: str
    case_id: str
    revision_no: int
    exported_at: str
    template_profile_id: str
    workbook_hash: str
    submitted_case_snapshot: str
    submitted_result_snapshot: str
    output_document_id: str
    status: str
    archived_at: str | None = None


class CaseRepository(Protocol):
    def put(self, record: CaseRecord) -> None: ...
    def get(self, record_id: str) -> CaseRecord | None: ...
    def archive(self, record_id: str, archived_at: str) -> None: ...


class SubjectPropertyRepository(Protocol):
    def put(self, record: SubjectPropertyRecord) -> None: ...
    def get(self, property_id: str) -> SubjectPropertyRecord | None: ...
    def archive(self, property_id: str, archived_at: str) -> None: ...


class ComparablePropertyRepository(Protocol):
    def put(self, record: ComparablePropertyRecord) -> None: ...
    def get(self, property_id: str) -> ComparablePropertyRecord | None: ...
    def archive(self, property_id: str, archived_at: str) -> None: ...


class ConstructionAssetRepository(Protocol):
    def put(self, record: ConstructionAssetRecord) -> None: ...
    def get(self, record_id: str) -> ConstructionAssetRecord | None: ...
    def archive(self, record_id: str, archived_at: str) -> None: ...


class AdjustmentDecisionRepository(Protocol):
    def put(self, record: AdjustmentDecisionRecord) -> None: ...
    def get(self, record_id: str) -> AdjustmentDecisionRecord | None: ...
    def archive(self, record_id: str, archived_at: str) -> None: ...


class ApprovalSubmissionRepository(Protocol):
    def put(self, record: ApprovalSubmissionRecord) -> None: ...
    def get(self, record_id: str) -> ApprovalSubmissionRecord | None: ...
    def archive(self, record_id: str, archived_at: str) -> None: ...


class PersistenceUnitOfWork(Protocol):
    cases: CaseRepository
    subjects: SubjectPropertyRepository
    comparables: ComparablePropertyRepository
    construction_assets: ConstructionAssetRepository
    adjustment_decisions: AdjustmentDecisionRepository
    approval_submissions: ApprovalSubmissionRepository

    @property
    def schema_version(self) -> int: ...
    def close(self) -> None: ...
