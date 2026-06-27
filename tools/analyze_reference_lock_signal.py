#!/usr/bin/env python3
"""Analyze whether a reference trajectory is coherent for low-command seeding.

This is an offline diagnostic. It does not step MuJoCo, train, SSH, deploy, or
touch the robot. It answers a narrower question than PPO:

    If the reference motion were followed, would it satisfy the command-progress
    and imitation signal expected by the current low-command training recipe?

It intentionally scores the reference itself before blaming the optimizer.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any, Iterable

import numpy as np

from analyze_low_command_reward_signal import build_config, reward_for_velocity
from eval_policy_with_actuator_bridge import load_reward_overrides


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_REFERENCE = ROOT / "outputs" / "analysis" / "reference_motion_x004_override.pkl"
DEFAULT_REWARD_OVERRIDES = (
    ROOT
    / "outputs"
    / "analysis"
    / "colab_cli"
    / "open-duck-a100-v20-staged-curriculum-20260625T032259Z"
    / "manual_partial"
    / "open_duck_staged_curriculum_cli"
    / "01_phase1_interpolated_reference_seed_x004"
    / "phase_01_seed_gate_xp0p040"
    / "phase_reward_overrides.json"
)
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "REFERENCE_LOCK_SIGNAL_V20.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "reference_lock_signal_v20.json"


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def stats(values: Iterable[float], *, abs_value: bool = False) -> dict[str, float] | None:
    data = [abs(float(v)) if abs_value else float(v) for v in values if finite(v)]
    if not data:
        return None
    data = sorted(data)
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


def load_reference_motion(playground_path: Path, reference_path: Path):
    sys.path.insert(0, str(playground_path))
    from playground.common.poly_reference_motion_numpy import PolyReferenceMotion

    return PolyReferenceMotion(str(reference_path))


def ideal_imitation_raw_reward() -> float:
    """Raw imitation reward when actual state exactly matches reference slices.

    Matches playground/open_duck_mini_v2/custom_rewards.py:
    orientation=1, linear xy=1, linear z=1, angular xy=0.5, angular z=0.5,
    joint position/velocity costs are 0, and two contact matches contribute 2.
    """

    return 1.0 + 1.0 + 1.0 + 0.5 + 0.5 + 2.0


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    reference_path = Path(args.reference)
    playground_path = Path(args.playground_path)
    overrides = load_reward_overrides(
        Path(args.reward_overrides_json) if args.reward_overrides_json else None,
        args.reward_overrides_phase,
    )
    scales, config = build_config(overrides)
    prm = load_reference_motion(playground_path, reference_path)
    period_steps = int(prm.nb_steps_in_period)
    frames = [
        np.asarray(
            prm.get_reference_motion(args.command_x, args.command_y, args.command_yaw, i),
            dtype=float,
        )
        for i in range(period_steps)
    ]
    linvel = np.asarray([frame[34:37] for frame in frames], dtype=float)
    angvel = np.asarray([frame[37:40] for frame in frames], dtype=float)
    contacts = np.asarray([frame[32:34] for frame in frames], dtype=float)
    contact_bool = contacts > 0.5
    contact_patterns = [
        tuple(int(value) for value in row)
        for row in contact_bool.tolist()
    ]
    contact_transitions = sum(
        1 for left, right in zip(contact_patterns, contact_patterns[1:]) if left != right
    )
    dt_s = float(args.dt_s)
    horizon_steps = int(args.horizon_steps)
    repeated_vx = [float(linvel[i % period_steps, 0]) for i in range(horizon_steps)]
    cumulative_progress = sum(repeated_vx) * dt_s
    target_progress = max(abs(args.command_x), 1.0e-6) * horizon_steps * dt_s
    progress_ratio = cumulative_progress / max(target_progress, 1.0e-6)
    pre_terminal_scores = [
        reward_for_velocity(
            command_x=args.command_x,
            vx=float(repeated_vx[i]),
            step=i,
            dt=dt_s,
            scales=scales,
            config=config,
        )
        for i in range(min(horizon_steps, int(args.pre_terminal_steps)))
    ]
    ideal_imitation_scaled = ideal_imitation_raw_reward() * float(
        scales.get("imitation", 0.0)
    )
    min_progress = float(config.get("command_progress_failure_min_ratio", 0.0))
    required_ratio = float(config.get("forward_shortfall_required_ratio", 0.0))
    vx_mean = float(np.mean(linvel[:, 0]))
    status = "PASS_REFERENCE_SIGNAL_COHERENT"
    warnings: list[str] = []
    if progress_ratio < min_progress:
        status = "HOLD_REFERENCE_PROGRESS_TOO_LOW"
        warnings.append("reference cumulative progress is below command-progress failure floor")
    if vx_mean < abs(args.command_x) * required_ratio:
        status = "HOLD_REFERENCE_FORWARD_SPEED_TOO_LOW"
        warnings.append("reference mean forward speed is below forward-shortfall requirement")
    vy_abs_p95 = float(stats(linvel[:, 1], abs_value=True)["p95"])
    if vy_abs_p95 > abs(args.command_x) * float(args.lateral_warn_ratio):
        warnings.append("reference lateral p95_abs is large relative to command_x")
    return {
        "status": status,
        "reference_path": str(reference_path),
        "playground_path": str(playground_path),
        "command": {
            "x": args.command_x,
            "y": args.command_y,
            "yaw": args.command_yaw,
        },
        "period_steps": period_steps,
        "horizon_steps": horizon_steps,
        "dt_s": dt_s,
        "reward_overrides_json": str(args.reward_overrides_json),
        "reward_overrides_phase": args.reward_overrides_phase,
        "velocity": {
            "linvel_x": stats(linvel[:, 0]),
            "linvel_y": stats(linvel[:, 1]),
            "linvel_y_abs": stats(linvel[:, 1], abs_value=True),
            "angvel_z": stats(angvel[:, 2]),
            "angvel_z_abs": stats(angvel[:, 2], abs_value=True),
        },
        "contacts": {
            "left_true_count": int(np.sum(contact_bool[:, 0])),
            "right_true_count": int(np.sum(contact_bool[:, 1])),
            "patterns": {str(pattern): contact_patterns.count(pattern) for pattern in sorted(set(contact_patterns))},
            "transitions_per_period": contact_transitions,
        },
        "progress": {
            "cumulative_progress_m": cumulative_progress,
            "target_progress_m": target_progress,
            "progress_ratio": progress_ratio,
            "failure_min_ratio": min_progress,
            "forward_required_ratio": required_ratio,
        },
        "reward_signal": {
            "ideal_imitation_raw": ideal_imitation_raw_reward(),
            "ideal_imitation_scaled": ideal_imitation_scaled,
            "pre_terminal_reward_mean": float(
                np.mean([item["reward"] for item in pre_terminal_scores])
            ),
            "pre_terminal_unclipped_sum_mean": float(
                np.mean([item["unclipped_sum"] for item in pre_terminal_scores])
            ),
        },
        "warnings": warnings,
    }


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    velocity = payload["velocity"]
    progress = payload["progress"]
    reward = payload["reward_signal"]
    contacts = payload["contacts"]
    lines = [
        "# Reference Lock Signal",
        "",
        f"status: `{payload['status']}`",
        f"reference: `{payload['reference_path']}`",
        f"command: `{payload['command']}`",
        f"period_steps: `{payload['period_steps']}`",
        "",
        "## Velocity",
        "",
        f"- linvel_x_mean: `{fmt(velocity['linvel_x']['mean'])}`",
        f"- linvel_x_p95: `{fmt(velocity['linvel_x']['p95'])}`",
        f"- linvel_y_mean: `{fmt(velocity['linvel_y']['mean'])}`",
        f"- linvel_y_abs_p95: `{fmt(velocity['linvel_y_abs']['p95'])}`",
        f"- angvel_z_abs_p95: `{fmt(velocity['angvel_z_abs']['p95'])}`",
        "",
        "## Progress",
        "",
        f"- progress_ratio: `{fmt(progress['progress_ratio'])}`",
        f"- failure_min_ratio: `{fmt(progress['failure_min_ratio'])}`",
        f"- forward_required_ratio: `{fmt(progress['forward_required_ratio'])}`",
        "",
        "## Imitation Signal",
        "",
        f"- ideal_imitation_raw: `{fmt(reward['ideal_imitation_raw'])}`",
        f"- ideal_imitation_scaled: `{fmt(reward['ideal_imitation_scaled'])}`",
        f"- pre_terminal_unclipped_sum_mean: `{fmt(reward['pre_terminal_unclipped_sum_mean'])}`",
        "",
        "## Contacts",
        "",
        f"- left_true_count: `{contacts['left_true_count']}`",
        f"- right_true_count: `{contacts['right_true_count']}`",
        f"- transitions_per_period: `{contacts['transitions_per_period']}`",
        f"- patterns: `{contacts['patterns']}`",
        "",
        "## Warnings",
        "",
    ]
    warnings = payload.get("warnings") or []
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `PASS_REFERENCE_SIGNAL_COHERENT` means the reference itself clears the analytic command-progress check.",
            "- This does not mean PPO can discover or preserve the reference; V20 showed it did not.",
            "- Large lateral velocity warnings should be carried into any later reference-lock or behavior-cloning work.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", default=str(DEFAULT_REFERENCE))
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--reward-overrides-json", default=str(DEFAULT_REWARD_OVERRIDES))
    parser.add_argument("--reward-overrides-phase", default="phase1_interpolated_reference_seed_x004")
    parser.add_argument("--command-x", type=float, default=0.04)
    parser.add_argument("--command-y", type=float, default=0.0)
    parser.add_argument("--command-yaw", type=float, default=0.0)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--horizon-steps", type=int, default=70)
    parser.add_argument("--pre-terminal-steps", type=int, default=60)
    parser.add_argument("--lateral-warn-ratio", type=float, default=4.0)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()
    payload = build_payload(args)
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
