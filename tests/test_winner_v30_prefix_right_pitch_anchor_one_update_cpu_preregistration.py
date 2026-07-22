from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "outputs/analysis/winner_v30_prefix_right_pitch_anchor_one_update_cpu_contract.json"


def test_preregistration_is_exact_when_present() -> None:
    if not PREREG.exists():
        return
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V30_PREFIX_RIGHT_PITCH_ANCHOR_ONE_UPDATE_CPU_PROOF"
    assert value["decision"] == "AUTHORIZE_EXACT_ONE_PREFIX_RIGHT_PITCH_ANCHOR_OPTIMIZER_UPDATE_ONLY"
    assert value["objective"]["anchor_scale"] == 197.3112030029297
    assert value["objective"]["prefix_ticks"] == list(range(8))
    assert value["objective"]["action_indices"] == [11, 12, 13]
    assert value["objective"]["selected_elements"] == 384
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["execution_future"] == {
        "rollout_episode_slots": 80,
        "optimizer_updates": 1,
        "formal_support_cells": 0,
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


def test_workflow_is_dormant_cpu_only_and_first_attempt() -> None:
    source = (
        ROOT / ".github/workflows/winner-v30-prefix-right-pitch-anchor-one-update-cpu-proof.yml"
    ).read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v30_prefix_right_pitch_anchor_one_update_cpu_contract.json" in trigger
    assert "workflow_dispatch" not in trigger
    assert 'test "${{ github.run_attempt }}" = "1"' in source
    assert "--offline-cpu-only" in source
    assert "--one-update-prefix-right-pitch-anchor-proof-authorized" in source
    assert "--hardware-authorized" not in source
