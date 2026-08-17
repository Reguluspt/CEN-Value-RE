from src.re.adapters.excel import (
    N08_0038_PROFILE,
    SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS,
)


def test_n08_profile_declares_frozen_rounding_defaults():
    unit = N08_0038_PROFILE.rounding_default_for("UNIT_PRICE")
    total = N08_0038_PROFILE.rounding_default_for("TOTAL_VALUE")

    assert unit is not None
    assert unit.mode == "NEAREST"
    assert unit.increment_vnd == 1_000
    assert total is not None
    assert total.mode == "NEAREST"
    assert total.increment_vnd == 1_000_000


def test_trusted_resolver_returns_n08_unit_price_default_from_profile():
    resolved = SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS.resolve(
        profile_id="cenvalue-re-n08-0038-v1",
        profile_version="1",
        target="UNIT_PRICE",
    )

    assert resolved is not None
    assert resolved.profile_id == "cenvalue-re-n08-0038-v1"
    assert resolved.profile_version == "1"
    assert resolved.target == "UNIT_PRICE"
    assert resolved.mode == "NEAREST"
    assert resolved.increment_vnd == 1_000


def test_trusted_resolver_fails_closed_for_unknown_profile_or_target():
    assert (
        SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS.resolve(
            profile_id="unknown-profile",
            profile_version="1",
            target="UNIT_PRICE",
        )
        is None
    )
    assert (
        SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS.resolve(
            profile_id="cenvalue-re-n08-0038-v1",
            profile_version="1",
            target="UNKNOWN_TARGET",
        )
        is None
    )
