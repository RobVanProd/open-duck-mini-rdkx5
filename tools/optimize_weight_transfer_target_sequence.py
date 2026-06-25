#!/usr/bin/env python3
"""Run a small offline random-shooting optimizer for weight-transfer targets.

This wraps the staged planner probe and the existing target-objective scorer.
It does not train, deploy, SSH, or touch the robot. The output is still a
target-source diagnostic; passing traces must be reviewed before any dataset or
training step is authorized.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import math
from pathlib import Path
import shutil
from types import SimpleNamespace
from typing import Any

import numpy as np

from probe_staged_weight_transfer_planner import (
    DEFAULT_PLAYGROUND,
    Planner,
    run_probe,
    write_markdown as write_probe_markdown,
)
from score_target_candidates_objective import (
    score_traces,
    write_markdown as write_score_markdown,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "analysis" / "weight_transfer_optimizer"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "WEIGHT_TRANSFER_OPTIMIZER.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "weight_transfer_optimizer.json"


BOUNDS: dict[str, tuple[float, float]] = {
    "period_s": (0.48, 0.82),
    "balance_fraction": (0.20, 0.65),
    "roll_shift_rad": (0.015, 0.075),
    "lateral_gate_m_s": (0.055, 0.12),
    "base_y_gate_m": (0.015, 0.075),
    "pitch_gate_rad": (0.10, 0.30),
    "swing_knee_rad": (0.06, 0.18),
    "swing_ankle_rad": (-0.035, 0.035),
    "swing_hip_reach_rad": (0.02, 0.11),
    "stance_retract_scale": (0.25, 1.25),
    "stance_push_gain": (0.25, 2.0),
    "pitch_target_rad": (-0.04, 0.07),
    "pitch_damping": (0.5, 3.0),
    "lateral_gain": (-1.25, 1.25),
    "body_y_gain": (-1.25, 1.25),
}


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def clip_param(name: str, value: float) -> float:
    lo, hi = BOUNDS[name]
    return float(min(max(value, lo), hi))


def sample_uniform(rng: np.random.Generator, label: str, push_limit: float) -> Planner:
    values = {key: rng.uniform(lo, hi) for key, (lo, hi) in BOUNDS.items()}
    return Planner(
        label=label,
        step_gate_mode=int(rng.choice([0, 1, 2])),
        stance_push_limit_rad=push_limit,
        **{key: float(value) for key, value in values.items()},
    )


def sample_from_elites(
    rng: np.random.Generator,
    label: str,
    elites: list[dict[str, float]],
    push_limit: float,
    iteration: int,
) -> Planner:
    values: dict[str, float] = {}
    for key, (lo, hi) in BOUNDS.items():
        data = np.asarray([elite[key] for elite in elites], dtype=float)
        center = float(np.mean(data))
        spread = float(np.std(data))
        min_spread = (hi - lo) * 0.08
        annealed = (hi - lo) * max(0.10, 0.35 / float(iteration + 1))
        sigma = max(spread, min_spread, annealed)
        values[key] = clip_param(key, float(rng.normal(center, sigma)))
    return Planner(
        label=label,
        step_gate_mode=int(rng.choice([0, 1, 2])),
        stance_push_limit_rad=push_limit,
        **values,
    )


def planner_to_candidate(planner: Planner) -> dict[str, Any]:
    return asdict(planner)


def write_candidates(candidates: list[Planner], path: Path) -> None:
    payload = {"candidates": [planner_to_candidate(candidate) for candidate in candidates]}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def make_probe_args(args: argparse.Namespace, candidate_json: Path, iteration_dir: Path) -> SimpleNamespace:
    return SimpleNamespace(
        playground_path=args.playground_path,
        task=args.task,
        command_x=args.command_x,
        duration_s=args.duration_s,
        seeds=args.seeds,
        periods="",
        balance_fractions="",
        roll_shifts="",
        lateral_gates="",
        base_y_gates="",
        pitch_gates="",
        swing_knees="",
        swing_ankles="",
        swing_hip_reaches="",
        stance_retract_scales="",
        stance_push_gains="",
        stance_push_limit=args.stance_push_limit,
        pitch_targets="",
        pitch_dampings="",
        lateral_feedback_gains="",
        body_y_gains="",
        min_height_m=args.min_height_m,
        max_candidates=args.candidates_per_iteration,
        shuffle_candidates=False,
        grid_seed=args.seed,
        trace_dir=str(iteration_dir / "traces"),
        output_md=str(iteration_dir / "probe.md"),
        output_json=str(iteration_dir / "probe.json"),
        candidate_json=str(candidate_json),
    )


def make_score_args(args: argparse.Namespace, iteration_dir: Path) -> SimpleNamespace:
    return SimpleNamespace(
        trace_glob=[str(iteration_dir / "traces" / "*" / "seed_*.jsonl")],
        seeds=args.seeds,
        window_samples=args.window_samples,
        stride_samples=args.stride_samples,
        dt_s=0.02,
        command_x=args.command_x,
        min_mean_vx=args.min_mean_vx,
        max_track_ratio=1.5,
        max_vy_abs_p95=args.max_vy_abs_p95,
        max_contact_dominance_pct=95.0,
        max_double_support_pct=args.max_double_support_pct,
        max_no_support_pct=100.0,
        min_single_support_pct=args.min_single_support_pct,
        min_each_single_support_pct=args.min_each_single_support_pct,
        min_contact_transitions=args.min_contact_transitions,
        min_foot_site_z_p95=-1.0,
        max_pitch_abs_p95=args.max_pitch_abs_p95,
        min_base_height=args.min_base_height,
        max_action_saturation_pct=1.0,
        max_sent_velocity_p95=args.max_sent_velocity_p95,
        max_tracking_p95=args.max_tracking_p95,
        min_done_margin=args.min_done_margin,
        forward_weight=8.0,
        lateral_weight=8.0,
        contact_weight=0.02,
        double_support_weight=0.02,
        no_support_weight=0.02,
        single_support_weight=0.02,
        single_support_balance_weight=0.02,
        contact_transition_weight=0.02,
        foot_clearance_weight=2.0,
        pitch_weight=4.0,
        height_weight=8.0,
        saturation_weight=0.1,
        actuator_weight=1.0,
        done_margin_weight=0.01,
        done_inside_window_penalty=10.0,
        max_report_modes=args.candidates_per_iteration,
        output_md=str(iteration_dir / "score.md"),
        output_json=str(iteration_dir / "score.json"),
    )


def result_params_by_label(candidates: list[Planner]) -> dict[str, dict[str, float]]:
    by_label = {}
    for candidate in candidates:
        data = planner_to_candidate(candidate)
        by_label[candidate.label] = {
            key: float(data[key])
            for key in BOUNDS
        }
    return by_label


def run_optimizer(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    if output_dir.exists() and args.clean_output_dir:
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    elite_params: list[dict[str, float]] = []
    iterations = []
    global_best = None

    for iteration in range(args.iterations):
        iteration_dir = output_dir / f"iteration_{iteration:02d}"
        if elite_params:
            candidates = [
                sample_from_elites(
                    rng,
                    f"opt_i{iteration:02d}_c{index:03d}",
                    elite_params,
                    args.stance_push_limit,
                    iteration,
                )
                for index in range(args.candidates_per_iteration)
            ]
        else:
            candidates = [
                sample_uniform(rng, f"opt_i{iteration:02d}_c{index:03d}", args.stance_push_limit)
                for index in range(args.candidates_per_iteration)
            ]
        candidate_json = iteration_dir / "candidates.json"
        write_candidates(candidates, candidate_json)

        probe_args = make_probe_args(args, candidate_json, iteration_dir)
        probe_payload = run_probe(probe_args)
        Path(probe_args.output_json).write_text(json.dumps(probe_payload, indent=2) + "\n")
        write_probe_markdown(probe_payload, Path(probe_args.output_md))

        score_args = make_score_args(args, iteration_dir)
        score_payload = score_traces(score_args)
        Path(score_args.output_json).write_text(json.dumps(score_payload, indent=2) + "\n")
        write_score_markdown(score_payload, Path(score_args.output_md))

        by_label = result_params_by_label(candidates)
        elite_rows = score_payload["results"][: max(1, args.elite_count)]
        elite_params = [
            by_label[row["mode"]]
            for row in elite_rows
            if row["mode"] in by_label
        ]
        best = score_payload["results"][0] if score_payload["results"] else None
        if best is not None and (
            global_best is None
            or float(best.get("min_seed_score", -999.0))
            > float(global_best.get("min_seed_score", -999.0))
        ):
            global_best = {**best, "iteration": iteration}
        iterations.append(
            {
                "iteration": iteration,
                "candidate_json": str(candidate_json),
                "probe_md": probe_args.output_md,
                "score_md": score_args.output_md,
                "status": score_payload["status"],
                "robust_mode_count": score_payload["robust_mode_count"],
                "reason_counts": score_payload["reason_counts"],
                "best": best,
            }
        )

    status = "PASS_OPTIMIZER_FOUND_ROBUST_TARGET" if any(
        item["robust_mode_count"] > 0 for item in iterations
    ) else "HOLD_OPTIMIZER_NO_ROBUST_TARGET"
    return {
        "status": status,
        "command_x": args.command_x,
        "duration_s": args.duration_s,
        "seeds": args.seeds,
        "iterations": args.iterations,
        "candidates_per_iteration": args.candidates_per_iteration,
        "output_dir": str(output_dir),
        "global_best": global_best,
        "iteration_results": iterations,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Weight-Transfer Optimizer",
        "",
        f"status: `{payload['status']}`",
        f"command_x: `{payload['command_x']}`",
        f"duration_s: `{payload['duration_s']}`",
        f"seeds: `{payload['seeds']}`",
        f"iterations: `{payload['iterations']}`",
        f"candidates_per_iteration: `{payload['candidates_per_iteration']}`",
        "",
        "## Iterations",
        "",
        "| iter | status | robust | best_mode | min_score | mean_score | seed0_vx | seed2_vx | seed2_vy95 | seed2_failures |",
        "|---:|---|---:|---|---:|---:|---:|---:|---:|---|",
    ]
    for item in payload["iteration_results"]:
        best = item.get("best") or {}
        seed0 = (best.get("seeds") or {}).get("seed_000") or {}
        seed2 = (best.get("seeds") or {}).get("seed_002") or {}
        lines.append(
            "| {iteration} | {status} | {robust} | {mode} | {min_score} | {mean_score} | {seed0_vx} | {seed2_vx} | {seed2_vy} | `{seed2_fail}` |".format(
                iteration=item["iteration"],
                status=item["status"],
                robust=item["robust_mode_count"],
                mode=best.get("mode", "NA"),
                min_score=fmt_float(best.get("min_seed_score")),
                mean_score=fmt_float(best.get("mean_seed_score")),
                seed0_vx=fmt_float(seed0.get("mean_vx_m_s")),
                seed2_vx=fmt_float(seed2.get("mean_vx_m_s")),
                seed2_vy=fmt_float(seed2.get("vy_abs_p95_m_s")),
                seed2_fail=", ".join(seed2.get("hard_failures") or []),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is an offline optimizer probe, not training.",
            "- `PASS_OPTIMIZER_FOUND_ROBUST_TARGET` requires at least one seed-robust scored target.",
            "- Do not build a target dataset from optimizer traces until the 100/150 tick gates pass.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def fmt_float(value: Any) -> str:
    if value is None or not finite(value):
        return "NA"
    return f"{float(value):.4f}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--task", default="flat_terrain")
    parser.add_argument("--command-x", type=float, default=0.04)
    parser.add_argument("--duration-s", type=float, default=2.0)
    parser.add_argument("--seeds", default="0,2")
    parser.add_argument("--iterations", type=int, default=2)
    parser.add_argument("--candidates-per-iteration", type=int, default=8)
    parser.add_argument("--elite-count", type=int, default=3)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--stance-push-limit", type=float, default=0.04)
    parser.add_argument("--min-height-m", type=float, default=0.145)
    parser.add_argument("--window-samples", type=int, default=100)
    parser.add_argument("--stride-samples", type=int, default=5)
    parser.add_argument("--min-mean-vx", type=float, default=0.04)
    parser.add_argument("--max-vy-abs-p95", type=float, default=0.12)
    parser.add_argument("--max-double-support-pct", type=float, default=90.0)
    parser.add_argument("--min-single-support-pct", type=float, default=8.0)
    parser.add_argument("--min-each-single-support-pct", type=float, default=2.0)
    parser.add_argument("--min-contact-transitions", type=int, default=3)
    parser.add_argument("--max-pitch-abs-p95", type=float, default=0.35)
    parser.add_argument("--min-base-height", type=float, default=0.145)
    parser.add_argument("--max-sent-velocity-p95", type=float, default=2.5)
    parser.add_argument("--max-tracking-p95", type=float, default=0.12)
    parser.add_argument("--min-done-margin", type=int, default=50)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--clean-output-dir", action="store_true")
    args = parser.parse_args()

    payload = run_optimizer(args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={payload['status']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
