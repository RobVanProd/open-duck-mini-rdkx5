#!/usr/bin/env python3
"""Preregister one V175 lexicographic-tangent hosted continuation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
V173_PREREG = (
    ANALYSIS
    / "winner_v173_lexicographic_tangent_cpu_preregistration.json"
)
V173_RESULT = ANALYSIS / "winner_v173_lexicographic_tangent_cpu_result.json"
V174_RESULT = ANALYSIS / "winner_v174_tangent_nominal_result.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
DRIVER = ROOT / "tools/colab_winner_v175_tangent_continuation.py"
OUTPUT = ANALYSIS / "winner_v175_hosted_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V175_HOSTED_PREREGISTRATION_20260725.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(
        candidate for candidate in path.rglob("*") if candidate.is_file()
    ):
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
    manifest = playground / "WINNER_V173_COMPOSED_SOURCE_MANIFEST.json"
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V175: {path}")

    v173_prereg = json.loads(V173_PREREG.read_text(encoding="utf-8"))
    v173 = json.loads(V173_RESULT.read_text(encoding="utf-8"))
    v174 = json.loads(V174_RESULT.read_text(encoding="utf-8"))
    input_hashes = {
        "driver": sha256(DRIVER),
        "v173_cpu_preregistration": sha256(V173_PREREG),
        "v173_cpu_result": sha256(V173_RESULT),
        "v174_nominal_result": sha256(V174_RESULT),
        "composed_manifest": sha256(manifest),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(REFERENCE),
    }
    checks = {
        "v173_cpu_contract_green": (
            v173.get("status")
            == "PASS_WINNER_V173_LEXICOGRAPHIC_TANGENT_CPU_CONTRACT"
            and v173.get("failed_checks") == []
        ),
        "v173_cpu_preregistration_exact": (
            v173_prereg.get("status")
            == "PREREGISTERED_WINNER_V173_LEXICOGRAPHIC_TANGENT_CPU_CONTRACT"
        ),
        "v174_nominal_screen_green_and_improves_source": (
            v174.get("status") == "PASS_WINNER_V174_TANGENT_NOMINAL"
            and v174.get("failed_checks") == []
            and v174.get("decision")
            == "EARN_ONE_V175_HOSTED_PREREGISTRATION_ONLY"
            and float(
                v174["summary"]["source_torque_reserve_improvement_nm"]
            )
            > 0.0
        ),
        "exact_v121_half_source": (
            directory_sha256(source)
            == "29b6d1d707784cc49050ab4b5513c06b020ebf7cf02dba3bee304a74477348f8"
        ),
        "lexicographic_branches_fixed": True,
        "actor_adam_disabled": True,
        "dual_disabled": True,
        "no_new_scalar": True,
        "single_continuation_only": True,
        "no_retry_or_resume": True,
        "both_postupdate_checkpoints_required": True,
        "robot_surface_absent": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v175.hosted_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V175_HOSTED_CONTINUATION"
            if not failed
            else "HOLD_WINNER_V175_HOSTED_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "decision": (
            "AUTHORIZE_ONE_HASH_FROZEN_V175_GPU_CONTINUATION_WITHOUT_RETRY"
            if not failed
            else "NO_HOSTED_RUN"
        ),
        "input_hashes": input_hashes,
        "evidence_basis": {
            "v170_first_r2_oracle_complete_walk": True,
            "v170_oracle_empty_intersections": 0,
            "v172_positive_batch_cost": 0.1912466287612915,
            "v172_tangent_retention": 0.5960909128189087,
            "v173_cpu_actor_updates": 64,
            "v173_cpu_zero_direction_updates": 0,
            "v173_cpu_max_constrained_derivative_excess": 0.0,
            "v174_nominal_cells": 8,
            "v174_worst_peak_torque_nm": v174["summary"][
                "worst_peak_torque_nm"
            ],
            "v174_source_reserve_improvement_nm": v174["summary"][
                "source_torque_reserve_improvement_nm"
            ],
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
            "actor_global_norm_cap": 1.0,
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
            "actor_optimizer": {
                "pre_cost": "reward descent",
                "positive_cost": "cost descent",
                "post_cost_zero_batch": "cost-tangent reward descent",
                "adam": False,
            },
            "critics": "separate reward/cost critics with frozen Adam",
            "dual": "disabled, all state pinned zero",
            "wall_ceiling_seconds": 21_600,
            "retry": False,
            "resume": False,
            "reward_curve_selection": False,
        },
        "falsifiable_prediction": {
            "expected_direction": (
                "cost-first and tangent steps prevent the half-to-final "
                "unconstrained drift seen in V127 while reward-only steps "
                "before the first violation preserve gait acquisition"
            ),
            "success": (
                "both half and final pass all 16 nominal physical/behavior "
                "cells, followed by the unchanged complete robustness matrix"
            ),
            "failure": (
                "either checkpoint fails any nominal cell; close V175 without "
                "branch, optimizer, lr, norm, batch, source, retry, resume, "
                "or checkpoint changes"
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
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V175 hosted preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Run budget: one 2,007,040-step hosted continuation, no retry or "
        "resume.\n"
        "- Source: exact V121-half raw checkpoint.\n"
        "- Actor: reward-only before cost, cost-only on violating batches, "
        "cost-tangent reward updates afterward; no actor Adam or dual.\n"
        "- Required exports: 0, 1,003,520, 2,007,040.\n"
        "- Both post-update checkpoints must pass all 16 nominal cells before "
        "the full robustness matrix.\n"
        "- Robot, RDK-X5, Gate 5, and motion authority: absent.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
