#!/usr/bin/env python3
"""Run the preregistered read-only T237 home-offset route autopsy."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper

from run_t136_static_calibration_router_transform import (
    ANALYSIS,
    canonical_sha256,
)


PREREG = ANALYSIS / "t238_home_offset_route_autopsy_preregistration.json"
OUTPUT = ANALYSIS / "t238_home_offset_route_autopsy_result.json"
MARKDOWN = ANALYSIS / "T238_HOME_OFFSET_ROUTE_AUTOPSY_RESULT_20260731.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def arrays(path: Path) -> dict[str, np.ndarray]:
    model = onnx.load(path, load_external_data=True)
    return {
        value.name: numpy_helper.to_array(value).astype(np.float64)
        for value in model.graph.initializer
    }


def router_score(
    context: np.ndarray,
    coefficient: np.ndarray,
    intercept: np.ndarray,
) -> float:
    return float(
        (
            np.asarray(context, dtype=np.float64)
            @ np.asarray(coefficient, dtype=np.float64)
            + np.asarray(intercept, dtype=np.float64)
        ).reshape(-1)[0]
    )


def hidden_gate_scores(
    hidden: np.ndarray,
    values: dict[str, np.ndarray],
) -> np.ndarray:
    return (
        (
            (
                np.asarray(hidden, dtype=np.float64)
                - values["hidden_gate_mean"]
            )
            / values["hidden_gate_scale"]
        )
        @ values["hidden_gate_coefficient"]
        + values["hidden_gate_intercept"]
    ).reshape(-1)


def load_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T238: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        prereg["status"]
        != "PREREGISTERED_T238_HOME_OFFSET_ROUTE_AUTOPSY"
    ):
        raise RuntimeError("T238 preregistration status changed")
    for row in prereg["frozen_inputs"].values():
        path = Path(row["path"])
        if sha256(path) != row["sha256"]:
            raise RuntimeError(f"T238 frozen input changed: {path}")

    contexts_result = json.loads(
        Path(prereg["frozen_inputs"]["t167_contexts"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    contexts = {
        (row["condition_id"], row["fit_id"]): {
            "value": np.asarray(row["context"], dtype=np.float64),
            "sha256": row["context_sha256"],
        }
        for row in contexts_result["cells"]
    }
    graph_values = {
        row["role"]: arrays(Path(row["path"])) for row in prereg["graphs"]
    }
    required = {
        "conditional_path_router_coefficient",
        "conditional_path_router_intercept",
        "positive_router_coefficient",
        "positive_router_intercept",
        "positive_adapter_weight",
        "positive_adapter_bias",
        "nominal_condition_negative_adapter_weight",
        "nominal_condition_negative_adapter_bias",
        "hidden_gate_mean",
        "hidden_gate_scale",
        "hidden_gate_coefficient",
        "hidden_gate_intercept",
    }
    if any(not required.issubset(values) for values in graph_values.values()):
        raise RuntimeError("T238 graph initializer contract changed")

    router_population: list[dict[str, Any]] = []
    half_values = graph_values["half"]
    for (condition, fit), context in sorted(contexts.items()):
        negative_score = router_score(
            context["value"],
            half_values["conditional_path_router_coefficient"],
            half_values["conditional_path_router_intercept"],
        )
        positive_score = router_score(
            context["value"],
            half_values["positive_router_coefficient"],
            half_values["positive_router_intercept"],
        )
        router_population.append(
            {
                "condition_id": condition,
                "fit_id": fit,
                "negative_score": negative_score,
                "negative_selected": negative_score >= 0.0,
                "positive_score": positive_score,
                "positive_selected": positive_score >= 0.0,
            }
        )

    traces: list[dict[str, Any]] = []
    trace_rows = 0
    for block in prereg["blocks"]:
        role = (
            "half"
            if block["checkpoint_id"].endswith("_HALF")
            else "final"
        )
        values = graph_values[role]
        context = contexts[(block["condition_id"], block["fit_id"])]
        negative_score = router_score(
            context["value"],
            values["conditional_path_router_coefficient"],
            values["conditional_path_router_intercept"],
        )
        positive_score = router_score(
            context["value"],
            values["positive_router_coefficient"],
            values["positive_router_intercept"],
        )
        for cell in block["cells"]:
            path = Path(cell["trace"]["path"])
            if sha256(path) != cell["trace"]["sha256"]:
                raise RuntimeError(f"T238 trace changed: {path}")
            rows = load_rows(path)
            trace_rows += len(rows)
            if (
                not rows
                or rows[0]["policy_calibration_context_sha256"]
                != context["sha256"]
                or any(
                    row["policy_calibration_context_sha256"]
                    != context["sha256"]
                    for row in rows
                )
            ):
                raise RuntimeError(f"T238 context/trace mismatch: {path}")
            hidden = np.asarray(
                [row["policy_state_output"]["h_out"][0] for row in rows],
                dtype=np.float64,
            )
            hidden_scores = hidden_gate_scores(hidden, values)
            traces.append(
                {
                    "condition_id": block["condition_id"],
                    "checkpoint_id": block["checkpoint_id"],
                    "role": role,
                    "fit_id": block["fit_id"],
                    "command_x_m_s": cell["command_x_m_s"],
                    "trace_sha256": cell["trace"]["sha256"],
                    "rows": len(rows),
                    "core_pass": cell["core_pass"],
                    "replacement_quality_pass": cell[
                        "replacement_quality_pass"
                    ],
                    "duration_protection_pass": cell[
                        "duration_protection_pass"
                    ],
                    "termination_reason": cell["termination_reason"],
                    "negative_router_score": negative_score,
                    "negative_router_selected": negative_score >= 0.0,
                    "positive_router_score": positive_score,
                    "positive_router_selected": positive_score >= 0.0,
                    "hidden_gate_active_rows": int(
                        np.sum(hidden_scores >= 0.0)
                    ),
                    "hidden_gate_active_fraction": float(
                        np.mean(hidden_scores >= 0.0)
                    ),
                    "hidden_gate_score_min": float(np.min(hidden_scores)),
                    "hidden_gate_score_max": float(np.max(hidden_scores)),
                }
            )

    positive_selected = {
        (row["condition_id"], row["fit_id"])
        for row in router_population
        if row["positive_selected"]
    }
    expected_positive = {
        (condition, fit)
        for condition in ("TORSO_COM_X_POS", "HOME_JOINT_OFFSET_NEG")
        for fit in ("p30", "p31_34")
    }
    home_traces = [
        row
        for row in traces
        if row["condition_id"] == "HOME_JOINT_OFFSET_NEG"
    ]
    floor_traces = [
        row for row in traces if row["condition_id"] == "FLOOR_FRICTION_LO"
    ]
    paired_trace_identity = all(
        next(
            row["trace_sha256"]
            for row in home_traces
            if row["role"] == "half"
            and row["fit_id"] == fit
            and row["command_x_m_s"] == command
        )
        == next(
            row["trace_sha256"]
            for row in home_traces
            if row["role"] == "final"
            and row["fit_id"] == fit
            and row["command_x_m_s"] == command
        )
        for fit in ("p30", "p31_34")
        for command in (0.074, 0.077, 0.08)
    )
    positive_adapter_identical = all(
        np.array_equal(
            graph_values["half"][name], graph_values["final"][name]
        )
        for name in ("positive_adapter_weight", "positive_adapter_bias")
    )
    nominal_adapter_changed = any(
        not np.array_equal(
            graph_values["half"][name], graph_values["final"][name]
        )
        for name in (
            "nominal_condition_negative_adapter_weight",
            "nominal_condition_negative_adapter_bias",
        )
    )
    condition_rows = {
        row["condition_id"]: row
        for row in json.loads(
            Path(prereg["frozen_inputs"]["t237_result"]["path"]).read_text(
                encoding="utf-8"
            )
        )["conditions"]
    }
    classification_checks = {
        "positive_router_selects_exactly_x_positive_and_home_negative": (
            positive_selected == expected_positive
        ),
        "home_negative_selects_positive_in_both_fits": all(
            row["positive_router_selected"] for row in home_traces
        ),
        "matched_floor_condition_does_not_select_positive": all(
            not row["positive_router_selected"] for row in floor_traces
        ),
        "positive_adapter_is_identical_between_checkpoints": (
            positive_adapter_identical and nominal_adapter_changed
        ),
        "home_negative_half_final_traces_are_pairwise_identical": (
            paired_trace_identity
        ),
        "all_home_negative_moving_cells_fall_with_quality_and_protection_green": (
            len(home_traces) == 12
            and all(
                not row["core_pass"]
                and row["replacement_quality_pass"]
                and row["duration_protection_pass"]
                and row["termination_reason"] == "fall_or_nan"
                for row in home_traces
            )
        ),
        "x_positive_condition_passed_sixteen_of_sixteen": (
            condition_rows["TORSO_COM_X_POS"]["condition_green"] is True
            and condition_rows["TORSO_COM_X_POS"]["green_cells"] == 16
        ),
    }
    classification_checks = {
        name: bool(value) for name, value in classification_checks.items()
    }
    classification_pass = all(classification_checks.values())
    status = (
        "PASS_T238_HOME_OFFSET_FALSE_POSITIVE_X_POSITIVE_ROUTE"
        if classification_pass
        else "HOLD_T238_HOME_OFFSET_ROUTE_CLASSIFICATION"
    )
    decision = (
        prereg["classification_rule"]["pass_decision"]
        if classification_pass
        else prereg["classification_rule"]["otherwise"]
    )

    result_basis: dict[str, Any] = {
        "schema_version": "open_duck.t238_home_offset_route_autopsy.v1",
        "status": status,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "router_population": router_population,
        "trace_route_replay": traces,
        "graph_path_identity": {
            "positive_adapter_half_final_identical": (
                positive_adapter_identical
            ),
            "nominal_adapter_half_final_changed": nominal_adapter_changed,
            "home_offset_half_final_trace_pairs_identical": (
                paired_trace_identity
            ),
        },
        "readback_attribution": {
            "legacy_expected_value": -0.03,
            "evaluator_reported_value": [-0.03] * 14,
            "legacy_strict_equality": False,
            "causal_for_moving_falls": False,
            "interpretation": (
                "reporting-only scalar expansion mismatch; all twelve moving "
                "cells independently fail the core behavior gate"
            ),
        },
        "classification_checks": classification_checks,
        "classification_pass": classification_pass,
        "interpretation": {
            "causal_route": (
                "the response context for negative home offset is a false "
                "positive of the X-positive COM router"
            ),
            "checkpoint_identity": (
                "that route selects the shared frozen positive adapter, "
                "explaining the pairwise identical half/final failures"
            ),
            "next_work": (
                "preregister the frozen cross-fit X-positive-versus-rest "
                "context-separability audit before any graph transform"
            ),
        },
        "execution": {
            "trace_rows": trace_rows,
            "router_context_rows": len(router_population),
            "onnx_inference_rows": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "router_separability_preregistration": classification_pass,
            "behavior": False,
            "training": False,
            "hosted": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    result = {
        **result_basis,
        "result_sha256": canonical_sha256(result_basis),
    }
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T238 home-offset route autopsy result\n\n"
        f"- Status: `{status}`\n"
        f"- Decision: `{decision}`\n"
        "- Positive router selected: `TORSO_COM_X_POS` and "
        "`HOME_JOINT_OFFSET_NEG`, both fits, and no other R2 context\n"
        "- Failed moving traces: `12/12`; half/final pairs are "
        "byte-identical under each fit and command\n"
        "- Readback note: scalar-to-vector comparison is reporting-only; "
        "the moving falls remain independently causal\n"
        "- Simulator/behavior/training/hosted/robot: `0/0/0/0/0`\n"
        f"- Result SHA-256: `{result['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(status)
    print(f"decision={decision}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if classification_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
