from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "audit_t15_x0_deadband_structural.py"
SPEC = importlib.util.spec_from_file_location("t15_deadband", MODULE_PATH)
assert SPEC and SPEC.loader
T15 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(T15)


def test_behavior_signature_ignores_policy_identity() -> None:
    behavior = {
        "samples": 46,
        "termination_reason": "fall_or_nan",
        "mean_local_vx_m_s": -0.38,
        "minimum_base_height_m": 0.055,
        "body_pitch_p95_rad": 0.005,
        "pitch_tracking_p95_rad": 0.023,
        "left_contact_transitions": 3,
        "right_contact_transitions": 2,
        "action_saturation_pct": 0.0,
        "p95_rate_excess_rad_s": 0.0,
        "instant_rate_excess_rad_s": 0.0,
        "policy_id": "must_not_enter_signature",
    }
    signature = T15.behavior_signature(behavior)
    assert "policy_id" not in signature
    assert signature["samples"] == 46


def test_zero_action_trace_requires_all_14_channels(tmp_path: Path) -> None:
    valid = tmp_path / "valid.jsonl"
    valid.write_text(
        '{"action":[0,0,0,0,0,0,0,0,0,0,0,0,0,0]}\n',
        encoding="utf-8",
    )
    exact, rows, _ = T15.trace_actions_are_zero(valid)
    assert exact
    assert rows == 1

    invalid = tmp_path / "invalid.jsonl"
    invalid.write_text(
        '{"action":[0,0,0,0,0,0,0,0,0,0,0,0,0,0.001]}\n',
        encoding="utf-8",
    )
    exact, rows, _ = T15.trace_actions_are_zero(invalid)
    assert not exact
    assert rows == 1
