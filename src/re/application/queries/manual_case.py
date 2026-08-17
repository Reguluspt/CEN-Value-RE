"""Read model for the Epic 1 manual-case data backbone."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json

from ...ports.persistence import (
    CaseRecord,
    ComparablePropertyRecord,
    EvidenceRecord,
    LandParcelRecord,
    LandValuationComponentRecord,
    MarketObservationRecord,
    PropertyCharacteristicRecord,
    SubjectPropertyRecord,
)


@dataclass(frozen=True, slots=True)
class SubjectBundle:
    property: SubjectPropertyRecord
    parcels: tuple[LandParcelRecord, ...]
    land_valuation_components: tuple[LandValuationComponentRecord, ...]
    characteristics: tuple[PropertyCharacteristicRecord, ...]


@dataclass(frozen=True, slots=True)
class ComparableBundle:
    property: ComparablePropertyRecord
    market_observation: MarketObservationRecord | None
    characteristics: tuple[PropertyCharacteristicRecord, ...]
    evidence: tuple[EvidenceRecord, ...]


@dataclass(frozen=True, slots=True)
class ManualCaseSnapshot:
    case: CaseRecord
    subject: SubjectBundle | None
    comparables: tuple[ComparableBundle, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
