#!/usr/bin/env python3
"""Run offline closed-loop candidate gates across multiple seeds.

This helper is for sim-side stability baselines. It does not SSH, deploy,
train, or touch the robot. It repeatedly calls
`tools/eval_policy_with_actuator_bridge.py` with explicit seeds and summarizes
the rollout distribution so a new candidate can be compared against a baseline
instead of a single lucky or unlucky rollout.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]


def parse_int_list(value: str) -> list[int]:
    seeds: list[int] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            step = 1 if end >= start else -1
            seeds.extend(range(start, end + step, step))
        else:
            seeds.append(int(part))
    if not seeds:
        raise argparse.ArgumentTypeError("expected at least one seed")
    deduped: list[int] = []
    seen = set()
    for seed in seeds:
        if seed not in seen:
            seen.add(seed)
            deduped.append(seed)
    return deduped


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, int | float):
        return f"{float(value):.{digits}f}"
    return str(value)


def finite(value: Any) -> bool:
    return isinstance(value, int | float) and not (
        math.isnan(float(value)) or math.isinf(float(value))
    )


def stats(values: Iterable[float]) -> dict[str, float] | None:
    data = sorted(float(value) for value in values if finite(value))
    if not data:
        return None
    return {
        "min": data[0],
        "mean": sum(data) / len(data),
        "p50": percentile(data, 50),
        "p95": percentile(data, 95),
        "max": data[-1],
    }


def percentile(values: list[float], pct: float) -> float:
    if len(values) == 1:
        return values[0]
    k = (len(values) - 1) * pct / 100.0
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return values[lo]
    return values[lo] * (hi - k) + values[hi] * (k - lo)


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def policy_label(path: Path) -> str:
    return path.parent.name if path.name == "candidate.onnx" else path.stem


def parse_policy(value: str) -> tuple[str, Path]:
    if "=" in value:
        label, path = value.split("=", 1)
        label = label.strip()
        path = path.strip()
        if label and path:
            return label, Path(path)
    path = Path(value)
    return policy_label(path), path


def extract_mode(payload: dict[str, Any], mode_name: str) -> dict[str, Any] | None:
    closed = payload.get("closed_loop_sim") or {}
    modes = closed.get("modes") or {}
    mode = modes.get(mode_name)
    if isinstance(mode, dict):
        return mode
    if len(modes) == 1:
        only = next(iter(modes.values()))
        return only if isinstance(only, dict) else None
    return None


def summarize_payload(payload: dict[str, Any], mode_name: str) -> dict[str, Any]:
    closed = payload.get("closed_loop_sim") or {}
    gate = closed.get("candidate_gate") or {}
    metrics = gate.get("metrics") or {}
    mode = extract_mode(payload, mode_name) or {}
    forward = mode.get("forward_motion") or {}
    height = mode.get("base_height_m") or {}
    push_recovery = mode.get("push_recovery") or {}
    foot_clearance = mode.get("foot_clearance") or {}
    feet = foot_clearance.get("feet") or {}
    support = foot_clearance.get("support") or {}
    left_lift = ((feet.get("left") or {}).get("swing_lift_over_stance_m") or {})
    right_lift = ((feet.get("right") or {}).get("swing_lift_over_stance_m") or {})
    left_peak = (feet.get("left") or {}).get("swing_peak_lift_over_stance_m")
    right_peak = (feet.get("right") or {}).get("swing_peak_lift_over_stance_m")
    left_segments = (feet.get("left") or {}).get("swing_segment_count")
    right_segments = (feet.get("right") or {}).get("swing_segment_count")
    segment_counts = [
        value for value in (left_segments, right_segments) if isinstance(value, int)
    ]
    left_rel_x_range = (
        (feet.get("left") or {}).get("swing_segment_rel_x_range_m") or {}
    )
    right_rel_x_range = (
        (feet.get("right") or {}).get("swing_segment_rel_x_range_m") or {}
    )
    left_rel_x_range_p95 = (
        0.0 if left_segments == 0 else left_rel_x_range.get("p95")
    )
    right_rel_x_range_p95 = (
        0.0 if right_segments == 0 else right_rel_x_range.get("p95")
    )
    rel_x_ranges = [
        value
        for value in (left_rel_x_range_p95, right_rel_x_range_p95)
        if finite(value)
    ]
    peaks = [value for value in (left_peak, right_peak) if finite(value)]
    return {
        "overall_status": payload.get("overall_status"),
        "candidate_gate_status": gate.get("status"),
        "samples": mode.get("samples"),
        "termination_reason": mode.get("termination_reason"),
        "elapsed_s": forward.get("elapsed_s"),
        "mean_local_vx_m_s": forward.get("mean_velocity_x_m_s"),
        "track_ratio": forward.get("command_tracking_ratio"),
        "body_pitch_p95_rad": metrics.get("max_abs_body_pitch_p95_rad"),
        "base_height_min_m": height.get("min"),
        "max_pitch_vel_p95_rad_s": metrics.get("max_sent_target_velocity_p95_rad_s"),
        "max_pitch_vel_limit_excess_rad_s": metrics.get(
            "max_sent_target_velocity_limit_excess_rad_s"
        ),
        "max_pitch_vel_max_limit_excess_rad_s": metrics.get(
            "max_sent_target_velocity_max_limit_excess_rad_s"
        ),
        "max_tracking_p95_rad": metrics.get("max_pitch_tracking_p95_rad"),
        "action_saturation_pct": metrics.get("max_action_saturation_pct"),
        "push_event_count": push_recovery.get("event_count"),
        "push_recovered_count": push_recovery.get("recovered_count"),
        "push_success_rate": push_recovery.get("success_rate"),
        "left_swing_lift_p95_m": left_lift.get("p95"),
        "right_swing_lift_p95_m": right_lift.get("p95"),
        "left_swing_peak_lift_m": left_peak,
        "right_swing_peak_lift_m": right_peak,
        "min_swing_peak_lift_m": min(peaks) if peaks else None,
        "left_swing_segment_count": left_segments,
        "right_swing_segment_count": right_segments,
        "min_swing_segment_count": min(segment_counts) if segment_counts else None,
        "left_swing_rel_x_range_p95_m": left_rel_x_range_p95,
        "right_swing_rel_x_range_p95_m": right_rel_x_range_p95,
        "min_swing_rel_x_range_p95_m": min(rel_x_ranges) if rel_x_ranges else None,
        "single_support_pct": support.get("single_support_pct"),
        "double_support_pct": support.get("double_support_pct"),
        "no_contact_pct": support.get("no_contact_pct"),
    }


def apply_optional_terrain_swing_gate(
    status: str | None, summary: dict[str, Any], args: argparse.Namespace
) -> tuple[str | None, dict[str, Any]]:
    checks = []
    thresholds = {
        "min_swing_segments": args.min_swing_segments_per_foot,
        "min_rel_x_range_p95_m": args.min_swing_rel_x_range_p95_m,
        "min_swing_peak_lift_m": args.min_swing_peak_lift_m,
    }
    observed = {
        "min_swing_segments": summary.get("min_swing_segment_count"),
        "min_rel_x_range_p95_m": summary.get("min_swing_rel_x_range_p95_m"),
        "min_swing_peak_lift_m": summary.get("min_swing_peak_lift_m"),
    }
    for name, threshold in thresholds.items():
        if threshold is None:
            continue
        value = observed.get(name)
        if value is None and float(threshold) <= 0.0:
            value = 0.0
        passed = finite(value) and float(value) >= float(threshold)
        checks.append(
            {
                "metric": name,
                "observed": value,
                "threshold": threshold,
                "passed": bool(passed),
            }
        )
    if not checks:
        return status, {"enabled": False, "checks": []}
    gate = {
        "enabled": True,
        "status_before": status,
        "checks": checks,
        "passed": all(item["passed"] for item in checks),
    }
    if status == "PASS_CANDIDATE_SIM_GATE" and not gate["passed"]:
        return "HOLD_CANDIDATE_TERRAIN_SWING", gate
    return status, gate


def run_one(
    args: argparse.Namespace, policy_item: tuple[str, Path], seed: int
) -> dict[str, Any]:
    label, policy = policy_item
    output_dir = Path(args.output_dir) / label / f"seed_{seed:03d}"
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(ROOT / "tools" / "eval_policy_with_actuator_bridge.py"),
        "--mode",
        "closed-loop-sim",
        "--eval-role",
        "candidate",
        "--policy",
        str(policy),
        "--fit-json",
        str(Path(args.fit_json)),
        "--playground-path",
        str(Path(args.playground_path)),
        "--env-python",
        str(Path(args.env_python)),
        "--command-x",
        str(args.command_x),
        "--task",
        str(args.task),
        "--duration",
        str(args.duration),
        "--seed",
        str(seed),
        "--bridge-mode",
        args.bridge_mode,
        "--policy-action-gain",
        str(args.policy_action_gain),
        "--jax-platform",
        args.jax_platform,
        "--sim-preflight-timeout-s",
        str(args.sim_preflight_timeout_s),
        "--closed-loop-timeout-s",
        str(args.closed_loop_timeout_s),
        "--output-dir",
        str(output_dir),
    ]
    if args.policy_action_rate_limit_rad_s is not None:
        command.extend(
            [
                "--policy-action-rate-limit-rad-s",
                str(args.policy_action_rate_limit_rad_s),
                "--policy-action-rate-limit-joint-indices",
                str(args.policy_action_rate_limit_joint_indices),
            ]
        )
        if args.policy_action_rate_limit_values:
            command.extend([
                "--policy-action-rate-limit-values",
                str(args.policy_action_rate_limit_values),
            ])
    if args.policy_phase_action_delta_json:
        command.extend(
            [
                "--policy-phase-action-delta-json",
                str(Path(args.policy_phase_action_delta_json)),
                "--policy-phase-action-delta-scale",
                str(args.policy_phase_action_delta_scale),
                "--policy-phase-action-delta-min-command-x",
                str(args.policy_phase_action_delta_min_command_x),
            ]
        )
    if seed in set(args.trace_seeds):
        command.extend(["--trace-jsonl", str(output_dir / "trace.jsonl")])
        if args.trace_full_obs:
            command.append("--trace-full-obs")
    if args.reward_overrides_json:
        command.extend(["--reward-overrides-json", str(Path(args.reward_overrides_json))])
    if args.reward_overrides_phase:
        command.extend(["--reward-overrides-phase", str(args.reward_overrides_phase)])
    if args.policy_obs_input_name:
        command.extend(["--policy-obs-input-name", str(args.policy_obs_input_name)])
    if args.policy_action_output_name:
        command.extend(["--policy-action-output-name", str(args.policy_action_output_name)])
    if args.policy_state_input_names:
        command.extend(["--policy-state-input-names", str(args.policy_state_input_names)])
    if args.policy_state_output_names:
        command.extend(["--policy-state-output-names", str(args.policy_state_output_names)])
    if args.eval_push_enable:
        command.append("--eval-push-enable")
    if args.eval_push_interval_min_s is not None:
        command.extend(["--eval-push-interval-min-s", str(args.eval_push_interval_min_s)])
    if args.eval_push_interval_max_s is not None:
        command.extend(["--eval-push-interval-max-s", str(args.eval_push_interval_max_s)])
    if args.eval_push_magnitude_min is not None:
        command.extend(["--eval-push-magnitude-min", str(args.eval_push_magnitude_min)])
    if args.eval_push_magnitude_max is not None:
        command.extend(["--eval-push-magnitude-max", str(args.eval_push_magnitude_max)])
    command.extend(["--push-recovery-window-s", str(args.push_recovery_window_s)])
    command.extend(
        [
            "--push-recovery-max-abs-pitch-rad",
            str(args.push_recovery_max_abs_pitch_rad),
        ]
    )
    command.extend(
        [
            "--push-recovery-min-base-height-m",
            str(args.push_recovery_min_base_height_m),
        ]
    )
    if args.terrain_hfield_z_scale is not None:
        command.extend(["--terrain-hfield-z-scale", str(args.terrain_hfield_z_scale)])
    if args.reset_settle_ticks:
        command.extend(["--reset-settle-ticks", str(args.reset_settle_ticks)])
    if args.reset_mode != "playground":
        command.extend(["--reset-mode", args.reset_mode])
    if args.bridge_reset_align_joint_indices:
        command.extend(
            [
                "--bridge-reset-align-joint-indices",
                args.bridge_reset_align_joint_indices,
            ]
        )
    result: dict[str, Any] = {
        "policy": str(policy),
        "policy_label": label,
        "seed": seed,
        "output_dir": str(output_dir),
        "command": command,
        "command_shell": shell_join(command),
    }
    if not args.run:
        result["status"] = "DRY_RUN"
        return result
    timeout_s = args.closed_loop_timeout_s + 120
    print(
        f"SEED_SWEEP_START policy={label} seed={seed} timeout_s={timeout_s} "
        f"output_dir={output_dir}",
        flush=True,
    )
    proc = subprocess.Popen(
        command,
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    try:
        stdout, _ = proc.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            stdout, _ = proc.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, _ = proc.communicate()
        result["returncode"] = proc.returncode
        result["status"] = "HOLD_SEED_TIMEOUT"
        result["timeout_s"] = timeout_s
        result["stdout_tail"] = (stdout or "")[-12000:]
        print(
            f"SEED_SWEEP_DONE policy={label} seed={seed} "
            f"status={result['status']} returncode={result.get('returncode')}",
            flush=True,
        )
        return result
    result["returncode"] = proc.returncode
    result["stdout_tail"] = (stdout or "")[-12000:]
    json_path = output_dir / "closed_loop_actuator_bridge_eval.json"
    result["result_json"] = str(json_path)
    if not json_path.exists():
        result["status"] = "HOLD_NO_RESULT_JSON"
        print(
            f"SEED_SWEEP_DONE policy={label} seed={seed} "
            f"status={result['status']} returncode={result.get('returncode')}",
            flush=True,
        )
        return result
    try:
        payload = json.loads(json_path.read_text())
    except json.JSONDecodeError as exc:
        result["status"] = "HOLD_BAD_RESULT_JSON"
        result["error"] = str(exc)
        print(
            f"SEED_SWEEP_DONE policy={label} seed={seed} "
            f"status={result['status']} returncode={result.get('returncode')}",
            flush=True,
        )
        return result
    result["summary"] = summarize_payload(payload, args.mode_name)
    status, terrain_swing_gate = apply_optional_terrain_swing_gate(
        payload.get("overall_status"), result["summary"], args
    )
    result["status"] = status
    result["terrain_swing_gate"] = terrain_swing_gate
    print(
        f"SEED_SWEEP_DONE policy={label} seed={seed} "
        f"status={result['status']} returncode={result.get('returncode')}",
        flush=True,
    )
    return result


def grouped(results: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        out.setdefault(result["policy_label"], []).append(result)
    return out


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summaries = [row.get("summary") or {} for row in rows]
    falls = [
        item for item in summaries if item.get("termination_reason") != "duration_complete"
    ]
    return {
        "runs": len(rows),
        "fall_count": len(falls),
        "duration_complete_count": len(rows) - len(falls),
        "samples": stats(item.get("samples") for item in summaries),
        "track_ratio": stats(item.get("track_ratio") for item in summaries),
        "mean_local_vx_m_s": stats(item.get("mean_local_vx_m_s") for item in summaries),
        "body_pitch_p95_rad": stats(item.get("body_pitch_p95_rad") for item in summaries),
        "base_height_min_m": stats(item.get("base_height_min_m") for item in summaries),
        "max_pitch_vel_p95_rad_s": stats(
            item.get("max_pitch_vel_p95_rad_s") for item in summaries
        ),
        "max_pitch_vel_limit_excess_rad_s": stats(
            item.get("max_pitch_vel_limit_excess_rad_s") for item in summaries
        ),
        "max_pitch_vel_max_limit_excess_rad_s": stats(
            item.get("max_pitch_vel_max_limit_excess_rad_s") for item in summaries
        ),
        "max_tracking_p95_rad": stats(item.get("max_tracking_p95_rad") for item in summaries),
        "push_event_count": stats(item.get("push_event_count") for item in summaries),
        "push_success_rate": stats(item.get("push_success_rate") for item in summaries),
        "left_swing_lift_p95_m": stats(
            item.get("left_swing_lift_p95_m") for item in summaries
        ),
        "right_swing_lift_p95_m": stats(
            item.get("right_swing_lift_p95_m") for item in summaries
        ),
        "min_swing_peak_lift_m": stats(
            item.get("min_swing_peak_lift_m") for item in summaries
        ),
        "min_swing_segment_count": stats(
            item.get("min_swing_segment_count") for item in summaries
        ),
        "min_swing_rel_x_range_p95_m": stats(
            item.get("min_swing_rel_x_range_p95_m") for item in summaries
        ),
        "single_support_pct": stats(item.get("single_support_pct") for item in summaries),
        "double_support_pct": stats(item.get("double_support_pct") for item in summaries),
    }


def build_report(results: list[dict[str, Any]], args: argparse.Namespace) -> str:
    lines = [
        "# Candidate Seed Sweep",
        "",
        "Offline multi-seed closed-loop candidate gate. This does not SSH, deploy,",
        "train, or touch the robot.",
        "",
        f"command_x: `{args.command_x}`",
        f"task: `{args.task}`",
        f"bridge_mode: `{args.bridge_mode}`",
        f"policy_action_gain: `{args.policy_action_gain}`",
        f"reward_overrides_json: `{args.reward_overrides_json or 'None'}`",
        f"reward_overrides_phase: `{args.reward_overrides_phase or 'None'}`",
        f"duration_s: `{args.duration}`",
        f"seeds: `{args.seeds}`",
        f"eval_push_enable: `{args.eval_push_enable}`",
        f"eval_push_interval_s: `{args.eval_push_interval_min_s}`-`{args.eval_push_interval_max_s}`",
        f"eval_push_magnitude: `{args.eval_push_magnitude_min}`-`{args.eval_push_magnitude_max}`",
        f"push_recovery_window_s: `{args.push_recovery_window_s}`",
        f"terrain_hfield_z_scale: `{args.terrain_hfield_z_scale}`",
        f"reset_settle_ticks: `{args.reset_settle_ticks}`",
        f"reset_mode: `{args.reset_mode}`",
        f"min_swing_segments_per_foot: `{args.min_swing_segments_per_foot}`",
        f"min_swing_rel_x_range_p95_m: `{args.min_swing_rel_x_range_p95_m}`",
        f"min_swing_peak_lift_m: `{args.min_swing_peak_lift_m}`",
        f"trace_seeds: `{args.trace_seeds}`",
        f"trace_full_obs: `{args.trace_full_obs}`",
        f"run: `{args.run}`",
        "",
        "## Per-Seed Results",
        "",
        "| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | p95_vel_excess | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support | push_events | push_success |",
        "|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for result in results:
        summary = result.get("summary") or {}
        lines.append(
            f"| `{result.get('policy_label')}` | {result.get('seed')} | "
            f"`{result.get('status')}` | {fmt(summary.get('samples'), 0)} | "
            f"`{summary.get('termination_reason')}` | "
            f"{fmt(summary.get('mean_local_vx_m_s'))} | "
            f"{fmt(summary.get('track_ratio'))} | "
            f"{fmt(summary.get('body_pitch_p95_rad'))} | "
            f"{fmt(summary.get('base_height_min_m'))} | "
            f"{fmt(summary.get('max_pitch_vel_p95_rad_s'))} | "
            f"{fmt(summary.get('max_pitch_vel_limit_excess_rad_s'))} | "
            f"{fmt(summary.get('max_pitch_vel_max_limit_excess_rad_s'))} | "
            f"{fmt(summary.get('max_tracking_p95_rad'))} | "
            f"{fmt(summary.get('min_swing_peak_lift_m'))} | "
            f"{fmt(summary.get('min_swing_segment_count'), 0)} | "
            f"{fmt(summary.get('min_swing_rel_x_range_p95_m'))} | "
            f"{fmt(summary.get('single_support_pct'))} | "
            f"{fmt(summary.get('double_support_pct'))} | "
            f"{fmt(summary.get('push_event_count'), 0)} | "
            f"{fmt(summary.get('push_success_rate'))} |"
        )
    lines.extend(["", "## Distribution Summary", ""])
    lines.append(
        "| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean | p95_vel_excess_mean | max_vel_excess_mean | min_swing_peak_mean | min_swing_segments_mean | min_rel_x_range_p95_mean | single_support_mean | double_support_mean | push_events_mean | push_success_mean |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for label, rows in grouped(results).items():
        agg = aggregate(rows)
        sample_stats = agg.get("samples") or {}
        lines.append(
            f"| `{label}` | {agg['runs']} | {agg['fall_count']} | "
            f"{agg['duration_complete_count']} | {fmt(sample_stats.get('mean'))} | "
            f"{fmt(sample_stats.get('min'), 0)} | {fmt(sample_stats.get('max'), 0)} | "
            f"{fmt((agg.get('track_ratio') or {}).get('mean'))} | "
            f"{fmt((agg.get('mean_local_vx_m_s') or {}).get('mean'))} | "
            f"{fmt((agg.get('body_pitch_p95_rad') or {}).get('mean'))} | "
            f"{fmt((agg.get('base_height_min_m') or {}).get('mean'))} | "
            f"{fmt((agg.get('max_pitch_vel_limit_excess_rad_s') or {}).get('mean'))} | "
            f"{fmt((agg.get('max_pitch_vel_max_limit_excess_rad_s') or {}).get('mean'))} | "
            f"{fmt((agg.get('min_swing_peak_lift_m') or {}).get('mean'))} | "
            f"{fmt((agg.get('min_swing_segment_count') or {}).get('mean'))} | "
            f"{fmt((agg.get('min_swing_rel_x_range_p95_m') or {}).get('mean'))} | "
            f"{fmt((agg.get('single_support_pct') or {}).get('mean'))} | "
            f"{fmt((agg.get('double_support_pct') or {}).get('mean'))} | "
            f"{fmt((agg.get('push_event_count') or {}).get('mean'))} | "
            f"{fmt((agg.get('push_success_rate') or {}).get('mean'))} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Treat this as a stability distribution, not a deployability approval.",
            "- A candidate still needs the standard full-duration x=0.0 and x=0.08",
            "  gates reviewed before any robot-side validation.",
            "- If fall samples vary widely across seeds, grade later recipes by",
            "  distribution shift, not by a single lucky rollout.",
        ]
    )
    return "\n".join(lines).rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run offline candidate gates across multiple explicit seeds."
    )
    parser.add_argument(
        "--policies",
        nargs="+",
        required=True,
        help="ONNX policy paths, optionally as label=/path/to/policy.onnx",
    )
    parser.add_argument("--seeds", type=parse_int_list, default=parse_int_list("0-7"))
    parser.add_argument("--fit-json", default="outputs/analysis/actuator_response_fit_corrected_knee.json")
    parser.add_argument("--playground-path", default="../Open_Duck_Playground")
    parser.add_argument("--env-python", default="../envs/open-duck-playground/bin/python")
    parser.add_argument("--command-x", type=float, default=0.08)
    parser.add_argument("--task", default="flat_terrain")
    parser.add_argument("--duration", type=float, default=15.0)
    parser.add_argument("--bridge-mode", default="fitted")
    parser.add_argument("--mode-name", default="fitted")
    parser.add_argument(
        "--policy-action-gain",
        type=float,
        default=1.0,
        help=(
            "Eval-only multiplier passed through to "
            "eval_policy_with_actuator_bridge.py. Default 1.0 preserves the "
            "policy exactly."
        ),
    )
    parser.add_argument(
        "--policy-action-rate-limit-rad-s",
        type=float,
        default=None,
        help="Eval-only temporal policy-action rate bound; omitted by default.",
    )
    parser.add_argument("--policy-phase-action-delta-json", default=None)
    parser.add_argument("--policy-phase-action-delta-scale", type=float, default=1.0)
    parser.add_argument(
        "--policy-phase-action-delta-min-command-x", type=float, default=0.02
    )
    parser.add_argument(
        "--policy-action-rate-limit-joint-indices",
        default="2,3,4,11,12,13",
    )
    parser.add_argument("--policy-action-rate-limit-values", default=None)
    parser.add_argument("--jax-platform", default="cpu")
    parser.add_argument("--trace-seeds", type=parse_int_list, default=[])
    parser.add_argument(
        "--trace-full-obs",
        action="store_true",
        help="When tracing selected seeds, include full obs_state in JSONL for DAgger relabeling.",
    )
    parser.add_argument(
        "--reward-overrides-json",
        default=None,
        help=(
            "Optional staged-curriculum JSON whose phase reward config should be "
            "replayed by eval_policy_with_actuator_bridge.py."
        ),
    )
    parser.add_argument(
        "--reward-overrides-phase",
        default=None,
        help="Phase name to select from --reward-overrides-json.",
    )
    parser.add_argument(
        "--policy-obs-input-name",
        default=None,
        help="Optional ONNX observation input name for stateful/recurrent policies.",
    )
    parser.add_argument(
        "--policy-action-output-name",
        default=None,
        help="Optional ONNX action output name for stateful/recurrent policies.",
    )
    parser.add_argument(
        "--policy-state-input-names",
        default=None,
        help="Comma-separated ONNX hidden-state input names for recurrent policies.",
    )
    parser.add_argument(
        "--policy-state-output-names",
        default=None,
        help="Comma-separated ONNX hidden-state output names for recurrent policies.",
    )
    parser.add_argument(
        "--eval-push-enable",
        action="store_true",
        help="Enable push perturbations in each closed-loop seed eval.",
    )
    parser.add_argument("--eval-push-interval-min-s", type=float, default=None)
    parser.add_argument("--eval-push-interval-max-s", type=float, default=None)
    parser.add_argument("--eval-push-magnitude-min", type=float, default=None)
    parser.add_argument("--eval-push-magnitude-max", type=float, default=None)
    parser.add_argument("--push-recovery-window-s", type=float, default=0.5)
    parser.add_argument("--push-recovery-max-abs-pitch-rad", type=float, default=0.8)
    parser.add_argument("--push-recovery-min-base-height-m", type=float, default=0.08)
    parser.add_argument(
        "--terrain-hfield-z-scale",
        type=float,
        default=None,
        help="Eval-only override for hfield vertical scale in terrain XMLs.",
    )
    parser.add_argument(
        "--reset-settle-ticks",
        type=int,
        default=0,
        help=(
            "Eval-only diagnostic passed through to closed-loop eval. Default "
            "0 preserves canonical gates."
        ),
    )
    parser.add_argument(
        "--reset-mode",
        choices=["playground", "home-support"],
        default="playground",
        help=(
            "Eval-only diagnostic passed through to closed-loop eval. Default "
            "'playground' preserves canonical randomized reset behavior."
        ),
    )
    parser.add_argument(
        "--bridge-reset-align-joint-indices",
        default="",
        help=(
            "Default-off eval-only diagnostic passed through to closed-loop eval."
        ),
    )
    parser.add_argument(
        "--min-swing-segments-per-foot",
        type=int,
        default=None,
        help=(
            "Optional terrain hard gate: require at least this many swing "
            "segments on each foot before preserving PASS_CANDIDATE_SIM_GATE."
        ),
    )
    parser.add_argument(
        "--min-swing-rel-x-range-p95-m",
        type=float,
        default=None,
        help=(
            "Optional terrain hard gate: require per-foot p95 swing relative-x "
            "range to meet this threshold before preserving PASS_CANDIDATE_SIM_GATE."
        ),
    )
    parser.add_argument(
        "--min-swing-peak-lift-m",
        type=float,
        default=None,
        help=(
            "Optional terrain hard gate: require each foot's peak swing lift "
            "over stance to meet this threshold before preserving PASS_CANDIDATE_SIM_GATE."
        ),
    )
    parser.add_argument("--sim-preflight-timeout-s", type=int, default=600)
    parser.add_argument("--closed-loop-timeout-s", type=int, default=1800)
    parser.add_argument("--output-dir", default="outputs/analysis/candidate_seed_sweep")
    parser.add_argument("--output-md", default=None)
    parser.add_argument("--output-json", default=None)
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()

    policies = [parse_policy(value) for value in args.policies]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    partial_json = output_dir / "candidate_seed_sweep.partial.json"
    for policy in policies:
        for seed in args.seeds:
            result = run_one(args, policy, seed)
            results.append(result)
            partial_payload = {
                "config": {
                    "policies": [str(path) for _, path in policies],
                    "policy_labels": [label for label, _ in policies],
                    "seeds": args.seeds,
                    "command_x": args.command_x,
                    "task": args.task,
                    "duration_s": args.duration,
                    "bridge_mode": args.bridge_mode,
                    "policy_action_gain": args.policy_action_gain,
                    "reward_overrides_json": args.reward_overrides_json,
                    "reward_overrides_phase": args.reward_overrides_phase,
                    "policy_obs_input_name": args.policy_obs_input_name,
                    "policy_action_output_name": args.policy_action_output_name,
                    "policy_state_input_names": args.policy_state_input_names,
                    "policy_state_output_names": args.policy_state_output_names,
                    "eval_push_enable": args.eval_push_enable,
                    "eval_push_interval_min_s": args.eval_push_interval_min_s,
                    "eval_push_interval_max_s": args.eval_push_interval_max_s,
                    "eval_push_magnitude_min": args.eval_push_magnitude_min,
                    "eval_push_magnitude_max": args.eval_push_magnitude_max,
                    "push_recovery_window_s": args.push_recovery_window_s,
                    "push_recovery_max_abs_pitch_rad": (
                        args.push_recovery_max_abs_pitch_rad
                    ),
                    "push_recovery_min_base_height_m": (
                        args.push_recovery_min_base_height_m
                    ),
                    "terrain_hfield_z_scale": args.terrain_hfield_z_scale,
                    "reset_settle_ticks": args.reset_settle_ticks,
                    "reset_mode": args.reset_mode,
                    "bridge_reset_align_joint_indices": (
                        args.bridge_reset_align_joint_indices
                    ),
                    "min_swing_segments_per_foot": args.min_swing_segments_per_foot,
                    "min_swing_rel_x_range_p95_m": (
                        args.min_swing_rel_x_range_p95_m
                    ),
                    "min_swing_peak_lift_m": args.min_swing_peak_lift_m,
                    "jax_platform": args.jax_platform,
                    "run": args.run,
                    "trace_seeds": args.trace_seeds,
                    "trace_full_obs": args.trace_full_obs,
                },
                "partial": True,
                "results": results,
            }
            partial_json.write_text(json.dumps(partial_payload, indent=2) + "\n")
    payload = {
        "config": {
            "policies": [str(path) for _, path in policies],
            "policy_labels": [label for label, _ in policies],
            "seeds": args.seeds,
            "command_x": args.command_x,
            "task": args.task,
            "duration_s": args.duration,
            "bridge_mode": args.bridge_mode,
            "policy_action_gain": args.policy_action_gain,
            "reward_overrides_json": args.reward_overrides_json,
            "reward_overrides_phase": args.reward_overrides_phase,
            "policy_obs_input_name": args.policy_obs_input_name,
            "policy_action_output_name": args.policy_action_output_name,
            "policy_state_input_names": args.policy_state_input_names,
            "policy_state_output_names": args.policy_state_output_names,
            "eval_push_enable": args.eval_push_enable,
            "eval_push_interval_min_s": args.eval_push_interval_min_s,
            "eval_push_interval_max_s": args.eval_push_interval_max_s,
            "eval_push_magnitude_min": args.eval_push_magnitude_min,
            "eval_push_magnitude_max": args.eval_push_magnitude_max,
            "push_recovery_window_s": args.push_recovery_window_s,
            "push_recovery_max_abs_pitch_rad": args.push_recovery_max_abs_pitch_rad,
            "push_recovery_min_base_height_m": args.push_recovery_min_base_height_m,
            "terrain_hfield_z_scale": args.terrain_hfield_z_scale,
            "reset_settle_ticks": args.reset_settle_ticks,
            "reset_mode": args.reset_mode,
            "bridge_reset_align_joint_indices": (
                args.bridge_reset_align_joint_indices
            ),
            "min_swing_segments_per_foot": args.min_swing_segments_per_foot,
            "min_swing_rel_x_range_p95_m": args.min_swing_rel_x_range_p95_m,
            "min_swing_peak_lift_m": args.min_swing_peak_lift_m,
            "jax_platform": args.jax_platform,
            "run": args.run,
            "trace_seeds": args.trace_seeds,
            "trace_full_obs": args.trace_full_obs,
        },
        "results": results,
        "aggregate": {
            label: aggregate(rows) for label, rows in grouped(results).items()
        },
    }
    report = build_report(results, args)
    output_md = Path(args.output_md) if args.output_md else output_dir / "CANDIDATE_SEED_SWEEP.md"
    output_json = Path(args.output_json) if args.output_json else output_dir / "candidate_seed_sweep.json"
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(report + "\n")
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
