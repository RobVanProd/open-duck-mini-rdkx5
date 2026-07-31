#!/usr/bin/env python3
"""Preregister the single no-retry T67 endpoint-core continuation."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

from colab_t32_action_margin_trainthrough_continuation import (
    SOURCE_VELOCITY_LIMITS,
    canonical_sha256,
    source_inventory,
)
from colab_winner_v114_linear_torque_continuation import (
    directory_sha256,
    sha256,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
CPU_PREREG = ANALYSIS / "t66_endpoint_core_cpu_preregistration.json"
CPU_RESULT = ANALYSIS / "t66_endpoint_core_cpu_result.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
DRIVER = ROOT / "tools" / "colab_t67_endpoint_core_continuation.py"
BUILDER = ROOT / "tools" / "build_t67_endpoint_core_hosted_preregistration.py"
OUTPUT = ANALYSIS / "t67_endpoint_core_hosted_preregistration.json"
MARKDOWN = ANALYSIS / "T67_ENDPOINT_CORE_HOSTED_PREREGISTRATION_20260728.md"


def git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T67: {path}")
    cpu_prereg = json.loads(CPU_PREREG.read_text(encoding="utf-8"))
    cpu_result = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    source = Path(
        cpu_prereg["assets"]["source_checkpoint"]["path"]
    ).resolve()
    step_zero = Path(
        cpu_prereg["assets"]["expected_step_zero_raw"]["path"]
    ).resolve()
    playground = Path(cpu_prereg["playground"]["path"]).resolve()
    inventory = source_inventory(playground)
    python_inventory = {
        path: item["sha256"]
        for path, item in inventory.items()
        if path.endswith(".py")
    }
    input_hashes = {
        "driver": sha256(DRIVER),
        "cpu_result": sha256(CPU_RESULT),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(REFERENCE),
        "expected_step_zero_raw": sha256(step_zero),
        "playground_inventory": canonical_sha256(inventory),
    }
    driver_text = DRIVER.read_text(encoding="utf-8")
    checks = {
        "t66_cpu_contract_passed": (
            cpu_result.get("status")
            == "PASS_T66_ENDPOINT_CORE_CPU_CONTRACT"
            and cpu_result.get("decision")
            == "EARN_T67_ENDPOINT_CORE_HOSTED_PREREGISTRATION_ONLY"
            and cpu_result.get("failed_checks") == []
        ),
        "source_checkpoint_exact": (
            input_hashes["source_checkpoint"]
            == cpu_prereg["assets"]["source_checkpoint"]["sha256"]
        ),
        "step_zero_reference_exact": (
            input_hashes["expected_step_zero_raw"]
            == cpu_prereg["assets"]["expected_step_zero_raw"]["sha256"]
        ),
        "playground_inventory_exact": (
            python_inventory == cpu_prereg["playground"]["python_inventory"]
        ),
        "driver_enables_exact_mechanism": all(
            token in driver_text
            for token in (
                '"--winner_t19_support_trainthrough"',
                '"--winner_t31_action_margin_trainthrough"',
                '"--winner_t37_freeze_observation_normalizer"',
                '"--winner_t66_endpoint_core_continuation"',
            )
        ),
        "exact_two_million_step_no_retry_continuation": (
            "EXPECTED_STEPS = [0, 1_003_520, 2_007_040]" in driver_text
            and '"2007040"' in driver_text
            and "no-retry path exists" in driver_text
        ),
        "eight_strata_exact_at_hosted_population": (
            cpu_prereg["mechanism"]["hosted_environments"] == 256
            and cpu_prereg["mechanism"]["hosted_per_category"] == 32
            and len(cpu_prereg["mechanism"]["endpoint_categories"]) == 8
        ),
        "actor_update_scope_exact": (
            cpu_result["checks"]["every_core_leaf_updated"]
            and cpu_result["checks"]["every_other_actor_leaf_bit_exact"]
            and cpu_result["checks"]["normalizer_bit_exact"]
        ),
        "reward_abi_runtime_changes_zero": all(
            not cpu_prereg["mechanism"][key]
            for key in ("reward_change", "policy_abi_change", "runtime_change")
        ),
        "no_scalar_or_behavior_selection": (
            not cpu_prereg["mechanism"]["scalar_sweep"]
        ),
        "robot_surface_absent": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    basis = {
        "schema_version": "open_duck.t67_endpoint_core_hosted_preregistration.v1",
        "status": (
            "PREREGISTERED_T67_ENDPOINT_CORE_HOSTED_CONTINUATION"
            if not failed
            else "HOLD_T67_ENDPOINT_CORE_HOSTED_PREREGISTRATION"
        ),
        "decision": (
            "AUTHORIZE_ONE_HASH_FROZEN_T67_L4_CONTINUATION_WITHOUT_RETRY"
            if not failed
            else "NO_T67_HOSTED_EXECUTION"
        ),
        "question": (
            "Does one continuation from the exact T52-half source, with "
            "nominal/broad/all-six isolated COM endpoint strata and only the "
            "recurrent actor core trainable, produce two persistent nominal "
            "checkpoints without sacrificing the previously green gait?"
        ),
        "repository_commit": git_head(),
        "input_hashes": input_hashes,
        "paths": {
            "playground": str(playground),
            "source_checkpoint": str(source),
            "expected_step_zero_raw": str(step_zero),
            "reference": str(REFERENCE.resolve()),
        },
        "playground": {
            "file_count": len(inventory),
            "file_inventory": inventory,
        },
        "causal_basis": {
            "source": "T52-half, green 64/64 through R2 condition 4",
            "remaining_failure": (
                "isolated torso COM x=-0.05 m dynamic backward-pitch fall"
            ),
            "closed_family": (
                "balance-first reward homotopy improved intermediate gait "
                "but closed under its preregistered persistence rule"
            ),
            "mechanism": (
                "exact endpoint coverage plus recurrent-core-only adaptation"
            ),
        },
        "training": {
            "source": "exact_T55_materialized_T52_half_checkpoint",
            "source_step": 1_003_520,
            "seed": 100,
            "timesteps": 2_007_040,
            "exports": [0, 1_003_520, 2_007_040],
            "num_envs": 256,
            "endpoint_strata": 8,
            "environments_per_stratum": 32,
            "actor_trainable_groups": [
                "adapter_obs_projection",
                "adapter_hidden_projection",
                "adapter_hidden_bias",
            ],
            "all_other_actor_groups_frozen": True,
            "critic_trainable": True,
            "observation_normalizer_frozen": True,
            "source_velocity_limits_rad_s": [
                float(value) for value in SOURCE_VELOCITY_LIMITS.split(",")
            ],
            "episode_length": 600,
            "unroll_length": 20,
            "batch_size": 256,
            "num_minibatches": 4,
            "num_updates_per_batch": 4,
            "learning_rate": 0.0003,
            "discounting": 0.97,
            "entropy_cost": 0.005,
            "reward_change": False,
            "policy_abi_change": False,
            "runtime_change": False,
            "scalar_sweep": False,
            "reward_curve_selection": False,
            "wall_ceiling_seconds": 21_600,
            "retry": False,
            "resume": False,
        },
        "post_training": {
            "behavior_cells_during_training": 0,
            "cpu_topology_validation_before_behavior": True,
            "source_and_step_zero_must_be_exact": True,
            "only_recurrent_core_and_critic_may_change": True,
            "normalizer_must_remain_bit_exact": True,
            "apply_exact_deployment_chain_to": [1_003_520, 2_007_040],
            "evaluate_nominal_16_cells_first": True,
            "both_postupdate_checkpoints_must_pass": True,
            "checkpoint_cherry_pick": False,
            "resume_r2_only_after_nominal_pass": True,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution_now": {
            "optimizer_steps": 0,
            "simulator_locomotion_steps": 0,
            "formal_behavior_cells": 0,
            "colab_sessions": 0,
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
        "sources": {
            "builder_sha256": sha256(BUILDER),
            "driver_sha256": sha256(DRIVER),
            "cpu_preregistration_sha256": sha256(CPU_PREREG),
            "cpu_result_sha256": sha256(CPU_RESULT),
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T67 endpoint-core hosted preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Run budget: `2,007,040 steps; one L4; no retry/resume`",
                "- Exports: `0 / 1,003,520 / 2,007,040`",
                "- Population: `8 exact strata × 32 environments`",
                "- Actor updates: `recurrent adaptation core only`",
                "- Reward / ABI / runtime changes: `0 / 0 / 0`",
                "- Behavior/robot execution now: `0 / 0`",
                (
                    "- Contract SHA-256: "
                    f"`{value['preregistered_contract_sha256']}`"
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
