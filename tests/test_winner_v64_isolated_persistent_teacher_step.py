from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v64_isolated_persistent_teacher_step.py"
RUNNER = ROOT / "tools/run_winner_v64_isolated_persistent_teacher_step.py"


def test_v64_sources_compile_and_transform() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v64_isolated_persistent_teacher_step as builder

    source, digest = builder.transformed_source()
    assert len(digest) == 64
    assert source.count("V64_ARTIFACT") == 2
    assert source.count("snapshot = v22v2.load_snapshot(checkpoint_path)") == 1
    assert "snapshot = v61.load_snapshot_for_reviewed_gate(checkpoint_path)" not in source


def test_v64_builder_freezes_one_update_only(tmp_path: Path) -> None:
    output = tmp_path / "v64.json"
    markdown = tmp_path / "v64.md"
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
    v64 = value["v64"]
    assert v64["identity"] == "WINNER_V64_ISOLATED_PERSISTENT_TEACHER_STEP"
    assert v64["source"]["optimizer_count"] == 554
    assert v64["objective"]["result_optimizer_count"] == 555
    assert v64["objective"]["integrated_ppo_predictor_anchor_first_tick_gradients"] is False
    assert v64["objective"]["inherited_adam_state"] is True
    assert v64["objective"]["attention_or_flat_transport_added"] is False
    assert v64["execution_future"] == {
        "rollout_episode_slots": 80,
        "scheduled_rollout_ticks": 20000,
        "optimizer_updates": 1,
        "continuation_updates": 0,
        "formal_support_cells": 0,
        "candidate_graph_exports": 1,
        "robot_or_rdk_access": 0,
    }
    assert v64["authority"]["robot_clearance"] is False
    assert v64["authority"]["one_optimizer_update_authorized"] is True
    assert v64["authority"]["continuation_training_authorized"] is False
    assert markdown.is_file()


def test_v64_runner_requires_explicit_offline_authority() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "--offline-cpu-only" in source
    assert "--one-update-authorized" in source
    assert "refusing to overwrite Winner-v64 evidence" in source
    assert '"optimizer_updates": 1' in source
    assert '"formal_support_cells": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "paramiko" not in source.lower()
    assert "/dev/tty" not in source.lower()
