from datetime import datetime, timezone
from decimal import Decimal, localcontext

import pytest

from src.re.domain.common.rounding import (
    RoundingPolicy,
    RoundingSource,
    TOTAL_VALUE_TARGET,
)
from src.re.domain.valuation import (
    FinalCompositionValidationError,
    LandComponentInput,
    compose_final_valuation,
)


def _n08_policy():
    return RoundingPolicy(
        target=TOTAL_VALUE_TARGET,
        increment_vnd=1_000_000,
        source=RoundingSource.TEMPLATE_DEFAULT,
        profile_id="cenvalue-re-n08-0038-v1",
        profile_version="1",
    )


def _golden_components():
    return (
        LandComponentInput.build(
            component_id="land-compliant",
            component_order=1,
            planning_status="COMPLIANT",
            area_m2="82.93",
            valuation_basis="MARKET_INDICATED",
            include_in_final_value=True,
        ),
        LandComponentInput.build(
            component_id="land-noncompliant",
            component_order=2,
            planning_status="NON_COMPLIANT",
            area_m2="20.27",
            valuation_basis="OFFICIAL_LAND_PRICE",
            include_in_final_value=True,
            explicit_unit_price_vnd_per_m2="106000000",
            policy_version="N08-0038:Nhap lieu!I31",
        ),
    )


def test_n08_golden_final_composition_preserves_g181_and_g182():
    result = compose_final_valuation(
        rounded_human_indication_vnd_per_m2="196308000",
        land_components=_golden_components(),
        supplied_construction_aggregate_vnd="1152970000",
        total_value_rounding_policy=_n08_policy(),
    )

    assert result.compliant_residential_land_value_vnd == Decimal("16279822440")
    assert result.other_recognized_land_value_vnd == Decimal("2148620000")
    assert result.recognized_land_value_vnd == Decimal("18428442440")
    assert result.construction_value_total_vnd == Decimal("1152970000")
    assert result.total_value_before_rounding_vnd == Decimal("19581412440")
    assert result.final_appraised_value_vnd == Decimal("19581000000")
    assert result.total_value_before_rounding_vnd != result.final_appraised_value_vnd


def test_market_indicated_component_uses_rounded_human_indication_not_raw():
    result = compose_final_valuation(
        rounded_human_indication_vnd_per_m2="196308000",
        land_components=(
            LandComponentInput.build(
                component_id="land",
                component_order=1,
                planning_status="COMPLIANT",
                area_m2="82.93",
                valuation_basis="MARKET_INDICATED",
                include_in_final_value=True,
            ),
        ),
        supplied_construction_aggregate_vnd="0",
        total_value_rounding_policy=_n08_policy(),
    )
    assert result.compliant_residential_land_value_vnd == Decimal("16279822440")


def test_conflicting_manual_price_on_market_indicated_component_fails_closed():
    with pytest.raises(FinalCompositionValidationError, match="conflicts"):
        compose_final_valuation(
            rounded_human_indication_vnd_per_m2="196308000",
            land_components=(
                LandComponentInput.build(
                    component_id="land",
                    component_order=1,
                    planning_status="COMPLIANT",
                    area_m2="82.93",
                    valuation_basis="MARKET_INDICATED",
                    include_in_final_value=True,
                    explicit_unit_price_vnd_per_m2="200000000",
                ),
            ),
            supplied_construction_aggregate_vnd="0",
            total_value_rounding_policy=_n08_policy(),
        )


def test_noncompliant_component_requires_explicit_price_and_provenance():
    base = dict(
        component_id="land-nc",
        component_order=2,
        planning_status="NON_COMPLIANT",
        area_m2="20.27",
        valuation_basis="OFFICIAL_LAND_PRICE",
        include_in_final_value=True,
    )
    with pytest.raises(FinalCompositionValidationError, match="explicit unit price"):
        compose_final_valuation(
            rounded_human_indication_vnd_per_m2="196308000",
            land_components=(
                LandComponentInput.build(
                    component_id="land-ok",
                    component_order=1,
                    planning_status="COMPLIANT",
                    area_m2="82.93",
                    valuation_basis="MARKET_INDICATED",
                    include_in_final_value=True,
                ),
                LandComponentInput.build(**base),
            ),
            supplied_construction_aggregate_vnd="0",
            total_value_rounding_policy=_n08_policy(),
        )
    with pytest.raises(FinalCompositionValidationError, match="provenance"):
        compose_final_valuation(
            rounded_human_indication_vnd_per_m2="196308000",
            land_components=(
                LandComponentInput.build(
                    component_id="land-ok",
                    component_order=1,
                    planning_status="COMPLIANT",
                    area_m2="82.93",
                    valuation_basis="MARKET_INDICATED",
                    include_in_final_value=True,
                ),
                LandComponentInput.build(
                    **base, explicit_unit_price_vnd_per_m2="106000000"
                ),
            ),
            supplied_construction_aggregate_vnd="0",
            total_value_rounding_policy=_n08_policy(),
        )


def test_total_value_case_override_is_distinct_and_auditable():
    override = RoundingPolicy(
        target=TOTAL_VALUE_TARGET,
        increment_vnd=10_000_000,
        source=RoundingSource.CASE_OVERRIDE,
        selected_by="appraiser-1",
        selected_at=datetime(2026, 8, 17, 15, 30, tzinfo=timezone.utc),
    )
    result = compose_final_valuation(
        rounded_human_indication_vnd_per_m2="196308000",
        land_components=_golden_components(),
        supplied_construction_aggregate_vnd="1152970000",
        total_value_rounding_policy=override,
    )
    assert result.total_value_before_rounding_vnd == Decimal("19581412440")
    assert result.final_appraised_value_vnd == Decimal("19580000000")
    assert result.total_value_rounding_policy is override


def test_composition_is_independent_of_ambient_decimal_precision():
    with localcontext() as context:
        context.prec = 6
        result = compose_final_valuation(
            rounded_human_indication_vnd_per_m2="196308000",
            land_components=_golden_components(),
            supplied_construction_aggregate_vnd="1152970000",
            total_value_rounding_policy=_n08_policy(),
        )
    assert result.total_value_before_rounding_vnd == Decimal("19581412440")
    assert result.final_appraised_value_vnd == Decimal("19581000000")


def test_binary_float_inputs_fail_closed():
    with pytest.raises(TypeError, match="binary float"):
        compose_final_valuation(
            rounded_human_indication_vnd_per_m2=196308000.0,
            land_components=_golden_components(),
            supplied_construction_aggregate_vnd="1152970000",
            total_value_rounding_policy=_n08_policy(),
        )
