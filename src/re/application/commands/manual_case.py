"""Manual-case commands for the Epic 1 data backbone."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TypeAlias
from uuid import UUID

from ...domain.common.numeric import DecimalInput, to_decimal

OptionalDecimalInput: TypeAlias = DecimalInput | None


def _nonempty(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError("optional text values must be strings")
    text = value.strip()
    return text or None



def _optional_uuid(value: str | None, field_name: str) -> str | None:
    value = _optional_text(value)
    if value is None:
        return None
    try:
        parsed = UUID(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a UUID") from exc
    return str(parsed)


def _iso_date(value: str | None, field_name: str, *, required: bool = False) -> str | None:
    if value is None:
        if required:
            raise ValueError(f"{field_name} is required")
        return None
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be an ISO date string")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO calendar date") from exc
    if parsed.isoformat() != value:
        raise ValueError(f"{field_name} must use canonical YYYY-MM-DD form")
    return value


def _decimal_text(
    value: OptionalDecimalInput,
    field_name: str,
    *,
    minimum: Decimal | None = None,
    maximum: Decimal | None = None,
) -> str | None:
    if value is None:
        return None
    result = to_decimal(value, field_name=field_name)
    if minimum is not None and result < minimum:
        raise ValueError(f"{field_name} must be >= {minimum}")
    if maximum is not None and result > maximum:
        raise ValueError(f"{field_name} must be <= {maximum}")
    return str(result)


@dataclass(frozen=True, slots=True)
class CharacteristicInput:
    definition_key: str
    decimal_value: OptionalDecimalInput = None
    text_value: str | None = None
    code_value: str | None = None
    bool_value: bool | None = None
    date_value: str | None = None
    source_status: str = "MANUAL"
    verified_by_user: bool = True
    provenance_id: str | None = None
    characteristic_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "definition_key", _nonempty(self.definition_key, "definition_key"))
        object.__setattr__(self, "source_status", _nonempty(self.source_status, "source_status"))
        object.__setattr__(self, "provenance_id", _optional_text(self.provenance_id))
        object.__setattr__(self, "characteristic_id", _optional_uuid(self.characteristic_id, "characteristic_id"))
        if self.bool_value is not None and not isinstance(self.bool_value, bool):
            raise TypeError("bool_value must be bool when supplied")
        values = (
            self.decimal_value is not None,
            self.text_value is not None,
            self.code_value is not None,
            self.bool_value is not None,
            self.date_value is not None,
        )
        if sum(values) != 1:
            raise ValueError("exactly one characteristic value must be supplied")
        if self.decimal_value is not None:
            object.__setattr__(
                self,
                "decimal_value",
                _decimal_text(self.decimal_value, f"characteristic[{self.definition_key}].decimal_value"),
            )
        if self.text_value is not None:
            object.__setattr__(self, "text_value", _nonempty(self.text_value, "text_value"))
        if self.code_value is not None:
            object.__setattr__(self, "code_value", _nonempty(self.code_value, "code_value"))
        if self.date_value is not None:
            object.__setattr__(self, "date_value", _iso_date(self.date_value, "date_value"))


@dataclass(frozen=True, slots=True)
class LandValuationComponentInput:
    planning_status: str
    area_m2: DecimalInput
    valuation_basis: str
    include_in_final_value: bool
    unit_price_vnd_per_m2: OptionalDecimalInput = None
    note: str | None = None
    policy_version: str | None = None
    component_id: str | None = None

    def __post_init__(self) -> None:
        planning = _nonempty(self.planning_status, "planning_status")
        basis = _nonempty(self.valuation_basis, "valuation_basis")
        if planning not in {"COMPLIANT", "NON_COMPLIANT", "UNKNOWN"}:
            raise ValueError("unsupported planning_status")
        if basis not in {"MARKET_INDICATED", "OFFICIAL_LAND_PRICE", "OTHER_MANUAL_BASIS"}:
            raise ValueError("unsupported valuation_basis")
        if not isinstance(self.include_in_final_value, bool):
            raise TypeError("include_in_final_value must be bool")
        object.__setattr__(self, "planning_status", planning)
        object.__setattr__(self, "valuation_basis", basis)
        object.__setattr__(self, "area_m2", _decimal_text(self.area_m2, "area_m2", minimum=Decimal("0")))
        object.__setattr__(
            self,
            "unit_price_vnd_per_m2",
            _decimal_text(
                self.unit_price_vnd_per_m2,
                "unit_price_vnd_per_m2",
                minimum=Decimal("0"),
            ),
        )
        object.__setattr__(self, "note", _optional_text(self.note))
        object.__setattr__(self, "policy_version", _optional_text(self.policy_version))
        object.__setattr__(self, "component_id", _optional_uuid(self.component_id, "component_id"))


@dataclass(frozen=True, slots=True)
class LandParcelInput:
    parcel_number: str | None = None
    map_sheet_number: str | None = None
    total_area_m2: OptionalDecimalInput = None
    legal_address: str | None = None
    current_address: str | None = None
    notes: str | None = None
    parcel_id: str | None = None
    valuation_components: tuple[LandValuationComponentInput, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "parcel_number", _optional_text(self.parcel_number))
        object.__setattr__(self, "map_sheet_number", _optional_text(self.map_sheet_number))
        object.__setattr__(
            self,
            "total_area_m2",
            _decimal_text(self.total_area_m2, "total_area_m2", minimum=Decimal("0")),
        )
        object.__setattr__(self, "legal_address", _optional_text(self.legal_address))
        object.__setattr__(self, "current_address", _optional_text(self.current_address))
        object.__setattr__(self, "notes", _optional_text(self.notes))
        object.__setattr__(self, "parcel_id", _optional_uuid(self.parcel_id, "parcel_id"))


@dataclass(frozen=True, slots=True)
class EvidenceInput:
    evidence_type: str | None = None
    source_url: str | None = None
    note: str | None = None
    evidence_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence_type", _optional_text(self.evidence_type))
        object.__setattr__(self, "source_url", _optional_text(self.source_url))
        object.__setattr__(self, "note", _optional_text(self.note))
        object.__setattr__(self, "evidence_id", _optional_uuid(self.evidence_id, "evidence_id"))
        if not any((self.evidence_type, self.source_url, self.note)):
            raise ValueError("evidence must contain at least one metadata field")


@dataclass(frozen=True, slots=True)
class CreateManualCase:
    case_code: str
    appraisal_date: str
    profile_id: str
    profile_version: str
    client_name: str | None = None
    valuation_purpose: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "case_code", _nonempty(self.case_code, "case_code"))
        object.__setattr__(self, "appraisal_date", _iso_date(self.appraisal_date, "appraisal_date", required=True))
        object.__setattr__(self, "profile_id", _nonempty(self.profile_id, "profile_id"))
        object.__setattr__(self, "profile_version", _nonempty(self.profile_version, "profile_version"))
        object.__setattr__(self, "client_name", _optional_text(self.client_name))
        object.__setattr__(self, "valuation_purpose", _optional_text(self.valuation_purpose))


@dataclass(frozen=True, slots=True)
class SaveSubject:
    case_id: str
    legal_address: str
    current_address: str
    legal_review_status: str
    display_name: str | None = None
    source_certificate_id: str | None = None
    latitude: OptionalDecimalInput = None
    longitude: OptionalDecimalInput = None
    planning_note: str | None = None
    environment_note: str | None = None
    property_id: str | None = None
    parcels: tuple[LandParcelInput, ...] = ()
    characteristics: tuple[CharacteristicInput, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "case_id", _nonempty(self.case_id, "case_id"))
        object.__setattr__(self, "legal_address", _nonempty(self.legal_address, "legal_address"))
        object.__setattr__(self, "current_address", _nonempty(self.current_address, "current_address"))
        object.__setattr__(self, "legal_review_status", _nonempty(self.legal_review_status, "legal_review_status"))
        object.__setattr__(self, "display_name", _optional_text(self.display_name))
        object.__setattr__(self, "source_certificate_id", _optional_text(self.source_certificate_id))
        object.__setattr__(
            self, "latitude", _decimal_text(self.latitude, "latitude", minimum=Decimal("-90"), maximum=Decimal("90"))
        )
        object.__setattr__(
            self, "longitude", _decimal_text(self.longitude, "longitude", minimum=Decimal("-180"), maximum=Decimal("180"))
        )
        object.__setattr__(self, "planning_note", _optional_text(self.planning_note))
        object.__setattr__(self, "environment_note", _optional_text(self.environment_note))
        object.__setattr__(self, "property_id", _optional_uuid(self.property_id, "property_id"))
        keys = [item.definition_key for item in self.characteristics]
        if len(keys) != len(set(keys)):
            raise ValueError("subject characteristic definition keys must be unique")


@dataclass(frozen=True, slots=True)
class SaveComparable:
    case_id: str
    comparable_order: int
    legal_address: str
    current_address: str
    completeness_status: str
    asking_or_sale_price_vnd: DecimalInput
    negotiated_price_vnd: DecimalInput
    display_name: str | None = None
    latitude: OptionalDecimalInput = None
    longitude: OptionalDecimalInput = None
    planning_note: str | None = None
    environment_note: str | None = None
    negotiation_rate_pct: OptionalDecimalInput = None
    observation_date: str | None = None
    observation_note: str | None = None
    property_id: str | None = None
    market_observation_id: str | None = None
    characteristics: tuple[CharacteristicInput, ...] = ()
    evidence: tuple[EvidenceInput, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "case_id", _nonempty(self.case_id, "case_id"))
        if isinstance(self.comparable_order, bool) or self.comparable_order not in (1, 2, 3):
            raise ValueError("comparable_order must be one of 1, 2, 3")
        object.__setattr__(self, "legal_address", _nonempty(self.legal_address, "legal_address"))
        object.__setattr__(self, "current_address", _nonempty(self.current_address, "current_address"))
        object.__setattr__(self, "completeness_status", _nonempty(self.completeness_status, "completeness_status"))
        object.__setattr__(
            self,
            "asking_or_sale_price_vnd",
            _decimal_text(self.asking_or_sale_price_vnd, "asking_or_sale_price_vnd", minimum=Decimal("0")),
        )
        object.__setattr__(
            self,
            "negotiated_price_vnd",
            _decimal_text(self.negotiated_price_vnd, "negotiated_price_vnd", minimum=Decimal("0")),
        )
        object.__setattr__(
            self,
            "negotiation_rate_pct",
            _decimal_text(self.negotiation_rate_pct, "negotiation_rate_pct"),
        )
        object.__setattr__(
            self, "latitude", _decimal_text(self.latitude, "latitude", minimum=Decimal("-90"), maximum=Decimal("90"))
        )
        object.__setattr__(
            self, "longitude", _decimal_text(self.longitude, "longitude", minimum=Decimal("-180"), maximum=Decimal("180"))
        )
        object.__setattr__(self, "display_name", _optional_text(self.display_name))
        object.__setattr__(self, "planning_note", _optional_text(self.planning_note))
        object.__setattr__(self, "environment_note", _optional_text(self.environment_note))
        object.__setattr__(self, "observation_date", _iso_date(self.observation_date, "observation_date"))
        object.__setattr__(self, "observation_note", _optional_text(self.observation_note))
        object.__setattr__(self, "property_id", _optional_uuid(self.property_id, "property_id"))
        object.__setattr__(self, "market_observation_id", _optional_uuid(self.market_observation_id, "market_observation_id"))
        keys = [item.definition_key for item in self.characteristics]
        if len(keys) != len(set(keys)):
            raise ValueError("comparable characteristic definition keys must be unique")
