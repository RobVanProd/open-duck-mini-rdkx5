#!/usr/bin/env python3
"""Validate recovered T228 training on CPU before any behavior."""

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

import validate_t216_recovered_training as base  # noqa: E402
from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    verify,
)


ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS / "t229_t228_recovered_training_validation_preregistration.json"
)
OUTPUT = ANALYSIS / "t229_t228_recovered_training_validation.json"
MARKDOWN = ANALYSIS / "T229_T228_RECOVERED_TRAINING_VALIDATION_20260730.md"
EXPECTED_STEPS = [0, 1_003_520, 2_007_040]


def restore_tree(path: Path, template: Any) -> Any:
    return ocp.PyTreeCheckpointer().restore(
        str(path),
        item=template,
        restore_args=orbax_utils.restore_args_from_target(template),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T229 result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T229 validation requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis_prereg = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T229_T228_RECOVERED_TRAINING_VALIDATION"
        or prereg["failed_checks"]
        or canonical_sha256(basis_prereg)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T229 preregistration identity changed")
    for name, item in prereg["frozen_inputs"].items():
        if item.get("kind") != "directory":
            verify(item, f"frozen_inputs.{name}")
            continue
        directory = Path(item["path"])
        files = [path for path in directory.rglob("*") if path.is_file()]
        if (
            len(files) != item["file_count"]
            or sum(path.stat().st_size for path in files) != item["bytes"]
            or base.directory_sha256(directory) != item["sha256"]
        ):
            raise RuntimeError(f"frozen_inputs.{name} changed")

    frozen = prereg["frozen_inputs"]
    hosted_path = Path(frozen["hosted_result"]["path"])
    archive_path = Path(frozen["recovery_archive"]["path"])
    receipt_path = Path(frozen["launch_receipt"]["path"])
    work = Path(frozen["extracted_work"]["path"])
    training = work / "training"
    source_path = Path(frozen["source_checkpoint"]["path"])
    source_raw = Path(frozen["source_raw_onnx"]["path"])
    policy_template_path = Path(frozen["policy_cpu_template"]["path"])
    cost_template_path = Path(frozen["cost_cpu_template"]["path"])
    hosted = json.loads(hosted_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    t228_prereg = json.loads(
        Path(frozen["t228_preregistration"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    cpu = json.loads(
        Path(frozen["t227d_cpu_result"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    package = json.loads(
        Path(frozen["package_contract"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    launch = json.loads(
        Path(frozen["launch_contract"]["path"]).read_text(
            encoding="utf-8"
        )
    )

    policy_paths = sorted(
        (
            path
            for path in training.iterdir()
            if path.is_dir() and "_v127_cost_value" not in path.name
        ),
        key=base.step,
    )
    cost_paths = sorted(
        training.glob("*_v127_cost_value"), key=base.cost_step
    )
    graph_paths = sorted(training.glob("*.onnx"), key=base.step)
    aux_paths = sorted(training.glob("*_v127_aux.json"))
    policy_by_step = {base.step(path): path for path in policy_paths}
    cost_by_step = {base.cost_step(path): path for path in cost_paths}
    graph_by_step = {base.step(path): path for path in graph_paths}
    aux_by_step = {
        int(json.loads(path.read_text(encoding="utf-8"))["step"]): path
        for path in aux_paths
    }
    policy_hashes = {
        value: base.directory_sha256(path)
        for value, path in policy_by_step.items()
    }
    cost_hashes = {
        value: base.directory_sha256(path)
        for value, path in cost_by_step.items()
    }
    graph_rows = {
        value: base.onnx_contract(path)
        for value, path in graph_by_step.items()
    }
    aux = {
        value: json.loads(path.read_text(encoding="utf-8"))
        for value, path in aux_by_step.items()
    }

    policy_template = ocp.PyTreeCheckpointer().restore(
        str(policy_template_path)
    )
    source_tree = restore_tree(source_path, policy_template)
    policy_trees = {
        value: restore_tree(path, source_tree)
        for value, path in policy_by_step.items()
    }
    zero_policy_structure, zero_policy_deltas = base.tree_deltas(
        source_tree, policy_trees[0]
    )
    policy_updates = [
        {
            "step": value,
            **base.split_policy_deltas(
                policy_trees[0], policy_trees[value]
            ),
        }
        for value in EXPECTED_STEPS[1:]
    ]

    cost_template = ocp.PyTreeCheckpointer().restore(
        str(cost_template_path)
    )
    cost_trees = {
        value: restore_tree(path, cost_template)
        for value, path in cost_by_step.items()
    }
    zero_cost_structure, zero_cost_deltas = base.tree_deltas(
        cost_template, cost_trees[0]
    )
    cost_updates = [
        {
            "step": value,
            **base.cost_tree_deltas(cost_trees[0], cost_trees[value]),
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
    events = base.t55.all_scalar_events(event_path)
    eval_metrics = base.finite_metric_rows(events, base.EVAL_TAGS)
    training_metrics = base.finite_metric_rows(
        events, base.TRAINING_TAGS
    )
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
    expected_eta = 1.0 / (expected_quarter * initial_cost)
    cost_tolerance = float(
        prereg["expected"]["step_zero_cost_backend_absolute_tolerance"]
    )
    max_zero_cost_delta = max(zero_cost_deltas.values(), default=0.0)

    checks = {
        "t228_preregistration_green": (
            t228_prereg["status"]
            == "PREREGISTERED_T228_COMMAND_ATOM_HOSTED_CONTINUATION"
            and t228_prereg["failed_checks"] == []
        ),
        "t227d_cpu_authority_exact": (
            cpu["status"] == "PASS_T227D_RECOVERED_CPU_VALIDATION"
            and cpu["failed_checks"] == []
            and hosted["validation"]["input_hashes"]["cpu_result"]
            == frozen["t227d_cpu_result"]["sha256"]
        ),
        "package_and_launch_contracts_green": (
            package["status"] == "PASS_T228_COMMAND_ATOM_HOSTED_PACKAGE"
            and package["failed_checks"] == []
            and launch["status"] == "PASS_T228_COLAB_CLI_LAUNCH_CONTRACT"
            and launch["failed_checks"] == []
        ),
        "hosted_artifact_passed_pending_cpu_validation": (
            hosted["status"]
            == "PASS_T228_TRAINING_ARTIFACT_PENDING_CPU_VALIDATION"
            and hosted["failed_checks"] == []
            and hosted["cpu_topology_validation_required"] is True
        ),
        "launch_receipt_complete": (
            receipt["status"] == "COMPLETED_T228_COLAB_LAUNCH"
            and receipt["returncode"] == 0
            and receipt["retry"] is False
            and receipt["same_run_resume"] is False
            and receipt["robot_or_rdk_access"] is False
        ),
        "result_and_archive_hashes_exact": (
            receipt["output_json_sha256"]
            == frozen["hosted_result"]["sha256"]
            and receipt["output_archive_sha256"]
            == frozen["recovery_archive"]["sha256"]
            == hosted["artifact"]["sha256"]
            and archive_path.stat().st_size == hosted["artifact"]["bytes"]
        ),
        "preregistration_hash_matches_hosted": (
            hosted["validation"]["preregistration_sha256"]
            == frozen["t228_preregistration"]["sha256"]
        ),
        "source_and_cpu_templates_frozen": (
            base.directory_sha256(source_path)
            == prereg["expected"]["source_checkpoint_sha256"]
            and base.sha256(source_raw)
            == prereg["expected"]["source_raw_onnx_sha256"]
            and base.directory_sha256(policy_template_path)
            == frozen["policy_cpu_template"]["sha256"]
            and base.directory_sha256(cost_template_path)
            == frozen["cost_cpu_template"]["sha256"]
        ),
        "all_exact_export_sets_present": (
            sorted(policy_by_step)
            == sorted(cost_by_step)
            == sorted(graph_by_step)
            == sorted(aux_by_step)
            == EXPECTED_STEPS
        ),
        "policy_cost_onnx_and_aux_match_hosted_result": (
            policy_hashes == hosted_policy_hashes
            and cost_hashes == hosted_cost_hashes
            and {
                value: row["sha256"]
                for value, row in graph_rows.items()
            }
            == hosted_graph_hashes
            and aux == hosted_aux
        ),
        "step_zero_policy_tree_source_bit_exact": (
            zero_policy_structure
            and max(zero_policy_deltas.values(), default=0.0) == 0.0
        ),
        "step_zero_cost_tree_within_one_float32_epsilon": (
            zero_cost_structure
            and max_zero_cost_delta <= cost_tolerance
            and base.tree_finite(cost_trees[0])
        ),
        "step_zero_raw_onnx_byte_exact": (
            graph_rows[0]["sha256"] == base.sha256(source_raw)
            == prereg["expected"]["source_raw_onnx_sha256"]
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
            all(base.tree_finite(tree) for tree in policy_trees.values())
            and all(base.tree_finite(tree) for tree in cost_trees.values())
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
            and initial_cost > 0.0
            and initial_cost == float(dual_final["initial_cost"])
            and int(dual_half["quarter_iterations"]) == expected_quarter
            and math.isclose(
                float(dual_half["eta"]),
                expected_eta,
                rel_tol=1e-6,
                abs_tol=1e-12,
            )
            and float(dual_half["eta"]) == float(dual_final["eta"])
            and 0.0 < float(dual_half["lambda"])
            <= float(dual_final["lambda"])
            and all(
                math.isfinite(float(item[name]))
                for item in (dual_half, dual_final)
                for name in ("lambda", "eta", "initial_cost")
            )
        ),
        "all_required_readbacks_exact": (
            prereg["expected"]["command_atom_readback"] in log_text
            and "T215B_AXIS_COMPLETE_TILT_COST=" in log_text
            and "T98_HIDDEN_EXPERT_CONTINUATION=" in log_text
        ),
        "eval_metrics_finite_at_all_exports": eval_steps_exact,
        "training_metrics_finite_at_both_exports": training_steps_exact,
        "axis_complete_tilt_cost_channel_exercised": (
            bool(eval_metrics)
            and max(
                float(row["value"])
                for row in eval_metrics[
                    "eval/episode_cost/t215b_predicted_tilt_box"
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
            "open_duck.t229_t228_recovered_training_validation.v1"
        ),
        "status": (
            "PASS_T229_T228_RECOVERED_TRAINING_VALIDATION"
            if not failed
            else "HOLD_T229_T228_RECOVERED_TRAINING_VALIDATION"
        ),
        "decision": (
            "EARN_T230_T228_POSTEXPORT_COMPOSITION_PREREGISTRATION_ONLY"
            if not failed
            else "NO_BEHAVIOR_EVALUATION"
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "checks": checks,
        "failed_checks": failed,
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
        "metrics": {"eval": eval_metrics, "training": training_metrics},
        "cost_init_backend_comparison": {
            "maximum_absolute_leaf_delta": max_zero_cost_delta,
            "absolute_tolerance": cost_tolerance,
            "within_tolerance": max_zero_cost_delta <= cost_tolerance,
        },
        "classification": {
            "training_completed": sorted(policy_by_step) == EXPECTED_STEPS,
            "training_retry": False,
            "same_run_resume": False,
            "behavior_cells": 0,
            "actor_update_scope": "negative_adapter_location_only",
            "reward_critic": "updated",
            "cost_critic": "separate_updated",
            "dual_update": "derived_dense_axis_complete_tilt_cost",
            "configuration_strata": 8,
            "command_strata": 4,
            "cartesian_strata": 32,
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
    value = {**basis, "result_sha256": base.sha256_json(basis)}
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T229 T228 recovered training validation\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Exports: `0 / 1,003,520 / 2,007,040`\n"
        "- Actor scope: existing negative adapter location head only\n"
        f"- Half / final lambda: "
        f"`{dual_half['lambda']} / {dual_final['lambda']}`\n"
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
