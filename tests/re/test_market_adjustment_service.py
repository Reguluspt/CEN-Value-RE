from contextlib import contextmanager
from dataclasses import replace
from decimal import Decimal

import pytest

from src.re.application.services.market_adjustment import (
    MarketAdjustmentConflictError,
    MarketAdjustmentService,
)
from src.re.ports.persistence import (
    AdjustmentDecisionRecord,
    CaseRecord,
    ComparablePropertyRecord,
)


class _CaseRepo:
    def __init__(self, record):
        self.record = record

    def get(self, record_id):
        return self.record if self.record.id == record_id else None


class _ComparableRepo:
    def __init__(self, record):
        self.record = record

    def get(self, record_id):
        return self.record if self.record.property_id == record_id else None


class _DecisionRepo:
    def __init__(self):
        self.records = {}

    def put(self, record):
        self.records[record.id] = record


class _DecisionQueryRepo:
    def __init__(self, decisions):
        self.decisions = decisions

    def list_for_comparable(self, case_id, comparable_property_id):
        return tuple(
            sorted(
                (
                    item
                    for item in self.decisions.records.values()
                    if item.case_id == case_id
                    and item.comparable_property_id == comparable_property_id
                    and item.archived_at is None
                ),
                key=lambda item: int(item.factor_key[1:]),
            )
        )


class _AuditRepo:
    def __init__(self):
        self.records = []

    def add(self, record):
        self.records.append(record)


class _SnapshotRepo:
    def __init__(self):
        self.records = []

    def add(self, record):
        self.records.append(record)


class _FakeUow:
    def __init__(self):
        self.cases = _CaseRepo(
            CaseRecord(
                id="case-1",
                case_code="C-1",
                status="IN_PROGRESS",
                created_at="2026-08-17T00:00:00Z",
                updated_at="2026-08-17T00:00:00Z",
            )
        )
        self.comparables = _ComparableRepo(
            ComparablePropertyRecord(
                property_id="comp-1",
                case_id="case-1",
                legal_address="A",
                current_address="A",
                comparable_order=1,
                completeness_status="COMPLETE",
                created_at="2026-08-17T00:00:00Z",
                updated_at="2026-08-17T00:00:00Z",
            )
        )
        self.adjustment_decisions = _DecisionRepo()
        self.adjustment_decision_queries = _DecisionQueryRepo(
            self.adjustment_decisions
        )
        self.adjustment_selection_audit = _AuditRepo()
        self.adjustment_calculation_snapshots = _SnapshotRepo()
        self.atomic_entries = 0

    @contextmanager
    def atomic(self):
        self.atomic_entries += 1
        yield


class _Ids:
    def __init__(self):
        self.value = 0

    def __call__(self):
        self.value += 1
        return f"id-{self.value}"


def _service():
    uow = _FakeUow()
    service = MarketAdjustmentService(
        uow,
        now=lambda: "2026-08-17T01:02:03Z",
        new_id=_Ids(),
    )
    return service, uow


def _select_all(service, *, revision="rev-1"):
    rates = {
        "C1": "0",
        "C2": "-0.05",
        "C3": "0",
        "C4": "-0.1",
        "C5": "0",
        "C6": "0",
        "C7": "0",
        "C8": "0",
        "C9": "0",
        "C10": "0",
        "C11": "0",
    }
    for key, value in rates.items():
        service.select_rate(
            case_id="case-1",
            comparable_property_id="comp-1",
            factor_key=key,
            selected_rate=value,
            selected_by="appraiser-1",
            source_data_revision=revision,
        )


def test_explicit_zero_selection_is_human_audited_and_not_missing():
    service, uow = _service()
    decision = service.select_rate(
        case_id="case-1",
        comparable_property_id="comp-1",
        factor_key="C1",
        selected_rate="0.000",
        selected_by="appraiser-1",
        source_data_revision="rev-1",
    )
    assert decision.selected_rate_pct == "0.000"
    assert decision.selected_explicitly is True
    assert decision.review_status == "CURRENT"
    assert uow.adjustment_selection_audit.records[0].event_kind == "SELECTED"
    assert uow.adjustment_selection_audit.records[0].selected_by == "appraiser-1"
    assert uow.adjustment_selection_audit.records[0].selected_rate_pct == "0.000"


def test_source_change_marks_decision_stale_without_overwriting_selected_rate():
    service, uow = _service()
    original = service.select_rate(
        case_id="case-1",
        comparable_property_id="comp-1",
        factor_key="C4",
        selected_rate="-0.10",
        selected_by="appraiser-1",
        source_data_revision="rev-1",
    )
    updated = service.mark_source_data_changed(
        case_id="case-1",
        comparable_property_id="comp-1",
        new_source_data_revision="rev-2",
    )
    assert len(updated) == 1
    stale = updated[0]
    assert stale.id == original.id
    assert stale.selected_rate_pct == "-0.10"
    assert stale.source_data_revision == "rev-1"
    assert stale.review_status == "SOURCE_DATA_CHANGED"
    audit = uow.adjustment_selection_audit.records[-1]
    assert audit.event_kind == "SOURCE_DATA_CHANGED"
    assert audit.source_data_revision == "rev-2"
    assert audit.selected_by == "SYSTEM_SOURCE_DRIFT"


def test_stale_decision_blocks_calculation_until_human_reselects():
    service, _ = _service()
    _select_all(service)
    service.mark_source_data_changed(
        case_id="case-1",
        comparable_property_id="comp-1",
        new_source_data_revision="rev-2",
    )
    with pytest.raises(MarketAdjustmentConflictError, match="human review"):
        service.run_adjustment(
            case_id="case-1",
            comparable_property_id="comp-1",
            source_data_revision="rev-2",
            normalized_base_price_vnd_per_m2="230951000",
        )


def test_complete_current_decision_set_persists_sha_bound_snapshot():
    service, uow = _service()
    _select_all(service)
    run = service.run_adjustment(
        case_id="case-1",
        comparable_property_id="comp-1",
        source_data_revision="rev-1",
        normalized_base_price_vnd_per_m2="230951000",
    )
    assert run.result.indicated_unit_price_vnd_per_m2 == Decimal("196308350.00")
    assert len(run.decision_set_sha256) == 64
    assert len(run.semantic_sha256) == 64
    assert len(uow.adjustment_calculation_snapshots.records) == 1
    record = uow.adjustment_calculation_snapshots.records[0]
    assert record.id == run.snapshot_id
    assert record.decision_set_sha256 == run.decision_set_sha256
    assert record.semantic_sha256 == run.semantic_sha256
    assert record.indicated_unit_price_vnd_per_m2 == "196308350.00"
    assert '"factor_key":"C1"' in record.ordered_steps_json
    assert '"factor_key":"C11"' in record.ordered_steps_json


def test_decision_set_revision_mismatch_blocks_calculation():
    service, _ = _service()
    _select_all(service, revision="rev-1")
    with pytest.raises(MarketAdjustmentConflictError, match="current source-data revision"):
        service.run_adjustment(
            case_id="case-1",
            comparable_property_id="comp-1",
            source_data_revision="rev-2",
            normalized_base_price_vnd_per_m2="230951000",
        )


def test_comparable_case_lineage_mismatch_fails_before_write():
    service, uow = _service()
    uow.comparables.record = replace(uow.comparables.record, case_id="other-case")
    with pytest.raises(MarketAdjustmentConflictError, match="does not belong"):
        service.select_rate(
            case_id="case-1",
            comparable_property_id="comp-1",
            factor_key="C1",
            selected_rate="0",
            selected_by="appraiser-1",
            source_data_revision="rev-1",
        )
    assert not uow.adjustment_decisions.records
    assert not uow.adjustment_selection_audit.records
