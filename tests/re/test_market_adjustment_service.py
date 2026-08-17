from contextlib import contextmanager
from dataclasses import replace
from decimal import Decimal

import pytest

from src.re.application.services.market_adjustment import (
    MarketAdjustmentConflictError,
    MarketAdjustmentService,
)
from src.re.ports.adjustment_source import AdjustmentSourceStateRecord
from src.re.ports.persistence import CaseRecord, ComparablePropertyRecord


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
        self.before_cas = None

    def put(self, record):
        self.records[record.id] = record

    def put_if_version(self, record, *, expected_version):
        if self.before_cas is not None:
            hook, self.before_cas = self.before_cas, None
            hook()
        current = self.records.get(record.id)
        if current is None or current.version != expected_version:
            return False
        self.records[record.id] = record
        return True


class _DecisionQueryRepo:
    def __init__(self, decisions):
        self.decisions = decisions
        self.before_read = None

    def list_for_comparable(self, case_id, comparable_property_id):
        if self.before_read is not None:
            hook, self.before_read = self.before_read, None
            hook()
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


class _SourceRepo:
    def __init__(self):
        self.state = AdjustmentSourceStateRecord(
            case_id="case-1",
            comparable_property_id="comp-1",
            source_revision=1,
            normalized_base_price_vnd_per_m2=None,
            normalized_base_bound_revision=None,
            normalized_base_evidence_ref=None,
            updated_at="2026-08-17T00:00:00Z",
        )

    def get(self, case_id, comparable_property_id):
        if (
            self.state.case_id == case_id
            and self.state.comparable_property_id == comparable_property_id
        ):
            return self.state
        return None

    def ensure(self, case_id, comparable_property_id, updated_at):
        return self.state

    def bind_normalized_base(
        self,
        *,
        case_id,
        comparable_property_id,
        expected_source_revision,
        normalized_base_price_vnd_per_m2,
        evidence_ref,
        updated_at,
    ):
        if self.state.source_revision != expected_source_revision:
            raise RuntimeError("revision changed")
        self.state = replace(
            self.state,
            normalized_base_price_vnd_per_m2=normalized_base_price_vnd_per_m2,
            normalized_base_bound_revision=expected_source_revision,
            normalized_base_evidence_ref=evidence_ref,
            updated_at=updated_at,
        )
        return self.state

    def drift(self):
        self.state = replace(
            self.state,
            source_revision=self.state.source_revision + 1,
            normalized_base_price_vnd_per_m2=None,
            normalized_base_bound_revision=None,
            normalized_base_evidence_ref=None,
        )


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
        self.adjustment_decision_queries = _DecisionQueryRepo(self.adjustment_decisions)
        self.adjustment_selection_audit = _AuditRepo()
        self.adjustment_calculation_snapshots = _SnapshotRepo()
        self.adjustment_source_states = _SourceRepo()
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


def _bind_base(service):
    return service.bind_normalized_base(
        case_id="case-1",
        comparable_property_id="comp-1",
        normalized_base_price_vnd_per_m2="230951000",
        evidence_ref="fixture://N08/P0/F53",
    )


def _select_all(service):
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
        )


def test_explicit_zero_selection_is_human_audited_and_authoritatively_bound():
    service, uow = _service()
    decision = service.select_rate(
        case_id="case-1",
        comparable_property_id="comp-1",
        factor_key="C1",
        selected_rate="0.000",
        selected_by="appraiser-1",
    )
    assert decision.selected_rate_pct == "0.000"
    assert decision.selected_explicitly is True
    assert decision.source_data_revision == "1"
    assert decision.review_status == "CURRENT"
    assert uow.adjustment_selection_audit.records[0].selected_by == "appraiser-1"


def test_caller_cannot_self_certify_stale_revision():
    service, uow = _service()
    uow.adjustment_source_states.drift()
    with pytest.raises(MarketAdjustmentConflictError, match="authoritative current revision"):
        service.select_rate(
            case_id="case-1",
            comparable_property_id="comp-1",
            factor_key="C1",
            selected_rate="0",
            selected_by="appraiser-1",
            source_data_revision="1",
        )


def test_source_change_marks_decision_stale_without_overwriting_selected_rate():
    service, uow = _service()
    original = service.select_rate(
        case_id="case-1",
        comparable_property_id="comp-1",
        factor_key="C4",
        selected_rate="-0.10",
        selected_by="appraiser-1",
    )
    uow.adjustment_source_states.drift()
    updated = service.mark_source_data_changed(
        case_id="case-1", comparable_property_id="comp-1"
    )
    stale = updated[0]
    assert stale.id == original.id
    assert stale.selected_rate_pct == "-0.10"
    assert stale.source_data_revision == "1"
    assert stale.review_status == "SOURCE_DATA_CHANGED"
    assert uow.adjustment_selection_audit.records[-1].source_data_revision == "2"


def test_stale_decision_and_unbound_p0_block_calculation():
    service, uow = _service()
    _bind_base(service)
    _select_all(service)
    uow.adjustment_source_states.drift()
    service.mark_source_data_changed(case_id="case-1", comparable_property_id="comp-1")
    with pytest.raises(MarketAdjustmentConflictError, match="not evidence-bound"):
        service.run_adjustment(case_id="case-1", comparable_property_id="comp-1")


def test_complete_current_decision_set_persists_sha_bound_snapshot():
    service, uow = _service()
    _bind_base(service)
    _select_all(service)
    run = service.run_adjustment(case_id="case-1", comparable_property_id="comp-1")
    assert run.result.indicated_unit_price_vnd_per_m2 == Decimal("196308350.00")
    assert len(run.decision_set_sha256) == 64
    assert len(run.semantic_sha256) == 64
    record = uow.adjustment_calculation_snapshots.records[0]
    assert record.id == run.snapshot_id
    assert record.source_data_revision == "1"
    assert record.normalized_base_price_vnd_per_m2 == "230951000"


def test_caller_p0_must_match_evidence_bound_current_p0():
    service, _ = _service()
    _bind_base(service)
    _select_all(service)
    with pytest.raises(MarketAdjustmentConflictError, match="evidence-bound current P0"):
        service.run_adjustment(
            case_id="case-1",
            comparable_property_id="comp-1",
            normalized_base_price_vnd_per_m2="999",
        )


def test_human_reselection_between_drift_read_and_write_is_not_overwritten():
    service, uow = _service()
    original = service.select_rate(
        case_id="case-1",
        comparable_property_id="comp-1",
        factor_key="C4",
        selected_rate="-0.10",
        selected_by="appraiser-1",
    )
    uow.adjustment_source_states.drift()

    def concurrent_reselection():
        uow.adjustment_decisions.records[original.id] = replace(
            original,
            selected_rate_pct="-0.20",
            source_data_revision="2",
            review_status="CURRENT",
            version=original.version + 1,
        )

    uow.adjustment_decisions.before_cas = concurrent_reselection
    with pytest.raises(MarketAdjustmentConflictError, match="changed concurrently"):
        service.mark_source_data_changed(
            case_id="case-1", comparable_property_id="comp-1"
        )
    persisted = uow.adjustment_decisions.records[original.id]
    assert persisted.selected_rate_pct == "-0.20"
    assert persisted.version == 2


def test_snapshot_aborts_if_decision_becomes_stale_after_initial_validation():
    service, uow = _service()
    _bind_base(service)
    _select_all(service)

    read_count = 0
    original_method = uow.adjustment_decision_queries.list_for_comparable

    def guarded_read(case_id, comparable_property_id):
        nonlocal read_count
        read_count += 1
        if read_count == 2:
            first = sorted(
                uow.adjustment_decisions.records.values(),
                key=lambda item: int(item.factor_key[1:]),
            )[0]
            uow.adjustment_decisions.records[first.id] = replace(
                first,
                review_status="SOURCE_DATA_CHANGED",
                version=first.version + 1,
            )
        return original_method(case_id, comparable_property_id)

    uow.adjustment_decision_queries.list_for_comparable = guarded_read
    with pytest.raises(MarketAdjustmentConflictError, match="changed during calculation"):
        service.run_adjustment(case_id="case-1", comparable_property_id="comp-1")
    assert uow.adjustment_calculation_snapshots.records == []


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
        )
    assert not uow.adjustment_decisions.records
