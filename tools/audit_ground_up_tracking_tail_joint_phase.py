#!/usr/bin/env python3
"""Audit which joints and reference-period bins set the tracking-tail gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


JOINTS = (
    (2, "left_hip_pitch"),
    (3, "left_knee"),
    (4, "left_ankle"),
    (11, "right_hip_pitch"),
    (12, "right_knee"),
    (13, "right_ankle"),
)
THRESHOLD = 0.20
PERIOD_TICKS = 27


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def trace_summary(path: Path) -> dict:
    records = rows(path)
    sent = np.asarray([row["sent_target_rad"] for row in records], dtype=np.float64)
    actual = np.asarray([row["actual_position_rad"] for row in records], dtype=np.float64)
    indices = np.asarray([index for index, _ in JOINTS])
    error = np.abs(sent[:, indices] - actual[:, indices])
    excess2 = np.square(np.maximum(error - THRESHOLD, 0.0))
    per_joint = {}
    for column, (_, name) in enumerate(JOINTS):
        phase_p95 = [
            float(np.percentile(error[np.arange(len(records)) % PERIOD_TICKS == phase, column], 95))
            for phase in range(PERIOD_TICKS)
        ]
        per_joint[name] = {
            "p95_rad": float(np.percentile(error[:, column], 95)),
            "mean_abs_error_rad": float(np.mean(error[:, column])),
            "fraction_above_0p20": float(np.mean(error[:, column] > THRESHOLD)),
            "raw_tail_cost_mean": float(np.mean(excess2[:, column])),
            "worst_period_bin": int(np.argmax(phase_p95)),
            "worst_period_bin_p95_rad": float(np.max(phase_p95)),
            "period_bin_p95_rad": phase_p95,
        }
    gate_joint = max(per_joint, key=lambda name: per_joint[name]["p95_rad"])
    mean_objective = float(np.mean(excess2))
    max_objective = float(np.mean(np.max(excess2, axis=1)))
    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "rows": len(records),
        "command_x": float(records[0]["command"][0]),
        "seed": int(records[0]["seed"]),
        "gate_joint": gate_joint,
        "gate_tracking_p95_rad": per_joint[gate_joint]["p95_rad"],
        "per_joint": per_joint,
        "current_mean_joint_tail_cost": mean_objective,
        "counterfactual_max_joint_tail_cost": max_objective,
        "max_to_mean_tail_cost_ratio": (
            None if mean_objective == 0.0 else max_objective / mean_objective
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-root", type=Path, required=True)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    groups = {}
    evaluator_errors = []
    total_exceed_rows = {name: 0 for _, name in JOINTS}
    gate_counts = {name: 0 for _, name in JOINTS}
    for directory in sorted(path for path in args.trace_root.iterdir() if path.is_dir()):
        summaries = [trace_summary(path) for path in sorted(directory.glob("*.jsonl"))]
        eval_path = args.eval_root / f"ground_up_tracking_tail_{directory.name}_eval.json"
        evaluation = json.loads(eval_path.read_text())
        eval_cells = {
            (float(run["command_x"]), int(run["seed"])): run for run in evaluation["runs"]
        }
        for item in summaries:
            expected = eval_cells[(item["command_x"], item["seed"])]["candidate_gate"][
                "metrics"
            ]["max_pitch_tracking_p95_rad"]
            evaluator_errors.append(abs(item["gate_tracking_p95_rad"] - expected))
            gate_counts[item["gate_joint"]] += 1
            for name, stats in item["per_joint"].items():
                total_exceed_rows[name] += int(round(stats["fraction_above_0p20"] * item["rows"]))
        mean_ratio = np.mean(
            [
                item["max_to_mean_tail_cost_ratio"]
                for item in summaries
                if item["max_to_mean_tail_cost_ratio"] is not None
            ]
        )
        groups[directory.name] = {
            "eval_path": str(eval_path.resolve()),
            "eval_sha256": sha256(eval_path),
            "traces": summaries,
            "gate_joint_counts": {
                name: sum(item["gate_joint"] == name for item in summaries)
                for _, name in JOINTS
            },
            "mean_max_to_mean_tail_cost_ratio": float(mean_ratio),
        }

    inactive = [name for name, count in total_exceed_rows.items() if count == 0]
    active = [name for name, count in total_exceed_rows.items() if count > 0]
    ratios = [
        trace["max_to_mean_tail_cost_ratio"]
        for group in groups.values()
        for trace in group["traces"]
        if trace["max_to_mean_tail_cost_ratio"] is not None
    ]
    half_gate = groups["T3_FOUR_512000"]["gate_joint_counts"]
    final_gate = groups["T3_FOUR_1024000"]["gate_joint_counts"]
    checks = {
        "all_36_traces_present": sum(len(item["traces"]) for item in groups.values()) == 36,
        "all_traces_have_600_rows": all(
            trace["rows"] == 600 for item in groups.values() for trace in item["traces"]
        ),
        "trace_p95_reproduces_evaluator": max(evaluator_errors) <= 1.0e-12,
        "exceedance_confined_to_left_knee_and_ankle": set(active)
        == {"left_knee", "left_ankle"},
        "four_of_six_objective_joints_never_exceed": len(inactive) == 4,
        "strong_arm_bottleneck_shifts_knee_to_ankle": (
            half_gate["left_knee"] > half_gate["left_ankle"]
            and final_gate["left_ankle"] > final_gate["left_knee"]
        ),
        "max_joint_candidate_is_exact_six_x_rescaling": max(
            abs(ratio - len(JOINTS)) for ratio in ratios
        )
        <= 1.0e-12,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = "PASS_JOINT_PHASE_TAIL_AUDIT" if not failed else "FAIL_JOINT_PHASE_TAIL_AUDIT"
    decision = (
        "REJECT_MAX_JOINT_AS_RESCALED_CLOSED_OBJECTIVE"
        if not failed
        else "NO_CAUSAL_MECHANISM_SELECTED"
    )
    payload = {
        "schema_version": "ground_up_tracking_tail_joint_phase_audit.v1",
        "status": status,
        "decision": decision,
        "checks": checks,
        "failed_checks": failed,
        "threshold_rad": THRESHOLD,
        "reference_period_ticks": PERIOD_TICKS,
        "gate_definition": "max over pitch-chain joints of each joint's 600-tick p95 absolute sent-to-actual error",
        "trained_objective_definition": "mean over pitch-chain joints of squared per-tick exceedance above 0.20 rad",
        "total_exceedance_rows_by_joint": total_exceed_rows,
        "gate_setting_trace_count_by_joint": gate_counts,
        "active_exceedance_joints": active,
        "inactive_exceedance_joints": inactive,
        "max_evaluator_reproduction_error": max(evaluator_errors),
        "max_to_mean_ratio_range": [min(ratios), max(ratios)],
        "groups": groups,
        "interpretation": (
            "The closed objective averages six joints although four never exceed the gate. "
            "As tail pressure rises, the gate-setting joint shifts from left knee to left "
            "ankle. However, only one joint exceeds at any tick, making per-tick maximum "
            "joint cost exactly six times the current six-joint mean on every trace. It is "
            "therefore only an untested stronger scale in the closed formulation, not a "
            "new causal mechanism. No training recipe is selected; the remaining read-only "
            "question is temporal exceedance occupancy versus squared magnitude."
        ),
        "authority": {
            "cpu_diagnostic_only": False,
            "training": False,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Tracking-Tail Joint/Phase Audit",
        "",
        f"status: `{status}`",
        f"decision: `{decision}`",
        "",
        f"active exceedance joints: `{active}`",
        f"inactive exceedance joints: `{inactive}`",
        f"gate-setting trace counts: `{gate_counts}`",
        f"max evaluator reproduction error: `{max(evaluator_errors)}`",
        "",
        "| checkpoint | gate-setting joints | max/mean cost ratio |",
        "|---|---|---:|",
    ]
    for name, group in groups.items():
        nonzero_counts = {key: value for key, value in group["gate_joint_counts"].items() if value}
        lines.append(
            f"| `{name}` | `{nonzero_counts}` | {group['mean_max_to_mean_tail_cost_ratio']:.6f} |"
        )
    lines.extend(["", payload["interpretation"], ""])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "failed": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
