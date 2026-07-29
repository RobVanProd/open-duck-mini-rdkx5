#!/usr/bin/env python3
"""Validate recovered T154 training on CPU before any behavior screen."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
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
    onnx_contract,
    sha256,
    step,
    tree_deltas,
    tree_finite,
)


ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t154_positive_only_expert_hosted_preregistration.json"
)
CPU_RESULT = ANALYSIS / "t153_positive_only_expert_cpu_result.json"
PACKAGE_CONTRACT = (
    ANALYSIS / "t154_positive_only_expert_hosted_package_contract.json"
)
LAUNCH_CONTRACT = ANALYSIS / "t154_colab_cli_launch_contract.json"
OUTPUT = ANALYSIS / "t155_t154_recovered_training_validation.json"
MARKDOWN = (
    ANALYSIS / "T155_T154_RECOVERED_TRAINING_VALIDATION_20260729.md"
)
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]
TRAINABLE_ACTOR = {"negative_adapter_location"}
CPU_TOPOLOGY = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t153_positive_only_expert_cpu_v1/t100c_half_cpu_remap"
)


def restore_tree(path: Path, template: Any) -> Any:
    return ocp.PyTreeCheckpointer().restore(
        str(path),
        item=template,
        restore_args=orbax_utils.restore_args_from_target(template),
    )


def split_deltas(source: Any, target: Any) -> dict[str, Any]:
    structure, deltas = tree_deltas(source, target)
    policy = {
        name: value
        for name, value in deltas.items()
        if name.startswith("1/params/")
    }
    trainable = {
        name: value
        for name, value in policy.items()
        if any(group in name for group in TRAINABLE_ACTOR)
    }
    frozen = {
        name: value for name, value in policy.items() if name not in trainable
    }
    normalizer = {
        name: value for name, value in deltas.items() if name.startswith("0/")
    }
    critic = {
        name: value
        for name, value in deltas.items()
        if name.startswith("2/params/")
    }
    return {
        "structure_exact": structure,
        "tree_finite": tree_finite(target),
        "trainable_actor_leaf_deltas": trainable,
        "frozen_mature_actor_leaf_deltas": frozen,
        "normalizer_leaf_deltas": normalizer,
        "critic_leaf_deltas": critic,
        "every_trainable_actor_leaf_updated": (
            len(trainable) == 2
            and all(value > 0.0 for value in trainable.values())
        ),
        "every_mature_actor_leaf_exact": (
            bool(frozen) and all(value == 0.0 for value in frozen.values())
        ),
        "normalizer_exact": (
            bool(normalizer)
            and all(value == 0.0 for value in normalizer.values())
        ),
        "every_critic_leaf_updated": (
            bool(critic) and all(value > 0.0 for value in critic.values())
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recovery-root", type=Path, required=True)
    parser.add_argument("--extracted-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T155: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T155 validation requires clean worktree")

    recovery_root = args.recovery_root.resolve()
    work = (
        args.extracted_root.resolve()
        / "t154_positive_only_expert_continuation"
    )
    training = work / "training"
    paths = {
        "hosted_result": recovery_root / "t154_result.json",
        "launch_receipt": recovery_root / "t154_launch_receipt.json",
        "recovery_archive": recovery_root / "t154_artifacts.tar.gz",
    }
    input_hashes = {name: sha256(path) for name, path in paths.items()}
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    cpu = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE_CONTRACT.read_text(encoding="utf-8"))
    launch = json.loads(LAUNCH_CONTRACT.read_text(encoding="utf-8"))
    hosted = json.loads(paths["hosted_result"].read_text(encoding="utf-8"))
    receipt = json.loads(paths["launch_receipt"].read_text(encoding="utf-8"))
    source_path = Path(prereg["paths"]["source_checkpoint"]).resolve()
    checkpoints = sorted(
        (path for path in training.iterdir() if path.is_dir()), key=step
    )
    graphs = sorted(training.glob("*.onnx"), key=step)
    checkpoint_steps = [step(path) for path in checkpoints]
    graph_steps = [step(path) for path in graphs]
    checkpoint_hashes = {
        step(path): directory_sha256(path) for path in checkpoints
    }
    graph_rows = [onnx_contract(path) for path in graphs]
    graph_hashes = {int(row["step"]): row["sha256"] for row in graph_rows}

    cpu_topology = ocp.PyTreeCheckpointer().restore(str(CPU_TOPOLOGY))
    source_tree = restore_tree(source_path, cpu_topology)
    trees = [restore_tree(path, source_tree) for path in checkpoints]
    zero_structure, zero_deltas = tree_deltas(source_tree, trees[0])
    update_rows = [
        {"step": step_value, **split_deltas(trees[0], tree)}
        for step_value, tree in zip(
            EXPECTED_STEPS[1:], trees[1:], strict=True
        )
    ]
    hosted_checkpoint_hashes = {
        int(row["step"]): row["directory_sha256"]
        for row in hosted["checkpoints"]
    }
    hosted_graph_hashes = {
        int(row["step"]): row["sha256"] for row in hosted["onnx"]
    }
    log_text = (work / "training.log").read_text(
        encoding="utf-8", errors="replace"
    )
    readback = (
        "T98_HIDDEN_EXPERT_CONTINUATION="
        "strata=1,exact=torso_com_x_pos,offset_m=+0.05,"
        "gate=always_on,"
        "actor_updates=isolated_positive_expert_slot_only"
    )
    checks = {
        "t154_preregistration_green": (
            prereg["status"]
            == "PREREGISTERED_T154_POSITIVE_ONLY_EXPERT_HOSTED_CONTINUATION"
            and prereg["failed_checks"] == []
        ),
        "t153_cpu_authority_exact": (
            cpu["status"]
            == "PASS_T153_POSITIVE_ONLY_EXPERT_CPU_CONTRACT"
            and cpu["failed_checks"] == []
            and hosted["validation"]["input_hashes"]["cpu_result"]
            == sha256(CPU_RESULT)
        ),
        "cpu_topology_is_frozen_t153_remap": (
            CPU_TOPOLOGY.resolve()
            == Path(cpu["source_remap"]["cpu_remap"]["path"]).resolve()
            and directory_sha256(CPU_TOPOLOGY)
            == cpu["source_remap"]["cpu_remap"]["sha256"]
        ),
        "package_and_launch_contracts_green": (
            package["status"]
            == "PASS_T154_POSITIVE_ONLY_EXPERT_HOSTED_PACKAGE"
            and package["failed_checks"] == []
            and launch["status"] == "PASS_T154_COLAB_CLI_LAUNCH_CONTRACT"
            and launch["failed_checks"] == []
        ),
        "hosted_artifact_passed_pending_cpu_validation": (
            hosted["status"]
            == "PASS_T154_TRAINING_ARTIFACT_PENDING_CPU_VALIDATION"
            and hosted["failed_checks"] == []
            and hosted["cpu_topology_validation_required"] is True
        ),
        "launch_receipt_complete": (
            receipt["status"] == "COMPLETED_T154_COLAB_LAUNCH"
            and receipt["returncode"] == 0
            and receipt["retry"] is False
            and receipt["same_run_resume"] is False
            and receipt["robot_or_rdk_access"] is False
        ),
        "result_hash_matches_receipt": (
            receipt["output_json_sha256"] == input_hashes["hosted_result"]
        ),
        "archive_hash_matches_result_and_receipt": (
            hosted["artifact"]["sha256"] == input_hashes["recovery_archive"]
            and receipt["output_archive_sha256"]
            == input_hashes["recovery_archive"]
            and hosted["artifact"]["bytes"]
            == paths["recovery_archive"].stat().st_size
        ),
        "exact_local_exports": (
            checkpoint_steps == EXPECTED_STEPS
            and graph_steps == EXPECTED_STEPS
        ),
        "checkpoint_hashes_match_hosted_result": (
            checkpoint_hashes == hosted_checkpoint_hashes
        ),
        "onnx_hashes_match_hosted_result": graph_hashes == hosted_graph_hashes,
        "source_checkpoint_exact": (
            directory_sha256(source_path)
            == prereg["input_hashes"]["source_checkpoint"]
        ),
        "step_zero_tree_source_bit_exact": (
            zero_structure
            and max(zero_deltas.values(), default=0.0) == 0.0
        ),
        "step_zero_raw_matches_cpu_contract_export": (
            graph_hashes.get(0)
            == cpu["training"]["graphs"]["0"]["receipt"]["sha256"]
            and graph_hashes.get(0)
            == hosted_graph_hashes.get(0)
        ),
        "exact_positive_readback": readback in log_text,
        "all_checkpoint_trees_finite": all(tree_finite(tree) for tree in trees),
        "both_exports_only_update_expert_and_critic": all(
            row["structure_exact"]
            and row["tree_finite"]
            and row["every_trainable_actor_leaf_updated"]
            and row["every_mature_actor_leaf_exact"]
            and row["normalizer_exact"]
            and row["every_critic_leaf_updated"]
            for row in update_rows
        ),
        "all_onnx_contracts_pass": all(
            row["abi_exact"]
            and row["initializers_finite"]
            and row["cpu_provider_exact"]
            and row["chain_256_finite"]
            for row in graph_rows
        ),
        "formal_behavior_cells_zero": (
            hosted["formal_behavior_cells_executed"] == 0
        ),
        "original_nominal_negative_graphs_unchanged": all(
            Path(item["path"]).is_file()
            and Path(item["path"]).stat().st_size == item["bytes"]
            and sha256(Path(item["path"])) == item["sha256"]
            for item in cpu["preserved_deployments"].values()
        ),
        "cpu_only_validation": all(
            device.platform == "cpu" for device in jax.devices()
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, value in checks.items() if not value)
    result = {
        "schema_version": (
            "open_duck.t155_t154_recovered_training_validation.v1"
        ),
        "status": (
            "PASS_T155_T154_RECOVERED_TRAINING_VALIDATION"
            if not failed
            else "HOLD_T155_T154_RECOVERED_TRAINING_VALIDATION"
        ),
        "decision": (
            "EARN_T156_POSITIVE_EXPERT_THREE_WAY_ROUTER_"
            "PREREGISTRATION_ONLY"
            if not failed
            else "NO_BEHAVIOR_EVALUATION"
        ),
        "checks": checks,
        "failed_checks": failed,
        "input_hashes": {
            **input_hashes,
            "t154_preregistration": sha256(PREREGISTRATION),
            "cpu_result": sha256(CPU_RESULT),
            "package_contract": sha256(PACKAGE_CONTRACT),
            "launch_contract": sha256(LAUNCH_CONTRACT),
            "source_checkpoint": directory_sha256(source_path),
            "cpu_topology": directory_sha256(CPU_TOPOLOGY),
        },
        "exports": {
            "checkpoints": [
                {
                    "step": step(path),
                    "path": str(path),
                    "directory_sha256": checkpoint_hashes[step(path)],
                }
                for path in checkpoints
            ],
            "onnx": graph_rows,
            "updates": update_rows,
        },
        "classification": {
            "training_completed": checkpoint_steps == EXPECTED_STEPS,
            "training_retry": False,
            "same_run_resume": False,
            "behavior_cells": 0,
            "actor_update_scope": "negative_adapter_location_only",
            "deployment_role": "positive_adapter_location",
            "forward_path": "isolated_positive_expert_slot_always_on",
            "body_configuration_strata": 1,
            "exact_torso_com_offset_m": [0.05, 0.0, 0.0],
            "hosted_wall_seconds": hosted["wall_seconds"],
        },
        "authority": {
            "postexport_preregistration_authorized": not failed,
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
        "# T155 T154 recovered training validation\n\n"
        f"- Status: `{result['status']}`\n"
        f"- Decision: `{result['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Exports: 0 / 1,003,520 / 2,007,040\n"
        "- Actor scope: isolated linear positive expert slot only\n"
        "- Mature actor / normalizer: bit-exact / bit-exact\n"
        "- Behavior / Gate 5 / robot authority: 0 / 0 / 0\n",
        encoding="utf-8",
        newline="\n",
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
