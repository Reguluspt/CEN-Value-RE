"""E1-PR-006 application/local-service integration proofs."""

from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from dataclasses import dataclass

from src.re.adapters.local_service import (
    AUTHORIZATION_HEADER,
    LAUNCH_ID_HEADER,
    LaunchSession,
    create_local_service_app,
)
from src.re.application.services.manual_workbench import (
    ManualWorkbenchConflictError,
    ManualWorkbenchService,
)
from src.re.domain.common.rounding import RoundingSource
from src.re.ports.adjustment_persistence import AdjustmentCalculationSnapshotRecord
from src.re.ports.adjustment_source import AdjustmentSourceStateRecord
from src.re.ports.excel import TemplateRoundingDefaultRecord
from src.re.ports.persistence import (
    AdjustmentDecisionRecord,
    CaseRecord,
    ComparablePropertyRecord,
)


def _sha(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class _Cases:
    def __init__(self, case):
        self.case = case

    def get(self, case_id):
        return self.case if self.case.id == case_id else None


class _Comparables:
    def __init__(self, records):
        self.records = tuple(records)

    def list_for_case(self, case_id):
        return tuple(item for item in self.records if item.case_id == case_id)


class _SourceStates:
    def __init__(self, record):
        self.record = record

    def get(self, case_id, comparable_property_id):
        if (
            self.record is not None
            and self.record.case_id == case_id
            and self.record.comparable_property_id == comparable_property_id
        ):
            return self.record
        return None


class _DecisionQueries:
    def __init__(self, records):
        self.records = tuple(records)

    def list_for_comparable(self, case_id, comparable_property_id):
        return tuple(
            item
            for item in self.records
            if item.case_id == case_id
            and item.comparable_property_id == comparable_property_id
        )


class _Snapshots:
    def __init__(self, records):
        self.records = tuple(records)

    def list_for_comparable(self, case_id, comparable_property_id):
        return tuple(
            item
            for item in self.records
            if item.case_id == case_id
            and item.comparable_property_id == comparable_property_id
        )


class _Uow:
    def __init__(self, case, comparable, source=None, decisions=(), snapshots=()):
        self.cases = _Cases(case)
        self.comparables = _Comparables((comparable,))
        self.adjustment_source_states = _SourceStates(source)
        self.adjustment_decision_queries = _DecisionQueries(decisions)
        self.adjustment_calculation_snapshots = _Snapshots(snapshots)
        self.atomic_calls = 0

    @contextmanager
    def atomic(self):
        self.atomic_calls += 1
        yield


class _NoopMarket:
    pass


class _Quality:
    def __init__(self):
        self.confirm_call = None

    def confirm_indication(self, **kwargs):
        self.confirm_call = kwargs
        return kwargs

    def preview(self, **kwargs):
        return kwargs

    def resolve_current_indication(self, **kwargs):
        return kwargs


class _Final:
    def __init__(self):
        self.compose_call = None

    def compose(self, **kwargs):
        self.compose_call = kwargs
        return kwargs

    def resolve_current(self, **kwargs):
        return kwargs

    def bind_supplied_construction_aggregate(self, **kwargs):
        return kwargs


class _Workbook:
    def generate(self, **kwargs):
        return kwargs


class _RoundingDefaults:
    def resolve(self, *, profile_id, profile_version, target):
        increments = {"UNIT_PRICE": 1_000, "TOTAL_VALUE": 1_000_000}
        return TemplateRoundingDefaultRecord(
            profile_id=profile_id,
            profile_version=profile_version,
            target=target,
            mode="NEAREST",
            increment_vnd=increments[target],
        )


def _case():
    return CaseRecord(
        id="case-1",
        case_code="CV-WORKBENCH",
        status="IN_PROGRESS",
        created_at="t",
        updated_at="t",
        appraisal_date="2026-08-18",
        template_profile_id="cenvalue-re-n08-0038-v1",
        template_profile_version="1",
    )


def _comparable():
    return ComparablePropertyRecord(
        property_id="comp-1",
        case_id="case-1",
        legal_address="L",
        current_address="C",
        comparable_order=1,
        completeness_status="COMPLETE",
        created_at="t",
        updated_at="t",
    )


def _decisions(*, stale=False):
    return tuple(
        AdjustmentDecisionRecord(
            id=f"decision-{index}",
            case_id="case-1",
            comparable_property_id="comp-1",
            factor_key=f"C{index}",
            selected_explicitly=True,
            source_data_revision="1",
            review_status="SOURCE_DATA_CHANGED" if stale and index == 1 else "CURRENT",
            selected_rate_pct="0" if index == 1 else "0.05",
            selected_at=f"t{index}",
            version=1,
        )
        for index in range(1, 12)
    )


def _decision_sha(records):
    return _sha(
        [
            {
                "id": item.id,
                "factor_key": item.factor_key,
                "selected_rate_pct": item.selected_rate_pct,
                "selected_explicitly": item.selected_explicitly,
                "source_data_revision": item.source_data_revision,
                "review_status": item.review_status,
                "selected_at": item.selected_at,
                "version": item.version,
            }
            for item in records
        ]
    )


def _snapshot(records):
    decision_sha = _decision_sha(records)
    steps = [
        {
            "factor_key": f"C{index}",
            "selected_rate_fraction": "0" if index == 1 else "0.05",
            "amount_base_vnd_per_m2": "100",
            "adjustment_amount_vnd_per_m2": "0" if index == 1 else "5",
            "running_price_vnd_per_m2": "100",
        }
        for index in range(1, 12)
    ]
    payload = {
        "case_id": "case-1",
        "comparable_property_id": "comp-1",
        "source_data_revision": "1",
        "normalized_base_price_vnd_per_m2": "100",
        "normalized_base_evidence_ref": "manual-p0",
        "property_adjustment_base_vnd_per_m2": "100",
        "indicated_unit_price_vnd_per_m2": "150",
        "decision_set_sha256": decision_sha,
        "steps": steps,
    }
    return AdjustmentCalculationSnapshotRecord(
        id="run-1",
        case_id="case-1",
        comparable_property_id="comp-1",
        source_data_revision="1",
        normalized_base_price_vnd_per_m2="100",
        normalized_base_evidence_ref="manual-p0",
        property_adjustment_base_vnd_per_m2="100",
        indicated_unit_price_vnd_per_m2="150",
        decision_set_sha256=decision_sha,
        ordered_steps_json=json.dumps(steps, separators=(",", ":")),
        semantic_sha256=_sha(payload),
        created_at="t",
    )


def _service(uow, *, quality=None, final=None):
    return ManualWorkbenchService(
        uow,
        market_adjustment=_NoopMarket(),
        comparable_quality=quality or _Quality(),
        final_valuation=final or _Final(),
        workbook_output=_Workbook(),
        template_rounding_defaults=_RoundingDefaults(),
    )


def test_adjustment_resume_preserves_explicit_zero_and_only_exposes_current_run():
    decisions = _decisions()
    source = AdjustmentSourceStateRecord(
        case_id="case-1",
        comparable_property_id="comp-1",
        source_revision=1,
        normalized_base_price_vnd_per_m2="100",
        normalized_base_bound_revision=1,
        normalized_base_evidence_ref="manual-p0",
        updated_at="t",
    )
    snapshot = _snapshot(decisions)
    uow = _Uow(_case(), _comparable(), source, decisions, (snapshot,))
    state = _service(uow).adjustment_state(case_id="case-1", comparable_order=1)

    assert state.decisions[0].factor_key == "C1"
    assert state.decisions[0].selected_explicitly is True
    assert state.decisions[0].selected_rate_pct == "0"
    assert state.current_run == snapshot

    stale = _decisions(stale=True)
    stale_uow = _Uow(_case(), _comparable(), source, stale, (snapshot,))
    stale_state = _service(stale_uow).adjustment_state(
        case_id="case-1", comparable_order=1
    )
    assert stale_state.decisions[0].selected_rate_pct == "0"
    assert stale_state.current_run is None


def test_workbench_constructs_template_rounding_policy_server_side():
    quality = _Quality()
    final = _Final()
    service = _service(_Uow(_case(), _comparable()), quality=quality, final=final)

    service.confirm_indication(
        case_id="case-1",
        selection_kind="COMPARABLE",
        selected_comparable_order=1,
        confirmed_by="valuer-1",
        reason="manual confirmation",
    )
    unit_policy = quality.confirm_call["rounding_policy"]
    assert unit_policy.source is RoundingSource.TEMPLATE_DEFAULT
    assert unit_policy.increment_vnd == 1_000
    assert unit_policy.profile_id == "cenvalue-re-n08-0038-v1"

    service.compose_final_valuation(case_id="case-1")
    total_policy = final.compose_call["total_value_rounding_policy"]
    assert total_policy.source is RoundingSource.TEMPLATE_DEFAULT
    assert total_policy.increment_vnd == 1_000_000


@dataclass(frozen=True, slots=True)
class _RouteState:
    selected_rate_pct: str
    selected_explicitly: bool


class _RouteWorkbench:
    def adjustment_state(self, **_kwargs):
        return _RouteState(selected_rate_pct="0", selected_explicitly=True)

    def select_adjustment_rate(self, **kwargs):
        return _RouteState(
            selected_rate_pct=kwargs["selected_rate"],
            selected_explicitly=True,
        )

    def quality_preview(self, **_kwargs):
        raise ManualWorkbenchConflictError("C1-C11 evidence is incomplete")


def test_workbench_routes_inherit_session_guard_and_structured_fail_closed_errors():
    session, credential = LaunchSession.issue()
    client = create_local_service_app(
        session,
        manual_workbench=_RouteWorkbench(),
    ).test_client()
    path = "/api/re/manual-cases/case-1/comparables/1/adjustment"

    anonymous = client.get(path)
    assert anonymous.status_code == 401
    assert anonymous.get_json()["error"]["code"] == "RE_SESSION_REQUIRED"

    headers = {
        LAUNCH_ID_HEADER: credential.launch_id,
        AUTHORIZATION_HEADER: f"Bearer {credential.bearer_token}",
    }
    current = client.get(path, headers=headers)
    assert current.status_code == 200
    assert current.get_json() == {
        "selected_explicitly": True,
        "selected_rate_pct": "0",
    }

    selected = client.put(
        "/api/re/manual-cases/case-1/comparables/1/adjustments/C1",
        headers=headers,
        json={
            "selected_rate": "0",
            "selected_by": "valuer-1",
            "source_data_revision": "1",
        },
    )
    assert selected.status_code == 200
    assert selected.get_json()["selected_rate_pct"] == "0"

    blocked = client.get("/api/re/manual-cases/case-1/quality", headers=headers)
    assert blocked.status_code == 409
    assert blocked.get_json() == {
        "error": {
            "code": "RE_WORKBENCH_BLOCKED",
            "message": "C1-C11 evidence is incomplete",
        }
    }
    assert credential.bearer_token not in blocked.get_data(as_text=True)
