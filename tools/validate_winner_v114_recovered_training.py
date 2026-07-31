#!/usr/bin/env python3
"""Validate recovered V114 outputs on an explicit CPU topology."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

from flax.training import orbax_utils
import jax
from orbax import checkpoint as ocp

from validate_winner_v112_recovered_training import (
    directory_sha256,
    event_scalars,
    onnx_contract,
    sha256,
    step,
    tree_deltas,
    tree_finite,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = (
    ANALYSIS / "winner_v114_linear_torque_hosted_preregistration.json"
)
PACKAGE_CONTRACT = (
    ANALYSIS / "winner_v114_linear_torque_hosted_package_contract.json"
)
OUTPUT = ANALYSIS / "winner_v114_recovered_training_validation.json"
MARKDOWN = ANALYSIS / "WINNER_V114_RECOVERED_TRAINING_VALIDATION_20260724.md"
PREREGISTRATION_SHA256 = (
    "a840c7ac2aaf5fae869c37b0c5735edb75570081ad1b93ef906316649c04de4e"
)
PACKAGE_CONTRACT_SHA256 = (
    "3e42930e1db70b5de3784fc1bc7720169aecfb03999c1f436bf86aa73859ad4d"
)
SOURCE_CHECKPOINT_SHA256 = (
    "d63309e0e0524d684813d1bf068e8642b21d2e829653d7716949614350f0423c"
)
CPU_TEMPLATE_SHA256 = (
    "70d589520d4280c9e2f276d45a3f12ccc90aa25a0691b5bd462cbde464419bbd"
)
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recovery-root", type=Path, required=True)
    parser.add_argument("--extracted-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    args = parser.parse_args()
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite V114 validation")
    recovery = args.recovery_root.resolve()
    work = (
        args.extracted_root.resolve()
        / "winner_v114_linear_torque_continuation"
    )
    training = work / "training"
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    paths = {
        "hosted_result": recovery / "winner_v114_result.json",
        "launch_receipt": recovery / "winner_v114_launch_receipt.json",
        "recovery_archive": recovery / "winner_v114_artifacts.tar.gz",
    }
    input_hashes = {name: sha256(path) for name, path in paths.items()}
    source_hash = directory_sha256(source)
    cpu_template_hash = directory_sha256(cpu_template)
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    package_contract = json.loads(
        PACKAGE_CONTRACT.read_text(encoding="utf-8")
    )
    hosted = json.loads(paths["hosted_result"].read_text(encoding="utf-8"))
    receipt = json.loads(
        paths["launch_receipt"].read_text(encoding="utf-8")
    )
    checkpoints = sorted(
        (path for path in training.iterdir() if path.is_dir()), key=step
    )
    graphs = sorted(training.glob("*.onnx"), key=step)
    checkpoint_steps = [step(path) for path in checkpoints]
    onnx_steps = [step(path) for path in graphs]
    checkpoint_hashes = {
        step(path): directory_sha256(path) for path in checkpoints
    }
    graph_rows = [onnx_contract(path) for path in graphs]
    hosted_checkpoint_hashes = {
        int(row["step"]): row["directory_sha256"]
        for row in hosted["checkpoints"]
    }
    hosted_onnx_hashes = {
        int(row["step"]): row["sha256"] for row in hosted["onnx"]
    }
    observed_onnx_hashes = {
        row["step"]: row["sha256"] for row in graph_rows
    }

    checkpointer = ocp.PyTreeCheckpointer()
    topology_template = checkpointer.restore(str(cpu_template))
    source_restore_args = orbax_utils.restore_args_from_target(
        topology_template
    )
    source_tree = checkpointer.restore(
        str(source),
        item=topology_template,
        restore_args=source_restore_args,
    )
    checkpoint_restore_args = orbax_utils.restore_args_from_target(
        source_tree
    )
    trees = [
        checkpointer.restore(
            str(path),
            item=source_tree,
            restore_args=checkpoint_restore_args,
        )
        for path in checkpoints
    ]
    initial_structure, initial_deltas = tree_deltas(source_tree, trees[0])
    trained_rows = []
    for path, tree in zip(checkpoints[1:], trees[1:], strict=True):
        structure, deltas = tree_deltas(trees[0], tree)
        policy_deltas = {
            name: value
            for name, value in deltas.items()
            if name.startswith("1/params/")
        }
        trained_rows.append(
            {
                "step": step(path),
                "structure_exact": structure,
                "tree_finite": tree_finite(tree),
                "policy_leaf_deltas": policy_deltas,
                "every_policy_leaf_updated": bool(policy_deltas)
                and all(value > 0.0 for value in policy_deltas.values()),
            }
        )

    event_file = next(training.glob("events.out.tfevents*"))
    scalars = event_scalars(event_file)
    metric_tags = (
        "eval/episode_cost/linear_peak_torque_exceedance",
        "eval/episode_cost/tracking_tail_exceedance",
        "eval/episode_reward",
        "eval/avg_episode_length",
    )
    metric_evidence = {tag: scalars.get(tag, []) for tag in metric_tags}
    metric_steps_exact = all(
        [row["step"] for row in rows] == EXPECTED_STEPS
        for rows in metric_evidence.values()
    )
    metric_values_finite = all(
        math.isfinite(row["value"])
        for rows in metric_evidence.values()
        for row in rows
    )
    result_sha = input_hashes["hosted_result"]
    archive_sha = input_hashes["recovery_archive"]
    checks = {
        "preregistration_exact": (
            sha256(PREREGISTRATION) == PREREGISTRATION_SHA256
            and prereg.get("status")
            == "PREREGISTERED_WINNER_V114_LINEAR_TORQUE_HOSTED_CONTINUATION"
        ),
        "package_contract_exact": (
            sha256(PACKAGE_CONTRACT) == PACKAGE_CONTRACT_SHA256
            and package_contract.get("status")
            == "PASS_WINNER_V114_LINEAR_TORQUE_HOSTED_PACKAGE"
        ),
        "source_checkpoint_exact": (
            source_hash == SOURCE_CHECKPOINT_SHA256
        ),
        "cpu_template_exact": cpu_template_hash == CPU_TEMPLATE_SHA256,
        "hosted_artifact_passed_pending_cpu_validation": (
            hosted.get("status")
            == "PASS_WINNER_V114_TRAINING_ARTIFACT_PENDING_CPU_TOPOLOGY_VALIDATION"
            and hosted.get("failed_checks") == []
            and hosted.get("checkpoint_steps") == EXPECTED_STEPS
            and hosted.get("onnx_steps") == EXPECTED_STEPS
            and hosted.get("cpu_topology_validation_required") is True
        ),
        "hosted_inputs_match_preregistration": (
            hosted.get("validation", {}).get("input_hashes")
            == prereg.get("input_hashes")
            and hosted.get("validation", {}).get("preregistration_sha256")
            == PREREGISTRATION_SHA256
        ),
        "launch_receipt_complete": (
            receipt.get("status") == "COMPLETED_WINNER_V114_COLAB_LAUNCH"
            and receipt.get("returncode") == 0
            and receipt.get("retry") is False
            and receipt.get("resume") is False
            and receipt.get("robot_or_rdk_access") is False
        ),
        "result_hash_matches_receipt": (
            receipt.get("output_json_sha256") == result_sha
        ),
        "archive_hash_matches_result_and_receipt": (
            hosted.get("artifact", {}).get("sha256") == archive_sha
            and receipt.get("output_archive_sha256") == archive_sha
            and hosted.get("artifact", {}).get("bytes")
            == paths["recovery_archive"].stat().st_size
        ),
        "local_exact_exports": checkpoint_steps == EXPECTED_STEPS
        and onnx_steps == EXPECTED_STEPS,
        "checkpoint_hashes_match_hosted_result": (
            checkpoint_hashes == hosted_checkpoint_hashes
        ),
        "onnx_hashes_match_hosted_result": (
            observed_onnx_hashes == hosted_onnx_hashes
        ),
        "step_zero_source_restore_structure_exact": initial_structure,
        "step_zero_source_parameters_bit_exact": max(
            initial_deltas.values(), default=0.0
        )
        == 0.0,
        "all_checkpoint_trees_finite": tree_finite(trees[0])
        and all(row["tree_finite"] for row in trained_rows),
        "all_postupdate_structures_exact": all(
            row["structure_exact"] for row in trained_rows
        ),
        "every_policy_leaf_updated_at_both_checkpoints": all(
            row["every_policy_leaf_updated"] for row in trained_rows
        ),
        "all_onnx_contracts_pass": all(
            row["abi_exact"]
            and row["initializers_finite"]
            and row["cpu_provider_exact"]
            and row["chain_256_finite"]
            for row in graph_rows
        ),
        "training_metrics_have_exact_export_steps": metric_steps_exact,
        "training_metrics_all_finite": metric_values_finite,
        "cpu_only_validation": all(
            device.platform == "cpu" for device in jax.devices()
        ),
        "formal_behavior_cells_zero": (
            hosted.get("formal_behavior_cells_executed") == 0
        ),
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v114.recovered_training_validation.v1",
        "status": (
            "PASS_WINNER_V114_RECOVERED_TRAINING_VALIDATION"
            if not failed
            else "HOLD_WINNER_V114_RECOVERED_TRAINING_VALIDATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "classification": {
            "training_completed": checkpoint_steps == EXPECTED_STEPS,
            "training_retry": False,
            "training_resume": False,
            "behavior_cells": 0,
            "correction_method": (
                "read-only CPU topology remap using the exact V111 CPU tree "
                "as the source restore template and exact V112 final as the "
                "checkpoint restore template"
            ),
        },
        "input_hashes": {
            **input_hashes,
            "preregistration": sha256(PREREGISTRATION),
            "package_contract": sha256(PACKAGE_CONTRACT),
            "source_checkpoint": source_hash,
            "cpu_template": cpu_template_hash,
        },
        "checkpoints": [
            {
                "step": step(path),
                "directory_sha256": checkpoint_hashes[step(path)],
            }
            for path in checkpoints
        ],
        "onnx": graph_rows,
        "trained_checkpoints": trained_rows,
        "training_metric_evidence": metric_evidence,
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
    )
    MARKDOWN.write_text(
        "# Winner-v114 recovered training validation\n\n"
        f"Status: `{result['status']}`\n\n"
        f"Failed checks: `{failed}`\n\n"
        "The exact recovered artifacts were cross-checked against the hosted "
        "result and launch receipt, then restored read-only on the explicit "
        "CPU topology. A pass authorizes only the frozen post-export "
        "transform preregistration; it does not authorize behavior selection,"
        " Gate 5, robot access, torque, or motion.\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"result_sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
