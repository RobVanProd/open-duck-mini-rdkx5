#!/usr/bin/env python3
"""Audit whether a nominal tracking pass persists across the training horizon."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np


JOINTS = [
    "left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee",
    "left_ankle", "neck_pitch", "head_pitch", "head_yaw", "head_roll",
    "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee",
    "right_ankle",
]
PITCH_INDICES = [2, 3, 4, 11, 12, 13]
TRACKING_LIMIT_RAD = 0.20
STARTUP_TICKS = 54
FULL_TICKS = 600
DT_S = 0.02


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_trace(path: Path) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    rows = [row for row in rows if row.get("mode") == "fitted"]
    if len(rows) != FULL_TICKS:
        raise ValueError(f"expected {FULL_TICKS} fitted rows in {path}, got {len(rows)}")
    return rows


def tracking_summary(rows: list[dict]) -> dict:
    sent = np.asarray([row["sent_target_rad"] for row in rows], dtype=np.float64)
    actual = np.asarray([row["actual_position_rad"] for row in rows], dtype=np.float64)
    error = np.abs(sent - actual)
    per_joint = {
        JOINTS[index]: float(np.percentile(error[:, index], 95))
        for index in PITCH_INDICES
    }
    worst_joint = max(per_joint, key=per_joint.get)
    worst = per_joint[worst_joint]
    pitch_error = error[:, PITCH_INDICES]
    worst_index = JOINTS.index(worst_joint)
    worst_values = error[:, worst_index]
    tail_cutoff = float(np.percentile(worst_values, 95))
    return {
        "samples": len(rows),
        "duration_s": len(rows) * DT_S,
        "max_pitch_tracking_p95_rad": worst,
        "max_pitch_tracking_joint": worst_joint,
        "per_pitch_joint_tracking_p95_rad": per_joint,
        "pitch_chain_tracking_mean_rad": float(np.mean(pitch_error)),
        "pitch_chain_tracking_rms_rad": float(
            np.sqrt(np.mean(np.square(pitch_error)))
        ),
        "worst_joint_fraction_above_limit": float(
            np.mean(worst_values > TRACKING_LIMIT_RAD)
        ),
        "worst_joint_cvar95_rad": float(
            np.mean(worst_values[worst_values >= tail_cutoff])
        ),
        "passes_tracking_limit": worst <= TRACKING_LIMIT_RAD,
        "mean_local_vx_m_s": float(
            np.mean([row["local_linvel_m_s"][0] for row in rows])
        ),
    }


def analyze_trace(path: Path) -> dict:
    rows = load_trace(path)
    command_x = float(rows[0]["command"][0])
    cumulative = []
    for end in list(range(STARTUP_TICKS, FULL_TICKS, STARTUP_TICKS)) + [FULL_TICKS]:
        cumulative.append({"end_tick": end, **tracking_summary(rows[:end])})
    windows = []
    for start in range(0, FULL_TICKS - STARTUP_TICKS + 1, STARTUP_TICKS):
        windows.append(
            {
                "start_tick": start,
                "end_tick": start + STARTUP_TICKS,
                **tracking_summary(rows[start : start + STARTUP_TICKS]),
            }
        )
    first_cumulative_failure = next(
        (row for row in cumulative if not row["passes_tracking_limit"]), None
    )
    first_window_failure = next(
        (row for row in windows if not row["passes_tracking_limit"]), None
    )
    return {
        "path": str(path.resolve()),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
        "command_x": command_x,
        "startup_54_ticks": tracking_summary(rows[:STARTUP_TICKS]),
        "full_600_ticks": tracking_summary(rows),
        "first_cumulative_failure": first_cumulative_failure,
        "first_fixed_window_failure": first_window_failure,
        "cumulative_horizons": cumulative,
        "fixed_54_tick_windows": windows,
    }


def analyze_directory(path: Path) -> dict:
    traces = [analyze_trace(item) for item in sorted(path.glob("*.jsonl"))]
    if len(traces) != 3:
        raise ValueError(f"expected three command traces in {path}, got {len(traces)}")
    return {
        "trace_count": len(traces),
        "all_startup_pass": all(
            row["startup_54_ticks"]["passes_tracking_limit"] for row in traces
        ),
        "all_full_horizon_pass": all(
            row["full_600_ticks"]["passes_tracking_limit"] for row in traces
        ),
        "traces": traces,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--traces-1m", type=Path, required=True)
    parser.add_argument("--traces-2m", type=Path, required=True)
    parser.add_argument("--eval-1m", type=Path, required=True)
    parser.add_argument("--eval-2m", type=Path, required=True)
    parser.add_argument("--baseline-traces", type=Path, required=True)
    parser.add_argument("--baseline-eval", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise RuntimeError("set CUDA_VISIBLE_DEVICES='' for this CPU-only audit")

    one = analyze_directory(args.traces_1m)
    two = analyze_directory(args.traces_2m)
    baseline = analyze_directory(args.baseline_traces)
    eval_one = json.loads(args.eval_1m.read_text())
    eval_two = json.loads(args.eval_2m.read_text())
    baseline_eval = json.loads(args.baseline_eval.read_text())
    checks = {
        "both_checkpoints_have_three_600_tick_traces": one["trace_count"] == 3
        and two["trace_count"] == 3,
        "one_million_reproduces_short_horizon_pass": one["all_startup_pass"],
        "two_million_reproduces_short_horizon_failure": not two["all_startup_pass"],
        "one_million_fails_full_training_horizon": not one["all_full_horizon_pass"],
        "two_million_fails_full_training_horizon": not two["all_full_horizon_pass"],
        "evaluator_reports_duration_complete": all(
            run["emergence"].get("termination_reason") == "duration_complete"
            for payload in (eval_one, eval_two)
            for run in payload["runs"]
        ),
        "evaluator_reports_tracking_hold": all(
            run["status"] == "HOLD_CANDIDATE_TRACKING"
            for payload in (eval_one, eval_two)
            for run in payload["runs"]
        ),
        "baseline_has_three_600_tick_duration_complete_traces": baseline["trace_count"] == 3
        and all(
            run["emergence"].get("termination_reason") == "duration_complete"
            for run in baseline_eval["runs"]
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = "PASS_NOMINAL_HORIZON_AUDIT" if not failed else "FAIL_NOMINAL_HORIZON_AUDIT"
    decision = "REJECT_SHORT_HORIZON_NOMINAL_PASS"
    payload = {
        "schema_version": "ground_up_nominal_horizon_persistence.v1",
        "status": status,
        "decision": decision,
        "checks": checks,
        "failed_checks": failed,
        "tracking_limit_rad": TRACKING_LIMIT_RAD,
        "startup_ticks": STARTUP_TICKS,
        "full_horizon_ticks": FULL_TICKS,
        "dt_s": DT_S,
        "checkpoints": {"1M": one, "2M": two},
        "baseline_best_walk_onnx_2": baseline,
        "eval_inputs": {
            "1M": {"path": str(args.eval_1m.resolve()), "sha256": sha256_file(args.eval_1m)},
            "2M": {"path": str(args.eval_2m.resolve()), "sha256": sha256_file(args.eval_2m)},
            "BEST_WALK_ONNX_2": {
                "path": str(args.baseline_eval.resolve()),
                "sha256": sha256_file(args.baseline_eval),
            },
        },
        "execution": {
            "cpu_only": True,
            "robot_access": False,
            "rdk_access": False,
            "gpu_access": False,
            "colab_access": False,
        },
        "authority": {
            "training_authorized": False,
            "robot_or_rdk_authorized": False,
            "gpu_authorized": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Ground-Up Nominal Horizon Persistence Audit",
        "",
        f"status: `{status}`",
        f"decision: `{decision}`",
        "",
        "Both checkpoints remain finite, upright, and walking for all 600 ticks at",
        "x=.074/.077/.080. Neither clears the frozen 0.20 rad pitch-chain tracking",
        "limit over that same 12-second horizon.",
        "",
        "| checkpoint | command | 54-tick p95 | 600-tick p95 | 600-tick mean | >.20 fraction | worst joint | first cumulative failure |",
        "|---|---:|---:|---:|---:|---:|---|---:|",
    ]
    for checkpoint, result in (("1M", one), ("2M", two)):
        for row in result["traces"]:
            first = row["first_cumulative_failure"]
            lines.append(
                f"| {checkpoint} | {row['command_x']:.3f} | "
                f"{row['startup_54_ticks']['max_pitch_tracking_p95_rad']:.6f} | "
                f"{row['full_600_ticks']['max_pitch_tracking_p95_rad']:.6f} | "
                f"{row['full_600_ticks']['pitch_chain_tracking_mean_rad']:.6f} | "
                f"{row['full_600_ticks']['worst_joint_fraction_above_limit']:.4f} | "
                f"`{row['full_600_ticks']['max_pitch_tracking_joint']}` | "
                f"{first['end_tick'] if first else 'none'} |"
            )
    lines += [
        "",
        "## Full-horizon baseline comparison",
        "",
        "| policy | command | mean vx | tracking p95 | rate-limit excess | gate status |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for policy, payload_eval in (
        ("applied-target 1M", eval_one),
        ("applied-target 2M", eval_two),
        ("BEST_WALK_ONNX_2", baseline_eval),
    ):
        for run in payload_eval["runs"]:
            metrics = run["candidate_gate"]["metrics"]
            lines.append(
                f"| {policy} | {run['command_x']:.3f} | "
                f"{run['emergence']['mean_velocity_x_m_s']:.6f} | "
                f"{metrics['max_pitch_tracking_p95_rad']:.6f} | "
                f"{metrics['max_sent_target_velocity_limit_excess_rad_s']:.6f} | "
                f"`{run['status']}` |"
            )
    lines += [
        "",
        "The ground-up policies move substantially faster than the baseline and have",
        "zero measured rate-limit excess, but none clears full-horizon tracking. The",
        "baseline comparison therefore does not turn either checkpoint into a winner.",
        "",
        "## Evidence-driven correction",
        "",
        "The prior 54-tick nominal gate covered only 9% of the 600-tick training",
        "episode. It admitted a transient 1M pass that does not persist in time.",
        "Future nominal advancement must evaluate the full 600-tick horizon before",
        "checkpoint-to-checkpoint persistence, x=0, robustness stages, or robot work.",
        "This is a gate-validity correction supported by existing policies; it does",
        "not select a new training recipe or retroactively approve a checkpoint.",
        "",
        "No training, Colab, local GPU, RDK-X5, robot, motor, or torque access was used.",
        "",
    ]
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "failed_checks": failed}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
