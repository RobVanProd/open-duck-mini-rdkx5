#!/usr/bin/env python3
"""Freeze the post-V102 CPU behavior and checkpoint-selection gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
BASE_PREREGISTRATION = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
BASE_RUNNER_CONTRACT = (
    ANALYSIS / "winner_v3_variable_configuration_behavior_runner_contract.json"
)
V102_PREREGISTRATION = (
    ANALYSIS
    / "winner_v102_response_conditioned_hosted_curriculum_preregistration.json"
)
V102_PACKAGE_CONTRACT = (
    ANALYSIS / "winner_v102_response_conditioned_hosted_package_contract.json"
)
V102_LAUNCH_CONTRACT = ANALYSIS / "winner_v102_colab_launch_contract.json"
CALIBRATION_WRAPPER = ROOT / "patches/winner_v98_response_calibration_wrapper.py"
OUTPUT = (
    ANALYSIS
    / "winner_v103_response_conditioned_behavior_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V103_RESPONSE_CONDITIONED_BEHAVIOR_PREREGISTRATION_20260722.md"
)

BASE_PREREGISTRATION_SHA256 = (
    "c8f986ceb24863f33c1fc99170548d2e255cb6a26737d3f74762f8dcd4485a24"
)
BASE_RUNNER_CONTRACT_SHA256 = (
    "9519c0902a41a530092f39cf5fe645cee7ce638bfc60c6b79a1ad61a075337b4"
)
V102_PREREGISTRATION_SHA256 = (
    "819b89d80dcd03b30e88e3596e55c343c14c753575b1797996a9107867b388fe"
)
V102_PACKAGE_CONTRACT_SHA256 = (
    "d4218997ab5bc75745c32c3e4b29adda82e5e7846adce82db0e52016c3909ea0"
)
V102_LAUNCH_CONTRACT_SHA256 = (
    "a8000d448e17c95a06a9b6a5d2e5a9f806a2e68cce33aebcc54220eaf21e0a29"
)
CALIBRATION_WRAPPER_SHA256 = (
    "04339bf7bbe16f2721ce92bbe62c458e70c1c8a5e9bdfe02424478ebc066a7ba"
)
CALIBRATOR_ONNX_SHA256 = (
    "cb3380ed99b3e9d7e9000904a210227aa397db2a064aa80d8f70e77c8339783b"
)
MATRIX_PLAN_SHA256 = (
    "10b5d3e407636d276275f3f39145233c3cd63688c3229235411ed2734651e073"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_exact(path: Path, expected_sha256: str) -> dict[str, Any]:
    if sha256(path) != expected_sha256:
        raise ValueError(f"frozen input changed: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload() -> dict[str, Any]:
    base = load_exact(BASE_PREREGISTRATION, BASE_PREREGISTRATION_SHA256)
    runner = load_exact(BASE_RUNNER_CONTRACT, BASE_RUNNER_CONTRACT_SHA256)
    v102 = load_exact(V102_PREREGISTRATION, V102_PREREGISTRATION_SHA256)
    package = load_exact(V102_PACKAGE_CONTRACT, V102_PACKAGE_CONTRACT_SHA256)
    launch = load_exact(V102_LAUNCH_CONTRACT, V102_LAUNCH_CONTRACT_SHA256)
    if sha256(CALIBRATION_WRAPPER) != CALIBRATION_WRAPPER_SHA256:
        raise ValueError("response-calibration wrapper changed")
    if (
        base.get("status") != "PREREGISTERED_CPU_CONTRACT_FIRST"
        or runner.get("status")
        != "PASS_WINNER_V3_VARIABLE_CONFIGURATION_BEHAVIOR_RUNNER_CONTRACT"
        or runner.get("matrix_plan_sha256") != MATRIX_PLAN_SHA256
        or runner.get("matrix_cells") != 1024
        or runner.get("condition_count") != 64
        or v102.get("status")
        != "PREREGISTERED_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_CURRICULUM"
        or package.get("status")
        != "PASS_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_PACKAGE"
        or launch.get("status") != "PASS_WINNER_V102_COLAB_LAUNCH_CONTRACT"
        or v102.get("training", {}).get("flat_transport") is not False
        or v102.get("contract", {}).get("powered_off_manual_com_packet_required")
        is not False
    ):
        raise ValueError("Winner-v103 prerequisite contract changed")

    matrix = base["evaluation_matrix"]
    per_cell = base["per_cell_contract"]
    if (
        matrix.get("checkpoints_full_domain_relative_steps")
        != [1_003_520, 2_007_040]
        or matrix.get("commands_x_m_s") != [0.0, 0.074, 0.077, 0.08]
        or matrix.get("actuator_plants")
        != ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"]
        or matrix.get("cell_count_derivation", {}).get("total") != 1024
        or per_cell.get("all_joint_tracking_p95_rad_max") != 0.2
        or per_cell.get("all_joint_current_p95_a_max") != 0.65
    ):
        raise ValueError("Winner-v103 inherited behavior matrix changed")

    return {
        "schema_version": (
            "winner_v103.response_conditioned_behavior_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V103_RESPONSE_CONDITIONED_CPU_BEHAVIOR_"
            "AND_SELECTION_GATE"
        ),
        "decision": "FREEZE_UNCHANGED_1024_CELL_MATRIX_BEFORE_V102_OUTCOME",
        "date": "2026-07-22",
        "causal_question": (
            "Does the response-conditioned policy preserve the complete inherited "
            "variable-configuration, measured-actuator, sensor, transport, command, "
            "and persistence envelope after automatically inferring each simulated "
            "build response?"
        ),
        "prerequisites": {
            "v102_training_artifact": (
                "must independently pass the frozen V102 artifact contract before "
                "any formal behavior cell executes"
            ),
            "v102_training_artifact_exists_now": False,
            "runner_contract": (
                "a separately hash-frozen V103 CPU runner contract must pass with "
                "zero formal behavior cells before execution"
            ),
            "runner_contract_exists_now": False,
        },
        "frozen_sources": {
            "builder": {
                "path": str(Path(__file__).resolve().relative_to(ROOT)),
                "sha256": sha256(Path(__file__).resolve()),
            },
            "base_behavior_preregistration": {
                "path": str(BASE_PREREGISTRATION.relative_to(ROOT)),
                "sha256": BASE_PREREGISTRATION_SHA256,
            },
            "base_behavior_runner_contract": {
                "path": str(BASE_RUNNER_CONTRACT.relative_to(ROOT)),
                "sha256": BASE_RUNNER_CONTRACT_SHA256,
                "matrix_plan_sha256": MATRIX_PLAN_SHA256,
            },
            "v102_training_preregistration": {
                "path": str(V102_PREREGISTRATION.relative_to(ROOT)),
                "sha256": V102_PREREGISTRATION_SHA256,
            },
            "v102_package_contract": {
                "path": str(V102_PACKAGE_CONTRACT.relative_to(ROOT)),
                "sha256": V102_PACKAGE_CONTRACT_SHA256,
            },
            "v102_launch_contract": {
                "path": str(V102_LAUNCH_CONTRACT.relative_to(ROOT)),
                "sha256": V102_LAUNCH_CONTRACT_SHA256,
            },
            "calibration_wrapper": {
                "path": str(CALIBRATION_WRAPPER.relative_to(ROOT)),
                "sha256": CALIBRATION_WRAPPER_SHA256,
            },
            "calibrator_onnx_sha256": CALIBRATOR_ONNX_SHA256,
        },
        "formal_matrix": {
            "population": "bit-exact inherited Winner-v3 1,024-cell matrix",
            "matrix_plan_sha256": MATRIX_PLAN_SHA256,
            "conditions": 64,
            "cells_total": 1024,
            "cells_per_checkpoint": 512,
            "checkpoints_full_domain_relative_steps": [1_003_520, 2_007_040],
            "actuator_plants": [
                "P30_ALL_JOINT",
                "P31_34_PITCH_WITH_P30_NONPITCH",
            ],
            "commands_x_m_s": [0.0, 0.074, 0.077, 0.08],
            "duration_valid_locomotion_ticks": 600,
            "control_hz": 50,
            "group_cell_counts": {
                "NOMINAL": 32,
                "FIXED_ANCHOR": 384,
                "DISCOVERY": 256,
                "HELDOUT": 256,
                "SENSOR_TRANSPORT": 96,
            },
            "all_numeric_configuration_samples_seeds_and_transport_values": (
                "inherited without modification from the exact base preregistration"
            ),
        },
        "automatic_calibration_per_cell": {
            "same_simulated_build_plant_and_transport_as_scored_episode": True,
            "calibration_ticks": 250,
            "home_return_ticks": 250,
            "ticks_count_toward_scored_duration": False,
            "calibration_command": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "calibration_phase": [1.0, 0.0],
            "calibration_projected_reference": [0.0] * 14,
            "initial_calibrator_hidden": [0.0] * 64,
            "initial_calibrator_previous_action": [0.0] * 14,
            "context": (
                "final 64-D calibrator h_out after tick 250, finite and immutable "
                "through the scored locomotion episode"
            ),
            "locomotion_phase_reset": [1.0, 0.0],
            "locomotion_hidden_reset": [0.0] * 64,
            "locomotion_previous_action_reset": [0.0] * 14,
            "failure_is_cell_failure": [
                "calibration terminates early",
                "home return terminates early",
                "context is nonfinite or wrong shape",
                "context changes during locomotion",
                "calibration or home-return tick count differs",
                "locomotion reset state, phase, hidden, or previous action differs",
            ],
        },
        "per_cell_contract": per_cell,
        "additional_response_contract": {
            "policy_abi": {
                "inputs": {
                    "obs": [1, 115],
                    "previous_action": [1, 14],
                    "h_in": [1, 64],
                    "calibration_context": [1, 64],
                },
                "outputs": {
                    "continuous_actions": [1, 14],
                    "previous_action_out": [1, 14],
                    "h_out": [1, 64],
                },
            },
            "protected_actor_and_normalizer_exact": True,
            "graph_authoritative_rate_guard_and_x0_deadband": True,
            "host_action_clipping_deadband_or_projection": False,
            "flat_transport": False,
            "training_or_simulator_reward_selection_weight": 0,
        },
        "selection_rule": {
            "both_checkpoints_must_pass_all_512_cells": True,
            "no_closest_checkpoint_or_metric_ranking": True,
            "no_selection_if_either_checkpoint_holds": True,
            "selected_checkpoint_if_both_pass": {
                "label": "final",
                "full_domain_relative_step": 2_007_040,
            },
            "selection_records_exact_locomotion_onnx_sha256": True,
            "selection_also_binds_exact_calibrator_onnx_sha256": (
                CALIBRATOR_ONNX_SHA256
            ),
        },
        "pass_rule": [
            "the V102 training artifact and the V103 zero-cell runner contract pass",
            "one CPU-only no-retry process completes all 1,024 formal cells",
            "all recorded models, plants, sensor and transport values read back exactly",
            "automatic calibration and home return pass exactly in every cell",
            "both persistent checkpoints pass every one of their 512 cells",
            "all traces, outputs, graph inputs, graph outputs, and contexts are finite",
            "the protected actor and normalizer remain exact and graph boundaries remain authoritative",
        ],
        "pass_authorizes_only": {
            "formal_checkpoint_selection": (
                "bind the final full-domain locomotion ONNX SHA-256 plus the exact "
                "calibrator SHA-256"
            ),
            "policy_clearance_artifact": (
                "write robot_clearance=true for the selected two-stage policy asset "
                "set and CPU/mock runtime freeze only"
            ),
            "gate5_preparation": True,
            "robot_access_or_motion_without_separate_gate_authorization": False,
            "grounded_walking": False,
        },
        "manual_measurement_disposition": {
            "powered_off_46_field_com_packet_required": False,
            "reason": (
                "the accepted route automatically infers a build-response context "
                "from measured motion; it does not use static build measurements"
            ),
        },
        "execution_now": {
            "training_artifacts_observed": 0,
            "formal_behavior_cells": 0,
            "checkpoint_selected": False,
            "robot_clearance": False,
            "robot_or_rdk_access": 0,
        },
        "authority_now": {
            "behavior_execution": False,
            "checkpoint_selection": False,
            "deployment": False,
            "gate5": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v103 prereg: {path}")
    payload = build_payload()
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "# Winner-v103 response-conditioned behavior preregistration\n\n"
        f"Status: `{payload['status']}`\n\n"
        "This freezes the unchanged 1,024-cell variable-configuration matrix "
        "before any Winner-v102 training outcome exists. Each cell first performs "
        "250 automatic-calibration ticks and 250 home-return ticks in the same "
        "simulated build and actuator plant, then scores exactly 600 locomotion "
        "ticks. Both half and final checkpoints must pass every cell; only then is "
        "the final checkpoint selected by its exact ONNX SHA-256. Training reward, "
        "a closest checkpoint, and post-outcome threshold changes have no selection "
        "weight.\n\n"
        "No behavior cell is authorized until the hosted artifact and a separately "
        "hash-frozen zero-cell runner contract pass. No robot, RDK-X5, Gate 5, "
        "torque, motion, or grounded walking is authorized by this preregistration.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
