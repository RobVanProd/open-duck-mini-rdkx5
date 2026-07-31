from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools/build_winner_v91_universal_target_full_gate_preregistration.py"
RUNNER = ROOT / "tools/run_winner_v91_universal_target_full_gate.py"


def test_builder_freezes_exact_target_and_full_population(tmp_path: Path) -> None:
    output = tmp_path / "v91.json"
    markdown = tmp_path / "v91.md"
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
    assert value["frozen_target"]["candidate_index"] == 536
    assert value["frozen_target"]["mirrored_coordinates"] == [0.5, 0.25, 0.25]
    assert value["frozen_target"]["expanded_raw_action"] == [
        0.0,
        0.0,
        -0.5,
        0.25,
        0.25,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.5,
        0.25,
        0.25,
    ]
    assert value["gate"]["core_model_plant_cells"] == 112
    assert value["gate"]["sensor_transport_plant_cells"] == 12
    assert value["gate"]["formal_cells"] == 124
    assert value["gate"]["predictor_or_context_selection"] is False
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["authority"]["robot_clearance"] is False


def test_runner_uses_exact_full_teacher_intervention_and_no_policy_update() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "v48.InterventionSession" in source
    assert 'mode="full_teacher"' in source
    assert "v43.expand_coordinates" in source
    assert "gate.run_cell" in source
    assert "all_124_support_cells_pass" in source
    assert "--offline-cpu-only" in source
    assert "--formal-gate-authorized" in source
    assert '"optimizer_updates": 0' in source
    assert '"snapshot_or_onnx_writes": 0' in source
    assert "adam_step(" not in source
    assert "write_snapshot" not in source
    assert "--hardware-authorized" not in source
    compile(source, str(RUNNER), "exec")
