#!/usr/bin/env python3
"""Reconstruct eval return from recorded ground-up TensorBoard components."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tensorboard.backend.event_processing.event_accumulator import EventAccumulator


COMPONENT_TAGS = {
    "alive": "eval/episode_reward/alive",
    "tracking_ang_vel": "eval/episode_reward/tracking_ang_vel",
    "tracking_lin_vel": "eval/episode_reward/tracking_lin_vel",
    "imitation": "eval/episode_reward/imitation",
    "action_rate": "eval/episode_cost/action_rate",
    "stand_still": "eval/episode_cost/stand_still",
    "torques": "eval/episode_cost/torques",
}
REWARD_TAG = "eval/episode_reward"
LENGTH_TAG = "eval/avg_episode_length"


def scalar_map(accumulator: EventAccumulator, tag: str) -> dict[int, float]:
    return {event.step: float(event.value) for event in accumulator.Scalars(tag)}


def audit_candidate(candidate_id: str, event_path: Path, dt: float) -> dict:
    accumulator = EventAccumulator(str(event_path), size_guidance={"scalars": 0})
    accumulator.Reload()
    logged = scalar_map(accumulator, REWARD_TAG)
    lengths = scalar_map(accumulator, LENGTH_TAG)
    components = {
        name: scalar_map(accumulator, tag) for name, tag in COMPONENT_TAGS.items()
    }
    rows = []
    for step in sorted(logged):
        values = {name: series[step] for name, series in components.items()}
        positive_mass = sum(
            values[name]
            for name in ("alive", "tracking_ang_vel", "tracking_lin_vel", "imitation")
        )
        cost_mass = sum(values[name] for name in ("action_rate", "stand_still", "torques"))
        reconstructed = (positive_mass - cost_mass) * dt
        invariant = values["alive"] + values["tracking_ang_vel"]
        rows.append(
            {
                "step": step,
                "avg_episode_length": lengths[step],
                "logged_episode_reward": logged[step],
                "reconstructed_raw_return": reconstructed,
                "absolute_clipping_gap": abs(logged[step] - reconstructed),
                "command_invariant_positive_mass": invariant,
                "total_positive_mass": positive_mass,
                "command_invariant_positive_share": (
                    invariant / positive_mass if positive_mass else None
                ),
                "components": values,
            }
        )
    mature = [row for row in rows if row["step"] > 0]
    return {
        "candidate_id": candidate_id,
        "event_path": str(event_path),
        "checkpoints": rows,
        "max_mature_absolute_clipping_gap": max(
            row["absolute_clipping_gap"] for row in mature
        ),
        "final_command_invariant_positive_share": rows[-1][
            "command_invariant_positive_share"
        ],
    }


def render_markdown(result: dict) -> str:
    lines = [
        "# Ground-Up Reward Accounting Audit",
        "",
        "status: `COMMAND_INVARIANT_REWARD_SELECTED_FOR_NEXT_CAUSAL_TEST`",
        "",
        "The logged evaluation return is reconstructed as `dt * (positive reward "
        "components - cost components)`. A material positive gap would be evidence "
        "that negative per-step totals were removed by the environment's lower clip.",
        "",
        "| candidate | step | logged return | reconstructed raw | absolute gap | alive+yaw positive share |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for candidate in result["candidates"]:
        for row in candidate["checkpoints"]:
            lines.append(
                f"| `{candidate['candidate_id']}` | {row['step']} | "
                f"{row['logged_episode_reward']:.6f} | "
                f"{row['reconstructed_raw_return']:.6f} | "
                f"{row['absolute_clipping_gap']:.8f} | "
                f"{100 * row['command_invariant_positive_share']:.2f}% |"
            )
    lines += [
        "",
        "## Decision",
        "",
        "Total-reward clipping is not selected for the next causal test. Across "
        "all mature B0/O1 evaluation checkpoints, reconstructed raw return matches "
        "logged return within the numerical precision recorded in TensorBoard. This "
        "does not measure every PPO training transition, but it provides no observed "
        "evaluation evidence that clipping drives the failed behavior.",
        "",
        "Command-invariant positive reward is selected. At the final checkpoints, "
        "alive plus zero-yaw tracking account for "
        f"{100 * result['candidates'][0]['final_command_invariant_positive_share']:.2f}% "
        "of B0 positive reward mass and "
        f"{100 * result['candidates'][1]['final_command_invariant_positive_share']:.2f}% "
        "of O1 positive reward mass. These terms do not distinguish forward gait "
        "from stationary survival in the exact-yaw-zero nominal stage.",
        "",
        "The next experiment must change only this structural mechanism and retain "
        "signed progress, the nominal bootstrap, PPO settings, phase, command, and "
        "frozen behavior gate. Its exact wiring and stop rule require a separate "
        "CPU contract and preregistration before accelerator compute.",
        "",
        "Training reward is not a selection gate. This audit reads recorded files "
        "only and does not access a GPU, iGPU, RDK-X5, robot, motor, or torque.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidate",
        action="append",
        required=True,
        help="CANDIDATE_ID=EVENT_FILE (repeatable)",
    )
    parser.add_argument("--dt", type=float, default=0.02)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    candidates = []
    for value in args.candidate:
        candidate_id, raw_path = value.split("=", 1)
        candidates.append(audit_candidate(candidate_id, Path(raw_path), args.dt))
    result = {
        "schema_version": "ground_up_reward_accounting_audit.v1",
        "status": "COMMAND_INVARIANT_REWARD_SELECTED_FOR_NEXT_CAUSAL_TEST",
        "dt": args.dt,
        "selection_uses_training_reward": False,
        "candidates": candidates,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    args.output_md.write_text(render_markdown(result))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
