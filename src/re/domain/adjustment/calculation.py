"""Deterministic market normalization and frozen N08 adjustment graph.

The domain owns appraisal math only. It has no dependency on persistence,
Flask, Excel, Astryx, Tauri, or provider infrastructure.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, localcontext

from ..common.numeric import DecimalInput, to_decimal


@dataclass(frozen=True, slots=True)
class AdjustmentFactorDefinition:
    factor_key: str
    canonical_key: str
    workbook_label: str
    order: int


N08_ADJUSTMENT_FACTORS: tuple[AdjustmentFactorDefinition, ...] = (
    AdjustmentFactorDefinition("C1", "legal_status", "Pháp lý", 1),
    AdjustmentFactorDefinition("C2", "location", "Vị trí", 2),
    AdjustmentFactorDefinition(
        "C3",
        "relative_distance_to_local_points",
        "Khoảng cách tương đối từ tài sản đến các địa điểm trong khu vực",
        3,
    ),
    AdjustmentFactorDefinition("C4", "scale_area", "Quy mô, diện tích", 4),
    AdjustmentFactorDefinition("C5", "frontage", "Mặt tiền", 5),
    AdjustmentFactorDefinition("C6", "depth", "Chiều dài", 6),
    AdjustmentFactorDefinition("C7", "shape", "Hình dáng", 7),
    AdjustmentFactorDefinition("C8", "traffic_access", "Giao thông", 8),
    AdjustmentFactorDefinition(
        "C9", "business_environment", "Môi trường kinh doanh", 9
    ),
    AdjustmentFactorDefinition(
        "C10", "infrastructure", "Hệ thống hạ tầng kỹ thuật", 10
    ),
    AdjustmentFactorDefinition(
        "C11", "other_disadvantage", "Yếu tố bất lợi khác", 11
    ),
)

N08_FACTOR_KEYS = tuple(item.factor_key for item in N08_ADJUSTMENT_FACTORS)


class IncompleteAdjustmentDecisionError(ValueError):
    """Raised when an adjustment run contains a missing/unreviewed decision."""


@dataclass(frozen=True, slots=True)
class SelectedAdjustmentDecision:
    factor_key: str
    selected_rate: Decimal | None
    selected_explicitly: bool = True

    def __init__(
        self,
        factor_key: str,
        selected_rate: DecimalInput | None,
        selected_explicitly: bool = True,
    ) -> None:
        if not isinstance(factor_key, str) or factor_key not in N08_FACTOR_KEYS:
            raise ValueError(f"unsupported adjustment factor key: {factor_key!r}")
        if not isinstance(selected_explicitly, bool):
            raise TypeError("selected_explicitly must be bool")
        rate = (
            None
            if selected_rate is None
            else to_decimal(selected_rate, field_name=f"{factor_key}.selected_rate")
        )
        object.__setattr__(self, "factor_key", factor_key)
        object.__setattr__(self, "selected_rate", rate)
        object.__setattr__(self, "selected_explicitly", selected_explicitly)


@dataclass(frozen=True, slots=True)
class AdjustmentStep:
    factor_key: str
    selected_rate: Decimal
    amount_base_vnd_per_m2: Decimal
    adjustment_amount_vnd_per_m2: Decimal
    running_price_vnd_per_m2: Decimal


@dataclass(frozen=True, slots=True)
class AdjustmentRunSnapshot:
    normalized_base_price_vnd_per_m2: Decimal
    property_adjustment_base_vnd_per_m2: Decimal
    steps: tuple[AdjustmentStep, ...]
    indicated_unit_price_vnd_per_m2: Decimal


@dataclass(frozen=True, slots=True)
class ComparableLandUnitPriceSnapshot:
    normalized_property_price_vnd: Decimal
    supplied_construction_value_vnd: Decimal
    land_use_conversion_cost_vnd: Decimal
    denominator_area_m2: Decimal
    used_converted_land_area: bool
    land_unit_price_vnd_per_m2: Decimal


def _round_to_increment(value: Decimal, increment: int) -> Decimal:
    if isinstance(increment, bool) or not isinstance(increment, int) or increment <= 0:
        raise ValueError("increment must be a positive whole integer")
    with localcontext() as context:
        context.prec = max(80, len(value.as_tuple().digits) + 40)
        unit = Decimal(increment)
        return (value / unit).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * unit


def normalize_market_price(
    *, asking_price_vnd: DecimalInput, transaction_success_factor: DecimalInput
) -> Decimal:
    """Apply the frozen N08 asking-price normalization and 10m-VND rounding."""
    asking = to_decimal(asking_price_vnd, field_name="asking_price_vnd")
    factor = to_decimal(
        transaction_success_factor, field_name="transaction_success_factor"
    )
    if asking < 0:
        raise ValueError("asking_price_vnd must not be negative")
    if factor < 0:
        raise ValueError("transaction_success_factor must not be negative")
    with localcontext() as context:
        context.prec = max(80, len(asking.as_tuple().digits) + 40)
        return _round_to_increment(asking * factor, 10_000_000)


def derive_comparable_land_unit_price(
    *,
    normalized_property_price_vnd: DecimalInput,
    supplied_construction_value_vnd: DecimalInput,
    converted_land_area_m2: DecimalInput | None,
    total_land_area_m2: DecimalInput,
    land_use_conversion_cost_vnd: DecimalInput = 0,
) -> ComparableLandUnitPriceSnapshot:
    """Derive frozen N08 P0 without implementing the CTXD calculation engine."""
    normalized = to_decimal(
        normalized_property_price_vnd, field_name="normalized_property_price_vnd"
    )
    construction = to_decimal(
        supplied_construction_value_vnd,
        field_name="supplied_construction_value_vnd",
    )
    total_area = to_decimal(total_land_area_m2, field_name="total_land_area_m2")
    conversion_cost = to_decimal(
        land_use_conversion_cost_vnd, field_name="land_use_conversion_cost_vnd"
    )
    converted = (
        None
        if converted_land_area_m2 is None
        else to_decimal(converted_land_area_m2, field_name="converted_land_area_m2")
    )
    if normalized < 0 or construction < 0 or conversion_cost < 0:
        raise ValueError("market/construction/conversion values must not be negative")
    if total_area <= 0:
        raise ValueError("total_land_area_m2 must be positive")

    use_converted = converted is not None and converted > 0
    denominator = converted if use_converted else total_area
    if denominator is None or denominator <= 0:
        raise ValueError("land-unit-price denominator must be positive")

    with localcontext() as context:
        context.prec = max(80, len(normalized.as_tuple().digits) + 40)
        numerator = normalized - construction
        if not use_converted:
            numerator += conversion_cost
        raw = numerator / denominator
        rounded = _round_to_increment(raw, 1_000)

    return ComparableLandUnitPriceSnapshot(
        normalized_property_price_vnd=normalized,
        supplied_construction_value_vnd=construction,
        land_use_conversion_cost_vnd=conversion_cost,
        denominator_area_m2=denominator,
        used_converted_land_area=use_converted,
        land_unit_price_vnd_per_m2=rounded,
    )


def calculate_adjustment_run(
    *,
    normalized_base_price_vnd_per_m2: DecimalInput,
    decisions: tuple[SelectedAdjustmentDecision, ...],
) -> AdjustmentRunSnapshot:
    """Calculate the frozen N08 C1-C11 graph.

    C1 uses P0. C2 uses P1. C3-C11 also use P1 as amount base while their
    amounts accumulate into the running indicated price.
    """
    p0 = to_decimal(
        normalized_base_price_vnd_per_m2,
        field_name="normalized_base_price_vnd_per_m2",
    )
    if p0 < 0:
        raise ValueError("normalized_base_price_vnd_per_m2 must not be negative")
    if len(decisions) != len(N08_FACTOR_KEYS):
        raise IncompleteAdjustmentDecisionError(
            f"complete adjustment run requires {len(N08_FACTOR_KEYS)} decisions"
        )
    received_keys = tuple(item.factor_key for item in decisions)
    if received_keys != N08_FACTOR_KEYS:
        raise ValueError(
            f"adjustment decisions must use frozen order {N08_FACTOR_KEYS!r}"
        )
    for item in decisions:
        if item.selected_rate is None or not item.selected_explicitly:
            raise IncompleteAdjustmentDecisionError(
                f"{item.factor_key} is missing/unreviewed; explicit zero is valid but missing is not"
            )

    steps: list[AdjustmentStep] = []
    with localcontext() as context:
        context.prec = max(80, len(p0.as_tuple().digits) + 50)
        running = p0
        property_base: Decimal | None = None
        for index, decision in enumerate(decisions):
            rate = decision.selected_rate
            assert rate is not None
            if index == 0:
                amount_base = p0
            elif index == 1:
                assert property_base is not None
                amount_base = property_base
            else:
                assert property_base is not None
                amount_base = property_base
            amount = rate * amount_base
            running = running + amount
            if index == 0:
                property_base = running
            steps.append(
                AdjustmentStep(
                    factor_key=decision.factor_key,
                    selected_rate=rate,
                    amount_base_vnd_per_m2=amount_base,
                    adjustment_amount_vnd_per_m2=amount,
                    running_price_vnd_per_m2=running,
                )
            )

    assert property_base is not None
    return AdjustmentRunSnapshot(
        normalized_base_price_vnd_per_m2=p0,
        property_adjustment_base_vnd_per_m2=property_base,
        steps=tuple(steps),
        indicated_unit_price_vnd_per_m2=running,
    )
