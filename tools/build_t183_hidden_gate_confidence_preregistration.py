#!/usr/bin/env python3
"""Preregister the saved-trace T183 hidden-gate confidence audit."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    ROOT,
    canonical_sha256,
    receipt,
)


T180B_PREREG = (
    ANALYSIS / "t180b_transform_route_attribution_preregistration.json"
)
T180B_RESULT = ANALYSIS / "t180b_transform_route_attribution_result.json"
T182B_RESULT = ANALYSIS / "t182b_shared_failure_single_cell_result.json"
OUTPUT = ANALYSIS / "t183_hidden_gate_confidence_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T183_HIDDEN_GATE_CONFIDENCE_PREREGISTRATION_20260730.md"
)
BUILDER = Path(__file__).resolve()
RUNNER = ROOT / "tools" / "run_t183_hidden_gate_confidence.py"
TEST = ROOT / "tests" / "test_t183_hidden_gate_confidence.py"


def _canonical_without(value: dict[str, Any], field: str) -> str:
    basis = dict(value)
    basis.pop(field, None)
    return canonical_sha256(basis)


def _require(condition: object, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _load(path: Path) -> dict[str, Any]:
    _require(path.is_file(), f"missing input: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def _case_basis(case: dict[str, Any]) -> dict[str, Any]:
    return {
        key: case[key]
        for key in (
            "case_id",
            "family",
            "checkpoint_pair",
            "fit_id",
            "command_x_m_s",
            "context",
            "context_sha256",
            "source_graph",
            "transformed_graph",
            "source_trace",
            "transformed_trace",
        )
    }


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T183: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T183 preregistration requires clean worktree")

    t180b_prereg = _load(T180B_PREREG)
    t180b_result = _load(T180B_RESULT)
    t182b_result = _load(T182B_RESULT)
    _require(
        _canonical_without(t180b_prereg, "preregistered_contract_sha256")
        == t180b_prereg["preregistered_contract_sha256"],
        "T180B preregistration hash differs",
    )
    _require(
        _canonical_without(t180b_result, "result_sha256")
        == t180b_result["result_sha256"],
        "T180B result hash differs",
    )
    _require(
        _canonical_without(t182b_result, "result_sha256")
        == t182b_result["result_sha256"],
        "T182B result hash differs",
    )
    _require(
        t180b_result["classification"]
        == "SHARED_HEAD_DIRECTION_CONTEXT_AMPLITUDE_TRADEOFF",
        "T180B does not support a confidence-gate audit",
    )
    _require(
        t182b_result["decision"]
        == "CLOSE_COUNT_WEIGHTED_ALPHA_0P2_WITHOUT_MORE_BEHAVIOR",
        "T182B has not closed fixed interpolation",
    )

    labeled = [
        _case_basis(case)
        for case in t180b_prereg["cases"]
        if case["family"]
        in ("negative_y_rescue", "positive_z_regression")
    ]
    shared = [
        _case_basis(case)
        for case in t180b_prereg["cases"]
        if case["family"] == "positive_z_shared_failure"
    ]
    _require(
        len(labeled) == 5
        and sum(
            case["family"] == "negative_y_rescue" for case in labeled
        )
        == 1
        and sum(
            case["family"] == "positive_z_regression" for case in labeled
        )
        == 4,
        "unexpected labeled T180B population",
    )
    _require(len(shared) == 1, "unexpected T180B shared-failure population")
    alpha_trace = t182b_result["cell"]["protection"]
    alpha_context = t182b_result["cell"]["handoff"]["response_audit"]
    _require(
        alpha_context["context_sha256"] == shared[0]["context_sha256"],
        "T182B alpha context differs from the frozen shared-failure context",
    )
    alpha_case = {
        "case_id": "Z_POS_SHARED_ALPHA_0P2_HALF_P31_X077",
        "family": "positive_z_shared_failure_unlabeled",
        "checkpoint_pair": "half",
        "fit_id": "p31_34",
        "command_x_m_s": 0.077,
        "context": shared[0]["context"],
        "context_sha256": alpha_context["context_sha256"],
        "candidate_trace": alpha_trace,
        "source_graph": shared[0]["source_graph"],
        "transformed_graph": shared[0]["transformed_graph"],
    }

    frozen_inputs = {
        "builder": receipt(BUILDER),
        "runner": receipt(RUNNER),
        "test": receipt(TEST),
        "t180b_preregistration": receipt(T180B_PREREG),
        "t180b_result": receipt(T180B_RESULT),
        "t182b_result": receipt(T182B_RESULT),
    }
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t183_hidden_gate_confidence_preregistration.v1"
        ),
        "status": "PREREGISTERED_T183_HIDDEN_GATE_CONFIDENCE",
        "question": (
            "Can the already deployed live hidden-gate score separate the "
            "T175 negative-Y rescue states from the T175-only positive-Z "
            "regression states with one exact, untuned confidence threshold?"
        ),
        "frozen_inputs": frozen_inputs,
        "labeled_cases": labeled,
        "unlabeled_shared_cases": shared,
        "unlabeled_alpha_case": alpha_case,
        "analysis_contract": {
            "provider": "CPUExecutionProvider",
            "prefix_ticks": 162,
            "alpha_trace_ticks": int(alpha_trace["rows"]),
            "feature": (
                "existing hidden_gate_score = "
                "((h_out-hidden_gate_mean)/hidden_gate_scale)"
                "@hidden_gate_coefficient+hidden_gate_intercept"
            ),
            "effective_head_row": (
                "L_inf(T175_action-source_action) > 1e-7"
            ),
            "derivation_banks": "source_trace only",
            "validation_banks": "transformed_trace only",
            "positive_class": "negative_y_rescue",
            "negative_class": "positive_z_regression",
            "fixed_direction": (
                "larger existing hidden_gate_score means greater confidence "
                "in the already frozen negative_com_gate"
            ),
            "threshold": (
                "midpoint(minimum derivation rescue score, "
                "maximum derivation regression score)"
            ),
            "required_derivation_margin": (
                "minimum rescue score - maximum regression score > 0"
            ),
            "required_validation": (
                "every effective rescue row score >= threshold and every "
                "effective regression row score < threshold"
            ),
            "shared_failure_role": (
                "unlabeled reporting only because source and T175 both fail "
                "while alpha=0.20 extends survival"
            ),
            "feature_search": False,
            "threshold_search": False,
            "alternate_direction": False,
            "behavior_cells": 0,
        },
        "frozen_gate_initializers": [
            "hidden_gate_mean",
            "hidden_gate_scale",
            "hidden_gate_coefficient",
            "hidden_gate_intercept",
            "hidden_gate_zero",
        ],
        "decision_rule": {
            "pass": (
                "EARN_T184_HIDDEN_CONFIDENCE_GATED_HEAD_GRAPH_"
                "PREREGISTRATION_ONLY"
            ),
            "fail": (
                "CLOSE_EXISTING_HIDDEN_SCORE_CONTEXT_GATE_AND_RETURN_TO_"
                "MECHANISM_SELECTION"
            ),
            "no_retry": True,
            "no_alternate_threshold": True,
        },
        "execution_now": {
            "saved_trace_rows": 0,
            "new_behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority_after_result": {
            "graph_transform_preregistration_if_pass": True,
            "new_behavior": False,
            "optimizer": False,
            "hosted_compute": False,
            "deployment_contract_audit": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T183 hidden-gate confidence preregistration\n\n"
        f"- Status: `{value['status']}`\n"
        "- Feature: the graph's existing live `hidden_gate_score` only\n"
        "- Derivation: source trajectories; validation: transformed "
        "trajectories\n"
        "- Threshold: midpoint of an exact rescue/regression score gap\n"
        "- No feature scan, threshold scan, behavior, optimizer, hosted "
        "compute, or robot\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"contract_sha256={value['preregistered_contract_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
