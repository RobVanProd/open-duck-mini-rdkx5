from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v18_imu_ankle_feedback_diagnostic.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v18_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_feedback_screen_is_exact() -> None:
    module = load()
    assert [row["id"] for row in module.INTERVENTIONS] == [
        "BASELINE",
        "CONSTANT_ANKLE_POS",
        "TILT_BACKWARD",
        "TILT_OPPOSITE",
        "RATE_BACKWARD",
        "RATE_OPPOSITE",
        "TILT_RATE_BACKWARD",
    ]
    assert len(module.FAILURE_IDS) == 6


def test_runner_uses_only_deployable_observation_and_has_no_training_authority() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert 'inputs["obs"][0]' in source
    assert "adam_step" not in source
    assert "--hardware-authorized" not in source
