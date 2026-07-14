#!/usr/bin/env python3
"""Evaluate a ground-up policy on frozen commands/seeds using the CPU simulator.

This wrapper intentionally reuses ``closed_loop_sim_eval`` for physics and
actuator-bridge measurements. It adds only campaign aggregation and the
preregistered gait-emergence classification needed by the recipe search.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

# The user's local accelerators are out of scope. These must be set before the
# evaluator imports JAX inside run_closed_loop_sim.
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

from closed_loop_sim_eval import ClosedLoopConfig, run_closed_loop_sim


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIT = ROOT / "outputs" / "analysis" / "fixed_target_p30_actuator_fit_20260712.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_csv(text: str, cast) -> list:
    return [cast(item.strip()) for item in text.split(",") if item.strip()]


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not (
        isinstance(value, float) and (value != value or abs(value) == float("inf"))
    )


def constant_saturated_action(mode: dict[str, Any]) -> bool:
    joints = mode.get("joints") or {}
    if len(joints) != 14:
        return False
    for item in joints.values():
        action = item.get("action") or {}
        action_abs = item.get("action_abs") or {}
        if not finite(action.get("std")) or not finite(action_abs.get("min")):
            return False
        if float(action["std"]) > 1.0e-6 or float(action_abs["min"]) < 0.98:
            return False
    return True


def emergence_evidence(
    result: dict[str, Any],
    command_x: float,
    requested_duration_s: float,
    minimum_duration_s: float,
) -> dict[str, Any]:
    fitted = (result.get("modes") or {}).get("fitted")
    if not fitted:
        return {
            "pass": False,
            "reasons": ["missing_fitted_mode"],
            "command_x": command_x,
        }

    reasons: list[str] = []
    if requested_duration_s + 1.0e-9 < minimum_duration_s:
        reasons.append("contract_window_too_short_for_gait_classification")
    if fitted.get("termination_reason") != "duration_complete":
        reasons.append("standing_collapse_or_nonfinite")

    forward = fitted.get("forward_motion") or {}
    progress = forward.get("progress_x_m")
    if command_x > 0 and (not finite(progress) or float(progress) <= 0.0):
        reasons.append("no_positive_forward_displacement")
    mean_velocity = forward.get("mean_velocity_x_m_s")
    if command_x > 0 and (
        not finite(mean_velocity) or float(mean_velocity) <= 0.0
    ):
        reasons.append("no_positive_mean_forward_velocity")

    clearance = fitted.get("foot_clearance") or {}
    feet = clearance.get("feet") or {}
    support = clearance.get("support") or {}
    if command_x > 0:
        for foot in ("left", "right"):
            item = feet.get(foot) or {}
            if int(item.get("stance_samples") or 0) <= 0:
                reasons.append(f"{foot}_has_no_support")
            if int(item.get("swing_samples") or 0) <= 0:
                reasons.append(f"{foot}_has_no_swing")
            if int(item.get("contact_transition_count") or 0) <= 0:
                reasons.append(f"{foot}_has_no_contact_transition")
        if int(support.get("support_transition_count") or 0) <= 0:
            reasons.append("no_support_transition")

    saturated_constant = constant_saturated_action(fitted)
    if saturated_constant:
        reasons.append("constant_saturated_action_vector")

    return {
        "pass": not reasons,
        "reasons": reasons,
        "command_x": command_x,
        "termination_reason": fitted.get("termination_reason"),
        "progress_x_m": progress,
        "mean_velocity_x_m_s": mean_velocity,
        "requested_duration_s": requested_duration_s,
        "minimum_emergence_duration_s": minimum_duration_s,
        "left_stance_samples": (feet.get("left") or {}).get("stance_samples"),
        "left_swing_samples": (feet.get("left") or {}).get("swing_samples"),
        "left_contact_transition_count": (feet.get("left") or {}).get(
            "contact_transition_count"
        ),
        "right_stance_samples": (feet.get("right") or {}).get("stance_samples"),
        "right_swing_samples": (feet.get("right") or {}).get("swing_samples"),
        "right_contact_transition_count": (feet.get("right") or {}).get(
            "contact_transition_count"
        ),
        "support_transition_count": support.get("support_transition_count"),
        "single_support_pct": support.get("single_support_pct"),
        "double_support_pct": support.get("double_support_pct"),
        "constant_saturated_action_vector": saturated_constant,
    }


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    policy = Path(args.policy).resolve()
    playground = Path(args.playground_root).resolve()
    fit_path = Path(args.fit).resolve()
    reference = (
        None if args.reference_feature_table is None else Path(args.reference_feature_table).resolve()
    )
    fit = json.loads(fit_path.read_text())
    commands = parse_csv(args.commands, float)
    seeds = parse_csv(args.seeds, int)

    runs: list[dict[str, Any]] = []
    for command_x in commands:
        for seed in seeds:
            result = run_closed_loop_sim(
                ClosedLoopConfig(
                    policy_path=policy,
                    fit=fit,
                    playground_root=playground,
                    command_x=command_x,
                    duration_s=args.duration_s,
                    bridge_mode="fitted",
                    expected_observation_dim=args.expected_observation_dim,
                    expected_action_dim=14,
                    task=args.task,
                    seed=seed,
                    eval_role="candidate",
                    reference_feature_table_path=reference,
                )
            )
            evidence = emergence_evidence(
                result,
                command_x,
                args.duration_s,
                args.minimum_emergence_duration_s,
            )
            runs.append(
                {
                    "command_x": command_x,
                    "seed": seed,
                    "status": result.get("status"),
                    "candidate_gate": result.get("candidate_gate"),
                    "emergence": evidence,
                    "modes": result.get("modes"),
                    "error": result.get("error"),
                }
            )

    moving = [row for row in runs if row["command_x"] > 0]
    zero = [row for row in runs if abs(row["command_x"]) <= 1.0e-12]
    moving_pass = bool(moving) and all(row["emergence"]["pass"] for row in moving)
    zero_recorded_finite = bool(zero) and all(
        row["emergence"].get("termination_reason") == "duration_complete"
        for row in zero
    )
    emergence_pass = moving_pass and zero_recorded_finite

    return {
        "schema_version": "ground_up_policy_eval.v1",
        "status": "PASS_GAIT_EMERGENCE_CHECKPOINT" if emergence_pass else "HOLD_GAIT_NOT_EMERGED",
        "execution": {
            "platform": "cpu",
            "cuda_visible_devices": os.environ["CUDA_VISIBLE_DEVICES"],
            "jax_platforms": os.environ["JAX_PLATFORMS"],
        },
        "inputs": {
            "policy": str(policy),
            "policy_sha256": sha256(policy),
            "playground_root": str(playground),
            "fit": str(fit_path),
            "fit_sha256": sha256(fit_path),
            "reference_feature_table": None if reference is None else str(reference),
            "reference_feature_table_sha256": None if reference is None else sha256(reference),
            "expected_observation_dim": args.expected_observation_dim,
            "commands": commands,
            "seeds": seeds,
            "duration_s": args.duration_s,
            "minimum_emergence_duration_s": args.minimum_emergence_duration_s,
            "task": args.task,
        },
        "aggregate": {
            "runs": len(runs),
            "moving_runs": len(moving),
            "zero_command_runs": len(zero),
            "moving_emergence_pass": moving_pass,
            "zero_command_finite_recorded": zero_recorded_finite,
            "checkpoint_emergence_pass": emergence_pass,
        },
        "runs": runs,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Ground-Up Policy Evaluation",
        "",
        f"status: `{payload['status']}`",
        "execution: `CPU_ONLY`",
        "",
        "## Aggregate",
        "",
    ]
    for key, value in payload["aggregate"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Runs",
            "",
            "| command x | seed | evaluator | emergence | termination | dx m | transitions | reasons |",
            "|---:|---:|---|---|---|---:|---:|---|",
        ]
    )
    for row in payload["runs"]:
        e = row["emergence"]
        reasons = ", ".join(e["reasons"]) if e["reasons"] else "none"
        lines.append(
            f"| {row['command_x']} | {row['seed']} | `{row['status']}` | "
            f"`{e['pass']}` | `{e.get('termination_reason')}` | "
            f"{e.get('progress_x_m')} | {e.get('support_transition_count')} | {reasons} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", required=True)
    parser.add_argument("--playground-root", required=True)
    parser.add_argument("--fit", default=str(DEFAULT_FIT))
    parser.add_argument("--reference-feature-table", default=None)
    parser.add_argument("--expected-observation-dim", type=int, default=101)
    parser.add_argument("--commands", default="0.0,0.08")
    parser.add_argument("--seeds", default="100,101")
    parser.add_argument("--duration-s", type=float, default=5.0)
    parser.add_argument(
        "--minimum-emergence-duration-s",
        type=float,
        default=1.08,
        help="Two complete 27-tick reference periods at the frozen 50 Hz rate.",
    )
    parser.add_argument("--task", default="flat_terrain")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", default=None)
    args = parser.parse_args()
    payload = evaluate(args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if args.output_md:
        write_markdown(payload, Path(args.output_md))
    print(json.dumps({"status": payload["status"], **payload["aggregate"]}, sort_keys=True))


if __name__ == "__main__":
    main()
