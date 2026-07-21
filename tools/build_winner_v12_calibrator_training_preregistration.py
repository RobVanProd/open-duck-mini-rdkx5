#!/usr/bin/env python3
"""Freeze the Winner-v12 calibrator-training plan before implementation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT_JSON = ANALYSIS / "winner_v12_calibrator_training_preregistration.json"
OUTPUT_MD = ANALYSIS / "WINNER_V12_CALIBRATOR_TRAINING_PREREGISTRATION_20260720.md"
HANDOFF = ROOT / "artifacts/runtime_handoff/rdkx5_native_20260719"

SOURCES = {
    "builder": Path(__file__),
    "winner_v12_mechanics_preregistration": (
        ANALYSIS / "winner_v12_zero_ppo_decomposed_backend_preregistration.json"
    ),
    "winner_v12_mechanics_result": (
        ANALYSIS / "winner_v12_zero_ppo_decomposed_backend_result.json"
    ),
    "winner_v11_interface": (
        ANALYSIS / "winner_v11_dynamic_calibration_interface_preregistration.json"
    ),
    "winner_v6_interface": (
        ANALYSIS / "winner_v6_dynamic_calibration_interface_preregistration.json"
    ),
    "winner_v12_network": ROOT / "patches/winner_v12_decomposed_backend_networks.py",
    "winner_v11_network": ROOT / "patches/winner_v11_dynamic_calibration_networks.py",
    "winner_v3_domain_basis": (
        ANALYSIS / "winner_v3_supported_configuration_basis.json"
    ),
    "winner_v3_domain_preregistration": (
        ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
    ),
    "winner_v3_failure_attribution": (ANALYSIS / "winner_v3_failure_attribution.json"),
    "winner_v5_support_preregistration": (
        ANALYSIS / "winner_v5_automatic_support_recovery_preregistration.json"
    ),
    "winner_v10_representation": (
        ANALYSIS / "winner_v10_inward_torque_contract_result.json"
    ),
    "winner_v10_nominal": ANALYSIS / "winner_v10_nominal_behavior_result.json",
    "winner_v10_r2_condition6": (ANALYSIS / "winner_v10_r2_condition6_result.json"),
    "winner_v10_r2_condition7_hold": (
        ANALYSIS / "winner_v10_r2_condition7_result.json"
    ),
    "current_gate": (ANALYSIS / "winner_v3_current_gate_application_contract.json"),
    "p30_fit": ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json",
    "p31_34_fit": ANALYSIS / "fixed_target_p31_34_actuator_fit_20260712.json",
    "runtime_observation_map": HANDOFF / "observation_map.json",
    "runtime_policy_contract": HANDOFF / "policy_contract.json",
    "runtime_observer_contract": HANDOFF / "observer_contract.json",
    "runtime_observer_cross_fit": (
        ANALYSIS / "winner_v2_observer_cross_fit_result.json"
    ),
    "runtime_p30_observer": HANDOFF / "observer/winner_v2_contract.py",
}
REFERENCE_TABLE = HANDOFF / "reference/ground_up_projected_reference_feature_table.npz"


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def sha256_raw(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    v12 = json.loads(SOURCES["winner_v12_mechanics_result"].read_text(encoding="utf-8"))
    v11_interface = json.loads(
        SOURCES["winner_v11_interface"].read_text(encoding="utf-8")
    )
    v6_interface = json.loads(
        SOURCES["winner_v6_interface"].read_text(encoding="utf-8")
    )
    domain_basis = json.loads(
        SOURCES["winner_v3_domain_basis"].read_text(encoding="utf-8")
    )
    domain_prereg = json.loads(
        SOURCES["winner_v3_domain_preregistration"].read_text(encoding="utf-8")
    )
    condition7 = json.loads(
        SOURCES["winner_v10_r2_condition7_hold"].read_text(encoding="utf-8")
    )
    winner_v5 = json.loads(
        SOURCES["winner_v5_support_preregistration"].read_text(encoding="utf-8")
    )
    current_contract = json.loads(SOURCES["current_gate"].read_text(encoding="utf-8"))
    observer_contract = json.loads(
        SOURCES["runtime_observer_contract"].read_text(encoding="utf-8")
    )
    observer_cross_fit = json.loads(
        SOURCES["runtime_observer_cross_fit"].read_text(encoding="utf-8")
    )
    if v12["status"] != "PASS_WINNER_V12_ZERO_PPO_DECOMPOSED_BACKEND_MECHANICS":
        raise ValueError("Winner-v12 mechanics is not passing")
    if v12["decision"] != (
        "AUTHORIZE_SEPARATE_WINNER_V12_TRAINING_PREREGISTRATION_ONLY"
    ):
        raise ValueError("Winner-v12 did not authorize this preregistration")
    if v12["authority"] != {
        "separate_training_preregistration_design": True,
        "training_or_optimizer": False,
        "behavior_evaluation": False,
        "runtime_implementation": False,
        "robot_rdk_torque_motion_gate5_deployment": False,
        "robot_clearance": False,
    }:
        raise ValueError("Winner-v12 authority boundary changed")
    if condition7["status"] != "HOLD_WINNER_V10_R2_CONDITION7_TORSO_COM_X_NEG":
        raise ValueError("the causal Winner-v10 configuration failure changed")
    if domain_basis["status"] != (
        "PASS_VARIABLE_CONFIGURATION_DOMAIN_BASIS_CURRENT_CANDIDATE_HELD"
    ):
        raise ValueError("the frozen hidden-configuration domain is not valid")
    if current_contract["status"] != (
        "PASS_PROSPECTIVE_CURRENT_GATE_APPLICATION_CONTRACT"
    ):
        raise ValueError("the frozen prospective current gate is not valid")
    if observer_cross_fit["status"] != ("PASS_P30_OBSERVER_MEASURED_CROSS_FIT_BRACKET"):
        raise ValueError("the fixed P30 observer cross-fit gate is not valid")
    if observer_contract["fit_path"] != "observer/p30_actuator_fit.json":
        raise ValueError("runtime observation observer is not the fixed P30 fit")
    if observer_contract["fit_provenance"]["cross_fit_result_sha256"] != sha256_lf(
        SOURCES["runtime_observer_cross_fit"]
    ):
        raise ValueError("runtime P30 observer cross-fit receipt changed")

    requested = v11_interface["requested_interface"]
    if requested["observation_contract"] != "winner-v2-115d":
        raise ValueError("Winner-v12 training requires the reviewed 115-D contract")
    support_gate = v6_interface["after_runtime_review_only"]["support_pass"]
    final_window_ticks = winner_v5["pass_requirements"]["final_window_ticks"]
    if final_window_ticks != 50:
        raise ValueError("the frozen support final window changed")
    evaluation = domain_prereg["evaluation_matrix"]
    fixed_anchors = evaluation["fixed_anchors"]
    discovery = evaluation["discovery_samples"]
    heldout = evaluation["heldout_samples"]
    sensor_transport = evaluation["sensor_transport_conditions"]
    if (len(fixed_anchors), len(discovery), len(heldout)) != (24, 16, 16):
        raise ValueError("the frozen model population changed")
    if evaluation["actuator_plants"] != [
        "P30_ALL_JOINT",
        "P31_34_PITCH_WITH_P30_NONPITCH",
    ]:
        raise ValueError("the frozen actuator population changed")
    if len(sensor_transport) != 6:
        raise ValueError("the frozen sensor/transport population changed")
    current_gate = current_contract["prospective_offline_candidate_gate"]
    expected_current_gate = {
        "all_joints_must_pass": True,
        "early_terminated_population": "evaluate every recorded tick before termination",
        "per_joint_peak_current_a_max": 2.5,
        "per_joint_peak_torque_kgf_cm_max": 19.5,
        "per_joint_peak_torque_nm_max": 1.91229675,
        "rated_current_p95": {
            "candidate_pass_fail": False,
            "reason": (
                "manufacturer evidence defines a rated operating point but does not "
                "define p95 over a 600-tick rollout as a safety or thermal rule"
            ),
            "role": "reported diagnostic only",
            "value_a": 0.65,
        },
        "sample_clock": "exact simulator 50 Hz ticks",
        "strict_overcurrent_max_consecutive_ticks": 99,
        "strict_overcurrent_threshold_a": 2.0,
        "strict_overcurrent_trip_duration_s": 2.0,
        "strict_overcurrent_trip_ticks": 100,
    }
    if current_gate != expected_current_gate:
        raise ValueError("the prospective current gate changed")

    sources = {
        name: {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "sha256": sha256_lf(path),
            "hash_mode": "sha256 after CRLF-to-LF normalization",
        }
        for name, path in SOURCES.items()
    }
    sources["runtime_reference_table"] = {
        "path": str(REFERENCE_TABLE.relative_to(ROOT)).replace("\\", "/"),
        "sha256": sha256_raw(REFERENCE_TABLE),
        "hash_mode": "raw sha256",
    }
    protected_policies = v12["protected_policy_hashes"]
    result = {
        "schema_version": "winner_v12.calibrator_training_preregistration.v2",
        "status": "PREREGISTERED_IMPLEMENTATION_NOT_RUN",
        "decision": (
            "AUTHORIZE_WINNER_V12_CALIBRATOR_IMPLEMENTATION_AND_CPU_SMOKE_CONTRACT_ONLY"
        ),
        "contract_id": "winner-v12-two-stage-automatic-calibrator-r64-fixed-p30",
        "supersedes": {
            "artifact_sha256": (
                "4b1a1822e7e03d9bc3cb5773fdb28f7580210ef097c218d6da282e747d75909a"
            ),
            "commit": "5236e47f48feab09da44797445119d181a8ec310",
            "disposition": "SUPERSEDED_BEFORE_ANY_OPTIMIZER_STEP",
            "optimizer_steps_executed_under_superseded_contract": 0,
            "reason": (
                "the v1 wording selected the observation observer with the hidden "
                "P30/P31 physical plant, which leaked a deployment-impossible plant "
                "choice; v2 restores the reviewed fixed-P30 runtime semantics"
            ),
        },
        "causal_hypothesis": (
            "Winner-v10 fails hidden build variation because its walking actor receives "
            "no per-session response evidence. A 250-tick recurrent calibrator can "
            "learn a deployable-observation-only response state, then use that fixed "
            "state encoder to learn graph-bounded support actions before locomotion, "
            "without any manual mass, COM, inertia, dimension, or component input."
        ),
        "why_this_follows_evidence": {
            "winner_v10_terminal_failure": condition7["status"],
            "winner_v12_mechanics_pass": v12["status"],
            "closed_winner_v11_preserved": True,
            "manual_configuration_route_reopened": False,
            "protected_walking_policy_changed": False,
            "locomotion_adapter_trained_in_this_stage": False,
            "fixed_p30_observer_cross_fit_pass": observer_cross_fit["status"],
        },
        "sources": sources,
        "protected_policies": protected_policies,
        "frozen_interface": {
            "calibrator": requested["calibrator"],
            "locomotion": requested["locomotion"],
            "observation_contract": "winner-v2-115d",
            "calibration_ticks": 250,
            "context_handoff": requested["context_handoff"],
            "previous_action_and_applied_target_handoff": requested[
                "previous_action_and_applied_target_handoff"
            ],
            "runtime_v1_101x14_changed": False,
            "runtime_v2_115d_semantics_changed": False,
        },
        "automatic_only": {
            "manual_measurements_required": False,
            "mass_com_inertia_dimensions_component_identity_inputs": False,
            "true_configuration_actor_inputs": False,
            "true_configuration_auxiliary_targets": False,
            "configuration_visible_only_to_simulator_randomizer": True,
            "runtime_context_source": "final successful calibrator h_out[1,64]",
            "runtime_context_persisted_between_sessions": False,
            "training_data_routing": {
                "response_encoder_inputs": (
                    "deployable obs[1,115], previous_action[1,14], and h_in[1,64] only"
                ),
                "action_head_input": "response encoder h_out[1,64] only",
                "training_only_value_head_input": ("response encoder h_out[1,64] only"),
                "training_only_auxiliary_inputs": (
                    "response encoder h_out[1,64] and current realized action a_t[1,14] only"
                ),
                "training_only_auxiliary_targets": (
                    "next valid deployable obs_(t+1) indices [0:6], [13:41], and [83:99] only"
                ),
                "simulator_randomizer_fields_concatenated_to_network_input": False,
            },
        },
        "calibration_episode": {
            "frequency_hz": 50,
            "duration_ticks": 250,
            "command": "exact float32 zeros[7]",
            "phase": [1.0, 0.0],
            "phase_advances": False,
            "initial_previous_action": "exact float32 zeros[1,14]",
            "initial_hidden": "exact float32 zeros[1,64]",
            "projected_reference": "frozen x=0 phase-index-zero reference",
            "observation_order": "exact frozen winner-v2 115-D order",
            "applied_target_observation": (
                "exact fixed runtime P30 observer for every episode, including when "
                "the hidden physical plant is P31/34"
            ),
            "hidden_physics_actuator_plant": (
                "selected P30 or P31/34 plant; never exposed by changing obs[83:97]"
            ),
            "action_boundary": (
                "graph-owned Winner-v10 stored/inward vector; no host limiter"
            ),
            "x0_deadband_on_calibrator": False,
            "support_mode": v6_interface["calibration_sequence"]["support_mode"],
        },
        "two_stage_training": {
            "stage_1_response_encoder": {
                "rollout_action": (
                    "training-only seed-locked ternary exploration increments "
                    "{-0.25,0,+0.25} times the per-joint inward action-delta vector, "
                    "accumulated through the exact graph absolute/slew boundary; the "
                    "actor action head remains exact zero; the exploration generator "
                    "is training-only and is not exported or used at runtime, while "
                    "its realized bounded action is committed through the normal "
                    "previous_action and observation-state chain"
                ),
                "transition_order": [
                    (
                        "at tick t compose obs_t from the last committed valid state: "
                        "previous_action is realized action a_(t-1), obs[41:55], "
                        "obs[55:69], and obs[69:83] are a_(t-2), a_(t-3), and "
                        "a_(t-4), and obs[83:97] is the fixed runtime P30 observer "
                        "value from tick t-1 regardless of the hidden physical plant"
                    ),
                    (
                        "draw the seed-locked ternary increment for tick t and apply "
                        "the exact graph absolute/slew boundary relative to realized "
                        "a_(t-1), producing current realized action a_t"
                    ),
                    (
                        "advance the fixed P30 observation observer from the sent "
                        "target and independently step the selected hidden P30/P31-34 "
                        "physical plant with a_t; the auxiliary predictor consumes "
                        "current h_t and current realized a_t and targets the resulting "
                        "next-tick deployable fields"
                    ),
                    (
                        "commit action history, applied-target observer state, sensors, "
                        "and recurrent h_out only after a valid transition; on tick "
                        "t+1 previous_action is a_t and obs[83:97] is the fixed P30 "
                        "observation-observer value advanced from the sent target at t"
                    ),
                ],
                "trainable_leaves": [
                    "obs_weight",
                    "previous_action_weight",
                    "hidden_weight",
                    "hidden_bias",
                    "auxiliary_hidden_weight",
                    "auxiliary_action_weight",
                    "auxiliary_bias",
                ],
                "frozen_leaves": ["action_weight", "action_bias"],
                "target": (
                    "next-tick values of the frozen deployable observation indices "
                    "[0:6], [13:41], and [83:99]"
                ),
                "target_semantics": (
                    "target obs_(t+1)[83:97] is the fixed P30 observation-observer "
                    "output; obs_(t+1)[97:99] and the physics-derived sensor/joint "
                    "fields reflect the selected hidden plant, but no P31/34 parameter "
                    "or plant label enters the observer or auxiliary routing"
                ),
                "loss": (
                    "mean squared error after per-field normalization computed from "
                    "training rollouts only, with float64 empirical mean and "
                    "std=max(empirical_std,1e-6), then float32 normalized arrays; "
                    "invalid/padded ticks masked and heldout cells excluded"
                ),
                "true_configuration_label_used": False,
                "required_nonzero_gradient_paths": [
                    "previous_action_weight",
                    "auxiliary_action_weight",
                ],
            },
            "stage_2_support_controller": {
                "trainable_leaves": [
                    "action_weight",
                    "action_bias",
                    "training_only_log_std",
                    "training_only_value_weight",
                    "training_only_value_bias",
                ],
                "frozen_leaves": (
                    "all stage-1 response encoder and auxiliary predictor leaves"
                ),
                "algorithm": (
                    "recurrent PPO with training-only diagonal-Gaussian log_std and "
                    "training-only value head; exact PPO and optimizer constants must "
                    "be frozen by the implementation contract before the smoke"
                ),
                "discount_factor_gamma": 1.0,
                "stochastic_policy": {
                    "distribution": "training-only diagonal Gaussian",
                    "log_std_initialization": (
                        "elementwise log(0.25 * per-joint inward action-delta vector)"
                    ),
                    "deployable_export": "deterministic bounded action mean only",
                    "log_std_exported": False,
                },
                "transition_validity": {
                    "both_contacts_required": True,
                    "minimum_base_z_m": 0.1,
                    "maximum_abs_roll_pitch_rad": 0.35,
                    "per_joint_current_estimate": (
                        "abs(MuJoCo data.actuator_force[joint] N.m) / 0.784532 N.m/A"
                    ),
                    "per_joint_peak_current_a_max": 2.5,
                    "per_joint_peak_torque_nm_max": 1.91229675,
                    "per_joint_peak_torque_kgf_cm_max": 19.5,
                    "strict_overcurrent_threshold_a": 2.0,
                    "strict_overcurrent_trip_ticks": 100,
                    "strict_overcurrent_max_consecutive_ticks": 99,
                    "invalid_transition_terminates_episode": True,
                },
                "per_tick_reward": (
                    "1.0 for each valid transition: both contacts, base-z >= 0.1 m, "
                    "absolute roll/pitch <= 0.35 rad, every absolute joint actuator "
                    "force <= 1.91229675 N.m (19.5 kgf.cm), every joint current <= "
                    "2.5 A, and no joint's strictly-above-2.0-A streak reaches 100 "
                    "ticks; 0.0 after termination"
                ),
                "terminal_success_bonus": {
                    "value": 250.0,
                    "condition": (
                        "episode completes all 250 valid ticks and the maximum "
                        "Euclidean norm of unbiased simulator gyro XY over the final "
                        "50 ticks is <= 0.05 rad/s"
                    ),
                    "derivation": (
                        "equal to the 250-tick horizon with gamma fixed at 1.0, so a "
                        "complete settled pass strictly dominates any non-settled or "
                        "early-terminated return"
                    ),
                },
                "maximum_return_without_terminal_success": 250.0,
                "settled_full_horizon_return": 500.0,
                "other_reward_terms": [],
                "training_reward_selection_weight": "NONE",
                "true_configuration_input_to_actor_or_critic": False,
            },
            "stage_order_fixed": True,
            "joint_end_to_end_finetuning": False,
            "locomotion_training": False,
        },
        "hidden_configuration_domain": {
            "continuous_training_domain": domain_prereg["training"]["domain_schedule"],
            "continuous_domain_canonical_sha256": canonical_sha256(
                domain_prereg["training"]["domain_schedule"]
            ),
            "actuator_plants": evaluation["actuator_plants"],
            "observation_observer": "fixed runtime P30 for every physical plant",
            "physical_plant_identity_visible_to_network": False,
            "fixed_anchor_count": len(fixed_anchors),
            "discovery_count": len(discovery),
            "heldout_count": len(heldout),
            "fixed_anchor_ids": [row["id"] for row in fixed_anchors],
            "discovery_ids": [row["id"] for row in discovery],
            "heldout_ids": [row["id"] for row in heldout],
            "sensor_transport_ids": [row["id"] for row in sensor_transport],
            "fixed_anchors_canonical_sha256": canonical_sha256(fixed_anchors),
            "discovery_canonical_sha256": canonical_sha256(discovery),
            "heldout_canonical_sha256": canonical_sha256(heldout),
            "sensor_transport_canonical_sha256": canonical_sha256(sensor_transport),
            "heldout_never_used_for_training_normalization_or_checkpoint_choice": True,
        },
        "future_support_gate": {
            **support_gate,
            "final_window_ticks": final_window_ticks,
            "final_window_gyro_definition": (
                "maximum Euclidean norm of unbiased simulator gyro XY over the final "
                "50 ticks"
            ),
            "current_safety": current_gate,
            "current_estimator": current_contract["conversion"][
                "per_tick_current_estimate_a"
            ],
            "observation_observer": "fixed runtime P30 for both physical plants",
            "model_cells": 56,
            "actuator_plants_per_model": 2,
            "core_model_actuator_cells_per_checkpoint": 112,
            "sensor_transport_conditions_on_nominal_model": 6,
            "sensor_transport_actuator_cells_per_checkpoint": 12,
            "total_cells_per_checkpoint": 124,
            "model_population": "24 fixed anchors + 16 discovery + 16 heldout",
            "sensor_transport_population": evaluation["sensor_transport_conditions"],
            "all_cells_must_pass": True,
            "selection_by_training_reward": False,
            "executed_by_this_preregistration": False,
        },
        "required_implementation_contract": {
            "before_any_optimizer_step": True,
            "checks": [
                "compose the pinned simulator and reproduce every source/domain hash",
                "reproduce exact 115-D observation, phase, history, fixed-P30 observation observer, selected hidden P30/P31-34 physical plant, reference, and action-bound semantics",
                "prove stage-1 gradients update only encoder/auxiliary leaves while the action head stays exact zero",
                "prove seed-locked bounded stage-1 exploration creates finite nonzero gradients for previous_action_weight and auxiliary_action_weight",
                "prove the realized stage-1 exploration action is chained exactly into next-tick previous_action, t-2/t-3/t-4 action histories, and fixed P30 observation-observer state",
                "prove changing only the hidden P30/P31-34 physical plant never switches or parameterizes obs[83:97], which remains the fixed runtime P30 observer validated by the frozen cross-fit receipt",
                "prove stage-2 finite nonzero gradients and its one optimizer update change every listed action/log_std/value leaf while every encoder/auxiliary leaf stays bit-exact",
                "prove stage-2 validity, termination, terminal gyro bonus, and current-streak logic exactly reproduce the frozen future support gate quantities",
                "read back the pinned XML force ranges and prove the independent 1.91229675 N.m / 19.5 kgf.cm peak-torque condition",
                "run one fixed 16-environment x 250-tick CPU smoke with one optimizer update per stage",
                "keep every parameter and metric finite and reproduce save/restore exactly",
                "export calibrator ONNX with the reviewed ABI and new-branch JAX/ONNX error <= 1e-7",
                "prove protected policies and locomotion adapter parameters are bit-exact and unused",
                "prove the exact actor and critic input schemas and auxiliary-target JAX routing contain only the frozen deployable observation, recurrent state, and action state, with no simulator-randomizer or true-configuration fields",
                "prove the stage-1 exploration generator, stage-1 auxiliary predictor, training-only log_std, and training-only value head are absent from the deployable ONNX graph",
            ],
            "smoke_seed": 120120,
            "smoke_environments": 16,
            "smoke_ticks_per_environment": 250,
            "stage_1_optimizer_updates": 1,
            "stage_2_optimizer_updates": 1,
            "formal_support_cells": 0,
        },
        "implementation_stop_rules": [
            "any source, domain, observation, action-bound, or ABI mismatch",
            "any mismatch in the realized-action history, previous_action, applied-target, auxiliary-target, or valid-state commit timing",
            "any selected-plant identity, P31/34 parameter, or true physical response substituted into the fixed P30 obs[83:97] observer path",
            "any nonfinite parameter, gradient, metric, observation, action, or state",
            "any action-head change during stage 1 or encoder/auxiliary change during stage 2",
            "any protected-policy or locomotion-adapter change",
            "any true configuration field entering actor, critic, auxiliary target, or exported graph",
            "any training-only exploration, auxiliary, log_std, or value tensor exported into the deployable graph",
            "any mismatch from the frozen gyro-settling or current-safety criteria",
            "any JAX/ONNX new-branch error above the unchanged 1e-7 threshold",
        ],
        "attention_or_architecture_scope": {
            "quadratic_attention_added": False,
            "flat_transport_kernel_added": False,
            "reason": (
                "Winner-v12 has not yet produced evidence that its R64 response state "
                "fails long-range transport; architecture changes remain a future "
                "falsification path, not a preference-driven substitution"
            ),
        },
        "pass_authorizes_only": (
            "freeze and run one exact CPU implementation smoke contract; it does not "
            "authorize the full calibrator training run"
        ),
        "authority": {
            "design_and_implement_cpu_smoke_contract": True,
            "optimizer_steps_now": 0,
            "formal_support_cells_now": 0,
            "full_calibrator_training": False,
            "locomotion_training_or_behavior_evaluation": False,
            "colab_hosted_gpu_or_igpu": False,
            "runtime_implementation": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "gate5_deployment_checkpoint_selection_robot_clearance": False,
        },
    }
    OUTPUT_JSON.write_bytes(
        (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    digest = sha256_lf(OUTPUT_JSON)
    OUTPUT_MD.write_bytes(
        (
            "# Winner-v12 Automatic Calibrator Training Preregistration\n\n"
            f"Status: `{result['status']}`\n\n"
            f"Decision: `{result['decision']}`\n\n"
            f"JSON SHA-256: `{digest}`\n\n"
            "This freezes a two-stage automatic calibration design: learn a recurrent "
            "next-response encoder from deployable observations only, freeze it, then "
            "train only bounded support-action and training-only value heads. No mass, "
            "COM, inertia, dimension, component identity, scale, caliper, or other "
            "manual per-build input enters the graph.\n\n"
            "This v2 artifact supersedes the zero-update v1 artifact: obs[83:97] is "
            "always the reviewed fixed P30 runtime observer. P30/P31-34 selection "
            "changes only hidden physics and sensor response; it never changes or "
            "parameterizes the deployable observation path.\n\n"
            "The next permitted action is implementation and review of one CPU smoke "
            "contract. This artifact itself runs zero optimizer steps and zero formal "
            "support cells and does not authorize full training, locomotion training, "
            "runtime implementation, hardware, Gate 5, deployment, checkpoint "
            "selection, or robot clearance.\n"
        ).encode("utf-8")
    )
    print(json.dumps({"status": result["status"], "sha256": digest}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
