#!/usr/bin/env python3
"""Load a T8 evaluator that shadows the existing locomotion recurrence.

The executed 250-tick response prefix remains owned by the frozen calibrator.
The locomotion policy observes the same prefix in shadow mode: its action is
ignored, while its existing recurrent ``h_out`` is chained.  At handoff that
state replaces the otherwise-zero locomotion ``h_in``.  No weights, policy
inputs, action boundaries, or physical prefix actions are changed.
"""

from __future__ import annotations

import hashlib
import sys
import types

import t8_state_coherent_eval_adapter as t8


MODULE_NAME = "closed_loop_sim_eval_t13_shadow_hidden"
EXPECTED_T8_SOURCE_SHA256 = (
    "1c7de5aba3b498975c3ef02c13599d176527028caaa0058172760125734e5a88"
)


PATCHES = (
    (
        """    response_preserve_handoff_state: bool = False
    policy_applied_target_observation: bool = False
""",
        """    response_preserve_handoff_state: bool = False
    response_shadow_policy_hidden: bool = False
    policy_applied_target_observation: bool = False
""",
    ),
    (
        """        if config.response_preserve_handoff_state and (
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
""",
        """        if config.response_preserve_handoff_state and (
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
        if config.response_shadow_policy_hidden and (
            not config.response_preserve_handoff_state
            or tuple(config.policy_state_input_names)
            != ("h_in", "previous_action")
            or tuple(config.policy_state_output_names)
            != ("h_out", "previous_action_out")
        ):
            return {
                "status": "HOLD_POLICY_IO_CONTRACT",
                "error": (
                    "shadow-hidden handoff requires preserved state and the "
                    "exact h_in/previous_action recurrent ABI"
                ),
            }
""",
    ),
    (
        """            config.response_home_return_ticks != 0,
            config.response_preserve_handoff_state,
        )
""",
        """            config.response_home_return_ticks != 0,
            config.response_preserve_handoff_state,
            config.response_shadow_policy_hidden,
        )
""",
    ),
    (
        """            "calibration_final_action": None,
            "locomotion_applied_target_observation_rad": None,
""",
        """            "calibration_final_action": None,
            "shadow_policy_enabled": False,
            "shadow_policy_steps": 0,
            "shadow_policy_actions_ignored": None,
            "shadow_policy_hidden": None,
            "shadow_policy_hidden_sha256": None,
            "shadow_policy_hidden_finite": None,
            "shadow_policy_hidden_nonzero": None,
            "locomotion_hidden_matches_shadow": None,
            "calibration_context": None,
            "locomotion_applied_target_observation_rad": None,
""",
    ),
    (
        """            calibrator_hidden = np.zeros((1, 64), dtype=np.float32)
            try:
                for _ in range(int(config.response_calibration_ticks)):
                    calibration_obs = prefix_observation(
                        state, calibration=True
                    )
                    calibration_outputs = calibrator_session.run(
""",
        """            calibrator_hidden = np.zeros((1, 64), dtype=np.float32)
            shadow_policy_hidden = np.zeros((1, 64), dtype=np.float32)
            shadow_policy_steps = 0
            try:
                for _ in range(int(config.response_calibration_ticks)):
                    calibration_obs = prefix_observation(
                        state, calibration=True
                    )
                    if config.response_shadow_policy_hidden:
                        shadow_feed = {
                            input_name: calibration_obs[None, :],
                            "h_in": shadow_policy_hidden,
                            "previous_action": calibrator_previous,
                            context_input_name: np.zeros(
                                (1, 64), dtype=np.float32
                            ),
                        }
                        shadow_outputs = session.run(
                            [output_name, *state_output_names], shadow_feed
                        )
                        graph_authoritative_action(
                            shadow_outputs[0],
                            expected_action_dim=config.expected_action_dim,
                            previous_action_output=shadow_outputs[
                                1
                                + state_output_names.index(
                                    "previous_action_out"
                                )
                            ],
                        )
                        shadow_policy_hidden = np.asarray(
                            shadow_outputs[
                                1 + state_output_names.index("h_out")
                            ],
                            dtype=np.float32,
                        )
                        if (
                            shadow_policy_hidden.shape != (1, 64)
                            or not np.all(np.isfinite(shadow_policy_hidden))
                        ):
                            raise ValueError(
                                "shadow policy hidden output is invalid"
                            )
                        shadow_policy_steps += 1
                    calibration_outputs = calibrator_session.run(
""",
    ),
    (
        """                if config.response_preserve_handoff_state:
                    hidden_state["previous_action"] = calibrator_previous.copy()
            except ValueError as exc:
""",
        """                if config.response_preserve_handoff_state:
                    hidden_state["previous_action"] = calibrator_previous.copy()
                    if config.response_shadow_policy_hidden:
                        hidden_state["h_in"] = shadow_policy_hidden.copy()
            except ValueError as exc:
""",
    ),
    (
        """                "calibration_final_action": (
                    calibrator_previous[0].astype(float).tolist()
                ),
                "locomotion_applied_target_observation_rad": (
""",
        """                "calibration_final_action": (
                    calibrator_previous[0].astype(float).tolist()
                ),
                "shadow_policy_enabled": bool(
                    config.response_shadow_policy_hidden
                ),
                "shadow_policy_steps": int(shadow_policy_steps),
                "shadow_policy_actions_ignored": bool(
                    config.response_shadow_policy_hidden
                ),
                "shadow_policy_hidden": (
                    shadow_policy_hidden[0].astype(float).tolist()
                    if config.response_shadow_policy_hidden
                    else None
                ),
                "shadow_policy_hidden_sha256": (
                    _array_sha256(shadow_policy_hidden)
                    if config.response_shadow_policy_hidden
                    else None
                ),
                "shadow_policy_hidden_finite": (
                    bool(np.all(np.isfinite(shadow_policy_hidden)))
                    if config.response_shadow_policy_hidden
                    else None
                ),
                "shadow_policy_hidden_nonzero": (
                    bool(np.count_nonzero(shadow_policy_hidden))
                    if config.response_shadow_policy_hidden
                    else None
                ),
                "locomotion_hidden_matches_shadow": (
                    bool(
                        np.array_equal(
                            hidden_state["h_in"], shadow_policy_hidden
                        )
                    )
                    if config.response_shadow_policy_hidden
                    else None
                ),
                "calibration_context": (
                    response_context[0].astype(float).tolist()
                ),
                "locomotion_applied_target_observation_rad": (
""",
    ),
    (
        """                or not response_calibration_audit[
                    "locomotion_hidden_exact_zero"
                ]
                or not previous_action_handoff_valid
""",
        """                or not (
                    (
                        config.response_shadow_policy_hidden
                        and response_calibration_audit[
                            "locomotion_hidden_matches_shadow"
                        ]
                        and response_calibration_audit[
                            "shadow_policy_hidden_finite"
                        ]
                        and response_calibration_audit[
                            "shadow_policy_hidden_nonzero"
                        ]
                        and response_calibration_audit[
                            "shadow_policy_steps"
                        ]
                        == config.response_calibration_ticks
                    )
                    or (
                        not config.response_shadow_policy_hidden
                        and response_calibration_audit[
                            "locomotion_hidden_exact_zero"
                        ]
                    )
                )
                or not previous_action_handoff_valid
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
            "shadow_policy_hidden": bool(
                config.response_shadow_policy_hidden
            ),
""",
    ),
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def source_bytes() -> bytes:
    value = t8.patched_source().encode("utf-8")
    observed = sha256_bytes(value)
    if observed != EXPECTED_T8_SOURCE_SHA256:
        raise RuntimeError(
            "frozen T8 evaluator source changed: "
            f"{observed} != {EXPECTED_T8_SOURCE_SHA256}"
        )
    return value


def patched_source() -> str:
    value = source_bytes().decode("utf-8")
    for index, (before, after) in enumerate(PATCHES):
        count = value.count(before)
        if count != 1:
            raise RuntimeError(
                f"T13 evaluator patch {index} expected one match, "
                f"observed {count}"
            )
        value = value.replace(before, after, 1)
    compile(value, f"{t8.SOURCE}::T13", "exec")
    return value


def patched_source_sha256() -> str:
    return sha256_bytes(patched_source().encode("utf-8"))


def load_module() -> types.ModuleType:
    source = patched_source()
    module = types.ModuleType(MODULE_NAME)
    module.__file__ = f"{t8.SOURCE}::T13"
    module.__package__ = ""
    sys.modules[MODULE_NAME] = module
    try:
        exec(compile(source, module.__file__, "exec"), module.__dict__)
    except Exception:
        sys.modules.pop(MODULE_NAME, None)
        raise
    return module
