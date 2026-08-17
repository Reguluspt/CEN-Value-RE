"""Pure-domain land and final valuation composition for E1-PR-004."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, localcontext

from ..common.numeric import DecimalInput, to_decimal
from ..common.rounding import RoundingPolicy, TOTAL_VALUE_TARGET


MARKET_INDICATED = "MARKET_INDICATED"
OFFICIAL_LAND_PRICE = "OFFICIAL_LAND_PRICE"
OTHER_MANUAL_BASIS = "OTHER_MANUAL_BASIS"


class FinalCompositionValidationError(ValueError):
    """Raised when final-composition inputs violate the frozen contract."""


@dataclass(frozen=True, slots=True)
class LandComponentInput:
    component_id: str
    component_order: int
    planning_status: str
    area_m2: Decimal
    valuation_basis: str
    include_in_final_value: bool
    explicit_unit_price_vnd_per_m2: Decimal | None = None
    policy_version: str | None = None
    note: str | None = None
    parcel_id: str | None = None

    @classmethod
    def build(
        cls,
        *,
        component_id: str,
        component_order: int,
        planning_status: str,
        area_m2: DecimalInput,
        valuation_basis: str,
        include_in_final_value: bool,
        explicit_unit_price_vnd_per_m2: DecimalInput | None = None,
        policy_version: str | None = None,
        note: str | None = None,
        parcel_id: str | None = None,
    ) -> "LandComponentInput":
        if not isinstance(component_id, str) or not component_id.strip():
            raise FinalCompositionValidationError("component_id must be non-empty")
        if isinstance(component_order, bool) or not isinstance(component_order, int) or component_order <= 0:
            raise FinalCompositionValidationError("component_order must be a positive integer")
        if planning_status not in {"COMPLIANT", "NON_COMPLIANT", "UNKNOWN"}:
            raise FinalCompositionValidationError("unsupported planning_status")
        if valuation_basis not in {
            MARKET_INDICATED,
            OFFICIAL_LAND_PRICE,
            OTHER_MANUAL_BASIS,
        }:
            raise FinalCompositionValidationError("unsupported valuation_basis")
        if not isinstance(include_in_final_value, bool):
            raise FinalCompositionValidationError("include_in_final_value must be boolean")
        area = to_decimal(area_m2, field_name="area_m2")
        if area < 0:
            raise FinalCompositionValidationError("area_m2 must not be negative")
        unit_price = None
        if explicit_unit_price_vnd_per_m2 is not None:
            unit_price = to_decimal(
                explicit_unit_price_vnd_per_m2,
                field_name="explicit_unit_price_vnd_per_m2",
            )
            if unit_price < 0:
                raise FinalCompositionValidationError(
                    "explicit_unit_price_vnd_per_m2 must not be negative"
                )
        return cls(
            component_id=component_id.strip(),
            component_order=component_order,
            planning_status=planning_status,
            area_m2=area,
            valuation_basis=valuation_basis,
            include_in_final_value=include_in_final_value,
            explicit_unit_price_vnd_per_m2=unit_price,
            policy_version=policy_version,
            note=note,
            parcel_id=parcel_id,
        )


@dataclass(frozen=True, slots=True)
class ComposedLandComponent:
    component_id: str
    component_order: int
    planning_status: str
    area_m2: Decimal
    valuation_basis: str
    effective_unit_price_vnd_per_m2: Decimal
    amount_vnd: Decimal
    policy_version: str | None
    note: str | None
    parcel_id: str | None


@dataclass(frozen=True, slots=True)
class FinalValuationComposition:
    land_components: tuple[ComposedLandComponent, ...]
    compliant_residential_land_value_vnd: Decimal
    other_recognized_land_value_vnd: Decimal
    recognized_land_value_vnd: Decimal
    construction_value_total_vnd: Decimal
    total_value_before_rounding_vnd: Decimal
    final_appraised_value_vnd: Decimal
    total_value_rounding_policy: RoundingPolicy


def _whole_vnd(value: Decimal) -> Decimal:
    tup = value.as_tuple()
    required_precision = len(tup.digits) + abs(tup.exponent) + 16
    with localcontext() as context:
        context.prec = max(50, required_precision)
        return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def compose_final_valuation(
    *,
    rounded_human_indication_vnd_per_m2: DecimalInput,
    land_components: tuple[LandComponentInput, ...],
    supplied_construction_aggregate_vnd: DecimalInput,
    total_value_rounding_policy: RoundingPolicy,
) -> FinalValuationComposition:
    """Compose land + supplied CTXD aggregate and preserve G181/G182 semantics."""

    indicated = to_decimal(
        rounded_human_indication_vnd_per_m2,
        field_name="rounded_human_indication_vnd_per_m2",
    )
    if indicated < 0:
        raise FinalCompositionValidationError(
            "rounded_human_indication_vnd_per_m2 must not be negative"
        )
    construction = to_decimal(
        supplied_construction_aggregate_vnd,
        field_name="supplied_construction_aggregate_vnd",
    )
    if construction < 0:
        raise FinalCompositionValidationError(
            "supplied_construction_aggregate_vnd must not be negative"
        )
    if not isinstance(total_value_rounding_policy, RoundingPolicy):
        raise FinalCompositionValidationError(
            "total_value_rounding_policy must be RoundingPolicy"
        )
    if total_value_rounding_policy.target != TOTAL_VALUE_TARGET:
        raise FinalCompositionValidationError(
            "final appraisal composition requires TOTAL_VALUE rounding target"
        )
    if not land_components:
        raise FinalCompositionValidationError("at least one land component is required")

    ordered = tuple(sorted(land_components, key=lambda item: (item.component_order, item.component_id)))
    if len({item.component_id for item in ordered}) != len(ordered):
        raise FinalCompositionValidationError("land component IDs must be unique")

    composed: list[ComposedLandComponent] = []
    compliant_total = Decimal("0")
    other_total = Decimal("0")

    for component in ordered:
        if not component.include_in_final_value:
            continue
        if component.planning_status == "UNKNOWN":
            raise FinalCompositionValidationError(
                f"included land component {component.component_id} has UNKNOWN planning status"
            )
        if component.valuation_basis == MARKET_INDICATED:
            if component.planning_status != "COMPLIANT":
                raise FinalCompositionValidationError(
                    "MARKET_INDICATED land component must be COMPLIANT"
                )
            if (
                component.explicit_unit_price_vnd_per_m2 is not None
                and component.explicit_unit_price_vnd_per_m2 != indicated
            ):
                raise FinalCompositionValidationError(
                    "MARKET_INDICATED explicit unit price conflicts with current human indication"
                )
            unit_price = indicated
        else:
            if component.planning_status != "NON_COMPLIANT":
                raise FinalCompositionValidationError(
                    "non-market included land component must be NON_COMPLIANT"
                )
            if component.explicit_unit_price_vnd_per_m2 is None:
                raise FinalCompositionValidationError(
                    "noncompliant/planning land component requires explicit unit price"
                )
            if not (
                (isinstance(component.policy_version, str) and component.policy_version.strip())
                or (isinstance(component.note, str) and component.note.strip())
            ):
                raise FinalCompositionValidationError(
                    "noncompliant/planning land unit price requires provenance metadata"
                )
            unit_price = component.explicit_unit_price_vnd_per_m2

        with localcontext() as context:
            context.prec = max(
                50,
                len(component.area_m2.as_tuple().digits)
                + len(unit_price.as_tuple().digits)
                + 24,
            )
            amount = component.area_m2 * unit_price
        row = ComposedLandComponent(
            component_id=component.component_id,
            component_order=component.component_order,
            planning_status=component.planning_status,
            area_m2=component.area_m2,
            valuation_basis=component.valuation_basis,
            effective_unit_price_vnd_per_m2=unit_price,
            amount_vnd=amount,
            policy_version=component.policy_version,
            note=component.note,
            parcel_id=component.parcel_id,
        )
        composed.append(row)
        if component.planning_status == "COMPLIANT":
            compliant_total += amount
        else:
            other_total += amount

    if not composed:
        raise FinalCompositionValidationError(
            "at least one included land component is required"
        )
    if not any(item.valuation_basis == MARKET_INDICATED for item in composed):
        raise FinalCompositionValidationError(
            "final composition requires a compliant MARKET_INDICATED land component"
        )

    recognized_land = compliant_total + other_total
    total_before_rounding = _whole_vnd(recognized_land + construction)
    final_rounding = total_value_rounding_policy.apply(total_before_rounding)

    return FinalValuationComposition(
        land_components=tuple(composed),
        compliant_residential_land_value_vnd=compliant_total,
        other_recognized_land_value_vnd=other_total,
        recognized_land_value_vnd=recognized_land,
        construction_value_total_vnd=construction,
        total_value_before_rounding_vnd=total_before_rounding,
        final_appraised_value_vnd=final_rounding.rounded_value,
        total_value_rounding_policy=total_value_rounding_policy,
    )
