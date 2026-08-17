"""Authoritative source-state contract for E1-PR-002 adjustment calculations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class AdjustmentSourceStateRecord:
    case_id: str
    comparable_property_id: str
    source_revision: int
    normalized_base_price_vnd_per_m2: str | None
    normalized_base_bound_revision: int | None
    normalized_base_evidence_ref: str | None
    updated_at: str


class AdjustmentSourceStateRepository(Protocol):
    def get(
        self, case_id: str, comparable_property_id: str
    ) -> AdjustmentSourceStateRecord | None: ...

    def ensure(
        self, case_id: str, comparable_property_id: str, updated_at: str
    ) -> AdjustmentSourceStateRecord: ...

    def bind_normalized_base(
        self,
        *,
        case_id: str,
        comparable_property_id: str,
        expected_source_revision: int,
        normalized_base_price_vnd_per_m2: str,
        evidence_ref: str,
        updated_at: str,
    ) -> AdjustmentSourceStateRecord: ...
