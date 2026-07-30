from __future__ import annotations

from tools.run_t178b_pre_action_handoff_correction import (
    compare_handoff_group,
    extract_pre_action_handoff,
)


def _row(command: float = 0.074) -> dict:
    obs = [0.0] * 115
    obs[0:2] = [1.0, 0.0]
    obs[2] = command
    obs[83:97] = [float(index) / 10.0 for index in range(14)]
    return {
        "tick": 0,
        "command": [command, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "obs_state": obs,
        "actual_position_pre_rad": [float(index) for index in range(14)],
        "policy_calibration_context_sha256": "a" * 64,
        "policy_state_input": {
            "previous_action": [[0.0] * 14],
            "h_in": [[0.0] * 64],
        },
        "applied_target_rad": [command] * 14,
        "qpos": [command],
        "qvel": [command],
    }


def test_extract_uses_pre_action_slot_not_current_outputs() -> None:
    low = extract_pre_action_handoff(_row(0.074))
    high = extract_pre_action_handoff(_row(0.08))
    assert low == high


def test_group_passes_when_only_post_action_outputs_differ() -> None:
    rows = [
        extract_pre_action_handoff(_row(command))
        for command in (0.0, 0.074, 0.077, 0.08)
    ]
    result = compare_handoff_group(rows)
    assert result["all_checks_pass"]
    assert all(result["checks"].values())


def test_group_detects_true_applied_observation_mismatch() -> None:
    rows = [
        extract_pre_action_handoff(_row(command))
        for command in (0.0, 0.074, 0.077, 0.08)
    ]
    rows[-1]["applied_target_observation_rad"][3] += 0.01
    result = compare_handoff_group(rows)
    assert not result["all_checks_pass"]
    assert not result["checks"]["applied_target_observation_rad"]
