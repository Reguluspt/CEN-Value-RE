import json
from decimal import Decimal
from pathlib import Path

import pytest

from src.re.domain.adjustment import SelectedAdjustmentDecision, calculate_adjustment_run
from src.re.domain.valuation import (
    ComparableQualityMetrics,
    build_minimum_gross_guidance,
    calculate_comparable_quality,
    evaluate_15_percent_readiness,
)


_FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "GOLDEN_CASE_ADJUSTMENT_DECISIONS_v1.json"
)


def _golden_metrics():
    fixture = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    p0_by_comparable = {
        "TSSS01": "230951000",
        "TSSS02": "239035000",
        "TSSS03": "196483000",
    }
    output = []
    for comparable in fixture["comparables"]:
        decisions = tuple(
            SelectedAdjustmentDecision(
                decision["factor_key"],
                decision["selected_rate_fraction"],
                selected_explicitly=decision["selected_explicitly"],
            )
            for decision in comparable["decisions"]
        )
        run = calculate_adjustment_run(
            normalized_base_price_vnd_per_m2=p0_by_comparable[comparable["comparable_id"]],
            decisions=decisions,
        )
        output.append(
            calculate_comparable_quality(
                comparable_property_id=comparable["comparable_id"], run=run
            )
        )
    return tuple(output)


def _metric(comp_id: str, price: str, gross: str = "1"):
    return ComparableQualityMetrics(
        comparable_property_id=comp_id,
        indicated_unit_price_vnd_per_m2=Decimal(price),
        gross_adjustment_value_vnd_per_m2=Decimal(gross),
        net_adjustment_value_vnd_per_m2=Decimal("0"),
        adjustment_count=0,
        min_abs_nonzero_rate=None,
        max_abs_nonzero_rate=None,
    )


def test_golden_quality_metrics_match_frozen_manifest():
    t1, t2, t3 = _golden_metrics()

    assert t1.indicated_unit_price_vnd_per_m2 == Decimal("196308350")
    assert t1.adjustment_count == 2
    assert t1.gross_adjustment_value_vnd_per_m2 == Decimal("34642650")
    assert t1.net_adjustment_value_vnd_per_m2 == Decimal("-34642650")
    assert t1.min_abs_nonzero_rate == Decimal("0.05")
    assert t1.max_abs_nonzero_rate == Decimal("0.1")
    assert t1.amplitude_percentage_points == "5–10"

    assert t2.indicated_unit_price_vnd_per_m2 == Decimal("227083250")
    assert t2.adjustment_count == 4
    assert t2.gross_adjustment_value_vnd_per_m2 == Decimal("83662250")
    assert t2.net_adjustment_value_vnd_per_m2 == Decimal("-11951750")
    assert t2.min_abs_nonzero_rate == Decimal("0.05")
    assert t2.max_abs_nonzero_rate == Decimal("0.15")
    assert t2.amplitude_percentage_points == "5–15"

    assert t3.indicated_unit_price_vnd_per_m2 == Decimal("212201640")
    assert t3.adjustment_count == 4
    assert t3.gross_adjustment_value_vnd_per_m2 == Decimal("35366940")
    assert t3.net_adjustment_value_vnd_per_m2 == Decimal("15718640")
    assert t3.min_abs_nonzero_rate == Decimal("0.03")
    assert t3.max_abs_nonzero_rate == Decimal("0.05")
    assert t3.amplitude_percentage_points == "3–5"


def test_zero_rates_are_valid_but_excluded_from_count_and_amplitude():
    decisions = tuple(
        SelectedAdjustmentDecision(f"C{index}", "0") for index in range(1, 12)
    )
    run = calculate_adjustment_run(
        normalized_base_price_vnd_per_m2="1000", decisions=decisions
    )
    metrics = calculate_comparable_quality(comparable_property_id="comp", run=run)
    assert metrics.adjustment_count == 0
    assert metrics.gross_adjustment_value_vnd_per_m2 == 0
    assert metrics.net_adjustment_value_vnd_per_m2 == 0
    assert metrics.min_abs_nonzero_rate is None
    assert metrics.max_abs_nonzero_rate is None
    assert metrics.amplitude_percentage_points is None


def test_golden_readiness_is_ready_and_uses_arithmetic_average():
    readiness = evaluate_15_percent_readiness(_golden_metrics())
    assert readiness.average_indicated_unit_price_vnd_per_m2 == Decimal(
        "211864413.3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333"
    )
    assert readiness.status == "READY"
    assert all(item.within_15_percent for item in readiness.items)


@pytest.mark.parametrize(
    ("prices", "expected_status", "expected_flags"),
    (
        (("85", "100", "115"), "READY", (True, True, True)),
        (("86", "100", "114"), "READY", (True, True, True)),
        (("84", "100", "116"), "NEEDS_REVIEW", (False, True, False)),
    ),
)
def test_15_percent_readiness_exact_inside_and_outside(prices, expected_status, expected_flags):
    metrics = tuple(_metric(f"c{index}", price) for index, price in enumerate(prices, 1))
    readiness = evaluate_15_percent_readiness(metrics)
    assert readiness.status == expected_status
    assert tuple(item.within_15_percent for item in readiness.items) == expected_flags


def test_golden_guidance_recommends_unique_minimum_gross_comparable():
    guidance = build_minimum_gross_guidance(_golden_metrics())
    assert guidance.kind == "COMPARABLE"
    assert guidance.recommended_comparable_id == "TSSS01"
    assert guidance.candidate_comparable_ids == ("TSSS01",)
    assert guidance.proposed_indicated_unit_price_vnd_per_m2 == Decimal("196308350")


def test_zero_gross_tie_allows_only_frozen_average_branch():
    metrics = (
        _metric("c1", "90", "0"),
        _metric("c2", "110", "0"),
        _metric("c3", "120", "5"),
    )
    guidance = build_minimum_gross_guidance(metrics)
    assert guidance.kind == "ZERO_GROSS_AVERAGE"
    assert guidance.candidate_comparable_ids == ("c1", "c2")
    assert guidance.proposed_indicated_unit_price_vnd_per_m2 == Decimal("100")


def test_equal_nonzero_minimum_does_not_invent_average_rule():
    metrics = (
        _metric("c1", "90", "5"),
        _metric("c2", "110", "5"),
        _metric("c3", "120", "7"),
    )
    guidance = build_minimum_gross_guidance(metrics)
    assert guidance.kind == "AMBIGUOUS_MIN_GROSS"
    assert guidance.candidate_comparable_ids == ("c1", "c2")
    assert guidance.recommended_comparable_id is None
    assert guidance.proposed_indicated_unit_price_vnd_per_m2 is None


def test_readiness_fails_closed_when_average_is_not_positive():
    with pytest.raises(ValueError, match="positive"):
        evaluate_15_percent_readiness(
            (_metric("c1", "0"), _metric("c2", "0"), _metric("c3", "0"))
        )
