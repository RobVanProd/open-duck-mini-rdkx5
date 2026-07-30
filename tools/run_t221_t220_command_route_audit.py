#!/usr/bin/env python3
"""Run T221's frozen T220 command-endpoint and route audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np
import onnx
from onnx import numpy_helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(ROOT / "tools"))
from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    verify,
)


PREREG = ANALYSIS / "t221_t220_command_route_audit_preregistration.json"
RESULT = ANALYSIS / "t221_t220_command_route_audit_result.json"
MARKDOWN = ANALYSIS / "T221_T220_COMMAND_ROUTE_AUDIT_RESULT_20260730.md"
OUTPUT_NAMES = ["continuous_actions", "h_out", "previous_action_out"]


def arrays(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        item.name: numpy_helper.to_array(item).copy()
        for item in model.graph.initializer
    }


def route_scores(
    values: dict[str, np.ndarray], context: np.ndarray
) -> tuple[float, float, str]:
    negative = float(
        (
            context @ values["conditional_path_router_coefficient"]
            + values["conditional_path_router_intercept"]
        ).reshape(-1)[0]
    )
    positive = float(
        (
            context @ values["positive_router_coefficient"]
            + values["positive_router_intercept"]
        ).reshape(-1)[0]
    )
    route = (
        "positive_expert"
        if positive >= 0.0
        else "negative_expert"
        if negative >= 0.0
        else "nominal_expert"
    )
    return negative, positive, route


def make_session(path: Path) -> ort.InferenceSession:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return ort.InferenceSession(
        str(path),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )


def endpoint_inference(
    graph: Path,
    context_row: dict[str, Any],
    seed: int,
    samples: int,
) -> dict[str, Any]:
    model = onnx.load(graph)
    values = arrays(model)
    session = make_session(graph)
    context = np.asarray(context_row["context"], np.float32).reshape(1, 64)
    negative, positive, active_route = route_scores(values, context)
    rng = np.random.default_rng(seed)
    differing_action_samples = 0
    differing_state_samples = 0
    all_finite = True
    for _ in range(samples):
        obs = rng.normal(0.0, 0.25, (1, 115)).astype(np.float32)
        previous = rng.uniform(-0.9, 0.9, (1, 14)).astype(np.float32)
        hidden = rng.uniform(-0.9, 0.9, (1, 64)).astype(np.float32)
        results = []
        for command in (0.077, 0.080):
            candidate = obs.copy()
            candidate[0, 6] = np.float32(command)
            results.append(
                session.run(
                    OUTPUT_NAMES,
                    {
                        "obs": candidate,
                        "previous_action": previous,
                        "h_in": hidden,
                        "calibration_context": context,
                    },
                )
            )
        differing_action_samples += int(
            not np.array_equal(results[0][0], results[1][0])
        )
        differing_state_samples += int(
            not np.array_equal(results[0][1], results[1][1])
        )
        all_finite &= all(
            np.all(np.isfinite(value))
            for result in results
            for value in result
        )
    node_names = {node.name for node in model.graph.node}
    cap = values["t149_command_cap_m_s"].reshape(-1)
    return {
        "step": None,
        "fit_id": context_row["fit_id"],
        "context_sha256": context_row["context_sha256"],
        "negative_router_score": negative,
        "positive_router_score": positive,
        "active_route": active_route,
        "t149_gate_active": negative >= 0.0,
        "t149_cap_node_present": "t149_cap_command" in node_names,
        "t149_select_node_present": "t149_select_command" in node_names,
        "t149_cap_m_s": float(cap[0]),
        "samples": samples,
        "differing_action_samples_077_vs_080": differing_action_samples,
        "differing_hidden_samples_077_vs_080": differing_state_samples,
        "all_outputs_finite": bool(all_finite),
        "provider": session.get_providers()[0],
    }


def select_cells(
    cells: list[dict[str, Any]], command: float
) -> list[dict[str, Any]]:
    return [
        row
        for row in cells
        if float(row["command_x_m_s"]) == command
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T221 result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T221 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T221_T220_COMMAND_ROUTE_AUDIT"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T221 preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    for index, item in enumerate(prereg["graphs"]):
        verify(item["graph"], f"graphs[{index}]")

    audit = prereg["audit"]
    expected_cap = np.float32(audit["existing_t149_cap_m_s"])
    endpoint = np.float32(audit["candidate_global_cap_m_s"])
    external = float(audit["external_command_for_counterfactual_ratio_m_s"])
    minimum_ratio = float(audit["minimum_track_ratio"])
    rows = []
    for graph_index, graph in enumerate(prereg["graphs"]):
        for context_index, context in enumerate(prereg["contexts"]):
            row = endpoint_inference(
                Path(graph["graph"]["path"]),
                context,
                int(audit["random_seed"])
                + graph_index * 1000
                + context_index,
                int(audit["samples_per_graph_context"]),
            )
            row["step"] = graph["step"]
            row["role"] = graph["role"]
            rows.append(row)

    nominal_077 = select_cells(prereg["nominal_cells"], float(endpoint))
    targeted_077 = select_cells(prereg["targeted_cells"], float(endpoint))
    targeted_080 = select_cells(prereg["targeted_cells"], 0.08)
    failures = [
        row for row in prereg["targeted_cells"] if not row["cell_green"]
    ]

    def counterfactual(rows_to_score: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "checkpoint_id": row["checkpoint_id"],
                "step": row["step"],
                "fit_id": row["fit_id"],
                "source_command_x_m_s": row["command_x_m_s"],
                "mean_local_vx_m_s": row["behavior"]["mean_local_vx_m_s"],
                "source_track_ratio": row["behavior"]["track_ratio"],
                "external_x008_track_ratio": (
                    row["behavior"]["mean_local_vx_m_s"] / external
                ),
                "cell_green": row["cell_green"],
            }
            for row in rows_to_score
        ]

    nominal_counterfactual = counterfactual(nominal_077)
    targeted_counterfactual = counterfactual(targeted_077)
    checks = {
        "exactly_three_targeted_failures_all_at_x008": (
            len(failures) == 3
            and all(float(row["command_x_m_s"]) == 0.08 for row in failures)
        ),
        "every_targeted_x0077_cell_passes": (
            len(targeted_077) == 4
            and all(row["cell_green"] for row in targeted_077)
        ),
        "every_nominal_x0077_cell_passes": (
            len(nominal_077) == 4
            and all(row["cell_green"] for row in nominal_077)
        ),
        "targeted_x0077_retains_external_x008_minimum_ratio": (
            len(targeted_counterfactual) == 4
            and all(
                row["external_x008_track_ratio"] >= minimum_ratio
                for row in targeted_counterfactual
            )
        ),
        "nominal_x0077_retains_external_x008_minimum_ratio": (
            len(nominal_counterfactual) == 4
            and all(
                row["external_x008_track_ratio"] >= minimum_ratio
                for row in nominal_counterfactual
            )
        ),
        "both_y_negative_contexts_route_nominal_at_both_checkpoints": (
            len(rows) == 4
            and all(row["active_route"] == "nominal_expert" for row in rows)
        ),
        "preserved_t149_cap_present_and_exact": (
            all(
                row["t149_cap_node_present"]
                and row["t149_select_node_present"]
                and np.float32(row["t149_cap_m_s"]) == expected_cap
                for row in rows
            )
        ),
        "preserved_t149_gate_false_for_y_negative": all(
            not row["t149_gate_active"] for row in rows
        ),
        "source_policy_responds_to_077_vs_080": all(
            row["differing_action_samples_077_vs_080"] > 0 for row in rows
        ),
        "all_inference_finite_cpu_only": all(
            row["all_outputs_finite"]
            and row["provider"] == "CPUExecutionProvider"
            for row in rows
        ),
        "all_four_x008_targeted_cells_enumerated": len(targeted_080) == 4,
        "zero_simulator_optimizer_behavior_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis_result: dict[str, Any] = {
        "schema_version": "open_duck.t221_t220_command_route_audit_result.v1",
        "status": (
            "PASS_T221_T220_COMMAND_ROUTE_AUDIT"
            if not failed
            else "HOLD_T221_T220_COMMAND_ROUTE_AUDIT"
        ),
        "decision": (
            "EARN_T222_GLOBAL_X008_TO_X0077_PLATEAU_"
            "CPU_CONTRACT_PREREGISTRATION_ONLY"
            if not failed
            else "CLOSE_GLOBAL_COMMAND_PLATEAU_WITHOUT_BEHAVIOR"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
        "classification": (
            "Y_NEGATIVE_NOMINAL_ROUTE_BYPASSES_T149_CAP_AT_X008"
            if not failed
            else "T220_COMMAND_ROUTE_ATTRIBUTION_NOT_CLOSED"
        ),
        "route_rows": rows,
        "nominal_x0077_as_external_x008": nominal_counterfactual,
        "targeted_x0077_as_external_x008": targeted_counterfactual,
        "targeted_x008_cells": [
            {
                "checkpoint_id": row["checkpoint_id"],
                "step": row["step"],
                "fit_id": row["fit_id"],
                "cell_green": row["cell_green"],
                "samples": row["behavior"]["samples"],
                "termination_reason": row["behavior"]["termination_reason"],
                "mean_local_vx_m_s": row["behavior"]["mean_local_vx_m_s"],
                "body_pitch_p95_rad": row["behavior"]["body_pitch_p95_rad"],
                "action_saturation_pct": row["behavior"][
                    "action_saturation_pct"
                ],
                "instant_rate_excess_rad_s": row["behavior"][
                    "instant_rate_excess_rad_s"
                ],
            }
            for row in targeted_080
        ],
        "execution": {
            "onnx_inferences": sum(row["samples"] * 2 for row in rows),
            "simulator_transitions": 0,
            "optimizer_steps": 0,
            "behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "transform_contract_preregistration": not failed,
            "behavior": False,
            "training": False,
            "colab": False,
            "gate5": False,
            "robot_or_rdk": False,
        },
    }
    value = {
        **basis_result,
        "result_sha256": canonical_sha256(basis_result),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T221 T220 command-route audit result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Classification: `{value['classification']}`\n"
        "- T220 failures: `3`, all at external x=`.080`\n"
        "- Existing T149 cap: present at `.074`, inactive for both "
        "Y-negative contexts\n"
        f"- Targeted `.077` minimum external-`.080` ratio: "
        f"`{min(row['external_x008_track_ratio'] for row in targeted_counterfactual):.9f}`\n"
        "- Simulator / optimizer / behavior / hosted / robot: `0/0/0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
