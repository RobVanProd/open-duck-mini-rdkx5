#!/usr/bin/env python3
"""Expose the T27 calibration context for a diagnostic-only prefix audit."""

from __future__ import annotations

import hashlib
import sys
import types
from typing import Any

import t27_state_coherent_eval_adapter as t27


MODULE_NAME = "closed_loop_sim_eval_t167_response_context"
BASE_PATCHED_SOURCE_SHA256 = t27.patched_source_sha256()
_BEFORE = (
    '                "context_sha256": _array_sha256(response_context),\n'
    '                "context_shape": list(response_context.shape),'
)
_AFTER = (
    '                "context_sha256": _array_sha256(response_context),\n'
    '                "context_value": response_context.astype(float).tolist(),\n'
    '                "context_shape": list(response_context.shape),'
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def patched_source() -> str:
    value = t27.patched_source()
    if value.count(_BEFORE) != 1:
        raise RuntimeError("T167 response-context insertion point changed")
    value = value.replace(_BEFORE, _AFTER, 1)
    compile(value, f"{t27.SOURCE}::T167", "exec")
    return value


def patched_source_sha256() -> str:
    return sha256_bytes(patched_source().encode("utf-8"))


def load_module() -> types.ModuleType:
    source = patched_source()
    module = types.ModuleType(MODULE_NAME)
    module.__file__ = f"{t27.SOURCE}::T167"
    module.__package__ = ""
    sys.modules[MODULE_NAME] = module
    try:
        exec(compile(source, module.__file__, "exec"), module.__dict__)
    except Exception:
        sys.modules.pop(MODULE_NAME, None)
        raise
    return module


def contract() -> dict[str, Any]:
    value = patched_source()
    return {
        "base_patched_source_sha256": BASE_PATCHED_SOURCE_SHA256,
        "patched_source_sha256": sha256_bytes(value.encode("utf-8")),
        "response_context_field_count": value.count(
            '"context_value": response_context.astype(float).tolist()'
        ),
        "semantic_change": (
            "one diagnostic output field after the frozen 250-tick "
            "calibration prefix; transition, observation, action, and "
            "handoff semantics are unchanged"
        ),
    }


if __name__ == "__main__":
    print(contract())
