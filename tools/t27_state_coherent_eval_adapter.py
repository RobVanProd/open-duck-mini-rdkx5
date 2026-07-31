#!/usr/bin/env python3
"""Apply the reviewed state-coherent handoff to the current T25 evaluator."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import types
from typing import Any

import t8_state_coherent_eval_adapter as t8


SOURCE = Path(__file__).resolve().parent / "closed_loop_sim_eval.py"
EXPECTED_SOURCE_SHA256 = (
    "a5bff87f2cce5e5f5c661a9fe73dee9de77a4c356912279e4771025c3379a4ac"
)
MODULE_NAME = "closed_loop_sim_eval_t27_state_coherent"

_CURRENT_RESPONSE_CONTRACT = (
    """    if response_prefix_enabled:
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
    elif zero_context_enabled:
        if (
            config.policy_context_input_name != "calibration_context"
            or config.response_calibrator_sha256 is not None
            or config.response_calibration_ticks != 0
            or config.response_home_return_ticks != 0
            or config.expected_observation_dim != 115
        ):
            return {
                "status": "HOLD_POLICY_IO_CONTRACT",
                "error": (
                    "diagnostic-zero context requires calibration_context, "
                    "no calibrator or prefix ticks, and a 115-D observation"
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
"""
)

_STATE_COHERENT_RESPONSE_CONTRACT = (
    """    if response_prefix_enabled:
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
    elif zero_context_enabled:
        if (
            config.policy_context_input_name != "calibration_context"
            or config.response_calibrator_sha256 is not None
            or config.response_calibration_ticks != 0
            or config.response_home_return_ticks != 0
            or config.expected_observation_dim != 115
        ):
            return {
                "status": "HOLD_POLICY_IO_CONTRACT",
                "error": (
                    "diagnostic-zero context requires calibration_context, "
                    "no calibrator or prefix ticks, and a 115-D observation"
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
"""
)

PATCHES = (
    t8.PATCHES[0],
    (_CURRENT_RESPONSE_CONTRACT, _STATE_COHERENT_RESPONSE_CONTRACT),
    *t8.PATCHES[2:],
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def source_bytes() -> bytes:
    value = SOURCE.read_bytes()
    if sha256_bytes(value) != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("current T27 closed-loop evaluator source changed")
    return value


def patched_source() -> str:
    value = source_bytes().decode("utf-8").replace("\r\n", "\n")
    for index, (before, after) in enumerate(PATCHES):
        count = value.count(before)
        if count != 1:
            raise RuntimeError(
                f"T27 evaluator patch {index} expected one match, "
                f"observed {count}"
            )
        value = value.replace(before, after, 1)
    compile(value, f"{SOURCE}::T27", "exec")
    return value


def patched_source_sha256() -> str:
    return sha256_bytes(patched_source().encode("utf-8"))


def load_module() -> types.ModuleType:
    source = patched_source()
    module = types.ModuleType(MODULE_NAME)
    module.__file__ = f"{SOURCE}::T27"
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
            "response_preserve_handoff_state defaults false; both the "
            "frozen 250+250 response path and T25 diagnostic-zero mode are "
            "otherwise unchanged"
        ),
        "authorized_delta": (
            "T27 only: require zero home-return ticks, retain the final "
            "calibrator action as locomotion previous_action, and report "
            "the coherent handoff receipt"
        ),
    }


if __name__ == "__main__":
    print(contract())
