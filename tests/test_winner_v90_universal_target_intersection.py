from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BUILDER = (
    ROOT / "tools/build_winner_v90_universal_target_intersection_preregistration.py"
)
RUNNER = ROOT / "tools/run_winner_v90_universal_target_intersection.py"


def test_builder_freezes_saved_result_only_intersection_and_selection(
    tmp_path: Path,
) -> None:
    output = tmp_path / "v90.json"
    markdown = tmp_path / "v90.md"
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
    frozen = value["frozen_source"]
    assert frozen["configurations"] == 15
    assert frozen["candidates_per_configuration"] == 729
    assert frozen["actuator_plants"] == 2
    assert frozen["candidate_plant_cells_already_captured"] == 21870
    assert value["selection_key_largest_first"][-1] == "negative candidate index"
    assert value["execution_now"]["new_simulation_cells"] == 0
    assert value["authority"]["robot_clearance"] is False


def test_runner_only_intersects_saved_receipts() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "set.intersection" in source
    assert "candidate_coordinates" in source
    assert "aggregate_candidate" in source
    assert "--saved-result-audit-authorized" in source
    assert '"new_simulation_cells": 0' in source
    assert '"optimizer_updates": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "mujoco" not in source
    assert "run_cell(" not in source
    assert "adam_step(" not in source
    assert "--hardware-authorized" not in source
    compile(source, str(RUNNER), "exec")
