from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v68_backtracked_adam_continuation.py"
RUNNER = ROOT / "tools/run_winner_v68_backtracked_adam_continuation.py"


def module():
    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v68_backtracked_adam_continuation as builder

    return builder


def test_v68_sources_compile_and_transform_once() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    source, digest = module().transformed_source()
    assert len(digest) == 64
    assert source.count("v68_builder.select_first_descent") == 1
    assert "UPDATES = 80" in source
    assert "SOURCE_COMPLETED_UPDATES = 575" in source
    assert "list(range(576, 656))" in source
    assert "len(metrics) == 80" in source
    assert "snapshot_backtracked_adam_update_" in source
    compile(source, "winner_v68_transformed.py", "exec")


def test_v68_selects_largest_strict_descent() -> None:
    builder = module()
    rows = [
        {"fraction": 1.0, "loss": 1.1},
        {"fraction": 0.5, "loss": 0.99},
        {"fraction": 0.25, "loss": 0.98},
        {"fraction": 0.125, "loss": 0.97},
        {"fraction": 0.0625, "loss": 0.96},
    ]
    assert builder.select_first_descent(rows, 1.0) is rows[1]


def test_v68_builder_freezes_80_updates_and_two_endpoints(tmp_path: Path) -> None:
    output = tmp_path / "v68.json"
    markdown = tmp_path / "v68.md"
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
    assert frozen["source_completed_updates"] == 575
    assert frozen["continuation_optimizer_updates"] == 80
    assert frozen["persistent_checkpoints"] == {"half": 605, "final": 655}
    assert frozen["fractions_largest_first"] == list(module().FRACTIONS)
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["formal_support_gate_authorized"] is False
    assert value["authority"]["robot_clearance"] is False
    assert markdown.is_file()


def test_v68_runner_is_offline_wrapper_only() -> None:
    source = RUNNER.read_text(encoding="utf-8").lower()
    assert "builder.transformed_source()" in source
    assert "training.adam_step" not in source
    assert "paramiko" not in source
    assert "/dev/tty" not in source
