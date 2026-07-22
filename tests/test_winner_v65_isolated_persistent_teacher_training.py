from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v65_isolated_persistent_teacher_training.py"
RUNNER = ROOT / "tools/run_winner_v65_isolated_persistent_teacher_training.py"


def test_v65_sources_compile_and_transform() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v65_isolated_persistent_teacher_training as builder

    source, receipts = builder.transformed_source()
    compile(source, "winner_v65_transformed.py", "exec")
    assert receipts
    assert "SOURCE_COMPLETED_UPDATES = 555" in source
    assert "HALF_COMPLETED_UPDATES = 605" in source
    assert "FINAL_COMPLETED_UPDATES = 655" in source
    assert "full_action_persistent_teacher_only" in source
    assert "same-batch teacher loss did not decrease" in source
    assert "full_horizon_gradients =" not in source
    assert "snapshot_isolated_persistent_teacher_update_" in source
    assert 'f"winner_v65_{label}.onnx"' in source


def test_v65_builder_freezes_teacher_only_horizon(tmp_path: Path) -> None:
    output = tmp_path / "v65.json"
    markdown = tmp_path / "v65.md"
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
        "PREREGISTERED_WINNER_V65_ISOLATED_PERSISTENT_TEACHER_TRAINING"
    )
    assert value["decision"] == (
        "AUTHORIZE_ONE_100_UPDATE_ISOLATED_PERSISTENT_TEACHER_ARM_ONLY"
    )
    assert value["source_checkpoint"]["optimizer_count"] == 555
    assert value["frozen_training"]["persistent_checkpoints"] == {
        "half": 605,
        "final": 655,
    }
    assert value["objective"]["update_gradient"] == (
        "full_action_persistent_teacher_only"
    )
    assert value["objective"]["monitor_only_excluded_from_update"] == [
        "PPO",
        "normalized predictor",
        "prefix right-pitch anchor",
        "first-tick teacher",
    ]
    assert value["objective"]["attention_or_flat_transport_added"] is False
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["training_authorized"] is True
    assert value["authority"]["formal_support_gate_authorized"] is False
    assert markdown.is_file()


def test_v65_runner_is_offline_wrapper_only() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "builder.transformed_source()" in source
    assert "namespace[\"main\"]()" in source
    assert "training.adam_step" not in source
    assert "paramiko" not in source.lower()
    assert "/dev/tty" not in source.lower()
