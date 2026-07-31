#!/usr/bin/env python3
"""Preregister the T11 state-coherent context-action observability audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t11_context_action_observability_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "T11_CONTEXT_ACTION_OBSERVABILITY_PREREGISTRATION_20260726.md"
)
T10_RESULT = (
    ANALYSIS / "t10_response_conditioned_continuation_cpu_result.json"
)
T10_AUDIT = (
    ANALYSIS
    / "t10_response_conditioned_continuation_cpu_independent_audit.json"
)
EXPLORATORY_DEBUG = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t10_response_conditioned_cpu_contract_v2"
    r"\t10_step1024_debug.onnx"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if not args.write:
        raise SystemExit("T11 preregistration requires --write")
    if PREREG.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T11 preregistration")

    t10 = json.loads(T10_RESULT.read_text(encoding="utf-8"))
    audit = json.loads(T10_AUDIT.read_text(encoding="utf-8"))
    if (
        t10["failed_checks"] != ["trained_graph_uses_context_action"]
        or audit["issues"] != ["trained_context_action_effect"]
    ):
        raise RuntimeError("T10 does not have the single expected hold")
    final_graph = Path(t10["training"]["final_onnx"]["path"])
    if receipt(final_graph) != t10["training"]["final_onnx"]:
        raise RuntimeError("T10 final graph changed")

    sources = {
        "builder": receipt(Path(__file__)),
        "runner": receipt(
            ROOT / "tools" / "run_t11_context_action_observability.py"
        ),
        "independent_auditor": receipt(
            ROOT / "tools" / "audit_t11_context_action_observability.py"
        ),
        "t10_result": receipt(T10_RESULT),
        "t10_independent_audit": receipt(T10_AUDIT),
        "t10_final_onnx": receipt(final_graph),
        "exploratory_debug_graph": receipt(EXPLORATORY_DEBUG),
    }
    basis = {
        "schema_version": "open_duck.t11_context_action_observability.v1",
        "status": "PREREGISTERED_T11_CONTEXT_ACTION_OBSERVABILITY",
        "question": (
            "Did T10 learn a deployment-visible context-to-action path that "
            "its random, state-incoherent previous-action test masked by "
            "forcing both actions onto the same supreme rate boundary?"
        ),
        "causal_basis": {
            "t10_single_hold": "trained final action context delta was zero",
            "t10_other_checks": "every other runner check passed",
            "known_updated_context_kernels": {
                "context_hidden_projection": 0.008539136499166489,
                "context_location": 0.007182755507528782,
            },
            "exploratory_zero_selection_weight": {
                "seed": 10101,
                "cases": 512,
                "context_location_delta": 0.07761482149362564,
                "raw_action_delta": 0.007934391498565674,
                "random_previous_final_delta": 0.0,
                "raw_coherent_previous_final_delta": 0.007934391498565674,
            },
        },
        "sources": sources,
        "formal_contract": {
            "device": "CPUExecutionProvider",
            "optimizer_steps": 0,
            "simulator_behavior_cells": 0,
            "original_test_reproduction": {
                "seed": 1010203,
                "cases": 256,
                "expected_final_delta": 0.0,
            },
            "disjoint_state_coherent_test": {
                "seed": 1111001,
                "cases": 2048,
                "previous_action": (
                    "zero-context raw_continuous_actions for the same "
                    "observation and recurrent state"
                ),
                "minimum_context_location_delta": 1e-6,
                "minimum_raw_action_delta": 1e-6,
                "minimum_final_action_delta": 1e-6,
                "minimum_effective_case_fraction": 0.95,
            },
            "disjoint_causal_sequence_test": {
                "seed": 1111002,
                "sequences": 128,
                "ticks": 32,
                "minimum_divergent_sequence_fraction": 0.95,
                "graph_owned_previous_action_and_hidden": True,
            },
            "x0_context_invariance": "final action remains exact zero",
            "rate_excess_tolerance": 1e-7,
        },
        "decision_rule": {
            "pass": (
                "runner and independent auditor pass every frozen check; "
                "T10 remains red as written, but its sole hold is classified "
                "as an invalid state-incoherent observability test"
            ),
            "pass_next_action": (
                "earn only a separately preregistered single hosted "
                "response-conditioned continuation; do not launch it"
            ),
            "fail": (
                "hold hosted compute and close this response-conditioned "
                "action-binding architecture"
            ),
            "partial_results_selection_weight": 0,
            "no_closest_result_promotion": True,
        },
        "authority": {
            "optimizer_steps": 0,
            "hosted_or_colab_compute": False,
            "simulator_behavior_cells": 0,
            "robot_or_rdk_access": False,
            "torque_or_motion": False,
            "gate5": False,
        },
        "execution_now": {
            "optimizer_steps": 0,
            "hosted_or_colab_compute": 0,
            "simulator_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    PREREG.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T11 context-action observability preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Optimizer steps: `0`\n"
        "- Behavior cells: `0`\n"
        "- Hosted/Colab compute: `0`\n"
        "- Robot/RDK-X5 access: `0`\n"
        "- T10 remains red; this tests only whether its sole action-effect "
        "check was masked by state-incoherent rate saturation.\n"
        "- Pass earns only a separately preregistered hosted continuation.\n"
        f"- Canonical SHA-256: "
        f"`{value['preregistered_contract_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    print(f"file_sha256={sha256(PREREG)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
