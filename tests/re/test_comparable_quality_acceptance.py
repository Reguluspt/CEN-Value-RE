import hashlib
import json
import sqlite3

import pytest

from src.re.adapters.persistence.migrations import apply_migrations
from src.re.adapters.persistence.store import SQLCipherUnitOfWork
from src.re.application.services.comparable_quality import (
    ComparableQualityConflictError,
    ComparableQualityService,
)
from src.re.application.services.market_adjustment import MarketAdjustmentService
from src.re.domain.common.rounding import (
    RoundingPolicy,
    RoundingSource,
    UNIT_PRICE_TARGET,
)


def _dict_factory(cursor, row):
    return {column[0]: row[index] for index, column in enumerate(cursor.description)}


def _connection():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = _dict_factory
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def _seed_case(connection):
    connection.execute(
        """INSERT INTO appraisal_case(
            id,case_code,status,created_at,updated_at,
            template_profile_id,template_profile_version
        ) VALUES ('case-1','CV-E1-003-A','IN_PROGRESS','t','t',
            'cenvalue-re-n08-0038-v1','1')"""
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


def _rounding_policy():
    return RoundingPolicy(
        target=UNIT_PRICE_TARGET,
        increment_vnd=1000,
        source=RoundingSource.TEMPLATE_DEFAULT,
        profile_id="cenvalue-re-n08-0038-v1",
        profile_version="1",
    )


def _select_all(market, comp_id, *, c2="0"):
    for index in range(1, 12):
        market.select_rate(
            case_id="case-1",
            comparable_property_id=comp_id,
            factor_key=f"C{index}",
            selected_rate=c2 if index == 2 else "0",
            selected_by="appraiser",
        )


def _semantic_sha(snapshot, sources):
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


def test_zero_gross_tie_average_is_supported_only_after_current_adjustment_runs():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_case(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        market = MarketAdjustmentService(
            uow,
            now=lambda: "2026-08-17T14:00:00Z",
            new_id=iter((f"adj-{index}" for index in range(1, 200))).__next__,
        )
        for comp_id, p0, c2 in (
            ("comp-1", "90000", "0"),
            ("comp-2", "110000", "0"),
            ("comp-3", "120000", "0.10"),
        ):
            market.bind_normalized_base(
                case_id="case-1",
                comparable_property_id=comp_id,
                normalized_base_price_vnd_per_m2=p0,
                evidence_ref=f"source://{comp_id}/P0",
            )
            _select_all(market, comp_id, c2=c2)
            market.run_adjustment(case_id="case-1", comparable_property_id=comp_id)

        service = ComparableQualityService(
            uow,
            now=lambda: "2026-08-17T14:01:00Z",
            new_id=lambda: "human-zero-tie",
        )
        preview = service.preview(case_id="case-1")
        assert preview.guidance.kind == "ZERO_GROSS_AVERAGE"
        assert preview.guidance.candidate_comparable_ids == ("comp-1", "comp-2")
        assert preview.guidance.proposed_indicated_unit_price_vnd_per_m2 == 100000

        confirmed = service.confirm_indication(
            case_id="case-1",
            selection_kind="ZERO_GROSS_AVERAGE",
            selected_comparable_property_id=None,
            confirmed_by="appraiser",
            reason="Frozen zero-gross tie reviewed and confirmed",
            rounding_policy=_rounding_policy(),
        )
        assert confirmed.raw_indicated_unit_price_vnd_per_m2 == 100000
        assert confirmed.rounded_indicated_unit_price_vnd_per_m2 == 100000
        persisted = uow.human_indication_snapshots.get("human-zero-tie")
        assert persisted is not None
        assert persisted.selection_kind == "ZERO_GROSS_AVERAGE"
        assert persisted.selected_comparable_property_id is None
        assert service.resolve_current_indication(case_id="case-1") == persisted
    finally:
        connection.close()


def test_confirmed_human_snapshot_stays_reproducible_but_is_not_current_after_source_drift():
    connection = _connection()
    try:
        schema_version = apply_migrations(connection)
        _seed_case(connection)
        uow = SQLCipherUnitOfWork(connection, schema_version)
        market = MarketAdjustmentService(
            uow,
            now=lambda: "2026-08-17T14:10:00Z",
            new_id=iter((f"adj-x-{index}" for index in range(1, 300))).__next__,
        )
        for comp_id, p0 in (
            ("comp-1", "100000"),
            ("comp-2", "105000"),
            ("comp-3", "110000"),
        ):
            market.bind_normalized_base(
                case_id="case-1",
                comparable_property_id=comp_id,
                normalized_base_price_vnd_per_m2=p0,
                evidence_ref=f"source://{comp_id}/P0-A",
            )
            _select_all(market, comp_id)
            market.run_adjustment(case_id="case-1", comparable_property_id=comp_id)

        service = ComparableQualityService(
            uow,
            now=lambda: "2026-08-17T14:11:00Z",
            new_id=lambda: "human-before-drift",
        )
        service.confirm_indication(
            case_id="case-1",
            selection_kind="ZERO_GROSS_AVERAGE",
            selected_comparable_property_id=None,
            confirmed_by="appraiser",
            reason="All three zero-gross comparables reviewed",
            rounding_policy=_rounding_policy(),
        )
        before = uow.human_indication_snapshots.get("human-before-drift")
        before_sources = uow.human_indication_sources.list_for_snapshot(
            "human-before-drift"
        )
        assert before is not None
        assert len(before_sources) == 3
        assert _semantic_sha(before, before_sources) == before.semantic_sha256
        assert service.resolve_current_indication(case_id="case-1") == before

        market.bind_normalized_base(
            case_id="case-1",
            comparable_property_id="comp-1",
            normalized_base_price_vnd_per_m2="999000",
            evidence_ref="source://comp-1/P0-B",
        )

        after = uow.human_indication_snapshots.get("human-before-drift")
        after_sources = uow.human_indication_sources.list_for_snapshot(
            "human-before-drift"
        )
        assert after == before
        assert after_sources == before_sources
        assert _semantic_sha(after, after_sources) == after.semantic_sha256

        _select_all(market, "comp-1")
        market.run_adjustment(case_id="case-1", comparable_property_id="comp-1")
        with pytest.raises(ComparableQualityConflictError, match="reconfirmation"):
            service.resolve_current_indication(case_id="case-1")
    finally:
        connection.close()
