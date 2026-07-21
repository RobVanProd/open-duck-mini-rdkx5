from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v16_support_action_direction_diagnostic.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v16_direction_diagnostic", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_screen_is_exact_and_negative_x_only() -> None:
    module = load()
    assert len(module.INTERVENTIONS) == 7
    assert module.INTERVENTIONS[0] == {"id": "BASELINE", "axis": None, "direction": 0}
    assert {row["axis"] for row in module.INTERVENTIONS[1:]} == {
        "hip_pitch_magnitude", "knee", "ankle"
    }
    assert {row["direction"] for row in module.INTERVENTIONS[1:]} == {-1, 1}
    assert module.FAILURE_IDS == (
        "COM_CORNER_01", "COM_CORNER_03", "COM_X_NEG",
        "DISCOVERY_03", "HELDOUT_04", "HELDOUT_09",
    )


def test_runner_is_cpu_only_and_has_no_training_or_hardware_authority() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "--offline-cpu-only" in source
    assert "--direction-diagnostic-authorized" in source
    assert '"optimizer_updates": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert "adam_step" not in source
    assert "--hardware-authorized" not in source
