#!/usr/bin/env python3
"""Plan or run a staged locomotion curriculum for actuator-bridge training.

The current candidate search is stuck between unsafe motion and safe
standstill. This helper defines a staged offline training recipe that first
bootstraps forward locomotion, then gradually reintroduces the measured actuator
bridge. It does not touch the robot, SSH, deploy, or modify runtime behavior.

By default this writes a plan only. Pass ``--run`` to execute the phases through
``tools/run_actuator_bridge_training_smoke.py`` in the selected Python/env.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
import datetime as dt
import json
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_ENV_PYTHON = ROOT.parent / "envs/open-duck-playground/bin/python"
DEFAULT_OUTPUT_ROOT = Path("/tmp/open_duck_staged_curriculum")
DEFAULT_PLAN_MD = ROOT / "outputs" / "analysis" / "STAGED_CURRICULUM_TRAINING_PLAN.md"
DEFAULT_PLAN_JSON = ROOT / "outputs" / "analysis" / "staged_curriculum_training_plan.json"


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def cli_value(value: Any) -> str:
    if isinstance(value, float):
        text = f"{value:.12f}".rstrip("0").rstrip(".")
        return text if text not in {"", "-0"} else "0"
    return str(value)


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def parse_seed_text(value: str | None) -> list[int]:
    if value is None:
        return []
    seeds: list[int] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text)
            end = int(end_text)
            step = 1 if end >= start else -1
            seeds.extend(range(start, end + step, step))
        else:
            seeds.append(int(part))
    deduped: list[int] = []
    seen: set[int] = set()
    for seed in seeds:
        if seed not in seen:
            deduped.append(seed)
            seen.add(seed)
    return deduped


def command_label(command_x: float) -> str:
    text = f"{command_x:+.3f}".replace("+", "p").replace("-", "m").replace(".", "p")
    return f"x{text}"


@dataclass(frozen=True)
class Phase:
    name: str
    purpose: str
    num_timesteps: int
    bridge: bool
    delay: tuple[int, int]
    tau_s: tuple[float, float]
    velocity_limit_rad_s: tuple[float, float]
    target_rate_scale: float
    actuator_tracking_scale: float
    tracking_lin_vel_scale: float
    tracking_sigma: float
    forward_progress_scale: float
    forward_shortfall_scale: float
    forward_shortfall_required_ratio: float
    action_rate_scale: float
    action_magnitude_scale: float
    stand_still_scale: float
    alive_scale: float
    imitation_scale: float
    lin_vel_x: tuple[float, float]
    zero_command_probability: float
    forward_overshoot_scale: float = 0.0
    forward_overshoot_allowed_ratio: float = 1.5
    forward_wrong_direction_scale: float = 0.0
    forward_wrong_direction_allowed_reverse_ratio: float = 0.1
    orientation_scale: float = 0.0
    base_height_scale: float = 0.0
    forward_pitch_scale: float = 0.0
    forward_pitch_rate_scale: float = 0.0
    forward_contact_support_scale: float = 0.0
    forward_contact_support_no_contact_weight: float = 1.0
    forward_contact_support_asymmetry_weight: float = 0.0
    forward_single_support_scale: float = 0.0
    forward_double_support_scale: float = 0.0
    ppo_learning_rate: float | None = None
    ppo_entropy_cost: float | None = None
    ppo_clipping_epsilon: float | None = None
    ppo_max_grad_norm: float | None = None
    command_progress_scale: float = 0.0
    command_progress_shortfall_scale: float = 0.0
    command_progress_failure_scale: float = 0.0
    command_progress_required_ratio: float = 0.6
    command_progress_warmup_steps: int = 50
    command_progress_failure_enable: bool = False
    command_progress_failure_min_ratio: float = 0.25
    command_progress_failure_warmup_steps: int = 120
    reward_clip_min: float = 0.0
    reward_clip_max: float = 10000.0
    action_rate_huber_delta: float = 0.0
    action_magnitude_huber_delta: float = 0.0
    target_rate_huber_delta: float = 0.0
    actuator_tracking_huber_delta: float = 0.0
    forward_shortfall_huber_delta: float = 0.0
    forward_overshoot_huber_delta: float = 0.0
    forward_wrong_direction_huber_delta: float = 0.0
    forward_pitch_huber_delta: float = 0.0
    forward_pitch_rate_huber_delta: float = 0.0
    command_progress_shortfall_huber_delta: float = 0.0
    phase_gate_bridge_mode: str | None = None
    reference_motion_override: str | None = None
    soft_prior_config_json: str | None = None
    soft_prior_scale: float = 0.0
    soft_prior_huber_delta: float = 0.05
    soft_prior_phase_source: str = "imitation_i"


RECIPE_DEFAULT_PHASE_GATE_COMMAND_X = {
    "movement_bootstrap_v23": 0.04,
    "movement_bootstrap_v22": 0.04,
    "movement_bootstrap_v21": 0.04,
    "movement_bootstrap_v20": 0.04,
    "movement_bootstrap_v19": 0.04,
    "movement_bootstrap_v18": 0.04,
}


SHORTFALL_V1_PHASES = [
    Phase(
        name="phase1_locomotion_bootstrap_no_bridge",
        purpose="force forward intent before actuator constraints make standing easy",
        num_timesteps=300_000,
        bridge=False,
        delay=(0, 0),
        tau_s=(0.0, 0.0),
        velocity_limit_rad_s=(5.24, 5.24),
        target_rate_scale=0.0,
        actuator_tracking_scale=0.0,
        tracking_lin_vel_scale=35.0,
        tracking_sigma=0.0025,
        forward_progress_scale=6.0,
        forward_shortfall_scale=-2.0,
        forward_shortfall_required_ratio=0.4,
        action_rate_scale=-0.02,
        action_magnitude_scale=-0.005,
        stand_still_scale=-0.6,
        alive_scale=0.2,
        imitation_scale=0.1,
        lin_vel_x=(0.06, 0.14),
        zero_command_probability=0.0,
    ),
    Phase(
        name="phase2_mild_bridge_transition",
        purpose="keep forward motion while introducing mild delay/lag/velocity limits",
        num_timesteps=250_000,
        bridge=True,
        delay=(1, 3),
        tau_s=(0.02, 0.06),
        velocity_limit_rad_s=(4.0, 5.24),
        target_rate_scale=-0.004,
        actuator_tracking_scale=-0.25,
        tracking_lin_vel_scale=30.0,
        tracking_sigma=0.0025,
        forward_progress_scale=5.0,
        forward_shortfall_scale=-3.0,
        forward_shortfall_required_ratio=0.45,
        action_rate_scale=-0.04,
        action_magnitude_scale=-0.01,
        stand_still_scale=-0.5,
        alive_scale=0.25,
        imitation_scale=0.15,
        lin_vel_x=(0.05, 0.13),
        zero_command_probability=0.0,
    ),
    Phase(
        name="phase3_fitted_bridge_consolidation",
        purpose="train under the fitted actuator envelope used by the candidate gates",
        num_timesteps=300_000,
        bridge=True,
        delay=(3, 8),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 4.7),
        target_rate_scale=-0.01,
        actuator_tracking_scale=-0.75,
        tracking_lin_vel_scale=25.0,
        tracking_sigma=0.0025,
        forward_progress_scale=4.0,
        forward_shortfall_scale=-4.0,
        forward_shortfall_required_ratio=0.5,
        action_rate_scale=-0.08,
        action_magnitude_scale=-0.02,
        stand_still_scale=-0.4,
        alive_scale=0.3,
        imitation_scale=0.2,
        lin_vel_x=(0.04, 0.12),
        zero_command_probability=0.05,
    ),
]


MOVEMENT_BOOTSTRAP_V2_PHASES = [
    Phase(
        name="phase1_motion_prior_no_bridge",
        purpose=(
            "force visible gait-like forward motion at a higher command floor "
            "before actuator constraints are introduced"
        ),
        num_timesteps=400_000,
        bridge=False,
        delay=(0, 0),
        tau_s=(0.0, 0.0),
        velocity_limit_rad_s=(5.24, 5.24),
        target_rate_scale=0.0,
        actuator_tracking_scale=0.0,
        tracking_lin_vel_scale=30.0,
        tracking_sigma=0.00125,
        forward_progress_scale=10.0,
        forward_shortfall_scale=-8.0,
        forward_shortfall_required_ratio=0.75,
        action_rate_scale=-0.005,
        action_magnitude_scale=-0.001,
        stand_still_scale=-1.0,
        alive_scale=0.05,
        imitation_scale=0.75,
        lin_vel_x=(0.08, 0.16),
        zero_command_probability=0.0,
    ),
    Phase(
        name="phase2_mild_bridge_keep_motion",
        purpose=(
            "retain discovered forward motion while adding mild delay, lag, "
            "and target-rate pressure"
        ),
        num_timesteps=300_000,
        bridge=True,
        delay=(1, 2),
        tau_s=(0.02, 0.05),
        velocity_limit_rad_s=(4.5, 5.24),
        target_rate_scale=-0.002,
        actuator_tracking_scale=-0.15,
        tracking_lin_vel_scale=30.0,
        tracking_sigma=0.00125,
        forward_progress_scale=8.0,
        forward_shortfall_scale=-8.0,
        forward_shortfall_required_ratio=0.70,
        action_rate_scale=-0.02,
        action_magnitude_scale=-0.005,
        stand_still_scale=-0.8,
        alive_scale=0.10,
        imitation_scale=0.60,
        lin_vel_x=(0.06, 0.14),
        zero_command_probability=0.0,
    ),
    Phase(
        name="phase3_fitted_bridge_preserve_motion",
        purpose=(
            "move toward the measured actuator envelope while keeping the "
            "minimum command high enough to avoid the standstill basin"
        ),
        num_timesteps=350_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(3.0, 4.7),
        target_rate_scale=-0.006,
        actuator_tracking_scale=-0.45,
        tracking_lin_vel_scale=28.0,
        tracking_sigma=0.00125,
        forward_progress_scale=6.0,
        forward_shortfall_scale=-6.0,
        forward_shortfall_required_ratio=0.60,
        action_rate_scale=-0.04,
        action_magnitude_scale=-0.01,
        stand_still_scale=-0.5,
        alive_scale=0.15,
        imitation_scale=0.40,
        lin_vel_x=(0.06, 0.12),
        zero_command_probability=0.0,
    ),
]


MOVEMENT_BOOTSTRAP_V3_PHASES = [
    Phase(
        name="phase1_window_progress_no_bridge",
        purpose=(
            "force sustained command-window displacement before adding "
            "actuator constraints"
        ),
        num_timesteps=450_000,
        bridge=False,
        delay=(0, 0),
        tau_s=(0.0, 0.0),
        velocity_limit_rad_s=(5.24, 5.24),
        target_rate_scale=0.0,
        actuator_tracking_scale=0.0,
        tracking_lin_vel_scale=26.0,
        tracking_sigma=0.00125,
        forward_progress_scale=8.0,
        forward_shortfall_scale=-6.0,
        forward_shortfall_required_ratio=0.65,
        action_rate_scale=-0.003,
        action_magnitude_scale=-0.001,
        stand_still_scale=-1.0,
        alive_scale=0.03,
        imitation_scale=0.85,
        lin_vel_x=(0.08, 0.16),
        zero_command_probability=0.0,
        command_progress_scale=10.0,
        command_progress_shortfall_scale=-10.0,
        command_progress_required_ratio=0.65,
        command_progress_warmup_steps=40,
    ),
    Phase(
        name="phase2_window_progress_mild_bridge",
        purpose=(
            "preserve sustained displacement while introducing mild actuator "
            "delay and target smoothing"
        ),
        num_timesteps=350_000,
        bridge=True,
        delay=(1, 2),
        tau_s=(0.02, 0.05),
        velocity_limit_rad_s=(4.5, 5.24),
        target_rate_scale=-0.0015,
        actuator_tracking_scale=-0.10,
        tracking_lin_vel_scale=28.0,
        tracking_sigma=0.00125,
        forward_progress_scale=7.0,
        forward_shortfall_scale=-6.0,
        forward_shortfall_required_ratio=0.65,
        action_rate_scale=-0.015,
        action_magnitude_scale=-0.004,
        stand_still_scale=-0.8,
        alive_scale=0.08,
        imitation_scale=0.65,
        lin_vel_x=(0.07, 0.14),
        zero_command_probability=0.0,
        command_progress_scale=8.0,
        command_progress_shortfall_scale=-8.0,
        command_progress_required_ratio=0.6,
        command_progress_warmup_steps=40,
    ),
    Phase(
        name="phase3_window_progress_fitted_bridge",
        purpose=(
            "train under the fitted actuator envelope while making sustained "
            "forward progress a non-negotiable objective"
        ),
        num_timesteps=400_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(3.0, 4.7),
        target_rate_scale=-0.004,
        actuator_tracking_scale=-0.35,
        tracking_lin_vel_scale=26.0,
        tracking_sigma=0.00125,
        forward_progress_scale=6.0,
        forward_shortfall_scale=-5.0,
        forward_shortfall_required_ratio=0.6,
        action_rate_scale=-0.03,
        action_magnitude_scale=-0.008,
        stand_still_scale=-0.5,
        alive_scale=0.12,
        imitation_scale=0.45,
        lin_vel_x=(0.06, 0.12),
        zero_command_probability=0.0,
        command_progress_scale=6.0,
        command_progress_shortfall_scale=-8.0,
        command_progress_required_ratio=0.6,
        command_progress_warmup_steps=40,
    ),
]


MOVEMENT_BOOTSTRAP_V4_PHASES = [
    Phase(
        name="phase1_fitted_bridge_x0_stability",
        purpose=(
            "recover zero-command stability under the fitted actuator bridge "
            "before asking for forward motion"
        ),
        num_timesteps=300_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(3.0, 4.7),
        target_rate_scale=-0.004,
        actuator_tracking_scale=-0.45,
        tracking_lin_vel_scale=12.0,
        tracking_sigma=0.0025,
        forward_progress_scale=0.0,
        forward_shortfall_scale=0.0,
        forward_shortfall_required_ratio=0.0,
        action_rate_scale=-0.04,
        action_magnitude_scale=-0.012,
        stand_still_scale=-1.5,
        alive_scale=0.25,
        imitation_scale=0.8,
        lin_vel_x=(0.0, 0.0),
        zero_command_probability=1.0,
        command_progress_scale=0.0,
        command_progress_shortfall_scale=0.0,
        command_progress_required_ratio=0.0,
        command_progress_warmup_steps=50,
    ),
    Phase(
        name="phase2_low_command_mild_bridge",
        purpose=(
            "introduce low positive commands after the stable x0 prior, while "
            "using only mild actuator constraints"
        ),
        num_timesteps=350_000,
        bridge=True,
        delay=(1, 3),
        tau_s=(0.02, 0.06),
        velocity_limit_rad_s=(4.2, 5.24),
        target_rate_scale=-0.002,
        actuator_tracking_scale=-0.18,
        tracking_lin_vel_scale=24.0,
        tracking_sigma=0.0015,
        forward_progress_scale=5.0,
        forward_shortfall_scale=-4.0,
        forward_shortfall_required_ratio=0.45,
        action_rate_scale=-0.02,
        action_magnitude_scale=-0.006,
        stand_still_scale=-0.6,
        alive_scale=0.12,
        imitation_scale=0.65,
        lin_vel_x=(0.04, 0.10),
        zero_command_probability=0.0,
        command_progress_scale=5.0,
        command_progress_shortfall_scale=-5.0,
        command_progress_required_ratio=0.45,
        command_progress_warmup_steps=50,
    ),
    Phase(
        name="phase3_fitted_bridge_stable_progress",
        purpose=(
            "restore the fitted actuator envelope while preserving both x0 "
            "stability and low-command forward progress"
        ),
        num_timesteps=450_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(3.0, 4.7),
        target_rate_scale=-0.004,
        actuator_tracking_scale=-0.35,
        tracking_lin_vel_scale=22.0,
        tracking_sigma=0.0015,
        forward_progress_scale=4.0,
        forward_shortfall_scale=-4.0,
        forward_shortfall_required_ratio=0.45,
        action_rate_scale=-0.035,
        action_magnitude_scale=-0.01,
        stand_still_scale=-0.6,
        alive_scale=0.16,
        imitation_scale=0.55,
        lin_vel_x=(0.04, 0.10),
        zero_command_probability=0.10,
        command_progress_scale=4.0,
        command_progress_shortfall_scale=-5.0,
        command_progress_required_ratio=0.45,
        command_progress_warmup_steps=50,
    ),
]


MOVEMENT_BOOTSTRAP_V5_PHASES = [
    Phase(
        name="phase1_feasible_low_command_mild_bridge",
        purpose=(
            "learn visible forward motion in the target-rate-feasible "
            "x=0.04-0.06 range before pushing toward x=0.08"
        ),
        num_timesteps=350_000,
        bridge=True,
        delay=(1, 3),
        tau_s=(0.02, 0.06),
        velocity_limit_rad_s=(4.0, 5.24),
        target_rate_scale=-0.0015,
        actuator_tracking_scale=-0.12,
        tracking_lin_vel_scale=28.0,
        tracking_sigma=0.0015,
        forward_progress_scale=6.0,
        forward_shortfall_scale=-5.0,
        forward_shortfall_required_ratio=0.50,
        action_rate_scale=-0.018,
        action_magnitude_scale=-0.004,
        stand_still_scale=-0.8,
        alive_scale=0.08,
        imitation_scale=0.60,
        lin_vel_x=(0.04, 0.06),
        zero_command_probability=0.0,
        command_progress_scale=7.0,
        command_progress_shortfall_scale=-7.0,
        command_progress_required_ratio=0.50,
        command_progress_warmup_steps=40,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        command_progress_shortfall_huber_delta=0.35,
    ),
    Phase(
        name="phase2_feasible_low_command_fitted_bridge",
        purpose=(
            "preserve low-command forward progress while moving to the robust "
            "fitted actuator envelope"
        ),
        num_timesteps=450_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.003,
        actuator_tracking_scale=-0.28,
        tracking_lin_vel_scale=26.0,
        tracking_sigma=0.0015,
        forward_progress_scale=5.0,
        forward_shortfall_scale=-5.0,
        forward_shortfall_required_ratio=0.50,
        action_rate_scale=-0.026,
        action_magnitude_scale=-0.006,
        stand_still_scale=-0.6,
        alive_scale=0.12,
        imitation_scale=0.50,
        lin_vel_x=(0.04, 0.06),
        zero_command_probability=0.0,
        command_progress_scale=6.0,
        command_progress_shortfall_scale=-7.0,
        command_progress_required_ratio=0.50,
        command_progress_warmup_steps=40,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        command_progress_shortfall_huber_delta=0.35,
    ),
    Phase(
        name="phase3_expand_toward_x008_fitted_bridge",
        purpose=(
            "expand the command window toward x=0.08 only after the lower "
            "feasible range has a moving gait"
        ),
        num_timesteps=450_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.004,
        actuator_tracking_scale=-0.32,
        tracking_lin_vel_scale=24.0,
        tracking_sigma=0.0015,
        forward_progress_scale=4.5,
        forward_shortfall_scale=-5.0,
        forward_shortfall_required_ratio=0.45,
        action_rate_scale=-0.030,
        action_magnitude_scale=-0.008,
        stand_still_scale=-0.5,
        alive_scale=0.14,
        imitation_scale=0.45,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        command_progress_scale=5.0,
        command_progress_shortfall_scale=-7.0,
        command_progress_required_ratio=0.45,
        command_progress_warmup_steps=40,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        command_progress_shortfall_huber_delta=0.35,
    ),
]


MOVEMENT_BOOTSTRAP_V6_PHASES = [
    Phase(
        name="phase1_recover_in_envelope_motion",
        purpose=(
            "recover the v5 phase-1 lead inside the measured actuator envelope "
            "instead of using a relaxed velocity budget"
        ),
        num_timesteps=350_000,
        bridge=True,
        delay=(1, 3),
        tau_s=(0.03, 0.08),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0015,
        actuator_tracking_scale=-0.12,
        tracking_lin_vel_scale=30.0,
        tracking_sigma=0.0015,
        forward_progress_scale=7.0,
        forward_shortfall_scale=-5.0,
        forward_shortfall_required_ratio=0.45,
        action_rate_scale=-0.016,
        action_magnitude_scale=-0.004,
        stand_still_scale=-0.8,
        alive_scale=0.06,
        imitation_scale=0.60,
        lin_vel_x=(0.06, 0.08),
        zero_command_probability=0.0,
        command_progress_scale=8.0,
        command_progress_shortfall_scale=-8.0,
        command_progress_required_ratio=0.45,
        command_progress_warmup_steps=35,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        command_progress_shortfall_huber_delta=0.35,
        ppo_learning_rate=2.0e-4,
        ppo_clipping_epsilon=0.16,
    ),
    Phase(
        name="phase2_stabilize_motion_low_step",
        purpose=(
            "continue from phase 1 with small PPO updates and light "
            "orientation/base-height costs so stability cannot be bought by "
            "leaving the measured envelope"
        ),
        num_timesteps=300_000,
        bridge=True,
        delay=(2, 5),
        tau_s=(0.05, 0.12),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.002,
        actuator_tracking_scale=-0.20,
        tracking_lin_vel_scale=28.0,
        tracking_sigma=0.0015,
        forward_progress_scale=6.5,
        forward_shortfall_scale=-5.5,
        forward_shortfall_required_ratio=0.45,
        action_rate_scale=-0.020,
        action_magnitude_scale=-0.005,
        stand_still_scale=-0.7,
        alive_scale=0.08,
        imitation_scale=0.55,
        lin_vel_x=(0.06, 0.08),
        zero_command_probability=0.0,
        orientation_scale=-0.15,
        base_height_scale=-1.0,
        command_progress_scale=7.0,
        command_progress_shortfall_scale=-8.0,
        command_progress_required_ratio=0.45,
        command_progress_warmup_steps=35,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        command_progress_shortfall_huber_delta=0.35,
        ppo_learning_rate=1.2e-4,
        ppo_clipping_epsilon=0.10,
        ppo_max_grad_norm=0.8,
    ),
    Phase(
        name="phase3_hold_motion_fitted_bridge",
        purpose=(
            "hold the same x=0.06-0.08 command window under fitted bridge "
            "rather than expanding the task after the gait has not stabilized"
        ),
        num_timesteps=300_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0025,
        actuator_tracking_scale=-0.24,
        tracking_lin_vel_scale=26.0,
        tracking_sigma=0.0015,
        forward_progress_scale=6.0,
        forward_shortfall_scale=-5.5,
        forward_shortfall_required_ratio=0.42,
        action_rate_scale=-0.022,
        action_magnitude_scale=-0.006,
        stand_still_scale=-0.6,
        alive_scale=0.10,
        imitation_scale=0.50,
        lin_vel_x=(0.06, 0.08),
        zero_command_probability=0.0,
        orientation_scale=-0.25,
        base_height_scale=-1.5,
        command_progress_scale=6.5,
        command_progress_shortfall_scale=-8.0,
        command_progress_required_ratio=0.42,
        command_progress_warmup_steps=35,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        command_progress_shortfall_huber_delta=0.35,
        ppo_learning_rate=8.0e-5,
        ppo_clipping_epsilon=0.08,
        ppo_max_grad_norm=0.8,
    ),
]


MOVEMENT_BOOTSTRAP_V7_PHASES = [
    Phase(
        name="phase1_checkpoint_anchor_mild_stability",
        purpose=(
            "continue from the recovered v5 phase-1 moving checkpoint with "
            "small PPO updates, mild bridge dynamics, and light stability "
            "pressure without allowing standstill to satisfy the objective"
        ),
        num_timesteps=160_000,
        bridge=True,
        delay=(1, 3),
        tau_s=(0.02, 0.06),
        velocity_limit_rad_s=(4.0, 5.24),
        target_rate_scale=-0.0015,
        actuator_tracking_scale=-0.12,
        tracking_lin_vel_scale=28.0,
        tracking_sigma=0.0015,
        forward_progress_scale=6.5,
        forward_shortfall_scale=-5.0,
        forward_shortfall_required_ratio=0.45,
        action_rate_scale=-0.018,
        action_magnitude_scale=-0.004,
        stand_still_scale=-0.9,
        alive_scale=0.06,
        imitation_scale=0.55,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        orientation_scale=-0.08,
        base_height_scale=-0.5,
        command_progress_scale=8.0,
        command_progress_shortfall_scale=-8.0,
        command_progress_required_ratio=0.45,
        command_progress_warmup_steps=35,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        command_progress_shortfall_huber_delta=0.35,
        ppo_learning_rate=5.0e-5,
        ppo_clipping_epsilon=0.05,
        ppo_max_grad_norm=0.5,
    ),
    Phase(
        name="phase2_checkpoint_anchor_fitted_bridge",
        purpose=(
            "move the anchored policy toward the fitted actuator envelope "
            "while preserving nonzero forward progress and keeping PPO updates "
            "small"
        ),
        num_timesteps=180_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.002,
        actuator_tracking_scale=-0.18,
        tracking_lin_vel_scale=26.0,
        tracking_sigma=0.0015,
        forward_progress_scale=6.0,
        forward_shortfall_scale=-5.5,
        forward_shortfall_required_ratio=0.40,
        action_rate_scale=-0.020,
        action_magnitude_scale=-0.005,
        stand_still_scale=-0.8,
        alive_scale=0.08,
        imitation_scale=0.50,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        orientation_scale=-0.12,
        base_height_scale=-0.8,
        command_progress_scale=7.0,
        command_progress_shortfall_scale=-8.0,
        command_progress_required_ratio=0.40,
        command_progress_warmup_steps=35,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        command_progress_shortfall_huber_delta=0.35,
        ppo_learning_rate=4.0e-5,
        ppo_clipping_epsilon=0.04,
        ppo_max_grad_norm=0.5,
    ),
]


MOVEMENT_BOOTSTRAP_V8_PHASES = [
    Phase(
        name="phase1_v7_lunge_damping_fitted_bridge",
        purpose=(
            "continue from the v7 anchor and directly penalize the observed "
            "x=0.08 lunge: local forward speed above command, pitch tilt, and "
            "pitch-rate growth under the fitted actuator bridge"
        ),
        num_timesteps=120_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0015,
        actuator_tracking_scale=-0.15,
        tracking_lin_vel_scale=28.0,
        tracking_sigma=0.0015,
        forward_progress_scale=5.5,
        forward_shortfall_scale=-5.0,
        forward_shortfall_required_ratio=0.35,
        action_rate_scale=-0.020,
        action_magnitude_scale=-0.005,
        stand_still_scale=-0.8,
        alive_scale=0.06,
        imitation_scale=0.48,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        forward_overshoot_scale=-3.0,
        forward_overshoot_allowed_ratio=1.35,
        orientation_scale=-0.08,
        base_height_scale=-0.8,
        forward_pitch_scale=-0.35,
        forward_pitch_rate_scale=-0.035,
        command_progress_scale=6.0,
        command_progress_shortfall_scale=-7.0,
        command_progress_required_ratio=0.35,
        command_progress_warmup_steps=35,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        forward_overshoot_huber_delta=0.50,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.35,
        ppo_learning_rate=3.0e-5,
        ppo_clipping_epsilon=0.035,
        ppo_max_grad_norm=0.45,
    ),
    Phase(
        name="phase2_v7_lunge_damping_consolidate",
        purpose=(
            "consolidate the damped gait with the same fitted bridge and "
            "slightly lower overshoot pressure so forward motion is not erased"
        ),
        num_timesteps=120_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0015,
        actuator_tracking_scale=-0.15,
        tracking_lin_vel_scale=28.0,
        tracking_sigma=0.0015,
        forward_progress_scale=6.0,
        forward_shortfall_scale=-5.0,
        forward_shortfall_required_ratio=0.38,
        action_rate_scale=-0.020,
        action_magnitude_scale=-0.005,
        stand_still_scale=-0.8,
        alive_scale=0.06,
        imitation_scale=0.48,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        forward_overshoot_scale=-2.2,
        forward_overshoot_allowed_ratio=1.5,
        orientation_scale=-0.08,
        base_height_scale=-0.8,
        forward_pitch_scale=-0.30,
        forward_pitch_rate_scale=-0.030,
        command_progress_scale=6.5,
        command_progress_shortfall_scale=-7.0,
        command_progress_required_ratio=0.38,
        command_progress_warmup_steps=35,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        forward_overshoot_huber_delta=0.50,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.35,
        ppo_learning_rate=2.5e-5,
        ppo_clipping_epsilon=0.03,
        ppo_max_grad_norm=0.45,
    ),
]


MOVEMENT_BOOTSTRAP_V9_PHASES = [
    Phase(
        name="phase1_v7_progress_recovery_light_damping",
        purpose=(
            "restart from the v7 moving anchor with fitted actuator dynamics, "
            "but use much lighter overshoot/pitch damping than v8 so forward "
            "motion is not erased"
        ),
        num_timesteps=140_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0012,
        actuator_tracking_scale=-0.12,
        tracking_lin_vel_scale=34.0,
        tracking_sigma=0.0012,
        forward_progress_scale=8.5,
        forward_shortfall_scale=-8.0,
        forward_shortfall_required_ratio=0.28,
        action_rate_scale=-0.016,
        action_magnitude_scale=-0.004,
        stand_still_scale=-1.0,
        alive_scale=0.05,
        imitation_scale=0.45,
        lin_vel_x=(0.04, 0.06),
        zero_command_probability=0.0,
        forward_overshoot_scale=-0.9,
        forward_overshoot_allowed_ratio=1.9,
        orientation_scale=-0.06,
        base_height_scale=-0.6,
        forward_pitch_scale=-0.10,
        forward_pitch_rate_scale=-0.010,
        command_progress_scale=11.0,
        command_progress_shortfall_scale=-12.0,
        command_progress_required_ratio=0.28,
        command_progress_warmup_steps=30,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        forward_overshoot_huber_delta=0.50,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.35,
        ppo_learning_rate=3.0e-5,
        ppo_clipping_epsilon=0.035,
        ppo_max_grad_norm=0.45,
    ),
    Phase(
        name="phase2_expand_x008_moderate_damping",
        purpose=(
            "expand back to x=0.08 while increasing damping only enough to "
            "avoid the v7 lunge, keeping command-window progress dominant"
        ),
        num_timesteps=160_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0013,
        actuator_tracking_scale=-0.13,
        tracking_lin_vel_scale=32.0,
        tracking_sigma=0.0012,
        forward_progress_scale=8.0,
        forward_shortfall_scale=-8.0,
        forward_shortfall_required_ratio=0.30,
        action_rate_scale=-0.018,
        action_magnitude_scale=-0.0045,
        stand_still_scale=-1.0,
        alive_scale=0.05,
        imitation_scale=0.44,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        forward_overshoot_scale=-1.3,
        forward_overshoot_allowed_ratio=1.7,
        orientation_scale=-0.07,
        base_height_scale=-0.7,
        forward_pitch_scale=-0.16,
        forward_pitch_rate_scale=-0.016,
        command_progress_scale=10.0,
        command_progress_shortfall_scale=-12.0,
        command_progress_required_ratio=0.30,
        command_progress_warmup_steps=30,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        forward_overshoot_huber_delta=0.50,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.35,
        ppo_learning_rate=2.5e-5,
        ppo_clipping_epsilon=0.03,
        ppo_max_grad_norm=0.45,
    ),
    Phase(
        name="phase3_consolidate_progress_no_lunge",
        purpose=(
            "consolidate the middle ground between v7 and v8: measurable "
            "forward progress, no lunge, no relaxation of the actuator envelope"
        ),
        num_timesteps=120_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0015,
        actuator_tracking_scale=-0.15,
        tracking_lin_vel_scale=30.0,
        tracking_sigma=0.0012,
        forward_progress_scale=7.5,
        forward_shortfall_scale=-8.0,
        forward_shortfall_required_ratio=0.32,
        action_rate_scale=-0.020,
        action_magnitude_scale=-0.005,
        stand_still_scale=-1.0,
        alive_scale=0.05,
        imitation_scale=0.43,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        forward_overshoot_scale=-1.6,
        forward_overshoot_allowed_ratio=1.6,
        orientation_scale=-0.08,
        base_height_scale=-0.8,
        forward_pitch_scale=-0.20,
        forward_pitch_rate_scale=-0.020,
        command_progress_scale=9.0,
        command_progress_shortfall_scale=-11.0,
        command_progress_required_ratio=0.32,
        command_progress_warmup_steps=30,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        forward_overshoot_huber_delta=0.50,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.35,
        ppo_learning_rate=2.0e-5,
        ppo_clipping_epsilon=0.025,
        ppo_max_grad_norm=0.45,
    ),
]


MOVEMENT_BOOTSTRAP_V10_PHASES = [
    Phase(
        name="phase1_v7_seed_consistency_recover",
        purpose=(
            "restart from the v7 moving anchor, but target the four observed "
            "V7/V9 seed regimes: lunge, reverse, early support collapse, and "
            "standstill. Keep forward progress dominant while adding explicit "
            "wrong-direction and no-contact support costs."
        ),
        num_timesteps=160_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0012,
        actuator_tracking_scale=-0.12,
        tracking_lin_vel_scale=34.0,
        tracking_sigma=0.0012,
        forward_progress_scale=8.8,
        forward_shortfall_scale=-8.5,
        forward_shortfall_required_ratio=0.30,
        action_rate_scale=-0.016,
        action_magnitude_scale=-0.004,
        stand_still_scale=-1.1,
        alive_scale=0.05,
        imitation_scale=0.42,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        forward_overshoot_scale=-1.0,
        forward_overshoot_allowed_ratio=1.8,
        forward_wrong_direction_scale=-3.0,
        forward_wrong_direction_allowed_reverse_ratio=0.05,
        orientation_scale=-0.06,
        base_height_scale=-0.75,
        forward_pitch_scale=-0.12,
        forward_pitch_rate_scale=-0.012,
        forward_contact_support_scale=-0.35,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.05,
        command_progress_scale=12.0,
        command_progress_shortfall_scale=-12.5,
        command_progress_required_ratio=0.30,
        command_progress_warmup_steps=25,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.35,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.35,
        ppo_learning_rate=2.5e-5,
        ppo_clipping_epsilon=0.03,
        ppo_max_grad_norm=0.45,
    ),
    Phase(
        name="phase2_consistency_stability_balance",
        purpose=(
            "preserve the forward-moving family while tightening lunge and "
            "collapse margins. Keep the fitted actuator envelope fixed and do "
            "not let stability be purchased by freezing."
        ),
        num_timesteps=180_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0014,
        actuator_tracking_scale=-0.14,
        tracking_lin_vel_scale=32.0,
        tracking_sigma=0.0012,
        forward_progress_scale=8.4,
        forward_shortfall_scale=-8.5,
        forward_shortfall_required_ratio=0.32,
        action_rate_scale=-0.018,
        action_magnitude_scale=-0.0045,
        stand_still_scale=-1.1,
        alive_scale=0.05,
        imitation_scale=0.40,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        forward_overshoot_scale=-1.4,
        forward_overshoot_allowed_ratio=1.65,
        forward_wrong_direction_scale=-3.5,
        forward_wrong_direction_allowed_reverse_ratio=0.03,
        orientation_scale=-0.08,
        base_height_scale=-0.9,
        forward_pitch_scale=-0.18,
        forward_pitch_rate_scale=-0.018,
        forward_contact_support_scale=-0.45,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.05,
        command_progress_scale=11.0,
        command_progress_shortfall_scale=-12.0,
        command_progress_required_ratio=0.32,
        command_progress_warmup_steps=25,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.35,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.35,
        ppo_learning_rate=2.0e-5,
        ppo_clipping_epsilon=0.025,
        ppo_max_grad_norm=0.45,
    ),
    Phase(
        name="phase3_consolidate_consistent_forward_gait",
        purpose=(
            "final consolidation pass for one coherent in-envelope forward "
            "behavior across seeds. This is the last planned run in the V7/V9 "
            "lineage unless the eight-seed distribution moves materially."
        ),
        num_timesteps=140_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0015,
        actuator_tracking_scale=-0.15,
        tracking_lin_vel_scale=30.0,
        tracking_sigma=0.0012,
        forward_progress_scale=8.0,
        forward_shortfall_scale=-8.2,
        forward_shortfall_required_ratio=0.34,
        action_rate_scale=-0.020,
        action_magnitude_scale=-0.005,
        stand_still_scale=-1.0,
        alive_scale=0.05,
        imitation_scale=0.38,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        forward_overshoot_scale=-1.7,
        forward_overshoot_allowed_ratio=1.55,
        forward_wrong_direction_scale=-3.5,
        forward_wrong_direction_allowed_reverse_ratio=0.03,
        orientation_scale=-0.09,
        base_height_scale=-0.95,
        forward_pitch_scale=-0.22,
        forward_pitch_rate_scale=-0.022,
        forward_contact_support_scale=-0.5,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.05,
        command_progress_scale=10.0,
        command_progress_shortfall_scale=-11.0,
        command_progress_required_ratio=0.34,
        command_progress_warmup_steps=25,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.35,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.35,
        ppo_learning_rate=1.8e-5,
        ppo_clipping_epsilon=0.025,
        ppo_max_grad_norm=0.45,
    ),
]


MOVEMENT_BOOTSTRAP_V11_PHASES = [
    Phase(
        name="phase1_fresh_hard_progress_floor_low_command",
        purpose=(
            "start a fresh lineage instead of restoring the fragile V7/V9/V10 "
            "anchor. Use a hard non-Huberized forward-progress floor in the "
            "x=0.04-0.06 range so standing still cannot satisfy the objective."
        ),
        num_timesteps=260_000,
        bridge=True,
        delay=(2, 5),
        tau_s=(0.05, 0.12),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0010,
        actuator_tracking_scale=-0.08,
        tracking_lin_vel_scale=42.0,
        tracking_sigma=0.0009,
        forward_progress_scale=18.0,
        forward_shortfall_scale=-36.0,
        forward_shortfall_required_ratio=0.55,
        action_rate_scale=-0.010,
        action_magnitude_scale=-0.0025,
        stand_still_scale=-1.4,
        alive_scale=0.02,
        imitation_scale=0.08,
        lin_vel_x=(0.04, 0.06),
        zero_command_probability=0.0,
        forward_overshoot_scale=-4.0,
        forward_overshoot_allowed_ratio=1.45,
        forward_wrong_direction_scale=-20.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.05,
        base_height_scale=-0.45,
        forward_pitch_scale=-0.08,
        forward_pitch_rate_scale=-0.008,
        forward_contact_support_scale=-0.20,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.02,
        command_progress_scale=24.0,
        command_progress_shortfall_scale=-50.0,
        command_progress_required_ratio=0.55,
        command_progress_warmup_steps=20,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=1.2e-4,
        ppo_clipping_epsilon=0.12,
        ppo_max_grad_norm=0.7,
    ),
    Phase(
        name="phase2_fresh_expand_command_keep_progress_floor",
        purpose=(
            "expand toward x=0.08 after the hard progress floor has made "
            "forward motion dominant. Keep the fitted actuator envelope fixed "
            "and retain strong wrong-direction pressure."
        ),
        num_timesteps=280_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0012,
        actuator_tracking_scale=-0.10,
        tracking_lin_vel_scale=40.0,
        tracking_sigma=0.0009,
        forward_progress_scale=16.0,
        forward_shortfall_scale=-34.0,
        forward_shortfall_required_ratio=0.50,
        action_rate_scale=-0.012,
        action_magnitude_scale=-0.003,
        stand_still_scale=-1.3,
        alive_scale=0.02,
        imitation_scale=0.06,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        forward_overshoot_scale=-5.0,
        forward_overshoot_allowed_ratio=1.35,
        forward_wrong_direction_scale=-22.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.06,
        base_height_scale=-0.55,
        forward_pitch_scale=-0.10,
        forward_pitch_rate_scale=-0.010,
        forward_contact_support_scale=-0.25,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.02,
        command_progress_scale=22.0,
        command_progress_shortfall_scale=-48.0,
        command_progress_required_ratio=0.50,
        command_progress_warmup_steps=20,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=8.0e-5,
        ppo_clipping_epsilon=0.08,
        ppo_max_grad_norm=0.7,
    ),
    Phase(
        name="phase3_fresh_stability_without_freeze",
        purpose=(
            "add stability margin only after forward motion is established. "
            "Keep hard progress and wrong-direction floors active so stability "
            "cannot be purchased by freezing or reversing."
        ),
        num_timesteps=220_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0015,
        actuator_tracking_scale=-0.14,
        tracking_lin_vel_scale=36.0,
        tracking_sigma=0.0010,
        forward_progress_scale=14.0,
        forward_shortfall_scale=-30.0,
        forward_shortfall_required_ratio=0.45,
        action_rate_scale=-0.018,
        action_magnitude_scale=-0.004,
        stand_still_scale=-1.2,
        alive_scale=0.02,
        imitation_scale=0.05,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        forward_overshoot_scale=-6.0,
        forward_overshoot_allowed_ratio=1.30,
        forward_wrong_direction_scale=-22.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.10,
        base_height_scale=-0.85,
        forward_pitch_scale=-0.18,
        forward_pitch_rate_scale=-0.018,
        forward_contact_support_scale=-0.40,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.04,
        command_progress_scale=18.0,
        command_progress_shortfall_scale=-42.0,
        command_progress_required_ratio=0.45,
        command_progress_warmup_steps=20,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=5.0e-5,
        ppo_clipping_epsilon=0.05,
        ppo_max_grad_norm=0.6,
    ),
]


MOVEMENT_BOOTSTRAP_V12_PHASES = [
    replace(
        MOVEMENT_BOOTSTRAP_V11_PHASES[0],
        name="phase1_progress_failure_low_command",
        purpose=(
            "mechanics test after V11 froze: keep the fresh hard-progress "
            "low-command setup, but enable command-progress failure so standing "
            "still ends the episode instead of remaining a viable basin."
        ),
        num_timesteps=220_000,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.25,
        command_progress_failure_warmup_steps=120,
    ),
    replace(
        MOVEMENT_BOOTSTRAP_V11_PHASES[1],
        name="phase2_progress_failure_expand_command",
        purpose=(
            "expand toward x=0.08 only if phase 1 survives the progress-failure "
            "mechanic. Keep fitted actuator limits and terminate persistent "
            "low-progress episodes."
        ),
        num_timesteps=240_000,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.30,
        command_progress_failure_warmup_steps=140,
    ),
    replace(
        MOVEMENT_BOOTSTRAP_V11_PHASES[2],
        name="phase3_progress_failure_stability",
        purpose=(
            "add stability margin without allowing consolidation to freeze: "
            "command-progress failure stays active while posture/support costs "
            "increase."
        ),
        num_timesteps=180_000,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.35,
        command_progress_failure_warmup_steps=150,
    ),
]


MOVEMENT_BOOTSTRAP_V13_PHASES = [
    replace(
        MOVEMENT_BOOTSTRAP_V12_PHASES[0],
        name="phase1_signed_failure_low_command",
        purpose=(
            "mechanics test after V12 froze: keep the same low-command setup, "
            "but make command-progress termination carry a signed penalty and "
            "allow negative terminal reward so standing until failure is not a "
            "cheap local optimum."
        ),
        command_progress_failure_scale=-120.0,
        command_progress_failure_warmup_steps=80,
        reward_clip_min=-10.0,
    ),
    replace(
        MOVEMENT_BOOTSTRAP_V12_PHASES[1],
        name="phase2_signed_failure_expand_command",
        purpose=(
            "expand toward x=0.08 only if the signed failure mechanic survives "
            "phase 1. Keep fitted actuator limits and preserve negative terminal "
            "cost for persistent low-progress episodes."
        ),
        command_progress_failure_scale=-140.0,
        command_progress_failure_warmup_steps=100,
        reward_clip_min=-10.0,
    ),
    replace(
        MOVEMENT_BOOTSTRAP_V12_PHASES[2],
        name="phase3_signed_failure_stability",
        purpose=(
            "add stability margin while signed low-progress termination remains "
            "active, so consolidation cannot buy stability by freezing."
        ),
        command_progress_failure_scale=-160.0,
        command_progress_failure_warmup_steps=120,
        reward_clip_min=-10.0,
    ),
]


MOVEMENT_BOOTSTRAP_V14_PHASES = [
    Phase(
        name="phase1_mild_bridge_motion_discovery",
        purpose=(
            "V13 proved signed progress failure works but did not discover "
            "motion under the fitted bridge from step zero. Start with a mild "
            "bridge so PPO can find low-command forward motion before the full "
            "measured actuator envelope is enforced."
        ),
        num_timesteps=280_000,
        bridge=True,
        delay=(1, 3),
        tau_s=(0.03, 0.08),
        velocity_limit_rad_s=(3.8, 5.24),
        target_rate_scale=-0.0008,
        actuator_tracking_scale=-0.05,
        tracking_lin_vel_scale=36.0,
        tracking_sigma=0.0012,
        forward_progress_scale=16.0,
        forward_shortfall_scale=-24.0,
        forward_shortfall_required_ratio=0.45,
        action_rate_scale=-0.006,
        action_magnitude_scale=-0.0015,
        stand_still_scale=-1.2,
        alive_scale=0.01,
        imitation_scale=0.20,
        lin_vel_x=(0.04, 0.06),
        zero_command_probability=0.0,
        forward_overshoot_scale=-3.0,
        forward_overshoot_allowed_ratio=1.60,
        forward_wrong_direction_scale=-18.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.04,
        base_height_scale=-0.35,
        forward_pitch_scale=-0.06,
        forward_pitch_rate_scale=-0.006,
        forward_contact_support_scale=-0.12,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.02,
        command_progress_scale=18.0,
        command_progress_shortfall_scale=-32.0,
        command_progress_required_ratio=0.45,
        command_progress_warmup_steps=20,
        command_progress_failure_scale=-80.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.20,
        command_progress_failure_warmup_steps=120,
        reward_clip_min=-8.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=1.2e-4,
        ppo_clipping_epsilon=0.12,
        ppo_max_grad_norm=0.7,
    ),
    Phase(
        name="phase2_fitted_bridge_motion_transfer",
        purpose=(
            "Transfer the discovered low-command gait into the fitted actuator "
            "envelope while keeping progress failure active. This phase should "
            "be skipped automatically if phase 1 freezes or fails its gate."
        ),
        num_timesteps=260_000,
        bridge=True,
        delay=(2, 5),
        tau_s=(0.05, 0.12),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0010,
        actuator_tracking_scale=-0.08,
        tracking_lin_vel_scale=38.0,
        tracking_sigma=0.0010,
        forward_progress_scale=16.0,
        forward_shortfall_scale=-28.0,
        forward_shortfall_required_ratio=0.45,
        action_rate_scale=-0.009,
        action_magnitude_scale=-0.002,
        stand_still_scale=-1.2,
        alive_scale=0.01,
        imitation_scale=0.14,
        lin_vel_x=(0.04, 0.06),
        zero_command_probability=0.0,
        forward_overshoot_scale=-4.0,
        forward_overshoot_allowed_ratio=1.45,
        forward_wrong_direction_scale=-20.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.05,
        base_height_scale=-0.45,
        forward_pitch_scale=-0.08,
        forward_pitch_rate_scale=-0.008,
        forward_contact_support_scale=-0.18,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.02,
        command_progress_scale=20.0,
        command_progress_shortfall_scale=-38.0,
        command_progress_required_ratio=0.45,
        command_progress_warmup_steps=20,
        command_progress_failure_scale=-120.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.25,
        command_progress_failure_warmup_steps=100,
        reward_clip_min=-10.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=8.0e-5,
        ppo_clipping_epsilon=0.08,
        ppo_max_grad_norm=0.65,
    ),
    Phase(
        name="phase3_expand_command_with_fitted_bridge",
        purpose=(
            "Expand toward x=0.08 only after low-command fitted-bridge motion "
            "survives. Keep progress failure and wrong-direction pressure active "
            "so stability cannot be bought by freezing or backing up."
        ),
        num_timesteps=220_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0013,
        actuator_tracking_scale=-0.12,
        tracking_lin_vel_scale=36.0,
        tracking_sigma=0.0010,
        forward_progress_scale=14.0,
        forward_shortfall_scale=-30.0,
        forward_shortfall_required_ratio=0.42,
        action_rate_scale=-0.014,
        action_magnitude_scale=-0.003,
        stand_still_scale=-1.1,
        alive_scale=0.01,
        imitation_scale=0.10,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        forward_overshoot_scale=-5.0,
        forward_overshoot_allowed_ratio=1.35,
        forward_wrong_direction_scale=-22.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.08,
        base_height_scale=-0.65,
        forward_pitch_scale=-0.14,
        forward_pitch_rate_scale=-0.014,
        forward_contact_support_scale=-0.30,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.03,
        command_progress_scale=18.0,
        command_progress_shortfall_scale=-42.0,
        command_progress_required_ratio=0.42,
        command_progress_warmup_steps=20,
        command_progress_failure_scale=-150.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.30,
        command_progress_failure_warmup_steps=120,
        reward_clip_min=-10.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=5.0e-5,
        ppo_clipping_epsilon=0.06,
        ppo_max_grad_norm=0.6,
    ),
]


MOVEMENT_BOOTSTRAP_V15_PHASES = [
    Phase(
        name="phase1_no_bridge_high_entropy_gait_discovery",
        purpose=(
            "V14's partial A100 checkpoint was still low-motion under a mild "
            "bridge. Remove actuator-bridge pressure for the first phase, remove "
            "alive/imitation crutches, and raise entropy so PPO has a cleaner "
            "chance to discover any coherent positive-command gait before "
            "actuator realism is reintroduced."
        ),
        num_timesteps=320_000,
        bridge=False,
        delay=(0, 0),
        tau_s=(0.0, 0.0),
        velocity_limit_rad_s=(5.24, 5.24),
        target_rate_scale=-0.0002,
        actuator_tracking_scale=0.0,
        tracking_lin_vel_scale=42.0,
        tracking_sigma=0.0010,
        forward_progress_scale=22.0,
        forward_shortfall_scale=-34.0,
        forward_shortfall_required_ratio=0.50,
        action_rate_scale=-0.003,
        action_magnitude_scale=-0.0005,
        stand_still_scale=-1.8,
        alive_scale=0.0,
        imitation_scale=0.0,
        lin_vel_x=(0.06, 0.10),
        zero_command_probability=0.0,
        forward_overshoot_scale=-2.0,
        forward_overshoot_allowed_ratio=1.80,
        forward_wrong_direction_scale=-28.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.02,
        base_height_scale=-0.20,
        forward_pitch_scale=-0.03,
        forward_pitch_rate_scale=-0.003,
        forward_contact_support_scale=-0.06,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.01,
        command_progress_scale=28.0,
        command_progress_shortfall_scale=-48.0,
        command_progress_required_ratio=0.50,
        command_progress_warmup_steps=20,
        command_progress_failure_scale=-180.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.30,
        command_progress_failure_warmup_steps=100,
        reward_clip_min=-12.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=1.5e-4,
        ppo_entropy_cost=0.02,
        ppo_clipping_epsilon=0.14,
        ppo_max_grad_norm=0.8,
        phase_gate_bridge_mode="vanilla",
    ),
    Phase(
        name="phase2_mild_bridge_gait_transfer",
        purpose=(
            "Only after vanilla discovery survives, reintroduce a mild actuator "
            "bridge while preserving the progress floor. This should reveal "
            "whether the discovered gait is structurally portable before the "
            "full fitted envelope is applied."
        ),
        num_timesteps=260_000,
        bridge=True,
        delay=(1, 3),
        tau_s=(0.03, 0.08),
        velocity_limit_rad_s=(3.6, 5.24),
        target_rate_scale=-0.0008,
        actuator_tracking_scale=-0.04,
        tracking_lin_vel_scale=40.0,
        tracking_sigma=0.0010,
        forward_progress_scale=20.0,
        forward_shortfall_scale=-34.0,
        forward_shortfall_required_ratio=0.48,
        action_rate_scale=-0.006,
        action_magnitude_scale=-0.0015,
        stand_still_scale=-1.5,
        alive_scale=0.0,
        imitation_scale=0.04,
        lin_vel_x=(0.05, 0.08),
        zero_command_probability=0.0,
        forward_overshoot_scale=-3.0,
        forward_overshoot_allowed_ratio=1.60,
        forward_wrong_direction_scale=-26.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.04,
        base_height_scale=-0.35,
        forward_pitch_scale=-0.06,
        forward_pitch_rate_scale=-0.006,
        forward_contact_support_scale=-0.12,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.02,
        command_progress_scale=24.0,
        command_progress_shortfall_scale=-48.0,
        command_progress_required_ratio=0.48,
        command_progress_warmup_steps=20,
        command_progress_failure_scale=-180.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.30,
        command_progress_failure_warmup_steps=100,
        reward_clip_min=-12.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=1.0e-4,
        ppo_entropy_cost=0.01,
        ppo_clipping_epsilon=0.10,
        ppo_max_grad_norm=0.7,
        phase_gate_bridge_mode="fitted",
    ),
    Phase(
        name="phase3_fitted_bridge_gait_consolidation",
        purpose=(
            "Consolidate only a gait that has survived discovery and mild-bridge "
            "transfer. Keep the fitted actuator envelope, progress failure, and "
            "wrong-direction pressure active so the final policy cannot buy "
            "stability by freezing or backing up."
        ),
        num_timesteps=240_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0012,
        actuator_tracking_scale=-0.10,
        tracking_lin_vel_scale=38.0,
        tracking_sigma=0.0010,
        forward_progress_scale=18.0,
        forward_shortfall_scale=-34.0,
        forward_shortfall_required_ratio=0.45,
        action_rate_scale=-0.012,
        action_magnitude_scale=-0.003,
        stand_still_scale=-1.3,
        alive_scale=0.0,
        imitation_scale=0.04,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        forward_overshoot_scale=-5.0,
        forward_overshoot_allowed_ratio=1.35,
        forward_wrong_direction_scale=-28.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.08,
        base_height_scale=-0.65,
        forward_pitch_scale=-0.14,
        forward_pitch_rate_scale=-0.014,
        forward_contact_support_scale=-0.30,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.03,
        command_progress_scale=22.0,
        command_progress_shortfall_scale=-52.0,
        command_progress_required_ratio=0.45,
        command_progress_warmup_steps=20,
        command_progress_failure_scale=-200.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.32,
        command_progress_failure_warmup_steps=120,
        reward_clip_min=-12.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=6.0e-5,
        ppo_entropy_cost=0.004,
        ppo_clipping_epsilon=0.07,
        ppo_max_grad_norm=0.65,
        phase_gate_bridge_mode="fitted",
    ),
]


MOVEMENT_BOOTSTRAP_V17_PHASES = [
    Phase(
        name="phase1_hard_signed_progress_discovery",
        purpose=(
            "fresh structural break after V16 showed no usable V5-anchor "
            "branch point. Discover a low-command gait with signed positive "
            "progress made non-negotiable from the start, while keeping enough "
            "pitch, base-height, and contact pressure active to avoid the old "
            "lunge/collapse modes."
        ),
        num_timesteps=260_000,
        bridge=False,
        delay=(0, 0),
        tau_s=(0.0, 0.0),
        velocity_limit_rad_s=(5.24, 5.24),
        target_rate_scale=-0.0003,
        actuator_tracking_scale=0.0,
        tracking_lin_vel_scale=48.0,
        tracking_sigma=0.0010,
        forward_progress_scale=26.0,
        forward_shortfall_scale=-52.0,
        forward_shortfall_required_ratio=0.55,
        action_rate_scale=-0.004,
        action_magnitude_scale=-0.0008,
        stand_still_scale=-2.2,
        alive_scale=0.0,
        imitation_scale=0.0,
        lin_vel_x=(0.04, 0.06),
        zero_command_probability=0.0,
        forward_overshoot_scale=-4.0,
        forward_overshoot_allowed_ratio=1.55,
        forward_wrong_direction_scale=-42.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.06,
        base_height_scale=-0.45,
        forward_pitch_scale=-0.10,
        forward_pitch_rate_scale=-0.010,
        forward_contact_support_scale=-0.22,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.03,
        command_progress_scale=34.0,
        command_progress_shortfall_scale=-72.0,
        command_progress_required_ratio=0.55,
        command_progress_warmup_steps=15,
        command_progress_failure_scale=-260.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.40,
        command_progress_failure_warmup_steps=60,
        reward_clip_min=-20.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=1.2e-4,
        ppo_entropy_cost=0.018,
        ppo_clipping_epsilon=0.12,
        ppo_max_grad_norm=0.75,
        phase_gate_bridge_mode="vanilla",
    ),
    Phase(
        name="phase2_mild_bridge_signed_progress_transfer",
        purpose=(
            "transfer only a phase-1 policy that already moves forward across "
            "seeds. Keep hard signed-progress failure active while adding mild "
            "actuator delay/lag so the policy cannot solve phase 2 by freezing "
            "or backing up."
        ),
        num_timesteps=220_000,
        bridge=True,
        delay=(1, 3),
        tau_s=(0.03, 0.08),
        velocity_limit_rad_s=(3.6, 4.7),
        target_rate_scale=-0.0009,
        actuator_tracking_scale=-0.06,
        tracking_lin_vel_scale=44.0,
        tracking_sigma=0.0010,
        forward_progress_scale=24.0,
        forward_shortfall_scale=-50.0,
        forward_shortfall_required_ratio=0.52,
        action_rate_scale=-0.008,
        action_magnitude_scale=-0.0018,
        stand_still_scale=-2.0,
        alive_scale=0.0,
        imitation_scale=0.0,
        lin_vel_x=(0.04, 0.06),
        zero_command_probability=0.0,
        forward_overshoot_scale=-4.5,
        forward_overshoot_allowed_ratio=1.45,
        forward_wrong_direction_scale=-42.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.07,
        base_height_scale=-0.55,
        forward_pitch_scale=-0.12,
        forward_pitch_rate_scale=-0.012,
        forward_contact_support_scale=-0.28,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.03,
        command_progress_scale=30.0,
        command_progress_shortfall_scale=-70.0,
        command_progress_required_ratio=0.52,
        command_progress_warmup_steps=15,
        command_progress_failure_scale=-260.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.38,
        command_progress_failure_warmup_steps=70,
        reward_clip_min=-20.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=8.0e-5,
        ppo_entropy_cost=0.010,
        ppo_clipping_epsilon=0.09,
        ppo_max_grad_norm=0.65,
        phase_gate_bridge_mode="vanilla",
    ),
    Phase(
        name="phase3_fitted_bridge_low_command_transfer",
        purpose=(
            "move the same signed-progress behavior into the measured fitted "
            "actuator envelope at low command. Do not expand toward x=0.08 "
            "until this phase passes multi-seed gates without freezing, "
            "reversing, or falling."
        ),
        num_timesteps=220_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0012,
        actuator_tracking_scale=-0.10,
        tracking_lin_vel_scale=40.0,
        tracking_sigma=0.0010,
        forward_progress_scale=22.0,
        forward_shortfall_scale=-48.0,
        forward_shortfall_required_ratio=0.48,
        action_rate_scale=-0.012,
        action_magnitude_scale=-0.0028,
        stand_still_scale=-1.8,
        alive_scale=0.0,
        imitation_scale=0.0,
        lin_vel_x=(0.04, 0.06),
        zero_command_probability=0.0,
        forward_overshoot_scale=-5.0,
        forward_overshoot_allowed_ratio=1.35,
        forward_wrong_direction_scale=-44.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.09,
        base_height_scale=-0.70,
        forward_pitch_scale=-0.15,
        forward_pitch_rate_scale=-0.015,
        forward_contact_support_scale=-0.36,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.04,
        command_progress_scale=26.0,
        command_progress_shortfall_scale=-68.0,
        command_progress_required_ratio=0.48,
        command_progress_warmup_steps=15,
        command_progress_failure_scale=-280.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.35,
        command_progress_failure_warmup_steps=80,
        reward_clip_min=-20.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=5.0e-5,
        ppo_entropy_cost=0.004,
        ppo_clipping_epsilon=0.07,
        ppo_max_grad_norm=0.60,
        phase_gate_bridge_mode="fitted",
    ),
]


MOVEMENT_BOOTSTRAP_V16_PHASES = [
    Phase(
        name="phase1_v5_anchor_mild_bridge_consistency",
        purpose=(
            "continue from the recovered V5 moving checkpoint and repair the "
            "multi-seed lunge/reverse/collapse/freeze split without letting "
            "the objective collapse into standstill. This phase keeps a mild "
            "bridge and strong imitation so the gait shape survives while "
            "wrong-direction, support, and pitch costs reduce fragility."
        ),
        num_timesteps=120_000,
        bridge=True,
        delay=(1, 3),
        tau_s=(0.03, 0.08),
        velocity_limit_rad_s=(3.6, 4.7),
        target_rate_scale=-0.0012,
        actuator_tracking_scale=-0.10,
        tracking_lin_vel_scale=32.0,
        tracking_sigma=0.0012,
        forward_progress_scale=9.0,
        forward_shortfall_scale=-8.0,
        forward_shortfall_required_ratio=0.35,
        action_rate_scale=-0.014,
        action_magnitude_scale=-0.0035,
        stand_still_scale=-1.0,
        alive_scale=0.04,
        imitation_scale=0.55,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        forward_overshoot_scale=-1.0,
        forward_overshoot_allowed_ratio=1.75,
        forward_wrong_direction_scale=-8.0,
        forward_wrong_direction_allowed_reverse_ratio=0.02,
        orientation_scale=-0.05,
        base_height_scale=-0.45,
        forward_pitch_scale=-0.08,
        forward_pitch_rate_scale=-0.008,
        forward_contact_support_scale=-0.25,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.04,
        command_progress_scale=11.0,
        command_progress_shortfall_scale=-12.0,
        command_progress_required_ratio=0.35,
        command_progress_warmup_steps=25,
        command_progress_failure_scale=-80.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.20,
        command_progress_failure_warmup_steps=90,
        reward_clip_min=-10.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.35,
        ppo_learning_rate=2.0e-5,
        ppo_entropy_cost=0.004,
        ppo_clipping_epsilon=0.025,
        ppo_max_grad_norm=0.45,
        phase_gate_bridge_mode="vanilla",
    ),
    Phase(
        name="phase2_v5_anchor_fitted_bridge_consistency",
        purpose=(
            "transfer the repaired V5-anchor behavior into the fitted actuator "
            "envelope while keeping the same multi-seed consistency objective. "
            "This phase should fail fast if the gait survives only in the "
            "relaxed mild-bridge dynamics."
        ),
        num_timesteps=140_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0014,
        actuator_tracking_scale=-0.12,
        tracking_lin_vel_scale=30.0,
        tracking_sigma=0.0012,
        forward_progress_scale=8.5,
        forward_shortfall_scale=-8.0,
        forward_shortfall_required_ratio=0.35,
        action_rate_scale=-0.016,
        action_magnitude_scale=-0.004,
        stand_still_scale=-1.0,
        alive_scale=0.04,
        imitation_scale=0.50,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        forward_overshoot_scale=-1.3,
        forward_overshoot_allowed_ratio=1.65,
        forward_wrong_direction_scale=-9.0,
        forward_wrong_direction_allowed_reverse_ratio=0.02,
        orientation_scale=-0.06,
        base_height_scale=-0.55,
        forward_pitch_scale=-0.10,
        forward_pitch_rate_scale=-0.010,
        forward_contact_support_scale=-0.30,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.04,
        command_progress_scale=10.0,
        command_progress_shortfall_scale=-12.0,
        command_progress_required_ratio=0.35,
        command_progress_warmup_steps=25,
        command_progress_failure_scale=-90.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.20,
        command_progress_failure_warmup_steps=90,
        reward_clip_min=-10.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.35,
        ppo_learning_rate=1.5e-5,
        ppo_entropy_cost=0.003,
        ppo_clipping_epsilon=0.020,
        ppo_max_grad_norm=0.40,
        phase_gate_bridge_mode="fitted",
    ),
    Phase(
        name="phase3_v5_anchor_fitted_bridge_margin",
        purpose=(
            "final low-step consolidation from the V5 anchor: keep the fitted "
            "envelope, preserve positive command tracking, and add only modest "
            "extra margin so the policy cannot buy stability by freezing."
        ),
        num_timesteps=120_000,
        bridge=True,
        delay=(3, 6),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 3.75),
        target_rate_scale=-0.0015,
        actuator_tracking_scale=-0.13,
        tracking_lin_vel_scale=28.0,
        tracking_sigma=0.0012,
        forward_progress_scale=8.0,
        forward_shortfall_scale=-8.0,
        forward_shortfall_required_ratio=0.36,
        action_rate_scale=-0.018,
        action_magnitude_scale=-0.0045,
        stand_still_scale=-0.95,
        alive_scale=0.04,
        imitation_scale=0.48,
        lin_vel_x=(0.04, 0.08),
        zero_command_probability=0.0,
        forward_overshoot_scale=-1.5,
        forward_overshoot_allowed_ratio=1.55,
        forward_wrong_direction_scale=-9.0,
        forward_wrong_direction_allowed_reverse_ratio=0.02,
        orientation_scale=-0.07,
        base_height_scale=-0.60,
        forward_pitch_scale=-0.12,
        forward_pitch_rate_scale=-0.012,
        forward_contact_support_scale=-0.34,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.04,
        command_progress_scale=9.0,
        command_progress_shortfall_scale=-11.0,
        command_progress_required_ratio=0.36,
        command_progress_warmup_steps=25,
        command_progress_failure_scale=-90.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.22,
        command_progress_failure_warmup_steps=100,
        reward_clip_min=-10.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.35,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.35,
        ppo_learning_rate=1.2e-5,
        ppo_entropy_cost=0.002,
        ppo_clipping_epsilon=0.018,
        ppo_max_grad_norm=0.40,
        phase_gate_bridge_mode="fitted",
    ),
]


MOVEMENT_BOOTSTRAP_V18_PHASES = [
    Phase(
        name="phase1_x004_dense_progress_discovery",
        purpose=(
            "minimal low-command discovery after V17 failed even at x=0.04. "
            "Train and gate on the same easy positive command, with no restore "
            "and no actuator bridge, so the run answers only whether dense "
            "signed-progress pressure can discover coherent forward motion."
        ),
        num_timesteps=260_000,
        bridge=False,
        delay=(0, 0),
        tau_s=(0.0, 0.0),
        velocity_limit_rad_s=(5.24, 5.24),
        target_rate_scale=-0.0002,
        actuator_tracking_scale=0.0,
        tracking_lin_vel_scale=42.0,
        tracking_sigma=0.0012,
        forward_progress_scale=60.0,
        forward_shortfall_scale=-120.0,
        forward_shortfall_required_ratio=0.65,
        action_rate_scale=-0.003,
        action_magnitude_scale=-0.0005,
        stand_still_scale=-1.0,
        alive_scale=0.0,
        imitation_scale=0.0,
        lin_vel_x=(0.035, 0.045),
        zero_command_probability=0.0,
        forward_overshoot_scale=-3.0,
        forward_overshoot_allowed_ratio=1.70,
        forward_wrong_direction_scale=-120.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.035,
        base_height_scale=-0.25,
        forward_pitch_scale=-0.06,
        forward_pitch_rate_scale=-0.006,
        forward_contact_support_scale=-0.10,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.02,
        command_progress_scale=12.0,
        command_progress_shortfall_scale=-80.0,
        command_progress_required_ratio=0.60,
        command_progress_warmup_steps=5,
        command_progress_failure_scale=-160.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.25,
        command_progress_failure_warmup_steps=50,
        reward_clip_min=-20.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=1.5e-4,
        ppo_entropy_cost=0.020,
        ppo_clipping_epsilon=0.14,
        ppo_max_grad_norm=0.80,
        phase_gate_bridge_mode="vanilla",
    ),
    Phase(
        name="phase2_x004_motion_cleanup",
        purpose=(
            "only run if phase 1 passes at x=0.04. Preserve low-command "
            "forward motion while adding modest posture/contact cleanup, still "
            "without actuator bridge or command expansion."
        ),
        num_timesteps=180_000,
        bridge=False,
        delay=(0, 0),
        tau_s=(0.0, 0.0),
        velocity_limit_rad_s=(5.24, 5.24),
        target_rate_scale=-0.0004,
        actuator_tracking_scale=0.0,
        tracking_lin_vel_scale=40.0,
        tracking_sigma=0.0012,
        forward_progress_scale=48.0,
        forward_shortfall_scale=-95.0,
        forward_shortfall_required_ratio=0.60,
        action_rate_scale=-0.005,
        action_magnitude_scale=-0.0010,
        stand_still_scale=-1.0,
        alive_scale=0.0,
        imitation_scale=0.0,
        lin_vel_x=(0.035, 0.045),
        zero_command_probability=0.0,
        forward_overshoot_scale=-4.0,
        forward_overshoot_allowed_ratio=1.55,
        forward_wrong_direction_scale=-100.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.055,
        base_height_scale=-0.40,
        forward_pitch_scale=-0.09,
        forward_pitch_rate_scale=-0.009,
        forward_contact_support_scale=-0.18,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.03,
        command_progress_scale=12.0,
        command_progress_shortfall_scale=-70.0,
        command_progress_required_ratio=0.55,
        command_progress_warmup_steps=5,
        command_progress_failure_scale=-160.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.25,
        command_progress_failure_warmup_steps=55,
        reward_clip_min=-20.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=8.0e-5,
        ppo_entropy_cost=0.010,
        ppo_clipping_epsilon=0.10,
        ppo_max_grad_norm=0.70,
        phase_gate_bridge_mode="vanilla",
    ),
    Phase(
        name="phase3_x004_mild_bridge_probe",
        purpose=(
            "only run if phase 2 passes. Add a mild actuator bridge at the "
            "same x=0.04 command to test whether the discovered low-command "
            "gait survives small delay/lag before any x=0.08 expansion."
        ),
        num_timesteps=180_000,
        bridge=True,
        delay=(1, 3),
        tau_s=(0.03, 0.08),
        velocity_limit_rad_s=(3.6, 4.7),
        target_rate_scale=-0.0008,
        actuator_tracking_scale=-0.04,
        tracking_lin_vel_scale=38.0,
        tracking_sigma=0.0014,
        forward_progress_scale=42.0,
        forward_shortfall_scale=-85.0,
        forward_shortfall_required_ratio=0.55,
        action_rate_scale=-0.007,
        action_magnitude_scale=-0.0015,
        stand_still_scale=-1.0,
        alive_scale=0.0,
        imitation_scale=0.0,
        lin_vel_x=(0.035, 0.045),
        zero_command_probability=0.0,
        forward_overshoot_scale=-4.5,
        forward_overshoot_allowed_ratio=1.50,
        forward_wrong_direction_scale=-95.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.065,
        base_height_scale=-0.50,
        forward_pitch_scale=-0.11,
        forward_pitch_rate_scale=-0.011,
        forward_contact_support_scale=-0.22,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.03,
        command_progress_scale=10.0,
        command_progress_shortfall_scale=-65.0,
        command_progress_required_ratio=0.50,
        command_progress_warmup_steps=5,
        command_progress_failure_scale=-180.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.22,
        command_progress_failure_warmup_steps=60,
        reward_clip_min=-20.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=5.0e-5,
        ppo_entropy_cost=0.006,
        ppo_clipping_epsilon=0.08,
        ppo_max_grad_norm=0.65,
        phase_gate_bridge_mode="vanilla",
    ),
]


MOVEMENT_BOOTSTRAP_V19_PHASES = [
    Phase(
        name="phase1_reference_imitation_seed_x004",
        purpose=(
            "decisive cold-start discovery split after V18: use the upstream "
            "polynomial reference-motion imitation path as a gait seed, with "
            "vanilla dynamics and the same x=0.04 command gate. The reference "
            "data's nearest positive dx is about 0.074, so this phase tests "
            "whether reference-gait structure lets PPO refine any coherent "
            "low-command forward motion instead of discovering gait from scratch."
        ),
        num_timesteps=320_000,
        bridge=False,
        delay=(0, 0),
        tau_s=(0.0, 0.0),
        velocity_limit_rad_s=(5.24, 5.24),
        target_rate_scale=-0.0002,
        actuator_tracking_scale=0.0,
        tracking_lin_vel_scale=24.0,
        tracking_sigma=0.0015,
        forward_progress_scale=24.0,
        forward_shortfall_scale=-45.0,
        forward_shortfall_required_ratio=0.55,
        action_rate_scale=-0.006,
        action_magnitude_scale=-0.0010,
        stand_still_scale=-1.0,
        alive_scale=0.0,
        imitation_scale=4.0,
        lin_vel_x=(0.035, 0.045),
        zero_command_probability=0.0,
        forward_overshoot_scale=-2.0,
        forward_overshoot_allowed_ratio=1.70,
        forward_wrong_direction_scale=-80.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.04,
        base_height_scale=-0.25,
        forward_pitch_scale=-0.06,
        forward_pitch_rate_scale=-0.006,
        forward_contact_support_scale=-0.12,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.02,
        command_progress_scale=10.0,
        command_progress_shortfall_scale=-45.0,
        command_progress_required_ratio=0.45,
        command_progress_warmup_steps=10,
        command_progress_failure_scale=-140.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.20,
        command_progress_failure_warmup_steps=70,
        reward_clip_min=-20.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=1.0e-4,
        ppo_entropy_cost=0.012,
        ppo_clipping_epsilon=0.10,
        ppo_max_grad_norm=0.70,
        phase_gate_bridge_mode="vanilla",
    ),
]


MOVEMENT_BOOTSTRAP_V20_PHASES = [
    Phase(
        name="phase1_interpolated_reference_seed_x004",
        purpose=(
            "repeat the V19 reference-imitation split with a synthesized "
            "straight x=0.04 reference override. V19 used the raw nearest "
            "reference key, which was faster and side-biased; V20 applies the "
            "training-only override that preserves PolyReferenceMotion grid "
            "shape while replacing the selected key with an interpolated "
            "low-speed straight reference."
        ),
        num_timesteps=320_000,
        bridge=False,
        delay=(0, 0),
        tau_s=(0.0, 0.0),
        velocity_limit_rad_s=(5.24, 5.24),
        target_rate_scale=-0.0002,
        actuator_tracking_scale=0.0,
        tracking_lin_vel_scale=24.0,
        tracking_sigma=0.0015,
        forward_progress_scale=24.0,
        forward_shortfall_scale=-45.0,
        forward_shortfall_required_ratio=0.55,
        action_rate_scale=-0.006,
        action_magnitude_scale=-0.0010,
        stand_still_scale=-1.0,
        alive_scale=0.0,
        imitation_scale=4.0,
        lin_vel_x=(0.035, 0.045),
        zero_command_probability=0.0,
        forward_overshoot_scale=-2.0,
        forward_overshoot_allowed_ratio=1.70,
        forward_wrong_direction_scale=-80.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.04,
        base_height_scale=-0.25,
        forward_pitch_scale=-0.06,
        forward_pitch_rate_scale=-0.006,
        forward_contact_support_scale=-0.12,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.02,
        command_progress_scale=10.0,
        command_progress_shortfall_scale=-45.0,
        command_progress_required_ratio=0.45,
        command_progress_warmup_steps=10,
        command_progress_failure_scale=-140.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.20,
        command_progress_failure_warmup_steps=70,
        reward_clip_min=-20.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=1.0e-4,
        ppo_entropy_cost=0.012,
        ppo_clipping_epsilon=0.10,
        ppo_max_grad_norm=0.70,
        phase_gate_bridge_mode="vanilla",
        reference_motion_override="outputs/analysis/reference_motion_x004_override.pkl",
    ),
]


MOVEMENT_BOOTSTRAP_V21_PHASES = [
    Phase(
        name="phase1_soft_prior_low_command_probe",
        purpose=(
            "first weak-soft-prior learner after direct reference targets and "
            "raw target labels held. This phase keeps vanilla dynamics and "
            "x=0.04 only, uses the compact pitch-chain fragment prior as a "
            "small auxiliary cost, and still grades by real closed-loop "
            "forward motion rather than imitation loss."
        ),
        num_timesteps=220_000,
        bridge=False,
        delay=(0, 0),
        tau_s=(0.0, 0.0),
        velocity_limit_rad_s=(5.24, 5.24),
        target_rate_scale=-0.0002,
        actuator_tracking_scale=0.0,
        tracking_lin_vel_scale=26.0,
        tracking_sigma=0.0015,
        forward_progress_scale=28.0,
        forward_shortfall_scale=-55.0,
        forward_shortfall_required_ratio=0.55,
        action_rate_scale=-0.006,
        action_magnitude_scale=-0.0010,
        stand_still_scale=-1.0,
        alive_scale=0.0,
        imitation_scale=0.0,
        lin_vel_x=(0.035, 0.045),
        zero_command_probability=0.0,
        forward_overshoot_scale=-2.0,
        forward_overshoot_allowed_ratio=1.65,
        forward_wrong_direction_scale=-90.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.04,
        base_height_scale=-0.28,
        forward_pitch_scale=-0.06,
        forward_pitch_rate_scale=-0.006,
        forward_contact_support_scale=-0.12,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.02,
        command_progress_scale=10.0,
        command_progress_shortfall_scale=-50.0,
        command_progress_required_ratio=0.45,
        command_progress_warmup_steps=10,
        command_progress_failure_scale=-150.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.20,
        command_progress_failure_warmup_steps=70,
        reward_clip_min=-20.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=1.0e-4,
        ppo_entropy_cost=0.014,
        ppo_clipping_epsilon=0.10,
        ppo_max_grad_norm=0.70,
        phase_gate_bridge_mode="vanilla",
        soft_prior_config_json="outputs/analysis/soft_prior_fragment_config.json",
        soft_prior_scale=-0.025,
        soft_prior_huber_delta=0.05,
        soft_prior_phase_source="imitation_i",
    ),
    Phase(
        name="phase2_soft_prior_mild_bridge_probe",
        purpose=(
            "only run if phase 1 passes the multi-seed x=0.04 vanilla gate. "
            "Keep the same weak prior while adding a mild actuator bridge at "
            "the same command before any fitted-envelope or x=0.08 expansion."
        ),
        num_timesteps=160_000,
        bridge=True,
        delay=(1, 3),
        tau_s=(0.03, 0.08),
        velocity_limit_rad_s=(3.6, 4.7),
        target_rate_scale=-0.0006,
        actuator_tracking_scale=-0.04,
        tracking_lin_vel_scale=24.0,
        tracking_sigma=0.0015,
        forward_progress_scale=24.0,
        forward_shortfall_scale=-45.0,
        forward_shortfall_required_ratio=0.50,
        action_rate_scale=-0.008,
        action_magnitude_scale=-0.0015,
        stand_still_scale=-1.0,
        alive_scale=0.0,
        imitation_scale=0.0,
        lin_vel_x=(0.035, 0.045),
        zero_command_probability=0.0,
        forward_overshoot_scale=-2.5,
        forward_overshoot_allowed_ratio=1.55,
        forward_wrong_direction_scale=-80.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.055,
        base_height_scale=-0.38,
        forward_pitch_scale=-0.08,
        forward_pitch_rate_scale=-0.008,
        forward_contact_support_scale=-0.16,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.02,
        command_progress_scale=8.0,
        command_progress_shortfall_scale=-42.0,
        command_progress_required_ratio=0.45,
        command_progress_warmup_steps=10,
        command_progress_failure_scale=-150.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.18,
        command_progress_failure_warmup_steps=80,
        reward_clip_min=-20.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=7.0e-5,
        ppo_entropy_cost=0.010,
        ppo_clipping_epsilon=0.09,
        ppo_max_grad_norm=0.65,
        phase_gate_bridge_mode="fitted",
        soft_prior_config_json="outputs/analysis/soft_prior_fragment_config.json",
        soft_prior_scale=-0.015,
        soft_prior_huber_delta=0.05,
        soft_prior_phase_source="imitation_i",
    ),
]


MOVEMENT_BOOTSTRAP_V22_PHASES = [
    Phase(
        name="phase1_strong_step_prior_lock_probe",
        purpose=(
            "diagnostic follow-up after V21 trained but the exported policy "
            "remained far from the compact pitch-chain prior. This phase uses "
            "a much stronger step-phased soft prior to test whether PPO can be "
            "kept in the curated low-command gait basin before any bridge or "
            "x=0.08 expansion."
        ),
        num_timesteps=160_000,
        bridge=False,
        delay=(0, 0),
        tau_s=(0.0, 0.0),
        velocity_limit_rad_s=(5.24, 5.24),
        target_rate_scale=-0.0002,
        actuator_tracking_scale=0.0,
        tracking_lin_vel_scale=22.0,
        tracking_sigma=0.0015,
        forward_progress_scale=22.0,
        forward_shortfall_scale=-40.0,
        forward_shortfall_required_ratio=0.50,
        action_rate_scale=-0.004,
        action_magnitude_scale=-0.0008,
        stand_still_scale=-1.0,
        alive_scale=0.0,
        imitation_scale=0.0,
        lin_vel_x=(0.035, 0.045),
        zero_command_probability=0.0,
        forward_overshoot_scale=-2.0,
        forward_overshoot_allowed_ratio=1.60,
        forward_wrong_direction_scale=-90.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.04,
        base_height_scale=-0.25,
        forward_pitch_scale=-0.05,
        forward_pitch_rate_scale=-0.005,
        forward_contact_support_scale=-0.10,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.02,
        command_progress_scale=8.0,
        command_progress_shortfall_scale=-42.0,
        command_progress_required_ratio=0.40,
        command_progress_warmup_steps=10,
        command_progress_failure_scale=-150.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.18,
        command_progress_failure_warmup_steps=70,
        reward_clip_min=-20.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=7.0e-5,
        ppo_entropy_cost=0.008,
        ppo_clipping_epsilon=0.08,
        ppo_max_grad_norm=0.65,
        phase_gate_bridge_mode="vanilla",
        soft_prior_config_json="outputs/analysis/soft_prior_fragment_config.json",
        soft_prior_scale=-0.50,
        soft_prior_huber_delta=0.05,
        soft_prior_phase_source="step",
    ),
]


MOVEMENT_BOOTSTRAP_V23_PHASES = [
    Phase(
        name="phase1_explicit_single_support_probe",
        purpose=(
            "diagnostic after the target-source branch held on persistent "
            "double-support/contact mismatch. This phase removes soft-prior "
            "target chasing and tests whether explicit forward single-support "
            "reward plus double-support dwell cost can teach low-command "
            "weight transfer before any actuator bridge, x=0.08 expansion, "
            "or robot validation."
        ),
        num_timesteps=180_000,
        bridge=False,
        delay=(0, 0),
        tau_s=(0.0, 0.0),
        velocity_limit_rad_s=(5.24, 5.24),
        target_rate_scale=-0.0002,
        actuator_tracking_scale=0.0,
        tracking_lin_vel_scale=22.0,
        tracking_sigma=0.0015,
        forward_progress_scale=22.0,
        forward_shortfall_scale=-42.0,
        forward_shortfall_required_ratio=0.50,
        action_rate_scale=-0.004,
        action_magnitude_scale=-0.0008,
        stand_still_scale=-1.0,
        alive_scale=0.0,
        imitation_scale=0.0,
        lin_vel_x=(0.035, 0.045),
        zero_command_probability=0.0,
        forward_overshoot_scale=-2.0,
        forward_overshoot_allowed_ratio=1.60,
        forward_wrong_direction_scale=-90.0,
        forward_wrong_direction_allowed_reverse_ratio=0.0,
        orientation_scale=-0.04,
        base_height_scale=-0.25,
        forward_pitch_scale=-0.05,
        forward_pitch_rate_scale=-0.005,
        forward_contact_support_scale=-0.06,
        forward_contact_support_no_contact_weight=1.0,
        forward_contact_support_asymmetry_weight=0.0,
        forward_single_support_scale=1.0,
        forward_double_support_scale=-1.0,
        command_progress_scale=8.0,
        command_progress_shortfall_scale=-42.0,
        command_progress_required_ratio=0.40,
        command_progress_warmup_steps=10,
        command_progress_failure_scale=-150.0,
        command_progress_failure_enable=True,
        command_progress_failure_min_ratio=0.18,
        command_progress_failure_warmup_steps=70,
        reward_clip_min=-20.0,
        reward_clip_max=10000.0,
        action_rate_huber_delta=0.08,
        action_magnitude_huber_delta=0.50,
        target_rate_huber_delta=1.0,
        actuator_tracking_huber_delta=0.08,
        forward_shortfall_huber_delta=0.0,
        forward_overshoot_huber_delta=0.50,
        forward_wrong_direction_huber_delta=0.0,
        forward_pitch_huber_delta=0.25,
        forward_pitch_rate_huber_delta=1.0,
        command_progress_shortfall_huber_delta=0.0,
        ppo_learning_rate=7.0e-5,
        ppo_entropy_cost=0.010,
        ppo_clipping_epsilon=0.08,
        ppo_max_grad_norm=0.65,
        phase_gate_bridge_mode="vanilla",
    ),
]


RECIPES = {
    "movement_bootstrap_v23": MOVEMENT_BOOTSTRAP_V23_PHASES,
    "movement_bootstrap_v22": MOVEMENT_BOOTSTRAP_V22_PHASES,
    "movement_bootstrap_v21": MOVEMENT_BOOTSTRAP_V21_PHASES,
    "movement_bootstrap_v20": MOVEMENT_BOOTSTRAP_V20_PHASES,
    "movement_bootstrap_v19": MOVEMENT_BOOTSTRAP_V19_PHASES,
    "movement_bootstrap_v18": MOVEMENT_BOOTSTRAP_V18_PHASES,
    "movement_bootstrap_v17": MOVEMENT_BOOTSTRAP_V17_PHASES,
    "movement_bootstrap_v16": MOVEMENT_BOOTSTRAP_V16_PHASES,
    "movement_bootstrap_v15": MOVEMENT_BOOTSTRAP_V15_PHASES,
    "movement_bootstrap_v14": MOVEMENT_BOOTSTRAP_V14_PHASES,
    "movement_bootstrap_v13": MOVEMENT_BOOTSTRAP_V13_PHASES,
    "movement_bootstrap_v12": MOVEMENT_BOOTSTRAP_V12_PHASES,
    "movement_bootstrap_v11": MOVEMENT_BOOTSTRAP_V11_PHASES,
    "movement_bootstrap_v10": MOVEMENT_BOOTSTRAP_V10_PHASES,
    "movement_bootstrap_v9": MOVEMENT_BOOTSTRAP_V9_PHASES,
    "movement_bootstrap_v8": MOVEMENT_BOOTSTRAP_V8_PHASES,
    "movement_bootstrap_v7": MOVEMENT_BOOTSTRAP_V7_PHASES,
    "movement_bootstrap_v6": MOVEMENT_BOOTSTRAP_V6_PHASES,
    "movement_bootstrap_v5": MOVEMENT_BOOTSTRAP_V5_PHASES,
    "movement_bootstrap_v4": MOVEMENT_BOOTSTRAP_V4_PHASES,
    "movement_bootstrap_v3": MOVEMENT_BOOTSTRAP_V3_PHASES,
    "movement_bootstrap_v2": MOVEMENT_BOOTSTRAP_V2_PHASES,
    "shortfall_v1": SHORTFALL_V1_PHASES,
}


def phase_command(
    args: argparse.Namespace,
    phase: Phase,
    output_root: Path,
    restore_checkpoint: Path | None,
) -> list[str]:
    command = [
        str(Path(args.env_python)),
        str(ROOT / "tools" / "run_actuator_bridge_training_smoke.py"),
        "--run",
        "--playground-path",
        str(Path(args.playground_path)),
        "--env-python",
        str(Path(args.env_python)),
        "--output-root",
        str(output_root),
        "--platform",
        args.platform,
        "--timeout-s",
        str(args.phase_timeout_s),
        "--num-timesteps",
        str(int(phase.num_timesteps * args.timesteps_scale)),
        "--export-min-step",
        str(args.export_min_step),
        "--ppo-num-envs",
        str(args.ppo_num_envs),
        "--ppo-num-evals",
        str(args.ppo_num_evals),
        "--ppo-episode-length",
        str(args.ppo_episode_length),
        "--ppo-unroll-length",
        str(args.ppo_unroll_length),
        "--ppo-batch-size",
        str(args.ppo_batch_size),
        "--ppo-num-minibatches",
        str(args.ppo_num_minibatches),
        "--ppo-num-updates-per-batch",
        str(args.ppo_num_updates_per_batch),
        "--target-rate-scale",
        cli_value(phase.target_rate_scale),
        "--actuator-tracking-scale",
        cli_value(phase.actuator_tracking_scale),
        "--tracking-lin-vel-scale",
        cli_value(phase.tracking_lin_vel_scale),
        "--tracking-ang-vel-scale",
        "0.0",
        "--tracking-sigma",
        cli_value(phase.tracking_sigma),
        "--forward-progress-scale",
        cli_value(phase.forward_progress_scale),
        "--forward-shortfall-scale",
        cli_value(phase.forward_shortfall_scale),
        "--forward-progress-deadband",
        "0.02",
        "--forward-shortfall-required-ratio",
        cli_value(phase.forward_shortfall_required_ratio),
        "--forward-overshoot-scale",
        cli_value(phase.forward_overshoot_scale),
        "--forward-overshoot-allowed-ratio",
        cli_value(phase.forward_overshoot_allowed_ratio),
        "--forward-wrong-direction-scale",
        cli_value(phase.forward_wrong_direction_scale),
        "--forward-wrong-direction-allowed-reverse-ratio",
        cli_value(phase.forward_wrong_direction_allowed_reverse_ratio),
        "--command-progress-scale",
        cli_value(phase.command_progress_scale),
        "--command-progress-shortfall-scale",
        cli_value(phase.command_progress_shortfall_scale),
        "--command-progress-failure-scale",
        cli_value(phase.command_progress_failure_scale),
        "--command-progress-required-ratio",
        cli_value(phase.command_progress_required_ratio),
        "--command-progress-warmup-steps",
        str(phase.command_progress_warmup_steps),
        "--command-progress-failure-min-ratio",
        cli_value(phase.command_progress_failure_min_ratio),
        "--command-progress-failure-warmup-steps",
        str(phase.command_progress_failure_warmup_steps),
        "--action-rate-huber-delta",
        cli_value(phase.action_rate_huber_delta),
        "--action-magnitude-huber-delta",
        cli_value(phase.action_magnitude_huber_delta),
        "--target-rate-huber-delta",
        cli_value(phase.target_rate_huber_delta),
        "--actuator-tracking-huber-delta",
        cli_value(phase.actuator_tracking_huber_delta),
        "--forward-shortfall-huber-delta",
        cli_value(phase.forward_shortfall_huber_delta),
        "--forward-overshoot-huber-delta",
        cli_value(phase.forward_overshoot_huber_delta),
        "--forward-wrong-direction-huber-delta",
        cli_value(phase.forward_wrong_direction_huber_delta),
        "--forward-pitch-huber-delta",
        cli_value(phase.forward_pitch_huber_delta),
        "--forward-pitch-rate-huber-delta",
        cli_value(phase.forward_pitch_rate_huber_delta),
        "--command-progress-shortfall-huber-delta",
        cli_value(phase.command_progress_shortfall_huber_delta),
        "--reward-clip-min",
        cli_value(phase.reward_clip_min),
        "--reward-clip-max",
        cli_value(phase.reward_clip_max),
        "--action-rate-scale",
        cli_value(phase.action_rate_scale),
        "--action-magnitude-scale",
        cli_value(phase.action_magnitude_scale),
        "--stand-still-scale",
        cli_value(phase.stand_still_scale),
        "--orientation-scale",
        cli_value(phase.orientation_scale),
        "--base-height-scale",
        cli_value(phase.base_height_scale),
        "--forward-pitch-scale",
        cli_value(phase.forward_pitch_scale),
        "--forward-pitch-rate-scale",
        cli_value(phase.forward_pitch_rate_scale),
        "--forward-contact-support-scale",
        cli_value(phase.forward_contact_support_scale),
        "--forward-contact-support-no-contact-weight",
        cli_value(phase.forward_contact_support_no_contact_weight),
        "--forward-contact-support-asymmetry-weight",
        cli_value(phase.forward_contact_support_asymmetry_weight),
        "--forward-single-support-scale",
        cli_value(phase.forward_single_support_scale),
        "--forward-double-support-scale",
        cli_value(phase.forward_double_support_scale),
        "--alive-scale",
        cli_value(phase.alive_scale),
        "--imitation-scale",
        cli_value(phase.imitation_scale),
        "--lin-vel-x-min",
        cli_value(phase.lin_vel_x[0]),
        "--lin-vel-x-max",
        cli_value(phase.lin_vel_x[1]),
        "--lin-vel-y-min",
        "0.0",
        "--lin-vel-y-max",
        "0.0",
        "--ang-vel-yaw-min",
        "0.0",
        "--ang-vel-yaw-max",
        "0.0",
        "--command-resample-steps",
        "600",
        "--zero-command-probability",
        cli_value(phase.zero_command_probability),
        "--head-range-factor",
        "0.25",
    ]
    if args.jax_platforms:
        command.extend(["--jax-platforms", args.jax_platforms])
    if phase.ppo_learning_rate is not None:
        command.extend(["--ppo-learning-rate", cli_value(phase.ppo_learning_rate)])
    if phase.ppo_entropy_cost is not None:
        command.extend(["--ppo-entropy-cost", cli_value(phase.ppo_entropy_cost)])
    if phase.ppo_clipping_epsilon is not None:
        command.extend(["--ppo-clipping-epsilon", cli_value(phase.ppo_clipping_epsilon)])
    if phase.ppo_max_grad_norm is not None:
        command.extend(["--ppo-max-grad-norm", cli_value(phase.ppo_max_grad_norm)])
    if phase.command_progress_failure_enable:
        command.append("--command-progress-failure-enable")
    if phase.reference_motion_override:
        command.extend(
            ["--reference-motion-override", phase.reference_motion_override]
        )
    if phase.soft_prior_config_json:
        command.extend(
            [
                "--enable-soft-prior",
                "--soft-prior-config-json",
                phase.soft_prior_config_json,
                "--soft-prior-scale",
                cli_value(phase.soft_prior_scale),
                "--soft-prior-huber-delta",
                cli_value(phase.soft_prior_huber_delta),
                "--soft-prior-phase-source",
                phase.soft_prior_phase_source,
            ]
        )
    if not phase.bridge:
        command.append("--disable-actuator-bridge")
    else:
        command.extend(
            [
                "--actuator-bridge-delay-min-ticks",
                str(phase.delay[0]),
                "--actuator-bridge-delay-max-ticks",
                str(phase.delay[1]),
                "--actuator-bridge-tau-min-s",
                cli_value(phase.tau_s[0]),
                "--actuator-bridge-tau-max-s",
                cli_value(phase.tau_s[1]),
                "--actuator-bridge-velocity-limit-min-rad-s",
                cli_value(phase.velocity_limit_rad_s[0]),
                "--actuator-bridge-velocity-limit-max-rad-s",
                cli_value(phase.velocity_limit_rad_s[1]),
                "--actuator-bridge-per-joint-variation",
                "0.15",
            ]
        )
    if restore_checkpoint is not None:
        command.extend(["--restore-checkpoint-path", str(restore_checkpoint)])
    return command


def find_latest_checkpoint(root: Path) -> Path | None:
    candidates: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        if path.name.endswith(("_x0", "_x008")) or "gate" in path.name:
            continue
        if any(path.with_suffix(suffix).exists() for suffix in (".onnx", ".pkl")):
            candidates.append(path)
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def find_latest_onnx(root: Path) -> Path | None:
    candidates = list(root.rglob("*.onnx"))
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def phase_payload(phase: Phase, command: list[str], output_root: Path) -> dict[str, Any]:
    payload = asdict(phase)
    payload.update(
        {
        "name": phase.name,
        "purpose": phase.purpose,
        "output_root": str(output_root),
        "bridge_enabled": phase.bridge,
        "delay_ticks": list(phase.delay),
        "tau_s": list(phase.tau_s),
        "velocity_limit_rad_s": list(phase.velocity_limit_rad_s),
        "lin_vel_x": list(phase.lin_vel_x),
        "zero_command_probability": phase.zero_command_probability,
        "tracking_ang_vel_scale": 0.0,
        "forward_progress_deadband": 0.02,
        "forward_shortfall_scale": phase.forward_shortfall_scale,
        "forward_shortfall_required_ratio": phase.forward_shortfall_required_ratio,
        "forward_overshoot_scale": phase.forward_overshoot_scale,
        "forward_overshoot_allowed_ratio": phase.forward_overshoot_allowed_ratio,
        "forward_wrong_direction_scale": phase.forward_wrong_direction_scale,
        "forward_wrong_direction_allowed_reverse_ratio": (
            phase.forward_wrong_direction_allowed_reverse_ratio
        ),
        "command_progress_scale": phase.command_progress_scale,
        "command_progress_shortfall_scale": phase.command_progress_shortfall_scale,
        "command_progress_failure_scale": phase.command_progress_failure_scale,
        "command_progress_required_ratio": phase.command_progress_required_ratio,
        "command_progress_warmup_steps": phase.command_progress_warmup_steps,
        "command_progress_failure_enable": phase.command_progress_failure_enable,
        "command_progress_failure_min_ratio": phase.command_progress_failure_min_ratio,
        "command_progress_failure_warmup_steps": (
            phase.command_progress_failure_warmup_steps
        ),
        "reward_clip_min": phase.reward_clip_min,
        "reward_clip_max": phase.reward_clip_max,
        "action_rate_huber_delta": phase.action_rate_huber_delta,
        "action_magnitude_huber_delta": phase.action_magnitude_huber_delta,
        "target_rate_huber_delta": phase.target_rate_huber_delta,
        "actuator_tracking_huber_delta": phase.actuator_tracking_huber_delta,
        "forward_shortfall_huber_delta": phase.forward_shortfall_huber_delta,
        "forward_overshoot_huber_delta": phase.forward_overshoot_huber_delta,
        "forward_wrong_direction_huber_delta": (
            phase.forward_wrong_direction_huber_delta
        ),
        "forward_pitch_huber_delta": phase.forward_pitch_huber_delta,
        "forward_pitch_rate_huber_delta": phase.forward_pitch_rate_huber_delta,
        "command_progress_shortfall_huber_delta": (
            phase.command_progress_shortfall_huber_delta
        ),
        "orientation_scale": phase.orientation_scale,
        "base_height_scale": phase.base_height_scale,
        "forward_pitch_scale": phase.forward_pitch_scale,
        "forward_pitch_rate_scale": phase.forward_pitch_rate_scale,
        "forward_contact_support_scale": phase.forward_contact_support_scale,
        "forward_contact_support_no_contact_weight": (
            phase.forward_contact_support_no_contact_weight
        ),
        "forward_contact_support_asymmetry_weight": (
            phase.forward_contact_support_asymmetry_weight
        ),
        "forward_single_support_scale": phase.forward_single_support_scale,
        "forward_double_support_scale": phase.forward_double_support_scale,
        "ppo_learning_rate": phase.ppo_learning_rate,
        "ppo_entropy_cost": phase.ppo_entropy_cost,
        "ppo_clipping_epsilon": phase.ppo_clipping_epsilon,
        "ppo_max_grad_norm": phase.ppo_max_grad_norm,
        "soft_prior_config_json": phase.soft_prior_config_json,
        "soft_prior_scale": phase.soft_prior_scale,
        "soft_prior_huber_delta": phase.soft_prior_huber_delta,
        "soft_prior_phase_source": phase.soft_prior_phase_source,
        "num_timesteps": phase.num_timesteps,
        "restore_checkpoint": (
            command[command.index("--restore-checkpoint-path") + 1]
            if "--restore-checkpoint-path" in command
            else None
        ),
        "command": command,
        "command_shell": shell_join(command),
        }
    )
    return payload


def recipe_rationale(recipe: str) -> str:
    if recipe == "movement_bootstrap_v23":
        return (
            "`movement_bootstrap_v23` is the first explicit contact/weight-"
            "transfer learner after the target-source branch held. The direct "
            "rollout and optimizer evidence showed persistent double support "
            "when forward stepping needs single support, so V23 removes the "
            "soft prior and tests whether rewarding forward single support "
            "while penalizing double-support dwell can create low-command "
            "weight transfer at x=0.04. It must not progress to x=0.08, fitted "
            "bridge, or robot validation unless the multi-seed x=0.04 gate "
            "shows coherent forward motion and contact alternation."
        )
    if recipe == "movement_bootstrap_v22":
        return (
            "`movement_bootstrap_v22` is a strong step-phased soft-prior lock "
            "diagnostic after V21 trained but stayed far from the prior. V22 "
            "uses the same compact pitch-chain fragment as V21, but raises the "
            "prior scale and uses `phase_source=step` to test whether PPO can "
            "be held near the curated low-command gait basin at x=0.04. It "
            "must not progress to x=0.08, fitted bridge, or robot validation "
            "unless the multi-seed gate and trace prior-distance check both "
            "pass."
        )
    if recipe == "movement_bootstrap_v21":
        return (
            "`movement_bootstrap_v21` is the first weak-soft-prior learner. "
            "V20 showed that a matched reference did not stay coherent under "
            "PPO, and direct fragment targets were too short to use as labels. "
            "V21 keeps the fragment data as a small pitch-chain auxiliary cost "
            "only, keeps the task at x=0.04, and requires multi-seed real "
            "forward motion before any actuator-envelope or x=0.08 expansion."
        )
    if recipe == "movement_bootstrap_v20":
        return (
            "`movement_bootstrap_v20` repeats the V19 reference-imitation "
            "experiment with the command-matched reference override. V19 held "
            "with fall/reverse/low-progress seeds, but its raw nearest "
            "reference was faster and side-biased. V20 applies "
            "`outputs/analysis/reference_motion_x004_override.pkl`, which "
            "replaces the selected raw key with an interpolated reference whose "
            "mean velocity is close to x=0.04 and y=0. This tests whether the "
            "reference-bootstrap idea failed because the seed was mismatched or "
            "because the task/reward landscape still destroys a matched "
            "low-command gait."
        )
    if recipe == "movement_bootstrap_v19":
        return (
            "`movement_bootstrap_v19` is the imitation/reference-gait seed "
            "experiment after V18 showed the immediate low-command reward signal "
            "already prefers forward motion, but cold-start PPO still learned "
            "low/reverse progress. V19 activates the upstream polynomial "
            "reference-motion imitation reward with vanilla dynamics and gates "
            "at x=0.04. If it refines into multi-seed forward motion, cold-start "
            "discovery was the blocker. If it degrades into standstill/reverse, "
            "the reward/task landscape is actively hostile to forward gait. The "
            "reference data's nearest positive dx is about 0.074, so the gait "
            "seed is slightly faster than the x=0.04 command and must be judged "
            "by command tracking, not just survival."
        )
    if recipe == "movement_bootstrap_v18":
        return (
            "`movement_bootstrap_v18` follows the V17 reward/sign audit. V17 "
            "used the intended reward config and a consistent local-forward "
            "sign convention, but still failed at x=0.04, the easiest command "
            "it trained on. V18 therefore stops treating x=0.08 as the first "
            "target and runs a minimal x=0.04 discovery experiment: no restore, "
            "no actuator bridge, dense per-step signed progress, immediate "
            "wrong-direction pressure, and phase gates at the same low command "
            "as training. Do not expand to x=0.08 until low-command motion "
            "passes across seeds."
        )
    if recipe == "movement_bootstrap_v17":
        return (
            "`movement_bootstrap_v17` is a structural break after V16 showed "
            "that every V5-anchor phase-1 checkpoint (40960, 81920, 122880) "
            "collapsed into low/reverse progress with one seed fall. V17 does "
            "not restore from the V5 checkpoint. Phase 1 removes the actuator "
            "bridge and makes signed positive progress non-negotiable at "
            "x=0.04-0.06 while keeping pitch, base-height, and contact pressure "
            "active enough to avoid the old lunge/collapse modes. Later phases "
            "transfer only a multi-seed forward mover into mild and fitted "
            "actuator envelopes."
        )
    if recipe == "movement_bootstrap_v16":
        return (
            "`movement_bootstrap_v16` returns to the recovered V5 moving "
            "checkpoint after V15's fresh no-bridge discovery learned "
            "standstill/reverse/collapse. It is intentionally a checkpoint-"
            "anchored recipe: phase 1 preserves the V5 gait shape under a mild "
            "bridge while reducing the multi-seed lunge/reverse/collapse/freeze "
            "split, then phase 2 and phase 3 transfer only a distributionally "
            "consistent mover into the fitted actuator envelope. Run this with "
            "`--initial-restore-checkpoint` pointing at the V5 recovery "
            "checkpoint and with multi-seed phase gates enabled."
        )
    if recipe == "movement_bootstrap_v15":
        return (
            "`movement_bootstrap_v15` responds to the incomplete V14 A100 "
            "phase-1 run: the recovered step-102400 checkpoint was still "
            "low-motion even under a mild bridge. V15 therefore separates "
            "gait discovery from actuator transfer. Phase 1 removes the "
            "actuator bridge, alive reward, and imitation reward while raising "
            "entropy and progress pressure. If it cannot produce vanilla "
            "forward motion, later actuator-transfer phases should not run. "
            "If it does, phase 2 and phase 3 reintroduce the mild and fitted "
            "actuator envelopes."
        )
    if recipe == "movement_bootstrap_v14":
        return (
            "`movement_bootstrap_v14` responds to the corrected V13 replay: "
            "V13's signed progress failure and negative reward were active, "
            "but PPO still learned a short-lived low-motion behavior under the "
            "fitted bridge from step zero. V14 therefore uses a mild-bridge "
            "motion-discovery phase first, then transfers to the fitted actuator "
            "envelope only if the phase gate shows real forward progress."
        )
    if recipe == "movement_bootstrap_v13":
        return (
            "`movement_bootstrap_v13` is a mechanics test after V12 showed "
            "that episode termination alone did not defeat stable no-motion. "
            "It keeps the V12 fitted-bridge low-command curriculum, but adds "
            "a signed command-progress failure penalty and lowers the reward "
            "clip floor so standing until failure has an explicit negative "
            "consequence."
        )
    if recipe == "movement_bootstrap_v12":
        return (
            "`movement_bootstrap_v12` is a mechanics test after V11 learned "
            "stable no-motion. It keeps the V11 fresh hard-progress structure "
            "but enables default-off command-progress failure so positive-command "
            "standstill terminates. It should be run with "
            "`--phase-gate-freeze-check` so frozen phases stop before later A100 "
            "phases spend time consolidating them."
        )
    if recipe == "movement_bootstrap_v11":
        return (
            "`movement_bootstrap_v11` starts a fresh hard-progress-floor "
            "lineage after V10 hit the pre-committed exit condition. It does "
            "not restore from the V7/V9 anchor by default. The recipe removes "
            "Huber smoothing from the forward shortfall and command-window "
            "shortfall floors so zero or reverse progress is expensive enough "
            "to compete with the safe standstill basin."
        )
    if recipe == "movement_bootstrap_v10":
        return (
            "`movement_bootstrap_v10` is the final planned pass in the V7/V9 "
            "moving-checkpoint lineage unless the eight-seed distribution moves "
            "materially. The V7/V9 multi-seed baseline showed four regimes: "
            "lunge, early contact/base-height collapse, reverse motion, and "
            "standstill. V10 keeps the fitted actuator envelope active, keeps "
            "forward progress dominant, and adds explicit wrong-direction and "
            "support-contact costs so stability cannot be bought by freezing "
            "or backing up."
        )
    if recipe == "movement_bootstrap_v9":
        return (
            "`movement_bootstrap_v9` starts from the v7 anchored checkpoint "
            "again, because v8 overcorrected into standstill. It keeps the "
            "fitted actuator bridge and velocity envelope active, but uses "
            "lighter overshoot/pitch damping and stronger command-window "
            "progress pressure to search the narrow region between v7's lunge "
            "and v8's no-motion solution."
        )
    if recipe == "movement_bootstrap_v8":
        return (
            "`movement_bootstrap_v8` starts from the v7 anchored checkpoint. "
            "The v7 x=0.08 trace showed an in-envelope, unsaturated lunge: "
            "local forward speed exceeded the command before the large pitch "
            "collapse. V8 keeps the fitted actuator bridge active and adds "
            "explicit forward-overshoot, pitch, and pitch-rate costs."
        )
    if recipe == "movement_bootstrap_v6":
        return (
            "`movement_bootstrap_v6` starts from the v5 phase-checkpoint "
            "finding: in-envelope x=0.08 forward motion exists but falls after "
            "about 80 samples. It keeps the fitted actuator envelope active "
            "through every phase, adds light orientation/base-height pressure, "
            "and lowers PPO update size in later phases so stability pressure "
            "is less likely to erase the moving gait."
        )
    if recipe == "movement_bootstrap_v5":
        return (
            "`movement_bootstrap_v5` follows the command feasibility curve: "
            "`BEST_WALK_ONNX_2` stays below the actuator target velocity "
            "envelope through roughly `x=0.06`, then crosses it at `x=0.08`. "
            "V5 therefore learns low-command motion first, using Huber-shaped "
            "smoothness costs, before expanding toward `x=0.08`."
        )
    return (
        f"`{recipe}` is a preserved staged curriculum recipe for offline "
        "candidate generation and comparison against the measured actuator "
        "envelope."
    )


def write_plan(payload: dict[str, Any], output_md: Path, output_json: Path) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Staged Curriculum Training Plan",
        "",
        "Offline-only plan. This does not touch the robot, SSH, deploy, or modify",
        "runtime behavior. Training only runs when the planner is invoked with",
        "`--run`.",
        "",
        f"status: `{payload['status']}`",
        f"platform: `{payload['platform']}`",
        f"recipe: `{payload['recipe']}`",
        f"output_root: `{payload['output_root']}`",
        "",
        "## Why",
        "",
        "Current candidates are either aggressive and unsafe, or stable and nearly",
        "stationary at `x=0.08`. The staged recipe bootstraps forward motion before",
        "tightening actuator realism.",
        "",
        recipe_rationale(payload["recipe"]),
        "",
        "## Phases",
        "",
        "| phase | bridge | gate bridge | timesteps | x command range | shortfall | window progress | failure penalty | delay | tau | velocity limit | purpose |",
        "|---|---|---|---:|---|---|---|---|---|---|---|---|",
    ]
    for phase in payload["phases"]:
        lines.append(
            "| `{name}` | {bridge} | `{gate_bridge}` | {steps} | `{x}` | `{shortfall}` | `{progress}` | `{failure}` | `{delay}` | `{tau}` | `{vel}` | {purpose} |".format(
                name=phase["name"],
                bridge="yes" if phase["bridge_enabled"] else "no",
                gate_bridge=phase.get("phase_gate_bridge_mode") or "global",
                steps=phase["num_timesteps"],
                x=phase["lin_vel_x"],
                shortfall={
                    "scale": phase["forward_shortfall_scale"],
                    "required_ratio": phase["forward_shortfall_required_ratio"],
                },
                progress={
                    "scale": phase["command_progress_scale"],
                    "shortfall": phase["command_progress_shortfall_scale"],
                    "required_ratio": phase["command_progress_required_ratio"],
                    "warmup_steps": phase["command_progress_warmup_steps"],
                    "failure": phase["command_progress_failure_enable"],
                    "failure_min_ratio": phase[
                        "command_progress_failure_min_ratio"
                    ],
                },
                failure={
                    "scale": phase["command_progress_failure_scale"],
                    "clip_min": phase["reward_clip_min"],
                },
                delay=phase["delay_ticks"],
                tau=phase["tau_s"],
                vel=phase["velocity_limit_rad_s"],
                purpose=phase["purpose"],
            )
        )
    lines.extend(["", "## Commands", ""])
    for phase in payload["phases"]:
        lines.extend(
            [
                f"### {phase['name']}",
                "",
                f"- restore_checkpoint: `{phase.get('restore_checkpoint') or 'None'}`",
                "",
                "```bash",
                phase["command_shell"],
                "```",
                "",
            ]
        )
    if payload.get("final_candidate_onnx"):
        lines.extend(
            [
                "## Result",
                "",
                f"- final_candidate_onnx: `{payload['final_candidate_onnx']}`",
                f"- final_checkpoint: `{payload.get('final_checkpoint', 'NA')}`",
                "",
            ]
        )
    lines.extend(["## Next Gate", ""])
    if payload.get("recipe") in {
        "movement_bootstrap_v23",
        "movement_bootstrap_v22",
        "movement_bootstrap_v19",
        "movement_bootstrap_v20",
        "movement_bootstrap_v21",
    }:
        lines.extend(
            [
                f"{payload.get('recipe')} is an x=0.04 discovery split, so the first gate is the built-in multi-seed phase gate:",
                "",
                f"- command_x: `{cli_value(payload.get('phase_gate_command_x', 0.04))}`",
                f"- bridge_mode: `{payload.get('phase_gate_bridge_mode') or 'vanilla'}`",
                "- pass condition: coherent positive forward tracking across seeds, not fall-count alone",
                "- hold condition: standstill, reverse, collapse, or command-progress failure across the seed distribution",
                "",
                "Do not run x=0.08, fitted bridge, or robot validation until the x=0.04 seeded gait passes across seeds.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "After a staged run, evaluate the final ONNX with:",
                "",
                "```bash",
                "JAX_PLATFORMS=cpu ../envs/open-duck-playground/bin/python tools/eval_policy_with_actuator_bridge.py \\",
                "  --mode closed-loop-sim --eval-role candidate \\",
                "  --policy <final_candidate.onnx> \\",
                "  --fit-json outputs/analysis/actuator_response_fit.json \\",
                "  --playground-path ../Open_Duck_Playground \\",
                "  --env-python ../envs/open-duck-playground/bin/python \\",
                "  --command-x 0.0 --duration 15 --bridge-mode all --jax-platform cpu \\",
                "  --output-dir outputs/analysis/<candidate>_gate_x0",
                "```",
                "",
                f"Then repeat with `--command-x {cli_value(payload.get('phase_gate_command_x', 0.08))}`. "
                "Robot validation remains blocked until both gates pass.",
                "",
            ]
        )
    output_md.write_text("\n".join(lines))


def run_phase(command: list[str], cwd: Path, timeout_s: int) -> None:
    print(">>>", shell_join(command), flush=True)
    completed = subprocess.run(command, cwd=cwd, text=True, timeout=timeout_s, check=False)
    print("<<<", completed.returncode, flush=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def run_phase_freeze_gate(
    args: argparse.Namespace,
    phase: Phase,
    policy: Path,
    phase_root: Path,
    phase_index: int,
) -> dict[str, Any]:
    label = command_label(float(args.phase_gate_command_x))
    output_dir = phase_root / f"phase_{phase_index:02d}_freeze_gate_{label}"
    bridge_mode = phase.phase_gate_bridge_mode or args.phase_gate_bridge_mode
    command = [
        str(Path(args.env_python)),
        str(ROOT / "tools" / "eval_policy_with_actuator_bridge.py"),
        "--mode",
        "closed-loop-sim",
        "--eval-role",
        "candidate",
        "--policy",
        str(policy),
        "--fit-json",
        str(ROOT / "outputs" / "analysis" / "actuator_response_fit.json"),
        "--playground-path",
        str(Path(args.playground_path)),
        "--env-python",
        str(Path(args.env_python)),
        "--command-x",
        cli_value(args.phase_gate_command_x),
        "--duration",
        cli_value(args.phase_gate_duration_s),
        "--bridge-mode",
        bridge_mode,
        "--jax-platform",
        args.phase_gate_platform,
        "--sim-preflight-timeout-s",
        "600",
        "--closed-loop-timeout-s",
        str(args.phase_gate_timeout_s),
        "--output-dir",
        str(output_dir),
    ]
    if args.phase_gate_jax_platforms:
        command.extend(["--jax-platforms", args.phase_gate_jax_platforms])
    print(">>>", shell_join(command), flush=True)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        timeout=args.phase_gate_timeout_s + 120,
        check=False,
    )
    print("<<<", completed.returncode, flush=True)
    result_path = output_dir / "closed_loop_actuator_bridge_eval.json"
    if not result_path.exists():
        return {
            "status": "HOLD_PHASE_GATE_NO_RESULT",
        "command": command,
        "bridge_mode": bridge_mode,
        "output_dir": str(output_dir),
        "returncode": completed.returncode,
        }
    result = json.loads(result_path.read_text())
    closed = result.get("closed_loop_sim") or {}
    gate = closed.get("candidate_gate") or {}
    metrics = gate.get("metrics") or {}
    diagnostic_failure = 0.0
    for mode in (closed.get("modes") or {}).values():
        terms = mode.get("reward_terms") or {}
        failure = (terms.get("diagnostic/command_progress_failure") or {}).get("max")
        if isinstance(failure, (int, float)):
            diagnostic_failure = max(diagnostic_failure, float(failure))
    gate_status = gate.get("status") or closed.get("status") or result.get("overall_status")
    candidate_gate_passed = gate_status == "PASS_CANDIDATE_SIM_GATE"
    progress_failure = diagnostic_failure > 0.0
    phase_status = (
        "PASS_PHASE_FREEZE_CHECK"
        if candidate_gate_passed and not progress_failure
        else "HOLD_PHASE_CANDIDATE_GATE"
    )
    if progress_failure:
        phase_status = "HOLD_PHASE_FREEZE_OR_LOW_PROGRESS"
    elif gate_status in {
        "HOLD_CANDIDATE_LOW_FORWARD_PROGRESS",
        "HOLD_CANDIDATE_NO_FORWARD_TRACKING",
    }:
        phase_status = "HOLD_PHASE_FREEZE_OR_LOW_PROGRESS"
    elif not candidate_gate_passed:
        phase_status = "HOLD_PHASE_CANDIDATE_GATE"
    return {
        "status": phase_status,
        "candidate_gate_status": gate_status,
        "candidate_gate_passed": candidate_gate_passed,
        "metrics": metrics,
        "diagnostic_command_progress_failure_max": diagnostic_failure,
        "command": command,
        "bridge_mode": bridge_mode,
        "output_dir": str(output_dir),
        "result_json": str(result_path),
        "returncode": completed.returncode,
    }


def run_phase_seed_gate(
    args: argparse.Namespace,
    phase: Phase,
    policy: Path,
    phase_root: Path,
    phase_index: int,
) -> dict[str, Any]:
    seeds = parse_seed_text(args.phase_gate_seeds)
    if not seeds:
        return run_phase_freeze_gate(args, phase, policy, phase_root, phase_index)

    label = command_label(float(args.phase_gate_command_x))
    output_dir = phase_root / f"phase_{phase_index:02d}_seed_gate_{label}"
    output_md = output_dir / "PHASE_SEED_GATE.md"
    output_json = output_dir / "phase_seed_gate.json"
    reward_overrides_json = output_dir / "phase_reward_overrides.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    reward_overrides_json.write_text(
        json.dumps({"phases": [phase_payload(phase, [], phase_root)]}, indent=2)
        + "\n"
    )
    bridge_mode = phase.phase_gate_bridge_mode or args.phase_gate_bridge_mode
    policy_label = f"phase_{phase_index:02d}"
    mode_name = "fitted" if bridge_mode == "all" else bridge_mode
    command = [
        str(Path(args.env_python)),
        str(ROOT / "tools" / "run_candidate_seed_sweep.py"),
        "--run",
        "--policies",
        f"{policy_label}={policy}",
        "--seeds",
        args.phase_gate_seeds,
        "--fit-json",
        str(ROOT / "outputs" / "analysis" / "actuator_response_fit.json"),
        "--playground-path",
        str(Path(args.playground_path)),
        "--env-python",
        str(Path(args.env_python)),
        "--command-x",
        cli_value(args.phase_gate_command_x),
        "--duration",
        cli_value(args.phase_gate_duration_s),
        "--bridge-mode",
        bridge_mode,
        "--mode-name",
        mode_name,
        "--reward-overrides-json",
        str(reward_overrides_json),
        "--reward-overrides-phase",
        phase.name,
        "--jax-platform",
        args.phase_gate_platform,
        "--sim-preflight-timeout-s",
        "600",
        "--closed-loop-timeout-s",
        str(args.phase_gate_timeout_s),
        "--output-dir",
        str(output_dir),
        "--output-md",
        str(output_md),
        "--output-json",
        str(output_json),
    ]
    print(">>>", shell_join(command), flush=True)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        timeout=(args.phase_gate_timeout_s + 120) * max(1, len(seeds)),
        check=False,
    )
    print("<<<", completed.returncode, flush=True)
    if not output_json.exists():
        return {
            "status": "HOLD_PHASE_MULTI_SEED_NO_RESULT",
            "command": command,
            "reward_overrides_json": str(reward_overrides_json),
            "reward_overrides_phase": phase.name,
            "bridge_mode": bridge_mode,
            "seeds": seeds,
            "output_dir": str(output_dir),
            "returncode": completed.returncode,
        }

    result = json.loads(output_json.read_text())
    aggregate = (result.get("aggregate") or {}).get(policy_label) or {}
    runs = int(aggregate.get("runs") or 0)
    fall_count = int(aggregate.get("fall_count") or 0)
    fall_fraction = (fall_count / runs) if runs else 1.0
    track_ratio_mean = ((aggregate.get("track_ratio") or {}).get("mean"))
    vx_mean = ((aggregate.get("mean_local_vx_m_s") or {}).get("mean"))

    gate_status = "PASS_PHASE_MULTI_SEED_CHECK"
    if runs != len(seeds):
        gate_status = "HOLD_PHASE_MULTI_SEED_INCOMPLETE"
    elif fall_fraction > args.phase_gate_max_fall_fraction:
        gate_status = "HOLD_PHASE_MULTI_SEED_FALLS"
    elif not isinstance(track_ratio_mean, (int, float)):
        gate_status = "HOLD_PHASE_MULTI_SEED_NO_PROGRESS_METRIC"
    elif float(track_ratio_mean) < args.phase_gate_min_track_ratio_mean:
        gate_status = "HOLD_PHASE_MULTI_SEED_LOW_TRACK_RATIO"
    elif not isinstance(vx_mean, (int, float)):
        gate_status = "HOLD_PHASE_MULTI_SEED_NO_VX_METRIC"
    elif float(vx_mean) < args.phase_gate_min_vx_mean:
        gate_status = "HOLD_PHASE_MULTI_SEED_LOW_FORWARD_SPEED"

    return {
        "status": gate_status,
        "aggregate": aggregate,
        "fall_fraction": fall_fraction,
        "track_ratio_mean": track_ratio_mean,
        "mean_local_vx_m_s": vx_mean,
        "thresholds": {
            "max_fall_fraction": args.phase_gate_max_fall_fraction,
            "min_track_ratio_mean": args.phase_gate_min_track_ratio_mean,
            "min_vx_mean": args.phase_gate_min_vx_mean,
        },
        "command": command,
        "reward_overrides_json": str(reward_overrides_json),
        "reward_overrides_phase": phase.name,
        "bridge_mode": bridge_mode,
        "mode_name": mode_name,
        "seeds": seeds,
        "output_dir": str(output_dir),
        "result_json": str(output_json),
        "result_md": str(output_md),
        "returncode": completed.returncode,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--env-python", default=str(DEFAULT_ENV_PYTHON))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--output-md", type=Path, default=DEFAULT_PLAN_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_PLAN_JSON)
    parser.add_argument("--platform", choices=["cpu", "gpu"], default="gpu")
    parser.add_argument(
        "--jax-platforms",
        default=None,
        help=(
            "Optional JAX_PLATFORMS override passed to each phase smoke. "
            "Use cuda for Colab/NVIDIA GPU, rocm for ROCm, or cpu for CPU."
        ),
    )
    parser.add_argument(
        "--recipe",
        choices=sorted(RECIPES),
        default="movement_bootstrap_v20",
        help=(
            "Staged recipe to emit/run. shortfall_v1 preserves the June 23 A100 "
            "recipe that landed in standstill; movement_bootstrap_v2 preserves "
            "the first movement-bootstrap attempt; movement_bootstrap_v3 adds "
            "command-window progress pressure; movement_bootstrap_v4 adds a "
            "fitted-bridge x0 stability phase before low-command progress; "
            "movement_bootstrap_v5 targets the measured low-command feasible "
            "range first; movement_bootstrap_v6 tries to preserve the v5 "
            "phase-1 in-envelope motion while adding stability pressure; "
            "movement_bootstrap_v7 is a checkpoint-anchored stabilization "
            "recipe intended to start from the recovered v5 phase-1 checkpoint; "
            "movement_bootstrap_v8 starts from v7 and targets the measured "
            "velocity-overshoot/pitch-over failure; movement_bootstrap_v9 "
            "starts from v7 again with lighter damping after v8 stabilized "
            "into standstill; movement_bootstrap_v10 targets the multi-seed "
            "V7/V9 failure surfaces: lunge, reverse, support collapse, and "
            "standstill; movement_bootstrap_v11 starts a fresh hard-progress "
            "lineage after V10 failed mostly by freezing; movement_bootstrap_v12 "
            "adds command-progress failure to invalidate V11-style no-motion; "
            "movement_bootstrap_v13 adds a signed command-progress failure "
            "penalty after V12 still froze; movement_bootstrap_v14 starts with "
            "a mild bridge for motion discovery before transferring to the "
            "fitted actuator envelope; movement_bootstrap_v15 separates "
            "vanilla gait discovery from actuator transfer after the V14 "
            "partial checkpoint remained low-motion; movement_bootstrap_v16 "
            "returns to the recovered V5 moving checkpoint and must be run with "
            "--initial-restore-checkpoint; movement_bootstrap_v17 is a fresh "
            "hard signed-progress structural break after V16 showed no usable "
            "V5-anchor branch point; movement_bootstrap_v18 is a minimal "
            "x=0.04 low-command discovery experiment after V17 failed even at "
            "the easiest trained command; movement_bootstrap_v19 is the "
            "reference/imitation-gait seed experiment after V18 proved the "
            "reward signal itself prefers forward motion; movement_bootstrap_v20 "
            "repeats V19 with a command-matched reference override after the "
            "V19 seed was found to be faster and side-biased. "
            "movement_bootstrap_v21 is the explicit weak-soft-prior learner; "
            "movement_bootstrap_v22 is a stronger step-phased prior-lock "
            "diagnostic after V21 trained but remained far from the prior; "
            "movement_bootstrap_v23 is an explicit single-support/contact "
            "objective probe after the target-source branch held; neither V21, "
            "V22, nor V23 is the default. V20 is the current default."
        ),
    )
    parser.add_argument("--timesteps-scale", type=float, default=1.0)
    parser.add_argument(
        "--export-min-step",
        type=int,
        default=1,
        help=(
            "Skip checkpoint/ONNX export callbacks before this PPO step. The "
            "default skips only step 0 to avoid cloud GPU/TensorFlow export "
            "handoff failures while preserving later candidate exports."
        ),
    )
    parser.add_argument(
        "--initial-restore-checkpoint",
        type=Path,
        default=None,
        help=(
            "Optional checkpoint path to use as the starting policy for phase 1. "
            "Later phases still continue from the previous phase output."
        ),
    )
    parser.add_argument(
        "--stop-after-phase",
        type=int,
        default=None,
        help=(
            "Stop after this 1-based phase index. Useful for preserving a "
            "trainable phase checkpoint without running later known-bad "
            "consolidation phases."
        ),
    )
    parser.add_argument("--phase-timeout-s", type=int, default=3600)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--ppo-num-envs", type=int, default=256)
    parser.add_argument("--ppo-num-evals", type=int, default=4)
    parser.add_argument("--ppo-episode-length", type=int, default=600)
    parser.add_argument("--ppo-unroll-length", type=int, default=10)
    parser.add_argument("--ppo-batch-size", type=int, default=256)
    parser.add_argument("--ppo-num-minibatches", type=int, default=4)
    parser.add_argument("--ppo-num-updates-per-batch", type=int, default=4)
    parser.add_argument(
        "--phase-gate-freeze-check",
        action="store_true",
        help=(
            "After each completed phase, run a short closed-loop candidate gate "
            "and stop the staged run if the phase freezes or trips command "
            "progress failure. Default off."
        ),
    )
    parser.add_argument(
        "--phase-gate-command-x",
        type=float,
        default=None,
        help=(
            "Command x for phase gates. Defaults to a recipe-specific value "
            "when available, otherwise 0.08."
        ),
    )
    parser.add_argument("--phase-gate-duration-s", type=float, default=5.0)
    parser.add_argument(
        "--phase-gate-bridge-mode",
        choices=["vanilla", "fitted", "stress", "all"],
        default="fitted",
    )
    parser.add_argument("--phase-gate-platform", choices=["cpu", "gpu"], default="cpu")
    parser.add_argument(
        "--phase-gate-jax-platforms",
        default=None,
        help=(
            "Optional JAX_PLATFORMS override for phase candidate gates. "
            "Usually unnecessary for CPU gates because the evaluator infers "
            "JAX_PLATFORMS=cpu from --phase-gate-platform cpu."
        ),
    )
    parser.add_argument("--phase-gate-timeout-s", type=int, default=900)
    parser.add_argument(
        "--phase-gate-seeds",
        default=None,
        help=(
            "Optional comma/range seed list such as 0-3. When set, the phase "
            "gate runs tools/run_candidate_seed_sweep.py and grades the "
            "distribution instead of a single rollout."
        ),
    )
    parser.add_argument(
        "--phase-gate-max-fall-fraction",
        type=float,
        default=0.0,
        help="Maximum allowed fraction of multi-seed phase-gate rollouts that fall.",
    )
    parser.add_argument(
        "--phase-gate-min-track-ratio-mean",
        type=float,
        default=0.25,
        help="Minimum mean command-tracking ratio for a multi-seed phase gate.",
    )
    parser.add_argument(
        "--phase-gate-min-vx-mean",
        type=float,
        default=0.02,
        help="Minimum mean local forward velocity for a multi-seed phase gate.",
    )
    args = parser.parse_args()
    if args.stop_after_phase is not None and args.stop_after_phase < 1:
        raise SystemExit("--stop-after-phase must be >= 1")
    if args.phase_gate_command_x is None:
        args.phase_gate_command_x = RECIPE_DEFAULT_PHASE_GATE_COMMAND_X.get(
            args.recipe, 0.08
        )
    if (
        args.run
        and args.recipe == "movement_bootstrap_v16"
        and args.initial_restore_checkpoint is None
    ):
        raise SystemExit(
            "movement_bootstrap_v16 requires --initial-restore-checkpoint "
            "pointing at the recovered V5 trainable checkpoint"
        )

    output_root = Path(args.output_root).expanduser().resolve()
    payload: dict[str, Any] = {
        "status": "RUN_REQUESTED" if args.run else "DRY_RUN",
        "timestamp": timestamp(),
        "robot_touched": False,
        "deploy_performed": False,
        "platform": args.platform,
        "recipe": args.recipe,
        "initial_restore_checkpoint": (
            str(args.initial_restore_checkpoint)
            if args.initial_restore_checkpoint is not None
            else None
        ),
        "export_min_step": args.export_min_step,
        "stop_after_phase": args.stop_after_phase,
        "phase_gate_freeze_check": args.phase_gate_freeze_check,
        "phase_gate_command_x": args.phase_gate_command_x,
        "phase_gate_seeds": args.phase_gate_seeds,
        "phase_gate_distribution_thresholds": {
            "max_fall_fraction": args.phase_gate_max_fall_fraction,
            "min_track_ratio_mean": args.phase_gate_min_track_ratio_mean,
            "min_vx_mean": args.phase_gate_min_vx_mean,
        },
        "output_root": str(output_root),
        "phases": [],
    }

    restore_checkpoint: Path | None = args.initial_restore_checkpoint
    if args.run and restore_checkpoint is not None and not restore_checkpoint.exists():
        raise SystemExit(f"Initial restore checkpoint missing: {restore_checkpoint}")
    if args.run and restore_checkpoint is not None:
        restore_checkpoint = restore_checkpoint.resolve()
    for index, phase in enumerate(RECIPES[args.recipe], 1):
        if args.stop_after_phase is not None and index > args.stop_after_phase:
            break
        phase_root = output_root / f"{index:02d}_{phase.name}"
        restore_for_command = restore_checkpoint
        if restore_for_command is None and not args.run and index > 1:
            restore_for_command = Path(f"<latest_checkpoint_from_phase_{index - 1}>")
        command = phase_command(args, phase, phase_root, restore_for_command)
        payload["phases"].append(phase_payload(phase, command, phase_root))
        if args.run:
            run_phase(command, ROOT, args.phase_timeout_s + 300)
            restore_checkpoint = find_latest_checkpoint(phase_root)
            if restore_checkpoint is None:
                raise SystemExit(f"{phase.name} produced no checkpoint under {phase_root}")
            if args.phase_gate_freeze_check:
                phase_onnx = find_latest_onnx(phase_root)
                if phase_onnx is None:
                    raise SystemExit(f"{phase.name} produced no ONNX under {phase_root}")
                gate_result = run_phase_seed_gate(args, phase, phase_onnx, phase_root, index)
                payload["phases"][-1]["phase_freeze_gate"] = gate_result
                pass_statuses = {
                    "PASS_PHASE_FREEZE_CHECK",
                    "PASS_PHASE_MULTI_SEED_CHECK",
                }
                if gate_result["status"] not in pass_statuses:
                    payload["status"] = gate_result["status"]
                    payload["final_checkpoint"] = str(restore_checkpoint)
                    payload["final_candidate_onnx"] = str(phase_onnx)
                    write_plan(payload, args.output_md, args.output_json)
                    raise SystemExit(gate_result["status"])
        elif index < len(RECIPES[args.recipe]):
            restore_checkpoint = Path(f"<latest_checkpoint_from_phase_{index}>")

    if args.run:
        payload["status"] = "PASS_STAGED_CURRICULUM_RUN"
        payload["final_checkpoint"] = str(restore_checkpoint) if restore_checkpoint else None
        final_onnx = find_latest_onnx(output_root)
        payload["final_candidate_onnx"] = str(final_onnx) if final_onnx else None
    write_plan(payload, args.output_md, args.output_json)
    print(f"Wrote {args.output_md}")
    print(f"Wrote {args.output_json}")
    if not args.run:
        print("Dry-run only. Pass --run to execute staged training.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.TimeoutExpired as exc:
        print(f"HOLD_STAGED_CURRICULUM_TIMEOUT: timed out after {exc.timeout}s", file=sys.stderr)
        raise SystemExit(124) from exc
