#!/usr/bin/env python3
"""Analyze the low-command forward reward signal without training or robot access.

This tool answers a bounded question:

    At a low positive command, does the configured reward prefer forward local
    velocity over standing/reversing before command-progress termination?

It uses the same reward formulas as Playground's open_duck_mini_v2 joystick
task for velocity/progress terms, but keeps posture/contact/action terms neutral
so the immediate signal is visible without a full rollout.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable

from eval_policy_with_actuator_bridge import load_reward_overrides


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN_JSON = ROOT / "outputs" / "analysis" / "v18_a100_staged_plan.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "LOW_COMMAND_REWARD_SIGNAL.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "low_command_reward_signal.json"


SCALE_KEYS = {
    "tracking_lin_vel_scale": "tracking_lin_vel",
    "tracking_ang_vel_scale": "tracking_ang_vel",
    "forward_progress_scale": "forward_progress",
    "forward_shortfall_scale": "forward_shortfall",
    "forward_overshoot_scale": "forward_overshoot",
    "forward_wrong_direction_scale": "forward_wrong_direction",
    "command_progress_scale": "command_progress",
    "command_progress_shortfall_scale": "command_progress_shortfall",
    "command_progress_failure_scale": "command_progress_failure",
    "orientation_scale": "orientation",
    "base_height_scale": "base_height",
    "forward_pitch_scale": "forward_pitch",
    "forward_pitch_rate_scale": "forward_pitch_rate",
    "forward_contact_support_scale": "forward_contact_support",
    "action_rate_scale": "action_rate",
    "action_magnitude_scale": "action_magnitude",
    "stand_still_scale": "stand_still",
    "target_rate_scale": "target_rate",
    "actuator_tracking_scale": "actuator_tracking",
    "alive_scale": "alive",
    "imitation_scale": "imitation",
}


DEFAULT_SCALES = {
    "tracking_lin_vel": 2.5,
    "tracking_ang_vel": 6.0,
    "torques": -1.0e-3,
    "action_rate": -0.5,
    "action_magnitude": 0.0,
    "stand_still": -0.2,
    "target_rate": 0.0,
    "actuator_tracking": 0.0,
    "forward_progress": 0.0,
    "forward_shortfall": 0.0,
    "forward_overshoot": 0.0,
    "forward_wrong_direction": 0.0,
    "command_progress": 0.0,
    "command_progress_shortfall": 0.0,
    "command_progress_failure": 0.0,
    "orientation": 0.0,
    "base_height": 0.0,
    "forward_pitch": 0.0,
    "forward_pitch_rate": 0.0,
    "forward_contact_support": 0.0,
    "alive": 20.0,
    "imitation": 1.0,
}


DEFAULT_CONFIG = {
    "tracking_sigma": 0.01,
    "forward_progress_deadband": 0.02,
    "forward_shortfall_required_ratio": 0.5,
    "forward_overshoot_allowed_ratio": 1.5,
    "forward_wrong_direction_allowed_reverse_ratio": 0.1,
    "command_progress_required_ratio": 0.6,
    "command_progress_warmup_steps": 50,
    "command_progress_failure_enable": False,
    "command_progress_failure_min_ratio": 0.25,
    "command_progress_failure_warmup_steps": 120,
    "reward_clip_min": 0.0,
    "reward_clip_max": 10000.0,
    "forward_shortfall_huber_delta": 0.0,
    "forward_overshoot_huber_delta": 0.0,
    "forward_wrong_direction_huber_delta": 0.0,
    "command_progress_shortfall_huber_delta": 0.0,
}


def pseudo_huber_cost(error: float, delta: float) -> float:
    if delta <= 0.0:
        return float(error) ** 2
    scaled = float(error) / float(delta)
    return float(delta) ** 2 * (math.sqrt(1.0 + scaled**2) - 1.0)


def reward_tracking_lin_vel(command_x: float, vx: float, tracking_sigma: float) -> float:
    error_x = (float(command_x) - float(vx)) ** 2
    return math.exp(-error_x / float(tracking_sigma))


def reward_forward_progress(command_x: float, vx: float, deadband: float) -> float:
    if abs(command_x) <= deadband:
        return 0.0
    target_speed = max(abs(command_x), 1.0e-6)
    signed_speed = vx * (1.0 if command_x >= 0.0 else -1.0)
    return max(0.0, min(1.0, signed_speed / target_speed))


def cost_forward_shortfall(
    command_x: float,
    vx: float,
    required_ratio: float,
    deadband: float,
    huber_delta: float,
) -> float:
    if abs(command_x) <= deadband:
        return 0.0
    target_speed = max(abs(command_x), 1.0e-6)
    signed_speed = vx * (1.0 if command_x >= 0.0 else -1.0)
    required_speed = target_speed * required_ratio
    shortfall = max(required_speed - signed_speed, 0.0)
    return pseudo_huber_cost(shortfall / target_speed, huber_delta)


def cost_forward_overshoot(
    command_x: float,
    vx: float,
    allowed_ratio: float,
    deadband: float,
    huber_delta: float,
) -> float:
    if abs(command_x) <= deadband:
        return 0.0
    target_speed = max(abs(command_x), 1.0e-6)
    signed_speed = vx * (1.0 if command_x >= 0.0 else -1.0)
    overshoot = max(signed_speed - target_speed * allowed_ratio, 0.0)
    return pseudo_huber_cost(overshoot / target_speed, huber_delta)


def cost_forward_wrong_direction(
    command_x: float,
    vx: float,
    allowed_reverse_ratio: float,
    deadband: float,
    huber_delta: float,
) -> float:
    if abs(command_x) <= deadband:
        return 0.0
    target_speed = max(abs(command_x), 1.0e-6)
    signed_speed = vx * (1.0 if command_x >= 0.0 else -1.0)
    wrong_direction = max(-target_speed * allowed_reverse_ratio - signed_speed, 0.0)
    return pseudo_huber_cost(wrong_direction / target_speed, huber_delta)


def build_config(overrides: dict[str, Any]) -> tuple[dict[str, float], dict[str, Any]]:
    scales = dict(DEFAULT_SCALES)
    config = dict(DEFAULT_CONFIG)
    for override_key, scale_key in SCALE_KEYS.items():
        if override_key in overrides:
            scales[scale_key] = float(overrides[override_key])
    for key in DEFAULT_CONFIG:
        if key in overrides:
            config[key] = overrides[key]
    return scales, config


def reward_for_velocity(
    *,
    command_x: float,
    vx: float,
    step: int,
    dt: float,
    scales: dict[str, float],
    config: dict[str, Any],
) -> dict[str, Any]:
    deadband = float(config["forward_progress_deadband"])
    target_speed = max(abs(command_x), 1.0e-6)
    sign = 1.0 if command_x >= 0.0 else -1.0
    signed_speed = vx * sign
    elapsed_s = max(int(step) * dt, dt)
    progress_distance = signed_speed * elapsed_s
    target_distance = target_speed * elapsed_s
    progress_ratio = progress_distance / max(target_distance, 1.0e-6)
    command_shortfall = 0.0
    if abs(command_x) > deadband and step >= int(config["command_progress_warmup_steps"]):
        required = target_distance * float(config["command_progress_required_ratio"])
        command_shortfall = max(required - progress_distance, 0.0) / max(
            target_distance, 1.0e-6
        )
        command_shortfall = pseudo_huber_cost(
            command_shortfall, float(config["command_progress_shortfall_huber_delta"])
        )
    command_progress_failure = 0.0
    if (
        bool(config["command_progress_failure_enable"])
        and abs(command_x) > deadband
        and step >= int(config["command_progress_failure_warmup_steps"])
        and progress_ratio < float(config["command_progress_failure_min_ratio"])
    ):
        command_progress_failure = 1.0

    raw_terms = {
        "tracking_lin_vel": reward_tracking_lin_vel(
            command_x, vx, float(config["tracking_sigma"])
        ),
        "tracking_ang_vel": 1.0,
        "forward_progress": reward_forward_progress(command_x, vx, deadband),
        "forward_shortfall": cost_forward_shortfall(
            command_x,
            vx,
            float(config["forward_shortfall_required_ratio"]),
            deadband,
            float(config["forward_shortfall_huber_delta"]),
        ),
        "forward_overshoot": cost_forward_overshoot(
            command_x,
            vx,
            float(config["forward_overshoot_allowed_ratio"]),
            deadband,
            float(config["forward_overshoot_huber_delta"]),
        ),
        "forward_wrong_direction": cost_forward_wrong_direction(
            command_x,
            vx,
            float(config["forward_wrong_direction_allowed_reverse_ratio"]),
            deadband,
            float(config["forward_wrong_direction_huber_delta"]),
        ),
        "command_progress": progress_ratio if abs(command_x) > deadband else 0.0,
        "command_progress_shortfall": command_shortfall,
        "command_progress_failure": command_progress_failure,
        "orientation": 0.0,
        "base_height": 0.0,
        "forward_pitch": 0.0,
        "forward_pitch_rate": 0.0,
        "forward_contact_support": 0.0,
        "action_rate": 0.0,
        "action_magnitude": 0.0,
        "stand_still": 0.0,
        "target_rate": 0.0,
        "actuator_tracking": 0.0,
        "alive": 1.0,
        "imitation": 0.0,
    }
    scaled_terms = {
        key: raw_terms.get(key, 0.0) * scales.get(key, 0.0)
        for key in sorted(scales)
        if scales.get(key, 0.0) != 0.0 or raw_terms.get(key, 0.0) != 0.0
    }
    unclipped_sum = sum(scaled_terms.values())
    reward = max(
        float(config["reward_clip_min"]),
        min(float(config["reward_clip_max"]), unclipped_sum * dt),
    )
    return {
        "vx": vx,
        "step": step,
        "progress_ratio": progress_ratio,
        "raw_terms": raw_terms,
        "scaled_terms": scaled_terms,
        "unclipped_sum": unclipped_sum,
        "reward": reward,
    }


def parse_velocity_values(text: str | None, command_x: float) -> list[float]:
    if text:
        return [float(item) for item in text.split(",") if item.strip()]
    return [
        -2.0 * command_x,
        -command_x,
        -0.5 * command_x,
        0.0,
        0.25 * command_x,
        0.5 * command_x,
        0.65 * command_x,
        command_x,
        1.5 * command_x,
        1.7 * command_x,
        2.0 * command_x,
    ]


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Low-Command Reward Signal",
        "",
        f"status: `{payload['status']}`",
        f"command_x: `{payload['command_x']}`",
        f"pre_failure_step: `{payload['pre_failure_step']}`",
        f"terminal_step: `{payload['terminal_step']}`",
        f"reward_overrides_json: `{payload['reward_overrides_json']}`",
        f"reward_overrides_phase: `{payload['reward_overrides_phase']}`",
        "",
        "## Verdict",
        "",
    ]
    if payload["status"] == "PASS_FORWARD_REWARDED_ABOVE_STANDSTILL":
        lines.append(
            "Forward local velocity is rewarded above standing before the "
            "command-progress terminal gate. This supports the exploration / "
            "optimization-landscape hypothesis rather than a simple reward-sign "
            "or reward-weight signal bug."
        )
    else:
        lines.append(
            "The configured reward does not clearly prefer forward local velocity "
            "above standing. Do not launch more training until the reward signal "
            "is fixed or explained."
        )
    lines.append("")
    lines.append("## Pre-Failure Reward Table")
    lines.append("")
    lines.append(
        "| vx | tracking | progress | shortfall_cost | wrong_dir_cost | "
        "window_progress | window_shortfall | failure | reward | delta_vs_stand |"
    )
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    stand_reward = payload["pre_failure"]["standstill_reward"]
    for row in payload["pre_failure"]["rows"]:
        terms = row["scaled_terms"]
        lines.append(
            f"| {fmt(row['vx'])} | {fmt(terms.get('tracking_lin_vel'))} | "
            f"{fmt(terms.get('forward_progress'))} | "
            f"{fmt(terms.get('forward_shortfall'))} | "
            f"{fmt(terms.get('forward_wrong_direction'))} | "
            f"{fmt(terms.get('command_progress'))} | "
            f"{fmt(terms.get('command_progress_shortfall'))} | "
            f"{fmt(terms.get('command_progress_failure'))} | "
            f"{fmt(row['reward'])} | {fmt(row['reward'] - stand_reward)} |"
        )
    lines.append("")
    lines.append("## Terminal-Step Check")
    lines.append("")
    lines.append(
        "At the command-progress terminal step, low-progress velocities are "
        "allowed to become strongly negative if the phase enables command-progress "
        "failure. This table is included to verify that the backstop is active."
    )
    lines.append("")
    lines.append("| vx | progress_ratio | failure_term | reward |")
    lines.append("|---:|---:|---:|---:|")
    for row in payload["terminal"]["rows"]:
        terms = row["scaled_terms"]
        lines.append(
            f"| {fmt(row['vx'])} | {fmt(row['progress_ratio'])} | "
            f"{fmt(terms.get('command_progress_failure'))} | {fmt(row['reward'])} |"
        )
    lines.append("")
    lines.append("## Gate Inputs")
    lines.append("")
    for key, value in payload["comparison"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Stop Condition")
    lines.append("")
    if payload["status"] == "PASS_FORWARD_REWARDED_ABOVE_STANDSTILL":
        lines.append(
            "No further reward-weight tuning is authorized solely to make "
            "standing worse. The immediate reward signal already prefers forward "
            "motion; the next decisive experiment is an imitation/reference gait "
            "seed test."
        )
    else:
        lines.append(
            "Reward-signal repair is required before another training run."
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reward-overrides-json", type=Path, default=DEFAULT_PLAN_JSON)
    parser.add_argument(
        "--reward-overrides-phase",
        default="phase1_x004_dense_progress_discovery",
    )
    parser.add_argument("--command-x", type=float, default=0.04)
    parser.add_argument("--dt", type=float, default=0.02)
    parser.add_argument(
        "--pre-failure-step",
        type=int,
        default=49,
        help="Step before command-progress failure can fire.",
    )
    parser.add_argument(
        "--terminal-step",
        type=int,
        default=50,
        help="Step where V18 command-progress failure can fire.",
    )
    parser.add_argument(
        "--velocities",
        default=None,
        help="Comma-separated local vx values. Defaults to ratios of command_x.",
    )
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    args = parser.parse_args()

    overrides = load_reward_overrides(
        args.reward_overrides_json, args.reward_overrides_phase
    )
    scales, config = build_config(overrides)
    velocities = parse_velocity_values(args.velocities, args.command_x)

    def table(step: int) -> dict[str, Any]:
        rows = [
            reward_for_velocity(
                command_x=args.command_x,
                vx=vx,
                step=step,
                dt=args.dt,
                scales=scales,
                config=config,
            )
            for vx in velocities
        ]
        standstill = min(rows, key=lambda row: abs(row["vx"]))
        return {"step": step, "rows": rows, "standstill_reward": standstill["reward"]}

    pre_failure = table(args.pre_failure_step)
    terminal = table(args.terminal_step)
    command_reward = min(
        pre_failure["rows"], key=lambda row: abs(row["vx"] - args.command_x)
    )["reward"]
    required_vx = abs(args.command_x) * float(config["forward_shortfall_required_ratio"])
    required_reward = min(
        pre_failure["rows"], key=lambda row: abs(row["vx"] - required_vx)
    )["reward"]
    stand_reward = pre_failure["standstill_reward"]
    status = (
        "PASS_FORWARD_REWARDED_ABOVE_STANDSTILL"
        if command_reward > stand_reward and required_reward > stand_reward
        else "HOLD_REWARD_SIGNAL_DOES_NOT_PREFER_FORWARD"
    )
    payload = {
        "status": status,
        "command_x": args.command_x,
        "dt": args.dt,
        "pre_failure_step": args.pre_failure_step,
        "terminal_step": args.terminal_step,
        "reward_overrides_json": str(args.reward_overrides_json),
        "reward_overrides_phase": args.reward_overrides_phase,
        "scales": scales,
        "config": config,
        "pre_failure": pre_failure,
        "terminal": terminal,
        "comparison": {
            "standstill_reward": stand_reward,
            "required_vx": required_vx,
            "required_vx_reward": required_reward,
            "command_vx": args.command_x,
            "command_vx_reward": command_reward,
            "required_minus_standstill": required_reward - stand_reward,
            "command_minus_standstill": command_reward - stand_reward,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(build_markdown(payload))
    print(f"{status}")
    print(f"Wrote {args.output_md}")
    print(f"Wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
