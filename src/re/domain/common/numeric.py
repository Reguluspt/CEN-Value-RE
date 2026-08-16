"""Decimal-backed appraisal numeric value objects.

Binary floats are intentionally rejected at this boundary. Canonical appraisal
numbers must enter the domain as ``Decimal``, ``int`` or an exact decimal
string.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import TypeAlias

DecimalInput: TypeAlias = Decimal | int | str


def to_decimal(value: DecimalInput, *, field_name: str = "value") -> Decimal:
    """Return a finite Decimal without passing through binary floating point."""
    if isinstance(value, bool):
        raise TypeError(
            f"{field_name} must be Decimal, int, or decimal string; bool is not allowed"
        )
    if isinstance(value, float):
        raise TypeError(f"{field_name} must not be a binary float")
    if isinstance(value, Decimal):
        result = value
    elif isinstance(value, int):
        result = Decimal(value)
    elif isinstance(value, str):
        try:
            result = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError(f"{field_name} is not a valid decimal string") from exc
    else:
        raise TypeError(f"{field_name} must be Decimal, int, or decimal string")
    if not result.is_finite():
        raise ValueError(f"{field_name} must be finite")
    return result


@dataclass(frozen=True, slots=True)
class Money:
    """A VND monetary amount preserving exact decimal arithmetic."""

    amount_vnd: Decimal

    def __init__(self, amount_vnd: DecimalInput) -> None:
        object.__setattr__(
            self,
            "amount_vnd",
            to_decimal(amount_vnd, field_name="amount_vnd"),
        )


@dataclass(frozen=True, slots=True)
class Percentage:
    """Canonical percentage stored as a fraction (5% == Decimal("0.05"))."""

    fraction: Decimal

    def __init__(self, fraction: DecimalInput) -> None:
        object.__setattr__(self, "fraction", to_decimal(fraction, field_name="fraction"))


@dataclass(frozen=True, slots=True)
class UnitPrice:
    """A VND-per-square-metre unit price using exact decimal arithmetic."""

    amount_vnd_per_m2: Decimal

    def __init__(self, amount_vnd_per_m2: DecimalInput) -> None:
        object.__setattr__(
            self,
            "amount_vnd_per_m2",
            to_decimal(amount_vnd_per_m2, field_name="amount_vnd_per_m2"),
        )
