"""Thin Flask routes for the Epic 1 manual-case application service."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from ...application.commands.manual_case import (
    CharacteristicInput,
    CreateManualCase,
    EvidenceInput,
    LandParcelInput,
    LandValuationComponentInput,
    SaveComparable,
    SaveSubject,
)
from ...application.services.manual_case import (
    ManualCaseConflictError,
    ManualCaseNotFoundError,
    ManualCasePersistenceError,
    ManualCaseService,
    ManualCaseValidationError,
    UnsupportedProfileError,
)


def _characteristic(payload: dict[str, object]) -> CharacteristicInput:
    return CharacteristicInput(**payload)


def _land_component(payload: dict[str, object]) -> LandValuationComponentInput:
    return LandValuationComponentInput(**payload)


def _parcel(payload: dict[str, object]) -> LandParcelInput:
    data = dict(payload)
    data["valuation_components"] = tuple(
        _land_component(dict(item))
        for item in data.get("valuation_components", ())
    )
    return LandParcelInput(**data)


def _evidence(payload: dict[str, object]) -> EvidenceInput:
    return EvidenceInput(**payload)


def _payload() -> dict[str, object]:
    value = request.get_json(silent=True)
    if not isinstance(value, dict):
        raise ManualCaseValidationError("A JSON object body is required")
    return value


def _validation_response(exc: Exception):
    code = "RE_PROFILE_UNSUPPORTED" if isinstance(exc, UnsupportedProfileError) else "RE_MANUAL_DATA_INVALID"
    return jsonify({"error": {"code": code, "message": str(exc)}}), 400



def _persistence_response(exc: Exception):
    return jsonify({"error": {"code": "RE_MANUAL_DATA_PERSISTENCE", "message": str(exc)}}), 500


def register_manual_case_routes(
    blueprint: Blueprint,
    service: ManualCaseService,
) -> None:
    @blueprint.post("/manual-cases")
    def create_manual_case():
        try:
            snapshot = service.create_case(CreateManualCase(**_payload()))
        except (TypeError, ValueError, ManualCaseValidationError) as exc:
            return _validation_response(exc)
        except ManualCaseConflictError as exc:
            return jsonify({"error": {"code": "RE_MANUAL_DATA_CONFLICT", "message": str(exc)}}), 409
        except ManualCasePersistenceError as exc:
            return _persistence_response(exc)
        return jsonify(snapshot.to_dict()), 201

    @blueprint.get("/manual-cases/<case_id>")
    def resume_manual_case(case_id: str):
        try:
            snapshot = service.resume_case(case_id)
        except ManualCaseNotFoundError as exc:
            return jsonify({"error": {"code": "RE_MANUAL_CASE_NOT_FOUND", "message": str(exc)}}), 404
        return jsonify(snapshot.to_dict())

    @blueprint.put("/manual-cases/<case_id>/subject")
    def save_manual_subject(case_id: str):
        try:
            data = _payload()
            data["case_id"] = case_id
            data["parcels"] = tuple(_parcel(dict(item)) for item in data.get("parcels", ()))
            data["characteristics"] = tuple(
                _characteristic(dict(item)) for item in data.get("characteristics", ())
            )
            snapshot = service.save_subject(SaveSubject(**data))
        except ManualCaseNotFoundError as exc:
            return jsonify({"error": {"code": "RE_MANUAL_CASE_NOT_FOUND", "message": str(exc)}}), 404
        except (TypeError, ValueError, ManualCaseValidationError) as exc:
            return _validation_response(exc)
        except ManualCaseConflictError as exc:
            return jsonify({"error": {"code": "RE_MANUAL_DATA_CONFLICT", "message": str(exc)}}), 409
        except ManualCasePersistenceError as exc:
            return _persistence_response(exc)
        return jsonify(snapshot.to_dict())

    @blueprint.put("/manual-cases/<case_id>/comparables/<int:comparable_order>")
    def save_manual_comparable(case_id: str, comparable_order: int):
        try:
            data = _payload()
            data["case_id"] = case_id
            data["comparable_order"] = comparable_order
            data["characteristics"] = tuple(
                _characteristic(dict(item)) for item in data.get("characteristics", ())
            )
            data["evidence"] = tuple(_evidence(dict(item)) for item in data.get("evidence", ()))
            snapshot = service.save_comparable(SaveComparable(**data))
        except ManualCaseNotFoundError as exc:
            return jsonify({"error": {"code": "RE_MANUAL_CASE_NOT_FOUND", "message": str(exc)}}), 404
        except (TypeError, ValueError, ManualCaseValidationError) as exc:
            return _validation_response(exc)
        except ManualCaseConflictError as exc:
            return jsonify({"error": {"code": "RE_MANUAL_DATA_CONFLICT", "message": str(exc)}}), 409
        except ManualCasePersistenceError as exc:
            return _persistence_response(exc)
        return jsonify(snapshot.to_dict())
