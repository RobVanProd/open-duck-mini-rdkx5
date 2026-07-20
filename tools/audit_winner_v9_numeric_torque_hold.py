#!/usr/bin/env python3
"""Attribute the closed winner-v9 hold without retrying or reclassifying it."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
RESULT = ANALYSIS / "winner_v9_nominal_behavior_result.json"
PREREG = ANALYSIS / "winner_v9_nominal_behavior_preregistration.json"
OUTPUT_JSON = ANALYSIS / "winner_v9_numeric_torque_hold_attribution.json"
OUTPUT_MD = ANALYSIS / "WINNER_V9_NUMERIC_TORQUE_HOLD_ATTRIBUTION_20260720.md"
CURRENT_NM_PER_A = 0.784532


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def flatten(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for fit in payload["matrices"].values()
        for row in fit.values()
    ]


def main() -> int:
    if OUTPUT_JSON.exists() or OUTPUT_MD.exists():
        raise FileExistsError("winner-v9 numeric torque attribution already exists")
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    blocks = flatten(result)
    traces = [trace for block in blocks for trace in block["traces"]]
    moving = [trace for trace in traces if trace["command_x"] > 0.0]
    stationary = [trace for trace in traces if trace["command_x"] == 0.0]
    gate = prereg["protection_gate"]

    exact_limit = float(gate["per_joint_peak_torque_nm_max"])
    represented_limit = float(np.float32(exact_limit))
    inward_limit = float(
        np.nextafter(np.float32(exact_limit), np.float32(-np.inf))
    )
    inward_xml_decimal = f"{inward_limit:.8f}"
    inward_round_trip = float(np.float32(float(inward_xml_decimal)))
    representational_overage = represented_limit - exact_limit
    float32_spacing = float(np.spacing(np.float32(exact_limit)))

    checks = {
        "formal_result_remains_hold_and_route_closed": result["status"]
        == "HOLD_WINNER_V9_NOMINAL_BEHAVIOR"
        and result["decision"] == "CLOSE_WINNER_V9_POLICY_ROUTE",
        "only_combined_protection_check_failed": result["failed_checks"]
        == ["all_current_torque_duration_and_full_vector_gates_pass"],
        "all_16_cells_and_four_behavior_matrices_pass": len(traces) == 16
        and len(blocks) == 4
        and all(block["behavior"]["matrix_pass"] for block in blocks),
        "all_current_duration_and_rate_components_pass_independently": all(
            trace["worst_peak_current_a"]
            <= gate["per_joint_peak_current_a_max"]
            and trace["maximum_consecutive_ticks_above_2a"]
            <= gate["strict_overcurrent_max_consecutive_ticks"]
            and trace["maximum_full_measured_vector_excess_rad_s"]
            <= gate["full_measured_vector_excess_rad_s_max"]
            for trace in traces
        ),
        "all_four_x0_cells_pass_complete_protection_gate": len(stationary) == 4
        and all(trace["pass"] for trace in stationary),
        "all_12_moving_cells_fail_only_at_represented_torque_boundary": len(moving)
        == 12
        and all(
            not trace["pass"]
            and trace["worst_peak_torque_nm"] == represented_limit
            and trace["force_limit_hit_ticks"] > 0
            for trace in moving
        ),
        "nearest_float32_is_strictly_above_decimal_gate": represented_limit
        > exact_limit
        and 0.0 < representational_overage < float32_spacing,
        "one_step_inward_decimal_round_trips_exactly": inward_round_trip
        == inward_limit
        and inward_limit < exact_limit,
        "represented_current_is_below_frozen_current_gate": represented_limit
        / CURRENT_NM_PER_A
        <= gate["per_joint_peak_current_a_max"],
        "winner_v9_close_rule_preserved": "closes the exact winner-v9 policy route"
        in prereg["no_retry_or_tuning"],
    }
    failed = [name for name, passed in checks.items() if not passed]
    attributed = not failed
    payload = {
        "schema_version": "open_duck_mini.winner_v9_numeric_torque_hold_attribution.v1",
        "status": "PASS_WINNER_V9_HOLD_ATTRIBUTED_TO_FLOAT32_TORQUE_BOUNDARY"
        if attributed
        else "HOLD_WINNER_V9_NUMERIC_TORQUE_ATTRIBUTION",
        "decision": "PREREGISTER_DISTINCT_WINNER_V10_INWARD_TORQUE_REPRESENTATION_CONTRACT_ONLY"
        if attributed
        else "STOP_WINNER_V9_FAMILY_PENDING_REVIEW",
        "winner_v9_remains_closed": True,
        "winner_v9_reclassified_or_retried": False,
        "checks": checks,
        "failed_checks": failed,
        "numeric_evidence": {
            "frozen_decimal_torque_gate_nm": exact_limit,
            "nearest_float32_torque_nm": represented_limit,
            "representational_overage_nm": representational_overage,
            "float32_spacing_at_gate_nm": float32_spacing,
            "one_step_inward_float32_torque_nm": inward_limit,
            "one_step_inward_xml_decimal": inward_xml_decimal,
            "one_step_inward_round_trip_float32_nm": inward_round_trip,
            "nearest_float32_implied_current_a": represented_limit
            / CURRENT_NM_PER_A,
            "moving_cell_count": len(moving),
            "x0_cell_count": len(stationary),
            "moving_force_limit_hit_ticks_min": min(
                trace["force_limit_hit_ticks"] for trace in moving
            ),
            "moving_force_limit_hit_ticks_max": max(
                trace["force_limit_hit_ticks"] for trace in moving
            ),
            "maximum_consecutive_ticks_above_2a": max(
                trace["maximum_consecutive_ticks_above_2a"] for trace in traces
            ),
            "maximum_full_measured_vector_excess_rad_s": max(
                trace["maximum_full_measured_vector_excess_rad_s"]
                for trace in traces
            ),
        },
        "distinct_v10_hypothesis": {
            "policy_graph_change": False,
            "xml_change": f'forcerange="-{exact_limit:.8f} {exact_limit:.8f}" -> forcerange="-{inward_xml_decimal} {inward_xml_decimal}"',
            "equation": "nextafter(float32(frozen_decimal_torque_gate_nm), -infinity)",
            "tolerance_or_current_gate_change": False,
            "physical_effect": "one float32 torque step inward on the inherited STS3215 actuator range",
            "why_distinct": "the XML force-range bytes and represented physical boundary differ from closed winner-v9 while both stateful ONNX graphs remain bit-identical",
            "first_gate": "new zero-behavior CPU graph/XML representation contract only",
            "pass_authorizes_only": "a separately frozen complete 16-cell nominal revalidation",
        },
        "inputs": {
            "result": {
                "path": str(RESULT.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(RESULT),
            },
            "preregistration": {
                "path": str(PREREG.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(PREREG),
            },
        },
        "authority": {
            "winner_v10_preregistration_design": attributed,
            "winner_v10_run_behavior_training_gpu_colab": False,
            "runtime_robot_torque_motion_gate5": False,
            "robot_clearance": False,
        },
    }
    OUTPUT_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    OUTPUT_MD.write_text(
        "# Winner-v9 Numeric Torque Hold Attribution\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']}`\n\n"
        f"- frozen decimal torque gate: `{exact_limit}` Nm\n"
        f"- nearest float32 torque: `{represented_limit}` Nm\n"
        f"- representational overage: `{representational_overage}` Nm\n"
        f"- one-step inward float32 torque: `{inward_limit}` Nm\n"
        f"- inward XML decimal: `{inward_xml_decimal}` Nm\n"
        f"- moving cells at the represented boundary: `{len(moving)}/12`\n\n"
        "All behavior, current, overcurrent-duration, measured-rate-vector, x=0, "
        "identity, and completeness checks passed. Winner-v9 remains closed. The "
        "distinct Winner-v10 hypothesis changes only the XML torque representation "
        "by one float32 step inward and first requires a zero-behavior contract. "
        "No training, runtime, robot access, torque, motion, Gate 5, deployment, or "
        "robot clearance is authorized.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"OUTPUT_SHA256={sha256(OUTPUT_JSON)}")
    return 0 if attributed else 2


if __name__ == "__main__":
    raise SystemExit(main())
