#!/usr/bin/env python3
"""Random-shoot horizon target sequences for contact/weight-transfer.

This is an offline target-source diagnostic. It does not train, deploy, SSH,
or touch the robot. Unlike the prior scalar controller sweeps, this tool
generates smooth finite-horizon action tables, replays them through the existing
closed-loop sim sequence path, and scores realized contact/forward behavior.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict
import json
import math
from pathlib import Path
import shutil
from types import SimpleNamespace
from typing import Any

import numpy as np

from run_target_sequence_replay_smoke import SequencePolicy, run_closed_loop_rollout
from score_target_candidates_objective import score_traces, write_markdown as write_score_markdown
from eval_reference_motion_rollout import fmt


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "analysis" / "contact_weight_transfer_sequence_optimizer"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "CONTACT_WEIGHT_TRANSFER_SEQUENCE_OPTIMIZER.md"
DEFAULT_OUTPUT_JSON = (
    ROOT / "outputs" / "analysis" / "contact_weight_transfer_sequence_optimizer.json"
)


PITCH_CHAIN = (2, 3, 4, 11, 12, 13)


@dataclass
class SequenceParams:
    label: str
    period_ticks: int
    roll_action: float
    swing_knee_action: float
    swing_ankle_action: float
    swing_reach_action: float
    stance_retract_action: float
    stance_push_action: float
    stance_ankle_push_action: float
    late_push_bias: float
    pitch_bias_action: float
    phase_bias: float


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def fmt_float(value: Any) -> str:
    if value is None or not finite(value):
        return "NA"
    return f"{float(value):.4f}"


def clip(value: float, lo: float, hi: float) -> float:
    return float(min(max(value, lo), hi))


def sample_params(rng: np.random.Generator, label: str) -> SequenceParams:
    return SequenceParams(
        label=label,
        period_ticks=int(rng.choice([42, 48, 56, 64, 72])),
        roll_action=float(rng.uniform(0.04, 0.28)),
        swing_knee_action=float(rng.uniform(0.15, 0.72)),
        swing_ankle_action=float(rng.uniform(-0.20, 0.20)),
        swing_reach_action=float(rng.uniform(0.00, 0.42)),
        stance_retract_action=float(rng.uniform(0.00, 0.30)),
        stance_push_action=float(rng.uniform(-0.10, 0.42)),
        stance_ankle_push_action=float(rng.uniform(-0.18, 0.24)),
        late_push_bias=float(rng.uniform(0.00, 0.65)),
        pitch_bias_action=float(rng.uniform(-0.08, 0.12)),
        phase_bias=float(rng.uniform(0.0, 1.0)),
    )


def mutate_params(
    rng: np.random.Generator,
    label: str,
    base: SequenceParams,
    *,
    scale: float,
) -> SequenceParams:
    period = int(round(base.period_ticks + rng.normal(0.0, 8.0 * scale)))
    period = int(min(max(period, 36), 84))
    return SequenceParams(
        label=label,
        period_ticks=period,
        roll_action=clip(base.roll_action + rng.normal(0.0, 0.08 * scale), 0.0, 0.35),
        swing_knee_action=clip(
            base.swing_knee_action + rng.normal(0.0, 0.18 * scale), 0.0, 0.85
        ),
        swing_ankle_action=clip(
            base.swing_ankle_action + rng.normal(0.0, 0.10 * scale), -0.28, 0.28
        ),
        swing_reach_action=clip(
            base.swing_reach_action + rng.normal(0.0, 0.12 * scale), -0.05, 0.50
        ),
        stance_retract_action=clip(
            base.stance_retract_action + rng.normal(0.0, 0.10 * scale), 0.0, 0.42
        ),
        stance_push_action=clip(
            base.stance_push_action + rng.normal(0.0, 0.14 * scale), -0.18, 0.55
        ),
        stance_ankle_push_action=clip(
            base.stance_ankle_push_action + rng.normal(0.0, 0.10 * scale), -0.28, 0.32
        ),
        late_push_bias=clip(
            base.late_push_bias + rng.normal(0.0, 0.16 * scale), 0.0, 1.0
        ),
        pitch_bias_action=clip(
            base.pitch_bias_action + rng.normal(0.0, 0.06 * scale), -0.16, 0.18
        ),
        phase_bias=float((base.phase_bias + rng.normal(0.0, 0.20 * scale)) % 1.0),
    )


def support_contact(phase: float) -> tuple[int, int]:
    return (1, 0) if phase < 0.5 else (0, 1)


def smooth_pulse(value: float) -> float:
    value = float(np.clip(value, 0.0, 1.0))
    return float(np.sin(np.pi * value))


def late_pulse(value: float) -> float:
    value = float(np.clip((value - 0.45) / 0.55, 0.0, 1.0))
    return float(np.sin(np.pi * value))


def action_table(params: SequenceParams, horizon_ticks: int) -> tuple[np.ndarray, list[tuple[int, int]]]:
    actions = np.zeros((horizon_ticks, 14), dtype=np.float64)
    contacts: list[tuple[int, int]] = []
    for tick in range(horizon_ticks):
        phase = ((tick / float(params.period_ticks)) + params.phase_bias) % 1.0
        left_stance = 1.0 if phase < 0.5 else 0.0
        right_stance = 1.0 - left_stance
        left_swing = 1.0 - left_stance
        right_swing = 1.0 - right_stance
        half = phase * 2.0 if phase < 0.5 else (phase - 0.5) * 2.0
        lift = smooth_pulse(half)
        push = (1.0 - params.late_push_bias) * lift + params.late_push_bias * late_pulse(half)
        stance_side = left_stance - right_stance
        roll = params.roll_action * stance_side

        row = np.zeros(14, dtype=np.float64)
        row[1] = roll
        row[10] = -roll

        row[2] = (
            params.pitch_bias_action
            + left_swing * params.swing_reach_action * lift
            - left_stance * params.stance_retract_action * lift
            + left_stance * params.stance_push_action * push
        )
        row[3] = left_swing * params.swing_knee_action * lift
        row[4] = (
            left_swing * params.swing_ankle_action * lift
            + left_stance * params.stance_ankle_push_action * push
        )

        row[11] = (
            params.pitch_bias_action
            + right_swing * params.swing_reach_action * lift
            - right_stance * params.stance_retract_action * lift
            + right_stance * params.stance_push_action * push
        )
        row[12] = right_swing * params.swing_knee_action * lift
        row[13] = (
            right_swing * params.swing_ankle_action * lift
            + right_stance * params.stance_ankle_push_action * push
        )
        actions[tick] = np.clip(row, -1.0, 1.0)
        contacts.append(support_contact(phase))
    return actions, contacts


def sequence_policy(params: SequenceParams, horizon_ticks: int) -> SequencePolicy:
    actions, contacts = action_table(params, horizon_ticks)
    return SequencePolicy(
        name=params.label,
        source="contact_weight_transfer_sequence_optimizer",
        mode="random_shoot_horizon_sequence",
        prefix_actions=actions[:1],
        window_actions=actions,
        prefix_contacts=contacts[:1],
        window_contacts=contacts,
        window_body_pitch_abs=np.zeros(horizon_ticks, dtype=np.float64),
        window_base_height=np.zeros(horizon_ticks, dtype=np.float64),
        window_vy_abs=np.zeros(horizon_ticks, dtype=np.float64),
        entry_ids=[params.label],
    )


def make_rollout_args(args: argparse.Namespace, trace_dir: Path) -> SimpleNamespace:
    return SimpleNamespace(
        playground_path=args.playground_path,
        task=args.task,
        command_x=args.command_x,
        duration_s=args.duration_s,
        seeds=args.seeds,
        phase_adapter="fixed_time",
        max_phase_hold_ticks=0,
        phase_lookahead=0,
        contact_mismatch_weight=10.0,
        pitch_match_weight=2.0,
        height_match_weight=5.0,
        vy_match_weight=1.0,
        phase_skip_weight=0.1,
        trace_dir=str(trace_dir),
        jax_platform=args.jax_platform,
        min_mean_vx=args.min_mean_vx,
        max_vy_abs_p95=args.max_vy_abs_p95,
        max_body_pitch_abs_p95=args.max_pitch_abs_p95,
        min_base_height=args.min_base_height,
        max_sent_velocity_p95=args.max_sent_velocity_p95,
    )


def make_score_args(args: argparse.Namespace, trace_dir: Path, output_md: Path, output_json: Path) -> SimpleNamespace:
    return SimpleNamespace(
        trace_glob=[str(trace_dir / "*" / "seed_*.jsonl")],
        seeds=args.seeds,
        window_samples=args.window_samples,
        stride_samples=args.stride_samples,
        dt_s=0.02,
        command_x=args.command_x,
        min_mean_vx=args.min_mean_vx,
        min_forward_displacement_m=args.min_forward_displacement_m,
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
        forward_displacement_weight=8.0,
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
        output_md=str(output_md),
        output_json=str(output_json),
    )


def run_optimizer(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    if output_dir.exists() and args.clean_output_dir:
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(args.seed)
    elites: list[SequenceParams] = []
    iterations = []
    global_best = None

    for iteration in range(args.iterations):
        iteration_dir = output_dir / f"iteration_{iteration:02d}"
        trace_dir = iteration_dir / "traces"
        if elites:
            candidates = [
                mutate_params(
                    rng,
                    f"horizon_i{iteration:02d}_c{index:03d}",
                    elites[index % len(elites)],
                    scale=max(0.25, 0.75 / float(iteration + 1)),
                )
                for index in range(args.candidates_per_iteration)
            ]
        else:
            candidates = [
                sample_params(rng, f"horizon_i{iteration:02d}_c{index:03d}")
                for index in range(args.candidates_per_iteration)
            ]

        iteration_dir.mkdir(parents=True, exist_ok=True)
        (iteration_dir / "candidates.json").write_text(
            json.dumps([asdict(candidate) for candidate in candidates], indent=2) + "\n"
        )
        policies = [sequence_policy(candidate, args.horizon_ticks) for candidate in candidates]
        rollout = run_closed_loop_rollout(
            policies=policies,
            args=make_rollout_args(args, trace_dir),
        )
        (iteration_dir / "rollout.json").write_text(json.dumps(rollout, indent=2) + "\n")

        score_md = iteration_dir / "score.md"
        score_json = iteration_dir / "score.json"
        score_args = make_score_args(args, trace_dir, score_md, score_json)
        score_payload = score_traces(score_args)
        score_json.write_text(json.dumps(score_payload, indent=2) + "\n")
        write_score_markdown(score_payload, score_md)

        by_label = {candidate.label: candidate for candidate in candidates}
        elite_rows = score_payload["results"][: max(1, args.elite_count)]
        elites = [
            by_label[row["mode"]]
            for row in elite_rows
            if row.get("mode") in by_label
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
                "candidate_json": str(iteration_dir / "candidates.json"),
                "rollout_json": str(iteration_dir / "rollout.json"),
                "score_md": str(score_md),
                "score_json": str(score_json),
                "rollout_status": rollout.get("status"),
                "score_status": score_payload.get("status"),
                "robust_mode_count": score_payload.get("robust_mode_count"),
                "reason_counts": score_payload.get("reason_counts"),
                "best": best,
            }
        )

    status = "PASS_HORIZON_SEQUENCE_TARGET_FOUND" if any(
        item.get("robust_mode_count", 0) > 0 for item in iterations
    ) else "HOLD_HORIZON_SEQUENCE_NO_ROBUST_TARGET"
    return {
        "status": status,
        "command_x": args.command_x,
        "duration_s": args.duration_s,
        "seeds": args.seeds,
        "iterations": args.iterations,
        "candidates_per_iteration": args.candidates_per_iteration,
        "horizon_ticks": args.horizon_ticks,
        "output_dir": str(output_dir),
        "global_best": global_best,
        "iteration_results": iterations,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Contact Weight-Transfer Sequence Optimizer",
        "",
        f"status: `{payload['status']}`",
        f"command_x: `{fmt(payload['command_x'])}`",
        f"duration_s: `{fmt(payload['duration_s'])}`",
        f"seeds: `{payload['seeds']}`",
        f"horizon_ticks: `{payload['horizon_ticks']}`",
        f"iterations: `{payload['iterations']}`",
        f"candidates_per_iteration: `{payload['candidates_per_iteration']}`",
        "",
        "## Iterations",
        "",
        "| iter | rollout_status | score_status | robust | best_mode | min_score | mean_score | seed0_vx | seed2_vx | seed2_failures |",
        "|---:|---|---|---:|---|---:|---:|---:|---:|---|",
    ]
    for item in payload["iteration_results"]:
        best = item.get("best") or {}
        seed0 = (best.get("seeds") or {}).get("seed_000") or {}
        seed2 = (best.get("seeds") or {}).get("seed_002") or {}
        lines.append(
            "| {iteration} | `{rollout_status}` | `{score_status}` | {robust} | {mode} | {min_score} | {mean_score} | {seed0_vx} | {seed2_vx} | `{seed2_fail}` |".format(
                iteration=item["iteration"],
                rollout_status=item.get("rollout_status"),
                score_status=item.get("score_status"),
                robust=item.get("robust_mode_count"),
                mode=best.get("mode", "NA"),
                min_score=fmt_float(best.get("min_seed_score")),
                mean_score=fmt_float(best.get("mean_seed_score")),
                seed0_vx=fmt_float(seed0.get("mean_vx_m_s")),
                seed2_vx=fmt_float(seed2.get("mean_vx_m_s")),
                seed2_fail=", ".join(seed2.get("hard_failures") or []),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is a bounded offline target-source optimizer, not PPO/BC training.",
            "- It generates finite-horizon target tables and scores realized closed-loop contacts.",
            "- Passing would only authorize a reviewed target-dataset smoke branch.",
            "- No robot tests, SSH, deploy, training, or runtime behavior changes were performed.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--task", default="flat_terrain")
    parser.add_argument("--command-x", type=float, default=0.04)
    parser.add_argument("--duration-s", type=float, default=2.0)
    parser.add_argument("--seeds", default="0,2")
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--candidates-per-iteration", type=int, default=6)
    parser.add_argument("--elite-count", type=int, default=2)
    parser.add_argument("--horizon-ticks", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--jax-platform", choices=["auto", "cpu", "gpu"], default="cpu")
    parser.add_argument("--window-samples", type=int, default=100)
    parser.add_argument("--stride-samples", type=int, default=5)
    parser.add_argument("--min-mean-vx", type=float, default=0.04)
    parser.add_argument("--min-forward-displacement-m", type=float, default=0.004)
    parser.add_argument("--max-vy-abs-p95", type=float, default=0.12)
    parser.add_argument("--max-double-support-pct", type=float, default=75.0)
    parser.add_argument("--min-single-support-pct", type=float, default=20.0)
    parser.add_argument("--min-each-single-support-pct", type=float, default=5.0)
    parser.add_argument("--min-contact-transitions", type=int, default=2)
    parser.add_argument("--max-pitch-abs-p95", type=float, default=0.35)
    parser.add_argument("--min-base-height", type=float, default=0.145)
    parser.add_argument("--max-sent-velocity-p95", type=float, default=3.75)
    parser.add_argument("--max-tracking-p95", type=float, default=0.12)
    parser.add_argument("--min-done-margin", type=int, default=20)
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
