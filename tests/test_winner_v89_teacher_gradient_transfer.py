from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v89_teacher_gradient_transfer_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v89_teacher_gradient_transfer.py"


def test_builder_freezes_strict_leave_one_configuration_gradient_signs(
    tmp_path: Path,
) -> None:
    output = tmp_path / "v89.json"
    markdown = tmp_path / "v89.md"
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
    assert value["frozen_source"]["groups"] == [
        "recurrent_core",
        "action_head",
        "combined_policy",
    ]
    assert value["diagnostic"]["folds_per_checkpoint"] == 12
    assert value["diagnostic"]["teacher_gradient_evaluations"] == 48
    assert value["diagnostic"]["optimizer_step_or_parameter_commit"] is False
    assert "all 12" in value["classification_rule"]["group_coherent_for_endpoint"]
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["robot_clearance"] is False


def test_runner_is_zero_update_gradient_direction_diagnostic() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "jax.value_and_grad" in source
    assert "np.dot" in source
    assert '"recurrent_core"' in source
    assert '"action_head"' in source
    assert '"combined_policy"' in source
    assert "--offline-cpu-only" in source
    assert "--gradient-transfer-authorized" in source
    assert '"optimizer_updates": 0' in source
    assert '"snapshot_or_onnx_writes": 0' in source
    assert "adam_step(" not in source
    assert "write_snapshot" not in source
    assert "--hardware-authorized" not in source
    compile(source, str(RUNNER), "exec")
