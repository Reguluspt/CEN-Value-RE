import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.re.adapters.excel import SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS
from src.re.adapters.persistence.migrations import LATEST_SCHEMA_VERSION, apply_migrations
from src.re.adapters.persistence.store import SQLCipherUnitOfWork
from src.re.application.services.comparable_quality import (
    ComparableQualityConflictError,
    ComparableQualityService,
    ComparableQualityValidationError,
)
from src.re.application.services.market_adjustment import MarketAdjustmentService
from src.re.domain.common.rounding import (
    RoundingPolicy,
    RoundingSource,
    UNIT_PRICE_TARGET,
)


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


def _quality_service(uow, **kwargs):
    return ComparableQualityService(
        uow,
        template_rounding_defaults=SUPPORTED_TEMPLATE_ROUNDING_DEFAULTS,
        **kwargs,
    )


def _seed_three_comparables(connection):
    connection.execute(
        """INSERT INTO appraisal_case(
            id,case_code,status,created_at,updated_at,
            template_profile_id,template_profile_version
        ) VALUES ('case-1','CV-E1-003','IN_PROGRESS','t','t',
            'cenvalue-re-n08-0038-v1','1')"""
    )
    for index in range(1, 4):
        comp_id = f"comp-{index}"
        connection.execute(
            """INSERT INTO property(
                id,case_id,role,legal_address,current_address,created_at,updated_at
            ) VALUES (?,?,?,?,?,?,?)""",
            (comp_id, "case-1", "COMPARABLE", f"A{index}", f"A{index}", "t", "t"),
        )
        connection.execute(
            """INSERT INTO comparable_property(
                property_id,case_id,comparable_order,completeness_status
            ) VALUES (?,?,?,?)""",
            (comp_id, "case-1", index, "COMPLETE"),
        )
    connection.commit()


def _build_golden_adjustment_evidence(uow):
    fixture = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    p0_values = ("230951000", "239035000", "196483000")
    market = MarketAdjustmentService(
        uow,
        now=lambda: "2026-08-17T13:00:00Z",
        new_id=iter((f"id-{index}" for index in range(1, 1000))).__next__,
    )
    snapshots = []
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
        snapshots.append(
            market.run_adjustment(
                case_id="case-1", comparable_property_id=comp_id
            )
        )
    return market, tuple(snapshots)


def _rounding_policy():
    return RoundingPolicy(
        target=UNIT_PRICE_TARGET,
        increment_vnd=1000,
        source=RoundingSource.TEMPLATE_DEFAULT,
        profile_id="cenvalue-re-n08-0038-v1",
        profile_version="1",
    )


def _recompute_human_semantic_sha(snapshot, sources):
    payload = {
        "case_id": snapshot.case_id,
        "selection_kind": snapshot.selection_kind,
        "selected_comparable_property_id": snapshot.selected_comparable_property_id,
        "raw_indicated_unit_price_vnd_per_m2": snapshot.raw_indicated_unit_price_vnd_per_m2,
        "rounded_indicated_unit_price_vnd_per_m2": snapshot.rounded_indicated_unit_price_vnd_per_m2,
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
        "confirmed_by": snapshot.confirmed_by,
        "confirmed_at": snapshot.confirmed_at,
        "reason": snapshot.reason,
        "sources": [
            {
                "comparable_property_id": item.comparable_property_id,
                "adjustment_snapshot_id": item.adjustment_snapshot_id,
                "adjustment_semantic_sha256": item.adjustment_semantic_sha256,
            }
            for item in sorted(sources, key=lambda current: current.comparable_property_id)
        ],
        "quality": json.loads(snapshot.quality_snapshot_json),
        "readiness": json.loads(snapshot.readiness_snapshot_json),
        "guidance": json.loads(snapshot.guidance_snapshot_json),
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def test_schema_v4_creates_append_only_human_indication_evidence():
    connection = _connection()
    try:
        assert apply_migrations(connection) == LATEST_SCHEMA_VERSION
        assert LATEST_SCHEMA_VERSION >= 4
        names = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert "human_indication_snapshot" in names
        assert "human_indication_source" in names
        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(human_indication_snapshot)"
            )
        }
        assert {
            "rounding_mode",
            "rounding_selected_by",
            "rounding_selected_at",
        }.issubset(columns)
        triggers = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger'"
            )
        }
        assert "human_indication_snapshot_update_guard" in triggers
        assert "human_indication_snapshot_delete_guard" in triggers
        assert "human_indication_source_lineage_guard" in triggers
    finally:
        connection.close()


def test_golden_preview_and_human_confirmation_match_g18_h119():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_three_comparables(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        _, source_runs = _build_golden_adjustment_evidence(uow)
        service = _quality_service(
            uow,
            now=lambda: "2026-08-17T13:30:00Z",
            new_id=lambda: "human-1",
        )

        preview = service.preview(case_id="case-1")
        assert tuple(
            item.quality.indicated_unit_price_vnd_per_m2
            for item in preview.comparables
        ) == (
            196308350,
            227083250,
            212201640,
        )
        assert tuple(item.quality.adjustment_count for item in preview.comparables) == (
            2,
            4,
            4,
        )
        assert tuple(
            item.quality.gross_adjustment_value_vnd_per_m2
            for item in preview.comparables
        ) == (34642650, 83662250, 35366940)
        assert tuple(
            item.quality.net_adjustment_value_vnd_per_m2
            for item in preview.comparables
        ) == (-34642650, -11951750, 15718640)
        assert preview.readiness.status == "READY"
        assert preview.guidance.kind == "COMPARABLE"
        assert preview.guidance.recommended_comparable_id == "comp-1"

        result = service.confirm_indication(
            case_id="case-1",
            selection_kind="COMPARABLE",
            selected_comparable_property_id="comp-1",
            confirmed_by="appraiser-1",
            reason="Minimum gross adjustment and comparable evidence reviewed",
            rounding_policy=_rounding_policy(),
        )
        assert result.raw_indicated_unit_price_vnd_per_m2 == 196308350
        assert result.rounded_indicated_unit_price_vnd_per_m2 == 196308000

        persisted = uow.human_indication_snapshots.get("human-1")
        assert persisted is not None
        assert persisted.raw_indicated_unit_price_vnd_per_m2 in {
            "196308350.00",
            "196308350",
        }
        assert persisted.rounded_indicated_unit_price_vnd_per_m2 == "196308000"
        assert persisted.rounding_target == "UNIT_PRICE"
        assert persisted.rounding_mode == "NEAREST"
        assert persisted.rounding_source == "TEMPLATE_DEFAULT"
        assert persisted.rounding_selected_by is None
        assert persisted.rounding_selected_at is None
        sources = uow.human_indication_sources.list_for_snapshot("human-1")
        assert len(sources) == 3
        assert {item.adjustment_snapshot_id for item in sources} == {
            item.snapshot_id for item in source_runs
        }
        assert _recompute_human_semantic_sha(persisted, sources) == persisted.semantic_sha256
        assert service.resolve_current_indication(case_id="case-1") == persisted
    finally:
        connection.close()


def test_case_override_rounding_metadata_is_audited_in_confirmation_snapshot():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_three_comparables(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        _build_golden_adjustment_evidence(uow)
        selected_at = datetime(2026, 8, 17, 13, 35, tzinfo=timezone.utc)
        policy = RoundingPolicy(
            target=UNIT_PRICE_TARGET,
            increment_vnd=10000,
            source=RoundingSource.CASE_OVERRIDE,
            profile_id="cenvalue-re-n08-0038-v1",
            profile_version="1",
            selected_by="rounding-appraiser",
            selected_at=selected_at,
        )
        service = _quality_service(
            uow,
            now=lambda: "2026-08-17T13:36:00Z",
            new_id=lambda: "human-case-rounding",
        )
        result = service.confirm_indication(
            case_id="case-1",
            selection_kind="COMPARABLE",
            selected_comparable_property_id="comp-1",
            confirmed_by="final-appraiser",
            reason="Case-level rounding override reviewed",
            rounding_policy=policy,
        )
        assert result.raw_indicated_unit_price_vnd_per_m2 == 196308350
        assert result.rounded_indicated_unit_price_vnd_per_m2 == 196310000
        persisted = uow.human_indication_snapshots.get("human-case-rounding")
        assert persisted is not None
        assert persisted.rounding_source == "CASE_OVERRIDE"
        assert persisted.rounding_mode == "NEAREST"
        assert persisted.rounding_increment_vnd == 10000
        assert persisted.rounding_selected_by == "rounding-appraiser"
        assert persisted.rounding_selected_at == selected_at.isoformat()
    finally:
        connection.close()


@pytest.mark.parametrize("bad_increment", [None, 10000])
def test_n08_template_default_rejects_increment_not_declared_by_profile(bad_increment):
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_three_comparables(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        _build_golden_adjustment_evidence(uow)
        service = _quality_service(uow)
        invalid_default = RoundingPolicy(
            target=UNIT_PRICE_TARGET,
            increment_vnd=bad_increment,
            source=RoundingSource.TEMPLATE_DEFAULT,
            profile_id="cenvalue-re-n08-0038-v1",
            profile_version="1",
        )
        with pytest.raises(ComparableQualityConflictError, match="trusted profile default"):
            service.confirm_indication(
                case_id="case-1",
                selection_kind="COMPARABLE",
                selected_comparable_property_id="comp-1",
                confirmed_by="appraiser",
                reason="attempted false template default",
                rounding_policy=invalid_default,
            )
    finally:
        connection.close()


def test_template_default_rounding_requires_trusted_profile_resolver():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_three_comparables(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        _build_golden_adjustment_evidence(uow)
        service = ComparableQualityService(uow)
        with pytest.raises(ComparableQualityConflictError, match="trusted template-profile resolver"):
            service.confirm_indication(
                case_id="case-1",
                selection_kind="COMPARABLE",
                selected_comparable_property_id="comp-1",
                confirmed_by="appraiser",
                reason="resolver intentionally missing",
                rounding_policy=_rounding_policy(),
            )
    finally:
        connection.close()


def test_template_default_rounding_must_match_case_profile():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_three_comparables(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        _build_golden_adjustment_evidence(uow)
        service = _quality_service(uow)
        wrong_profile = RoundingPolicy(
            target=UNIT_PRICE_TARGET,
            increment_vnd=1000,
            source=RoundingSource.TEMPLATE_DEFAULT,
            profile_id="other-profile",
            profile_version="1",
        )
        with pytest.raises(ComparableQualityConflictError, match="case profile"):
            service.confirm_indication(
                case_id="case-1",
                selection_kind="COMPARABLE",
                selected_comparable_property_id="comp-1",
                confirmed_by="appraiser",
                reason="attempted wrong profile",
                rounding_policy=wrong_profile,
            )
    finally:
        connection.close()


def test_human_can_choose_nonrecommended_current_comparable_but_not_arbitrary_price():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_three_comparables(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        _build_golden_adjustment_evidence(uow)
        service = _quality_service(
            uow,
            now=lambda: "2026-08-17T13:31:00Z",
            new_id=lambda: "human-2",
        )
        result = service.confirm_indication(
            case_id="case-1",
            selection_kind="COMPARABLE",
            selected_comparable_property_id="comp-2",
            confirmed_by="appraiser-1",
            reason="Professional judgement after reviewing comparable evidence",
            rounding_policy=_rounding_policy(),
        )
        assert result.raw_indicated_unit_price_vnd_per_m2 == 227083250
        assert result.rounded_indicated_unit_price_vnd_per_m2 == 227083000

        with pytest.raises(ComparableQualityValidationError):
            service.confirm_indication(
                case_id="case-1",
                selection_kind="MANUAL_PRICE",
                selected_comparable_property_id=None,
                confirmed_by="appraiser-1",
                reason="not supported",
                rounding_policy=_rounding_policy(),
            )
    finally:
        connection.close()


def test_reselection_after_snapshot_blocks_quality_until_adjustment_is_rerun():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_three_comparables(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        market, _ = _build_golden_adjustment_evidence(uow)
        service = _quality_service(uow)
        assert service.preview(case_id="case-1").guidance.kind == "COMPARABLE"

        market.select_rate(
            case_id="case-1",
            comparable_property_id="comp-1",
            factor_key="C2",
            selected_rate="-0.04",
            selected_by="appraiser-1",
        )
        with pytest.raises(ComparableQualityConflictError, match="fresh"):
            service.preview(case_id="case-1")

        market.run_adjustment(case_id="case-1", comparable_property_id="comp-1")
        assert service.preview(case_id="case-1").comparables[0].quality.adjustment_count == 2
    finally:
        connection.close()


def test_human_confirmation_requires_actor_reason_and_current_supported_average():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_three_comparables(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        _build_golden_adjustment_evidence(uow)
        service = _quality_service(uow)

        with pytest.raises(ComparableQualityValidationError, match="confirmed_by"):
            service.confirm_indication(
                case_id="case-1",
                selection_kind="COMPARABLE",
                selected_comparable_property_id="comp-1",
                confirmed_by=" ",
                reason="reviewed",
                rounding_policy=_rounding_policy(),
            )
        with pytest.raises(ComparableQualityValidationError, match="reason"):
            service.confirm_indication(
                case_id="case-1",
                selection_kind="COMPARABLE",
                selected_comparable_property_id="comp-1",
                confirmed_by="appraiser",
                reason=" ",
                rounding_policy=_rounding_policy(),
            )
        with pytest.raises(ComparableQualityConflictError, match="zero-gross"):
            service.confirm_indication(
                case_id="case-1",
                selection_kind="ZERO_GROSS_AVERAGE",
                selected_comparable_property_id=None,
                confirmed_by="appraiser",
                reason="attempted unsupported average",
                rounding_policy=_rounding_policy(),
            )
    finally:
        connection.close()


def test_persisted_human_indication_and_source_rows_are_immutable():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_three_comparables(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        _build_golden_adjustment_evidence(uow)
        service = _quality_service(
            uow,
            now=lambda: "2026-08-17T13:40:00Z",
            new_id=lambda: "human-immutable",
        )
        service.confirm_indication(
            case_id="case-1",
            selection_kind="COMPARABLE",
            selected_comparable_property_id="comp-1",
            confirmed_by="appraiser",
            reason="reviewed",
            rounding_policy=_rounding_policy(),
        )

        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "UPDATE human_indication_snapshot SET reason='tampered' WHERE id='human-immutable'"
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "DELETE FROM human_indication_snapshot WHERE id='human-immutable'"
            )
        source = uow.human_indication_sources.list_for_snapshot("human-immutable")[0]
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                """UPDATE human_indication_source SET adjustment_semantic_sha256='bad'
                WHERE indication_snapshot_id=? AND comparable_property_id=?""",
                (source.indication_snapshot_id, source.comparable_property_id),
            )
    finally:
        connection.close()
