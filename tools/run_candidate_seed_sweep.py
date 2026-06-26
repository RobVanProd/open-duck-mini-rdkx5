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
        "max_tracking_p95_rad": metrics.get("max_pitch_tracking_p95_rad"),
        "action_saturation_pct": metrics.get("max_action_saturation_pct"),
    }


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
        "--jax-platform",
        args.jax_platform,
        "--sim-preflight-timeout-s",
        str(args.sim_preflight_timeout_s),
        "--closed-loop-timeout-s",
        str(args.closed_loop_timeout_s),
        "--output-dir",
        str(output_dir),
    ]
    if seed in set(args.trace_seeds):
        command.extend(["--trace-jsonl", str(output_dir / "trace.jsonl")])
    if args.reward_overrides_json:
        command.extend(["--reward-overrides-json", str(Path(args.reward_overrides_json))])
    if args.reward_overrides_phase:
        command.extend(["--reward-overrides-phase", str(args.reward_overrides_phase)])
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
    result["status"] = payload.get("overall_status")
    result["summary"] = summarize_payload(payload, args.mode_name)
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
        "max_tracking_p95_rad": stats(item.get("max_tracking_p95_rad") for item in summaries),
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
        f"reward_overrides_json: `{args.reward_overrides_json or 'None'}`",
        f"reward_overrides_phase: `{args.reward_overrides_phase or 'None'}`",
        f"duration_s: `{args.duration}`",
        f"seeds: `{args.seeds}`",
        f"run: `{args.run}`",
        "",
        "## Per-Seed Results",
        "",
        "| policy | seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 |",
        "|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|",
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
            f"{fmt(summary.get('max_tracking_p95_rad'))} |"
        )
    lines.extend(["", "## Distribution Summary", ""])
    lines.append(
        "| policy | runs | falls | duration_complete | samples_mean | samples_min | samples_max | track_ratio_mean | vx_mean | body_pitch_p95_mean | base_height_min_mean |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
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
            f"{fmt((agg.get('base_height_min_m') or {}).get('mean'))} |"
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
    parser.add_argument("--fit-json", default="outputs/analysis/actuator_response_fit.json")
    parser.add_argument("--playground-path", default="../Open_Duck_Playground")
    parser.add_argument("--env-python", default="../envs/open-duck-playground/bin/python")
    parser.add_argument("--command-x", type=float, default=0.08)
    parser.add_argument("--task", default="flat_terrain")
    parser.add_argument("--duration", type=float, default=15.0)
    parser.add_argument("--bridge-mode", default="fitted")
    parser.add_argument("--mode-name", default="fitted")
    parser.add_argument("--jax-platform", default="cpu")
    parser.add_argument("--trace-seeds", type=parse_int_list, default=[])
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
                    "reward_overrides_json": args.reward_overrides_json,
                    "reward_overrides_phase": args.reward_overrides_phase,
                    "jax_platform": args.jax_platform,
                    "run": args.run,
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
            "reward_overrides_json": args.reward_overrides_json,
            "reward_overrides_phase": args.reward_overrides_phase,
            "jax_platform": args.jax_platform,
            "run": args.run,
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
