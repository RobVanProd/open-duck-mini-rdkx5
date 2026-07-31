from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v67b_source_decision_correction.py"
RUNNER = ROOT / "tools/run_winner_v67b_source_decision_correction.py"


def test_v67b_sources_compile_and_correct_one_literal() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v67b_source_decision_correction as builder

    source, digest = builder.corrected_source()
    assert len(digest) == 64
    assert source.count(builder.NEW) == 1
    assert builder.OLD not in source
    assert source.count("v67_builder.select_first_descent") == 1


def test_v67b_builder_preserves_step_contract(tmp_path: Path) -> None:
    output = tmp_path / "v67b.json"
    markdown = tmp_path / "v67b.md"
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
    assert value["v67b"]["replacement_count"] == 1
    assert value["v67b"][
        "step_objective_backtracking_adam_artifact_or_authority_change"
    ] is False
    assert value["step"]["source_optimizer_count"] == 574
    assert value["step"]["completed_optimizer_count"] == 575
    assert value["step"]["expected_accepted_fraction"] == 0.25
    assert value["execution_now"]["optimizer_updates"] == 0
    assert markdown.is_file()


def test_v67b_runner_is_offline_wrapper_only() -> None:
    source = RUNNER.read_text(encoding="utf-8").lower()
    assert "builder.corrected_source()" in source
    assert "training.adam_step" not in source
    assert "paramiko" not in source
    assert "/dev/tty" not in source
