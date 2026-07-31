#!/usr/bin/env python3
"""Preregister the single Winner-v102 response-conditioned GPU curriculum."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CPU_PREREGISTRATION = (
    ANALYSIS / "winner_v101_response_conditioned_cpu_retry_preregistration.json"
)
CPU_RESULT = ANALYSIS / "winner_v101_response_conditioned_cpu_contract.json"
DRIVER = ROOT / "tools/colab_winner_v102_response_conditioned_curriculum.py"
SOURCE_ARCHIVE = ANALYSIS / "GROUND_UP_TRACKING_TAIL_artifacts.tar.gz"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
PROTECTED_POLICY = (
    ROOT
    / "artifacts/runtime_handoff/rdkx5_native_20260719/policies/"
    "T2_EQUAL_512000.onnx"
)
V96_NETWORK = ROOT / "patches/winner_v96_response_conditioned_networks.py"
OUTPUT = (
    ANALYSIS
    / "winner_v102_response_conditioned_hosted_curriculum_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V102_RESPONSE_CONDITIONED_HOSTED_CURRICULUM_PREREGISTRATION_20260722.md"
)
CPU_PREREGISTRATION_SHA256 = (
    "f4a92918b148c4ee1d5ae50b66086084cffff91925de27f7c16007af845d437e"
)
CPU_RESULT_SHA256 = (
    "4f44c2ff9de0ee715b09c1c95048bedb0a43f3334eaa70970dac8c08d6e047d0"
)
SOURCE_CHECKPOINT_DIRECTORY_SHA256 = (
    "311ce59807ad872795dd95e4a30c626f11d3d80f1b3f78c5b2b997639da4d67e"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--calibrator", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v102 prereg: {path}")
    playground = args.playground_root.resolve()
    calibrator = args.calibrator.resolve()
    cpu_prereg = json.loads(CPU_PREREGISTRATION.read_text(encoding="utf-8"))
    cpu_result = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(CPU_PREREGISTRATION) != CPU_PREREGISTRATION_SHA256
        or sha256(CPU_RESULT) != CPU_RESULT_SHA256
        or cpu_prereg.get("status")
        != "PREREGISTERED_WINNER_V101_RESPONSE_CONDITIONED_CPU_RETRY"
        or cpu_result.get("status")
        != "PASS_WINNER_V101_RESPONSE_CONDITIONED_CPU_CONTRACT"
        or cpu_result.get("failed_checks") != []
        or cpu_result.get("source_checkpoint_directory_sha256")
        != SOURCE_CHECKPOINT_DIRECTORY_SHA256
        or cpu_result.get("update_family_max_delta", {}).get("protected") != 0.0
        or not all(
            cpu_result.get("update_family_max_delta", {}).get(name, 0.0) > 0.0
            for name in ("adapter_state", "adapter_context", "adapter_action")
        )
        or cpu_result.get("authority", {}).get(
            "separate_hosted_curriculum_preregistration_after_pass"
        )
        is not True
        or cpu_result.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v102 CPU prerequisite changed")

    manifest_path = playground / "WINNER_V98_COMPOSED_SOURCE_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("schema_version") != "winner_v98.composed_playground_source.v1"
        or manifest.get("control_commit")
        != "b9be205ac64488c23504ca42e5ec790337adeec3"
        or manifest.get("stop_before_winner_v98") is not False
    ):
        raise ValueError("Winner-v102 composed source identity changed")
    expected_composed = cpu_prereg["composed_playground_files"]
    observed_composed = {
        relative: sha256(playground / relative) for relative in expected_composed
    }
    if observed_composed != expected_composed:
        raise ValueError("Winner-v102 composed source changed after CPU pass")

    driver_text = DRIVER.read_text(encoding="utf-8")
    required_driver_tokens = (
        '"steps": 245_760',
        '"steps": 2_007_040',
        '"expected_steps": [0, 1_003_520, 2_007_040]',
        '"deviation_scale": 0.25',
        '"deviation_scale": 0.5',
        '"deviation_scale": 1.0',
        '"--ppo_num_envs",\n        "256"',
        '"--winner_v98_calibration_ticks",\n        "250"',
        '"--winner_v98_home_return_ticks",\n        "250"',
        'if not args.hosted_gpu_authorized:',
        'single-run no-retry work root exists',
        'all(device.platform == "gpu"',
        '"formal_behavior_cells_executed": 0',
        '"robot_clearance": False',
    )
    if not all(token in driver_text for token in required_driver_tokens):
        raise ValueError("Winner-v102 driver invariant is absent")
    if any(
        token in driver_text
        for token in (
            "--hardware-authorized",
            "--suspended-or-benched",
            "/dev/tty",
            "serial.Serial",
            "GPIO",
        )
    ):
        raise ValueError("Winner-v102 driver contains a hardware surface")

    external = cpu_prereg["external_binaries"]
    repository = cpu_prereg["repository_binaries"]
    input_hashes = {
        "driver": sha256(DRIVER),
        "v96_network": sha256(V96_NETWORK),
        "cpu_contract": sha256(CPU_RESULT),
        "composed_manifest": sha256(manifest_path),
        "source_archive": sha256(SOURCE_ARCHIVE),
        "reference_features": sha256(REFERENCE),
        "protected_policy": sha256(PROTECTED_POLICY),
        "calibrator": sha256(calibrator),
    }
    if (
        input_hashes["source_archive"]
        != repository["archive"]["sha256"]
        or input_hashes["reference_features"]
        != repository["reference"]["sha256"]
        or input_hashes["protected_policy"]
        != repository["policy"]["sha256"]
        or input_hashes["calibrator"]
        != external["calibrator_onnx"]["sha256"]
        or lf_sha256(V96_NETWORK)
        != cpu_prereg["sources"]["v96_network"]["sha256"]
    ):
        raise ValueError("Winner-v102 binary/source provenance changed")

    payload = {
        "schema_version": (
            "winner_v102.response_conditioned_hosted_curriculum_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V102_RESPONSE_CONDITIONED_HOSTED_CURRICULUM"
        ),
        "decision": "AUTHORIZE_ONE_HASH_FROZEN_GPU_CURRICULUM_WITHOUT_RETRY",
        "date": "2026-07-22",
        "rationale": (
            "Winner-v101 passed exact restore, automatic calibration, finite update, "
            "protected-actor isolation, stateful export, graph-boundary, and x=0 checks."
        ),
        "cpu_prerequisite": {
            "preregistration_sha256": CPU_PREREGISTRATION_SHA256,
            "result_sha256": CPU_RESULT_SHA256,
            "status": cpu_result["status"],
            "protected_parameter_update_max": 0.0,
            "adapter_update_families": cpu_result["update_family_max_delta"],
        },
        "input_hashes": input_hashes,
        "source_checkpoint_directory_sha256": (
            SOURCE_CHECKPOINT_DIRECTORY_SHA256
        ),
        "composed_playground_files": observed_composed,
        "software_versions": cpu_prereg["software_versions"],
        "training": {
            "seed": 100,
            "architecture": "response_conditioned_reference_residual",
            "flat_transport": False,
            "automatic_calibration_ticks_per_reset": 250,
            "automatic_home_return_ticks_per_reset": 250,
            "calibration_context_dimensions": 64,
            "recurrent_hidden_dimensions": 64,
            "num_envs": 256,
            "episode_length": 600,
            "unroll_length": 20,
            "batch_size": 256,
            "num_minibatches": 4,
            "num_updates_per_batch": 4,
            "learning_rate": 0.0003,
            "discounting": 0.97,
            "entropy_cost": 0.005,
            "stages": [
                {
                    "id": "DOMAIN_25_PERCENT",
                    "deviation_scale": 0.25,
                    "timesteps": 245_760,
                },
                {
                    "id": "DOMAIN_50_PERCENT",
                    "deviation_scale": 0.5,
                    "timesteps": 245_760,
                },
                {
                    "id": "DOMAIN_100_PERCENT",
                    "deviation_scale": 1.0,
                    "timesteps": 2_007_040,
                    "exports": [1_003_520, 2_007_040],
                },
            ],
            "wall_ceiling_seconds": 21_600,
            "retry": False,
            "resume": False,
            "reward_curve_selection": False,
        },
        "contract": {
            "protected_source_actor_and_normalizer_remain_bit_exact": True,
            "only_response_adapter_and_critic_may_update": True,
            "stateful_onnx_abi": {
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
            "x0_deadband_exact": True,
            "graph_authoritative_rate_guard_deadband": True,
            "powered_off_manual_com_packet_required": False,
            "build_specific_response_is_automatically_inferred": True,
            "formal_behavior_cells_during_training": 0,
        },
        "pass_rule": [
            "all input, composed-source, software, and package hashes match",
            "exactly one GPU process runs the frozen three-stage curriculum without retry or resume",
            "all seven scheduled checkpoints and ONNX graphs exist and are finite",
            "the protected actor and protected normalizer have exactly zero update",
            "state, context, and action adapter families each update",
            "stage restore continuity is exact",
            "every ONNX graph has the frozen four-input/three-output ABI and exact x=0 deadband",
            "the run completes within 21,600 seconds",
        ],
        "execution_now": {
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_hosted_gpu_curriculum_after_package_contract": True,
            "additional_training_or_retry": False,
            "behavior_evaluation_after_valid_artifact": False,
            "checkpoint_selection": False,
            "deployment": False,
            "gate5": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "# Winner-v102 response-conditioned hosted-curriculum preregistration\n\n"
        "Winner-v101 passed its CPU mechanics contract. This freezes one GPU-only, "
        "no-retry 25% → 50% → 100% variable-configuration curriculum. The protected "
        "actor remains frozen; only the response adapter and critic may update. Build "
        "response is inferred automatically during reset, so no manual COM worksheet "
        "is required. This run creates training artifacts only: it does not evaluate "
        "behavior, select a deployment checkpoint, access the robot, or grant robot "
        "clearance.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
