from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v70_fresh_moment_step.py"
RUNNER = ROOT / "tools/run_winner_v70_fresh_moment_step.py"


def module():
    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v70_fresh_moment_step as builder

    return builder


def test_v70_sources_compile_and_transform_once() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    source, digest = module().transformed_source()
    assert len(digest) == 64
    assert source.count("v70_builder.select_first_descent") == 1
    assert "--fresh-moment-step-authorized" in source
    assert "snapshot_fresh_moment_update_602.npz" in source
    compile(source, "winner_v70_transformed.py", "exec")


def test_v70_selects_first_strict_descent() -> None:
    builder = module()
    rows = [
        {"fraction": fraction, "loss": 1.1 if index < 2 else 0.9}
        for index, fraction in enumerate(builder.FRACTIONS)
    ]
    assert builder.select_first_descent(rows, 1.0) is rows[2]


def test_v70_builder_freezes_one_step_only(tmp_path: Path) -> None:
    output = tmp_path / "v70.json"
    markdown = tmp_path / "v70.md"
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
    assert value["step"]["source_optimizer_count"] == 601
    assert value["step"]["completed_optimizer_count"] == 602
    assert value["step"]["fractions_largest_first"] == list(module().FRACTIONS)
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["continuation_authorized_now"] is False
    assert value["authority"]["robot_clearance"] is False
    assert markdown.is_file()


def test_v70_runner_is_offline_wrapper_only() -> None:
    source = RUNNER.read_text(encoding="utf-8").lower()
    assert "builder.transformed_source()" in source
    assert "training.adam_step" not in source
    assert "paramiko" not in source
    assert "/dev/tty" not in source
