#!/usr/bin/env python3
"""Preregister one Winner-v114 linear-torque hosted continuation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CPU_RESULT = ANALYSIS / "winner_v114_linear_torque_cpu_result.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
DRIVER = ROOT / "tools/colab_winner_v114_linear_torque_continuation.py"
OUTPUT = (
    ANALYSIS / "winner_v114_linear_torque_hosted_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V114_LINEAR_TORQUE_HOSTED_PREREGISTRATION_20260724.md"
)
CPU_RESULT_SHA256 = (
    "f211c6cb344e5548c15de9d3213217a69e1c3891afce9e63e30e07d2a177c104"
)
DRIVER_SHA256 = (
    "ebca591a31b0b1894ca115649eb7eee0afa24c7cbfe0f790013cec7ae666f3aa"
)
COMPOSED_MANIFEST_SHA256 = (
    "d0bcf899e9be15b1ddd678ccb35036f6d750eae6aa65e9686fba2a1cf81a5a41"
)
SOURCE_CHECKPOINT_SHA256 = (
    "d63309e0e0524d684813d1bf068e8642b21d2e829653d7716949614350f0423c"
)
REFERENCE_SHA256 = (
    "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v114: {path}")
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    manifest = playground / "WINNER_V114_COMPOSED_SOURCE_MANIFEST.json"
    cpu_result = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "driver": sha256(DRIVER),
        "cpu_result": sha256(CPU_RESULT),
        "composed_manifest": sha256(manifest),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(REFERENCE),
    }
    expected_hashes = {
        "driver": DRIVER_SHA256,
        "cpu_result": CPU_RESULT_SHA256,
        "composed_manifest": COMPOSED_MANIFEST_SHA256,
        "source_checkpoint": SOURCE_CHECKPOINT_SHA256,
        "reference_features": REFERENCE_SHA256,
    }
    checks = {
        "cpu_result_exact": (
            input_hashes["cpu_result"] == CPU_RESULT_SHA256
            and cpu_result.get("status")
            == "PASS_WINNER_V114_LINEAR_TORQUE_CPU_SMOKE"
            and cpu_result.get("failed_checks") == []
            and cpu_result.get("authority", {}).get(
                "hosted_preregistration_authorized"
            )
            is True
        ),
        "driver_exact": input_hashes["driver"] == DRIVER_SHA256,
        "composed_manifest_exact": (
            input_hashes["composed_manifest"] == COMPOSED_MANIFEST_SHA256
        ),
        "source_checkpoint_exact": (
            input_hashes["source_checkpoint"] == SOURCE_CHECKPOINT_SHA256
        ),
        "reference_features_exact": (
            input_hashes["reference_features"] == REFERENCE_SHA256
        ),
        "single_continuation_only": True,
        "no_scalar_search": True,
        "robot_surface_absent": True,
    }
    if input_hashes != expected_hashes:
        raise ValueError(f"Winner-v114 input identity changed: {input_hashes}")
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v114.linear_torque_hosted_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V114_LINEAR_TORQUE_HOSTED_CONTINUATION"
            if not failed
            else "HOLD_WINNER_V114_LINEAR_TORQUE_HOSTED_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "date": "2026-07-24",
        "decision": (
            "AUTHORIZE_ONE_HASH_FROZEN_GPU_CONTINUATION_WITHOUT_RETRY"
        ),
        "evidence_basis": {
            "v113_nominal_passes": 5,
            "v113_nominal_cells": 16,
            "behavior_failure_count": 0,
            "current_peak_failure_count": 9,
            "torque_peak_failure_count": 11,
            "torque_failures_sparse_single_joint": True,
            "max_squared_closed_as_scalar_rewrite": True,
            "selected_mechanism": (
                "mean_all_joint_linear_torque_hinge"
            ),
            "scale_derivation": (
                "matches the frozen prior squared penalty at the V110 "
                "worst-tick evidence point; not selected by a sweep"
            ),
        },
        "input_hashes": input_hashes,
        "training": {
            "source": "exact_v112_final_checkpoint",
            "seed": 100,
            "architecture": "reference_residual_recurrent_adapter",
            "recurrent_hidden_size": 64,
            "full_variable_configuration": True,
            "deviation_scale": 1.0,
            "timesteps": 2_007_040,
            "exports": [0, 1_003_520, 2_007_040],
            "num_envs": 256,
            "episode_length": 600,
            "unroll_length": 20,
            "batch_size": 256,
            "num_minibatches": 4,
            "num_updates_per_batch": 4,
            "learning_rate": 0.0003,
            "discounting": 0.97,
            "entropy_cost": 0.005,
            "linear_peak_torque_threshold_nm": 1.91229675,
            "linear_peak_torque_scale": -307.48131091308585,
            "squared_peak_torque_scale": 0.0,
            "tracking_tail_threshold_rad": 0.20,
            "tracking_tail_scale": -6572.254964031055,
            "wall_ceiling_seconds": 21_600,
            "retry": False,
            "resume": False,
            "reward_curve_selection": False,
            "scalar_sweep": False,
        },
        "post_training": {
            "behavior_cells_during_training": 0,
            "cpu_topology_validation_before_behavior": True,
            "apply_exact_frozen_g3_guard_and_deadband_to": [
                1_003_520,
                2_007_040,
            ],
            "evaluate_nominal_16_cells_first": True,
            "evaluate_full_frozen_matrix_only_after_nominal_pass": True,
            "both_postupdate_checkpoints_must_pass": True,
            "checkpoint_cherry_pick": False,
        },
        "software_versions": {
            "brax": "0.14.2",
            "flax": "0.11.2",
            "jax": "0.7.2",
            "jaxlib": "0.7.2",
            "mujoco": "3.9.0",
            "mujoco-mjx": "3.9.0",
            "numpy": "2.0.2",
            "onnx": "1.22.0",
            "onnxruntime": "1.27.0",
            "optax": "0.2.5",
            "orbax-checkpoint": "0.11.25",
            "playground": "0.0.3",
        },
        "execution_now": {
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_hosted_gpu_continuation_after_package_contract": not failed,
            "additional_training_or_retry": False,
            "behavior_evaluation_after_valid_artifact": False,
            "checkpoint_selection": False,
            "gate5": False,
            "deployment": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v114 linear-torque hosted preregistration\n\n"
        f"Status: `{payload['status']}`\n\n"
        "One no-retry GPU continuation is frozen from the exact V112 final "
        "checkpoint. It replaces the squared torque objective with the "
        "CPU-proven all-joint linear hinge selected by V113 failure "
        "attribution. The scale is analytically derived, not swept. No "
        "behavior gate runs during training. Both post-update checkpoints "
        "must pass the same frozen nominal gate before robustness evaluation."
        " This grants no Gate 5, deployment, robot, torque, or motion "
        "authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
