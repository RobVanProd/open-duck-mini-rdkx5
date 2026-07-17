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
    world_progress = forward.get("progress_x_m")
    progress = forward.get("body_forward_progress_m")
    if progress is None:
        mean_velocity = forward.get("mean_velocity_x_m_s")
        elapsed_s = forward.get("elapsed_s")
        progress = (
            float(mean_velocity) * float(elapsed_s)
            if finite(mean_velocity) and finite(elapsed_s)
            else world_progress
        )
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
        "world_progress_x_m": world_progress,
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
    policy_observer_fit_path = (
        None
        if args.policy_observer_fit is None
        else Path(args.policy_observer_fit).resolve()
    )
    reference = (
        None if args.reference_feature_table is None else Path(args.reference_feature_table).resolve()
    )
    fit = json.loads(fit_path.read_text())
    policy_observer_fit = (
        None
        if policy_observer_fit_path is None
        else json.loads(policy_observer_fit_path.read_text())
    )
    commands = parse_csv(args.commands, float)
    seeds = parse_csv(args.seeds, int)
    state_input_names = tuple(parse_csv(args.policy_state_input_names, str))
    state_output_names = tuple(parse_csv(args.policy_state_output_names, str))
    dynamics_override = (
        None
        if args.eval_dynamics_override_json is None
        else json.loads(args.eval_dynamics_override_json)
    )
    if dynamics_override is not None and not isinstance(dynamics_override, dict):
        raise ValueError("--eval-dynamics-override-json must decode to an object")

    runs: list[dict[str, Any]] = []
    for command_x in commands:
        for seed in seeds:
            trace_path = None
            if args.trace_dir is not None:
                trace_path = args.trace_dir / (
                    f"x{command_x:.3f}_seed{seed}_{policy.stem}.jsonl"
                )
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
                    reset_mode=args.reset_mode,
                    policy_action_rate_limit_rad_s=args.policy_action_rate_limit_rad_s,
                    policy_action_rate_limit_joint_indices=tuple(
                        parse_csv(args.policy_action_rate_limit_joint_indices, int)
                    ),
                    policy_action_rate_limit_values=tuple(
                        parse_csv(args.policy_action_rate_limit_values, float)
                    ),
                    reference_feature_table_path=reference,
                    reference_start_phase=args.reference_start_phase,
                    policy_state_input_names=state_input_names,
                    policy_state_output_names=state_output_names,
                    policy_applied_target_observation=(
                        args.policy_applied_target_observation
                    ),
                    policy_observer_fit=policy_observer_fit,
                    policy_reset_com_estimator_input=(
                        args.policy_reset_com_estimator_input
                    ),
                    eval_dynamics_override=dynamics_override,
                    trace_jsonl=trace_path,
                    trace_full_obs=bool(args.trace_full_obs),
                    trace_com_accelerometer_map_ticks=tuple(
                        parse_csv(args.trace_com_accelerometer_map_ticks, int)
                    ),
                )
            )
            evidence = emergence_evidence(
                result,
                command_x,
                args.duration_s,
                args.minimum_emergence_duration_s,
            )
            run_payload = {
                    "command_x": command_x,
                    "seed": seed,
                    "status": result.get("status"),
                    "candidate_gate": result.get("candidate_gate"),
                    "emergence": evidence,
                    "modes": result.get("modes"),
                    "dynamics_override": (
                        (result.get("insertion_point") or {}).get(
                            "dynamics_override"
                        )
                    ),
                    "error": result.get("error"),
                    "trace_jsonl": None if trace_path is None else str(trace_path),
                }
            if policy_observer_fit_path is not None:
                run_payload["policy_observer_fit_enabled"] = bool(
                    result.get("policy_observer_fit_enabled")
                )
                run_payload["policy_observer_fit"] = str(policy_observer_fit_path)
                run_payload["policy_observer_fit_sha256"] = sha256(
                    policy_observer_fit_path
                )
            runs.append(run_payload)

    moving = [row for row in runs if row["command_x"] > 0]
    zero = [row for row in runs if abs(row["command_x"]) <= 1.0e-12]
    moving_pass = bool(moving) and all(row["emergence"]["pass"] for row in moving)
    zero_recorded_finite = (not zero) or all(
        row["emergence"].get("termination_reason") == "duration_complete"
        for row in zero
    )
    emergence_pass = moving_pass and zero_recorded_finite

    payload = {
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
            "reference_start_phase": args.reference_start_phase,
            "expected_observation_dim": args.expected_observation_dim,
            "commands": commands,
            "seeds": seeds,
            "duration_s": args.duration_s,
            "minimum_emergence_duration_s": args.minimum_emergence_duration_s,
            "task": args.task,
            "reset_mode": args.reset_mode,
            "policy_action_rate_limit_rad_s": args.policy_action_rate_limit_rad_s,
            "policy_action_rate_limit_joint_indices": parse_csv(
                args.policy_action_rate_limit_joint_indices, int
            ),
            "policy_action_rate_limit_values": parse_csv(
                args.policy_action_rate_limit_values, float
            ),
            "policy_state_input_names": list(state_input_names),
            "policy_state_output_names": list(state_output_names),
            "policy_applied_target_observation": bool(
                args.policy_applied_target_observation
            ),
            "policy_reset_com_estimator_input": bool(
                args.policy_reset_com_estimator_input
            ),
            "eval_dynamics_override": dynamics_override,
            "trace_dir": None if args.trace_dir is None else str(args.trace_dir),
            "trace_full_obs": bool(args.trace_full_obs),
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
    if policy_observer_fit_path is not None:
        payload["inputs"]["policy_observer_fit"] = str(policy_observer_fit_path)
        payload["inputs"]["policy_observer_fit_sha256"] = sha256(
            policy_observer_fit_path
        )
    return payload


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
    parser.add_argument("--reference-start-phase", type=int, default=None)
    parser.add_argument("--expected-observation-dim", type=int, default=101)
    parser.add_argument(
        "--policy-state-input-names",
        default="",
        help="Comma-separated recurrent ONNX state inputs, for example h_in.",
    )
    parser.add_argument(
        "--policy-state-output-names",
        default="",
        help="Comma-separated recurrent ONNX state outputs, for example h_out.",
    )
    parser.add_argument(
        "--policy-applied-target-observation",
        action="store_true",
        help="Replace actor obs[83:97] with the external bridge-applied target.",
    )
    parser.add_argument(
        "--policy-observer-fit",
        default=None,
        help=(
            "Default-off evaluator contract: independent fitted bridge used only "
            "for the actor applied-target observation."
        ),
    )
    parser.add_argument(
        "--policy-reset-com-estimator-input",
        action="store_true",
        help="Enable the environment's reset-latched torso-COM estimator input.",
    )
    parser.add_argument(
        "--trace-dir",
        type=Path,
        help="Optional output directory for one JSONL closed-loop trace per run.",
    )
    parser.add_argument(
        "--trace-full-obs",
        action="store_true",
        help="Include the complete actor observation in traces (requires --trace-dir).",
    )
    parser.add_argument(
        "--trace-com-accelerometer-map-ticks",
        default="",
        help=(
            "Default-off reporting only: comma-separated pre-policy ticks at "
            "which to read matched torso-COM accelerometer branches."
        ),
    )
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
    parser.add_argument(
        "--eval-dynamics-override-json",
        default=None,
        help="R2 contract-only JSON object containing exactly one dynamics axis.",
    )
    parser.add_argument(
        "--reset-mode",
        choices=("home-support", "playground"),
        default="home-support",
        help=(
            "Ground-up nominal gates require deterministic home-support. "
            "Playground is retained only for explicit randomized-reset diagnostics."
        ),
    )
    parser.add_argument("--policy-action-rate-limit-rad-s", type=float, default=None)
    parser.add_argument(
        "--policy-action-rate-limit-joint-indices",
        default="2,3,4,11,12,13",
    )
    parser.add_argument("--policy-action-rate-limit-values", default="")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", default=None)
    args = parser.parse_args()
    if args.trace_full_obs and args.trace_dir is None:
        parser.error("--trace-full-obs requires --trace-dir")
    if args.trace_com_accelerometer_map_ticks and args.trace_dir is None:
        parser.error("--trace-com-accelerometer-map-ticks requires --trace-dir")
    if args.trace_dir is not None:
        args.trace_dir.mkdir(parents=True, exist_ok=True)
    payload = evaluate(args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if args.output_md:
        write_markdown(payload, Path(args.output_md))
    print(json.dumps({"status": payload["status"], **payload["aggregate"]}, sort_keys=True))


if __name__ == "__main__":
    main()
