from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v65b_preregistration_path_correction.py"
RUNNER = ROOT / "tools/run_winner_v65b_preregistration_path_correction.py"
INVALID = ROOT / "outputs/analysis/winner_v65_isolated_persistent_teacher_invalid_invocation.json"


def test_v65b_sources_compile_and_correct_one_path() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v65b_preregistration_path_correction as builder

    source, digest = builder.corrected_source()
    assert len(digest) == 64
    assert source.count(builder.NEW) == 1
    assert builder.OLD not in source
    compile(source, "winner_v65b_transformed.py", "exec")


def test_v65b_builder_preserves_training_contract(tmp_path: Path) -> None:
    output = tmp_path / "v65b.json"
    markdown = tmp_path / "v65b.md"
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
    correction = value["v65b"]
    assert correction["identity"] == "WINNER_V65B_PREREGISTRATION_PATH_CORRECTION"
    assert correction["replacement_count"] == 1
    assert correction[
        "objective_rollout_gradient_adam_checkpoint_schedule_or_authority_change"
    ] is False
    assert correction["invalid_invocation"]["sha256"] == hashlib.sha256(
        INVALID.read_bytes()
    ).hexdigest()
    assert value["frozen_training"]["persistent_checkpoints"] == {
        "half": 605,
        "final": 655,
    }
    assert value["objective"]["update_gradient"] == (
        "full_action_persistent_teacher_only"
    )
    assert value["execution_now"]["optimizer_updates"] == 0
    assert markdown.is_file()


def test_v65b_runner_is_offline_wrapper_only() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "builder.corrected_source()" in source
    assert "namespace[\"main\"]()" in source
    assert "training.adam_step" not in source
    assert "paramiko" not in source.lower()
    assert "/dev/tty" not in source.lower()
