import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.re.adapters.excel.rounding_defaults import SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS
from src.re.adapters.persistence.migrations import LATEST_SCHEMA_VERSION, apply_migrations
from src.re.adapters.persistence.store import SQLCipherUnitOfWork
from src.re.application.services.comparable_quality import ComparableQualityService
from src.re.application.services.final_valuation import (
    FinalValuationConflictError,
    FinalValuationService,
)
from src.re.application.services.market_adjustment import MarketAdjustmentService
from src.re.domain.common.rounding import RoundingPolicy, RoundingSource, TOTAL_VALUE_TARGET


_FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "GOLDEN_CASE_ADJUSTMENT_DECISIONS_v1.json"
)


def _dict_factory(cursor, row):
    return {column[0]: row[index] for index, column in enumerate(cursor.description)}


def _connection():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = _dict_factory
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def _seed_case_subject_and_comparables(connection):
    connection.execute(
        """INSERT INTO appraisal_case(
            id,case_code,status,created_at,updated_at,appraisal_date,
            template_profile_id,template_profile_version
        ) VALUES ('case-1','CV-E1-004','IN_PROGRESS','t','t','2026-08-05',
            'cenvalue-re-n08-0038-v1','1')"""
    )
    connection.execute(
        """INSERT INTO property(
            id,case_id,role,legal_address,current_address,created_at,updated_at
        ) VALUES ('subject-1','case-1','SUBJECT','N08 subject','N08 subject','t','t')"""
    )
    connection.execute(
        "INSERT INTO subject_property(property_id,legal_review_status) VALUES ('subject-1','REVIEWED')"
    )
    connection.execute(
        """INSERT INTO land_valuation_component(
            id,property_id,component_order,planning_status,area_m2,valuation_basis,
            unit_price_vnd_per_m2,include_in_final_value,note,policy_version,
            created_at,updated_at
        ) VALUES ('land-1','subject-1',1,'COMPLIANT','82.93','MARKET_INDICATED',
            NULL,1,'Current human indicated unit price','E1-PR-003','t','t')"""
    )
    connection.execute(
        """INSERT INTO land_valuation_component(
            id,property_id,component_order,planning_status,area_m2,valuation_basis,
            unit_price_vnd_per_m2,include_in_final_value,note,policy_version,
            created_at,updated_at
        ) VALUES ('land-2','subject-1',2,'NON_COMPLIANT','20.27','OFFICIAL_LAND_PRICE',
            '106000000',1,'N08 frozen control cell Nhap lieu!I31',
            'cenvalue-re-n08-0038-v1@1:Nhap lieu!I31','t','t')"""
    )
    for index in range(1, 4):
        comp_id = f"comp-{index}"
        connection.execute(
            """INSERT INTO property(
                id,case_id,role,legal_address,current_address,created_at,updated_at
            ) VALUES (?,?,?,?,?,?,?)""",
            (comp_id, "case-1", "COMPARABLE", comp_id, comp_id, "t", "t"),
        )
        connection.execute(
            """INSERT INTO comparable_property(
                property_id,case_id,comparable_order,completeness_status
            ) VALUES (?,?,?,?)""",
            (comp_id, "case-1", index, "COMPLETE"),
        )
    connection.commit()


def _build_upstream_evidence(uow):
    fixture = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    p0_values = ("230951000", "239035000", "196483000")
    ids = iter((f"id-{index}" for index in range(1, 2000)))
    market = MarketAdjustmentService(
        uow,
        now=lambda: "2026-08-17T15:00:00Z",
        new_id=ids.__next__,
    )
    for index, comparable in enumerate(fixture["comparables"], 1):
        comp_id = f"comp-{index}"
        market.bind_normalized_base(
            case_id="case-1",
            comparable_property_id=comp_id,
            normalized_base_price_vnd_per_m2=p0_values[index - 1],
            evidence_ref=f"fixture://N08/{comparable['workbook_column']}/P0",
        )
        for decision in comparable["decisions"]:
            market.select_rate(
                case_id="case-1",
                comparable_property_id=comp_id,
                factor_key=decision["factor_key"],
                selected_rate=decision["selected_rate_fraction"],
                selected_by="appraiser-1",
            )
        market.run_adjustment(case_id="case-1", comparable_property_id=comp_id)

    indication = ComparableQualityService(
        uow,
        template_rounding_defaults=SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS,
        now=lambda: "2026-08-17T15:10:00Z",
        new_id=lambda: "human-1",
    )
    indication.confirm_indication(
        case_id="case-1",
        selection_kind="COMPARABLE",
        selected_comparable_property_id="comp-1",
        confirmed_by="appraiser-1",
        reason="Minimum gross adjustment reviewed and confirmed",
        rounding_policy=RoundingPolicy(
            target=__import__(
                "src.re.domain.common.rounding",
                fromlist=["UNIT_PRICE_TARGET"],
            ).UNIT_PRICE_TARGET,
            increment_vnd=1000,
            source=RoundingSource.TEMPLATE_DEFAULT,
            profile_id="cenvalue-re-n08-0038-v1",
            profile_version="1",
        ),
    )
    return market


def _total_policy(increment=1_000_000, source=RoundingSource.TEMPLATE_DEFAULT, **kwargs):
    return RoundingPolicy(
        target=TOTAL_VALUE_TARGET,
        increment_vnd=increment,
        source=source,
        profile_id="cenvalue-re-n08-0038-v1" if source is not RoundingSource.APPLICATION_DEFAULT else None,
        profile_version="1" if source is not RoundingSource.APPLICATION_DEFAULT else None,
        **kwargs,
    )


def test_schema_v5_creates_append_only_final_valuation_evidence():
    connection = _connection()
    try:
        assert apply_migrations(connection) == 5
        assert LATEST_SCHEMA_VERSION == 5
        names = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert {
            "construction_aggregate_input",
            "final_valuation_snapshot",
            "final_valuation_land_source",
        }.issubset(names)
        triggers = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger'"
            )
        }
        assert {
            "construction_aggregate_input_update_guard",
            "final_valuation_snapshot_update_guard",
            "final_valuation_land_source_lineage_guard",
        }.issubset(triggers)
    finally:
        connection.close()


def test_golden_final_composition_reproduces_g171_g169_g178_g181_g182():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_case_subject_and_comparables(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        _build_upstream_evidence(uow)
        ids = iter(("construction-1", "valuation-1"))
        service = FinalValuationService(
            uow,
            template_rounding_defaults=SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS,
            now=lambda: "2026-08-17T15:20:00Z",
            new_id=ids.__next__,
        )
        construction = service.bind_supplied_construction_aggregate(
            case_id="case-1",
            amount_vnd="1152970000",
            evidence_ref="workbook://N08/Bangtinh!G178:supplied-precomputed",
            supplied_by="appraiser-1",
        )
        assert construction.revision == 1
        result = service.compose(
            case_id="case-1",
            total_value_rounding_policy=_total_policy(),
        )
        assert result.compliant_residential_land_value_vnd == 16279822440
        assert result.other_recognized_land_value_vnd == 2148620000
        assert result.recognized_land_value_vnd == 18428442440
        assert result.construction_value_total_vnd == 1152970000
        assert result.total_value_before_rounding_vnd == 19581412440
        assert result.final_appraised_value_vnd == 19581000000

        persisted = uow.final_valuation_snapshots.get("valuation-1")
        assert persisted is not None
        assert persisted.total_value_before_rounding_vnd == "19581412440"
        assert persisted.final_appraised_value_vnd == "19581000000"
        assert persisted.total_value_before_rounding_vnd != persisted.final_appraised_value_vnd
        assert persisted.rounding_target == "TOTAL_VALUE"
        assert persisted.rounding_increment_vnd == 1_000_000
        assert persisted.human_indication_snapshot_id == "human-1"
        assert len(uow.final_valuation_land_sources.list_for_snapshot("valuation-1")) == 2
        assert service.resolve_current(case_id="case-1") == persisted
    finally:
        connection.close()


def test_material_construction_rebind_makes_old_final_snapshot_stale():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_case_subject_and_comparables(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        _build_upstream_evidence(uow)
        ids = iter(("construction-1", "valuation-1", "construction-2"))
        service = FinalValuationService(
            uow,
            template_rounding_defaults=SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS,
            now=lambda: "2026-08-17T15:20:00Z",
            new_id=ids.__next__,
        )
        first = service.bind_supplied_construction_aggregate(
            case_id="case-1",
            amount_vnd="1152970000",
            evidence_ref="source://construction/A",
            supplied_by="appraiser",
        )
        duplicate = service.bind_supplied_construction_aggregate(
            case_id="case-1",
            amount_vnd="1152970000",
            evidence_ref="source://construction/A",
            supplied_by="another-user",
        )
        assert duplicate == first
        service.compose(case_id="case-1", total_value_rounding_policy=_total_policy())
        changed = service.bind_supplied_construction_aggregate(
            case_id="case-1",
            amount_vnd="1200000000",
            evidence_ref="source://construction/B",
            supplied_by="appraiser",
        )
        assert changed.revision == 2
        with pytest.raises(FinalValuationConflictError, match="inputs changed"):
            service.resolve_current(case_id="case-1")
    finally:
        connection.close()


def test_land_component_change_makes_old_final_snapshot_stale():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_case_subject_and_comparables(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        _build_upstream_evidence(uow)
        ids = iter(("construction-1", "valuation-1"))
        service = FinalValuationService(
            uow,
            template_rounding_defaults=SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS,
            new_id=ids.__next__,
        )
        service.bind_supplied_construction_aggregate(
            case_id="case-1",
            amount_vnd="1152970000",
            evidence_ref="source://construction/A",
            supplied_by="appraiser",
        )
        service.compose(case_id="case-1", total_value_rounding_policy=_total_policy())
        connection.execute(
            "UPDATE land_valuation_component SET unit_price_vnd_per_m2='107000000' WHERE id='land-2'"
        )
        connection.commit()
        with pytest.raises(FinalValuationConflictError, match="Land composition inputs changed"):
            service.resolve_current(case_id="case-1")
    finally:
        connection.close()


def test_total_value_template_default_is_profile_authoritative_and_override_is_audited():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_case_subject_and_comparables(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        _build_upstream_evidence(uow)
        ids = iter(("construction-1", "valuation-override"))
        service = FinalValuationService(
            uow,
            template_rounding_defaults=SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS,
            new_id=ids.__next__,
        )
        service.bind_supplied_construction_aggregate(
            case_id="case-1",
            amount_vnd="1152970000",
            evidence_ref="source://construction/A",
            supplied_by="appraiser",
        )
        with pytest.raises(FinalValuationConflictError, match="trusted profile"):
            service.compose(
                case_id="case-1",
                total_value_rounding_policy=_total_policy(increment=10_000_000),
            )

        override = _total_policy(
            increment=10_000_000,
            source=RoundingSource.CASE_OVERRIDE,
            selected_by="rounding-appraiser",
            selected_at=datetime(2026, 8, 17, 15, 30, tzinfo=timezone.utc),
        )
        result = service.compose(
            case_id="case-1",
            total_value_rounding_policy=override,
        )
        assert result.total_value_before_rounding_vnd == 19581412440
        assert result.final_appraised_value_vnd == 19580000000
        persisted = uow.final_valuation_snapshots.get("valuation-override")
        assert persisted is not None
        assert persisted.rounding_source == "CASE_OVERRIDE"
        assert persisted.rounding_selected_by == "rounding-appraiser"
        assert persisted.rounding_selected_at is not None
    finally:
        connection.close()


def test_final_snapshot_and_sources_are_append_only():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_case_subject_and_comparables(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        _build_upstream_evidence(uow)
        ids = iter(("construction-1", "valuation-1"))
        service = FinalValuationService(
            uow,
            template_rounding_defaults=SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS,
            new_id=ids.__next__,
        )
        service.bind_supplied_construction_aggregate(
            case_id="case-1",
            amount_vnd="1152970000",
            evidence_ref="source://construction/A",
            supplied_by="appraiser",
        )
        service.compose(case_id="case-1", total_value_rounding_policy=_total_policy())
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "UPDATE final_valuation_snapshot SET final_appraised_value_vnd='1' WHERE id='valuation-1'"
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "DELETE FROM construction_aggregate_input WHERE id='construction-1'"
            )
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "UPDATE final_valuation_land_source SET component_semantic_sha256='bad' WHERE valuation_snapshot_id='valuation-1'"
            )
    finally:
        connection.close()
