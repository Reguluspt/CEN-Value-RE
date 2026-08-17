"""Comparable quality, 15% readiness and frozen indication guidance.

This module is pure domain logic. It consumes accepted E1-PR-002 adjustment
run snapshots and has no dependency on persistence, Flask, Excel, or UI code.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext

from ..adjustment import AdjustmentRunSnapshot

READINESS_THRESHOLD = Decimal("0.15")


@dataclass(frozen=True, slots=True)
class ComparableQualityMetrics:
    comparable_property_id: str
    indicated_unit_price_vnd_per_m2: Decimal
    gross_adjustment_value_vnd_per_m2: Decimal
    net_adjustment_value_vnd_per_m2: Decimal
    adjustment_count: int
    min_abs_nonzero_rate: Decimal | None
    max_abs_nonzero_rate: Decimal | None

    @property
    def amplitude_percentage_points(self) -> str | None:
        if self.min_abs_nonzero_rate is None or self.max_abs_nonzero_rate is None:
            return None
        return (
            f"{_percentage_points_text(self.min_abs_nonzero_rate)}"
            f"–{_percentage_points_text(self.max_abs_nonzero_rate)}"
        )


@dataclass(frozen=True, slots=True)
class ComparableReadinessItem:
    comparable_property_id: str
    indicated_unit_price_vnd_per_m2: Decimal
    deviation_fraction: Decimal
    within_15_percent: bool


@dataclass(frozen=True, slots=True)
class ComparableReadinessResult:
    average_indicated_unit_price_vnd_per_m2: Decimal
    items: tuple[ComparableReadinessItem, ...]
    status: str


@dataclass(frozen=True, slots=True)
class GuidanceResult:
    kind: str
    candidate_comparable_ids: tuple[str, ...]
    recommended_comparable_id: str | None
    proposed_indicated_unit_price_vnd_per_m2: Decimal | None
    reason_code: str


def _percentage_points_text(rate_fraction: Decimal) -> str:
    points = rate_fraction * Decimal(100)
    text = format(points, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def calculate_comparable_quality(
    *, comparable_property_id: str, run: AdjustmentRunSnapshot
) -> ComparableQualityMetrics:
    if not isinstance(comparable_property_id, str) or not comparable_property_id.strip():
        raise ValueError("comparable_property_id must be non-empty")
    if not isinstance(run, AdjustmentRunSnapshot):
        raise TypeError("run must be AdjustmentRunSnapshot")

    with localcontext() as context:
        context.prec = 100
        amounts = tuple(step.adjustment_amount_vnd_per_m2 for step in run.steps)
        nonzero_rates = tuple(
            abs(step.selected_rate) for step in run.steps if step.selected_rate != 0
        )
        gross = sum((abs(item) for item in amounts), Decimal(0))
        net = sum(amounts, Decimal(0))

    return ComparableQualityMetrics(
        comparable_property_id=comparable_property_id.strip(),
        indicated_unit_price_vnd_per_m2=run.indicated_unit_price_vnd_per_m2,
        gross_adjustment_value_vnd_per_m2=gross,
        net_adjustment_value_vnd_per_m2=net,
        adjustment_count=len(nonzero_rates),
        min_abs_nonzero_rate=min(nonzero_rates) if nonzero_rates else None,
        max_abs_nonzero_rate=max(nonzero_rates) if nonzero_rates else None,
    )


def evaluate_15_percent_readiness(
    metrics: tuple[ComparableQualityMetrics, ...],
) -> ComparableReadinessResult:
    if len(metrics) != 3:
        raise ValueError("Walking Skeleton readiness requires exactly three comparables")
    identifiers = tuple(item.comparable_property_id for item in metrics)
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("comparable_property_id values must be unique")

    with localcontext() as context:
        context.prec = 100
        average = sum(
            (item.indicated_unit_price_vnd_per_m2 for item in metrics), Decimal(0)
        ) / Decimal(len(metrics))
        if average <= 0:
            raise ValueError("average indicated unit price must be positive")
        items = tuple(
            ComparableReadinessItem(
                comparable_property_id=item.comparable_property_id,
                indicated_unit_price_vnd_per_m2=item.indicated_unit_price_vnd_per_m2,
                deviation_fraction=(
                    item.indicated_unit_price_vnd_per_m2 - average
                )
                / average,
                within_15_percent=abs(
                    (item.indicated_unit_price_vnd_per_m2 - average) / average
                )
                <= READINESS_THRESHOLD,
            )
            for item in metrics
        )
    return ComparableReadinessResult(
        average_indicated_unit_price_vnd_per_m2=average,
        items=items,
        status="READY" if all(item.within_15_percent for item in items) else "NEEDS_REVIEW",
    )


def build_minimum_gross_guidance(
    metrics: tuple[ComparableQualityMetrics, ...],
) -> GuidanceResult:
    if len(metrics) != 3:
        raise ValueError("Walking Skeleton guidance requires exactly three comparables")
    identifiers = tuple(item.comparable_property_id for item in metrics)
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("comparable_property_id values must be unique")

    minimum_gross = min(item.gross_adjustment_value_vnd_per_m2 for item in metrics)
    candidates = tuple(
        item for item in metrics if item.gross_adjustment_value_vnd_per_m2 == minimum_gross
    )
    candidate_ids = tuple(item.comparable_property_id for item in candidates)

    if len(candidates) == 1:
        candidate = candidates[0]
        return GuidanceResult(
            kind="COMPARABLE",
            candidate_comparable_ids=candidate_ids,
            recommended_comparable_id=candidate.comparable_property_id,
            proposed_indicated_unit_price_vnd_per_m2=candidate.indicated_unit_price_vnd_per_m2,
            reason_code="UNIQUE_MIN_GROSS_ADJUSTMENT",
        )

    if minimum_gross == 0:
        with localcontext() as context:
            context.prec = 100
            average = sum(
                (item.indicated_unit_price_vnd_per_m2 for item in candidates), Decimal(0)
            ) / Decimal(len(candidates))
        return GuidanceResult(
            kind="ZERO_GROSS_AVERAGE",
            candidate_comparable_ids=candidate_ids,
            recommended_comparable_id=None,
            proposed_indicated_unit_price_vnd_per_m2=average,
            reason_code="FROZEN_ZERO_GROSS_TIE_AVERAGE",
        )

    return GuidanceResult(
        kind="AMBIGUOUS_MIN_GROSS",
        candidate_comparable_ids=candidate_ids,
        recommended_comparable_id=None,
        proposed_indicated_unit_price_vnd_per_m2=None,
        reason_code="EQUAL_NONZERO_MIN_GROSS_REQUIRES_HUMAN_CHOICE",
    )
