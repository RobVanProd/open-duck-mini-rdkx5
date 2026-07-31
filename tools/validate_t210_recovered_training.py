#!/usr/bin/env python3
"""Validate recovered T210 training on CPU before any behavior."""

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
    ANALYSIS / "t210_dual_roll_cost_hosted_preregistration.json"
)
CPU_RESULT = ANALYSIS / "t209_dual_roll_cost_cpu_result.json"
T204_VALIDATION = (
    ANALYSIS / "t204_t203_recovered_training_validation.json"
)
T208_SELECTION = ANALYSIS / "t208_t203_persistence_autopsy_result.json"
PACKAGE_CONTRACT = (
    ANALYSIS / "t210_dual_roll_cost_hosted_package_contract.json"
)
LAUNCH_CONTRACT = ANALYSIS / "t210_colab_cli_launch_contract.json"
OUTPUT = ANALYSIS / "t211_t210_recovered_training_validation.json"
MARKDOWN = ANALYSIS / "T211_T210_RECOVERED_TRAINING_VALIDATION_20260730.md"
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]
TRAINABLE_ACTOR = {"negative_adapter_location"}
EVAL_TAGS = (
    "eval/avg_episode_length",
    "eval/episode_cost/t209_predicted_roll_risk",
    "eval/episode_cost/winner_v127_dense_torque_exceedance",
    "eval/episode_reward",
    "eval/episode_t209/original_clipped_reward",
    "eval/episode_t209/predicted_roll_risk_rad",
    "eval/episode_t209/roll_risk_excess_rad",
)
TRAINING_TAGS = (
    "training/cost_advantage_mean",
    "training/cost_advantage_std",
    "training/cost_v_loss",
    "training/dense_cost_max",
    "training/dense_cost_mean",
    "training/dual_lambda",
    "training/policy_loss",
    "training/reward_advantage_mean",
    "training/reward_advantage_std",
    "training/total_loss",
    "training/v_loss",
    "training/winner_v127_batch_episode_cost",
    "training/winner_v127_dual_eta",
    "training/winner_v127_dual_initial_cost",
    "training/winner_v127_dual_lambda_after_update",
)


def restore_tree(path: Path, template: Any) -> Any:
    return ocp.PyTreeCheckpointer().restore(
        str(path),
        item=template,
        restore_args=orbax_utils.restore_args_from_target(template),
    )


def cost_step(path: Path) -> int:
    return int(
        path.name.split("_v127_cost_value", 1)[0].rsplit("_", 1)[1]
    )


def split_policy_deltas(source: Any, target: Any) -> dict[str, Any]:
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
    reward_critic = {
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
        "reward_critic_leaf_deltas": reward_critic,
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
        "every_reward_critic_leaf_updated": (
            bool(reward_critic)
            and all(value > 0.0 for value in reward_critic.values())
        ),
    }


def cost_tree_deltas(source: Any, target: Any) -> dict[str, Any]:
    structure, deltas = tree_deltas(source, target)
    return {
        "structure_exact": structure,
        "tree_finite": tree_finite(target),
        "leaf_deltas": deltas,
        "every_leaf_updated": (
            bool(deltas) and all(value > 0.0 for value in deltas.values())
        ),
    }


def finite_metric_rows(
    events: dict[str, list[dict[str, float | int]]],
    tags: tuple[str, ...],
) -> dict[str, list[dict[str, float | int]]]:
    rows = {tag: events.get(tag, []) for tag in tags}
    if not all(
        values
        and all(math.isfinite(float(item["value"])) for item in values)
        for values in rows.values()
    ):
        return {}
    return rows


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
            raise FileExistsError(f"refusing to overwrite T211: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T211 validation requires clean worktree")

    recovery_root = args.recovery_root.resolve()
    work = args.extracted_root.resolve() / "t210_dual_roll_cost_continuation"
    training = work / "training"
    paths = {
        "hosted_result": recovery_root / "t210_result.json",
        "launch_receipt": recovery_root / "t210_launch_receipt.json",
        "recovery_archive": recovery_root / "t210_artifacts.tar.gz",
    }
    input_hashes = {name: sha256(path) for name, path in paths.items()}
    prereg = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    cpu = json.loads(CPU_RESULT.read_text(encoding="utf-8"))
    t204 = json.loads(T204_VALIDATION.read_text(encoding="utf-8"))
    t208 = json.loads(T208_SELECTION.read_text(encoding="utf-8"))
    package = json.loads(PACKAGE_CONTRACT.read_text(encoding="utf-8"))
    launch = json.loads(LAUNCH_CONTRACT.read_text(encoding="utf-8"))
    hosted = json.loads(paths["hosted_result"].read_text(encoding="utf-8"))
    receipt = json.loads(paths["launch_receipt"].read_text(encoding="utf-8"))

    source_path = Path(prereg["paths"]["source_checkpoint"]).resolve()
    expected_step_zero = Path(
        prereg["paths"]["expected_step_zero_raw"]
    ).resolve()
    policy_cpu_template_path = Path(
        cpu["source_remap"]["cpu_remap"]["path"]
    ).resolve()
    cost_cpu_template_path = Path(
        cpu["training"]["cost_checkpoints"]["0"]["path"]
    ).resolve()

    policy_paths = sorted(
        (
            path
            for path in training.iterdir()
            if path.is_dir() and "_v127_cost_value" not in path.name
        ),
        key=step,
    )
    cost_paths = sorted(training.glob("*_v127_cost_value"), key=cost_step)
    graph_paths = sorted(training.glob("*.onnx"), key=step)
    aux_paths = sorted(training.glob("*_v127_aux.json"))
    policy_by_step = {step(path): path for path in policy_paths}
    cost_by_step = {cost_step(path): path for path in cost_paths}
    graph_by_step = {step(path): path for path in graph_paths}
    aux_by_step = {
        int(json.loads(path.read_text(encoding="utf-8"))["step"]): path
        for path in aux_paths
    }
    policy_hashes = {
        value: directory_sha256(path)
        for value, path in policy_by_step.items()
    }
    cost_hashes = {
        value: directory_sha256(path)
        for value, path in cost_by_step.items()
    }
    graph_rows = {
        value: onnx_contract(path)
        for value, path in graph_by_step.items()
    }
    aux = {
        value: json.loads(path.read_text(encoding="utf-8"))
        for value, path in aux_by_step.items()
    }

    policy_template = ocp.PyTreeCheckpointer().restore(
        str(policy_cpu_template_path)
    )
    source_tree = restore_tree(source_path, policy_template)
    policy_trees = {
        value: restore_tree(path, source_tree)
        for value, path in policy_by_step.items()
    }
    zero_policy_structure, zero_policy_deltas = tree_deltas(
        source_tree, policy_trees[0]
    )
    policy_updates = [
        {
            "step": value,
            **split_policy_deltas(policy_trees[0], policy_trees[value]),
        }
        for value in EXPECTED_STEPS[1:]
    ]

    cost_template = ocp.PyTreeCheckpointer().restore(
        str(cost_cpu_template_path)
    )
    cost_trees = {
        value: restore_tree(path, cost_template)
        for value, path in cost_by_step.items()
    }
    zero_cost_structure, zero_cost_deltas = tree_deltas(
        cost_template, cost_trees[0]
    )
    cost_updates = [
        {
            "step": value,
            **cost_tree_deltas(cost_trees[0], cost_trees[value]),
        }
        for value in EXPECTED_STEPS[1:]
    ]

    hosted_policy_hashes = {
        int(row["step"]): row["directory_sha256"]
        for row in hosted["policy_checkpoints"]
    }
    hosted_cost_hashes = {
        int(row["step"]): row["directory_sha256"]
        for row in hosted["cost_checkpoints"]
    }
    hosted_graph_hashes = {
        int(row["step"]): row["sha256"] for row in hosted["onnx"]
    }
    hosted_aux = {int(row["step"]): row for row in hosted["aux"]}
    event_path = next(training.glob("events.out.tfevents*"))
    events = t55.all_scalar_events(event_path)
    eval_metrics = finite_metric_rows(events, EVAL_TAGS)
    training_metrics = finite_metric_rows(events, TRAINING_TAGS)
    eval_steps_exact = bool(eval_metrics) and all(
        [int(row["step"]) for row in rows] == EXPECTED_STEPS
        for rows in eval_metrics.values()
    )
    training_steps_exact = bool(training_metrics) and all(
        [int(row["step"]) for row in rows] == EXPECTED_STEPS[1:]
        for rows in training_metrics.values()
    )
    log_text = (work / "training.log").read_text(
        encoding="utf-8", errors="replace"
    )

    dual_initial = aux[0]
    dual_half = aux[1_003_520]
    dual_final = aux[2_007_040]
    expected_quarter = math.ceil(
        int(dual_half["total_training_iterations"]) / 4
    )
    initial_cost = float(dual_half["initial_cost"])
    expected_eta = (
        1.0 / (expected_quarter * initial_cost)
        if expected_quarter > 0 and initial_cost > 0.0
        else None
    )
    checks = {
        "t210_preregistration_green": (
            prereg["status"]
            == "PREREGISTERED_T210_DUAL_ROLL_COST_HOSTED_CONTINUATION"
            and prereg["decision"]
            == "AUTHORIZE_ONE_HASH_FROZEN_T210_L4_CONTINUATION"
            and prereg["failed_checks"] == []
        ),
        "t209_cpu_authority_exact": (
            cpu["status"] == "PASS_T209_DUAL_ROLL_COST_CPU_CONTRACT"
            and cpu["decision"]
            == "EARN_T210_DUAL_ROLL_COST_HOSTED_PREREGISTRATION_ONLY"
            and cpu["failed_checks"] == []
            and hosted["validation"]["input_hashes"]["cpu_result"]
            == sha256(CPU_RESULT)
        ),
        "t204_and_t208_authorities_exact": (
            t204["status"]
            == "PASS_T204_T203_RECOVERED_TRAINING_VALIDATION"
            and t208["status"] == "PASS_T208_T203_PERSISTENCE_AUTOPSY"
            and t208["decision"]
            == "EARN_T209_DUAL_ROLL_COST_CPU_CONTRACT_PREREGISTRATION_ONLY"
            and hosted["validation"]["input_hashes"]["t204_validation"]
            == sha256(T204_VALIDATION)
            and hosted["validation"]["input_hashes"]["t208_selection"]
            == sha256(T208_SELECTION)
        ),
        "package_and_launch_contracts_green": (
            package["status"] == "PASS_T210_DUAL_ROLL_COST_HOSTED_PACKAGE"
            and package["failed_checks"] == []
            and launch["status"] == "PASS_T210_COLAB_CLI_LAUNCH_CONTRACT"
            and launch["failed_checks"] == []
        ),
        "hosted_artifact_passed_pending_cpu_validation": (
            hosted["status"]
            == "PASS_T210_TRAINING_ARTIFACT_PENDING_CPU_VALIDATION"
            and hosted["failed_checks"] == []
            and hosted["cpu_topology_validation_required"] is True
        ),
        "launch_receipt_complete": (
            receipt["status"] == "COMPLETED_T210_COLAB_LAUNCH"
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
        "source_and_cpu_templates_frozen": (
            directory_sha256(source_path)
            == prereg["input_hashes"]["source_checkpoint"]
            and directory_sha256(policy_cpu_template_path)
            == cpu["source_remap"]["cpu_remap"]["sha256"]
            and directory_sha256(cost_cpu_template_path)
            == cpu["training"]["cost_checkpoints"]["0"]["sha256"]
        ),
        "all_exact_export_sets_present": (
            sorted(policy_by_step)
            == sorted(cost_by_step)
            == sorted(graph_by_step)
            == sorted(aux_by_step)
            == EXPECTED_STEPS
        ),
        "policy_hashes_match_hosted_result": (
            policy_hashes == hosted_policy_hashes
        ),
        "cost_hashes_match_hosted_result": cost_hashes == hosted_cost_hashes,
        "onnx_hashes_match_hosted_result": (
            {
                value: row["sha256"]
                for value, row in graph_rows.items()
            }
            == hosted_graph_hashes
        ),
        "aux_states_match_hosted_result": aux == hosted_aux,
        "step_zero_policy_tree_source_bit_exact": (
            zero_policy_structure
            and max(zero_policy_deltas.values(), default=0.0) == 0.0
        ),
        "step_zero_cost_tree_reproducible_bit_exact": (
            zero_cost_structure
            and max(zero_cost_deltas.values(), default=0.0) == 0.0
        ),
        "step_zero_raw_onnx_byte_exact": (
            graph_rows[0]["sha256"] == sha256(expected_step_zero)
            and graph_rows[0]["sha256"]
            == prereg["input_hashes"]["expected_step_zero_raw"]
        ),
        "both_exports_only_update_head_and_reward_critic": all(
            row["structure_exact"]
            and row["tree_finite"]
            and row["every_trainable_actor_leaf_updated"]
            and row["every_mature_actor_leaf_exact"]
            and row["normalizer_exact"]
            and row["every_reward_critic_leaf_updated"]
            for row in policy_updates
        ),
        "both_exports_update_cost_critic": all(
            row["structure_exact"]
            and row["tree_finite"]
            and row["every_leaf_updated"]
            for row in cost_updates
        ),
        "all_policy_and_cost_trees_finite": (
            all(tree_finite(tree) for tree in policy_trees.values())
            and all(tree_finite(tree) for tree in cost_trees.values())
        ),
        "dual_initial_state_exact": (
            dual_initial["initialized"] is False
            and float(dual_initial["lambda"]) == 0.0
            and float(dual_initial["eta"]) == 0.0
            and float(dual_initial["initial_cost"]) == 0.0
        ),
        "dual_initialized_from_derived_cost_and_monotone": (
            dual_half["initialized"] is True
            and dual_final["initialized"] is True
            and float(dual_half["initial_cost"]) > 0.0
            and float(dual_half["initial_cost"])
            == float(dual_final["initial_cost"])
            and float(dual_half["eta"]) > 0.0
            and float(dual_half["eta"]) == float(dual_final["eta"])
            and int(dual_half["quarter_iterations"]) == expected_quarter
            and expected_eta is not None
            and math.isclose(
                float(dual_half["eta"]),
                expected_eta,
                rel_tol=1e-6,
                abs_tol=1e-12,
            )
            and 0.0 < float(dual_half["lambda"])
            <= float(dual_final["lambda"])
            and all(
                math.isfinite(float(item[name]))
                for item in (dual_half, dual_final)
                for name in ("lambda", "eta", "initial_cost")
            )
        ),
        "t209_and_t98_readbacks_exact": (
            "T209_DUAL_ROLL_COST=" in log_text
            and "T98_HIDDEN_EXPERT_CONTINUATION=" in log_text
        ),
        "eval_metrics_finite_at_all_exports": eval_steps_exact,
        "training_metrics_finite_at_both_exports": training_steps_exact,
        "roll_cost_channel_exercised": (
            bool(eval_metrics)
            and max(
                float(row["value"])
                for row in eval_metrics[
                    "eval/episode_cost/t209_predicted_roll_risk"
                ]
            )
            > 0.0
            and float(dual_final["lambda"]) > 0.0
        ),
        "all_onnx_contracts_pass": all(
            row["abi_exact"]
            and row["initializers_finite"]
            and row["cpu_provider_exact"]
            and row["chain_256_finite"]
            for row in graph_rows.values()
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
            "open_duck.t211_t210_recovered_training_validation.v1"
        ),
        "status": (
            "PASS_T211_T210_RECOVERED_TRAINING_VALIDATION"
            if not failed
            else "HOLD_T211_T210_RECOVERED_TRAINING_VALIDATION"
        ),
        "decision": (
            "EARN_T212_T210_POSTEXPORT_COMPOSITION_PREREGISTRATION_ONLY"
            if not failed
            else "NO_BEHAVIOR_EVALUATION"
        ),
        "checks": checks,
        "failed_checks": failed,
        "input_hashes": {
            **input_hashes,
            "t210_preregistration": sha256(PREREGISTRATION),
            "t209_cpu_result": sha256(CPU_RESULT),
            "t204_validation": sha256(T204_VALIDATION),
            "t208_selection": sha256(T208_SELECTION),
            "package_contract": sha256(PACKAGE_CONTRACT),
            "launch_contract": sha256(LAUNCH_CONTRACT),
            "source_checkpoint": directory_sha256(source_path),
            "policy_cpu_template": directory_sha256(
                policy_cpu_template_path
            ),
            "cost_cpu_template": directory_sha256(cost_cpu_template_path),
            "event_file": sha256(event_path),
        },
        "exports": {
            "policy_checkpoints": [
                {
                    "step": value,
                    "path": str(policy_by_step[value]),
                    "directory_sha256": policy_hashes[value],
                }
                for value in EXPECTED_STEPS
            ],
            "cost_checkpoints": [
                {
                    "step": value,
                    "path": str(cost_by_step[value]),
                    "directory_sha256": cost_hashes[value],
                }
                for value in EXPECTED_STEPS
            ],
            "onnx": [graph_rows[value] for value in EXPECTED_STEPS],
            "aux": {str(value): aux[value] for value in EXPECTED_STEPS},
            "policy_updates": policy_updates,
            "cost_updates": cost_updates,
        },
        "metrics": {
            "eval": eval_metrics,
            "training": training_metrics,
        },
        "classification": {
            "training_completed": sorted(policy_by_step) == EXPECTED_STEPS,
            "training_retry": False,
            "same_run_resume": False,
            "behavior_cells": 0,
            "actor_update_scope": "negative_adapter_location_only",
            "reward_critic": "updated",
            "cost_critic": "separate_updated",
            "dual_update": "derived_dense_roll_cost",
            "reward_channel": "unchanged_original_clipped_reward",
            "deployment_graph_change": False,
            "body_configuration_strata": 8,
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
        "# T211 T210 recovered training validation\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Exports: `0 / 1,003,520 / 2,007,040`\n"
        "- Actor scope: existing negative adapter location head only\n"
        "- Reward critic / cost critic: updated / separately updated\n"
        f"- Half / final lambda: "
        f"`{dual_half['lambda']} / {dual_final['lambda']}`\n"
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
