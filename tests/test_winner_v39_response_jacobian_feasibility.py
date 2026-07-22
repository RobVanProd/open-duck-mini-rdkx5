from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v39_response_jacobian_feasibility.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v39_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_response_jacobian_screen_scope_is_exact() -> None:
    module = load()
    assert module.CONFIGURATION_IDS == ("COM_X_NEG",)
    assert module.PITCH_INDICES == (2, 3, 4, 11, 12, 13)
    assert module.MIRRORED_DIMENSIONS == 3
    assert module.TICKS == 250
    assert module.RESPONSE_HORIZON_TICKS == 8


def test_mirrored_steps_use_minimum_paired_graph_delta() -> None:
    module = load()

    class Networks:
        INTERNAL_ACTION_DELTA = np.asarray(
            [0.5, 0.5, 0.11, 0.09, 0.13, 0.5, 0.5,
             0.5, 0.5, 0.5, 0.5, 0.10, 0.08, 0.12],
            dtype=np.float32,
        )

    class Smoke:
        networks = Networks()

    np.testing.assert_array_equal(
        module.mirrored_steps(Smoke()),
        np.asarray([0.10, 0.08, 0.12], dtype=np.float32),
    )


def test_mirrored_target_expansion_is_exact() -> None:
    module = load()
    action = module.expand_mirrored_target(
        np.asarray([0.25, -0.50, 0.75], dtype=np.float32)
    )
    expected = np.zeros(14, dtype=np.float32)
    expected[[2, 3, 4, 11, 12, 13]] = [-0.25, -0.50, 0.75, 0.25, -0.50, 0.75]
    np.testing.assert_array_equal(action, expected)


def test_runner_freezes_local_solver_and_has_no_search_training_or_hardware() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "np.linalg.lstsq(" in source
    assert "rcond=None" in source
    assert "unclipped_correction, -steps.astype" in source
    assert '"response_dimensions": ["base_pitch_rad", "body_pitch_rate_rad_s"]' in source
    assert '"response_horizon_ticks": RESPONSE_HORIZON_TICKS' in source
    assert "population" not in source.lower()
    assert "v38.cem_search" not in source
    assert "iteration_receipts" not in source
    assert "np.random" not in source
    assert "training.adam_step" not in source
    assert "--hardware-authorized" not in source
    assert '"optimizer_updates": 0' in source
    assert '"locomotion_training_steps": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert '"runtime_oracle_or_action_wrapper_authorized": False' in source
    assert "closest" not in source.lower()
