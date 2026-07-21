#!/usr/bin/env python3
"""Freeze the prospective Winner-v12 124-cell support/context gate."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
FULL_PREREGISTRATION = (
    ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
)
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
RUNNER = ROOT / "tools/run_winner_v12_calibrator_support_gate.py"
TEST = ROOT / "tests/test_winner_v12_calibrator_support_gate.py"
OUTPUT = ANALYSIS / "winner_v12_calibrator_support_gate_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V12_CALIBRATOR_SUPPORT_GATE_PREREGISTRATION_20260721.md"
SOURCE_PATHS = {
    "builder": (Path(__file__), "lf"),
    "full_training_preregistration": (FULL_PREREGISTRATION, "lf"),
    "variable_configuration_domain": (DOMAIN, "lf"),
    "gate_runner": (RUNNER, "lf"),
    "gate_tests": (TEST, "lf"),
    "cpu_smoke": (ROOT / "tools/run_winner_v12_calibrator_cpu_smoke.py", "lf"),
    "full_training_runner": (
        ROOT / "tools/run_winner_v12_full_calibrator_training.py",
        "lf",
    ),
    "training_primitives": (ROOT / "patches/winner_v12_calibrator_training.py", "lf"),
    "deployable_network": (
        ROOT / "patches/winner_v12_decomposed_backend_networks.py",
        "lf",
    ),
    "actuator_bridge": (ROOT / "tools/actuator_bridge_model.py", "lf"),
    "runtime_observer": (
        ROOT
        / "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py",
        "lf",
    ),
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
    return {
        name: {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "hash_mode": mode,
            "sha256": lf_sha256(path) if mode == "lf" else sha256(path),
        }
        for name, (path, mode) in SOURCE_PATHS.items()
    }


def main() -> int:
    full = json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    frozen = full["future_frozen_support_gate"]
    matrix = domain["evaluation_matrix"]
    configurations = (
        matrix["fixed_anchors"]
        + matrix["discovery_samples"]
        + matrix["heldout_samples"]
    )
    conditions = frozen["sensor_transport_population"]
    runner = RUNNER.read_text(encoding="utf-8")
    tests = TEST.read_text(encoding="utf-8")
    checks = {
        "upstream_gate_exact": frozen["checkpoint_labels"] == ["half", "final"]
        and frozen["cells_per_checkpoint"] == 124
        and frozen["duration_ticks"] == 250
        and frozen["all_cells_at_both_checkpoints_must_pass"] is True,
        "model_population_exact": len(matrix["fixed_anchors"]) == 24
        and len(matrix["discovery_samples"]) == 16
        and len(matrix["heldout_samples"]) == 16
        and len(configurations) == 56,
        "transport_population_exact": len(conditions) == 6
        and [row["id"] for row in conditions]
        == [
            "NATIVE_INPUT_QUANTIZATION",
            "DECLARED_SENSOR_NOISE",
            "ACTION_DELAY_1",
            "ACTION_DELAY_2",
            "IMU_DELAY_1",
            "IMU_DELAY_2",
        ]
        and canonical_sha256(conditions)
        == frozen["sensor_transport_population_sha256"],
        "runner_requires_explicit_offline_authority": "--offline-cpu-only" in runner
        and "--formal-gate-authorized" in runner,
        "runner_uses_graph_authoritative_outputs": "session.run(" in runner
        and '"calibration_actions"' in runner
        and '"previous_action_out"' in runner
        and '"h_out"' in runner,
        "runner_has_exact_model_and_transport_counts": '"exact_124_main_cells"'
        in runner
        and '"formal_support_cells": 248' in runner
        and '"heldout_repeat_cells": 64' in runner,
        "runner_has_context_and_prediction_gate": "final_h_out_linf_separation"
        in runner
        and "learned_normalized_prediction_mse" in runner
        and "constant_normalized_prediction_mse" in runner,
        "runner_has_no_robot_or_locomotion_authority": '"locomotion_training_steps": 0'
        in runner
        and '"robot_or_rdk_access": 0' in runner
        and '"robot_clearance": False' in runner,
        "boundary_tests_present": all(
            token in tests
            for token in (
                "test_delayed_action_queue_is_exact",
                "test_imu_delay_observation_transport_is_exact",
                "test_native_quantization_changes_only_sensor_joint_slots",
                "test_support_pass_requires_every_frozen_boundary",
            )
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise SystemExit(f"support-gate preregistration failed: {failed}")
    sources = source_manifest()
    payload = {
        "schema_version": "winner_v12.calibrator_support_gate_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V12_CALIBRATOR_SUPPORT_GATE",
        "decision": "AUTHORIZE_SUPPORT_GATE_CPU_CONTRACT_ONLY",
        "selection": {
            "checkpoint_labels": ["half", "final"],
            "all_cells_at_both_checkpoints_must_pass": True,
            "selection_by_closest_result": False,
            "selection_by_training_reward": False,
        },
        "main_matrix": {
            "per_checkpoint": {
                "model_plant_cells": 112,
                "sensor_transport_plant_cells": 12,
                "total": 124,
            },
            "both_checkpoints_total": 248,
            "model_configuration_ids": [row["id"] for row in configurations],
            "plants": [
                "P30_ALL_JOINT",
                "P31_34_PITCH_WITH_P30_NONPITCH",
            ],
            "sensor_transport_conditions": conditions,
            "nominal_sensor_transport_model": (
                "load the exact composed scene and apply identity mass scale, zero torso "
                "mass/COM change, and the scene's exact nominal torso principal inertia"
            ),
        },
        "transport_semantics": {
            "native_quantization": {
                "gyro_lsb_rad_s": math.pi / (180.0 * 16.0),
                "accelerometer_lsb_m_s2": 0.01,
                "position_lsb_rad": 2.0 * math.pi / 4096.0,
                "velocity_observation_lsb": (2.0 * math.pi / 4095.0) * 0.05,
                "unchanged_slots": "obs[6:13] and obs[41:115]",
            },
            "declared_sensor_noise": {
                "distribution": "independent NumPy PCG64 uniform[-scale,+scale]",
                "gyro": "obs[0:3], rad/s scale",
                "accelerometer": "obs[3:6], native scale",
                "joint_position": "obs[13:27], hip/knee/ankle category scale; head zero",
                "joint_velocity": "obs[27:41], rad/s scale multiplied by frozen 0.05 observation scale",
                "gravity_and_linvel": "declared domain fields have no deployable slot in the frozen calibrator 115-D observation and therefore do not alter another slot",
            },
            "imu_delay": "delay the complete obs[0:6] gyro/accelerometer pair by exactly 1 or 2 ticks; prehistory is zero",
            "action_delay": "delay only the action sent to the physical bridge by exactly 1 or 2 ticks; policy previous_action/history remains the graph-authoritative requested action; prehistory is zero",
            "seed_derivation": frozen["sensor_noise_seed_derivation"],
        },
        "support_thresholds": frozen["gates"],
        "heldout_context_gate": {
            **frozen["heldout_context_gate"],
            "repeat_cells_per_checkpoint": 32,
            "repeat_cells_both_checkpoints": 64,
            "repeat_outputs": [
                "observations",
                "actions",
                "auxiliary_predictions",
                "h_out",
            ],
        },
        "graph_and_state_contract": {
            "action_source": "stateful checkpoint ONNX calibration_actions only",
            "previous_action_chain": "previous_action_out must equal calibration_actions bit-exact every tick",
            "hidden_crosscheck": "training response_step h_out versus ONNX h_out max absolute error <= 1e-7 every tick",
            "auxiliary_target_indices": "next valid observation [0:6], [13:41], and [83:99]",
            "normalization": "the checkpoint's immutable Stage-1 target_mean/target_std only",
        },
        "prerequisites_before_launch": [
            "successful corrected full-training workflow result",
            "safe ZIP extraction and independent artifact/snapshot/ONNX verification",
            "exact half/final checkpoint and ONNX hashes frozen into a launch contract",
            "one zero-cell CPU contract of this gate implementation in the pinned CPU environment",
        ],
        "execution_now": {
            "formal_support_cells": 0,
            "heldout_repeat_cells": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a zero-cell CPU contract; it does not authorize the 248-cell gate until its training artifact and exact hashes are independently verified",
        },
        "checks": checks,
        "failed_checks": [],
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# Winner-v12 calibrator support-gate preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Main cells: `124 per checkpoint × 2 = 248`",
                "- Heldout deterministic repeat cells: `32 per checkpoint × 2 = 64`",
                "- Duration: `250 ticks per cell`",
                "- Training/robot execution now: `0 / 0`",
                "",
                "Both half and final must pass every support cell, every heldout repeat,",
                "the per-plant learned-vs-constant prediction test, and all 16 hidden-plant",
                "context separations. There is no closest-result selection.",
                "",
                "This freezes the evaluator before training results are inspected. It",
                "authorizes only a zero-cell CPU contract. The formal gate remains blocked",
                "until the complete training artifact and checkpoint hashes pass independent",
                "verification.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "sha256": lf_sha256(OUTPUT)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
