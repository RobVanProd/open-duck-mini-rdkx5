from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v66_failed_step_attribution.py"
RUNNER = ROOT / "tools/run_winner_v66_failed_step_attribution.py"


def module():
    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v66_failed_step_attribution as builder

    return builder


def test_v66_sources_compile_and_transform_once() -> None:
    for path in (BUILDER, RUNNER):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    source, digest = module().transformed_source()
    assert len(digest) == 64
    assert source.count("v66_builder.classify_failed_step") == 1
    assert "UPDATES = 1" in source
    assert "SOURCE_COMPLETED_UPDATES = 574" in source
    assert "--failed-step-attribution-authorized" in source
    compile(source, "winner_v66_transformed.py", "exec")


def test_v66_classification_rules() -> None:
    builder = module()
    ones = [1.0] * len(builder.FRACTIONS)
    assert builder.classify_failed_step(
        loss_before=1.0,
        inherited_full_loss=1.1,
        inherited_gradient_dot_delta=0.2,
        inherited_fraction_losses=ones,
        negative_gradient_fraction_losses=[0.99, *ones[1:]],
    )[0] == "INHERITED_ADAM_MOMENT_DIRECTION_OPPOSES_TEACHER"
    assert builder.classify_failed_step(
        loss_before=1.0,
        inherited_full_loss=1.1,
        inherited_gradient_dot_delta=-0.2,
        inherited_fraction_losses=[0.99, *ones[1:]],
        negative_gradient_fraction_losses=ones,
    )[0] == "INHERITED_ADAM_FULL_STEP_OVERSHOOT"
    assert builder.classify_failed_step(
        loss_before=1.0,
        inherited_full_loss=0.9,
        inherited_gradient_dot_delta=-0.2,
        inherited_fraction_losses=ones,
        negative_gradient_fraction_losses=ones,
    )[0] == "FAILED_STEP_DID_NOT_REPRODUCE"


def test_v66_builder_freezes_zero_update_contract(tmp_path: Path) -> None:
    output = tmp_path / "v66.json"
    markdown = tmp_path / "v66.md"
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
    assert value["diagnostic"]["source_optimizer_count"] == 574
    assert value["diagnostic"]["attempted_optimizer_count"] == 575
    assert value["diagnostic"]["fractions"] == list(module().FRACTIONS)
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["robot_clearance"] is False
    assert markdown.is_file()


def test_v66_runner_is_offline_wrapper_only() -> None:
    source = RUNNER.read_text(encoding="utf-8").lower()
    assert "builder.transformed_source()" in source
    assert "adam_step" not in source
    assert "paramiko" not in source
    assert "/dev/tty" not in source
