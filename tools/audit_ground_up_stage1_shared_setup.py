#!/usr/bin/env python3
"""Audit objective and curriculum alignment in the ground-up Stage-1 setup."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

import mujoco
import numpy as np
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(text: str, pattern: str, description: str) -> None:
    if re.search(pattern, text, re.MULTILINE) is None:
        raise SystemExit(f"source contract missing {description}: {pattern}")


def scalar_series(path: Path, tag: str) -> list[dict[str, float | int]]:
    events = EventAccumulator(str(path))
    events.Reload()
    return [
        {"step": int(item.step), "value": float(item.value)}
        for item in events.Scalars(tag)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--event", action="append", default=[], help="ID=event-file")
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    root = args.playground_root.resolve()
    sys.path.insert(0, str(root))
    from playground.common.poly_reference_motion_numpy import PolyReferenceMotion
    from playground.open_duck_mini_v2 import joystick

    joystick_path = root / "playground/open_duck_mini_v2/joystick.py"
    rewards_path = root / "playground/common/rewards.py"
    imitation_path = root / "playground/open_duck_mini_v2/custom_rewards.py"
    runner_path = root / "playground/open_duck_mini_v2/runner.py"
    randomize_path = root / "playground/common/randomize.py"
    reference_path = root / "playground/open_duck_mini_v2/data/polynomial_coefficients.pkl"
    xml_path = root / "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml"

    joystick_text = joystick_path.read_text()
    rewards_text = rewards_path.read_text()
    imitation_text = imitation_path.read_text()
    runner_text = runner_path.read_text()
    prereg_text = args.preregistration.read_text()
    require(joystick_text, r"USE_IMITATION_REWARD\s*=\s*True", "imitation enabled")
    require(joystick_text, r"state\.info\[\"imitation_i\"\]\s*\+=\s*1", "fixed phase advance")
    require(joystick_text, r'"imitation_i"\s*:\s*0', "phase-zero reset")
    require(joystick_text, r'"imitation_phase"\s*:\s*jp\.zeros\(2\)', "zero phase-vector reset")
    require(joystick_text, r"push_config\.enable", "push application")
    require(runner_text, r"self\.randomizer\s*=\s*randomize\.domain_randomize", "domain randomization")
    require(imitation_text, r"reward \*= cmd_norm > 0\.01", "zero-command imitation mask")
    require(joystick_text, r"jp\.clip\(sum\(rewards\.values\(\)\) \* self\.dt, 0\.0", "reward clipping")
    require(prereg_text, r"Nominal flat backlash reference tracking", "nominal first stage")
    require(prereg_text, r"Mild pushes", "later push stage")

    config = joystick.default_config()
    prm = PolyReferenceMotion(str(reference_path))
    dxs = np.asarray(prm.dxs, dtype=float)
    command_min, command_max = map(float, config.ground_up_forward_command_range)
    command_samples = np.linspace(command_min, command_max, 100_001)
    nearest_indices = np.abs(command_samples[:, None] - dxs[None, :]).argmin(axis=1)
    unique, counts = np.unique(nearest_indices, return_counts=True)
    command_mapping = [
        {
            "reference_dx": float(dxs[index]),
            "sample_fraction": float(count / command_samples.size),
        }
        for index, count in zip(unique, counts)
    ]

    model = mujoco.MjModel.from_xml_path(str(xml_path))
    key_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "home")
    home_qpos = model.key_qpos[key_id]
    home_actions = np.asarray([
        home_qpos[model.jnt_qposadr[model.actuator_trnid[index, 0]]]
        for index in range(model.nu)
    ])
    home_legs = np.r_[home_actions[:5], home_actions[9:]]
    reference_dx = float(dxs[np.abs(dxs - 0.08).argmin()])
    phase_rows = []
    for phase in range(int(prm.nb_steps_in_period)):
        frame = np.asarray(prm.get_reference_motion(reference_dx, 0.0, 0.0, phase))
        reference_legs = np.r_[frame[:5], frame[11:16]]
        contacts = (frame[32:34] > 0.5).astype(int)
        phase_rows.append({
            "phase": phase,
            "leg_pose_squared_error_from_home": float(np.square(reference_legs - home_legs).sum()),
            "leg_pose_l1_error_from_home": float(np.abs(reference_legs - home_legs).sum()),
            "reference_contacts": contacts.tolist(),
            "double_support": bool(contacts.sum() == 2),
        })
    best_double = min(
        (row for row in phase_rows if row["double_support"]),
        key=lambda row: row["leg_pose_squared_error_from_home"],
    )

    scales = config.reward_config.scales
    sigma = float(config.reward_config.tracking_sigma)
    core_rows = []
    for command in (0.04, 0.074, 0.08, 0.12):
        stationary_lin = float(np.exp(-(command**2) / sigma))
        stationary = float(scales.alive + scales.tracking_ang_vel + scales.tracking_lin_vel * stationary_lin)
        perfect = float(scales.alive + scales.tracking_ang_vel + scales.tracking_lin_vel)
        core_rows.append({
            "command_x": command,
            "stationary_tracking_lin_reward_fraction": stationary_lin,
            "stationary_positive_core_reward": stationary,
            "perfect_positive_core_reward": perfect,
            "stationary_core_retention_fraction": stationary / perfect,
        })

    training_metrics = {}
    tags = (
        "eval/episode_reward",
        "eval/episode_reward/alive",
        "eval/episode_reward/imitation",
        "eval/episode_reward/tracking_lin_vel",
        "eval/avg_episode_length",
    )
    for value in args.event:
        candidate, separator, filename = value.partition("=")
        if not separator:
            raise SystemExit("--event must be ID=event-file")
        event_path = Path(filename).resolve()
        training_metrics[candidate] = {
            "event_path": str(event_path),
            "event_sha256": sha256(event_path),
            "series": {tag: scalar_series(event_path, tag) for tag in tags},
        }

    payload = {
        "schema_version": "ground_up_stage1_shared_setup_audit.v1",
        "status": "OBJECTIVE_AND_CURRICULUM_MISMATCH_FOUND",
        "source_contract": {
            str(path): sha256(path) for path in (
                joystick_path, rewards_path, imitation_path, runner_path,
                randomize_path, reference_path, xml_path, args.preregistration.resolve(),
            )
        },
        "reference": {
            "period_s": float(prm.period),
            "fps": int(prm.fps),
            "phase_steps": int(prm.nb_steps_in_period),
            "dx_cells": dxs.tolist(),
            "positive_command_mapping": command_mapping,
            "phase_zero": phase_rows[0],
            "reset_phase_vector": [0.0, 0.0],
            "reset_phase_vector_norm": 0.0,
            "cyclic_phase_vectors_after_first_step_have_unit_norm": True,
            "closest_home_compatible_double_support_phase": best_double,
        },
        "objective": {
            "scales": {key: float(value) for key, value in scales.items()},
            "tracking_sigma": sigma,
            "stationary_vs_perfect_positive_core": core_rows,
            "zero_command_imitation_masked": True,
            "total_step_reward_clipped_below_at_zero": True,
        },
        "curriculum": {
            "preregistered_order": [
                "nominal_flat_backlash_reference_tracking",
                "measured_actuator_model",
                "zero_and_positive_command_mixture",
                "sensor_mass_friction_initialization_variation",
                "mild_pushes",
                "rough_terrain_last",
            ],
            "implemented_single_stage": True,
            "domain_randomization_active_from_first_update": True,
            "pushes_active_from_first_update": bool(config.push_config.enable),
            "push_interval_s": list(map(float, config.push_config.interval_range)),
            "sensor_noise_level": float(config.noise_config.level),
            "action_delay_steps": [
                int(config.noise_config.action_min_delay),
                int(config.noise_config.action_max_delay),
            ],
            "imu_delay_steps": [
                int(config.noise_config.imu_min_delay),
                int(config.noise_config.imu_max_delay),
            ],
            "reset_joint_multiplier_range": [0.5, 1.5],
            "zero_command_probability": float(config.ground_up_zero_command_probability),
            "positive_command_range": [command_min, command_max],
        },
        "training_objective_diagnostics_only": training_metrics,
        "decision": {
            "reference_was_used_from_start": True,
            "clean_nominal_reference_bootstrap_was_used": False,
            "training_reward_is_policy_selection_metric": False,
            "next_experiment_requires_preregistration": True,
        },
    }

    lines = [
        "# Ground-Up Stage-One Shared Setup Audit",
        "",
        "status: `OBJECTIVE_AND_CURRICULUM_MISMATCH_FOUND`",
        "",
        "## Finding",
        "",
        "The reference motion was active from the first update, but the declared staged curriculum was not implemented as stages. Domain randomization, reset/sensor noise, action and IMU delay, and mild pushes were active from the first update.",
        "",
        f"Reference phase 0 requests contacts `{phase_rows[0]['reference_contacts']}` and has home-pose squared leg error `{phase_rows[0]['leg_pose_squared_error_from_home']:.6f}`. The deterministic closest home-compatible double-support phase is `{best_double['phase']}`, with squared error `{best_double['leg_pose_squared_error_from_home']:.6f}`.",
        "",
        "The actor's reset phase feature is `[0,0]` (norm 0), while every normal cyclic phase feature after the first step has norm 1. Thus the first action of every episode receives an out-of-contract phase sentinel rather than the reset reference phase.",
        "",
        "The continuous positive-command sampler does not produce a continuous reference target:",
        "",
        "| discrete reference dx | training-sample fraction |",
        "|---:|---:|",
    ]
    for row in command_mapping:
        if row["sample_fraction"] > 0:
            lines.append(f"| {row['reference_dx']:.3f} | {100 * row['sample_fraction']:.3f}% |")
    lines.extend([
        "",
        "The positive core objective (alive + angular tracking + linear tracking) weakly separates stationary behavior from exact speed tracking:",
        "",
        "| command x | stationary linear term | stationary core | perfect core | retained |",
        "|---:|---:|---:|---:|---:|",
    ])
    for row in core_rows:
        lines.append(
            f"| {row['command_x']:.3f} | {row['stationary_tracking_lin_reward_fraction']:.4f} | "
            f"{row['stationary_positive_core_reward']:.4f} | {row['perfect_positive_core_reward']:.4f} | "
            f"{100 * row['stationary_core_retention_fraction']:.2f}% |"
        )
    lines.extend([
        "",
        "These are objective diagnostics, not policy-selection metrics. The completed behavior gates remain authoritative.",
        "",
        "## Supported next step",
        "",
        "Preregister a nominal reference-bootstrap screen before more architecture or scalar search. It must isolate a clean nominal stage and test deterministic home-compatible phase alignment before adding zero-command mixing, randomization, delay, pushes, or rough terrain. No training is authorized by this audit alone.",
        "",
        "No robot, RDK-X5, local GPU, iGPU, or onboard GPU access occurred.",
        "",
    ])

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({
        "status": payload["status"],
        "phase_zero_error": phase_rows[0]["leg_pose_squared_error_from_home"],
        "best_double_support_phase": best_double["phase"],
        "command_mapping": command_mapping,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
