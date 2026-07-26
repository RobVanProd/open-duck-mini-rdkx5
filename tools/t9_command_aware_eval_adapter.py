#!/usr/bin/env python3
"""Versioned x=0 context-bypass adapter layered on the frozen T8 evaluator."""

from __future__ import annotations

import hashlib
import sys
import types
from typing import Any

import t8_state_coherent_eval_adapter as t8


EXPECTED_T8_SOURCE_SHA256 = (
    "1c7de5aba3b498975c3ef02c13599d176527028caaa0058172760125734e5a88"
)
MODULE_NAME = "closed_loop_sim_eval_t9_command_aware"

PATCHES = (
    (
        """    response_preserve_handoff_state: bool = False
    policy_applied_target_observation: bool = False
""",
        """    response_preserve_handoff_state: bool = False
    response_zero_context_bypass: bool = False
    policy_applied_target_observation: bool = False
""",
    ),
    (
        """    elif any(
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
        """    elif config.response_zero_context_bypass:
        if (
            config.policy_context_input_name != "calibration_context"
            or config.expected_observation_dim != 115
            or config.response_calibrator_sha256 is not None
            or config.response_calibration_ticks != 0
            or config.response_home_return_ticks != 0
            or config.response_preserve_handoff_state
        ):
            return {
                "status": "HOLD_POLICY_IO_CONTRACT",
                "error": "invalid command-aware zero-context bypass",
            }
    elif any(
        (
            config.policy_context_input_name is not None,
            config.response_calibrator_sha256 is not None,
            config.response_calibration_ticks != 0,
            config.response_home_return_ticks != 0,
            config.response_preserve_handoff_state,
            config.response_zero_context_bypass,
        )
    ):
        return {
            "status": "HOLD_POLICY_IO_CONTRACT",
            "error": "partial response-conditioned prefix configuration",
        }
""",
    ),
    (
        """        response_context: np.ndarray | None = None
        response_calibration_audit = {
            "enabled": False,
""",
        """        response_context: np.ndarray | None = (
            np.zeros((1, 64), dtype=np.float32)
            if config.response_zero_context_bypass
            else None
        )
        response_calibration_audit = {
            "enabled": False,
            "zero_context_bypass": bool(
                config.response_zero_context_bypass
            ),
""",
    ),
    (
        """        for tick in range(sim_steps):
""",
        """        if config.response_zero_context_bypass:
            bypass_observation = np.asarray(
                jax.device_get(state.obs["state"]), dtype=np.float32
            )
            bypass_previous_action = np.asarray(
                jax.device_get(state.info["last_act"]), dtype=np.float32
            )
            observer_bridge = (
                bridge
                if policy_observer_bridge is None
                else policy_observer_bridge
            )
            response_calibration_audit.update(
                {
                    "context_sha256": _array_sha256(response_context),
                    "context_shape": list(response_context.shape),
                    "context_finite": bool(
                        np.all(np.isfinite(response_context))
                    ),
                    "locomotion_phase_reset": np.asarray(
                        jax.device_get(state.info["imitation_phase"]),
                        dtype=np.float32,
                    ).astype(float).tolist(),
                    "locomotion_hidden_exact_zero": all(
                        np.count_nonzero(value) == 0
                        for value in hidden_state.values()
                    ),
                    "locomotion_previous_action_exact_zero": bool(
                        bypass_previous_action.shape
                        == (config.expected_action_dim,)
                        and np.count_nonzero(bypass_previous_action) == 0
                    ),
                    "locomotion_applied_target_observation_rad": (
                        bypass_observation[83:97].astype(float).tolist()
                    ),
                    "observer_bridge_applied_target_rad": (
                        observer_bridge.value.astype(float).tolist()
                    ),
                    "applied_target_observation_matches_bridge": bool(
                        np.array_equal(
                            bypass_observation[83:97],
                            observer_bridge.value.astype(np.float32),
                        )
                    ),
                }
            )
            if (
                response_calibration_audit["locomotion_phase_reset"]
                != [1.0, 0.0]
                or not response_calibration_audit[
                    "locomotion_hidden_exact_zero"
                ]
                or not response_calibration_audit[
                    "locomotion_previous_action_exact_zero"
                ]
                or not response_calibration_audit[
                    "applied_target_observation_matches_bridge"
                ]
            ):
                return {
                    "status": "HOLD_RESPONSE_CALIBRATION_PREFIX",
                    "error": "x=0 bypass state differs from frozen contract",
                    "policy": policy,
                    "mode": mode,
                    "response_calibration": response_calibration_audit,
                }

        for tick in range(sim_steps):
""",
    ),
    (
        """            "preserve_handoff_state": bool(
                config.response_preserve_handoff_state
            ),
""",
        """            "preserve_handoff_state": bool(
                config.response_preserve_handoff_state
            ),
            "zero_context_bypass": bool(
                config.response_zero_context_bypass
            ),
""",
    ),
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def base_source() -> str:
    value = t8.patched_source()
    if sha256_bytes(value.encode("utf-8")) != EXPECTED_T8_SOURCE_SHA256:
        raise RuntimeError("frozen T8 evaluator source changed")
    return value


def patched_source() -> str:
    value = base_source()
    for index, (before, after) in enumerate(PATCHES):
        count = value.count(before)
        if count != 1:
            raise RuntimeError(
                f"T9 evaluator patch {index} expected one match, observed {count}"
            )
        value = value.replace(before, after, 1)
    compile(value, "closed_loop_sim_eval.py::T9", "exec")
    return value


def patched_source_sha256() -> str:
    return sha256_bytes(patched_source().encode("utf-8"))


def load_module() -> types.ModuleType:
    source = patched_source()
    module = types.ModuleType(MODULE_NAME)
    module.__file__ = "closed_loop_sim_eval.py::T9"
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
        "base": t8.contract(),
        "base_patched_source_sha256": EXPECTED_T8_SOURCE_SHA256,
        "patched_source_sha256": patched_source_sha256(),
        "patch_count": len(PATCHES),
        "default_off": (
            "response_zero_context_bypass defaults false; T8 response-prefix "
            "behavior is unchanged"
        ),
        "authorized_delta": (
            "T9 x=0 only: omit the universal-support prefix, inject immutable "
            "zero context, and audit exact home/phase/recurrent/applied-target "
            "initialization"
        ),
    }


if __name__ == "__main__":
    print(contract())
