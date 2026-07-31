#!/usr/bin/env python3
"""Freeze the prospective Winner-v12 full calibrator-training design."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V12_FULL_CALIBRATOR_TRAINING_PREREGISTRATION_20260721.md"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
RECOVERY = ANALYSIS / "winner_v12_calibrator_artifact_recovery_result.json"
DESIGN = ANALYSIS / "winner_v12_calibrator_training_preregistration.json"
SOURCE_PATHS = {
    "builder": (
        "tools/build_winner_v12_full_calibrator_training_preregistration.py",
        "lf",
    ),
    "tests": (
        "tests/test_winner_v12_full_calibrator_training_preregistration.py",
        "lf",
    ),
    "artifact_recovery_result": (
        "outputs/analysis/winner_v12_calibrator_artifact_recovery_result.json",
        "lf",
    ),
    "calibrator_design_preregistration": (
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json",
        "lf",
    ),
    "calibrator_smoke_contract": (
        "outputs/analysis/winner_v12_calibrator_cpu_smoke_contract.json",
        "lf",
    ),
    "calibrator_smoke_failure_attribution": (
        "outputs/analysis/winner_v12_calibrator_cpu_smoke_failure_attribution.json",
        "lf",
    ),
    "calibrator_smoke_runner": (
        "tools/run_winner_v12_calibrator_cpu_smoke.py",
        "lf",
    ),
    "training_primitives": ("patches/winner_v12_calibrator_training.py", "lf"),
    "decomposed_network": (
        "patches/winner_v12_decomposed_backend_networks.py",
        "lf",
    ),
    "winner_v11_network": (
        "patches/winner_v11_dynamic_calibration_networks.py",
        "lf",
    ),
    "winner_v6_network": (
        "patches/winner_v6_dynamic_calibration_networks.py",
        "lf",
    ),
    "domain_preregistration": (
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json",
        "lf",
    ),
    "current_gate": (
        "outputs/analysis/winner_v3_current_gate_application_contract.json",
        "lf",
    ),
    "p30_fit": (
        "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json",
        "lf",
    ),
    "p31_34_fit": (
        "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json",
        "lf",
    ),
    "runtime_observer": (
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py",
        "lf",
    ),
    "runtime_observer_contract": (
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer_contract.json",
        "lf",
    ),
    "runtime_reference_table": (
        "artifacts/runtime_handoff/rdkx5_native_20260719/reference/ground_up_projected_reference_feature_table.npz",
        "raw",
    ),
    "actuator_bridge": ("tools/actuator_bridge_model.py", "lf"),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def source_manifest() -> dict[str, dict[str, str]]:
    result = {}
    for label, (relative, mode) in SOURCE_PATHS.items():
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        result[label] = {
            "path": relative,
            "hash_mode": mode,
            "sha256": lf_sha256(path) if mode == "lf" else sha256(path),
        }
    return result


def main() -> int:
    recovery = json.loads(RECOVERY.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    matrix = domain["evaluation_matrix"]
    fixed = matrix["fixed_anchors"]
    discovery = matrix["discovery_samples"]
    heldout = matrix["heldout_samples"]
    training_rows = fixed + discovery
    sensor_conditions = design["future_support_gate"]["sensor_transport_population"]
    checks = {
        "recovery_pass_exact": recovery.get("status")
        == "PASS_WINNER_V12_CALIBRATOR_ARTIFACT_RECOVERY"
        and recovery.get("decision")
        == "AUTHORIZE_FULL_CALIBRATOR_TRAINING_PREREGISTRATION_ONLY"
        and recovery.get("failed_checks") == []
        and all(recovery.get("checks", {}).values()),
        "recovery_zero_update_authority_exact": recovery.get("execution")
        == {
            "formal_support_cells": 0,
            "locomotion_behavior_cells": 0,
            "locomotion_training_steps": 0,
            "new_checkpoints_written": 0,
            "new_onnx_graphs_written": 0,
            "optimizer_updates": {"stage1": 0, "stage2": 0},
            "protected_policy_inference_calls": 0,
            "retry_of_failed_smoke": False,
            "robot_or_rdk_access": 0,
        },
        "training_population_exact": len(fixed) == 24
        and len(discovery) == 16
        and len(training_rows) == 40
        and len(heldout) == 16,
        "heldout_excluded_from_training": not (
            {row["id"] for row in training_rows} & {row["id"] for row in heldout}
        ),
        "evaluation_population_exact": len(training_rows) + len(heldout) == 56,
        "sensor_transport_population_exact": len(sensor_conditions) == 6
        and [row["id"] for row in sensor_conditions]
        == [
            "NATIVE_INPUT_QUANTIZATION",
            "DECLARED_SENSOR_NOISE",
            "ACTION_DELAY_1",
            "ACTION_DELAY_2",
            "IMU_DELAY_1",
            "IMU_DELAY_2",
        ],
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"full calibrator preregistration checks failed: {failed}")

    training_ids = [row["id"] for row in training_rows]
    heldout_ids = [row["id"] for row in heldout]
    plants = ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"]
    payload = {
        "schema_version": "winner_v12.full_calibrator_training_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V12_FULL_CALIBRATOR_TRAINING",
        "decision": "AUTHORIZE_FULL_CALIBRATOR_RUNNER_AND_CPU_CONTRACT_ONLY",
        "causal_hypothesis": (
            "A deployable-observation-only recurrent encoder trained to predict the "
            "next measured response, followed by a frozen-encoder support controller, "
            "can finish a safe 250-tick automatic calibration across the complete "
            "configuration envelope and produce a session context for later locomotion "
            "conditioning without manual per-build measurements."
        ),
        "architectural_scope": {
            "calibrator_only": True,
            "locomotion_adapter_training": False,
            "locomotion_adapter_enabled": False,
            "protected_winner_v10_changed_or_inferred": False,
            "calibration_context_used_for_walking_in_this_run": False,
            "flat_transport_kernel_added": False,
            "quadratic_attention_added": False,
            "reason_attention_is_deferred": (
                "No evidence yet shows that the frozen R64 response state fails "
                "long-range transport; the proposed flat kernel remains a future "
                "one-factor falsification, not an unmeasured architecture change."
            ),
        },
        "frozen_interface": {
            "observation": {"name": "obs", "dtype": "float32", "shape": [1, 115]},
            "previous_action": {
                "name": "previous_action",
                "dtype": "float32",
                "shape": [1, 14],
            },
            "hidden_input": {"name": "h_in", "dtype": "float32", "shape": [1, 64]},
            "outputs": [
                {"name": "calibration_actions", "dtype": "float32", "shape": [1, 14]},
                {"name": "previous_action_out", "dtype": "float32", "shape": [1, 14]},
                {"name": "h_out", "dtype": "float32", "shape": [1, 64]},
            ],
            "ticks": 250,
            "control_hz": 50,
            "phase": [1.0, 0.0],
            "phase_advances": False,
            "command": [0.0] * 7,
            "applied_target_observer": "fixed P30 for every hidden physical plant",
            "true_configuration_input": False,
            "manual_measurement_input": False,
        },
        "population": {
            "training_configuration_ids": training_ids,
            "training_configuration_sha256": canonical_sha256(training_rows),
            "training_configuration_count": 40,
            "heldout_configuration_ids": heldout_ids,
            "heldout_configuration_sha256": canonical_sha256(heldout),
            "heldout_configuration_count": 16,
            "hidden_plants": plants,
            "episodes_per_update": 80,
            "ticks_per_episode": 250,
            "scheduled_tick_slots_per_update": 20_000,
            "training_cross_product": "40 configurations x 2 hidden plants",
            "heldout_never_enters_normalization_or_optimizer": True,
            "sample_accounting": (
                "20,000 is the maximum scheduled horizon capacity per update; "
                "episodes stop on the frozen invalid-support condition, so actual "
                "sampled and valid-transition counts must be recorded separately"
            ),
        },
        "root_seed": 120120,
        "parameter_initialization": {
            "function": "winner_v12_calibrator_training.initialize_training_parameters",
            "seed": 60720,
            "keys": [
                "action_bias",
                "action_weight",
                "auxiliary_action_weight",
                "auxiliary_bias",
                "auxiliary_hidden_weight",
                "hidden_bias",
                "hidden_weight",
                "obs_weight",
                "previous_action_weight",
                "training_only_log_std",
                "training_only_value_bias",
                "training_only_value_weight",
            ],
            "tree_sha256": "2b8cbc46517c1e6b073c7b93a9fe4c1b50e66e1ee7be514371bafd2b050e0127",
            "tree_hash_algorithm": (
                "for each sorted leaf hash dtype text + compact JSON shape + "
                "contiguous raw bytes; canonical-JSON hash the leaf manifest"
            ),
            "action_head_exact_zero": True,
            "value_head_exact_zero": True,
            "log_std_initialization": (
                "elementwise log(0.25 * frozen inward action-delta vector)"
            ),
        },
        "implementation_contract_environment": {
            "platform": "CPU only",
            "python": "3.12.13",
            "jax": "0.7.2",
            "jaxlib": "0.7.2",
            "mujoco": "3.9.0",
            "numpy": "2.0.2",
            "onnx": "1.22.0",
            "onnxruntime": "1.27.0",
        },
        "seed_derivation": (
            "numpy SeedSequence([120120, stage, update_index, environment_index]); "
            "environment order is configuration-major then P30/P31-34"
        ),
        "stage1": {
            "purpose": "learn deployable-observation response state by full 250-tick BPTT",
            "update_count": 100,
            "scheduled_tick_slot_capacity": 2_000_000,
            "learning_rate": 1.0e-4,
            "optimizer": {
                "name": "Adam",
                "beta1": 0.9,
                "beta2": 0.999,
                "epsilon": 1.0e-8,
            },
            "normalization": (
                "float64 empirical mean/std from valid auxiliary targets in update 0 "
                "only; std=max(std,1e-6); cast once to float32 and freeze"
            ),
            "rollout": (
                "fresh seed-locked ternary exploration at every update through the "
                "exact graph absolute/inward rate boundary"
            ),
            "updates": "one full-batch gradient and one Adam step per fresh rollout",
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
            "optimizer_initialization": (
                "fresh Adam count 0 with exact-zero m/v for only the seven "
                "encoder/auxiliary trainable leaves"
            ),
            "required_at_every_update": [
                "finite loss, gradients, parameters, Adam moments, and normalization",
                "nonzero valid transition count",
                "no heldout configuration",
                "exact 40x2 population and fixed-P30 observation slot",
            ],
        },
        "stage2": {
            "purpose": "learn a bounded automatic support action with the Stage-1 encoder frozen",
            "update_count": 100,
            "scheduled_tick_slot_capacity": 2_000_000,
            "learning_rate": 1.0e-4,
            "optimizer": {
                "name": "Adam",
                "beta1": 0.9,
                "beta2": 0.999,
                "epsilon": 1.0e-8,
            },
            "ppo": {
                "gamma": 1.0,
                "gae_lambda": 0.95,
                "clip_epsilon": 0.2,
                "value_coefficient": 0.5,
                "entropy_coefficient": 0.001,
                "fresh_rollouts_per_update": 1,
                "epochs_per_rollout": 1,
                "minibatches": 1,
                "training_reward_selection_weight": "NONE",
            },
            "trainable_leaves": [
                "action_weight",
                "action_bias",
                "training_only_log_std",
                "training_only_value_weight",
                "training_only_value_bias",
            ],
            "frozen_leaves": "all Stage-1 encoder and auxiliary leaves",
            "stage1_to_stage2_handoff": (
                "start from the exact final Stage-1 encoder/auxiliary leaves; retain "
                "the seed-60720 exact-zero action head, exact initial training-only "
                "log_std, and exact-zero value head; do not carry Stage-1 Adam state"
            ),
            "optimizer_initialization": (
                "fresh Adam count 0 with exact-zero m/v for only the two deployable "
                "action leaves and three training-only Stage-2 leaves"
            ),
            "log_std_clamp": [-5.0, 1.0],
            "reward": (
                "1 per valid support tick, zero after termination, plus 250 only for "
                "all 250 valid ticks with final-50-tick unbiased gyro-XY norm <=0.05 rad/s"
            ),
            "required_at_every_update": [
                "finite loss, metrics, gradients, parameters, and Adam moments",
                "nonzero valid transition count and exact terminal masking",
                "all Stage-1 leaves bit-exact",
                "graph-owned bounds and log-std clamp respected",
            ],
        },
        "persistent_checkpoints": [
            {
                "label": "half",
                "stage2_update": 50,
                "stage2_scheduled_tick_slots": 1_000_000,
            },
            {
                "label": "final",
                "stage2_update": 100,
                "stage2_scheduled_tick_slots": 2_000_000,
            },
        ],
        "artifact_contract": {
            "stage1_final_checkpoint": True,
            "stage2_checkpoint_and_calibrator_onnx_at_each_persistent_checkpoint": True,
            "atomic_recovery_snapshot_every_updates": 1,
            "snapshot_contains": [
                "parameters",
                "active optimizer state and exact count",
                "frozen normalization",
                "stage/update/scheduled-slot counters",
                "source and contract hashes",
                "metric history",
                "cumulative actual sampled and valid-transition counts",
            ],
            "resume_rule": (
                "Only continue the same logical run from the newest hash-verified "
                "atomic per-update snapshot after process loss; an update is complete "
                "only after its snapshot rename commits, so no completed update may be "
                "replayed and no seed may change"
            ),
            "result_must_hash_every_checkpoint_graph_and_snapshot": True,
        },
        "future_frozen_support_gate": {
            "executed_by_this_preregistration": False,
            "checkpoint_labels": ["half", "final"],
            "cells_per_checkpoint": 124,
            "cell_derivation": (
                "56 model configurations x 2 actuator plants + 6 nominal-model "
                "sensor/transport conditions x 2 actuator plants"
            ),
            "duration_ticks": 250,
            "sensor_transport_population": sensor_conditions,
            "sensor_transport_population_sha256": canonical_sha256(sensor_conditions),
            "sensor_noise_seed_derivation": (
                "numpy SeedSequence([120120, 3, checkpoint_index, "
                "condition_index, plant_index]); checkpoint order half/final and "
                "plant order P30/P31-34"
            ),
            "heldout_context_gate": {
                "cells": (
                    "the existing 16 heldout configurations x 2 hidden plants within "
                    "the 112 model/plant cells; no additional behavior cells"
                ),
                "actions": "the checkpoint's bounded deployable calibrator actions",
                "normalization": "the frozen Stage-1 training normalization only",
                "prediction_metric": (
                    "mean squared normalized next-response error over all 250 valid "
                    "transitions using the frozen Stage-1 auxiliary predictor"
                ),
                "constant_baseline": (
                    "predict the frozen Stage-1 training target mean, equivalently "
                    "zero in normalized target space, on the identical heldout rows"
                ),
                "required_prediction_rule": (
                    "learned aggregate mean MSE must be strictly below the constant "
                    "baseline separately for P30 and P31/34 at each checkpoint"
                ),
                "matched_plant_context_rule": (
                    "for every heldout configuration, start P30 and P31/34 from the "
                    "same deterministic reset, initial observation, previous action, "
                    "and h_in with no stochastic sensor perturbation; the deployable "
                    "calibrator remains authoritative in each closed loop, and final "
                    "h_out L-infinity separation must exceed 1e-7"
                ),
                "repeat_rule": (
                    "repeat every heldout context cell from reset and require all "
                    "actions, observations, predictions, and h_out values bit-exact"
                ),
                "stochastic_inputs": False,
                "true_configuration_or_plant_label_enters_network": False,
            },
            "all_cells_at_both_checkpoints_must_pass": True,
            "selection_by_closest_result": False,
            "gates": {
                "duration_valid_ticks": 250,
                "two_foot_contact_failure_ticks": 0,
                "minimum_base_z_m": 0.1,
                "maximum_abs_roll_pitch_rad": 0.35,
                "maximum_final_50_tick_gyro_xy_norm_rad_s": 0.05,
                "per_joint_peak_torque_nm_max": 1.91229675,
                "per_joint_peak_current_a_max": 2.5,
                "strict_overcurrent_threshold_a": 2.0,
                "strict_overcurrent_max_consecutive_ticks": 99,
                "rated_current_p95_a": "0.65 diagnostic only; not candidate pass/fail",
            },
            "pass_authorizes_only": (
                "a separate response-conditioned locomotion-training preregistration; "
                "the calibrator checkpoint alone is not a deployable walking policy"
            ),
        },
        "stop_rules": [
            "stop before training if the fresh implementation/CPU contract does not pass",
            "stop on source, contract, population, seed, environment, checkpoint, or graph hash drift",
            "stop on nonfinite loss, metric, gradient, parameter, optimizer moment, state, action, observation, or sensor value",
            "stop on zero valid transitions, malformed terminal masking, stale data, failed action commit, or support ambiguity",
            "stop if Stage-1 frozen action leaves or Stage-2 frozen encoder/auxiliary leaves change",
            "stop if any heldout row enters normalization or optimization",
            "stop if graph-owned absolute/inward rate bounds, current/torque safety, or ONNX ABI checks fail",
            "do not retry, tune, extend, choose a closest checkpoint, add attention, or begin locomotion training from a failed result",
        ],
        "authority": {
            "implement_full_training_runner": True,
            "run_fresh_cpu_implementation_contract": True,
            "optimizer_updates_now": 0,
            "full_calibrator_training_now": False,
            "formal_support_cells_now": 0,
            "locomotion_training_or_behavior_cells": False,
            "colab_or_other_hosted_compute_now": False,
            "local_gpu_or_igpu": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "gate5_deployment_or_robot_clearance": False,
        },
        "pass_authorizes_only": (
            "one separately frozen full-training implementation/CPU contract; "
            "this preregistration does not itself authorize optimizer execution"
        ),
        "checks": checks,
        "sources": source_manifest(),
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# Winner-v12 full calibrator-training preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Training authorized now: `false`",
                "- Stage 1 / Stage 2 scheduled tick capacity: `2,000,000 / 2,000,000`",
                "- Training population: `40 configurations x 2 hidden plants`",
                "- Persistent checkpoints: `Stage-2 updates 50 / 100`",
                "- Future support gate: `124 cells per checkpoint; both must pass`",
                "- Robot clearance: `false`",
                "",
                "This freezes the full automatic-calibrator design before implementation.",
                "It deliberately does not train or enable the locomotion adapter. A",
                "calibrator pass can authorize only a separate response-conditioned",
                "locomotion-training preregistration.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "output": str(OUTPUT),
                "output_sha256": sha256(OUTPUT),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
