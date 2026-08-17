from decimal import Decimal, localcontext

import pytest

from src.re.domain.adjustment import (
    IncompleteAdjustmentDecisionError,
    N08_ADJUSTMENT_FACTORS,
    N08_FACTOR_KEYS,
    SelectedAdjustmentDecision,
    calculate_adjustment_run,
    derive_comparable_land_unit_price,
    normalize_market_price,
)


def _decisions(*, c1="0", c2="0", c3="0"):
    rates = {key: "0" for key in N08_FACTOR_KEYS}
    rates.update({"C1": c1, "C2": c2, "C3": c3})
    return tuple(SelectedAdjustmentDecision(key, rates[key]) for key in N08_FACTOR_KEYS)


def test_n08_registry_preserves_frozen_order_and_canonical_keys():
    assert tuple(item.factor_key for item in N08_ADJUSTMENT_FACTORS) == (
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C6",
        "C7",
        "C8",
        "C9",
        "C10",
        "C11",
    )
    assert tuple(item.canonical_key for item in N08_ADJUSTMENT_FACTORS) == (
        "legal_status",
        "location",
        "relative_distance_to_local_points",
        "scale_area",
        "frontage",
        "depth",
        "shape",
        "traffic_access",
        "business_environment",
        "infrastructure",
        "other_disadvantage",
    )


@pytest.mark.parametrize(
    ("asking", "factor", "expected"),
    (
        ("21500000000", "0.85", "18280000000"),
        ("88000000000", "0.85", "74800000000"),
        ("38000000000", "0.85", "32300000000"),
    ),
)
def test_market_normalization_reproduces_frozen_n08_vectors(asking, factor, expected):
    assert normalize_market_price(
        asking_price_vnd=asking,
        transaction_success_factor=factor,
    ) == Decimal(expected)


def test_land_unit_price_uses_supplied_construction_boundary_and_converted_area():
    snapshot = derive_comparable_land_unit_price(
        normalized_property_price_vnd="1000000000",
        supplied_construction_value_vnd="100000000",
        converted_land_area_m2="3",
        total_land_area_m2="10",
        land_use_conversion_cost_vnd="50000000",
    )
    assert snapshot.used_converted_land_area is True
    assert snapshot.denominator_area_m2 == Decimal("3")
    # Conversion cost does not participate when converted land area is used.
    assert snapshot.land_unit_price_vnd_per_m2 == Decimal("300000000")


def test_land_unit_price_fallback_uses_total_area_and_conversion_cost():
    snapshot = derive_comparable_land_unit_price(
        normalized_property_price_vnd="1000000000",
        supplied_construction_value_vnd="100000000",
        converted_land_area_m2="0",
        total_land_area_m2="10",
        land_use_conversion_cost_vnd="50000000",
    )
    assert snapshot.used_converted_land_area is False
    assert snapshot.denominator_area_m2 == Decimal("10")
    assert snapshot.land_unit_price_vnd_per_m2 == Decimal("95000000")


def test_explicit_zero_is_valid_selected_decision_and_kept_in_snapshot():
    snapshot = calculate_adjustment_run(
        normalized_base_price_vnd_per_m2="1000",
        decisions=_decisions(),
    )
    assert len(snapshot.steps) == 11
    assert snapshot.steps[0].selected_rate == Decimal("0")
    assert snapshot.steps[0].adjustment_amount_vnd_per_m2 == Decimal("0")
    assert snapshot.indicated_unit_price_vnd_per_m2 == Decimal("1000")


def test_missing_rate_does_not_collapse_to_zero():
    decisions = list(_decisions())
    decisions[4] = SelectedAdjustmentDecision("C5", None)
    with pytest.raises(IncompleteAdjustmentDecisionError, match="C5"):
        calculate_adjustment_run(
            normalized_base_price_vnd_per_m2="1000",
            decisions=tuple(decisions),
        )


def test_unreviewed_value_does_not_count_as_selected_even_when_zero():
    decisions = list(_decisions())
    decisions[6] = SelectedAdjustmentDecision("C7", "0", selected_explicitly=False)
    with pytest.raises(IncompleteAdjustmentDecisionError, match="C7"):
        calculate_adjustment_run(
            normalized_base_price_vnd_per_m2="1000",
            decisions=tuple(decisions),
        )


def test_wrong_factor_order_fails_closed():
    decisions = list(_decisions())
    decisions[0], decisions[1] = decisions[1], decisions[0]
    with pytest.raises(ValueError, match="frozen order"):
        calculate_adjustment_run(
            normalized_base_price_vnd_per_m2="1000",
            decisions=tuple(decisions),
        )


def test_c3_amount_base_is_frozen_p1_not_previous_running_price():
    snapshot = calculate_adjustment_run(
        normalized_base_price_vnd_per_m2="1000",
        decisions=_decisions(c1="0.10", c2="0.10", c3="0.10"),
    )
    c1, c2, c3 = snapshot.steps[:3]
    assert c1.adjustment_amount_vnd_per_m2 == Decimal("100")
    assert c1.running_price_vnd_per_m2 == Decimal("1100")
    assert snapshot.property_adjustment_base_vnd_per_m2 == Decimal("1100")
    assert c2.amount_base_vnd_per_m2 == Decimal("1100")
    assert c2.adjustment_amount_vnd_per_m2 == Decimal("110.00")
    assert c2.running_price_vnd_per_m2 == Decimal("1210.00")
    # Generic full compounding would produce 121 here. Frozen N08 produces 110.
    assert c3.amount_base_vnd_per_m2 == Decimal("1100")
    assert c3.adjustment_amount_vnd_per_m2 == Decimal("110.00")
    assert c3.running_price_vnd_per_m2 == Decimal("1320.00")


def test_calculation_is_deterministic_under_low_ambient_decimal_precision():
    expected = calculate_adjustment_run(
        normalized_base_price_vnd_per_m2="230951000",
        decisions=_decisions(c1="-0.05", c2="0.10", c3="-0.03"),
    )
    with localcontext() as context:
        context.prec = 6
        actual = calculate_adjustment_run(
            normalized_base_price_vnd_per_m2="230951000",
            decisions=_decisions(c1="-0.05", c2="0.10", c3="-0.03"),
        )
    assert actual == expected


@pytest.mark.parametrize(
    "call",
    (
        lambda: normalize_market_price(
            asking_price_vnd=1.5, transaction_success_factor="0.85"
        ),
        lambda: normalize_market_price(
            asking_price_vnd="100", transaction_success_factor=0.85
        ),
        lambda: calculate_adjustment_run(
            normalized_base_price_vnd_per_m2=1000.0,
            decisions=_decisions(),
        ),
    ),
)
def test_binary_float_is_rejected_at_canonical_numeric_boundary(call):
    with pytest.raises(TypeError):
        call()
