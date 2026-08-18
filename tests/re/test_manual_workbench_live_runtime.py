"""Live-listener proof for E1-PR-006 service injection."""

from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.request import Request, urlopen

from src.re.adapters.local_service import (
    AUTHORIZATION_HEADER,
    LAUNCH_ID_HEADER,
    LocalServiceConfig,
    LocalServiceRuntime,
)


@dataclass(frozen=True, slots=True)
class _AdjustmentState:
    selected_rate_pct: str
    selected_explicitly: bool


class _Workbench:
    def adjustment_state(self, **_kwargs):
        return _AdjustmentState(
            selected_rate_pct="0",
            selected_explicitly=True,
        )


def test_live_runtime_serves_injected_workbench_capability_under_launch_guard():
    runtime = LocalServiceRuntime(
        LocalServiceConfig(host="127.0.0.1", port=0),
        manual_workbench=_Workbench(),
    )
    bootstrap = runtime.start()
    try:
        request = Request(
            f"{bootstrap.base_url}/api/re/manual-cases/case-1/comparables/1/adjustment",
            headers={
                LAUNCH_ID_HEADER: bootstrap.launch_id,
                AUTHORIZATION_HEADER: f"Bearer {bootstrap.bearer_token}",
            },
        )
        response = urlopen(request, timeout=3)
        assert response.status == 200
        payload = json.loads(response.read().decode("utf-8"))
        assert payload == {
            "selected_explicitly": True,
            "selected_rate_pct": "0",
        }
    finally:
        runtime.shutdown()
