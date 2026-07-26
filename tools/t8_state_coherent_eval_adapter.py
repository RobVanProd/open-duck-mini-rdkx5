#!/usr/bin/env python3
"""Load a narrowly patched T8 evaluator without changing the frozen source."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import types
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "closed_loop_sim_eval.py"
EXPECTED_SOURCE_SHA256 = (
    "352ea320936c83801fa47f76e35faea36a68f1d7f45c11b1869292e1955f4114"
)
MODULE_NAME = "closed_loop_sim_eval_t8_state_coherent"


PATCHES = (
    (
        """    response_calibration_ticks: int = 0
    response_home_return_ticks: int = 0
    policy_applied_target_observation: bool = False
""",
        """    response_calibration_ticks: int = 0
    response_home_return_ticks: int = 0
    response_preserve_handoff_state: bool = False
    policy_applied_target_observation: bool = False
""",
    ),
    (
        """    response_prefix_enabled = config.response_calibrator_path is not None
    if response_prefix_enabled:
        if (
            config.policy_context_input_name is None
            or config.response_calibrator_sha256 is None
            or config.response_calibration_ticks != 250
            or config.response_home_return_ticks != 250
            or config.expected_observation_dim != 115
        ):
            return {
                "status": "HOLD_POLICY_IO_CONTRACT",
                "error": (
                    "response-conditioned evaluation requires a context input, "
                    "an expected calibrator SHA-256, exact 250+250 prefix ticks, "
                    "and a 115-D observation"
                ),
            }
        if not config.response_calibrator_path.exists():
            return {
                "status": "HOLD_POLICY_IO_CONTRACT",
                "error": (
                    f"response calibrator missing: {config.response_calibrator_path}"
                ),
            }
        observed_calibrator_sha256 = _sha256_path(config.response_calibrator_path)
        if observed_calibrator_sha256 != config.response_calibrator_sha256:
            return {
                "status": "HOLD_POLICY_IO_CONTRACT",
                "error": (
                    "response calibrator SHA-256 changed: "
                    f"{observed_calibrator_sha256}"
                ),
            }
    elif any(
        (
            config.policy_context_input_name is not None,
            config.response_calibrator_sha256 is not None,
            config.response_calibration_ticks != 0,
            config.response_home_return_ticks != 0,
        )
    ):
        return {
            "status": "HOLD_POLICY_IO_CONTRACT",
            "error": "partial response-conditioned prefix configuration",
        }
""",
        """    response_prefix_enabled = config.response_calibrator_path is not None
    if response_prefix_enabled:
        expected_home_return_ticks = (
            0 if config.response_preserve_handoff_state else 250
        )
        if (
            config.policy_context_input_name is None
            or config.response_calibrator_sha256 is None
            or config.response_calibration_ticks != 250
            or config.response_home_return_ticks != expected_home_return_ticks
            or config.expected_observation_dim != 115
        ):
            return {
                "status": "HOLD_POLICY_IO_CONTRACT",
                "error": (
                    "response-conditioned evaluation requires a context input, "
                    "an expected calibrator SHA-256, exactly 250 calibration "
                    "ticks, the handoff-selected home-return duration, and a "
                    "115-D observation"
                ),
            }
        if config.response_preserve_handoff_state and (
            "previous_action" not in config.policy_state_input_names
            or "previous_action_out" not in config.policy_state_output_names
        ):
            return {
                "status": "HOLD_POLICY_IO_CONTRACT",
                "error": (
                    "state-coherent handoff requires previous_action and "
                    "previous_action_out in the recurrent ABI"
                ),
            }
        if not config.response_calibrator_path.exists():
            return {
                "status": "HOLD_POLICY_IO_CONTRACT",
                "error": (
                    f"response calibrator missing: {config.response_calibrator_path}"
                ),
            }
        observed_calibrator_sha256 = _sha256_path(config.response_calibrator_path)
        if observed_calibrator_sha256 != config.response_calibrator_sha256:
            return {
                "status": "HOLD_POLICY_IO_CONTRACT",
                "error": (
                    "response calibrator SHA-256 changed: "
                    f"{observed_calibrator_sha256}"
                ),
            }
    elif any(
        (
            config.policy_context_input_name is not None,
            config.response_calibrator_sha256 is not None,
            config.response_calibration_ticks != 0,
            config.response_home_return_ticks != 0,
            config.response_preserve_handoff_state,
        )
    ):
        return {
            "status": "HOLD_POLICY_IO_CONTRACT",
            "error": "partial response-conditioned prefix configuration",
        }
""",
    ),
    (
        """            "locomotion_previous_action_exact_zero": None,
        }
""",
        """            "locomotion_previous_action_exact_zero": None,
            "locomotion_previous_action_matches_calibration": None,
            "handoff_state_preserved": False,
            "calibration_final_action": None,
            "locomotion_applied_target_observation_rad": None,
            "observer_bridge_applied_target_rad": None,
            "applied_target_observation_matches_bridge": None,
        }
""",
    ),
    (
        """                for _ in range(int(config.response_home_return_ticks)):
                    prefix_observation(state, calibration=False)
                    state = apply_unscored_prefix_action(state, zero_action)
                    if bool(np.asarray(jax.device_get(state.done))):
                        raise ValueError("home-return prefix terminated early")
            except ValueError as exc:
""",
        """                for _ in range(int(config.response_home_return_ticks)):
                    prefix_observation(state, calibration=False)
                    state = apply_unscored_prefix_action(state, zero_action)
                    if bool(np.asarray(jax.device_get(state.done))):
                        raise ValueError("home-return prefix terminated early")
                if config.response_preserve_handoff_state:
                    hidden_state["previous_action"] = calibrator_previous.copy()
            except ValueError as exc:
""",
    ),
    (
        """                "locomotion_hidden_exact_zero": all(
                    np.count_nonzero(value) == 0
                    for value in hidden_state.values()
                ),
                "locomotion_previous_action_exact_zero": bool(
                    locomotion_previous_action.shape
                    == (config.expected_action_dim,)
                    and np.count_nonzero(locomotion_previous_action) == 0
                ),
            }
            if (
                response_calibration_audit["locomotion_phase_reset"]
                != [1.0, 0.0]
                or not response_calibration_audit[
                    "locomotion_hidden_exact_zero"
                ]
                or not response_calibration_audit[
                    "locomotion_previous_action_exact_zero"
                ]
            ):
""",
        """                "locomotion_hidden_exact_zero": all(
                    np.count_nonzero(value) == 0
                    for name, value in hidden_state.items()
                    if name != "previous_action"
                ),
                "locomotion_previous_action_exact_zero": bool(
                    locomotion_previous_action.shape
                    == (config.expected_action_dim,)
                    and np.count_nonzero(locomotion_previous_action) == 0
                ),
                "locomotion_previous_action_matches_calibration": bool(
                    locomotion_previous_action.shape
                    == (config.expected_action_dim,)
                    and np.array_equal(
                        locomotion_previous_action, calibrator_previous[0]
                    )
                    and np.array_equal(
                        hidden_state["previous_action"], calibrator_previous
                    )
                ),
                "handoff_state_preserved": bool(
                    config.response_preserve_handoff_state
                ),
                "calibration_final_action": (
                    calibrator_previous[0].astype(float).tolist()
                ),
                "locomotion_applied_target_observation_rad": (
                    np.asarray(
                        jax.device_get(state.obs["state"]),
                        dtype=np.float32,
                    )[83:97].astype(float).tolist()
                ),
                "observer_bridge_applied_target_rad": (
                    (
                        bridge
                        if policy_observer_bridge is None
                        else policy_observer_bridge
                    ).value.astype(float).tolist()
                ),
                "applied_target_observation_matches_bridge": bool(
                    np.array_equal(
                        np.asarray(
                            jax.device_get(state.obs["state"]),
                            dtype=np.float32,
                        )[83:97],
                        (
                            bridge
                            if policy_observer_bridge is None
                            else policy_observer_bridge
                        ).value.astype(np.float32),
                    )
                ),
            }
            previous_action_handoff_valid = (
                response_calibration_audit[
                    "locomotion_previous_action_matches_calibration"
                ]
                if config.response_preserve_handoff_state
                else response_calibration_audit[
                    "locomotion_previous_action_exact_zero"
                ]
            )
            applied_target_handoff_valid = (
                not config.policy_applied_target_observation
                or response_calibration_audit[
                    "applied_target_observation_matches_bridge"
                ]
            )
            if (
                response_calibration_audit["locomotion_phase_reset"]
                != [1.0, 0.0]
                or not response_calibration_audit[
                    "locomotion_hidden_exact_zero"
                ]
                or not previous_action_handoff_valid
                or not applied_target_handoff_valid
            ):
""",
    ),
    (
        """            "home_return_ticks": int(config.response_home_return_ticks),
        },
""",
        """            "home_return_ticks": int(config.response_home_return_ticks),
            "preserve_handoff_state": bool(
                config.response_preserve_handoff_state
            ),
        },
""",
    ),
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def source_bytes() -> bytes:
    value = SOURCE.read_bytes()
    if sha256_bytes(value) != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("frozen closed-loop evaluator source changed")
    return value


def patched_source() -> str:
    value = source_bytes().decode("utf-8").replace("\r\n", "\n")
    for index, (before, after) in enumerate(PATCHES):
        count = value.count(before)
        if count != 1:
            raise RuntimeError(
                f"T8 evaluator patch {index} expected one match, observed {count}"
            )
        value = value.replace(before, after, 1)
    compile(value, f"{SOURCE}::T8", "exec")
    return value


def patched_source_sha256() -> str:
    return sha256_bytes(patched_source().encode("utf-8"))


def load_module() -> types.ModuleType:
    source = patched_source()
    module = types.ModuleType(MODULE_NAME)
    module.__file__ = f"{SOURCE}::T8"
    module.__package__ = ""
    sys.modules[MODULE_NAME] = module
    try:
        exec(compile(source, module.__file__, "exec"), module.__dict__)
    except Exception:
        sys.modules.pop(MODULE_NAME, None)
        raise
    return module


def contract() -> dict[str, Any]:
    return {
        "source_path": str(SOURCE),
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "patched_source_sha256": patched_source_sha256(),
        "patch_count": len(PATCHES),
        "default_off": (
            "response_preserve_handoff_state defaults false; the frozen "
            "250+250 response path is otherwise unchanged"
        ),
        "authorized_delta": (
            "T8 only: require zero home-return ticks, retain the final "
            "calibrator action as the locomotion previous_action, and report "
            "the coherent handoff receipt"
        ),
    }


if __name__ == "__main__":
    print(contract())
