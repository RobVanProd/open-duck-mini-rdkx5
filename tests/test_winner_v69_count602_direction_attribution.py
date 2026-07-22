from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v69_count602_direction_attribution.py"
RUNNER = ROOT / "tools/run_winner_v69_count602_direction_attribution.py"


def module():
    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v69_count602_direction_attribution as builder

    return builder


def test_v69_sources_compile_and_transform_once() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    source, digest = module().transformed_source()
    assert len(digest) == 64
    assert source.count("v69_builder.classify_count602") == 1
    assert "SOURCE_COMPLETED_UPDATES = 601" in source
    assert "--count602-attribution-authorized" in source
    compile(source, "winner_v69_transformed.py", "exec")


def test_v69_classification_rules() -> None:
    builder = module()
    before = 1.0
    original_fail_extended_pass = [1.1] * 5 + [0.99] + [1.0] * 5
    assert builder.classify_count602(
        loss_before=before,
        adam_gradient_dot_delta=-0.1,
        adam_losses=original_fail_extended_pass,
        negative_gradient_losses=[0.9] * 5,
    )[0] == "ADAM_DESCENT_EXISTS_BELOW_FROZEN_GRID"
    assert builder.classify_count602(
        loss_before=before,
        adam_gradient_dot_delta=0.1,
        adam_losses=[1.1] * 11,
        negative_gradient_losses=[0.9] * 5,
    )[0] == "INHERITED_ADAM_MOMENT_DIRECTION_OPPOSES_TEACHER"


def test_v69_builder_freezes_zero_update_contract(tmp_path: Path) -> None:
    output = tmp_path / "v69.json"
    markdown = tmp_path / "v69.md"
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
    assert value["diagnostic"]["source_optimizer_count"] == 601
    assert value["diagnostic"]["attempted_optimizer_count"] == 602
    assert value["diagnostic"]["adam_fractions"] == list(module().ADAM_FRACTIONS)
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["robot_clearance"] is False
    assert markdown.is_file()


def test_v69_runner_is_offline_wrapper_only() -> None:
    source = RUNNER.read_text(encoding="utf-8").lower()
    assert "builder.transformed_source()" in source
    assert "training.adam_step" not in source
    assert "paramiko" not in source
    assert "/dev/tty" not in source
