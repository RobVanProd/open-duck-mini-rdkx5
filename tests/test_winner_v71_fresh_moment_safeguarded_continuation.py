from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v71_fresh_moment_safeguarded_continuation.py"
RUNNER = ROOT / "tools/run_winner_v71_fresh_moment_safeguarded_continuation.py"


def module():
    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v71_fresh_moment_safeguarded_continuation as builder

    return builder


def test_v71_sources_compile_and_transform_once() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    source, digest = module().transformed_source()
    assert len(digest) == 64
    assert source.count("v71_builder.select_first_descent") == 1
    assert "UPDATES = 53" in source
    assert "SOURCE_COMPLETED_UPDATES = 602" in source
    assert "list(range(603, 656))" in source
    assert "moment_reset_applied" in source
    assert "accepted_backtracking_fraction" in source
    compile(source, "winner_v71_transformed.py", "exec")


def test_v71_selects_largest_strict_descent() -> None:
    builder = module()
    rows = [
        {"fraction": fraction, "loss": 1.1 if index < 3 else 0.9}
        for index, fraction in enumerate(builder.FRACTIONS)
    ]
    assert builder.select_first_descent(rows, 1.0) is rows[3]


def test_v71_builder_freezes_remaining_updates(tmp_path: Path) -> None:
    output = tmp_path / "v71.json"
    markdown = tmp_path / "v71.md"
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
    frozen = value["frozen_training"]
    assert frozen["source_completed_updates"] == 602
    assert frozen["continuation_optimizer_updates"] == 53
    assert frozen["persistent_checkpoints"] == {"half": 605, "final": 655}
    assert frozen["fractions_largest_first"] == list(module().FRACTIONS)
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["formal_support_gate_authorized"] is False
    assert value["authority"]["robot_clearance"] is False
    assert markdown.is_file()


def test_v71_runner_is_offline_wrapper_only() -> None:
    source = RUNNER.read_text(encoding="utf-8").lower()
    assert "builder.transformed_source()" in source
    assert "training.adam_step" not in source
    assert "paramiko" not in source
    assert "/dev/tty" not in source
