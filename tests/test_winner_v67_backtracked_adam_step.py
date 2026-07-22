from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v67_backtracked_adam_step.py"
RUNNER = ROOT / "tools/run_winner_v67_backtracked_adam_step.py"


def module():
    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v67_backtracked_adam_step as builder

    return builder


def test_v67_sources_compile_and_transform_once() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    source, digest = module().transformed_source()
    assert len(digest) == 64
    assert source.count("v67_builder.select_first_descent") == 1
    assert "--backtracked-adam-step-authorized" in source
    assert "snapshot_backtracked_adam_update_575.npz" in source
    compile(source, "winner_v67_transformed.py", "exec")


def test_v67_selects_first_largest_fraction_with_descent() -> None:
    builder = module()
    rows = [
        {"fraction": 1.0, "loss": 1.1},
        {"fraction": 0.5, "loss": 1.01},
        {"fraction": 0.25, "loss": 0.99},
        {"fraction": 0.125, "loss": 0.98},
        {"fraction": 0.0625, "loss": 0.97},
    ]
    selected = builder.select_first_descent(rows, 1.0)
    assert selected is rows[2]
    assert selected["fraction"] == 0.25
    assert builder.select_first_descent(
        [{"fraction": fraction, "loss": 1.0} for fraction in builder.FRACTIONS],
        1.0,
    ) is None


def test_v67_builder_freezes_one_step_only(tmp_path: Path) -> None:
    output = tmp_path / "v67.json"
    markdown = tmp_path / "v67.md"
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
    assert value["step"]["source_optimizer_count"] == 574
    assert value["step"]["completed_optimizer_count"] == 575
    assert value["step"]["fractions_largest_first"] == list(module().FRACTIONS)
    assert value["step"]["expected_accepted_fraction"] == 0.25
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["continuation_authorized_now"] is False
    assert value["authority"]["robot_clearance"] is False
    assert markdown.is_file()


def test_v67_runner_is_offline_wrapper_only() -> None:
    source = RUNNER.read_text(encoding="utf-8").lower()
    assert "builder.transformed_source()" in source
    assert "training.adam_step" not in source
    assert "paramiko" not in source
    assert "/dev/tty" not in source
