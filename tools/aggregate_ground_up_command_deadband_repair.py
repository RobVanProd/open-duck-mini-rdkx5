#!/usr/bin/env python3
"""Aggregate the preregistered command-deadband repair behavior matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


STEPS = (512000, 1024000)
COMMANDS = (0.0, 0.074, 0.077, 0.080)
MOVING_COMMANDS = COMMANDS[1:]
SEEDS = (100, 101)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def summarize_run(run: dict) -> dict:
    metrics = run["candidate_gate"]["metrics"]
    emergence = run["emergence"]
    fitted = run["modes"]["fitted"]
    return {
        "command_x": float(run["command_x"]),
        "seed": int(run["seed"]),
        "candidate_gate_status": run["candidate_gate"]["status"],
        "samples": int(fitted["samples"]),
        "termination_reason": emergence["termination_reason"],
        "emergence_pass": bool(emergence["pass"]),
        "left_contact_transition_count": int(emergence["left_contact_transition_count"]),
        "right_contact_transition_count": int(emergence["right_contact_transition_count"]),
        "mean_velocity_x_m_s": float(emergence["mean_velocity_x_m_s"]),
        "body_pitch_p95_rad": float(metrics["max_abs_body_pitch_p95_rad"]),
        "min_base_height_m": float(metrics["min_base_height_m"]),
        "tracking_p95_rad": float(metrics["max_pitch_tracking_p95_rad"]),
        "action_saturation_pct": float(metrics["max_action_saturation_pct"]),
        "rate_excess_rad_s": float(metrics["max_sent_target_velocity_limit_excess_rad_s"]),
        "max_rate_excess_rad_s": float(metrics["max_sent_target_velocity_max_limit_excess_rad_s"]),
    }


def checkpoint_summary(path: Path, x0_gate: dict) -> dict:
    payload = json.loads(path.read_text())
    keyed = {(float(run["command_x"]), int(run["seed"])): run for run in payload["runs"]}
    expected = {(command, seed) for command in COMMANDS for seed in SEEDS}
    rows = [summarize_run(keyed[key]) for key in sorted(expected) if key in keyed]
    complete = len(keyed) == 8 and set(keyed) == expected
    x0_rows = [row for row in rows if row["command_x"] == 0.0]
    moving_rows = [row for row in rows if row["command_x"] in MOVING_COMMANDS]

    for row in x0_rows:
        row["pass"] = (
            row["samples"] == x0_gate["samples"]
            and row["termination_reason"] == x0_gate["termination_reason"]
            and row["candidate_gate_status"] == x0_gate["candidate_gate_status"]
            and abs(row["mean_velocity_x_m_s"])
            <= x0_gate["maximum_absolute_mean_local_velocity_m_s"]
            and row["body_pitch_p95_rad"] <= x0_gate["maximum_body_pitch_p95_rad"]
            and row["min_base_height_m"] >= x0_gate["minimum_base_height_m"]
            and row["tracking_p95_rad"] <= x0_gate["maximum_pitch_tracking_p95_rad"]
            and row["action_saturation_pct"] <= x0_gate["maximum_action_saturation_pct"]
            and row["rate_excess_rad_s"] <= x0_gate["maximum_rate_excess_rad_s"]
            and row["max_rate_excess_rad_s"] <= x0_gate["maximum_rate_excess_rad_s"]
        )

    moving_full = len(moving_rows) == 6 and all(
        row["samples"] == 600 and row["termination_reason"] == "duration_complete"
        for row in moving_rows
    )
    moving_bilateral = len(moving_rows) == 6 and all(
        row["emergence_pass"]
        and row["left_contact_transition_count"] > 0
        and row["right_contact_transition_count"] > 0
        for row in moving_rows
    )
    moving_zero_saturation_rate = len(moving_rows) == 6 and all(
        row["action_saturation_pct"] == 0.0
        and row["rate_excess_rad_s"] == 0.0
        and row["max_rate_excess_rad_s"] == 0.0
        for row in moving_rows
    )
    moving_candidate_gate = len(moving_rows) == 6 and all(
        row["candidate_gate_status"] == "PASS_CANDIDATE_SIM_GATE" for row in moving_rows
    )
    worst_tracking = max((row["tracking_p95_rad"] for row in moving_rows), default=float("inf"))
    nominal_pass = (
        moving_full
        and moving_bilateral
        and moving_zero_saturation_rate
        and moving_candidate_gate
        and worst_tracking <= 0.20
    )
    x0_pass = len(x0_rows) == 2 and all(row["pass"] for row in x0_rows)
    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "execution_platform": payload["execution"]["platform"],
        "all_eight_cells_present": complete,
        "x0_pass": x0_pass,
        "nominal_pass": nominal_pass,
        "checkpoint_pass": complete and x0_pass and nominal_pass,
        "worst_nominal_tracking_p95_rad": worst_tracking,
        "minimum_nominal_forward_velocity_m_s": min(
            (row["mean_velocity_x_m_s"] for row in moving_rows), default=float("-inf")
        ),
        "x0_cells": x0_rows,
        "nominal_cells": moving_rows,
        "nominal_checks": {
            "all_six_cells_600_ticks_duration_complete": moving_full,
            "all_walk_with_bilateral_support": moving_bilateral,
            "all_zero_saturation_and_rate_excess": moving_zero_saturation_rate,
            "all_candidate_gates_pass": moving_candidate_gate,
            "worst_tracking_p95_at_most_0p20": worst_tracking <= 0.20,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--transform-contract", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    prereg = json.loads(args.preregistration.read_text())
    transform = json.loads(args.transform_contract.read_text())
    checkpoints = {
        str(step): checkpoint_summary(
            args.eval_root / f"ground_up_command_deadband_repair_T2_EQUAL_{step}_eval.json",
            prereg["x0_gate"],
        )
        for step in STEPS
    }
    checks = {
        "preregistration_status_valid": prereg["status"] == "PREREGISTERED_CPU_ONLY",
        "preregistered_matrix_exact": (
            prereg["behavior_matrix"]["checkpoints"] == list(STEPS)
            and prereg["behavior_matrix"]["commands_x"] == list(COMMANDS)
            and prereg["behavior_matrix"]["seeds"] == list(SEEDS)
            and prereg["behavior_matrix"]["duration_ticks"] == 600
            and prereg["behavior_matrix"]["cells"] == 16
        ),
        "transform_contract_passed": transform["status"]
        == "PASS_COMMAND_DEADBAND_REPAIR_TRANSFORM_CONTRACT",
        "all_16_cells_present": all(item["all_eight_cells_present"] for item in checkpoints.values()),
        "all_16_cells_cpu_only": all(item["execution_platform"] == "cpu" for item in checkpoints.values()),
    }
    failed = [name for name, passed in checks.items() if not passed]
    repair_pass = not failed and all(item["checkpoint_pass"] for item in checkpoints.values())
    if failed:
        status = "FAIL_COMMAND_DEADBAND_REPAIR_EVIDENCE_CONTRACT"
        decision = "INVALID_EVIDENCE"
    elif repair_pass:
        status = "PASS_COMMAND_DEADBAND_REPAIR"
        decision = "ADVANCE_OFFLINE_CANDIDATE_TO_PREREGISTERED_ROBUSTNESS_LADDER"
    else:
        status = "PASS_COMMAND_DEADBAND_REPAIR_NO_ADVANCE"
        decision = "HOLD_AND_CLOSE_COMMAND_DEADBAND_REPAIR"
    payload = {
        "schema_version": "ground_up_command_deadband_repair_result.v1",
        "status": status,
        "decision": decision,
        "checks": checks,
        "failed_checks": failed,
        "repair_pass": repair_pass,
        "preregistration": {"path": str(args.preregistration.resolve()), "sha256": sha256(args.preregistration)},
        "transform_contract": {"path": str(args.transform_contract.resolve()), "sha256": sha256(args.transform_contract)},
        "checkpoints": checkpoints,
        "authority": {
            "preregister_robustness_ladder": repair_pass,
            "run_robustness_without_preregistration": False,
            "training": False,
            "colab": False,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
        "interpretation": (
            "The explicit zero-command branch repairs the out-of-support x=0 failure while "
            "preserving the complete moving-command gate at both selected checkpoints."
            if repair_pass else
            "The explicit zero-command branch does not preserve both x=0 and nominal gates at both checkpoints."
        ),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Command-Deadband Repair Result", "",
        f"status: `{status}`", f"decision: `{decision}`", "",
        "| step | x=0 pass | nominal pass | worst nominal tracking | min nominal vx | checkpoint pass |",
        "|---:|---|---|---:|---:|---|",
    ]
    for step, item in checkpoints.items():
        lines.append(
            f"| {step} | `{item['x0_pass']}` | `{item['nominal_pass']}` | "
            f"{item['worst_nominal_tracking_p95_rad']:.9f} | "
            f"{item['minimum_nominal_forward_velocity_m_s']:.9f} | `{item['checkpoint_pass']}` |"
        )
    lines.extend(["", "## x=0 cells", "", "| step | seed | samples | mean vx | body pitch p95 | tracking p95 | saturation | pass |", "|---:|---:|---:|---:|---:|---:|---:|---|"])
    for step, item in checkpoints.items():
        for row in item["x0_cells"]:
            lines.append(
                f"| {step} | {row['seed']} | {row['samples']} | {row['mean_velocity_x_m_s']:.9f} | "
                f"{row['body_pitch_p95_rad']:.9f} | {row['tracking_p95_rad']:.9f} | "
                f"{row['action_saturation_pct']:.6f}% | `{row['pass']}` |"
            )
    lines.extend(["", payload["interpretation"], "", "Passing authorizes only preregistration of the offline robustness ladder. No training, RDK-X5, or robot access is authorized.", ""])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "repair_pass": repair_pass}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
