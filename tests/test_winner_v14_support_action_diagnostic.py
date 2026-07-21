from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
PRIMITIVES = ROOT / "patches/winner_v14_support_action_diagnostic.py"
RUNNER = ROOT / "tools/run_winner_v14_support_action_diagnostic.py"
PREREG = (
    ROOT / "outputs/analysis/winner_v14_support_action_diagnostic_preregistration.json"
)


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_corrected_normalized_scoring_keeps_constant_contacts_finite() -> None:
    module = load(PRIMITIVES, "winner_v14_primitives")
    prediction = np.zeros((50,), dtype=np.float32)
    target = np.zeros((50,), dtype=np.float32)
    mean = np.zeros((50,), dtype=np.float32)
    std = np.ones((50,), dtype=np.float32)
    target[-2:] = 1.0
    mean[-2:] = 1.0
    std[-2:] = np.float32(1.0e-6)
    learned = module.normalized_prediction_squared_error(
        prediction, target, mean, std
    )
    baseline = module.constant_prediction_squared_error(target, mean, std)
    assert np.array_equal(learned, np.zeros((50,), dtype=np.float32))
    assert np.array_equal(baseline, np.zeros((50,), dtype=np.float32))


def test_scale_transform_is_identity_at_one_and_zero_at_zero_from_reset() -> None:
    module = load(PRIMITIVES, "winner_v14_action")
    rng = np.random.default_rng(120120)
    previous = np.zeros((14,), dtype=np.float32)
    delta = np.full((14,), np.float32(0.12), dtype=np.float32)
    for _ in range(250):
        source = np.clip(
            previous + rng.uniform(-0.12, 0.12, 14).astype(np.float32), -1.0, 1.0
        ).astype(np.float32)
        identity = module.scale_and_rebound_action(source, previous, delta, 1.0)
        assert np.array_equal(identity, source)
        previous = identity
    assert np.array_equal(
        module.scale_and_rebound_action(
            np.ones((14,), dtype=np.float32),
            np.zeros((14,), dtype=np.float32),
            delta,
            0.0,
        ),
        np.zeros((14,), dtype=np.float32),
    )


def test_transform_reapplies_absolute_and_rate_bounds() -> None:
    module = load(PRIMITIVES, "winner_v14_bounds")
    source = np.linspace(-1.0, 1.0, 14, dtype=np.float32)
    previous = np.linspace(0.8, -0.8, 14, dtype=np.float32)
    delta = np.linspace(0.03, 0.16, 14, dtype=np.float32)
    result = module.scale_and_rebound_action(source, previous, delta, 0.5)
    assert np.all(result >= np.maximum(previous - delta, -1.0))
    assert np.all(result <= np.minimum(previous + delta, 1.0))
    with pytest.raises(ValueError):
        module.scale_and_rebound_action(source, previous, delta, 1.01)


def test_preregistration_freezes_full_population_and_no_training() -> None:
    value = json.loads(PREREG.read_text(encoding="utf-8"))
    assert value["status"] == "PREREGISTERED_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC_V2"
    assert value["frozen_screen"]["scales"] == [0.0, 0.25, 0.5, 0.75, 1.0]
    assert value["frozen_screen"]["main_cells"] == 1240
    assert value["frozen_screen"]["repeat_cells"] == 320
    assert value["selection_rule"]["winner"] == "largest complete-pass scale"
    assert value["execution_now"]["optimizer_updates"] == 0
    assert value["preexecution_correction"] == {
        "failed_run_id": 29833400247,
        "failed_run_main_cells": 0,
        "failed_run_repeat_cells": 0,
        "only_change": "formal result comparison uses LF-normalized SHA-256",
    }
    assert value["authority"]["robot_clearance"] is False


def test_runner_is_cpu_only_diagnostic_and_uses_normalized_stage1() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "winner_v13_normalized_calibrator_training" in source
    assert "normalized_prediction_squared_error" in source
    assert "--diagnostic-authorized" in source
    assert "--hardware-authorized" not in source
    assert "adam_step" not in source
    assert "stage2_ppo_loss" not in source
