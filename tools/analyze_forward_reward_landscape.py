#!/usr/bin/env python3
"""Analyze forward-command tracking reward shape without running sim/training.

This mirrors the straight-ahead pieces of ``playground.common.rewards``:

    tracking_lin_vel = exp(-square(command_x - local_vx) / tracking_sigma)
    forward_progress = clipped signed velocity ratio
    forward_shortfall = square normalized shortfall below required ratio

The tool is offline-only. It does not import Playground, run MuJoCo, train,
deploy, SSH, or touch the robot.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable


def parse_float_list(raw: str) -> list[float]:
    values = []
    for item in raw.split(","):
        item = item.strip()
        if item:
            values.append(float(item))
    if not values:
        raise argparse.ArgumentTypeError("expected at least one comma-separated float")
    return values


def tracking_reward(command_x: float, velocity_x: float, sigma: float) -> float:
    if sigma <= 0:
        raise ValueError("tracking_sigma must be positive")
    return math.exp(-((command_x - velocity_x) ** 2) / sigma)


def forward_progress(command_x: float, velocity_x: float, deadband: float) -> float:
    if abs(command_x) <= deadband:
        return 0.0
    target_speed = max(abs(command_x), 1.0e-6)
    signed_speed = velocity_x * (1.0 if command_x >= 0.0 else -1.0)
    return max(0.0, min(signed_speed / target_speed, 1.0))


def forward_shortfall_cost(
    command_x: float,
    velocity_x: float,
    required_ratio: float,
    deadband: float,
) -> float:
    if abs(command_x) <= deadband:
        return 0.0
    target_speed = max(abs(command_x), 1.0e-6)
    signed_speed = velocity_x * (1.0 if command_x >= 0.0 else -1.0)
    required_speed = target_speed * required_ratio
    shortfall = max(required_speed - signed_speed, 0.0)
    return (shortfall / target_speed) ** 2


def velocity_grid(command_x: float) -> list[tuple[str, float]]:
    return [
        ("backward_50pct", -0.5 * command_x),
        ("zero", 0.0),
        ("forward_25pct", 0.25 * command_x),
        ("forward_50pct", 0.5 * command_x),
        ("forward_75pct", 0.75 * command_x),
        ("target", command_x),
        ("overshoot_125pct", 1.25 * command_x),
    ]


def analyze(
    command_x_values: Iterable[float],
    sigma_values: Iterable[float],
    tracking_scales: Iterable[float],
    forward_progress_scales: Iterable[float],
    forward_shortfall_scales: Iterable[float],
    forward_shortfall_required_ratios: Iterable[float],
    alive_scales: Iterable[float],
    forward_progress_deadband: float,
    dt_s: float,
) -> dict:
    rows = []
    for command_x in command_x_values:
        for sigma in sigma_values:
            for tracking_scale in tracking_scales:
                for progress_scale in forward_progress_scales:
                    for shortfall_scale in forward_shortfall_scales:
                        for required_ratio in forward_shortfall_required_ratios:
                            target_reward = tracking_reward(command_x, command_x, sigma)
                            zero_reward = tracking_reward(command_x, 0.0, sigma)
                            target_components = None
                            zero_components = None
                            for label, velocity_x in velocity_grid(command_x):
                                raw = tracking_reward(command_x, velocity_x, sigma)
                                progress = forward_progress(
                                    command_x, velocity_x, forward_progress_deadband
                                )
                                shortfall = forward_shortfall_cost(
                                    command_x,
                                    velocity_x,
                                    required_ratio,
                                    forward_progress_deadband,
                                )
                                scaled_tracking = raw * tracking_scale
                                scaled_progress = progress * progress_scale
                                scaled_shortfall = shortfall * shortfall_scale
                                scaled_total_no_alive = (
                                    scaled_tracking
                                    + scaled_progress
                                    + scaled_shortfall
                                )
                                components = {
                                    "raw_tracking_reward": raw,
                                    "raw_forward_progress_reward": progress,
                                    "raw_forward_shortfall_cost": shortfall,
                                    "scaled_tracking_reward": scaled_tracking,
                                    "scaled_forward_progress_reward": scaled_progress,
                                    "scaled_forward_shortfall_reward": scaled_shortfall,
                                    "scaled_total_no_alive": scaled_total_no_alive,
                                }
                                if label == "target":
                                    target_components = components
                                if label == "zero":
                                    zero_components = components
                                rows.append(
                                    {
                                        "command_x_m_s": command_x,
                                        "tracking_sigma": sigma,
                                        "tracking_lin_vel_scale": tracking_scale,
                                        "forward_progress_scale": progress_scale,
                                        "forward_shortfall_scale": shortfall_scale,
                                        "forward_shortfall_required_ratio": required_ratio,
                                        "forward_progress_deadband": forward_progress_deadband,
                                        "velocity_label": label,
                                        "velocity_x_m_s": velocity_x,
                                        **components,
                                        "per_tick_tracking_reward": (
                                            scaled_tracking * dt_s
                                        ),
                                        "per_tick_total_no_alive": (
                                            scaled_total_no_alive * dt_s
                                        ),
                                        "raw_reward_ratio_vs_target": (
                                            raw / target_reward
                                            if target_reward
                                            else None
                                        ),
                                        "raw_reward_ratio_zero_vs_target": (
                                            zero_reward / target_reward
                                            if target_reward
                                            else None
                                        ),
                                    }
                                )
                            if target_components is not None and zero_components is not None:
                                target_total = target_components["scaled_total_no_alive"]
                                zero_total = zero_components["scaled_total_no_alive"]
                                for row in rows[-len(velocity_grid(command_x)) :]:
                                    row["scaled_total_zero_vs_target"] = (
                                        zero_total / target_total
                                        if abs(target_total) > 1.0e-9
                                        else None
                                    )

    alive_rows = [
        {
            "alive_scale": alive,
            "per_tick_alive_reward": alive * dt_s,
        }
        for alive in alive_scales
    ]
    return {
        "dt_s": dt_s,
        "forward_progress_deadband": forward_progress_deadband,
        "rows": rows,
        "alive_rows": alive_rows,
    }


def fmt(value: float | None) -> str:
    if value is None:
        return "NA"
    return f"{value:.6f}"


def write_markdown(payload: dict, output: Path) -> None:
    rows = payload["rows"]
    lines = [
        "# Forward Reward Landscape",
        "",
        "Offline analysis of the straight-ahead tracking reward shape.",
        "",
        "Formula:",
        "",
        "```text",
        "tracking = exp(-square(command_x - local_vx) / tracking_sigma)",
        "progress = clip(signed_local_vx / abs(command_x), 0, 1)",
        "shortfall = square(max(abs(command_x) * required_ratio - signed_local_vx, 0) / abs(command_x))",
        "scaled_total_no_alive = tracking * tracking_scale + progress * progress_scale + shortfall * shortfall_scale",
        "```",
        "",
        f"dt_s: `{payload['dt_s']}`",
        f"forward_progress_deadband: `{payload['forward_progress_deadband']}`",
        "",
        "## Alive Term",
        "",
        "| alive_scale | per_tick_alive_reward |",
        "|---:|---:|",
    ]
    for row in payload["alive_rows"]:
        lines.append(
            f"| {fmt(row['alive_scale'])} | {fmt(row['per_tick_alive_reward'])} |"
        )

    lines.extend(
        [
            "",
            "## Zero-Velocity Reward Ratio",
            "",
            "| command_x | sigma | tracking_scale | progress_scale | shortfall_scale | required_ratio | zero/target raw tracking | zero/target scaled total | zero per-tick total no alive |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    zero_rows = [row for row in rows if row["velocity_label"] == "zero"]
    for row in zero_rows:
        lines.append(
            "| {cmd} | {sigma} | {scale} | {progress_scale} | {shortfall_scale} | {required_ratio} | {ratio} | {total_ratio} | {per_tick} |".format(
                cmd=fmt(row["command_x_m_s"]),
                sigma=fmt(row["tracking_sigma"]),
                scale=fmt(row["tracking_lin_vel_scale"]),
                progress_scale=fmt(row["forward_progress_scale"]),
                shortfall_scale=fmt(row["forward_shortfall_scale"]),
                required_ratio=fmt(row["forward_shortfall_required_ratio"]),
                ratio=fmt(row["raw_reward_ratio_zero_vs_target"]),
                total_ratio=fmt(row.get("scaled_total_zero_vs_target")),
                per_tick=fmt(row["per_tick_total_no_alive"]),
            )
        )

    lines.extend(
        [
            "",
            "## Full Velocity Grid",
            "",
            "| command_x | sigma | tracking_scale | progress_scale | shortfall_scale | required_ratio | velocity | tracking | progress | shortfall_cost | scaled_total_no_alive | per_tick_total_no_alive |",
            "|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in rows:
        lines.append(
            "| {cmd} | {sigma} | {scale} | {progress_scale} | {shortfall_scale} | {required_ratio} | `{label}` {vx} | {tracking} | {progress} | {shortfall} | {scaled_total} | {per_tick} |".format(
                cmd=fmt(row["command_x_m_s"]),
                sigma=fmt(row["tracking_sigma"]),
                scale=fmt(row["tracking_lin_vel_scale"]),
                progress_scale=fmt(row["forward_progress_scale"]),
                shortfall_scale=fmt(row["forward_shortfall_scale"]),
                required_ratio=fmt(row["forward_shortfall_required_ratio"]),
                label=row["velocity_label"],
                vx=fmt(row["velocity_x_m_s"]),
                tracking=fmt(row["raw_tracking_reward"]),
                progress=fmt(row["raw_forward_progress_reward"]),
                shortfall=fmt(row["raw_forward_shortfall_cost"]),
                scaled_total=fmt(row["scaled_total_no_alive"]),
                per_tick=fmt(row["per_tick_total_no_alive"]),
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- High zero/target ratios mean standing still can retain a large fraction of",
            "  the shaped nonzero-command reward for a nonzero command.",
            "- Compare per-tick tracking reward against per-tick alive reward to see",
            "  whether survival/stability can dominate weak locomotion.",
            "- Negative `forward_shortfall_scale` reduces the total when local forward",
            "  velocity is below the required ratio; if zero velocity still has a",
            "  positive total, discovery/exploration may still collapse to standstill.",
            "- This is only reward-shape analysis; it does not prove a policy will learn",
            "  until candidate training and closed-loop gates are rerun.",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze Open Duck forward tracking reward shape offline."
    )
    parser.add_argument("--command-x", type=parse_float_list, default="0.04,0.08")
    parser.add_argument(
        "--tracking-sigma",
        type=parse_float_list,
        default="0.01,0.005,0.0025,0.00125",
    )
    parser.add_argument("--tracking-scale", type=parse_float_list, default="2.5,12.0")
    parser.add_argument("--forward-progress-scale", type=parse_float_list, default="0.0")
    parser.add_argument("--forward-shortfall-scale", type=parse_float_list, default="0.0")
    parser.add_argument(
        "--forward-shortfall-required-ratio",
        type=parse_float_list,
        default="0.5",
    )
    parser.add_argument("--forward-progress-deadband", type=float, default=0.02)
    parser.add_argument("--alive-scale", type=parse_float_list, default="20.0,0.5")
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--output-md", type=Path)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    payload = analyze(
        command_x_values=args.command_x,
        sigma_values=args.tracking_sigma,
        tracking_scales=args.tracking_scale,
        forward_progress_scales=args.forward_progress_scale,
        forward_shortfall_scales=args.forward_shortfall_scale,
        forward_shortfall_required_ratios=args.forward_shortfall_required_ratio,
        alive_scales=args.alive_scale,
        forward_progress_deadband=args.forward_progress_deadband,
        dt_s=args.dt_s,
    )

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if args.output_md:
        write_markdown(payload, args.output_md)

    if not args.output_json and not args.output_md:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
