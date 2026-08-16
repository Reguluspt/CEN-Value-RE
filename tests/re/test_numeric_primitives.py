from decimal import Decimal

import pytest

from src.re.domain.common import Money, Percentage, UnitPrice, to_decimal


def test_percentage_uses_fraction_representation() -> None:
    assert Percentage(Decimal("0.05")).fraction == Decimal("0.05")
    assert Percentage("0").fraction == Decimal("0")
    assert Percentage("-0.10").fraction == Decimal("-0.10")


@pytest.mark.parametrize(
    ("factory", "field"),
    [
        (Money, "amount_vnd"),
        (Percentage, "fraction"),
        (UnitPrice, "amount_vnd_per_m2"),
    ],
)
def test_numeric_primitives_reject_binary_float(factory, field: str) -> None:
    with pytest.raises(TypeError, match="binary float"):
        factory(0.1)


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity"])
def test_numeric_primitives_reject_non_finite_values(value: str) -> None:
    with pytest.raises(ValueError, match="finite"):
        Money(value)


def test_money_and_unit_price_preserve_decimal_precision() -> None:
    money = Money("19581412440.000002")
    unit_price = UnitPrice("196308350.125")
    assert money.amount_vnd == Decimal("19581412440.000002")
    assert unit_price.amount_vnd_per_m2 == Decimal("196308350.125")


def test_to_decimal_accepts_exact_int_and_string_inputs() -> None:
    assert to_decimal(1_000) == Decimal("1000")
    assert to_decimal("19.35") == Decimal("19.35")
