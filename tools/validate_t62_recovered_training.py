#!/usr/bin/env python3
"""Validate recovered T62 midpoint and transfer outputs on CPU topology."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

from flax.training import orbax_utils
import jax
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from validate_winner_v112_recovered_training import (  # noqa: E402
    directory_sha256,
    event_scalars,
    onnx_contract,
    sha256,
    step,
    tree_deltas,
    tree_finite,
)


ANALYSIS = ROOT / "outputs" / "analysis"
HOSTED_PREREGISTRATION = (
    ANALYSIS
    / "t62_midpoint_gait_transfer_hosted_preregistration.json"
)
T61_RESULT = ANALYSIS / "t61_midpoint_gait_transfer_cpu_result.json"
PACKAGE_CONTRACT = (
    ANALYSIS
    / "t62_midpoint_gait_transfer_hosted_package_contract.json"
)
LAUNCH_CONTRACT = ANALYSIS / "t62_colab_cli_launch_contract.json"
OUTPUT = ANALYSIS / "t62_recovered_training_validation.json"
MARKDOWN = ANALYSIS / "T62_RECOVERED_TRAINING_VALIDATION_20260728.md"
HOSTED_PREREGISTRATION_SHA256 = (
    "59c194e147ad30644c8ee766a5ffcaaf6a2927e8c6123fd594097b46e4c51b7b"
)
T61_RESULT_SHA256 = (
    "f4841089a531b76daa9601774405fd42d9ff90c47c53388b69cedbb9131d3013"
)
PACKAGE_CONTRACT_SHA256 = (
    "799fce40eae39cc0bc4fc0b19561aceaca4878fa291b673719af3d1d1f9bac87"
)
LAUNCH_CONTRACT_SHA256 = (
    "c1ae78799facd67b1bd4b4fab133731f8e00e4cfd353cd321807875d51aa7de1"
)
SOURCE_CHECKPOINT_SHA256 = (
    "4d2c2098489bedebf637f72cb3f520a94b036af8989ddab9a568697ec1db07b8"
)
CPU_TEMPLATE_SHA256 = (
    "16a867c653476d6829ddaf400e5f02fc21658a78d3efc5ddfd167cc497f3ac83"
)
EXPECTED_MIDPOINT_STEPS = [0, 1_003_520]
EXPECTED_TRANSFER_STEPS = [0, 1_003_520, 2_007_040]


def leaf_update_row(
    source: Any,
    target: Any,
    target_step: int,
) -> dict[str, Any]:
    structure, deltas = tree_deltas(source, target)
    policy_deltas = {
        name: value
        for name, value in deltas.items()
        if name.startswith("1/params/")
    }
    critic_deltas = {
        name: value
        for name, value in deltas.items()
        if name.startswith("2/params/")
    }
    return {
        "step": target_step,
        "structure_exact": structure,
        "tree_finite": tree_finite(target),
        "policy_leaf_deltas": policy_deltas,
        "critic_leaf_deltas": critic_deltas,
        "every_policy_leaf_updated": bool(policy_deltas)
        and all(value > 0.0 for value in policy_deltas.values()),
        "every_critic_leaf_updated": bool(critic_deltas)
        and all(value > 0.0 for value in critic_deltas.values()),
    }


def stage_artifacts(
    training: Path,
    expected_steps: list[int],
) -> dict[str, Any]:
    checkpoints = sorted(
        (path for path in training.iterdir() if path.is_dir()),
        key=step,
    )
    graphs = sorted(training.glob("*.onnx"), key=step)
    return {
        "training": training,
        "checkpoints": checkpoints,
        "graphs": graphs,
        "checkpoint_steps": [step(path) for path in checkpoints],
        "onnx_steps": [step(path) for path in graphs],
        "checkpoint_hashes": {
            step(path): directory_sha256(path) for path in checkpoints
        },
        "graph_rows": [onnx_contract(path) for path in graphs],
        "expected_steps": expected_steps,
    }


def metric_evidence(
    training: Path,
    expected_steps: list[int],
) -> tuple[dict[str, list[dict[str, Any]]], bool, bool, bool]:
    event_file = next(training.glob("events.out.tfevents*"))
    scalars = event_scalars(event_file)
    tags = (
        "eval/episode_reward/t55_left_support_match",
        "eval/episode_reward/t55_right_support_match",
        "eval/episode_reward/t55_single_support_balance",
        "eval/episode_reward",
        "eval/avg_episode_length",
    )
    evidence = {tag: scalars.get(tag, []) for tag in tags}
    steps_exact = all(
        [row["step"] for row in rows] == expected_steps
        for rows in evidence.values()
    )
    finite = all(
        math.isfinite(row["value"])
        for rows in evidence.values()
        for row in rows
    )
    bilateral_positive = all(
        row["value"] > 0.0
        for tag in tags[:3]
        for row in evidence[tag]
    )
    return evidence, steps_exact, finite, bilateral_positive


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recovery-root", type=Path, required=True)
    parser.add_argument("--extracted-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    args = parser.parse_args()
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite T62 validation")
    recovery = args.recovery_root.resolve()
    work = (
        args.extracted_root.resolve()
        / "t62_midpoint_gait_transfer_continuation"
    )
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    paths = {
        "hosted_result": recovery / "t62_result.json",
        "launch_receipt": recovery / "t62_launch_receipt.json",
        "recovery_archive": recovery / "t62_artifacts.tar.gz",
    }
    input_hashes = {name: sha256(path) for name, path in paths.items()}
    source_hash = directory_sha256(source)
    cpu_template_hash = directory_sha256(cpu_template)
    prereg = json.loads(
        HOSTED_PREREGISTRATION.read_text(encoding="utf-8")
    )
    t61 = json.loads(T61_RESULT.read_text(encoding="utf-8"))
    package_contract = json.loads(
        PACKAGE_CONTRACT.read_text(encoding="utf-8")
    )
    launch_contract = json.loads(
        LAUNCH_CONTRACT.read_text(encoding="utf-8")
    )
    hosted = json.loads(paths["hosted_result"].read_text(encoding="utf-8"))
    receipt = json.loads(
        paths["launch_receipt"].read_text(encoding="utf-8")
    )
    midpoint = stage_artifacts(
        work / "midpoint_training",
        EXPECTED_MIDPOINT_STEPS,
    )
    transfer = stage_artifacts(
        work / "transfer_training",
        EXPECTED_TRANSFER_STEPS,
    )

    checkpointer = ocp.PyTreeCheckpointer()
    topology_template = checkpointer.restore(str(cpu_template))
    source_tree = checkpointer.restore(
        str(source),
        item=topology_template,
        restore_args=orbax_utils.restore_args_from_target(
            topology_template
        ),
    )
    restore_args = orbax_utils.restore_args_from_target(source_tree)
    midpoint_trees = [
        checkpointer.restore(
            str(path),
            item=source_tree,
            restore_args=restore_args,
        )
        for path in midpoint["checkpoints"]
    ]
    transfer_trees = [
        checkpointer.restore(
            str(path),
            item=source_tree,
            restore_args=restore_args,
        )
        for path in transfer["checkpoints"]
    ]
    midpoint_zero_structure, midpoint_zero_deltas = tree_deltas(
        source_tree,
        midpoint_trees[0],
    )
    transfer_zero_structure, transfer_zero_deltas = tree_deltas(
        midpoint_trees[-1],
        transfer_trees[0],
    )
    midpoint_updates = [
        leaf_update_row(
            midpoint_trees[0],
            midpoint_trees[1],
            EXPECTED_MIDPOINT_STEPS[1],
        )
    ]
    transfer_updates = [
        leaf_update_row(transfer_trees[0], tree, step_value)
        for tree, step_value in zip(
            transfer_trees[1:],
            EXPECTED_TRANSFER_STEPS[1:],
            strict=True,
        )
    ]
    (
        midpoint_metrics,
        midpoint_metric_steps,
        midpoint_metric_finite,
        midpoint_bilateral_positive,
    ) = metric_evidence(
        midpoint["training"],
        EXPECTED_MIDPOINT_STEPS,
    )
    (
        transfer_metrics,
        transfer_metric_steps,
        transfer_metric_finite,
        transfer_bilateral_positive,
    ) = metric_evidence(
        transfer["training"],
        EXPECTED_TRANSFER_STEPS,
    )

    def hosted_checkpoint_hashes(stage_name: str) -> dict[int, str]:
        return {
            int(row["step"]): row["directory_sha256"]
            for row in hosted[stage_name]["checkpoints"]
        }

    def hosted_onnx_hashes(stage_name: str) -> dict[int, str]:
        return {
            int(row["step"]): row["sha256"]
            for row in hosted[stage_name]["onnx"]
        }

    def observed_onnx_hashes(stage: dict[str, Any]) -> dict[int, str]:
        return {
            int(row["step"]): row["sha256"]
            for row in stage["graph_rows"]
        }

    all_graphs = midpoint["graph_rows"] + transfer["graph_rows"]
    all_trees = midpoint_trees + transfer_trees
    result_sha = input_hashes["hosted_result"]
    archive_sha = input_hashes["recovery_archive"]
    checks = {
        "hosted_preregistration_exact": (
            sha256(HOSTED_PREREGISTRATION)
            == HOSTED_PREREGISTRATION_SHA256
            and prereg["status"]
            == "PREREGISTERED_T62_MIDPOINT_GAIT_TRANSFER_HOSTED_CONTINUATION"
            and prereg["failed_checks"] == []
        ),
        "t61_cpu_authority_exact": (
            sha256(T61_RESULT) == T61_RESULT_SHA256
            and t61["status"]
            == "PASS_T61_MIDPOINT_GAIT_TRANSFER_CPU_CONTRACT"
            and t61["decision"]
            == "EARN_T62_MIDPOINT_GAIT_TRANSFER_HOSTED_PREREGISTRATION"
        ),
        "hosted_package_contract_exact": (
            sha256(PACKAGE_CONTRACT) == PACKAGE_CONTRACT_SHA256
            and package_contract["status"]
            == "PASS_T62_MIDPOINT_GAIT_TRANSFER_HOSTED_PACKAGE"
            and package_contract["failed_checks"] == []
        ),
        "launch_contract_exact": (
            sha256(LAUNCH_CONTRACT) == LAUNCH_CONTRACT_SHA256
            and launch_contract["status"]
            == "PASS_T62_COLAB_CLI_LAUNCH_CONTRACT"
            and launch_contract["failed_checks"] == []
        ),
        "source_checkpoint_exact": (
            source_hash == SOURCE_CHECKPOINT_SHA256
            and source_hash == prereg["input_hashes"]["source_checkpoint"]
        ),
        "cpu_template_exact": cpu_template_hash == CPU_TEMPLATE_SHA256,
        "hosted_artifact_passed_pending_cpu_validation": (
            hosted["status"]
            == "PASS_T62_TRAINING_ARTIFACT_PENDING_CPU_VALIDATION"
            and hosted["failed_checks"] == []
            and hosted["cpu_topology_validation_required"] is True
        ),
        "hosted_inputs_match_preregistration": (
            hosted["validation"]["input_hashes"]
            == prereg["input_hashes"]
            and hosted["validation"]["preregistration_sha256"]
            == HOSTED_PREREGISTRATION_SHA256
        ),
        "launch_receipt_complete": (
            receipt["status"] == "COMPLETED_T62_COLAB_LAUNCH"
            and receipt["returncode"] == 0
            and receipt["retry"] is False
            and receipt["resume"] is False
            and receipt["robot_or_rdk_access"] is False
        ),
        "result_hash_matches_receipt": (
            receipt["output_json_sha256"] == result_sha
        ),
        "archive_hash_matches_result_and_receipt": (
            hosted["artifact"]["sha256"] == archive_sha
            and receipt["output_archive_sha256"] == archive_sha
            and hosted["artifact"]["bytes"]
            == paths["recovery_archive"].stat().st_size
        ),
        "midpoint_local_exact_exports": (
            midpoint["checkpoint_steps"] == EXPECTED_MIDPOINT_STEPS
            and midpoint["onnx_steps"] == EXPECTED_MIDPOINT_STEPS
        ),
        "transfer_local_exact_exports": (
            transfer["checkpoint_steps"] == EXPECTED_TRANSFER_STEPS
            and transfer["onnx_steps"] == EXPECTED_TRANSFER_STEPS
        ),
        "all_checkpoint_hashes_match_hosted_result": (
            midpoint["checkpoint_hashes"]
            == hosted_checkpoint_hashes("midpoint")
            and transfer["checkpoint_hashes"]
            == hosted_checkpoint_hashes("transfer")
        ),
        "all_onnx_hashes_match_hosted_result": (
            observed_onnx_hashes(midpoint)
            == hosted_onnx_hashes("midpoint")
            and observed_onnx_hashes(transfer)
            == hosted_onnx_hashes("transfer")
        ),
        "midpoint_step_zero_source_bit_exact": (
            midpoint_zero_structure
            and max(midpoint_zero_deltas.values(), default=0.0) == 0.0
        ),
        "transfer_step_zero_midpoint_final_bit_exact": (
            transfer_zero_structure
            and max(transfer_zero_deltas.values(), default=0.0) == 0.0
        ),
        "all_checkpoint_trees_finite": all(
            tree_finite(tree) for tree in all_trees
        ),
        "all_midpoint_actor_and_critic_leaves_updated": all(
            row["structure_exact"]
            and row["tree_finite"]
            and row["every_policy_leaf_updated"]
            and row["every_critic_leaf_updated"]
            for row in midpoint_updates
        ),
        "all_transfer_actor_and_critic_leaves_updated": all(
            row["structure_exact"]
            and row["tree_finite"]
            and row["every_policy_leaf_updated"]
            and row["every_critic_leaf_updated"]
            for row in transfer_updates
        ),
        "all_onnx_contracts_pass": all(
            row["abi_exact"]
            and row["initializers_finite"]
            and row["cpu_provider_exact"]
            and row["chain_256_finite"]
            for row in all_graphs
        ),
        "training_metrics_have_exact_export_steps": (
            midpoint_metric_steps and transfer_metric_steps
        ),
        "training_metrics_all_finite": (
            midpoint_metric_finite and transfer_metric_finite
        ),
        "bilateral_support_metrics_positive_at_every_export": (
            midpoint_bilateral_positive and transfer_bilateral_positive
        ),
        "cpu_only_validation": all(
            device.platform == "cpu" for device in jax.devices()
        ),
        "formal_behavior_cells_zero": (
            hosted["formal_behavior_cells_executed"] == 0
        ),
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "open_duck.t62_recovered_training_validation.v1",
        "status": (
            "PASS_T62_RECOVERED_TRAINING_VALIDATION"
            if not failed
            else "HOLD_T62_RECOVERED_TRAINING_VALIDATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "classification": {
            "training_completed": (
                midpoint["checkpoint_steps"] == EXPECTED_MIDPOINT_STEPS
                and transfer["checkpoint_steps"] == EXPECTED_TRANSFER_STEPS
            ),
            "training_retry": False,
            "training_resume": False,
            "behavior_cells": 0,
            "midpoint_transfer": True,
            "full_gait_transfer": True,
            "correction_method": (
                "read-only CPU topology remap using the frozen CPU template"
            ),
        },
        "input_hashes": {
            **input_hashes,
            "hosted_preregistration": sha256(HOSTED_PREREGISTRATION),
            "t61_result": sha256(T61_RESULT),
            "package_contract": sha256(PACKAGE_CONTRACT),
            "launch_contract": sha256(LAUNCH_CONTRACT),
            "source_checkpoint": source_hash,
            "cpu_template": cpu_template_hash,
        },
        "stages": {
            "midpoint": {
                "checkpoints": [
                    {
                        "step": step(path),
                        "directory_sha256": midpoint[
                            "checkpoint_hashes"
                        ][step(path)],
                    }
                    for path in midpoint["checkpoints"]
                ],
                "onnx": midpoint["graph_rows"],
                "trained_checkpoints": midpoint_updates,
                "training_metric_evidence": midpoint_metrics,
            },
            "transfer": {
                "checkpoints": [
                    {
                        "step": step(path),
                        "directory_sha256": transfer[
                            "checkpoint_hashes"
                        ][step(path)],
                    }
                    for path in transfer["checkpoints"]
                ],
                "onnx": transfer["graph_rows"],
                "trained_checkpoints": transfer_updates,
                "training_metric_evidence": transfer_metrics,
            },
        },
        "authority": {
            "postexport_transform_preregistration_authorized": not failed,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T62 recovered training validation",
                "",
                f"- Status: `{result['status']}`",
                f"- Failed checks: `{failed}`",
                "- Exports: midpoint `0/final`; transfer `0/half/final`",
                "- All files cross-checked against hosted result and receipt",
                "- Read-only validation topology: `CPU`",
                "- Behavior/Gate5/robot authority: `0/0/0`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(result["status"])
    print(f"failed_checks={failed}")
    print(f"result_sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
