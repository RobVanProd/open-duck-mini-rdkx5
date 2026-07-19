#!/usr/bin/env python3
"""Freeze the winner-v3 variable-configuration replacement study."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUT_JSON = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
OUT_MD = ANALYSIS / "WINNER_V3_VARIABLE_CONFIGURATION_REPLACEMENT_PREREGISTRATION_20260719.md"
BASIS = ANALYSIS / "winner_v3_supported_configuration_basis.json"
TAIL_ARCHIVE = ANALYSIS / "GROUND_UP_TRACKING_TAIL_artifacts.tar.gz"
TAIL_PREREG = ANALYSIS / "ground_up_tracking_tail_search_preregistration.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
P30_ALL = ANALYSIS / "fixed_target_p30_all_joint_actuator_fit_20260712.json"
P30_PITCH = ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json"
P31_PITCH = ANALYSIS / "fixed_target_p31_34_actuator_fit_20260712.json"
BREAK_RESULT = ANALYSIS / "composite_winner_torso_com_break_radius_result.json"

JOINTS = (
    "left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee",
    "left_ankle", "neck_pitch", "head_pitch", "head_yaw", "head_roll",
    "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee",
    "right_ankle",
)
PITCH_JOINTS = {
    "left_hip_pitch", "left_knee", "left_ankle",
    "right_hip_pitch", "right_knee", "right_ankle",
}
VELOCITY_LIMITS = (
    1.0, 0.75, 1.5, 1.5, 1.5, 0.5, 0.5,
    0.5, 0.5, 0.5, 0.75, 1.25, 1.0, 1.25,
)
DISCOVERY_SEED = 0xD699DCE0
HELDOUT_SEED = 0x8B24715A


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source(path: Path) -> dict[str, Any]:
    return {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}


def joint_fit(payload: dict[str, Any], name: str) -> dict[str, float | int]:
    row = payload["primary"]["joints"][name]
    combined = row["combined"]
    return {
        "delay_ticks": int(combined["delay_ticks"]),
        "tau_s": float(combined["tau_s"]),
        "velocity_limit_rad_s": float(combined["velocity_limit_rad_s"]),
        "gain_ratio": float(row["series"]["amplitude_ratio"]),
    }


def actuator_domain() -> dict[str, Any]:
    p30 = json.loads(P30_ALL.read_text())
    p31 = json.loads(P31_PITCH.read_text())
    per_joint = {}
    for index, name in enumerate(JOINTS):
        a = joint_fit(p30, name)
        b = joint_fit(p31, name) if name in PITCH_JOINTS else a
        per_joint[name] = {
            "delay_ticks": [min(a["delay_ticks"], b["delay_ticks"]), max(a["delay_ticks"], b["delay_ticks"])],
            "tau_s": [min(a["tau_s"], b["tau_s"]), max(a["tau_s"], b["tau_s"])],
            "gain_ratio": [min(a["gain_ratio"], b["gain_ratio"]), max(a["gain_ratio"], b["gain_ratio"])],
            "conservative_velocity_limit_rad_s": VELOCITY_LIMITS[index],
            "fit_p30": a,
            "fit_p31_34": b,
        }
    return {
        "semantics": (
            "home-relative first-order delayed target: actual = home + gain_ratio * "
            "lagged_slew_limited(target-home); sample integer delay and continuous tau/gain "
            "inside each frozen per-joint interval"
        ),
        "per_joint": per_joint,
        "additional_action_delay_ticks": [0, 2],
        "imu_delay_ticks": [0, 2],
    }


def valid_inertia(tensor: np.ndarray) -> bool:
    values = np.linalg.eigvalsh(tensor)
    return bool(
        np.all(values > 0.0)
        and values[2] < values[0] + values[1]
    )


def make_sample_set(
    *, name: str, seed: int, count: int, basis: dict[str, Any]
) -> list[dict[str, Any]]:
    domain = basis["frozen_continuous_domain"]
    inertia = domain["torso_inertia"]
    nominal = np.asarray(basis["compiled_torso"]["principal_inertia_kg_m2"], dtype=float)
    diagonal_bounds = np.asarray(
        [inertia["principal_component_bounds_kg_m2"][axis] for axis in ("ixx", "iyy", "izz")],
        dtype=float,
    )
    product = float(inertia["product_additive_allowance_abs_kg_m2"])
    bounds = np.asarray([
        domain["all_link_mass_scale"], domain["torso_mass_add_kg"],
        domain["torso_com_offset_m"]["x"], domain["torso_com_offset_m"]["y"],
        domain["torso_com_offset_m"]["z"], diagonal_bounds[0], diagonal_bounds[1],
        diagonal_bounds[2], [-product, product], [-product, product], [-product, product],
    ], dtype=float)
    rng = np.random.Generator(np.random.PCG64(seed))
    unit = np.empty((count, len(bounds)), dtype=float)
    for column in range(unit.shape[1]):
        unit[:, column] = (rng.permutation(count) + 0.5) / count
    raw = bounds[:, 0] + unit * (bounds[:, 1] - bounds[:, 0])
    rows: list[dict[str, Any]] = []
    torso_mass = float(basis["compiled_torso"]["mass_kg"])
    for index, values in enumerate(raw):
        diag = values[5:8].copy()
        off = values[8:11].copy()
        contraction = 0
        while True:
            tensor = np.asarray([
                [diag[0], off[0], off[1]],
                [off[0], diag[1], off[2]],
                [off[1], off[2], diag[2]],
            ])
            if valid_inertia(tensor):
                break
            diag = nominal + 0.5 * (diag - nominal)
            off *= 0.5
            contraction += 1
            if contraction > 16:
                raise RuntimeError("could not produce a valid coupled inertia sample")
        rows.append({
            "id": f"{name}_{index:02d}",
            "all_link_mass_scale": float(values[0]),
            "torso_mass_add_kg": float(values[1]),
            "resulting_torso_mass_kg": float(torso_mass * values[0] + values[1]),
            "torso_com_offset_m": values[2:5].tolist(),
            "torso_inertia_tensor_kg_m2": tensor.tolist(),
            "inertia_validity_contractions": contraction,
            "sampling_role": name,
            "optional_configuration_semantics": "aggregate_optional_non_locomotion_configuration",
        })
    return rows


def fixed_anchors(basis: dict[str, Any]) -> list[dict[str, Any]]:
    domain = basis["frozen_continuous_domain"]
    nominal = np.asarray(basis["compiled_torso"]["principal_inertia_kg_m2"], dtype=float)
    diag_bounds = np.asarray([
        domain["torso_inertia"]["principal_component_bounds_kg_m2"][axis]
        for axis in ("ixx", "iyy", "izz")
    ])

    def row(
        ident: str, *, scale: float = 1.0, add: float = 0.0,
        com: tuple[float, float, float] = (0.0, 0.0, 0.0),
        diag: np.ndarray | None = None, optional: bool = False,
    ) -> dict[str, Any]:
        values = nominal if diag is None else np.asarray(diag)
        return {
            "id": ident,
            "all_link_mass_scale": scale,
            "torso_mass_add_kg": add,
            "torso_com_offset_m": list(com),
            "torso_inertia_tensor_kg_m2": np.diag(values).tolist(),
            "optional_configuration_semantics": (
                "aggregate_optional_non_locomotion_configuration" if optional else "none"
            ),
        }

    anchors = [
        row("MASS_LOW", scale=0.9, add=-0.1, diag=nominal * 0.9),
        row("MASS_HIGH", scale=1.1, add=0.1, diag=nominal * 1.1),
    ]
    for axis in range(3):
        for sign, label in ((-0.05, "NEG"), (0.05, "POS")):
            com = [0.0, 0.0, 0.0]
            com[axis] = sign
            anchors.append(row(f"COM_{'XYZ'[axis]}_{label}", com=tuple(com)))
    for axis in range(3):
        for endpoint, label in ((0, "LOW"), (1, "HIGH")):
            diag = nominal.copy()
            diag[axis] = diag_bounds[axis, endpoint]
            anchors.append(row(f"INERTIA_{'XYZ'[axis]}_{label}", diag=diag))
    for corner_index, signs in enumerate(
        (x, y, z) for x in (-0.05, 0.05) for y in (-0.05, 0.05) for z in (-0.05, 0.05)
    ):
        high = bool(corner_index % 2)
        anchors.append(row(
            f"COM_CORNER_{corner_index:02d}",
            scale=1.1 if high else 0.9,
            add=0.1 if high else -0.1,
            com=signs,
            diag=diag_bounds[:, 1 if high else 0],
            optional=True,
        ))
    anchors.extend([
        row(
            "OPTIONAL_AGGREGATE_LIGHT_FORWARD", scale=0.9, add=-0.05,
            com=(0.025, 0.0, 0.025), diag=nominal * 0.9, optional=True,
        ),
        row(
            "OPTIONAL_AGGREGATE_HEAVY_AFT", scale=1.1, add=0.05,
            com=(-0.025, 0.0, -0.025), diag=nominal * 1.1, optional=True,
        ),
    ])
    if len(anchors) != 24:
        raise AssertionError(len(anchors))
    return anchors


def main() -> int:
    basis = json.loads(BASIS.read_text())
    if basis["decision"] != "PASS_VARIABLE_CONFIGURATION_DOMAIN_BASIS_CURRENT_CANDIDATE_HELD":
        raise ValueError("supported-configuration basis is not passed")
    if sha256(BASIS) != "d699dce08b24715a9e61e86feafab238192aeb92d130d24c9da05d50d0dbeb08":
        raise ValueError("supported-configuration basis hash changed")

    discovery = make_sample_set(name="DISCOVERY", seed=DISCOVERY_SEED, count=16, basis=basis)
    heldout = make_sample_set(name="HELDOUT", seed=HELDOUT_SEED, count=16, basis=basis)
    anchors = fixed_anchors(basis)
    actuator = actuator_domain()
    sensor_noise = {
        "hip_pos_rad": 0.03, "knee_pos_rad": 0.05, "ankle_pos_rad": 0.08,
        "joint_vel_rad_s": 2.5, "gravity": 0.1, "linvel_m_s": 0.1,
        "gyro_rad_s": 0.1, "accelerometer": 0.05,
    }
    base_cells = 2 * 2 * 4
    matrix = {
        "checkpoints_full_domain_relative_steps": [1003520, 2007040],
        "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
        "commands_x_m_s": [0.0, 0.074, 0.077, 0.080],
        "nominal_seeds": [167931544, 528299293],
        "other_seed": 167931544,
        "duration_ticks": 600,
        "control_hz": 50,
        "physics_substeps_per_tick": 10,
        "fixed_anchor_count": len(anchors),
        "discovery_count": len(discovery),
        "heldout_count": len(heldout),
        "sensor_transport_conditions": [
            {"id": "NATIVE_INPUT_QUANTIZATION", "native_quantization": True},
            {"id": "DECLARED_SENSOR_NOISE", "sensor_noise_scales": sensor_noise},
            {"id": "ACTION_DELAY_1", "additional_action_delay_ticks": 1},
            {"id": "ACTION_DELAY_2", "additional_action_delay_ticks": 2},
            {"id": "IMU_DELAY_1", "imu_delay_ticks": 1},
            {"id": "IMU_DELAY_2", "imu_delay_ticks": 2},
        ],
        "cell_count_derivation": {
            "nominal": base_cells * 2,
            "fixed_anchors": base_cells * len(anchors),
            "discovery": base_cells * len(discovery),
            "heldout": base_cells * len(heldout),
            "sensor_transport": base_cells * 6,
            "total": base_cells * (2 + len(anchors) + len(discovery) + len(heldout) + 6),
        },
        "fixed_anchors": anchors,
        "discovery_samples": discovery,
        "heldout_samples": heldout,
    }
    if matrix["cell_count_derivation"]["total"] != 1024:
        raise AssertionError(matrix["cell_count_derivation"])

    result = {
        "schema_version": "winner_v3.variable_configuration_replacement_preregistration.v1",
        "status": "PREREGISTERED_CPU_CONTRACT_FIRST",
        "causal_question": (
            "Can the protected command-tracking winner become persistent over the frozen broad "
            "configuration domain when given deployable temporal state and trained over coupled "
            "mass/COM/inertia, measured actuator, sensor, and transport variation?"
        ),
        "falsified_routes_not_reopened": [
            "memoryless targeted COM exposure", "reset-latched COM class", "frozen-base oracle residual",
            "oracle sequence rescue", "oracle viability funnel", "per-unit static COM measurement",
        ],
        "sources": {
            "domain_basis": source(BASIS),
            "tracking_tail_archive": source(TAIL_ARCHIVE),
            "tracking_tail_preregistration": source(TAIL_PREREG),
            "projected_reference_table": source(REFERENCE),
            "p30_all_joint_fit": source(P30_ALL),
            "p30_pitch_fit": source(P30_PITCH),
            "p31_34_pitch_fit": source(P31_PITCH),
            "current_candidate_break_result": source(BREAK_RESULT),
            "reference_residual_actor": source(ROOT / "patches/reference_residual_hard_vector_ppo_networks.py"),
            "historical_recurrent_actor": source(ROOT / "patches/ground_up_recurrent_ppo.patch"),
        },
        "protected_restore": {
            "archive_member": "ground_up_tracking_tail_outputs/T2_EQUAL/2026_07_14_190026_512000/",
            "source_stage_step": 512000,
            "source_recipe": "T2_EQUAL",
            "source_tail_scale": -6572.254964031055,
            "base_actor_and_privileged_critic_restored": True,
            "training_reward_selection": False,
        },
        "single_candidate": {
            "id": "R64_ZERO_INIT_RECURRENT_ADAPTER",
            "actor": {
                "base": "protected 115-D reference-residual actor, hidden sizes [512,256,128]",
                "adapter_state_dim": 64,
                "state_update": "h_out=tanh(normalized_obs@W_obs+h_in@W_h+b_h)",
                "action_composition": "base anchored action location + h_out@W_adapter+b_adapter",
                "initialization": {
                    "base_parameters": "exact protected restore",
                    "W_obs_W_h_b_h": "standard deterministic seed-100 initialization",
                    "W_adapter_b_adapter": "exact zeros",
                    "step_zero_action_equivalence": "bit-exact base distribution location and deterministic action for every observation/history control vector",
                },
                "trainable": "base actor plus recurrent adapter; no frozen-base restriction",
                "corrected_joints": "all 14 policy joints",
                "oracle_inputs": False,
                "true_configuration_parameter_input": False,
            },
            "critic": "unchanged protected privileged critic architecture and observation",
            "policy_inputs": {
                "obs": [1, 115], "previous_action": [1, 14], "h_in": [1, 64],
            },
            "policy_outputs": {
                "continuous_actions": [1, 14], "previous_action_out": [1, 14], "h_out": [1, 64],
            },
            "reset": "h_in and previous_action reset to exact zero only at deterministic episode reset",
            "baked_post_actor_transforms_in_order": [
                "measured hard-vector projection", "actual-centered tracking guard",
                "conservative all-joint actuator envelope", "exact x=0 command deadband",
            ],
        },
        "training": {
            "execution": "CPU_ONLY_SINGLE_PROCESS_NO_RETRY",
            "seed": 100,
            "stages": [
                {"id": "DOMAIN_25_PERCENT", "steps": 245760, "deviation_scale": 0.25},
                {"id": "DOMAIN_50_PERCENT", "steps": 245760, "deviation_scale": 0.50},
                {"id": "DOMAIN_100_PERCENT", "steps": 2007040, "deviation_scale": 1.00,
                 "persistent_exports_relative_steps": [1003520, 2007040]},
            ],
            "ppo": {
                "num_envs": 256, "episode_length": 600, "unroll_length": 20,
                "batch_size": 256, "num_minibatches": 4, "updates_per_batch": 4,
                "learning_rate": 0.0003, "discounting": 0.97, "entropy_cost": 0.005,
                "imitation_scale": 1.0, "tail_scale": -6572.254964031055,
                "command_x_sampling": "uniform [0.074,0.080)", "reference_start_phase": 0,
            },
            "domain_schedule": {
                "configuration": basis["frozen_continuous_domain"],
                "coupled_sampler": "same positive-definite, triangle-valid full-tensor sampler frozen in this artifact",
                "floor_friction": [0.5, 1.0],
                "joint_frictionloss_scale": [0.9, 1.1],
                "armature_scale": [1.0, 1.05],
                "actuator": actuator,
                "sensor_noise_maximum_scales": sensor_noise,
                "native_input_quantization_probability": 0.5,
                "all deviations scaled about nominal by the active curriculum fraction": True,
            },
            "cpu_contract_before_training": [
                "clean pinned source compose and exact archive hash",
                "checkpoint restore on CPU and exact parameter round trip",
                "step-zero base-action equivalence for fixed and pseudorandom vectors",
                "hidden state changes while zero adapter head preserves action",
                "1024-step update produces finite metrics/parameters and updates base and adapter actor leaves",
                "ONNX/JAX action and both state outputs agree within 1e-7",
                "CPU throughput ceiling predicts completion without using an accelerator",
            ],
            "stop_rules": [
                "any CPU contract failure", "nonfinite metric or parameter", "restore mismatch",
                "ABI/export mismatch", "wall-time ceiling exceeded", "interrupted process",
            ],
            "forbidden_after_outcome": (
                "retry, seed/LR/reward/architecture/domain/curriculum/checkpoint/horizon/bridge/command/reset change"
            ),
        },
        "actuator_domain": actuator,
        "evaluation_matrix": matrix,
        "per_cell_contract": {
            "reset": "deterministic home-support; exact h/previous-action zero",
            "model_readback": "exact per-run body name/id, mass, COM, full inertia tensor, actuator, delay, sensor and transport readback",
            "moving": (
                "600 ticks, duration_complete, PASS_CANDIDATE_SIM_GATE, bilateral left/right transitions, "
                "positive command-consistent mean vx, zero saturation, zero rate/envelope excess, tracking p95<=0.20 rad"
            ),
            "zero_command": (
                "600 ticks, duration_complete, PASS_CANDIDATE_SIM_GATE, |mean local vx|<=0.02 m/s, "
                "body pitch p95<=0.25 rad, base height>=0.12 m, tracking p95<=0.20 rad, "
                "zero saturation and zero rate/envelope excess"
            ),
            "all_joint_tracking_p95_rad_max": 0.20,
            "all_joint_current_p95_a_max": 0.65,
            "current_derivation": "abs(sim actuator torque N.m)/(8 kgf.cm/A = 0.784532 N.m/A)",
            "training_or_simulator_reward_has_selection_weight": False,
        },
        "advancement": {
            "rule": (
                "both full-domain checkpoints must pass all 1024 cells, including every heldout cell; "
                "a sibling checkpoint, closest configuration, or aggregate score cannot be promoted"
            ),
            "pass_token": "PASS_WINNER_V3_VARIABLE_CONFIGURATION_REPLACEMENT",
            "fail_token": "HOLD_WINNER_V3_VARIABLE_CONFIGURATION_REPLACEMENT",
            "invalid_token": "INVALID_WINNER_V3_VARIABLE_CONFIGURATION_STUDY",
        },
        "observable_response_envelope_v2": {
            "metric_count": 73,
            "per_joint_metrics": ["delay_ticks", "gain_ratio", "time_constant_s", "tracking_p95_rad", "current_p95_a"],
            "body_metrics": ["pitch_rate_p95_rad_s", "roll_rate_p95_rad_s", "accel_norm_p95_m_s2"],
            "bounds_derivation": {
                "delay_gain_time_constant": "exact frozen actuator-domain min/max",
                "tracking_p95": "[0, ceil(max passing 1024-cell value / (2*pi/4096)) * (2*pi/4096)], capped at 0.20",
                "current_p95": "[0, ceil(max passing 1024-cell value / 0.0065 A) * 0.0065 A], capped at 0.65 A",
                "pitch_roll_rate_p95": "[0, ceil(max passing value / (pi/(180*16))) * pi/(180*16)]",
                "accel_norm_p95": "[0, ceil(max passing value / 0.01) * 0.01]",
            },
            "physical_calibration_can_widen": False,
            "publication_order": [
                "preregistration commit", "selected-policy commit", "clearance artifact commit",
                "later supported_configuration_envelope.v2 publication commit",
            ],
        },
        "required_artifacts": [
            "WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT_20260719.md",
            "winner_v3_recurrent_adapter_cpu_contract.json",
            "winner_v3_recurrent_adapter_training_result.json",
            "winner_v3_recurrent_adapter_artifacts.tar.gz",
            "winner_v3_variable_configuration_cells/*.json",
            "winner_v3_variable_configuration_traces/*.jsonl",
            "WINNER_V3_VARIABLE_CONFIGURATION_RESULT_20260719.md",
            "winner_v3_variable_configuration_result.json",
            "policy_robot_clearance_v1.json only after pass",
            "supported_configuration_envelope_v2.json only after later clearance commit",
        ],
        "current_candidate": {
            "onnx_sha256": "99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de",
            "prior_result_reused_not_rerun": source(BREAK_RESULT),
            "status": "FAILED_REQUIRED_X_DOMAIN_HELD",
            "selection_eligible": False,
        },
        "authority": {
            "cpu_contract": True,
            "cpu_training_after_contract_pass": True,
            "cpu_evaluation_after_valid_artifact_contract": True,
            "hosted_or_colab": False,
            "gpu_or_igpu": False,
            "rdkx5_or_robot": False,
            "serial_gpio_i2c": False,
            "torque_or_motion": False,
            "robot_clearance_before_complete_pass": False,
            "runtime_or_gate5": False,
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(f"""# Winner-v3 Variable-Configuration Replacement Preregistration — 2026-07-19

Status: `PREREGISTERED_CPU_CONTRACT_FIRST`

## Frozen decision

The current `99d3afce…304de` graph is held by its already-hashed X-COM failure
bracket and is not rerun. The single prospective replacement is
`R64_ZERO_INIT_RECURRENT_ADAPTER`: a 64-state deployable recurrent adapter on
the protected T2_EQUAL 512,000 checkpoint. Its action head begins at exact
zero, so step-zero deterministic actions equal the protected base while the
hidden state can evolve. The protected actor, adapter, and unchanged privileged
critic may then train together. There is no oracle or true configuration input.

The choice is causal, not a search: memoryless exposure, the reset latch, and
frozen-base oracle correction have already failed, while a zero-head adapter
tests whether deployable history plus base-policy adaptation can use the
time-varying signal without discarding the verified gait at initialization.

## Frozen domain and training

Training is CPU only, seed 100, one process, no retry. It restores the protected
T2_EQUAL archive `{sha256(TAIL_ARCHIVE)}` and preserves the PPO recipe and
training reward. Domain deviations run at 25% for 245,760 steps, 50% for
245,760, then the full domain for 2,007,040 steps. Formal checkpoints are
1,003,520 and 2,007,040 steps into the full-domain stage. No training reward is
used for selection.

The full stage samples the basis' independent ±0.05 m torso COM axes,
0.5286734–0.8683786 kg resulting torso mass, full positive-definite and
triangle-valid inertia tensors, passed friction/frictionloss/armature ranges,
both measured actuator configurations, declared sensor noise, native
quantization, and zero-to-two-tick additional action/IMU delay.

## Frozen evaluation

Exactly 1,024 CPU cells are frozen: 32 nominal; 384 over 24 fixed aggregate
anchors; 256 over 16 discovery coupled samples; 256 over a separately seeded
16-sample heldout set; and 96 native-quantization/noise/delay cells. Every set
crosses both full-domain checkpoints, both actuator plants, and commands
`0/.074/.077/.080`; every cell is 600 ticks with exact per-run readback.

The existing gates remain unchanged. Moving commands require complete duration,
bilateral transitions, positive command-consistent motion, the candidate gate,
tracking p95 <=.20 rad, and zero saturation/rate/envelope excess. At x=0,
absolute mean local vx must be <=.02 m/s, pitch p95 <=.25 rad, base height
>=.12 m, and the same tracking/safety limits. All-joint current p95 must also be
<=.65 A, derived from simulated torque using the STS3215 8 kg.cm/A constant.

Both checkpoints must pass all 1,024 cells. There is no closest-policy
promotion and no post-outcome change. A pass only permits the ordered policy
asset/clearance/envelope commits and a new two-repository runtime freeze; it is
not X5 execution, robot use, motion, Gate 5, or deployment clearance.

## Authority

This preregistration authorizes the CPU implementation contract, and only after
that contract passes, the single CPU training process and frozen CPU evaluation.
It authorizes no Colab/hosted allocation, GPU/iGPU, RDK-X5, robot, serial,
GPIO/I2C, torque, motion, runtime execution, Gate 5, or deployment.
""")
    print(result["status"])
    print(f"cells={matrix['cell_count_derivation']['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
