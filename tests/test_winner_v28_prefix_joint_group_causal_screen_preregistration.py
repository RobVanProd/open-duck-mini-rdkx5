from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v28_prefix_joint_group_causal_screen_preregistration.json"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V28_PREFIX_JOINT_GROUP_CAUSAL_SCREEN"
    assert value["decision"] == "AUTHORIZE_ONE_ZERO_UPDATE_PREFIX_JOINT_GROUP_SCREEN_ONLY"
    diagnostic = value["diagnostic"]
    assert diagnostic["repair_ticks"] == 8
    assert diagnostic["minimum_recovery_gain"] == 0.25
    assert diagnostic["control_replay_pose_atol_rad"] == 1.0e-12
    assert diagnostic["expected_prefix_arms"] == 240
    assert diagnostic["expected_source_recovery_rollouts"] == 480
    assert sorted(index for group in diagnostic["arms"].values() for index in group) == list(range(14))


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
    source = (ROOT / ".github/workflows/winner-v28-prefix-joint-group-causal-screen.yml").read_text()
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v28_prefix_joint_group_causal_screen_preregistration.json" in trigger
    assert "workflow_dispatch" not in trigger
    assert "--read-only-diagnostic-authorized" in source
    assert "--hardware-authorized" not in source
