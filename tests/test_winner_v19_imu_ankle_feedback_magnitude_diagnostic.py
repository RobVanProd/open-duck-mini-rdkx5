from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v19_imu_ankle_feedback_magnitude_diagnostic.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v19_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_magnitude_screen_is_exact_and_one_variable() -> None:
    module = load()
    assert [row["id"] for row in module.INTERVENTIONS] == [
        "BASELINE",
        "CONSTANT_003",
        "CONSTANT_006",
        "CONSTANT_009",
        "TILT_RATE_003",
        "TILT_RATE_006",
        "TILT_RATE_009",
    ]
    assert sorted({row["maximum_target_offset_rad"] for row in module.INTERVENTIONS[1:]}) == [
        0.03,
        0.06,
        0.09,
    ]


def test_runner_has_no_training_or_hardware_authority() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step" not in source
    assert "--hardware-authorized" not in source
