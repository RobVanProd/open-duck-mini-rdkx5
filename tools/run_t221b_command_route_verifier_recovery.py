#!/usr/bin/env python3
"""Run T221B's read-only command-route verifier recovery."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(ROOT / "tools"))
from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    verify,
)


PREREG = (
    ANALYSIS / "t221b_command_route_verifier_recovery_preregistration.json"
)
RESULT = ANALYSIS / "t221b_command_route_verifier_recovery_result.json"
MARKDOWN = (
    ANALYSIS / "T221B_COMMAND_ROUTE_VERIFIER_RECOVERY_RESULT_20260730.md"
)
OUTPUT_NAMES = ["continuous_actions", "h_out", "previous_action_out"]


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


def read_rows(path: Path, count: int) -> list[dict[str, Any]]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return rows[:count]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T221B result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T221B execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T221B_COMMAND_ROUTE_VERIFIER_RECOVERY"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T221B preregistration changed")
    for name, item in prereg["frozen_inputs"].items():
        verify(item, f"frozen_inputs.{name}")
    source = json.loads(
        Path(prereg["frozen_inputs"]["t221_preregistration"]["path"])
        .read_text(encoding="utf-8")
    )
    source_result = json.loads(
        Path(prereg["frozen_inputs"]["t221_partial_result"]["path"])
        .read_text(encoding="utf-8")
    )
    for index, pair in enumerate(prereg["pairs"]):
        verify(pair["graph"], f"pairs[{index}].graph")
        verify(pair["trace"], f"pairs[{index}].trace")

    recovery = prereg["recovery"]
    endpoint = float(recovery["endpoint_m_s"])
    tolerance = float(recovery["endpoint_absolute_tolerance"])
    external = float(recovery["external_command_m_s"])
    minimum_ratio = float(recovery["minimum_track_ratio"])
    nominal = [
        row
        for row in source["nominal_cells"]
        if math.isclose(
            float(row["command_x_m_s"]),
            endpoint,
            rel_tol=0.0,
            abs_tol=tolerance,
        )
    ]
    targeted = [
        row
        for row in source["targeted_cells"]
        if math.isclose(
            float(row["command_x_m_s"]),
            endpoint,
            rel_tol=0.0,
            abs_tol=tolerance,
        )
    ]

    pair_results = []
    total_inferences = 0
    total_trace_rows = 0
    for pair in prereg["pairs"]:
        rows = read_rows(
            Path(pair["trace"]["path"]),
            int(recovery["trace_rows_per_pair"]),
        )
        ticks = [int(row["tick"]) for row in rows]
        session = make_session(Path(pair["graph"]["path"]))
        context = np.asarray(
            pair["context"]["context"], dtype=np.float32
        ).reshape(1, 64)
        differing_action = 0
        differing_hidden = 0
        maximum_action_delta = 0.0
        all_finite = True
        all_trace_command_exact = True
        for row in rows:
            state = row["policy_state_input"]
            obs = np.asarray(row["obs_state"], dtype=np.float32).reshape(1, 115)
            all_trace_command_exact &= math.isclose(
                float(obs[0, 6]),
                endpoint,
                rel_tol=0.0,
                abs_tol=tolerance,
            )
            outputs = []
            for command in recovery["same_state_commands_m_s"]:
                candidate = obs.copy()
                candidate[0, 6] = np.float32(command)
                outputs.append(
                    session.run(
                        OUTPUT_NAMES,
                        {
                            "obs": candidate,
                            "previous_action": np.asarray(
                                state["previous_action"], dtype=np.float32
                            ),
                            "h_in": np.asarray(
                                state["h_in"], dtype=np.float32
                            ),
                            "calibration_context": context,
                        },
                    )
                )
                total_inferences += 1
            action_delta = float(
                np.max(np.abs(outputs[0][0] - outputs[1][0]))
            )
            maximum_action_delta = max(maximum_action_delta, action_delta)
            differing_action += int(action_delta > 0.0)
            differing_hidden += int(
                not np.array_equal(outputs[0][1], outputs[1][1])
            )
            all_finite &= all(
                np.all(np.isfinite(value))
                for output in outputs
                for value in output
            )
        total_trace_rows += len(rows)
        pair_results.append(
            {
                "checkpoint_id": pair["checkpoint_id"],
                "step": pair["step"],
                "role": pair["role"],
                "fit_id": pair["fit_id"],
                "context_sha256": pair["context"]["context_sha256"],
                "trace_sha256": pair["trace"]["sha256"],
                "rows": len(rows),
                "ticks_contiguous_from_zero": ticks == list(range(len(rows))),
                "all_trace_commands_match_endpoint": bool(
                    all_trace_command_exact
                ),
                "differing_action_rows_077_vs_080": differing_action,
                "differing_hidden_rows_077_vs_080": differing_hidden,
                "maximum_action_delta_077_vs_080": maximum_action_delta,
                "all_outputs_finite": bool(all_finite),
                "provider": session.get_providers()[0],
            }
        )

    nominal_ratios = [
        float(row["behavior"]["mean_local_vx_m_s"]) / external
        for row in nominal
    ]
    targeted_ratios = [
        float(row["behavior"]["mean_local_vx_m_s"]) / external
        for row in targeted
    ]
    retained_route_checks = {
        name: source_result["checks"][name]
        for name in (
            "both_y_negative_contexts_route_nominal_at_both_checkpoints",
            "preserved_t149_cap_present_and_exact",
            "preserved_t149_gate_false_for_y_negative",
            "all_inference_finite_cpu_only",
        )
    }
    checks = {
        "source_t221_identity_exact": (
            source["preregistered_contract_sha256"]
            == prereg["source_t221_contract_sha256"]
            and source_result["result_sha256"]
            == prereg["source_t221_result_sha256"]
        ),
        "exactly_four_nominal_and_targeted_endpoints_selected": (
            len(nominal) == 4 and len(targeted) == 4
        ),
        "all_selected_endpoint_cells_pass": all(
            row["cell_green"] for row in [*nominal, *targeted]
        ),
        "nominal_endpoint_retains_external_x008_ratio": (
            len(nominal_ratios) == 4
            and min(nominal_ratios) >= minimum_ratio
        ),
        "targeted_endpoint_retains_external_x008_ratio": (
            len(targeted_ratios) == 4
            and min(targeted_ratios) >= minimum_ratio
        ),
        "all_four_trace_prefixes_exact_and_contiguous": (
            len(pair_results) == 4
            and all(
                row["rows"] == int(recovery["trace_rows_per_pair"])
                and row["ticks_contiguous_from_zero"]
                and row["all_trace_commands_match_endpoint"]
                for row in pair_results
            )
        ),
        "same_state_command_sensitivity_exercised_every_pair": all(
            row["differing_action_rows_077_vs_080"] > 0
            and row["maximum_action_delta_077_vs_080"] > 0.0
            for row in pair_results
        ),
        "all_recovery_inference_finite_cpu_only": all(
            row["all_outputs_finite"]
            and row["provider"] == "CPUExecutionProvider"
            for row in pair_results
        ),
        "all_t221_route_and_existing_cap_checks_retained": all(
            retained_route_checks.values()
        ),
        "zero_simulator_optimizer_behavior_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t221b_command_route_verifier_recovery_result.v1"
        ),
        "status": (
            "PASS_T221B_COMMAND_ROUTE_VERIFIER_RECOVERY"
            if not failed
            else "HOLD_T221B_COMMAND_ROUTE_VERIFIER_RECOVERY"
        ),
        "decision": (
            "RECOVER_T221_AND_EARN_T222_GLOBAL_X008_TO_X0077_"
            "PLATEAU_CPU_CONTRACT_PREREGISTRATION_ONLY"
            if not failed
            else "CLOSE_GLOBAL_COMMAND_PLATEAU_WITHOUT_BEHAVIOR"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "source_t221_contract_sha256": prereg[
            "source_t221_contract_sha256"
        ],
        "source_t221_result_sha256": prereg["source_t221_result_sha256"],
        "checks": checks,
        "failed_checks": failed,
        "classification": (
            "T221_VERIFIER_ONLY_HOLD_RECOVERED_ON_FROZEN_TRACE_STATES"
            if not failed
            else "T221_COMMAND_ROUTE_ATTRIBUTION_NOT_RECOVERED"
        ),
        "retained_route_checks": retained_route_checks,
        "nominal_x0077_external_x008_ratios": nominal_ratios,
        "targeted_x0077_external_x008_ratios": targeted_ratios,
        "pair_results": pair_results,
        "execution": {
            "saved_trace_rows": total_trace_rows,
            "onnx_inferences": total_inferences,
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
        "# T221B command-route verifier recovery result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Classification: `{value['classification']}`\n"
        f"- Targeted `.077` minimum external-`.080` ratio: "
        f"`{min(targeted_ratios):.9f}`\n"
        "- Same-state command sensitivity: exercised on all four graph/fit "
        "pairs\n"
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
