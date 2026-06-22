#!/usr/bin/env python3
"""Analyze forward-command tracking reward shape without running sim/training.

This mirrors ``playground.common.rewards.reward_tracking_lin_vel`` for the
straight-ahead case:

    exp(-square(command_x - local_vx) / tracking_sigma)

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
    alive_scales: Iterable[float],
    dt_s: float,
) -> dict:
    rows = []
    for command_x in command_x_values:
        for sigma in sigma_values:
            for tracking_scale in tracking_scales:
                target_reward = tracking_reward(command_x, command_x, sigma)
                zero_reward = tracking_reward(command_x, 0.0, sigma)
                for label, velocity_x in velocity_grid(command_x):
                    raw = tracking_reward(command_x, velocity_x, sigma)
                    scaled = raw * tracking_scale
                    rows.append(
                        {
                            "command_x_m_s": command_x,
                            "tracking_sigma": sigma,
                            "tracking_lin_vel_scale": tracking_scale,
                            "velocity_label": label,
                            "velocity_x_m_s": velocity_x,
                            "raw_tracking_reward": raw,
                            "scaled_tracking_reward": scaled,
                            "per_tick_tracking_reward": scaled * dt_s,
                            "raw_reward_ratio_vs_target": (
                                raw / target_reward if target_reward else None
                            ),
                            "raw_reward_ratio_zero_vs_target": (
                                zero_reward / target_reward if target_reward else None
                            ),
                        }
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
        "reward = exp(-square(command_x - local_vx) / tracking_sigma)",
        "scaled_per_tick = reward * tracking_lin_vel_scale * dt",
        "```",
        "",
        f"dt_s: `{payload['dt_s']}`",
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
            "| command_x | tracking_sigma | tracking_scale | zero/target raw reward | zero per-tick tracking |",
            "|---:|---:|---:|---:|---:|",
        ]
    )
    zero_rows = [row for row in rows if row["velocity_label"] == "zero"]
    for row in zero_rows:
        lines.append(
            "| {cmd} | {sigma} | {scale} | {ratio} | {per_tick} |".format(
                cmd=fmt(row["command_x_m_s"]),
                sigma=fmt(row["tracking_sigma"]),
                scale=fmt(row["tracking_lin_vel_scale"]),
                ratio=fmt(row["raw_reward_ratio_zero_vs_target"]),
                per_tick=fmt(row["per_tick_tracking_reward"]),
            )
        )

    lines.extend(
        [
            "",
            "## Full Velocity Grid",
            "",
            "| command_x | sigma | scale | velocity | raw reward | scaled reward | per-tick reward | ratio vs target |",
            "|---:|---:|---:|---|---:|---:|---:|---:|",
        ]
    )
    for row in rows:
        lines.append(
            "| {cmd} | {sigma} | {scale} | `{label}` {vx} | {raw} | {scaled} | {per_tick} | {ratio} |".format(
                cmd=fmt(row["command_x_m_s"]),
                sigma=fmt(row["tracking_sigma"]),
                scale=fmt(row["tracking_lin_vel_scale"]),
                label=row["velocity_label"],
                vx=fmt(row["velocity_x_m_s"]),
                raw=fmt(row["raw_tracking_reward"]),
                scaled=fmt(row["scaled_tracking_reward"]),
                per_tick=fmt(row["per_tick_tracking_reward"]),
                ratio=fmt(row["raw_reward_ratio_vs_target"]),
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- High zero/target ratios mean standing still can retain a large fraction of",
            "  the velocity-tracking reward for a nonzero command.",
            "- Compare per-tick tracking reward against per-tick alive reward to see",
            "  whether survival/stability can dominate weak locomotion.",
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
    parser.add_argument("--alive-scale", type=parse_float_list, default="20.0,0.5")
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--output-md", type=Path)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    payload = analyze(
        command_x_values=args.command_x,
        sigma_values=args.tracking_sigma,
        tracking_scales=args.tracking_scale,
        alive_scales=args.alive_scale,
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
