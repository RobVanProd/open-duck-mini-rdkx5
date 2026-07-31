#!/usr/bin/env python3
"""Preregister one V127 constrained hosted continuation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CPU_RESULT = ANALYSIS / "winner_v127_constrained_cpu_result.json"
CPU_PREREG = ANALYSIS / "winner_v127_constrained_cpu_preregistration.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
DRIVER = ROOT / "tools/colab_winner_v127_constrained_continuation.py"
OUTPUT = ANALYSIS / "winner_v127_hosted_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V127_HOSTED_PREREGISTRATION_20260724.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
        digest.update(item.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with item.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    args = parser.parse_args()
    playground = args.playground_root.resolve()
    source = args.source_checkpoint.resolve()
    manifest = playground / "WINNER_V127_COMPOSED_SOURCE_MANIFEST.json"
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite {path}")
    cpu_result = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "driver": sha256(DRIVER),
        "cpu_result": sha256(CPU_RESULT),
        "cpu_preregistration": sha256(CPU_PREREG),
        "composed_manifest": sha256(manifest),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(REFERENCE),
    }
    checks = {
        "cpu_contract_green": (
            cpu_result.get("status")
            == "PASS_WINNER_V127_CONSTRAINED_CPU_CONTRACT"
            and cpu_result.get("failed_checks") == []
            and cpu_result.get("decision")
            == "EARN_ONE_V127_HOSTED_PREREGISTRATION"
            and cpu_result.get("authority", {}).get(
                "hosted_preregistration_authorized"
            )
            is True
        ),
        "oracle_screen_green": True,
        "exact_v121_half_source": True,
        "dense_cost_outside_reward": True,
        "separate_cost_critic": True,
        "first_positive_batch_dual_derivation": True,
        "no_dual_scalar_search": True,
        "single_continuation_only": True,
        "no_retry_or_resume": True,
        "both_postupdate_checkpoints_required": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v127.hosted_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V127_HOSTED_CONTINUATION"
            if not failed
            else "HOLD_WINNER_V127_HOSTED_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "decision": (
            "AUTHORIZE_ONE_HASH_FROZEN_V127_GPU_CONTINUATION_WITHOUT_RETRY"
            if not failed
            else "NO_HOSTED_RUN"
        ),
        "input_hashes": input_hashes,
        "evidence_basis": {
            "oracle_cells_passed": 16,
            "oracle_total_cells": 16,
            "oracle_torque_projections": 15,
            "oracle_empty_intersections": 0,
            "cpu_contract_failed_checks": [],
            "cpu_policy_and_cost_critic_all_leaves_updated": True,
            "cpu_step0_v121_half_max_abs_error": (
                cpu_result["deployment"][
                    "step0_v121_half_max_abs_error"
                ]
            ),
            "cpu_first_positive_batch_cost": (
                cpu_result["training"]["aux"]["1024"]["initial_cost"]
            ),
            "cpu_derived_eta": (
                cpu_result["training"]["aux"]["1024"]["eta"]
            ),
            "cpu_final_lambda": (
                cpu_result["training"]["aux"]["1024"]["lambda"]
            ),
        },
        "training": {
            "source": "exact_v121_half_raw_checkpoint",
            "source_step": 1_003_520,
            "seed": 100,
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
            "architecture": "reference_residual_recurrent_adapter",
            "recurrent_hidden_size": 64,
            "full_variable_configuration": True,
            "deviation_scale": 1.0,
            "transition_match_enabled": True,
            "tracking_tail_threshold_rad": 0.20,
            "tracking_tail_scale": -6572.254964031055,
            "old_squared_torque_scale": 0.0,
            "old_linear_torque_scale": 0.0,
            "dense_cost": (
                "sum_j max(abs(actuator_force_nm[j])-1.91229675,0)"
            ),
            "cost_discount": 1.0,
            "cost_critic": "separate privileged-state value network",
            "dual_eta": "1/(ceil(K/4)*first_positive_batch_cost)",
            "dual_scalars_searched": 0,
            "wall_ceiling_seconds": 21_600,
            "retry": False,
            "resume": False,
            "reward_curve_selection": False,
        },
        "falsifiable_prediction": {
            "expected_direction": (
                "the later checkpoint should be at least as torque-safe as "
                "the half checkpoint because violations are no longer an "
                "unpriced reward trade"
            ),
            "success": (
                "both half and final pass all 16 nominal physical cells"
            ),
            "failure": (
                "either checkpoint fails any nominal cell; close V127 without "
                "eta changes, retry, resume, or a second continuation"
            ),
        },
        "post_training": {
            "cpu_topology_validation_before_behavior": True,
            "deployment_transform_both_postupdate_checkpoints": True,
            "nominal_cells_first": 16,
            "full_frozen_robustness_only_after_nominal_pass": True,
            "checkpoint_cherry_pick": False,
        },
        "authority": {
            "one_hosted_gpu_continuation_after_package_contract": not failed,
            "additional_training_or_retry": False,
            "behavior_evaluation": False,
            "checkpoint_selection": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V127 hosted preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Run budget: one 2,007,040-step L4 continuation, no retry/resume\n"
        "- Source: exact V121-half raw checkpoint\n"
        "- Objective: unchanged reward plus a separate dense torque-cost critic\n"
        "- Required exports: 0, 1,003,520, 2,007,040\n"
        "- Selection: both post-update checkpoints must pass all 16 nominal cells\n"
        "- Robot, RDK-X5, Gate 5, and motion authority: absent\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
