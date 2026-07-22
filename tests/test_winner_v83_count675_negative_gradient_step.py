from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v83_count675_negative_gradient_step_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v83_count675_negative_gradient_step.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("winner_v83_builder_test", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_builder_freezes_one_step_only(tmp_path: Path) -> None:
    output = tmp_path / "v83.json"
    markdown = tmp_path / "v83.md"
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
    assert value["source"]["optimizer_count"] == 674
    assert value["source"]["target_optimizer_count"] == 675
    assert value["step"]["expected_first_descent_fraction_from_read_only_attribution"] == 0.5
    assert value["step"]["optimizer_m_and_v_transition"] == (
        "all elements bit-exact preserved"
    )
    assert value["step"]["snapshot_count"] == 1
    assert value["step"]["stateful_onnx_count"] == 1
    assert value["authority"]["continuation_authorized_now"] is False
    assert value["authority"]["robot_clearance"] is False


def test_runner_is_localized_offline_one_step() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "--offline-cpu-only" in source
    assert "--negative-gradient-step-authorized" in source
    assert "v80.project_pitch_head_gradient" in source
    assert "v63.tree_bit_exact(optimizer[\"m\"], optimizer_after[\"m\"])" in source
    assert '"optimizer_updates": 1' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "--hardware-authorized" not in source
    compile(source, str(RUNNER), "exec")
