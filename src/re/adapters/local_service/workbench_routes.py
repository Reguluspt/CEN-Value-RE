"""Thin local-service transport routes for the Epic 1 manual workbench."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from decimal import Decimal
from enum import Enum

from flask import Blueprint, jsonify, request

from ...application.services.comparable_quality import (
    ComparableQualityConflictError,
    ComparableQualityNotFoundError,
    ComparableQualityPersistenceError,
    ComparableQualityValidationError,
)
from ...application.services.final_valuation import (
    FinalValuationConflictError,
    FinalValuationNotFoundError,
    FinalValuationPersistenceError,
    FinalValuationValidationError,
)
from ...application.services.manual_workbench import (
    ManualWorkbenchConflictError,
    ManualWorkbenchExportError,
    ManualWorkbenchNotFoundError,
    ManualWorkbenchService,
    ManualWorkbenchValidationError,
)
from ...application.services.market_adjustment import (
    MarketAdjustmentConflictError,
    MarketAdjustmentNotFoundError,
    MarketAdjustmentPersistenceError,
    MarketAdjustmentValidationError,
)


def _payload(*, required: bool = True) -> dict[str, object]:
    value = request.get_json(silent=True)
    if value is None and not required:
        return {}
    if not isinstance(value, dict):
        raise ManualWorkbenchValidationError("A JSON object body is required")
    return value


def _json_value(value):
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: _json_value(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    raise TypeError(f"Unsupported local-service response value: {type(value).__name__}")


def _response(value, status: int = 200):
    return jsonify(_json_value(value)), status


def _error(code: str, message: str, status: int):
    return jsonify({"error": {"code": code, "message": message}}), status


def _application_error(exc: Exception):
    if isinstance(
        exc,
        (
            ManualWorkbenchValidationError,
            MarketAdjustmentValidationError,
            ComparableQualityValidationError,
            FinalValuationValidationError,
            TypeError,
            ValueError,
        ),
    ):
        return _error("RE_WORKBENCH_INVALID", str(exc), 400)
    if isinstance(
        exc,
        (
            ManualWorkbenchNotFoundError,
            MarketAdjustmentNotFoundError,
            ComparableQualityNotFoundError,
            FinalValuationNotFoundError,
        ),
    ):
        return _error("RE_WORKBENCH_NOT_FOUND", str(exc), 404)
    if isinstance(
        exc,
        (
            ManualWorkbenchConflictError,
            MarketAdjustmentConflictError,
            ComparableQualityConflictError,
            FinalValuationConflictError,
        ),
    ):
        return _error("RE_WORKBENCH_BLOCKED", str(exc), 409)
    if isinstance(exc, ManualWorkbenchExportError):
        return _error("RE_WORKBOOK_EXPORT_BLOCKED", str(exc), 409)
    if isinstance(
        exc,
        (
            MarketAdjustmentPersistenceError,
            ComparableQualityPersistenceError,
            FinalValuationPersistenceError,
        ),
    ):
        return _error(
            "RE_WORKBENCH_PERSISTENCE",
            "The workbench could not complete the canonical persistence operation.",
            500,
        )
    return _error("RE_WORKBENCH_ERROR", "The workbench request could not be completed.", 500)


def register_workbench_routes(
    blueprint: Blueprint,
    service: ManualWorkbenchService,
) -> None:
    @blueprint.get("/manual-cases/<case_id>/comparables/<int:comparable_order>/adjustment")
    def adjustment_state(case_id: str, comparable_order: int):
        try:
            return _response(
                service.adjustment_state(
                    case_id=case_id,
                    comparable_order=comparable_order,
                )
            )
        except Exception as exc:
            return _application_error(exc)

    @blueprint.put("/manual-cases/<case_id>/comparables/<int:comparable_order>/adjustment/base")
    def bind_adjustment_base(case_id: str, comparable_order: int):
        try:
            data = _payload()
            value = service.bind_adjustment_base(
                case_id=case_id,
                comparable_order=comparable_order,
                normalized_base_price_vnd_per_m2=data.get(
                    "normalized_base_price_vnd_per_m2"
                ),
                evidence_ref=data.get("evidence_ref"),
            )
            return _response(value)
        except Exception as exc:
            return _application_error(exc)

    @blueprint.put(
        "/manual-cases/<case_id>/comparables/<int:comparable_order>/adjustments/<factor_key>"
    )
    def select_adjustment_rate(
        case_id: str,
        comparable_order: int,
        factor_key: str,
    ):
        try:
            data = _payload()
            value = service.select_adjustment_rate(
                case_id=case_id,
                comparable_order=comparable_order,
                factor_key=factor_key,
                selected_rate=data.get("selected_rate"),
                selected_by=data.get("selected_by"),
                source_data_revision=data.get("source_data_revision"),
            )
            return _response(value)
        except Exception as exc:
            return _application_error(exc)

    @blueprint.post("/manual-cases/<case_id>/comparables/<int:comparable_order>/adjustment/run")
    def run_adjustment(case_id: str, comparable_order: int):
        try:
            data = _payload(required=False)
            value = service.run_adjustment(
                case_id=case_id,
                comparable_order=comparable_order,
                source_data_revision=data.get("source_data_revision"),
            )
            return _response(value, 201)
        except Exception as exc:
            return _application_error(exc)

    @blueprint.get("/manual-cases/<case_id>/quality")
    def quality_preview(case_id: str):
        try:
            return _response(service.quality_preview(case_id=case_id))
        except Exception as exc:
            return _application_error(exc)

    @blueprint.post("/manual-cases/<case_id>/indication")
    def confirm_indication(case_id: str):
        try:
            data = _payload()
            value = service.confirm_indication(
                case_id=case_id,
                selection_kind=data.get("selection_kind"),
                selected_comparable_order=data.get("selected_comparable_order"),
                confirmed_by=data.get("confirmed_by"),
                reason=data.get("reason"),
            )
            return _response(value, 201)
        except Exception as exc:
            return _application_error(exc)

    @blueprint.get("/manual-cases/<case_id>/indication")
    def current_indication(case_id: str):
        try:
            return _response(service.current_indication(case_id=case_id))
        except Exception as exc:
            return _application_error(exc)

    @blueprint.put("/manual-cases/<case_id>/construction-aggregate")
    def bind_construction_aggregate(case_id: str):
        try:
            data = _payload()
            value = service.bind_construction_aggregate(
                case_id=case_id,
                amount_vnd=data.get("amount_vnd"),
                evidence_ref=data.get("evidence_ref"),
                supplied_by=data.get("supplied_by"),
            )
            return _response(value)
        except Exception as exc:
            return _application_error(exc)

    @blueprint.post("/manual-cases/<case_id>/final-valuation")
    def compose_final_valuation(case_id: str):
        try:
            _payload(required=False)
            return _response(service.compose_final_valuation(case_id=case_id), 201)
        except Exception as exc:
            return _application_error(exc)

    @blueprint.get("/manual-cases/<case_id>/final-valuation")
    def current_final_valuation(case_id: str):
        try:
            return _response(service.current_final_valuation(case_id=case_id))
        except Exception as exc:
            return _application_error(exc)

    @blueprint.post("/manual-cases/<case_id>/workbook-output")
    def generate_workbook(case_id: str):
        try:
            data = _payload()
            value = service.generate_workbook(
                case_id=case_id,
                template_path=data.get("template_path"),
                output_path=data.get("output_path"),
            )
            return _response(value, 201)
        except Exception as exc:
            return _application_error(exc)
