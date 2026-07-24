#!/usr/bin/env python3
"""Validate recovered V122 outputs on an explicit CPU topology."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys

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


ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v122_hosted_preregistration.json"
PACKAGE_CONTRACT = ANALYSIS / "winner_v122_hosted_package_contract.json"
TRANSPORT = ANALYSIS / "winner_v122_upload_transport_correction.json"
LAUNCH_CONTRACT = (
    ANALYSIS / "winner_v122b_chunked_colab_launch_contract.json"
)
OUTPUT = ANALYSIS / "winner_v122_recovered_training_validation.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V122_RECOVERED_TRAINING_VALIDATION_20260724.md"
)
EXPECTED = {
    "preregistration": (
        "fbbd796fdbf30d0e634ea712ceadd2946af035037bf6481f4ef3e1d0caed8c8e"
    ),
    "package_contract": (
        "ac313412a362d33d1ed3803777aa0e0a45fca6c4a45cc69b235584a40107926d"
    ),
    "transport_correction": (
        "1f2816b15c18eda6cb9afc918334a8d10498905b67e0b7fffa843e6e8b7df8fb"
    ),
    "launch_contract": (
        "d9197a637f3dfe83ae858931195d13d120a749d4ff401addd630a5524beec4bc"
    ),
    "hosted_result": (
        "8afec0b928c22010d98b5536e45b605bd231f5470e8d74817bc5ac495403df93"
    ),
    "launch_receipt": (
        "ccf76707c99530abac8aee9d2375c483213f825d51aca75ac71f142960406cda"
    ),
    "recovery_archive": (
        "4cad20c1498f40eebfc6361d3a2aa737d090d485a4045d1d893959f246bf2e59"
    ),
    "source_checkpoint": (
        "6f2d9856b5ab674f9f20f04c46be6dc00adc5eabc31826f16b4743c5172dfad8"
    ),
    "cpu_template": (
        "16a867c653476d6829ddaf400e5f02fc21658a78d3efc5ddfd167cc497f3ac83"
    ),
}
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recovery-root", type=Path, required=True)
    parser.add_argument("--extracted-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V122: {path}")
    recovery = args.recovery_root.resolve()
    work = (
        args.extracted_root.resolve()
        / "winner_v122_episode_peak_continuation"
    )
    training = work / "training"
    source = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    paths = {
        "hosted_result": recovery / "winner_v122_result.json",
        "launch_receipt": recovery / "winner_v122_launch_receipt.json",
        "recovery_archive": recovery / "winner_v122_artifacts.tar.gz",
    }
    input_hashes = {
        "preregistration": sha256(PREREGISTRATION),
        "package_contract": sha256(PACKAGE_CONTRACT),
        "transport_correction": sha256(TRANSPORT),
        "launch_contract": sha256(LAUNCH_CONTRACT),
        **{name: sha256(path) for name, path in paths.items()},
        "source_checkpoint": directory_sha256(source),
        "cpu_template": directory_sha256(cpu_template),
    }
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    package_contract = json.loads(
        PACKAGE_CONTRACT.read_text(encoding="utf-8")
    )
    transport = json.loads(TRANSPORT.read_text(encoding="utf-8"))
    launch_contract = json.loads(
        LAUNCH_CONTRACT.read_text(encoding="utf-8")
    )
    hosted = json.loads(
        paths["hosted_result"].read_text(encoding="utf-8")
    )
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
                "every_policy_leaf_updated": len(policy_deltas) == 15
                and all(value > 0.0 for value in policy_deltas.values()),
            }
        )

    event_file = next(training.glob("events.out.tfevents*"))
    scalars = event_scalars(event_file)
    metric_tags = (
        "eval/episode_cost/episode_peak_torque_increment",
        "eval/episode_cost/tracking_tail_exceedance",
        "eval/episode_reward",
        "eval/avg_episode_length",
        "training/total_loss",
        "training/policy_loss",
        "training/v_loss",
        "training/kl_mean",
    )
    metric_evidence = {tag: scalars.get(tag, []) for tag in metric_tags}
    eval_tags = metric_tags[:4]
    training_tags = metric_tags[4:]
    metric_steps_exact = all(
        [row["step"] for row in metric_evidence[tag]] == EXPECTED_STEPS
        for tag in eval_tags
    ) and all(
        [row["step"] for row in metric_evidence[tag]]
        == EXPECTED_STEPS[1:]
        for tag in training_tags
    )
    metric_values_finite = all(
        math.isfinite(row["value"])
        for rows in metric_evidence.values()
        for row in rows
    )
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "preregistration_and_package_pass": (
            prereg.get("status")
            == "PREREGISTERED_WINNER_V122_HOSTED_CONTINUATION"
            and package_contract.get("status")
            == "PASS_WINNER_V122_HOSTED_PACKAGE"
        ),
        "transport_correction_and_launch_pass": (
            transport.get("status")
            == "PASS_WINNER_V122_UPLOAD_TRANSPORT_CORRECTION"
            and launch_contract.get("status")
            == "PASS_WINNER_V122B_CHUNKED_COLAB_LAUNCH_CONTRACT"
        ),
        "hosted_artifact_passed_pending_cpu_validation": (
            hosted.get("status")
            == "PASS_WINNER_V122_TRAINING_ARTIFACT_PENDING_CPU_TOPOLOGY_VALIDATION"
            and hosted.get("failed_checks") == []
            and hosted.get("checkpoint_steps") == EXPECTED_STEPS
            and hosted.get("onnx_steps") == EXPECTED_STEPS
            and hosted.get("cpu_topology_validation_required") is True
        ),
        "launch_receipt_complete_no_retry": (
            receipt.get("status") == "COMPLETED_WINNER_V122_COLAB_LAUNCH"
            and receipt.get("returncode") == 0
            and receipt.get("retry") is False
            and receipt.get("resume") is False
            and receipt.get("robot_or_rdk_access") is False
        ),
        "result_hash_matches_receipt": (
            receipt.get("output_json_sha256")
            == input_hashes["hosted_result"]
        ),
        "archive_hash_matches_result_and_receipt": (
            hosted.get("artifact", {}).get("sha256")
            == input_hashes["recovery_archive"]
            and receipt.get("output_archive_sha256")
            == input_hashes["recovery_archive"]
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
        "schema_version": "winner_v122.recovered_training_validation.v1",
        "status": (
            "PASS_WINNER_V122_RECOVERED_TRAINING_VALIDATION"
            if not failed
            else "HOLD_WINNER_V122_RECOVERED_TRAINING_VALIDATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "classification": {
            "training_completed": checkpoint_steps == EXPECTED_STEPS,
            "training_retry": False,
            "training_resume": False,
            "prelaunch_transport_correction": True,
            "behavior_cells": 0,
            "episode_peak_objective_trained": True,
        },
        "input_hashes": input_hashes,
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
            "deployment_transform_preregistration_authorized": not failed,
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
        "# Winner-v122 recovered training validation\n\n"
        f"Status: `{result['status']}`\n\n"
        f"Failed checks: `{failed}`\n\n"
        "Recovered artifacts are hash-cross-checked and restored read-only "
        "on CPU. A pass authorizes only the exact V121 deployment transform; "
        "no behavior, Gate 5, RDK-X5, or robot access.\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"result_sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
