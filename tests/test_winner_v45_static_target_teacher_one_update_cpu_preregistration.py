from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "outputs/analysis/winner_v45_static_target_teacher_one_update_cpu_contract.json"


def test_contract_is_exact_when_present() -> None:
    if not CONTRACT.exists():
        return
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V45_STATIC_TARGET_TEACHER_ONE_UPDATE_CPU_PROOF"
    assert value["decision"] == "AUTHORIZE_EXACT_ONE_STATIC_TARGET_TEACHER_OPTIMIZER_UPDATE_ONLY"
    assert value["objective"]["source_checkpoint"] == {"label": "winner_v32_half", "update": 251}
    assert value["objective"]["result_optimizer_count"] == 252
    assert value["objective"]["teacher_scale"] == 58.436370849609375
    assert value["objective"]["teacher_action_indices"] == [2, 3, 4, 11, 12, 13]
    assert value["execution_future"] == {
        "rollout_episode_slots": 80,
        "scheduled_rollout_ticks": 20000,
        "optimizer_updates": 1,
        "formal_support_cells": 0,
        "continuation_training_updates": 0,
        "deployable_graph_exports": 1,
        "robot_or_rdk_access": 0,
    }


def test_source_manifest_is_exact_when_present() -> None:
    if not CONTRACT.exists():
        return
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))
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
    source = (ROOT / ".github/workflows/winner-v45-static-target-teacher-one-update-cpu.yml").read_text(encoding="utf-8")
    trigger = source.split("permissions:", 1)[0]
    assert "winner_v45_static_target_teacher_one_update_cpu_contract.json" in trigger
    assert "workflow_dispatch" not in trigger
    assert 'test "${{ github.run_attempt }}" = "1"' in source
    assert "--offline-cpu-only" in source
    assert "--one-update-static-target-teacher-proof-authorized" in source
    assert "--hardware-authorized" not in source

