from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v63_persistent_teacher_conflict_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v63_persistent_teacher_conflict_attribution.py"
V60_RESULT = ROOT / "outputs/analysis/winner_v60_integrated_numeric_guard_training_result.json"
V62_RESULT = ROOT / "outputs/analysis/winner_v62_residual_teacher_causal_result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v63_sources_compile() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")


def test_v63_builder_freezes_exact_causal_and_training_sources(tmp_path: Path) -> None:
    output = tmp_path / "v63.json"
    markdown = tmp_path / "v63.md"
    subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--output",
            str(output),
            "--markdown",
            str(markdown),
        ],
        cwd=ROOT,
        check=True,
    )
    value = json.loads(output.read_text(encoding="utf-8"))
    assert value["status"] == (
        "PREREGISTERED_WINNER_V63_PERSISTENT_TEACHER_CONFLICT_ATTRIBUTION"
    )
    assert value["decision"] == "AUTHORIZE_ONE_ZERO_COMMIT_CPU_ATTRIBUTION_ONLY"
    assert value["frozen_source"]["completed_updates"] == 554
    assert value["frozen_source"]["v60_result_sha256"] == sha256(V60_RESULT)
    assert value["frozen_source"]["v62_result_sha256"] == sha256(V62_RESULT)
    assert value["evidence_selection"]["flat_transport_or_attention_selected"] is False
    assert value["frozen_execution"] == {
        "rollout_episode_slots": 80,
        "scheduled_rollout_ticks": 20000,
        "counterfactual_in_memory_adam_steps": 2,
        "committed_optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "deployable_graph_exports": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["execution_now"] == {
        "rollout_episode_slots": 0,
        "scheduled_rollout_ticks": 0,
        "counterfactual_in_memory_adam_steps": 0,
        "committed_optimizer_updates": 0,
        "formal_support_cells": 0,
        "locomotion_training_steps": 0,
        "deployable_graph_exports": 0,
        "robot_or_rdk_access": 0,
    }
    assert value["authority"]["robot_clearance"] is False
    assert value["authority"]["training_authorized"] is False
    assert len(value["classification_rule"]) == 5
    assert markdown.is_file()


def test_v63_runner_is_read_only_and_precommitted() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "ROLLOUT_UPDATE_INDEX = 554" in source
    assert "counterfactual_in_memory_adam_steps" in source
    assert '"committed_optimizer_updates": 0' in source
    assert "training.adam_step" in source
    assert "PREREGISTER_TEACHER_TRAJECTORY_PERSISTENT_PREFIX_CONTRACT" in source
    assert "INTEGRATED_STEP_BLOCKS_PERSISTENT_TEACHER_DESCENT" in source
    assert "request_user_input" not in source
    assert "ssh" not in source.lower()
    assert "paramiko" not in source.lower()
    assert "/dev/tty" not in source.lower()
    assert "torque_enable" not in source.lower()
