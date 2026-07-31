from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v25_directional_support_control_diagnostic_preregistration.json"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_WINNER_V25_DIRECTIONAL_SUPPORT_CONTROL_DIAGNOSTIC"
    )
    assert value["decision"] == (
        "AUTHORIZE_ONE_ZERO_UPDATE_SAME_STATE_DIRECTIONAL_DIAGNOSTIC_ONLY"
    )
    diagnostic = value["diagnostic"]
    assert diagnostic["source_checkpoint"] == {
        "label": "winner_v22_final",
        "update": 100,
    }
    assert diagnostic["candidate_checkpoints"] == [
        {"label": "half", "update": 150},
        {"label": "final", "update": 200},
    ]
    assert len(diagnostic["configuration_ids"]) == 10
    assert diagnostic["base_prefix_ticks"] == 20
    assert diagnostic["fork_horizon_ticks"] == 5
    assert diagnostic["expected_fork_points"] == 800
    assert diagnostic["expected_short_horizon_rollouts"] == 1600
    assert diagnostic["destabilizing_fraction_threshold"] == 0.75
    assert value["execution_now"] == {
        "base_trajectories": 0,
        "fork_points": 0,
        "short_horizon_rollouts": 0,
        "optimizer_updates": 0,
        "locomotion_steps": 0,
        "robot_or_rdk_access": 0,
    }


def test_source_manifest_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    for item in value["sources"].values():
        observed = hashlib.sha256(
            (ROOT / item["path"]).read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        assert item["hash_mode"] == "lf"
        assert observed == item["sha256"]
    canonical = hashlib.sha256(
        json.dumps(value["sources"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert canonical == value["source_manifest_sha256"]


def test_workflow_is_dormant_and_cpu_only() -> None:
    workflow = ROOT / ".github/workflows/winner-v25-directional-support-control-diagnostic.yml"
    source = workflow.read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v25_directional_support_control_diagnostic_preregistration.json" in trigger
    assert "workflow_dispatch" not in trigger
    assert "--read-only-diagnostic-authorized" in source
    assert "--hardware-authorized" not in source
