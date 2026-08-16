from datetime import datetime, timezone
from decimal import Decimal, localcontext

import pytest

from src.re.domain.common import (
    TOTAL_VALUE_TARGET,
    UNIT_PRICE_TARGET,
    RoundingPolicy,
    RoundingSource,
    RoundingTarget,
    resolve_rounding_policy,
)


def policy(target, increment, source=RoundingSource.APPLICATION_DEFAULT, **kwargs):
    return RoundingPolicy(
        target=target,
        increment_vnd=increment,
        source=source,
        **kwargs,
    )


@pytest.mark.parametrize(
    ("increment", "expected"),
    [
        (1_000, Decimal("12346000")),
        (10_000, Decimal("12350000")),
        (100_000, Decimal("12300000")),
        (1_000_000, Decimal("12000000")),
        (10_000_000, Decimal("10000000")),
        (250_000, Decimal("12250000")),
    ],
)
def test_supported_and_custom_nearest_increments(
    increment: int, expected: Decimal
) -> None:
    result = policy(TOTAL_VALUE_TARGET, increment).apply("12345678")
    assert result.raw_value == Decimal("12345678")
    assert result.rounded_value == expected


def test_none_rounding_preserves_raw_value_exactly() -> None:
    result = policy(UNIT_PRICE_TARGET, None).apply("196308350.125")
    assert result.raw_value == Decimal("196308350.125")
    assert result.rounded_value == Decimal("196308350.125")


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1500", Decimal("2000")),
        ("-1500", Decimal("-2000")),
        ("1499.999", Decimal("1000")),
        ("-1499.999", Decimal("-1000")),
    ],
)
def test_nearest_rounding_is_excel_compatible_half_away_from_zero(
    raw, expected
) -> None:
    assert policy(TOTAL_VALUE_TARGET, 1000).apply(raw).rounded_value == expected


def test_rounding_rejects_binary_float_input() -> None:
    with pytest.raises(TypeError, match="binary float"):
        policy(TOTAL_VALUE_TARGET, 1000).apply(1.5)


@pytest.mark.parametrize("increment", [0, -1])
def test_increment_must_be_positive_whole_vnd(increment: int) -> None:
    with pytest.raises(ValueError, match="positive"):
        policy(TOTAL_VALUE_TARGET, increment)


@pytest.mark.parametrize("increment", [True, Decimal("1000"), 1000.0])
def test_increment_rejects_non_integer_types(increment) -> None:
    with pytest.raises(TypeError, match="whole-VND integer"):
        policy(TOTAL_VALUE_TARGET, increment)


def test_case_override_requires_audit_actor_and_timestamp() -> None:
    with pytest.raises(ValueError, match="selected_by"):
        policy(
            TOTAL_VALUE_TARGET,
            1_000_000,
            source=RoundingSource.CASE_OVERRIDE,
        )


def test_resolver_priority_case_then_template_then_application() -> None:
    selected_at = datetime(2026, 8, 16, tzinfo=timezone.utc)
    case = policy(
        TOTAL_VALUE_TARGET,
        None,
        source=RoundingSource.CASE_OVERRIDE,
        selected_by="appraiser-1",
        selected_at=selected_at,
    )
    profile = policy(
        TOTAL_VALUE_TARGET,
        1_000_000,
        source=RoundingSource.TEMPLATE_DEFAULT,
        profile_id="cenvalue-re-n08-0038-v1",
        profile_version="1",
    )
    application = policy(
        TOTAL_VALUE_TARGET,
        100_000,
        source=RoundingSource.APPLICATION_DEFAULT,
    )
    assert resolve_rounding_policy(
        target=TOTAL_VALUE_TARGET,
        case_override=case,
        profile_default=profile,
        application_default=application,
    ) is case

    assert resolve_rounding_policy(
        target=TOTAL_VALUE_TARGET,
        case_override=None,
        profile_default=profile,
        application_default=application,
    ) is profile

    assert resolve_rounding_policy(
        target=TOTAL_VALUE_TARGET,
        case_override=None,
        profile_default=None,
        application_default=application,
    ) is application


def test_explicit_none_case_override_is_not_treated_as_missing() -> None:
    case = policy(
        UNIT_PRICE_TARGET,
        None,
        source=RoundingSource.CASE_OVERRIDE,
        selected_by="appraiser-1",
        selected_at=datetime(2026, 8, 16, tzinfo=timezone.utc),
    )
    profile = policy(
        UNIT_PRICE_TARGET,
        1_000,
        source=RoundingSource.TEMPLATE_DEFAULT,
    )
    resolved = resolve_rounding_policy(
        target=UNIT_PRICE_TARGET,
        case_override=case,
        profile_default=profile,
        application_default=None,
    )
    assert resolved is case
    assert resolved.apply("196308350").rounded_value == Decimal("196308350")


def test_resolver_fails_closed_on_target_mismatch() -> None:
    profile = policy(
        UNIT_PRICE_TARGET,
        1_000,
        source=RoundingSource.TEMPLATE_DEFAULT,
    )
    with pytest.raises(ValueError, match="target"):
        resolve_rounding_policy(
            target=TOTAL_VALUE_TARGET,
            case_override=None,
            profile_default=profile,
            application_default=None,
        )


def test_n08_profile_defaults_reproduce_frozen_golden_values() -> None:
    unit_price_policy = policy(
        UNIT_PRICE_TARGET,
        1_000,
        source=RoundingSource.TEMPLATE_DEFAULT,
        profile_id="cenvalue-re-n08-0038-v1",
        profile_version="1",
    )
    total_value_policy = policy(
        TOTAL_VALUE_TARGET,
        1_000_000,
        source=RoundingSource.TEMPLATE_DEFAULT,
        profile_id="cenvalue-re-n08-0038-v1",
        profile_version="1",
    )

    indicated = unit_price_policy.apply("196308350")
    final_total = total_value_policy.apply("19581412440")

    assert indicated.raw_value == Decimal("196308350")
    assert indicated.rounded_value == Decimal("196308000")
    assert final_total.raw_value == Decimal("19581412440")
    assert final_total.rounded_value == Decimal("19581000000")


def test_rounding_target_is_extensible_without_core_enum_change() -> None:
    future_target = RoundingTarget("CONSTRUCTION_COMPONENT")
    future_policy = policy(future_target, 10_000)
    assert future_policy.apply("12345").rounded_value == Decimal("10000")


def test_rounding_is_independent_of_external_decimal_context_precision() -> None:
    p = policy(TOTAL_VALUE_TARGET, 1_000_000)
    with localcontext() as context:
        context.prec = 6
        result = p.apply("19581412440.123456789")
    assert result.raw_value == Decimal("19581412440.123456789")
    assert result.rounded_value == Decimal("19581000000")


def test_rounding_result_keeps_effective_policy_with_raw_and_rounded_values() -> None:
    p = policy(UNIT_PRICE_TARGET, 1_000)
    result = p.apply("196308350")
    assert result.policy is p
    assert result.raw_value == Decimal("196308350")
    assert result.rounded_value == Decimal("196308000")


def test_resolver_fails_closed_on_source_mismatch() -> None:
    wrong_source = policy(
        TOTAL_VALUE_TARGET,
        1_000_000,
        source=RoundingSource.APPLICATION_DEFAULT,
    )
    with pytest.raises(ValueError, match="source"):
        resolve_rounding_policy(
            target=TOTAL_VALUE_TARGET,
            case_override=None,
            profile_default=wrong_source,
            application_default=None,
        )


def test_resolver_requires_an_effective_policy() -> None:
    with pytest.raises(ValueError, match="no rounding policy"):
        resolve_rounding_policy(
            target=TOTAL_VALUE_TARGET,
            case_override=None,
            profile_default=None,
            application_default=None,
        )


def test_future_rounding_target_is_not_restricted_to_a_closed_enum() -> None:
    target = RoundingTarget("PROFILE:CONSTRUCTION_COMPONENT")
    assert target.key == "PROFILE:CONSTRUCTION_COMPONENT"
