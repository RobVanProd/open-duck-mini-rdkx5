from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_t7_universal_response_support import (  # noqa: E402
    canonical_sha256,
    longest_true_run_per_joint,
    response_checks,
)


def test_longest_true_run_is_per_joint_and_consecutive() -> None:
    mask = np.zeros((8, 14), dtype=bool)
    mask[0:2, 0] = True
    mask[4:7, 0] = True
    mask[1:6, 1] = True
    observed = longest_true_run_per_joint(mask)
    assert observed[0] == 3
    assert observed[1] == 5
    assert observed[2:] == [0] * 12


def test_canonical_sha256_is_key_order_independent() -> None:
    left = {"b": [2, 3], "a": 1}
    right = {"a": 1, "b": [2, 3]}
    assert canonical_sha256(left) == canonical_sha256(right)


def cell(
    configuration: str,
    fit: str,
    repeat: int,
    context: list[float],
    trace: str,
) -> dict:
    context_array = np.asarray(context, dtype=np.float32)
    context_hash = hashlib.sha256(context_array.tobytes()).hexdigest()
    return {
        "configuration_id": configuration,
        "fit_id": fit,
        "repeat": repeat,
        "trace": {"sha256": trace},
        "response_context": context,
        "response_context_sha256": context_hash,
        "hidden_trace_sha256": f"hidden-{configuration}-{fit}",
    }


def test_response_checks_require_repeatability_and_signed_separation() -> None:
    prereg = {
        "matrix": {
            "configurations": [
                {"id": "NOMINAL"},
                {"id": "TORSO_COM_X_NEG"},
                {"id": "TORSO_COM_X_POS"},
            ],
            "fits": ["p30", "p31_34"],
        },
        "behavior_contract": {
            "response_signal": {
                "minimum_signed_com_endpoint_linf_separation_per_fit": 0.15,
                "nominal_difference_floor_linf": 1.0e-7,
            }
        },
    }
    cells = []
    contexts = {
        "NOMINAL": [0.0, 0.0],
        "TORSO_COM_X_NEG": [-0.1, 0.0],
        "TORSO_COM_X_POS": [0.1, 0.0],
    }
    for configuration, context in contexts.items():
        for fit in prereg["matrix"]["fits"]:
            trace = f"trace-{configuration}-{fit}"
            first = cell(configuration, fit, 0, context, trace)
            second = cell(configuration, fit, 1, context, trace)
            second["hidden_trace_sha256"] = first["hidden_trace_sha256"]
            cells.extend([first, second])
    checks, evidence = response_checks(prereg, cells)
    assert all(checks.values())
    assert all(
        item["signed_endpoint_linf"] == 0.2
        for item in evidence["separation"]
    )


def test_response_checks_reject_a_nonrepeatable_trace() -> None:
    prereg = {
        "matrix": {
            "configurations": [
                {"id": "NOMINAL"},
                {"id": "TORSO_COM_X_NEG"},
                {"id": "TORSO_COM_X_POS"},
            ],
            "fits": ["p30"],
        },
        "behavior_contract": {
            "response_signal": {
                "minimum_signed_com_endpoint_linf_separation_per_fit": 0.15,
                "nominal_difference_floor_linf": 1.0e-7,
            }
        },
    }
    cells = []
    for configuration, context in (
        ("NOMINAL", [0.0]),
        ("TORSO_COM_X_NEG", [-0.1]),
        ("TORSO_COM_X_POS", [0.1]),
    ):
        first = cell(configuration, "p30", 0, context, configuration)
        second = cell(configuration, "p30", 1, context, configuration)
        second["hidden_trace_sha256"] = first["hidden_trace_sha256"]
        cells.extend([first, second])
    cells[-1]["trace"]["sha256"] = "different"
    checks, _ = response_checks(prereg, cells)
    assert checks["all_repeat_traces_bit_exact"] is False


def test_frozen_preregistration_is_canonical_after_generation() -> None:
    path = (
        ROOT
        / "outputs"
        / "analysis"
        / "t7_universal_response_support_preregistration.json"
    )
    if not path.exists():
        return
    value = json.loads(path.read_text(encoding="utf-8"))
    basis = {
        key: value[key]
        for key in (
            "repository_inputs",
            "playground",
            "frozen_policy",
            "causal_audit",
            "matrix",
            "behavior_contract",
            "decision_rule",
            "authority",
            "execution_contract",
        )
    }
    assert canonical_sha256(basis) == value["preregistered_contract_sha256"]
    assert value["matrix"]["cells"] == 12
    assert value["authority"]["training_or_hosted_compute"] is False
