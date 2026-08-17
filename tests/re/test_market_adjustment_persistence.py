import sqlite3

import pytest

from src.re.adapters.persistence.migrations import LATEST_SCHEMA_VERSION, apply_migrations


def _connection():
    connection = sqlite3.connect(":memory:")
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
    connection.execute(
        """INSERT INTO property(id,case_id,role,legal_address,current_address,created_at,updated_at)
        VALUES ('comp-1','case-1','COMPARABLE','A','A','t','t')"""
    )
    connection.execute(
        """INSERT INTO comparable_property(property_id,comparable_order,completeness_status,case_id)
        VALUES ('comp-1',1,'COMPLETE','case-1')"""
    )
    connection.execute(
        """INSERT INTO adjustment_decision(
            id,case_id,comparable_property_id,factor_key,selected_explicitly,
            source_data_revision,review_status,selected_rate_pct,selected_at
        ) VALUES ('decision-1','case-1','comp-1','C1',1,'rev-1','CURRENT','0','t')"""
    )
    connection.commit()


def test_schema_v3_creates_adjustment_audit_and_snapshot_tables():
    connection = _connection()
    try:
        assert apply_migrations(connection) == 3
        assert LATEST_SCHEMA_VERSION == 3
        names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert "adjustment_selection_audit" in names
        assert "adjustment_calculation_snapshot" in names
        triggers = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger'"
            )
        }
        assert "adjustment_decision_lineage_insert_guard" in triggers
        assert "adjustment_selection_audit_lineage_guard" in triggers
        assert "adjustment_snapshot_lineage_guard" in triggers
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
                ) VALUES ('bad','case-2','comp-1','C2',1,'rev-1','CURRENT')"""
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
                    'SELECTED','0',1,'appraiser','t','rev-1','CURRENT')"""
            )
        connection.execute(
            """INSERT INTO adjustment_selection_audit(
                id,adjustment_decision_id,case_id,comparable_property_id,factor_key,
                event_kind,selected_rate_pct,selected_explicitly,selected_by,selected_at,
                source_data_revision,review_status
            ) VALUES ('audit-good','decision-1','case-1','comp-1','C1',
                'SELECTED','0',1,'appraiser','t','rev-1','CURRENT')"""
        )
        assert connection.execute(
            "SELECT selected_by FROM adjustment_selection_audit WHERE id='audit-good'"
        ).fetchone()[0] == "appraiser"
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
                    normalized_base_price_vnd_per_m2,property_adjustment_base_vnd_per_m2,
                    indicated_unit_price_vnd_per_m2,decision_set_sha256,ordered_steps_json,
                    semantic_sha256,created_at
                ) VALUES ('snapshot-bad','case-2','comp-1','rev-1','1','1','1',
                    'd','[]','s','t')"""
            )
    finally:
        connection.close()
