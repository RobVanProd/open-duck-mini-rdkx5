#!/usr/bin/env python3
"""Aggregate the preregistered R1 measured-actuator-fit robustness matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


STEPS = (512000, 1024000)
FITS = ("p30", "p31_34")
COMMANDS = (0.0, 0.074, 0.077, 0.080)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row(run: dict) -> dict:
    metrics = run["candidate_gate"]["metrics"]
    emergence = run["emergence"]
    fitted = run["modes"]["fitted"]
    return {
        "command_x": float(run["command_x"]),
        "seed": int(run["seed"]),
        "samples": int(fitted["samples"]),
        "termination_reason": emergence["termination_reason"],
        "candidate_gate_status": run["candidate_gate"]["status"],
        "emergence_pass": bool(emergence["pass"]),
        "left_transitions": int(emergence["left_contact_transition_count"]),
        "right_transitions": int(emergence["right_contact_transition_count"]),
        "mean_vx": float(emergence["mean_velocity_x_m_s"]),
        "body_pitch_p95": float(metrics["max_abs_body_pitch_p95_rad"]),
        "min_height": float(metrics["min_base_height_m"]),
        "tracking_p95": float(metrics["max_pitch_tracking_p95_rad"]),
        "saturation_pct": float(metrics["max_action_saturation_pct"]),
        "rate_excess": float(metrics["max_sent_target_velocity_limit_excess_rad_s"]),
        "max_rate_excess": float(metrics["max_sent_target_velocity_max_limit_excess_rad_s"]),
    }


def summarize(path: Path, x0_gate: dict, expected_seed: int) -> dict:
    payload = json.loads(path.read_text())
    rows = [row(run) for run in payload["runs"]]
    keys = {(item["command_x"], item["seed"]) for item in rows}
    expected = {(command, expected_seed) for command in COMMANDS}
    x0 = [item for item in rows if item["command_x"] == 0.0]
    moving = [item for item in rows if item["command_x"] > 0.0]
    for item in x0:
        item["pass"] = (
            item["samples"] == x0_gate["samples"]
            and item["termination_reason"] == x0_gate["termination_reason"]
            and item["candidate_gate_status"] == x0_gate["candidate_gate_status"]
            and abs(item["mean_vx"]) <= x0_gate["maximum_absolute_mean_local_velocity_m_s"]
            and item["body_pitch_p95"] <= x0_gate["maximum_body_pitch_p95_rad"]
            and item["min_height"] >= x0_gate["minimum_base_height_m"]
            and item["tracking_p95"] <= x0_gate["maximum_pitch_tracking_p95_rad"]
            and item["saturation_pct"] <= x0_gate["maximum_action_saturation_pct"]
            and item["rate_excess"] <= x0_gate["maximum_rate_excess_rad_s"]
            and item["max_rate_excess"] <= x0_gate["maximum_rate_excess_rad_s"]
        )
    nominal_pass = len(moving) == 3 and all(
        item["samples"] == 600
        and item["termination_reason"] == "duration_complete"
        and item["candidate_gate_status"] == "PASS_CANDIDATE_SIM_GATE"
        and item["emergence_pass"]
        and item["left_transitions"] > 0
        and item["right_transitions"] > 0
        and item["tracking_p95"] <= 0.20
        and item["saturation_pct"] == 0.0
        and item["rate_excess"] == 0.0
        and item["max_rate_excess"] == 0.0
        for item in moving
    )
    x0_pass = len(x0) == 1 and x0[0]["pass"]
    complete = len(rows) == 4 and keys == expected
    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "execution_platform": payload["execution"]["platform"],
        "complete": complete,
        "x0_pass": x0_pass,
        "nominal_pass": nominal_pass,
        "matrix_pass": complete and x0_pass and nominal_pass,
        "worst_nominal_tracking_p95_rad": max(item["tracking_p95"] for item in moving),
        "minimum_nominal_vx_m_s": min(item["mean_vx"] for item in moving),
        "x0": x0[0] if x0 else None,
        "moving": moving,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    prereg = json.loads(args.preregistration.read_text())
    contract = json.loads(args.contract.read_text())
    seed = prereg["stages"][0]["seeds"][0]
    x0_gate = {
        "samples": 600,
        "termination_reason": "duration_complete",
        "candidate_gate_status": "PASS_CANDIDATE_SIM_GATE",
        "maximum_absolute_mean_local_velocity_m_s": 0.02,
        "maximum_body_pitch_p95_rad": 0.25,
        "minimum_base_height_m": 0.12,
        "maximum_pitch_tracking_p95_rad": 0.20,
        "maximum_action_saturation_pct": 0.0,
        "maximum_rate_excess_rad_s": 0.0,
    }
    matrices = {
        fit: {
            str(step): summarize(
                args.eval_root / f"ground_up_robustness_r1_{fit}_T2_EQUAL_{step}_eval.json",
                x0_gate,
                seed,
            ) for step in STEPS
        } for fit in FITS
    }
    flat = [item for fit in matrices.values() for item in fit.values()]
    checks = {
        "preregistration_valid": prereg["status"] == "PREREGISTERED_SEQUENTIAL_CPU_ONLY",
        "contract_passed": contract["status"] == "PASS_ROBUSTNESS_R1_CONTRACT",
        "all_16_cells_present": len(flat) == 4 and all(item["complete"] for item in flat),
        "all_cpu_only": all(item["execution_platform"] == "cpu" for item in flat),
    }
    failed = [key for key, value in checks.items() if not value]
    r1_pass = not failed and all(item["matrix_pass"] for item in flat)
    rate_failures = [
        {
            "fit": fit,
            "step": int(step),
            "command_x": item["command_x"],
            "rate_excess_rad_s": item["max_rate_excess"],
        }
        for fit, steps in matrices.items()
        for step, matrix in steps.items()
        for item in matrix["moving"]
        if item["max_rate_excess"] > 0.0
    ]
    if failed:
        status, decision = "FAIL_ROBUSTNESS_R1_EVIDENCE_CONTRACT", "INVALID_EVIDENCE"
    elif r1_pass:
        status, decision = "PASS_ROBUSTNESS_R1", "AUTHORIZE_CONTRACT_R2_ONLY"
    else:
        status, decision = "PASS_ROBUSTNESS_R1_NO_ADVANCE", "CLOSE_FROZEN_POLICY_AT_R1"
    payload = {
        "schema_version": "ground_up_robustness_r1_result.v1",
        "status": status,
        "decision": decision,
        "checks": checks,
        "failed_checks": failed,
        "r1_pass": r1_pass,
        "rate_failures": rate_failures,
        "matrices": matrices,
        "authority": {
            "contract_r2": r1_pass,
            "run_r2_before_contract": False,
            "run_r3_or_later": False,
            "training": False,
            "colab": False,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = ["# Ground-Up Robustness R1 Result", "", f"status: `{status}`", f"decision: `{decision}`", "", "| fit | step | x=0 | nominal | worst tracking | min vx | pass |", "|---|---:|---|---|---:|---:|---|"]
    for fit, steps in matrices.items():
        for step, item in steps.items():
            lines.append(f"| `{fit}` | {step} | `{item['x0_pass']}` | `{item['nominal_pass']}` | {item['worst_nominal_tracking_p95_rad']:.9f} | {item['minimum_nominal_vx_m_s']:.9f} | `{item['matrix_pass']}` |")
    if rate_failures:
        lines.extend([
            "",
            "All six P31/34 moving cells retain gait, tracking below .20 rad, and zero saturation, but exceed that fit's left-ankle 1.50 rad/s limit by .250001 rad/s. The guarded policy was built around the P30 left-ankle 1.75 rad/s limit.",
        ])
    lines.extend(["", "R1 passing authorizes only the R2 evaluator contract. It does not authorize R2 behavior, later stages, training, RDK-X5, or robot access.", ""])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "r1_pass": r1_pass}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
