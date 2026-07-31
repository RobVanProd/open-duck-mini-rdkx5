#!/usr/bin/env python3
"""Preregister one Winner-v122 episode-peak hosted continuation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CPU_RESULT = ANALYSIS / "winner_v122_episode_peak_cpu_result.json"
REWARD_MASS = ANALYSIS / "winner_v122_cpu_reward_mass_attribution.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
DRIVER = ROOT / "tools/colab_winner_v122_episode_peak_continuation.py"
DRIVER_HELPER = (
    ROOT / "tools/colab_winner_v114_linear_torque_continuation.py"
)
PATCH = ROOT / "patches/winner_v122_episode_peak_torque_increment.patch"
OUTPUT = ANALYSIS / "winner_v122_hosted_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V122_HOSTED_PREREGISTRATION_20260724.md"
EXPECTED = {
    "driver": (
        "6d2e1e4a6253436f59d683f175adbe1e7dac1e5fd76dc6b933057c88aa1aea69"
    ),
    "driver_helper": (
        "ebca591a31b0b1894ca115649eb7eee0afa24c7cbfe0f790013cec7ae666f3aa"
    ),
    "objective_patch": (
        "afa07528fa832b0e64e220587936b3c699ee893f026d1caa822674b3850f6c8e"
    ),
    "cpu_result": (
        "56006d763f9a92ef2a40ea6e0501ef7181d5411569f411b43b85f6614f88689a"
    ),
    "reward_mass_attribution": (
        "5704b7e4cdff53cd1bbb13b2b0077802e4228471fe26e139622d82c1d8385de3"
    ),
    "composed_manifest": (
        "5a53d713e22035151f2f5aaa1a3ee57735a90296a15fe5f3336f13178fca8918"
    ),
    "source_checkpoint": (
        "6f2d9856b5ab674f9f20f04c46be6dc00adc5eabc31826f16b4743c5172dfad8"
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
            raise FileExistsError(f"refusing to overwrite V122: {path}")
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    manifest = playground / "WINNER_V122_COMPOSED_SOURCE_MANIFEST.json"
    cpu_result = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    reward_mass = json.loads(REWARD_MASS.read_text(encoding="utf-8"))
    input_hashes = {
        "driver": sha256(DRIVER),
        "driver_helper": sha256(DRIVER_HELPER),
        "objective_patch": sha256(PATCH),
        "cpu_result": sha256(CPU_RESULT),
        "reward_mass_attribution": sha256(REWARD_MASS),
        "composed_manifest": sha256(manifest),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(REFERENCE),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "cpu_result_exact_green": (
            cpu_result.get("status")
            == "PASS_WINNER_V122_EPISODE_PEAK_CPU_SMOKE"
            and cpu_result.get("failed_checks") == []
            and cpu_result.get("authority", {}).get(
                "hosted_preregistration_authorized"
            )
            is True
        ),
        "reward_mass_attribution_exact_green": (
            reward_mass.get("status")
            == "PASS_WINNER_V122_CPU_REWARD_MASS_ATTRIBUTION"
            and reward_mass.get("decision")
            == "PREREGISTER_ONE_V122_HOSTED_CONTINUATION"
        ),
        "exact_v119_half_source": True,
        "source_used_for_continuation_not_deployment": True,
        "objective_is_exact_gate_surrogate": True,
        "existing_linear_hinge_disabled": True,
        "same_scale_no_search": True,
        "single_continuation_only": True,
        "no_retry_or_resume": True,
        "both_postupdate_checkpoints_required": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "winner_v122.hosted_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V122_HOSTED_CONTINUATION"
            if not failed
            else "HOLD_WINNER_V122_HOSTED_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "date": "2026-07-24",
        "decision": (
            "AUTHORIZE_ONE_HASH_FROZEN_V122_GPU_CONTINUATION_WITHOUT_RETRY"
        ),
        "evidence_basis": {
            "v121_half_nominal_passes": 8,
            "v121_final_nominal_passes": 3,
            "v121_failure_class": "sparse_current_and_torque_peaks_only",
            "torque_exceed_events": 15,
            "selected_mechanism": (
                "episode-global peak torque increment integral"
            ),
            "cpu_default_off_exact": True,
            "cpu_integral_identity_exact": True,
            "cpu_step_zero_restore_bit_exact": True,
            "cpu_all_15_policy_leaves_updated": True,
            "cpu_deployed_onnx_contracts_pass": True,
            "cpu_reward_and_episode_length_healthy": True,
        },
        "input_hashes": input_hashes,
        "training": {
            "source": "exact_v119_half_checkpoint",
            "source_step": 1_003_520,
            "seed": 100,
            "architecture": "reference_residual_recurrent_adapter",
            "recurrent_hidden_size": 64,
            "full_variable_configuration": True,
            "deviation_scale": 1.0,
            "transition_match_enabled": True,
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
            "episode_peak_torque_threshold_nm": 1.91229675,
            "episode_peak_torque_increment_scale": -307.48131091308585,
            "linear_peak_torque_scale": 0.0,
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
            "apply_exact_v121_deployment_hierarchy_to": [
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
        "# Winner-v122 hosted preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "One no-retry GPU continuation is frozen from exact V119 half. The "
        "only objective change is the CPU-proven episode-global peak "
        "increment; the old linear hinge is zero. Both post-update "
        "checkpoints remain mandatory. No behavior, Gate 5, RDK-X5, or "
        "robot authority is granted.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
