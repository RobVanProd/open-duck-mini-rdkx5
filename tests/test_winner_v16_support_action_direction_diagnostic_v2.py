from __future__ import annotations

import copy
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v16_support_action_direction_diagnostic_v2.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v16_direction_v2", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def specimen() -> tuple[dict, dict]:
    formal = {
        "configuration_id": "COM_X_NEG",
        "configuration_sha256": "a" * 64,
        "plant": "P30_ALL_JOINT",
        "condition": None,
        "support_pass": False,
        "maximum_jax_onnx_hidden_error": 0.0,
        "final_h_out": [0.0] * 64,
        "constant_normalized_prediction_mse": 0.1,
        "terminal": {"tick": 28, "reason": "roll_pitch", "pitch_rad": -0.36},
        "episode": {"full_duration": False, "maximum_abs_tilt_rad": 0.36},
        "trace_hashes": {
            "observations": "o",
            "actions": "a",
            "predictions": "p",
            "hidden": "h",
        },
    }
    diagnostic = copy.deepcopy(formal)
    diagnostic["source_previous_action_out_exact"] = True
    return diagnostic, formal


def test_baseline_reproduction_tolerates_only_bounded_derived_floats() -> None:
    module = load()
    diagnostic, formal = specimen()
    diagnostic["terminal"]["pitch_rad"] += 4.0e-13
    diagnostic["episode"]["maximum_abs_tilt_rad"] -= 4.0e-13
    assert module.baseline_matches_formal(diagnostic, formal)

    diagnostic["terminal"]["pitch_rad"] += 2.0e-12
    assert not module.baseline_matches_formal(diagnostic, formal)


def test_baseline_reproduction_keeps_traces_and_decisions_exact() -> None:
    module = load()
    diagnostic, formal = specimen()
    diagnostic["trace_hashes"]["actions"] = "changed"
    assert not module.baseline_matches_formal(diagnostic, formal)

    diagnostic, formal = specimen()
    diagnostic["support_pass"] = True
    assert not module.baseline_matches_formal(diagnostic, formal)

    diagnostic, formal = specimen()
    diagnostic["terminal"]["tick"] = 29
    assert not module.baseline_matches_formal(diagnostic, formal)


def test_runner_retains_screen_and_has_no_training_or_hardware_authority() -> None:
    module = load()
    assert module.FAILURE_IDS == (
        "COM_CORNER_01",
        "COM_CORNER_03",
        "COM_X_NEG",
        "DISCOVERY_03",
        "HELDOUT_04",
        "HELDOUT_09",
    )
    assert len(module.INTERVENTIONS) == 7
    source = RUNNER.read_text(encoding="utf-8")
    assert "adam_step" not in source
    assert "--hardware-authorized" not in source
