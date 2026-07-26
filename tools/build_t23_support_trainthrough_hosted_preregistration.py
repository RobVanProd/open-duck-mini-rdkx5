#!/usr/bin/env python3
"""Preregister one no-retry T23 support-train-through continuation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
T22_RESULT = ANALYSIS / "t22_corrected_one_update_cpu_result.json"
T22_PREREGISTRATION = (
    ANALYSIS / "t22_corrected_one_update_cpu_preregistration.json"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
DRIVER = ROOT / "tools" / "colab_t23_support_trainthrough_continuation.py"
COMPOSED = Path(
    "D:/CodexProjects/Open_Duck_Playground-composed-t19-v6"
)
MANIFEST = COMPOSED / "T19_COMPOSED_SOURCE_MANIFEST.json"
OUTPUT = ANALYSIS / "t23_support_trainthrough_hosted_preregistration.json"
MARKDOWN = (
    ANALYSIS / "T23_SUPPORT_TRAINTHROUGH_HOSTED_PREREGISTRATION_20260726.md"
)
BUILDER = (
    ROOT
    / "tools"
    / "build_t23_support_trainthrough_hosted_preregistration.py"
)
SOURCE_RATES = [
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
]
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


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T23: {path}")
    t22 = json.loads(T22_RESULT.read_text(encoding="utf-8"))
    t22_prereg = json.loads(T22_PREREGISTRATION.read_text(encoding="utf-8"))
    source = Path(
        t22_prereg["assets"]["source_checkpoint"]["path"]
    ).resolve()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    input_hashes = {
        "driver": sha256(DRIVER),
        "cpu_result": sha256(T22_RESULT),
        "composed_manifest": sha256(MANIFEST),
        "source_checkpoint": directory_sha256(source),
        "reference_features": sha256(REFERENCE),
    }
    driver_text = DRIVER.read_text(encoding="utf-8")
    checks = {
        "t22_passed_and_earned_hosted_preregistration": (
            t22.get("status")
            == "PASS_T22_CORRECTED_ONE_UPDATE_CPU_SMOKE"
            and t22.get("decision")
            == "EARN_T22_HOSTED_CONTINUATION_PREREGISTRATION"
            and t22.get("failed_checks") == []
        ),
        "source_checkpoint_is_exact_v121_half": (
            t22_prereg["assets"]["source_checkpoint"]["sha256"]
            == directory_sha256(source)
            and t22_prereg["contract"]["source"] == "V121_TRAIN_MATCHED_HALF"
        ),
        "driver_uses_source_and_external_rate_separation": (
            "SOURCE_VELOCITY_LIMITS" in driver_text
            and "--winner_t19_support_trainthrough" in driver_text
            and "T19_COMPOSED_SOURCE_MANIFEST.json" in driver_text
        ),
        "composed_v6_manifest_exact": (
            manifest.get("schema_version")
            == "open_duck.t19_composed_source.v1"
        ),
        "single_continuation_no_retry_resume": True,
        "both_postupdate_exports_required": True,
        "no_reward_or_optimizer_search": True,
        "behavior_cells_during_training_zero": True,
        "robot_surface_absent": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis = {
        "schema_version": (
            "open_duck.t23_support_trainthrough_hosted_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_T23_SUPPORT_TRAINTHROUGH_HOSTED_CONTINUATION"
            if not failed
            else "HOLD_T23_SUPPORT_TRAINTHROUGH_HOSTED_PREREGISTRATION"
        ),
        "decision": (
            "AUTHORIZE_ONE_HASH_FROZEN_T23_L4_CONTINUATION_WITHOUT_RETRY"
        ),
        "question": (
            "Can training through the CPU-proven coherent support handoff "
            "preserve V121's gait while adapting the recurrent actor to the "
            "deployment coordinate transition at both frozen checkpoints?"
        ),
        "evidence_basis": {
            "t21b_default_off_states": "9/9",
            "t21b_variable_configuration_prefixes": "64/64",
            "t21b_prefix_ticks": "250/250",
            "t22_restore_exact": True,
            "t22_all_actor_and_critic_leaves_updated": True,
            "t22_four_stage_step_zero_chain_byte_exact": True,
            "t20_training_selection_weight": 0,
        },
        "input_hashes": input_hashes,
        "paths": {
            "playground": str(COMPOSED.resolve()),
            "source_checkpoint": str(source),
            "reference": str(REFERENCE.resolve()),
        },
        "training": {
            "source": "exact_V121_TRAIN_MATCHED_HALF_checkpoint",
            "source_step": 1_003_520,
            "seed": 100,
            "architecture": "reference_residual_recurrent_adapter",
            "recurrent_hidden_size": 64,
            "support_trainthrough": True,
            "support_prefix_ticks": 250,
            "support_home_return_ticks": 0,
            "full_variable_configuration": True,
            "deviation_scale": 1.0,
            "source_rate_limits_rad_s": SOURCE_RATES,
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
            "apply_exact_four_stage_deployment_chain_to": [
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
            "t22_result_sha256": sha256(T22_RESULT),
            "t22_preregistration_sha256": sha256(T22_PREREGISTRATION),
            "manifest_sha256": sha256(MANIFEST),
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
                "# T23 support train-through hosted preregistration",
                "",
                f"- Status: `{value['status']}`",
                "- Run budget: `2,007,040 steps; one L4; no retry/resume`",
                "- Exports: `0 / 1,003,520 / 2,007,040`",
                "- Behavior/robot execution now: `0/0`",
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
    print(
        "preregistered_contract_sha256="
        f"{value['preregistered_contract_sha256']}"
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
