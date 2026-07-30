#!/usr/bin/env python3
"""Validate recovered T203 training on CPU before any behavior."""

from __future__ import annotations

import argparse
import json
import math
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
import run_t55_dynamic_single_support_cpu_contract as t55  # noqa: E402


ANALYSIS = ROOT / "outputs" / "analysis"
PREREGISTRATION = (
    ANALYSIS / "t203_predicted_roll_risk_hosted_preregistration.json"
)
CPU_SOURCE = ANALYSIS / "t202_predicted_roll_risk_cpu_result.json"
CPU_AUTHORITY = ANALYSIS / "t202b_metric_namespace_recovery_result.json"
PACKAGE_CONTRACT = (
    ANALYSIS / "t203_predicted_roll_risk_hosted_package_contract.json"
)
LAUNCH_CONTRACT = ANALYSIS / "t203_colab_cli_launch_contract.json"
OUTPUT = ANALYSIS / "t204_t203_recovered_training_validation.json"
MARKDOWN = ANALYSIS / "T204_T203_RECOVERED_TRAINING_VALIDATION_20260730.md"
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]
TRAINABLE_ACTOR = {"negative_adapter_location"}
COST_TAG = "eval/episode_cost/t202_predicted_roll_risk"
RISK_TAG = "eval/episode_t202/predicted_roll_risk_rad"
EXCESS_TAG = "eval/episode_t202/roll_risk_excess_rad"
ORIGINAL_REWARD_TAG = "eval/episode_t202/original_clipped_reward"


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
        name: value
        for name, value in deltas.items()
        if name.startswith("0/")
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


def finite_values(
    events: dict[str, list[dict[str, float | int]]],
    tag: str,
) -> list[float]:
    values = [float(row["value"]) for row in events.get(tag, [])]
    if not values or not all(math.isfinite(value) for value in values):
        return []
    return values


def sha256_json(value: Any) -> str:
    import hashlib

    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recovery-root", type=Path, required=True)
    parser.add_argument("--extracted-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T204: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T204 validation requires clean worktree")

    recovery_root = args.recovery_root.resolve()
    work = (
        args.extracted_root.resolve()
        / "t203_predicted_roll_risk_continuation"
    )
    training = work / "training"
    paths = {
        "hosted_result": recovery_root / "t203_result.json",
        "launch_receipt": recovery_root / "t203_launch_receipt.json",
        "recovery_archive": recovery_root / "t203_artifacts.tar.gz",
    }
    input_hashes = {name: sha256(path) for name, path in paths.items()}
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    cpu_source = json.loads(CPU_SOURCE.read_text(encoding="utf-8"))
    cpu_authority = json.loads(CPU_AUTHORITY.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE_CONTRACT.read_text(encoding="utf-8"))
    launch = json.loads(LAUNCH_CONTRACT.read_text(encoding="utf-8"))
    hosted = json.loads(paths["hosted_result"].read_text(encoding="utf-8"))
    receipt = json.loads(paths["launch_receipt"].read_text(encoding="utf-8"))
    source_path = Path(prereg["paths"]["source_checkpoint"]).resolve()
    expected_step_zero = Path(
        prereg["paths"]["expected_step_zero_raw"]
    ).resolve()
    cpu_topology = Path(
        cpu_source["source_remap"]["cpu_remap"]["path"]
    ).resolve()

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

    topology_tree = ocp.PyTreeCheckpointer().restore(str(cpu_topology))
    source_tree = restore_tree(source_path, topology_tree)
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
    t202_readback = (
        "T202_PREDICTED_ROLL_RISK="
        "horizon_s=0.08,envelope_rad=0.3541802655745987,"
        "scale=0.80177631665518045,"
        "objective=original_clipped_reward_minus_cost,"
        "deployment_graph=unchanged"
    )
    t98_readback = (
        "T98_HIDDEN_EXPERT_CONTINUATION="
        "strata=8,broad=1,isolated=7,gate=fixed_live_hidden,"
        "actor_updates=negative_adapter_location_only"
    )
    event_path = next(training.glob("events.out.tfevents*"))
    events = t55.all_scalar_events(event_path)
    metric_values = {
        "cost": finite_values(events, COST_TAG),
        "risk": finite_values(events, RISK_TAG),
        "excess": finite_values(events, EXCESS_TAG),
        "original_reward": finite_values(events, ORIGINAL_REWARD_TAG),
    }

    checks = {
        "t203_preregistration_green": (
            prereg["status"]
            == "PREREGISTERED_T203_PREDICTED_ROLL_RISK_HOSTED_CONTINUATION"
            and prereg["decision"]
            == "AUTHORIZE_ONE_HASH_FROZEN_T203_L4_CONTINUATION"
            and prereg["failed_checks"] == []
        ),
        "t202_cpu_authority_exact": (
            cpu_authority["status"]
            == "PASS_T202B_METRIC_NAMESPACE_RECOVERY"
            and cpu_authority["decision"]
            == (
                "EARN_T203_PREDICTED_ROLL_RISK_HOSTED_"
                "PREREGISTRATION_ONLY"
            )
            and cpu_authority["failed_checks"] == []
            and hosted["validation"]["input_hashes"]["recovery_result"]
            == sha256(CPU_AUTHORITY)
        ),
        "cpu_topology_and_source_frozen": (
            directory_sha256(cpu_topology)
            == cpu_source["source_remap"]["cpu_remap"]["sha256"]
            and directory_sha256(source_path)
            == prereg["input_hashes"]["source_checkpoint"]
        ),
        "package_and_launch_contracts_green": (
            package["status"]
            == "PASS_T203_PREDICTED_ROLL_RISK_HOSTED_PACKAGE"
            and package["failed_checks"] == []
            and launch["status"] == "PASS_T203_COLAB_CLI_LAUNCH_CONTRACT"
            and launch["failed_checks"] == []
        ),
        "hosted_artifact_passed_pending_cpu_validation": (
            hosted["status"]
            == "PASS_T203_TRAINING_ARTIFACT_PENDING_CPU_VALIDATION"
            and hosted["failed_checks"] == []
            and hosted["cpu_topology_validation_required"] is True
        ),
        "launch_receipt_complete": (
            receipt["status"] == "COMPLETED_T203_COLAB_LAUNCH"
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
        "preregistration_hash_matches_hosted": (
            hosted["validation"]["preregistration_sha256"]
            == sha256(PREREGISTRATION)
        ),
        "exact_local_exports": (
            checkpoint_steps == EXPECTED_STEPS
            and graph_steps == EXPECTED_STEPS
        ),
        "checkpoint_hashes_match_hosted_result": (
            checkpoint_hashes == hosted_checkpoint_hashes
        ),
        "onnx_hashes_match_hosted_result": graph_hashes == hosted_graph_hashes,
        "step_zero_tree_source_bit_exact": (
            zero_structure
            and max(zero_deltas.values(), default=0.0) == 0.0
        ),
        "step_zero_raw_onnx_byte_exact": (
            graph_hashes.get(0) == sha256(expected_step_zero)
            and graph_hashes.get(0)
            == prereg["input_hashes"]["expected_step_zero_raw"]
        ),
        "exact_t202_and_t98_readbacks": (
            t202_readback in log_text and t98_readback in log_text
        ),
        "hosted_roll_metrics_finite_three_exports": all(
            len(values) == 3 for values in metric_values.values()
        ),
        "hosted_roll_objective_exercised": (
            min(metric_values["risk"], default=0.0) > 0.0
            and max(metric_values["cost"], default=0.0) > 0.0
            and max(metric_values["excess"], default=0.0) > 0.0
            and min(metric_values["original_reward"], default=0.0) > 0.0
        ),
        "all_checkpoint_trees_finite": all(
            tree_finite(tree) for tree in trees
        ),
        "both_exports_only_update_head_and_critic": all(
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
        "cpu_only_validation": all(
            device.platform == "cpu" for device in jax.devices()
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis: dict[str, Any] = {
        "schema_version": (
            "open_duck.t204_t203_recovered_training_validation.v1"
        ),
        "status": (
            "PASS_T204_T203_RECOVERED_TRAINING_VALIDATION"
            if not failed
            else "HOLD_T204_T203_RECOVERED_TRAINING_VALIDATION"
        ),
        "decision": (
            "EARN_T205_T203_POSTEXPORT_COMPOSITION_PREREGISTRATION_ONLY"
            if not failed
            else "NO_BEHAVIOR_EVALUATION"
        ),
        "checks": checks,
        "failed_checks": failed,
        "input_hashes": {
            **input_hashes,
            "t203_preregistration": sha256(PREREGISTRATION),
            "t202_cpu_authority": sha256(CPU_AUTHORITY),
            "t202_cpu_source": sha256(CPU_SOURCE),
            "package_contract": sha256(PACKAGE_CONTRACT),
            "launch_contract": sha256(LAUNCH_CONTRACT),
            "source_checkpoint": directory_sha256(source_path),
            "cpu_topology": directory_sha256(cpu_topology),
            "event_file": sha256(event_path),
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
        "roll_metrics": metric_values,
        "classification": {
            "training_completed": checkpoint_steps == EXPECTED_STEPS,
            "training_retry": False,
            "same_run_resume": False,
            "behavior_cells": 0,
            "actor_update_scope": "negative_adapter_location_only",
            "body_configuration_strata": 8,
            "predicted_roll_objective": "outside_reward_clip",
            "support_objective": False,
            "hosted_wall_seconds": hosted["wall_seconds"],
        },
        "authority": {
            "postexport_composition_preregistration_authorized": not failed,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    value = {**basis, "result_sha256": sha256_json(basis)}
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T204 T203 recovered training validation\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Exports: `0 / 1,003,520 / 2,007,040`\n"
        "- T202 risk/cost/excess metrics: finite and exercised\n"
        "- Actor scope: existing negative adapter location head only\n"
        "- Mature actor / normalizer: bit-exact / bit-exact\n"
        "- Behavior / Gate 5 / robot authority: `0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
