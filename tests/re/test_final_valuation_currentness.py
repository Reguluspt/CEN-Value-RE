import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from src.re.adapters.excel.rounding_defaults import SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS
from src.re.adapters.persistence.migrations import apply_migrations
from src.re.adapters.persistence.store import SQLCipherUnitOfWork
from src.re.application.services.final_valuation import (
    FinalValuationConflictError,
    FinalValuationService,
)


_HELPER_PATH = Path(__file__).with_name("test_final_valuation_service.py")
_SPEC = importlib.util.spec_from_file_location("_e1pr004_service_helpers", _HELPER_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_HELPERS = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_HELPERS)


def _prepared_final_service(connection, ids):
    schema_version = apply_migrations(connection)
    _HELPERS._seed_case_subject_and_comparables(connection)
    uow = SQLCipherUnitOfWork(connection, schema_version)
    market = _HELPERS._build_upstream_evidence(uow)
    service = FinalValuationService(
        uow,
        template_rounding_defaults=SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS,
        now=lambda: "2026-08-17T15:20:00Z",
        new_id=ids.__next__,
    )
    service.bind_supplied_construction_aggregate(
        case_id="case-1",
        amount_vnd="1152970000",
        evidence_ref="source://construction/A",
        supplied_by="appraiser",
    )
    return uow, market, service


def _recompute_final_sha(snapshot):
    payload = {
        "case_id": snapshot.case_id,
        "subject_property_id": snapshot.subject_property_id,
        "appraisal_date": snapshot.appraisal_date,
        "human_indication_snapshot_id": snapshot.human_indication_snapshot_id,
        "human_indication_semantic_sha256": snapshot.human_indication_semantic_sha256,
        "rounded_indicated_unit_price_vnd_per_m2": snapshot.rounded_indicated_unit_price_vnd_per_m2,
        "land_components": json.loads(snapshot.land_components_json),
        "land_components_sha256": snapshot.land_components_sha256,
        "compliant_residential_land_value_vnd": snapshot.compliant_residential_land_value_vnd,
        "other_recognized_land_value_vnd": snapshot.other_recognized_land_value_vnd,
        "recognized_land_value_vnd": snapshot.recognized_land_value_vnd,
        "construction_aggregate_input_id": snapshot.construction_aggregate_input_id,
        "construction_aggregate_semantic_sha256": snapshot.construction_aggregate_semantic_sha256,
        "construction_value_total_vnd": snapshot.construction_value_total_vnd,
        "total_value_before_rounding_vnd": snapshot.total_value_before_rounding_vnd,
        "final_appraised_value_vnd": snapshot.final_appraised_value_vnd,
        "rounding": {
            "target": snapshot.rounding_target,
            "mode": snapshot.rounding_mode,
            "increment_vnd": snapshot.rounding_increment_vnd,
            "source": snapshot.rounding_source,
            "profile_id": snapshot.rounding_profile_id,
            "profile_version": snapshot.rounding_profile_version,
            "selected_by": snapshot.rounding_selected_by,
            "selected_at": snapshot.rounding_selected_at,
        },
        "composed_at": snapshot.composed_at,
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def test_final_snapshot_semantic_sha_is_reconstructable_from_immutable_snapshot():
    connection = _HELPERS._connection()
    try:
        uow, _, service = _prepared_final_service(
            connection, iter(("construction-1", "valuation-1"))
        )
        service.compose(
            case_id="case-1",
            total_value_rounding_policy=_HELPERS._total_policy(),
        )
        snapshot = uow.final_valuation_snapshots.get("valuation-1")
        assert snapshot is not None
        assert _recompute_final_sha(snapshot) == snapshot.semantic_sha256
    finally:
        connection.close()


def test_appraisal_date_drift_invalidates_current_final_snapshot():
    connection = _HELPERS._connection()
    try:
        _, _, service = _prepared_final_service(
            connection, iter(("construction-1", "valuation-1"))
        )
        service.compose(
            case_id="case-1",
            total_value_rounding_policy=_HELPERS._total_policy(),
        )
        connection.execute(
            "UPDATE appraisal_case SET appraisal_date='2026-08-06' WHERE id='case-1'"
        )
        connection.commit()
        with pytest.raises(FinalValuationConflictError, match="inputs changed"):
            service.resolve_current(case_id="case-1")
    finally:
        connection.close()


def test_template_profile_drift_invalidates_template_default_final_snapshot():
    connection = _HELPERS._connection()
    try:
        _, _, service = _prepared_final_service(
            connection, iter(("construction-1", "valuation-1"))
        )
        service.compose(
            case_id="case-1",
            total_value_rounding_policy=_HELPERS._total_policy(),
        )
        connection.execute(
            "UPDATE appraisal_case SET template_profile_version='2' WHERE id='case-1'"
        )
        connection.commit()
        with pytest.raises(FinalValuationConflictError, match="template profile changed"):
            service.resolve_current(case_id="case-1")
    finally:
        connection.close()


def test_upstream_human_indication_drift_invalidates_current_final_snapshot():
    connection = _HELPERS._connection()
    try:
        _, market, service = _prepared_final_service(
            connection, iter(("construction-1", "valuation-1"))
        )
        service.compose(
            case_id="case-1",
            total_value_rounding_policy=_HELPERS._total_policy(),
        )
        market.select_rate(
            case_id="case-1",
            comparable_property_id="comp-1",
            factor_key="C2",
            selected_rate="-0.04",
            selected_by="appraiser-2",
        )
        with pytest.raises(FinalValuationConflictError, match="decisions are no longer current"):
            service.resolve_current(case_id="case-1")
    finally:
        connection.close()
