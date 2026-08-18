"""Application facade for the Epic 1 manual workbench.

The facade adapts UI-sized commands to already accepted application services. It
never owns appraisal formulas and never imports Flask, persistence adapters, or
Excel writer implementations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ...domain.common.rounding import (
    RoundingMode,
    RoundingPolicy,
    RoundingSource,
    RoundingTarget,
    TOTAL_VALUE_TARGET,
    UNIT_PRICE_TARGET,
)
from ...ports.adjustment_persistence import AdjustmentPersistenceUnitOfWork
from ...ports.excel import TemplateRoundingDefaultResolver
from .comparable_quality import ComparableQualityService
from .final_valuation import FinalValuationService
from .market_adjustment import MarketAdjustmentService
from .workbook_output import WorkbookOutputService


class ManualWorkbenchError(Exception):
    """Base application error for E1-PR-006 orchestration."""


class ManualWorkbenchValidationError(ManualWorkbenchError, ValueError):
    pass


class ManualWorkbenchNotFoundError(ManualWorkbenchError, LookupError):
    pass


class ManualWorkbenchConflictError(ManualWorkbenchError):
    pass


class ManualWorkbenchExportError(ManualWorkbenchError):
    pass


class WorkbenchComparable(Protocol):
    property_id: str
    comparable_order: int
    archived_at: str | None


@dataclass(frozen=True, slots=True)
class WorkbenchProfileBinding:
    profile_id: str
    profile_version: str


def _required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManualWorkbenchValidationError(f"{field_name} must be non-empty")
    return value.strip()


class ManualWorkbenchService:
    """Translate workbench actions to the accepted Epic 1 services."""

    def __init__(
        self,
        uow: AdjustmentPersistenceUnitOfWork,
        *,
        market_adjustment: MarketAdjustmentService,
        comparable_quality: ComparableQualityService,
        final_valuation: FinalValuationService,
        workbook_output: WorkbookOutputService,
        template_rounding_defaults: TemplateRoundingDefaultResolver,
    ) -> None:
        self._uow = uow
        self._market_adjustment = market_adjustment
        self._comparable_quality = comparable_quality
        self._final_valuation = final_valuation
        self._workbook_output = workbook_output
        self._template_rounding_defaults = template_rounding_defaults

    def _case_profile(self, case_id: str) -> WorkbenchProfileBinding:
        case_id = _required_text(case_id, "case_id")
        with self._uow.atomic():
            case = self._uow.cases.get(case_id)
            if case is None or case.archived_at is not None:
                raise ManualWorkbenchNotFoundError("Appraisal case was not found")
            if not case.template_profile_id or not case.template_profile_version:
                raise ManualWorkbenchConflictError(
                    "Manual workbench requires a supported case template profile"
                )
            return WorkbenchProfileBinding(
                profile_id=case.template_profile_id,
                profile_version=case.template_profile_version,
            )

    def _comparable_id(self, case_id: str, comparable_order: int) -> str:
        case_id = _required_text(case_id, "case_id")
        if isinstance(comparable_order, bool) or comparable_order not in (1, 2, 3):
            raise ManualWorkbenchValidationError(
                "comparable_order must be one of 1, 2 or 3"
            )
        with self._uow.atomic():
            case = self._uow.cases.get(case_id)
            if case is None or case.archived_at is not None:
                raise ManualWorkbenchNotFoundError("Appraisal case was not found")
            matches = [
                item
                for item in self._uow.comparables.list_for_case(case_id)
                if item.archived_at is None and item.comparable_order == comparable_order
            ]
            if len(matches) != 1:
                raise ManualWorkbenchNotFoundError(
                    f"Current TSSS{comparable_order:02d} was not found"
                )
            return matches[0].property_id

    def _template_policy(
        self,
        *,
        case_id: str,
        target: RoundingTarget,
    ) -> RoundingPolicy:
        profile = self._case_profile(case_id)
        trusted = self._template_rounding_defaults.resolve(
            profile_id=profile.profile_id,
            profile_version=profile.profile_version,
            target=target.key,
        )
        if trusted is None:
            raise ManualWorkbenchConflictError(
                f"Case profile does not declare a trusted {target.key} rounding default"
            )
        if (
            trusted.profile_id != profile.profile_id
            or trusted.profile_version != profile.profile_version
            or trusted.target != target.key
        ):
            raise ManualWorkbenchConflictError(
                "Trusted template rounding metadata does not match the current case profile"
            )
        try:
            mode = RoundingMode(trusted.mode)
        except ValueError as exc:
            raise ManualWorkbenchConflictError(
                "Trusted template rounding mode is unsupported"
            ) from exc
        return RoundingPolicy(
            target=target,
            increment_vnd=trusted.increment_vnd,
            source=RoundingSource.TEMPLATE_DEFAULT,
            mode=mode,
            profile_id=trusted.profile_id,
            profile_version=trusted.profile_version,
        )

    def adjustment_state(self, *, case_id: str, comparable_order: int):
        comparable_id = self._comparable_id(case_id, comparable_order)
        return self._market_adjustment.read_state(
            case_id=case_id,
            comparable_property_id=comparable_id,
        )

    def bind_adjustment_base(
        self,
        *,
        case_id: str,
        comparable_order: int,
        normalized_base_price_vnd_per_m2,
        evidence_ref: str,
    ):
        comparable_id = self._comparable_id(case_id, comparable_order)
        return self._market_adjustment.bind_normalized_base(
            case_id=case_id,
            comparable_property_id=comparable_id,
            normalized_base_price_vnd_per_m2=normalized_base_price_vnd_per_m2,
            evidence_ref=evidence_ref,
        )

    def select_adjustment_rate(
        self,
        *,
        case_id: str,
        comparable_order: int,
        factor_key: str,
        selected_rate,
        selected_by: str,
        source_data_revision: str | None = None,
    ):
        comparable_id = self._comparable_id(case_id, comparable_order)
        return self._market_adjustment.select_rate(
            case_id=case_id,
            comparable_property_id=comparable_id,
            factor_key=factor_key,
            selected_rate=selected_rate,
            selected_by=selected_by,
            source_data_revision=source_data_revision,
        )

    def run_adjustment(
        self,
        *,
        case_id: str,
        comparable_order: int,
        source_data_revision: str | None = None,
    ):
        comparable_id = self._comparable_id(case_id, comparable_order)
        return self._market_adjustment.run_adjustment(
            case_id=case_id,
            comparable_property_id=comparable_id,
            source_data_revision=source_data_revision,
        )

    def quality_preview(self, *, case_id: str):
        return self._comparable_quality.preview(case_id=case_id)

    def confirm_indication(
        self,
        *,
        case_id: str,
        selection_kind: str,
        selected_comparable_order: int | None,
        confirmed_by: str,
        reason: str,
    ):
        selected_id = None
        if selection_kind == "COMPARABLE":
            if selected_comparable_order is None:
                raise ManualWorkbenchValidationError(
                    "COMPARABLE selection requires selected_comparable_order"
                )
            selected_id = self._comparable_id(case_id, selected_comparable_order)
        elif selection_kind == "ZERO_GROSS_AVERAGE":
            if selected_comparable_order is not None:
                raise ManualWorkbenchValidationError(
                    "ZERO_GROSS_AVERAGE must not select a comparable order"
                )
        else:
            raise ManualWorkbenchValidationError(
                "selection_kind must be COMPARABLE or ZERO_GROSS_AVERAGE"
            )
        return self._comparable_quality.confirm_indication(
            case_id=case_id,
            selection_kind=selection_kind,
            selected_comparable_property_id=selected_id,
            confirmed_by=confirmed_by,
            reason=reason,
            rounding_policy=self._template_policy(
                case_id=case_id,
                target=UNIT_PRICE_TARGET,
            ),
        )

    def current_indication(self, *, case_id: str):
        return self._comparable_quality.resolve_current_indication(case_id=case_id)

    def bind_construction_aggregate(
        self,
        *,
        case_id: str,
        amount_vnd,
        evidence_ref: str,
        supplied_by: str,
    ):
        return self._final_valuation.bind_supplied_construction_aggregate(
            case_id=case_id,
            amount_vnd=amount_vnd,
            evidence_ref=evidence_ref,
            supplied_by=supplied_by,
        )

    def compose_final_valuation(self, *, case_id: str):
        return self._final_valuation.compose(
            case_id=case_id,
            total_value_rounding_policy=self._template_policy(
                case_id=case_id,
                target=TOTAL_VALUE_TARGET,
            ),
        )

    def current_final_valuation(self, *, case_id: str):
        return self._final_valuation.resolve_current(case_id=case_id)

    def generate_workbook(
        self,
        *,
        case_id: str,
        template_path: str,
        output_path: str,
    ):
        try:
            return self._workbook_output.generate(
                case_id=case_id,
                template_path=_required_text(template_path, "template_path"),
                output_path=_required_text(output_path, "output_path"),
            )
        except ManualWorkbenchError:
            raise
        except Exception as exc:
            raise ManualWorkbenchExportError(
                "Workbook export could not be completed"
            ) from exc
