from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_winner_v34_prefix_right_pitch_hard_intervention.py"


def load():
    spec = importlib.util.spec_from_file_location("winner_v34_runner", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_intervention_scope_and_counts_are_exact() -> None:
    module = load()
    assert module.RIGHT_PITCH_INDICES == (11, 12, 13)
    assert module.REPLACEMENT_TICKS == 8
    assert module.TICKS == 250
    assert module.CONTROL_SCALAR_FLOAT_ATOL == 1.0e-12
    assert len(module.CONFIGURATION_IDS) == 15
    assert module.CHECKPOINTS == (("half", 251), ("final", 301))
    assert module.ARMS == ("CONTROL", "RIGHT_PITCH_REPLACED")


def test_runner_has_no_optimizer_hardware_or_action_wrapper_path() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert "training.adam_step" not in source
    assert "--hardware-authorized" not in source
    assert '"optimizer_updates": 0' in source
    assert '"robot_or_rdk_access": 0' in source
    assert '"runtime_action_wrapper_authorized": False' in source
    assert "tick < REPLACEMENT_TICKS" in source


def test_control_signature_excludes_only_noncausal_diagnostics() -> None:
    module = load()
    cell = {
        "terminal": None,
        "episode": {"valid_ticks": 250},
        "support_pass": True,
        "previous_action_chain_exact": True,
        "final_h_out": [0.0] * 64,
        "trace_hashes": {
            "observations": "a",
            "actions": "b",
            "hidden": "c",
            "predictions": "d",
            "candidate_actions": "e",
        },
    }
    signature = module.control_signature(cell)
    assert set(signature["trace_hashes"]) == {"actions", "hidden"}
    assert "predictions" not in signature["trace_hashes"]
    assert "observations" not in signature["trace_hashes"]


def test_control_comparison_freezes_trace_but_tolerates_only_roundoff() -> None:
    module = load()
    base = {
        "terminal": {"tick": 26, "pitch_rad": -0.36, "checks": {"roll_pitch": False}},
        "episode": {"valid_ticks": 26, "maximum_abs_tilt_rad": 0.36},
        "support_pass": False,
        "previous_action_chain_exact": True,
        "final_h_out": [0.0] * 64,
        "trace_hashes": {
            "observations": "a",
            "actions": "b",
            "hidden": "c",
            "predictions": "d",
            "candidate_actions": "e",
        },
    }
    close = json.loads(json.dumps(base))
    close["terminal"]["pitch_rad"] += 5.0e-13
    same, delta = module.compare_control_replay(base, close)
    assert same and 0.0 < delta <= module.CONTROL_SCALAR_FLOAT_ATOL
    changed = json.loads(json.dumps(base))
    changed["trace_hashes"]["actions"] = "different"
    assert module.compare_control_replay(base, changed)[0] is False
