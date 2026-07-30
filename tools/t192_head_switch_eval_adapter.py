#!/usr/bin/env python3
"""Add one default-off, tick-exact policy-session switch to T27."""

from __future__ import annotations

import hashlib
import sys
import types
from typing import Any

import t27_state_coherent_eval_adapter as t27


MODULE_NAME = "closed_loop_sim_eval_t192_head_switch"

_CONFIG_BEFORE = """    bridge_mode: str
    command_y: float = 0.0
"""
_CONFIG_AFTER = """    bridge_mode: str
    policy_switch_path: Path | None = None
    policy_switch_sha256: str | None = None
    policy_switch_tick: int | None = None
    command_y: float = 0.0
"""

_SESSION_BEFORE = """    try:
        session = ort.InferenceSession(str(config.policy_path), providers=["CPUExecutionProvider"])
    except Exception as exc:  # pragma: no cover - environment-dependent
        return {
            "status": "HOLD_ENV_NOT_READY",
            "error": f"ONNX Runtime session failed: {type(exc).__name__}: {exc}",
        }
    calibrator_session = None
"""
_SESSION_AFTER = """    try:
        session = ort.InferenceSession(str(config.policy_path), providers=["CPUExecutionProvider"])
    except Exception as exc:  # pragma: no cover - environment-dependent
        return {
            "status": "HOLD_ENV_NOT_READY",
            "error": f"ONNX Runtime session failed: {type(exc).__name__}: {exc}",
        }
    switch_fields = (
        config.policy_switch_path,
        config.policy_switch_sha256,
        config.policy_switch_tick,
    )
    switch_enabled = all(value is not None for value in switch_fields)
    if any(value is not None for value in switch_fields) and not switch_enabled:
        return {
            "status": "HOLD_POLICY_IO_CONTRACT",
            "error": "partial policy-switch configuration",
        }
    switch_session = None
    if switch_enabled:
        if int(config.policy_switch_tick) < 0:
            return {
                "status": "HOLD_POLICY_IO_CONTRACT",
                "error": "policy-switch tick must be nonnegative",
            }
        if not config.policy_switch_path.exists():
            return {
                "status": "HOLD_POLICY_IO_CONTRACT",
                "error": f"policy-switch graph missing: {config.policy_switch_path}",
            }
        observed_switch_sha256 = _sha256_path(config.policy_switch_path)
        if observed_switch_sha256 != config.policy_switch_sha256:
            return {
                "status": "HOLD_POLICY_IO_CONTRACT",
                "error": (
                    "policy-switch graph SHA-256 changed: "
                    f"{observed_switch_sha256}"
                ),
            }
        try:
            switch_session = ort.InferenceSession(
                str(config.policy_switch_path),
                providers=["CPUExecutionProvider"],
            )
        except Exception as exc:
            return {
                "status": "HOLD_POLICY_IO_CONTRACT",
                "error": (
                    "policy-switch ONNX session failed: "
                    f"{type(exc).__name__}: {exc}"
                ),
            }
    calibrator_session = None
"""

_IO_BEFORE = """    try:
        policy_io = init_policy_io_state(session, config)
    except ValueError as exc:
        return {"status": "HOLD_POLICY_IO_CONTRACT", "error": str(exc), "policy": policy}
    input_name = policy_io["obs_input_name"]
"""
_IO_AFTER = """    try:
        policy_io = init_policy_io_state(session, config)
        switch_policy_io = (
            None
            if switch_session is None
            else init_policy_io_state(switch_session, config)
        )
    except ValueError as exc:
        return {"status": "HOLD_POLICY_IO_CONTRACT", "error": str(exc), "policy": policy}
    if switch_policy_io is not None:
        comparable_keys = (
            "obs_input_name",
            "action_output_name",
            "state_input_names",
            "state_output_names",
            "state_input_shapes",
            "context_input_name",
            "context_input_shape",
        )
        if any(
            switch_policy_io[key] != policy_io[key]
            for key in comparable_keys
        ):
            return {
                "status": "HOLD_POLICY_IO_CONTRACT",
                "error": "primary and switch policy ABIs differ",
                "policy": policy,
            }
    input_name = policy_io["obs_input_name"]
"""

_RUN_BEFORE = """            outputs = session.run([output_name, *state_output_names], feed)
"""
_RUN_AFTER = """            policy_switch_active = bool(
                switch_session is not None
                and tick >= int(config.policy_switch_tick)
            )
            active_session = switch_session if policy_switch_active else session
            outputs = active_session.run(
                [output_name, *state_output_names],
                feed,
            )
"""

_TRACE_BEFORE = """                "policy_graph_authoritative_output": bool(
                    config.policy_graph_authoritative_output
                ),
"""
_TRACE_AFTER = """                "policy_graph_authoritative_output": bool(
                    config.policy_graph_authoritative_output
                ),
                "policy_switch_active": policy_switch_active,
                "policy_session_role": (
                    "switch" if policy_switch_active else "primary"
                ),
"""

PATCHES = (
    (_CONFIG_BEFORE, _CONFIG_AFTER),
    (_SESSION_BEFORE, _SESSION_AFTER),
    (_IO_BEFORE, _IO_AFTER),
    (_RUN_BEFORE, _RUN_AFTER),
    (_TRACE_BEFORE, _TRACE_AFTER),
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def patched_source() -> str:
    value = t27.patched_source()
    for index, (before, after) in enumerate(PATCHES):
        count = value.count(before)
        if count != 1:
            raise RuntimeError(
                f"T192 evaluator patch {index} expected one match, "
                f"observed {count}"
            )
        value = value.replace(before, after, 1)
    compile(value, f"{t27.SOURCE}::T192", "exec")
    return value


def patched_source_sha256() -> str:
    return sha256_bytes(patched_source().encode("utf-8"))


def load_module() -> types.ModuleType:
    source = patched_source()
    module = types.ModuleType(MODULE_NAME)
    module.__file__ = f"{t27.SOURCE}::T192"
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
        "t27_patched_source_sha256": t27.patched_source_sha256(),
        "t192_patched_source_sha256": patched_source_sha256(),
        "patch_count": len(PATCHES),
        "default_off": (
            "all three switch fields default to None; the T27 path is "
            "otherwise unchanged"
        ),
        "authorized_delta": (
            "T192 only: switch from the primary ONNX session to one "
            "hash-frozen ABI-identical ONNX session at one exact scored tick"
        ),
    }


if __name__ == "__main__":
    print(contract())
