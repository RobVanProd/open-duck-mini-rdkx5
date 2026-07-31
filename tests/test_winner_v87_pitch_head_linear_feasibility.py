from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = (
    ROOT / "tools/build_winner_v87_pitch_head_linear_feasibility_preregistration.py"
)
RUNNER = ROOT / "tools/run_winner_v87_pitch_head_linear_feasibility.py"


def test_builder_freezes_two_endpoint_leave_one_configuration_out_audit(
    tmp_path: Path,
) -> None:
    output = tmp_path / "v87.json"
    markdown = tmp_path / "v87.md"
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
    assert value["frozen_source"]["checkpoint_labels_updates"] == {
        "half": 705,
        "final": 755,
    }
    assert value["frozen_source"]["pitch_indices"] == [2, 3, 4, 11, 12, 13]
    assert value["frozen_source"]["teacher_configuration_count"] == 16
    assert value["frozen_source"]["teacher_episodes_per_checkpoint"] == 32
    assert value["fit"]["solver"] == "numpy.linalg.lstsq"
    assert value["fit"]["rcond"] is None
    assert value["fit"]["cross_validation_fits_per_checkpoint"] == 16
    assert value["fit"]["hyperparameter_search"] is False
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["robot_clearance"] is False


def test_runner_is_read_only_and_uses_existing_affine_tanh_head() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "--offline-cpu-only" in source
    assert "--linear-feasibility-authorized" in source
    assert "np.linalg.lstsq" in source
    assert "np.arctanh" in source
    assert "np.tanh" in source
    assert "training.bounded_action" in source
    assert '"optimizer_updates": 0' in source
    assert '"formal_support_cells": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "adam_step(" not in source
    assert "write_snapshot" not in source
    assert "export" not in source
    assert "--hardware-authorized" not in source
    compile(source, str(RUNNER), "exec")
