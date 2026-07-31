from pathlib import Path
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import run_t20_support_trainthrough_one_update as t20  # noqa: E402


def test_t20_training_command_is_exactly_scoped() -> None:
    command = t20.training_command(
        python=Path("python"),
        output=Path("output"),
        reference=Path("reference.npz"),
        restore=Path("checkpoint"),
    )
    assert command[0] == "python"
    assert command[1] == "playground/open_duck_mini_v2/runner.py"
    assert "--winner_t19_support_trainthrough" in command
    assert "--winner_v119_train_transition_match" in command
    assert "--winner_v3_variable_configuration" in command
    assert command[command.index("--num_timesteps") + 1] == "1024"
    assert (
        command[
            command.index("--ground_up_action_velocity_limits_rad_s") + 1
        ]
        == t20.VELOCITY_LIMITS
    )
    assert command[command.index("--policy_architecture") + 1] == (
        "reference_residual_recurrent_adapter"
    )
    assert "response_conditioned_reference_residual" not in command


def test_t20_abi_and_rate_contracts_are_frozen() -> None:
    assert t20.EXPECTED_RAW_INPUTS == {
        "obs": [1, 115],
        "previous_action": [1, 14],
        "h_in": [1, 64],
    }
    assert t20.EXPECTED_CONTEXT_INPUTS == {
        **t20.EXPECTED_RAW_INPUTS,
        "calibration_context": [1, 64],
    }
    assert t20.EXPECTED_OUTPUTS == {
        "continuous_actions": [1, 14],
        "previous_action_out": [1, 14],
        "h_out": [1, 64],
    }
    rates = np.asarray(
        [float(value) for value in t20.VELOCITY_LIMITS.split(",")],
        dtype=np.float32,
    )
    np.testing.assert_array_equal(
        rates,
        np.asarray(
            [
                1.0,
                0.75,
                1.5,
                1.5,
                1.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.75,
                1.25,
                1.0,
                1.25,
            ],
            dtype=np.float32,
        ),
    )
