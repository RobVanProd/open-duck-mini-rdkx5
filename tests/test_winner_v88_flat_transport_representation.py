from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = (
    ROOT / "tools/build_winner_v88_flat_transport_representation_preregistration.py"
)
RUNNER = ROOT / "tools/run_winner_v88_flat_transport_representation.py"


def test_builder_freezes_equation_component_without_coefficient_search(
    tmp_path: Path,
) -> None:
    output = tmp_path / "v88.json"
    markdown = tmp_path / "v88.md"
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
    assert value["equation_boundary"]["c_n_final_row"] == "(1/n, ..., 1/n)"
    assert value["equation_boundary"]["rho_or_q_selected_or_searched"] is False
    assert value["equation_boundary"]["policy_architecture_changed"] is False
    assert value["fit"]["families"] == [
        "current_observation",
        "flat_transport_basis",
        "hidden_plus_flat_transport",
    ]
    assert value["fit"]["total_least_squares_fits"] == 78
    assert value["fit"]["hyperparameter_or_rho_q_search"] is False
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["robot_clearance"] is False


def test_runner_is_read_only_causal_prefix_mean_probe() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "def causal_prefix_mean" in source
    assert "np.cumsum" in source
    assert "flat_transport_basis" in source
    assert "hidden_plus_flat_transport" in source
    assert "--offline-cpu-only" in source
    assert "--representation-diagnostic-authorized" in source
    assert '"optimizer_updates": 0' in source
    assert '"formal_support_cells": 0' in source
    assert '"snapshot_or_onnx_writes": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "adam_step(" not in source
    assert "write_snapshot" not in source
    assert "--hardware-authorized" not in source
    compile(source, str(RUNNER), "exec")
