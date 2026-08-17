import hashlib
import json
import sqlite3

import pytest

from src.re.adapters.persistence.migrations import LATEST_SCHEMA_VERSION, apply_migrations
from src.re.adapters.persistence.store import SQLCipherUnitOfWork
from src.re.adapters.persistence.strict_adjustment_decision_repository import (
    StrictSQLCipherAdjustmentDecisionRepository,
)
from src.re.application.commands import (
    CharacteristicInput,
    CreateManualCase,
    SaveComparable,
)
from src.re.application.services.manual_case import ManualCaseService
from src.re.application.services.market_adjustment import (
    MarketAdjustmentConflictError,
    MarketAdjustmentService,
)
from src.re.ports.persistence import AdjustmentDecisionRecord


def _dict_factory(cursor, row):
    return {column[0]: row[index] for index, column in enumerate(cursor.description)}


def _connection():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = _dict_factory
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def _seed_case_comparable_decision(connection):
    connection.execute(
        """INSERT INTO appraisal_case(id,case_code,status,created_at,updated_at)
        VALUES ('case-1','C-1','IN_PROGRESS','t','t')"""
    )
    connection.execute(
        """INSERT INTO appraisal_case(id,case_code,status,created_at,updated_at)
        VALUES ('case-2','C-2','IN_PROGRESS','t','t')"""
    )
    for comp_id, case_id, order_no in (("comp-1", "case-1", 1), ("comp-2", "case-2", 1)):
        connection.execute(
            """INSERT INTO property(id,case_id,role,legal_address,current_address,created_at,updated_at)
            VALUES (?,?,?,?,?,?,?)""",
            (comp_id, case_id, "COMPARABLE", "A", "A", "t", "t"),
        )
        connection.execute(
            """INSERT INTO comparable_property(property_id,comparable_order,completeness_status,case_id)
            VALUES (?,?,?,?)""",
            (comp_id, order_no, "COMPLETE", case_id),
        )
    revision = connection.execute(
        "SELECT source_revision FROM adjustment_source_state WHERE comparable_property_id='comp-1'"
    ).fetchone()["source_revision"]
    connection.execute(
        """INSERT INTO adjustment_decision(
            id,case_id,comparable_property_id,factor_key,selected_explicitly,
            source_data_revision,review_status,selected_rate_pct,selected_at
        ) VALUES ('decision-1','case-1','comp-1','C1',1,?,'CURRENT','0','t')""",
        (str(revision),),
    )
    connection.commit()


def _select_all(service):
    for index in range(1, 12):
        service.select_rate(
            case_id="case-1",
            comparable_property_id="comp-1",
            factor_key=f"C{index}",
            selected_rate="0",
            selected_by="appraiser",
        )


def _semantic_sha_from_snapshot(snapshot):
    payload = {
        "case_id": snapshot.case_id,
        "comparable_property_id": snapshot.comparable_property_id,
        "source_data_revision": snapshot.source_data_revision,
        "normalized_base_price_vnd_per_m2": snapshot.normalized_base_price_vnd_per_m2,
        "normalized_base_evidence_ref": snapshot.normalized_base_evidence_ref,
        "property_adjustment_base_vnd_per_m2": snapshot.property_adjustment_base_vnd_per_m2,
        "indicated_unit_price_vnd_per_m2": snapshot.indicated_unit_price_vnd_per_m2,
        "decision_set_sha256": snapshot.decision_set_sha256,
        "steps": json.loads(snapshot.ordered_steps_json),
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def test_schema_v3_creates_authoritative_source_state_and_identity_guards():
    connection = _connection()
    try:
        assert apply_migrations(connection) == 3
        assert LATEST_SCHEMA_VERSION == 3
        names = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert "adjustment_selection_audit" in names
        assert "adjustment_calculation_snapshot" in names
        assert "adjustment_source_state" in names
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(adjustment_calculation_snapshot)"
            )
        }
        assert "normalized_base_evidence_ref" in columns
        triggers = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger'"
            )
        }
        assert "adjustment_decision_identity_update_guard" in triggers
        assert "adjustment_source_market_update" in triggers
        assert "adjustment_source_characteristic_update" in triggers
    finally:
        connection.close()


def test_adjustment_decision_cannot_cross_case_lineage():
    connection = _connection()
    try:
        apply_migrations(connection)
        _seed_case_comparable_decision(connection)
        with pytest.raises(sqlite3.IntegrityError, match="case lineage mismatch"):
            connection.execute(
                """INSERT INTO adjustment_decision(
                    id,case_id,comparable_property_id,factor_key,selected_explicitly,
                    source_data_revision,review_status
                ) VALUES ('bad','case-2','comp-1','C2',1,'1','CURRENT')"""
            )
    finally:
        connection.close()


def test_existing_decision_identity_cannot_be_reparented_or_refactored():
    connection = _connection()
    try:
        apply_migrations(connection)
        _seed_case_comparable_decision(connection)
        connection.execute(
            """INSERT INTO adjustment_selection_audit(
                id,adjustment_decision_id,case_id,comparable_property_id,factor_key,
                event_kind,selected_rate_pct,selected_explicitly,selected_by,selected_at,
                source_data_revision,review_status
            ) VALUES ('audit-1','decision-1','case-1','comp-1','C1',
                'SELECTED','0',1,'appraiser','t','1','CURRENT')"""
        )
        with pytest.raises(sqlite3.IntegrityError, match="identity is immutable"):
            connection.execute(
                """UPDATE adjustment_decision
                SET case_id='case-2',comparable_property_id='comp-2',factor_key='C2'
                WHERE id='decision-1'"""
            )
        with pytest.raises(sqlite3.IntegrityError, match="identity is immutable"):
            connection.execute(
                "UPDATE adjustment_decision SET factor_key='C2' WHERE id='decision-1'"
            )
        current = connection.execute(
            "SELECT case_id,comparable_property_id,factor_key FROM adjustment_decision WHERE id='decision-1'"
        ).fetchone()
        audit = connection.execute(
            "SELECT case_id,comparable_property_id,factor_key FROM adjustment_selection_audit WHERE id='audit-1'"
        ).fetchone()
        assert current == audit == {
            "case_id": "case-1",
            "comparable_property_id": "comp-1",
            "factor_key": "C1",
        }
    finally:
        connection.close()


def test_strict_repository_upsert_never_updates_identity_fields():
    connection = _connection()
    try:
        apply_migrations(connection)
        _seed_case_comparable_decision(connection)
        repo = StrictSQLCipherAdjustmentDecisionRepository(connection)
        original = repo.get("decision-1")
        assert original is not None
        attempted = AdjustmentDecisionRecord(
            id=original.id,
            case_id="case-2",
            comparable_property_id="comp-2",
            factor_key="C2",
            selected_explicitly=True,
            source_data_revision=original.source_data_revision,
            review_status="CURRENT",
            selected_rate_pct="-0.20",
            selected_at="t2",
            version=original.version + 1,
        )
        repo.put(attempted)
        persisted = repo.get("decision-1")
        assert persisted is not None
        assert persisted.case_id == "case-1"
        assert persisted.comparable_property_id == "comp-1"
        assert persisted.factor_key == "C1"
        assert persisted.selected_rate_pct == "-0.20"
    finally:
        connection.close()


def test_market_observation_update_atomically_bumps_revision_clears_p0_stales_and_audits():
    connection = _connection()
    try:
        apply_migrations(connection)
        _seed_case_comparable_decision(connection)
        connection.execute(
            """INSERT INTO adjustment_selection_audit(
                id,adjustment_decision_id,case_id,comparable_property_id,factor_key,
                event_kind,selected_rate_pct,selected_explicitly,selected_by,selected_at,
                source_data_revision,review_status
            ) VALUES ('selected-1','decision-1','case-1','comp-1','C1',
                'SELECTED','0',1,'appraiser','t','1','CURRENT')"""
        )
        connection.execute(
            """UPDATE adjustment_source_state
            SET normalized_base_price_vnd_per_m2='230951000',
                normalized_base_bound_revision=source_revision,
                normalized_base_evidence_ref='fixture://P0'
            WHERE comparable_property_id='comp-1'"""
        )
        before = connection.execute(
            "SELECT source_revision FROM adjustment_source_state WHERE comparable_property_id='comp-1'"
        ).fetchone()["source_revision"]
        connection.execute(
            """INSERT INTO market_observation(
                id,comparable_property_id,asking_or_sale_price_vnd,negotiated_price_vnd,created_at,updated_at
            ) VALUES ('obs-1','comp-1','100','85','t','t')"""
        )
        after = connection.execute(
            "SELECT * FROM adjustment_source_state WHERE comparable_property_id='comp-1'"
        ).fetchone()
        decision = connection.execute(
            "SELECT selected_rate_pct,review_status FROM adjustment_decision WHERE id='decision-1'"
        ).fetchone()
        audit = connection.execute(
            """SELECT event_kind,selected_by,source_data_revision,review_status
            FROM adjustment_selection_audit
            WHERE adjustment_decision_id='decision-1'
            ORDER BY rowid DESC LIMIT 1"""
        ).fetchone()
        assert after["source_revision"] == before + 1
        assert after["normalized_base_price_vnd_per_m2"] is None
        assert after["normalized_base_bound_revision"] is None
        assert decision["selected_rate_pct"] == "0"
        assert decision["review_status"] == "SOURCE_DATA_CHANGED"
        assert audit == {
            "event_kind": "SOURCE_DATA_CHANGED",
            "selected_by": "SYSTEM_SOURCE_DRIFT",
            "source_data_revision": str(after["source_revision"]),
            "review_status": "SOURCE_DATA_CHANGED",
        }
    finally:
        connection.close()


def test_material_p0_rebind_advances_revision_stales_rates_and_requires_reselection():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_case_comparable_decision(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        service = MarketAdjustmentService(uow, now=lambda: "2026-08-17T02:00:00Z")
        first = service.bind_normalized_base(
            case_id="case-1",
            comparable_property_id="comp-1",
            normalized_base_price_vnd_per_m2="1000",
            evidence_ref="source://P0-A",
        )
        _select_all(service)
        first_run = service.run_adjustment(
            case_id="case-1", comparable_property_id="comp-1"
        )
        assert first_run.result.indicated_unit_price_vnd_per_m2 == 1000

        rebound = service.bind_normalized_base(
            case_id="case-1",
            comparable_property_id="comp-1",
            normalized_base_price_vnd_per_m2="9000",
            evidence_ref="source://P0-B",
        )
        assert rebound.source_revision == first.source_revision + 1
        decisions = uow.adjustment_decision_queries.list_for_comparable(
            "case-1", "comp-1"
        )
        assert len(decisions) == 11
        assert all(item.review_status == "SOURCE_DATA_CHANGED" for item in decisions)
        assert all(item.selected_rate_pct == "0" for item in decisions)
        drift_audits = connection.execute(
            """SELECT COUNT(*) AS count FROM adjustment_selection_audit
            WHERE comparable_property_id='comp-1'
              AND event_kind='SOURCE_DATA_CHANGED'
              AND source_data_revision=?""",
            (str(rebound.source_revision),),
        ).fetchone()["count"]
        assert drift_audits == 11
        with pytest.raises(MarketAdjustmentConflictError, match="human review"):
            service.run_adjustment(case_id="case-1", comparable_property_id="comp-1")

        _select_all(service)
        second_run = service.run_adjustment(
            case_id="case-1", comparable_property_id="comp-1"
        )
        assert second_run.result.indicated_unit_price_vnd_per_m2 == 9000
    finally:
        connection.close()


def test_manual_case_source_change_rejects_old_revision_even_when_caller_replays_it():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        manual = ManualCaseService(
            uow,
            supported_profiles={("cenvalue-re-n08-0038-v1", "1")},
            now=lambda: "2026-08-17T01:00:00Z",
        )
        created = manual.create_case(
            CreateManualCase(
                case_code="CV-DRIFT",
                appraisal_date="2026-08-17",
                profile_id="cenvalue-re-n08-0038-v1",
                profile_version="1",
            )
        )
        case_id = created.case.id
        saved = manual.save_comparable(
            SaveComparable(
                case_id=case_id,
                comparable_order=1,
                legal_address="A",
                current_address="A",
                completeness_status="COMPLETE",
                asking_or_sale_price_vnd="1000000000",
                negotiated_price_vnd="850000000",
                characteristics=(
                    CharacteristicInput(definition_key="frontage", decimal_value="4.0"),
                ),
            )
        )
        comp_id = saved.comparables[0].property.property_id
        adjustment = MarketAdjustmentService(
            uow, now=lambda: "2026-08-17T01:00:01Z"
        )
        state = adjustment.bind_normalized_base(
            case_id=case_id,
            comparable_property_id=comp_id,
            normalized_base_price_vnd_per_m2="230951000",
            evidence_ref="fixture://N08/P0",
        )
        old_revision = str(state.source_revision)
        for index in range(1, 12):
            adjustment.select_rate(
                case_id=case_id,
                comparable_property_id=comp_id,
                factor_key=f"C{index}",
                selected_rate="0",
                selected_by="appraiser",
            )

        manual.save_comparable(
            SaveComparable(
                case_id=case_id,
                comparable_order=1,
                property_id=comp_id,
                legal_address="A",
                current_address="A",
                completeness_status="COMPLETE",
                asking_or_sale_price_vnd="1200000000",
                negotiated_price_vnd="1000000000",
                characteristics=(
                    CharacteristicInput(definition_key="frontage", decimal_value="4.5"),
                ),
            )
        )
        current_state = uow.adjustment_source_states.get(case_id, comp_id)
        assert current_state is not None
        assert str(current_state.source_revision) != old_revision
        decisions = uow.adjustment_decision_queries.list_for_comparable(case_id, comp_id)
        assert all(item.review_status == "SOURCE_DATA_CHANGED" for item in decisions)
        assert all(item.selected_rate_pct == "0" for item in decisions)
        audits = connection.execute(
            """SELECT event_kind,selected_by,source_data_revision FROM adjustment_selection_audit
            WHERE comparable_property_id=? AND event_kind='SOURCE_DATA_CHANGED'""",
            (comp_id,),
        ).fetchall()
        assert audits
        assert all(item["selected_by"] == "SYSTEM_SOURCE_DRIFT" for item in audits)
        assert all(
            item["source_data_revision"] == str(current_state.source_revision)
            for item in audits[-11:]
        )

        with pytest.raises(MarketAdjustmentConflictError):
            adjustment.run_adjustment(
                case_id=case_id,
                comparable_property_id=comp_id,
                source_data_revision=old_revision,
                normalized_base_price_vnd_per_m2="230951000",
            )
    finally:
        connection.close()


def test_selection_audit_must_bind_exact_decision_case_comparable_and_factor():
    connection = _connection()
    try:
        apply_migrations(connection)
        _seed_case_comparable_decision(connection)
        with pytest.raises(sqlite3.IntegrityError, match="audit lineage mismatch"):
            connection.execute(
                """INSERT INTO adjustment_selection_audit(
                    id,adjustment_decision_id,case_id,comparable_property_id,factor_key,
                    event_kind,selected_rate_pct,selected_explicitly,selected_by,selected_at,
                    source_data_revision,review_status
                ) VALUES ('audit-bad','decision-1','case-1','comp-1','C2',
                    'SELECTED','0',1,'appraiser','t','1','CURRENT')"""
            )
    finally:
        connection.close()


def test_snapshot_semantic_sha_is_reconstructable_after_source_drift():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_case_comparable_decision(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        service = MarketAdjustmentService(uow, now=lambda: "2026-08-17T03:00:00Z")
        service.bind_normalized_base(
            case_id="case-1",
            comparable_property_id="comp-1",
            normalized_base_price_vnd_per_m2="1000",
            evidence_ref="source://immutable-P0-A",
        )
        _select_all(service)
        run = service.run_adjustment(case_id="case-1", comparable_property_id="comp-1")
        snapshot = uow.adjustment_calculation_snapshots.get(run.snapshot_id)
        assert snapshot is not None
        assert snapshot.normalized_base_evidence_ref == "source://immutable-P0-A"
        assert _semantic_sha_from_snapshot(snapshot) == snapshot.semantic_sha256

        service.bind_normalized_base(
            case_id="case-1",
            comparable_property_id="comp-1",
            normalized_base_price_vnd_per_m2="9000",
            evidence_ref="source://immutable-P0-B",
        )
        old_snapshot = uow.adjustment_calculation_snapshots.get(run.snapshot_id)
        assert old_snapshot is not None
        assert old_snapshot.normalized_base_evidence_ref == "source://immutable-P0-A"
        assert _semantic_sha_from_snapshot(old_snapshot) == old_snapshot.semantic_sha256
    finally:
        connection.close()


def test_calculation_snapshot_cannot_cross_case_lineage():
    connection = _connection()
    try:
        apply_migrations(connection)
        _seed_case_comparable_decision(connection)
        with pytest.raises(sqlite3.IntegrityError, match="snapshot case lineage mismatch"):
            connection.execute(
                """INSERT INTO adjustment_calculation_snapshot(
                    id,case_id,comparable_property_id,source_data_revision,
                    normalized_base_price_vnd_per_m2,normalized_base_evidence_ref,
                    property_adjustment_base_vnd_per_m2,indicated_unit_price_vnd_per_m2,
                    decision_set_sha256,ordered_steps_json,semantic_sha256,created_at
                ) VALUES ('snapshot-bad','case-2','comp-1','1','1','evidence://x','1','1',
                    'd','[]','s','t')"""
            )
    finally:
        connection.close()
