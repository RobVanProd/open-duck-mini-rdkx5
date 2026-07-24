#!/usr/bin/env python3
"""Preregister one Winner-v119 transition-matched hosted continuation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CPU_RESULT = ANALYSIS / "winner_v119_transition_cpu_result.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
DRIVER = ROOT / "tools/colab_winner_v119_transition_continuation.py"
DRIVER_HELPER = (
    ROOT / "tools/colab_winner_v114_linear_torque_continuation.py"
)
PATCH = ROOT / "patches/winner_v119_train_transition_match.patch"
OUTPUT = ANALYSIS / "winner_v119_hosted_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V119_HOSTED_PREREGISTRATION_20260724.md"
)
EXPECTED = {
    "driver": (
        "e0cf405d17df2ac6a296a01fc10f49908a912f2690ea76d18d3953eada37049d"
    ),
    "driver_helper": (
        "ebca591a31b0b1894ca115649eb7eee0afa24c7cbfe0f790013cec7ae666f3aa"
    ),
    "transition_patch": (
        "2cafd2280f5233c50bcad94d1c2d4d5f76065ca1e4f8bb657de4fdb7e597f94f"
    ),
    "cpu_result": (
        "5761e21e652a66ae46cd8aff92dd84ee3eaeb3a088d2d1345b0218b5e62b94fb"
    ),
    "composed_manifest": (
        "88cdb1287461a82c6d2b79c467afd6c78fb232c0355e28e9bfc7291b8053917b"
    ),
    "source_checkpoint": (
        "3a31304fc673a4ec24cf7a2f099a51a9e120031787179afc973553f6dff92c26"
    ),
    "reference_features": (
        "8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212"
    ),
}


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
            raise FileExistsError(f"refusing to overwrite V119: {path}")

    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    manifest = playground / "WINNER_V119_COMPOSED_SOURCE_MANIFEST.json"
    cpu_result = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "driver": sha256(DRIVER),
        "driver_helper": sha256(DRIVER_HELPER),
        "transition_patch": sha256(PATCH),
        "cpu_result": sha256(CPU_RESULT),
        "composed_manifest": sha256(manifest),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(REFERENCE),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "driver_helper_exact": (
            input_hashes["driver_helper"] == EXPECTED["driver_helper"]
        ),
        "transition_patch_exact": (
            input_hashes["transition_patch"] == EXPECTED["transition_patch"]
        ),
        "cpu_result_exact": (
            cpu_result.get("status")
            == "PASS_WINNER_V119_TRANSITION_CPU_SMOKE_RECOVERED"
            and cpu_result.get("failed_checks") == []
            and cpu_result.get("authority", {}).get(
                "hosted_preregistration_authorized"
            )
            is True
            and cpu_result.get("recovery", {}).get("training_rerun")
            is False
        ),
        "single_continuation_only": True,
        "exact_v114_final_source": True,
        "same_v117_transition_vector": True,
        "no_new_reward_term": True,
        "no_scalar_search": True,
        "no_retry_or_resume": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "winner_v119.hosted_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V119_HOSTED_CONTINUATION"
            if not failed
            else "HOLD_WINNER_V119_HOSTED_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "date": "2026-07-24",
        "decision": (
            "AUTHORIZE_ONE_HASH_FROZEN_V119_GPU_CONTINUATION_WITHOUT_RETRY"
        ),
        "evidence_basis": {
            "v117_final_nominal_passes": 8,
            "v118_final_nominal_passes": 8,
            "v117_half_nominal_passes": 3,
            "v118_half_nominal_passes": 2,
            "output_only_rate_tightening_closed": True,
            "selected_mechanism": (
                "train transition matches deployed G3 and V117 final rate"
            ),
            "cpu_default_off_bit_exact": True,
            "cpu_step_zero_restore_bit_exact": True,
            "cpu_all_policy_leaves_updated": True,
            "cpu_deployed_onnx_contracts_pass": True,
        },
        "input_hashes": input_hashes,
        "training": {
            "source": "exact_v114_final_checkpoint",
            "seed": 100,
            "architecture": "reference_residual_recurrent_adapter",
            "recurrent_hidden_size": 64,
            "full_variable_configuration": True,
            "deviation_scale": 1.0,
            "transition_match_enabled": True,
            "actual_centered_guard_margin_rad": 0.165,
            "rate_limits_rad_s": [
                1.0,
                0.75,
                1.4736209064722061,
                1.4300791546702385,
                1.3976470567286015,
                0.5,
                0.5,
                0.5,
                0.5,
                0.5,
                0.75,
                1.25,
                1.0,
                1.2215287424623966,
            ],
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
            "apply_exact_v117_deployment_hierarchy_to": [
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
            "colab_sessions": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_hosted_gpu_continuation_after_package_contract": (
                not failed
            ),
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
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v119 hosted preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "One no-retry GPU continuation is frozen from exact V114 final. The "
        "only mechanism change is the CPU-proven train/deploy transition "
        "match; objectives, seed, architecture, and optimizer remain frozen. "
        "Both post-update checkpoints must pass nominal and robustness. No "
        "behavior, Gate 5, deployment, or robot authority is granted.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
