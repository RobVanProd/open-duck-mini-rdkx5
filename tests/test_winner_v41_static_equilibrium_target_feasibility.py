from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v41_static_equilibrium_target_feasibility.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v41_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_static_equilibrium_screen_scope_is_exact() -> None:
    module = load()
    assert module.CONFIGURATION_IDS == ("COM_X_NEG",)
    assert module.PITCH_INDICES == (2, 3, 4, 11, 12, 13)
    assert module.GRID_VALUES == (-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0)
    assert module.GRID_DIMENSIONS == 3
    assert module.EXPECTED_CANDIDATES == 729
    assert module.TICKS == 250


def test_grid_is_complete_unique_and_centered() -> None:
    module = load()
    candidates = module.candidate_coordinates()
    assert len(candidates) == 729
    assert len({tuple(row.tolist()) for row in candidates}) == 729
    np.testing.assert_array_equal(candidates[364], np.zeros(3, dtype=np.float32))
    assert tuple(candidates[0]) == (-1.0, -1.0, -1.0)
    assert tuple(candidates[-1]) == (1.0, 1.0, 1.0)


def test_candidate_key_is_all_or_nothing_and_deterministic() -> None:
    module = load()

    def plant(support: bool, ticks: int) -> dict:
        return {
            "support_pass": support,
            "episode": {
                "valid_ticks": ticks,
                "minimum_base_z_m": 0.14,
                "maximum_abs_tilt_rad": 0.2,
                "maximum_final_window_gyro_xy_norm_rad_s": 0.03,
            },
        }

    passing = {
        "candidate_index": 2,
        "coordinates": [0.0, 0.0, 0.0],
        "plant_results": [plant(True, 250), plant(True, 250)],
    }
    partial = {
        "candidate_index": 1,
        "coordinates": [0.0, 0.0, 0.0],
        "plant_results": [plant(True, 250), plant(False, 249)],
    }
    assert module.candidate_key(passing) > module.candidate_key(partial)


def test_runner_is_constant_target_not_receding_search_training_or_hardware() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "candidate_coordinates()" in source
    assert "one time-invariant raw action target for all 250 ticks" in source
    assert "v38.cem_search" not in source
    assert "np.random" not in source
    assert "lstsq" not in source
    assert "training.adam_step" not in source
    assert "--hardware-authorized" not in source
    assert '"optimizer_updates": 0' in source
    assert '"locomotion_training_steps": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert '"runtime_static_target_or_action_wrapper_authorized": False' in source
    assert "closest" not in source.lower()
