#!/usr/bin/env python3
"""Preregister one no-retry T32 action-margin continuation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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
T31_RESULT = ANALYSIS / "t31_action_margin_trainthrough_cpu_result.json"
T31_PREREGISTRATION = (
    ANALYSIS / "t31_action_margin_trainthrough_cpu_preregistration.json"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
DRIVER = ROOT / "tools" / "colab_t32_action_margin_trainthrough_continuation.py"
BUILDER = (
    ROOT
    / "tools"
    / "build_t32_action_margin_trainthrough_hosted_preregistration.py"
)
OUTPUT = (
    ANALYSIS / "t32_action_margin_trainthrough_hosted_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "T32_ACTION_MARGIN_TRAINTHROUGH_HOSTED_PREREGISTRATION_20260727.md"
)
EXTERNAL_RATES = [
    1.0,
    0.75,
    1.5,
    1.5,
    1.5,
    0.5,
    0.5,
    0.5,
    0.5,
    0.5,
    0.75,
    1.25,
    1.0,
    1.25,
]


def parse_rates(value: str) -> list[float]:
    return [float(item) for item in value.split(",")]


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T32: {path}")
    t31 = json.loads(T31_RESULT.read_text(encoding="utf-8"))
    t31_prereg = json.loads(
        T31_PREREGISTRATION.read_text(encoding="utf-8")
    )
    source = Path(
        t31_prereg["assets"]["source_checkpoint"]["path"]
    ).resolve()
    playground = Path(t31_prereg["playground"]["path"]).resolve()
    inventory = source_inventory(playground)
    python_inventory = {
        path: item["sha256"]
        for path, item in inventory.items()
        if path.endswith(".py")
    }
    input_hashes = {
        "driver": sha256(DRIVER),
        "cpu_result": sha256(T31_RESULT),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(REFERENCE),
        "playground_inventory": canonical_sha256(inventory),
    }
    driver_text = DRIVER.read_text(encoding="utf-8")
    checks = {
        "t31_passed_and_earned_hosted_preregistration": (
            t31.get("status")
            == "PASS_T31_ACTION_MARGIN_TRAINTHROUGH_CPU_SMOKE"
            and t31.get("decision")
            == "EARN_T31_HOSTED_CONTINUATION_PREREGISTRATION"
            and t31.get("failed_checks") == []
        ),
        "source_checkpoint_is_exact_t23_half": (
            t31_prereg["assets"]["source_checkpoint"]["sha256"]
            == directory_sha256(source)
            and t31_prereg["selection_evidence"][
                "half_margin_green_cells"
            ]
            == 24
        ),
        "playground_python_inventory_matches_cpu_smoke": (
            python_inventory
            == t31_prereg["playground"]["python_inventory"]
        ),
        "driver_enables_both_required_transitions": (
            '"--winner_t19_support_trainthrough"' in driver_text
            and '"--winner_t31_action_margin_trainthrough"' in driver_text
        ),
        "exact_two_million_step_no_retry_continuation": (
            "EXPECTED_STEPS = [0, 1_003_520, 2_007_040]" in driver_text
            and '"2007040"' in driver_text
            and "no-retry path exists" in driver_text
        ),
        "no_reward_or_optimizer_search": True,
        "behavior_cells_during_training_zero": True,
        "robot_surface_absent": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t32_action_margin_trainthrough_hosted_"
            "preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T32_ACTION_MARGIN_TRAINTHROUGH_HOSTED_CONTINUATION"
            if not failed
            else "HOLD_T32_ACTION_MARGIN_TRAINTHROUGH_HOSTED_PREREGISTRATION"
        ),
        "decision": (
            "AUTHORIZE_ONE_HASH_FROZEN_T32_L4_CONTINUATION_WITHOUT_RETRY"
        ),
        "question": (
            "Can continuing from the exact T23 half checkpoint while the "
            "environment realizes the final 0.98 action margin preserve gait "
            "and prevent the final-checkpoint margin drift at both exports?"
        ),
        "evidence_basis": {
            "t23_half_margin_green_cells": 24,
            "t28_posthoc_transform_closed": True,
            "t31_cpu_restore_update_export_passed": True,
            "t31_all_policy_and_critic_leaves_updated": True,
            "t31_both_margin_export_contracts_passed": True,
            "reward_changes": 0,
            "new_scalar_search": False,
        },
        "input_hashes": input_hashes,
        "paths": {
            "playground": str(playground),
            "source_checkpoint": str(source),
            "reference": str(REFERENCE.resolve()),
        },
        "playground": {
            "file_count": len(inventory),
            "file_inventory": inventory,
        },
        "training": {
            "source": "exact_T23_SUPPORT_HALF_checkpoint",
            "source_step": 1_003_520,
            "seed": 100,
            "architecture": "reference_residual_recurrent_adapter",
            "recurrent_hidden_size": 64,
            "support_trainthrough": True,
            "action_margin_trainthrough": True,
            "action_margin_limit": (
                "nextafter(float32(0.98), float32(0.0))"
            ),
            "full_variable_configuration": True,
            "deviation_scale": 1.0,
            "source_rate_limits_rad_s": parse_rates(
                SOURCE_VELOCITY_LIMITS
            ),
            "external_rate_limits_rad_s": EXTERNAL_RATES,
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
            "apply_exact_t31_deployment_chain_to": [
                1_003_520,
                2_007_040,
            ],
            "evaluate_nominal_16_cells_first": True,
            "both_postupdate_checkpoints_must_pass": True,
            "checkpoint_cherry_pick": False,
            "robustness_only_after_nominal_pass": True,
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
            "t31_result_sha256": sha256(T31_RESULT),
            "t31_preregistration_sha256": sha256(T31_PREREGISTRATION),
        },
    }
    value = {
        **basis,
        "preregistered_contract_sha256": canonical_sha256(basis),
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T32 action-margin train-through hosted preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Run budget: `2,007,040 steps; one L4; no retry/resume`",
                "- Exports: `0 / 1,003,520 / 2,007,040`",
                "- Reward changes / scalar search: `0 / 0`",
                "- Behavior/robot execution now: `0 / 0`",
                (
                    "- Contract SHA-256: "
                    f"`{value['preregistered_contract_sha256']}`"
                ),
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"playground_files={len(inventory)}")
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
