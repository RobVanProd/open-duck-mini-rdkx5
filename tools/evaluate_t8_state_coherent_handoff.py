#!/usr/bin/env python3
"""Evaluate the T8 state-coherent support-to-locomotion handoff on CPU."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any


# Keep JAX on CPU before the versioned evaluator module is loaded.
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["XLA_PYTHON_CLIENT_PREALLOCATE"] = "false"

import t8_state_coherent_eval_adapter as adapter  # noqa: E402


EXPECTED_CALIBRATOR_SHA256 = (
    "0f3aebfd9946a6271fdb14adec3d68d556648f270984639d372c973a7d7dc576"
)
COMMANDS = (0.0, 0.074, 0.077, 0.08)
SEED = 167931544
FREQUENCY_HZ = 50
CALIBRATION_TICKS = 250
HOME_RETURN_TICKS = 0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_commands(text: str) -> tuple[float, ...]:
    values = tuple(float(item.strip()) for item in text.split(",") if item.strip())
    if values != COMMANDS:
        raise ValueError(f"T8 commands changed: {values}")
    return values


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


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
) -> dict[str, Any]:
    """Reproduce the frozen ground-up gait-emergence evidence extraction."""

    fitted = (result.get("modes") or {}).get("fitted")
    if not fitted:
        return {
            "pass": False,
            "reasons": ["missing_fitted_mode"],
            "command_x": command_x,
        }

    reasons: list[str] = []
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
        "minimum_emergence_duration_s": 1.08,
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--fit", type=Path, required=True)
    parser.add_argument("--reference-feature-table", type=Path, required=True)
    parser.add_argument("--calibrator", type=Path, required=True)
    parser.add_argument(
        "--calibrator-sha256", default=EXPECTED_CALIBRATOR_SHA256
    )
    parser.add_argument("--commands", default="0.0,0.074,0.077,0.08")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--duration-s", type=float, default=12.0)
    parser.add_argument("--trace-dir", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    commands = parse_commands(args.commands)
    if args.seed != SEED or args.duration_s != 12.0:
        raise ValueError("T8 seed or duration changed")
    policy = args.policy.resolve()
    playground = args.playground_root.resolve()
    fit_path = args.fit.resolve()
    reference = args.reference_feature_table.resolve()
    calibrator = args.calibrator.resolve()
    if sha256(calibrator) != args.calibrator_sha256:
        raise RuntimeError("T8 calibrator hash changed")
    fit = json.loads(fit_path.read_text(encoding="utf-8"))
    module = adapter.load_module()
    args.trace_dir.mkdir(parents=True, exist_ok=True)

    runs = []
    for command_x in commands:
        trace_path = (
            args.trace_dir
            / f"x{command_x:.3f}_seed{args.seed}_{policy.stem}.jsonl"
        )
        result = module.run_closed_loop_sim(
            module.ClosedLoopConfig(
                policy_path=policy,
                fit=fit,
                playground_root=playground,
                command_x=command_x,
                duration_s=args.duration_s,
                bridge_mode="fitted",
                expected_observation_dim=115,
                expected_action_dim=14,
                task="flat_terrain_backlash",
                seed=args.seed,
                eval_role="candidate",
                reset_mode="home-support",
                policy_state_input_names=("previous_action", "h_in"),
                policy_state_output_names=("previous_action_out", "h_out"),
                policy_context_input_name="calibration_context",
                policy_graph_authoritative_output=True,
                response_calibrator_path=calibrator,
                response_calibrator_sha256=args.calibrator_sha256,
                response_calibration_ticks=CALIBRATION_TICKS,
                response_home_return_ticks=HOME_RETURN_TICKS,
                response_preserve_handoff_state=True,
                policy_applied_target_observation=True,
                eval_dynamics_override={"torso_com_offset_m": [0.0, 0.0, 0.0]},
                trace_jsonl=trace_path,
                trace_full_obs=True,
                reference_feature_table_path=reference,
                reference_start_phase=0,
            )
        )
        runs.append(
            {
                "command_x": command_x,
                "seed": args.seed,
                "status": result.get("status"),
                "candidate_gate": result.get("candidate_gate"),
                "emergence": emergence_evidence(
                    result, command_x, args.duration_s
                ),
                "modes": result.get("modes"),
                "dynamics_override": (
                    (result.get("insertion_point") or {}).get(
                        "dynamics_override"
                    )
                ),
                "policy_io": result.get("policy_io"),
                "response_calibration": result.get("response_calibration"),
                "error": result.get("error"),
                "trace_jsonl": str(trace_path),
            }
        )

    payload = {
        "schema_version": "open_duck.t8_state_coherent_handoff_evaluation.v1",
        "status": "COMPLETE_T8_STATE_COHERENT_HANDOFF_BLOCK",
        "execution": {
            "platform": "cpu",
            "cuda_visible_devices": os.environ["CUDA_VISIBLE_DEVICES"],
            "jax_platforms": os.environ["JAX_PLATFORMS"],
            "optimizer_updates": 0,
            "robot_or_rdk_access": 0,
        },
        "inputs": {
            "policy": str(policy),
            "policy_sha256": sha256(policy),
            "playground_root": str(playground),
            "fit": str(fit_path),
            "fit_sha256": sha256(fit_path),
            "reference_feature_table": str(reference),
            "reference_feature_table_sha256": sha256(reference),
            "calibrator": str(calibrator),
            "calibrator_sha256": args.calibrator_sha256,
            "commands": list(commands),
            "seed": args.seed,
            "duration_s": args.duration_s,
            "calibration_ticks": CALIBRATION_TICKS,
            "home_return_ticks": HOME_RETURN_TICKS,
            "preserve_handoff_state": True,
            "expected_observation_dim": 115,
            "expected_action_dim": 14,
            "policy_state_input_names": ["previous_action", "h_in"],
            "policy_state_output_names": ["previous_action_out", "h_out"],
            "policy_context_input_name": "calibration_context",
            "policy_graph_authoritative_output": True,
            "policy_applied_target_observation": True,
            "reference_start_phase": 0,
            "eval_dynamics_override": {
                "torso_com_offset_m": [0.0, 0.0, 0.0]
            },
            "adapter": adapter.contract(),
        },
        "runs": runs,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "runs": len(runs),
                "duration_complete": sum(
                    (run.get("emergence") or {}).get("termination_reason")
                    == "duration_complete"
                    for run in runs
                ),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
