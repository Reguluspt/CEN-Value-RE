"""Explicit Excel-compatible nearest-increment rounding primitives."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP, localcontext
from enum import Enum

from .numeric import DecimalInput, to_decimal

_TARGET_KEY = re.compile(r"^[A-Z][A-Z0-9_]*$")


@dataclass(frozen=True, slots=True)
class RoundingTarget:
    """Open target identifier so future profiles can declare new targets."""

    key: str

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not _TARGET_KEY.fullmatch(self.key):
            raise ValueError("rounding target must be an uppercase identifier")


UNIT_PRICE_TARGET = RoundingTarget("UNIT_PRICE")
TOTAL_VALUE_TARGET = RoundingTarget("TOTAL_VALUE")


class RoundingMode(str, Enum):
    NEAREST = "NEAREST"


class RoundingSource(str, Enum):
    TEMPLATE_DEFAULT = "TEMPLATE_DEFAULT"
    CASE_OVERRIDE = "CASE_OVERRIDE"
    APPLICATION_DEFAULT = "APPLICATION_DEFAULT"


@dataclass(frozen=True, slots=True)
class RoundingPolicy:
    """Nearest-increment policy.

    ``increment_vnd=None`` represents NONE. Any explicit increment must be a
    positive whole-VND integer, which includes the frozen 1k/10k/100k/1m/10m
    presets and CUSTOM_INCREMENT values.
    """

    target: RoundingTarget
    increment_vnd: int | None
    source: RoundingSource
    mode: RoundingMode = RoundingMode.NEAREST
    profile_id: str | None = None
    profile_version: str | None = None
    selected_by: str | None = None
    selected_at: datetime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.target, RoundingTarget):
            raise TypeError("target must be RoundingTarget")
        if not isinstance(self.source, RoundingSource):
            raise TypeError("source must be RoundingSource")
        if not isinstance(self.mode, RoundingMode):
            raise TypeError("mode must be RoundingMode")
        if self.mode is not RoundingMode.NEAREST:
            raise ValueError("only NEAREST rounding is supported in E0-PR-003")

        if self.increment_vnd is not None:
            if isinstance(self.increment_vnd, bool) or not isinstance(
                self.increment_vnd, int
            ):
                raise TypeError("increment_vnd must be a whole-VND integer or None")
            if self.increment_vnd <= 0:
                raise ValueError("increment_vnd must be positive")

        if self.selected_at is not None and not isinstance(self.selected_at, datetime):
            raise TypeError("selected_at must be datetime or None")

        if self.source is RoundingSource.CASE_OVERRIDE:
            if not self.selected_by:
                raise ValueError("case override requires selected_by")
            if self.selected_at is None:
                raise ValueError("case override requires selected_at")
        elif self.selected_by is not None or self.selected_at is not None:
            raise ValueError("selected_by/selected_at are only valid for case overrides")

    def apply(self, raw_value: DecimalInput) -> "RoundingResult":
        raw = to_decimal(raw_value, field_name="raw_value")
        if self.increment_vnd is None:
            rounded = raw
        else:
            increment = Decimal(self.increment_vnd)
            raw_tuple = raw.as_tuple()
            required_precision = (
                len(raw_tuple.digits)
                + abs(raw_tuple.exponent)
                + len(str(self.increment_vnd))
                + 16
            )
            with localcontext() as context:
                context.prec = max(50, required_precision)
                units = (raw / increment).quantize(
                    Decimal("1"), rounding=ROUND_HALF_UP
                )
                rounded = units * increment
        return RoundingResult(policy=self, raw_value=raw, rounded_value=rounded)


@dataclass(frozen=True, slots=True)
class RoundingResult:
    """Applied policy plus immutable raw and rounded values for snapshots."""

    policy: RoundingPolicy
    raw_value: Decimal
    rounded_value: Decimal


def resolve_rounding_policy(
    *,
    target: RoundingTarget,
    case_override: RoundingPolicy | None,
    profile_default: RoundingPolicy | None,
    application_default: RoundingPolicy | None,
) -> RoundingPolicy:
    """Resolve case override -> profile default -> application default."""

    if not isinstance(target, RoundingTarget):
        raise TypeError("target must be RoundingTarget")

    candidates = (
        (case_override, RoundingSource.CASE_OVERRIDE, "case_override"),
        (profile_default, RoundingSource.TEMPLATE_DEFAULT, "profile_default"),
        (
            application_default,
            RoundingSource.APPLICATION_DEFAULT,
            "application_default",
        ),
    )
    for policy, expected_source, name in candidates:
        if policy is None:
            continue
        if policy.target != target:
            raise ValueError(
                f"{name} target does not match requested target {target.key}"
            )
        if policy.source is not expected_source:
            raise ValueError(f"{name} source must be {expected_source.value}")
        return policy
    raise ValueError(f"no rounding policy available for target {target.key}")
