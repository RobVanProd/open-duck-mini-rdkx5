#!/usr/bin/env python3
"""Read-only recovery and judgment of T112's completed CPU smoke."""

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

import numpy as np
import onnx
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import build_t112_always_on_trainthrough_preregistration as build  # noqa: E402
import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t98_hidden_expert_cpu_contract as t98  # noqa: E402
import run_t109_always_on_expert_transform as t109  # noqa: E402
import run_t112_always_on_trainthrough_cpu_contract as t112  # noqa: E402
from run_winner_v111_peak_torque_cpu_smoke import tree_errors  # noqa: E402


PREREG = ANALYSIS / "t112b_cpu_recovery_preregistration.json"
RESULT = ANALYSIS / "t112b_cpu_recovery_result.json"
MARKDOWN = ANALYSIS / "T112B_CPU_RECOVERY_RESULT_20260729.md"
EXTRA_HEAD = "negative_adapter_location"


def validate_prereg(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status") != "PREREGISTERED_T112B_READ_ONLY_CPU_RECOVERY"
        or value.get("failed_checks")
        or build.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T112B preregistration identity changed")
    for name, item in value["sources"].items():
        t20.verify_receipt(item, name)
    for name in (
        "original_contract",
        "source_checkpoint",
        "source_raw_onnx",
        "cpu_topology_template",
        "trace_population",
        "cpu_remapped_source",
        "expected_always_on_graph",
        "training_log",
    ):
        t20.verify_receipt(value["assets"][name], name)
    for index, item in enumerate(value["assets"]["checkpoints"]):
        t20.verify_receipt(item, f"checkpoint:{index}")
    for index, item in enumerate(value["assets"]["graphs"]):
        t20.verify_receipt(item, f"graph:{index}")


def expected_transform_contract(
    source_path: Path, expected_path: Path
) -> dict[str, Any]:
    source = onnx.load(source_path)
    expected = onnx.load(expected_path)
    identity = [
        node
        for node in expected.graph.node
        if node.op_type == "Identity"
        and list(node.input) == ["negative_adapter_location"]
        and list(node.output) == ["conditional_adapter_location"]
    ]
    gate_consumers = [
        node
        for node in expected.graph.node
        if "negative_com_gate" in node.input
    ]
    return {
        "node_count_exact": len(source.graph.node) == len(expected.graph.node),
        "abi_exact": t109.graph_abi(source) == t109.graph_abi(expected),
        "initializers_exact": (
            t109.initializer_map(source) == t109.initializer_map(expected)
        ),
        "replacement_count": len(identity),
        "negative_gate_consumer_count": len(gate_consumers),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recover-read-only", action="store_true")
    args = parser.parse_args()
    if not args.recover_read_only:
        raise PermissionError("T112B requires --recover-read-only")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T112B result: {path}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T112B recovery requires a clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    validate_prereg(prereg)
    assets = prereg["assets"]
    source_path = Path(assets["source_checkpoint"]["path"])
    topology_path = Path(assets["cpu_topology_template"]["path"])
    cpu_source_path = Path(assets["cpu_remapped_source"]["path"])
    source_graph = Path(assets["source_raw_onnx"]["path"])
    expected_graph = Path(assets["expected_always_on_graph"]["path"])
    checkpoints = {
        int(Path(item["path"]).name.rsplit("_", 1)[1]): Path(item["path"])
        for item in assets["checkpoints"]
    }
    graphs = {
        int(Path(item["path"]).stem.rsplit("_", 1)[1]): Path(item["path"])
        for item in assets["graphs"]
    }

    topology = ocp.PyTreeCheckpointer().restore(str(topology_path))
    source = t98.restore_tree(source_path, topology)
    cpu_source = t98.restore_tree(cpu_source_path, source)
    remap_structure, remap_deltas = tree_errors(source, cpu_source)
    initial = t98.restore_tree(checkpoints[0], source)
    final = t98.restore_tree(checkpoints[1024], source)
    restore_structure, restore_deltas = tree_errors(source, initial)
    update_structure, update_deltas = tree_errors(initial, final)
    policy_deltas = {
        name: value
        for name, value in update_deltas.items()
        if name.startswith("1/params/")
    }
    expert_deltas = {
        name: value
        for name, value in policy_deltas.items()
        if EXTRA_HEAD in name
    }
    protected_deltas = {
        name: value
        for name, value in policy_deltas.items()
        if name not in expert_deltas
    }
    normalizer_deltas = {
        name: value
        for name, value in update_deltas.items()
        if name.startswith("0/")
    }
    critic_deltas = {
        name: value
        for name, value in update_deltas.items()
        if name.startswith("2/params/")
    }

    case_prereg = {
        "assets": {"t97_preregistration": assets["trace_population"]}
    }
    cases = t98.trace_cases(case_prereg)
    step_zero_trace = t112.trace_equivalence(
        expected_graph, graphs[0], cases
    )
    step_zero_chain = t98.compare_random_chain(expected_graph, graphs[0])
    postupdate = t112.update_binding(graphs[0], graphs[1024], cases)
    random_binding = t112.random_update_binding(
        graphs[0], graphs[1024]
    )
    transform = expected_transform_contract(source_graph, expected_graph)
    graph_contracts = {
        str(step): {
            "receipt": t20.receipt(graph),
            "io": t98.graph_io(graph),
            "chain": t98.graph_chain(graph),
        }
        for step, graph in sorted(graphs.items())
    }
    thresholds = prereg["recovery"]["contract_thresholds"]
    expected_io = {
        "inputs": {
            "h_in": [1, 64],
            "obs": [1, 115],
            "previous_action": [1, 14],
        },
        "outputs": {
            "continuous_actions": [1, 14],
            "h_out": [1, 64],
            "previous_action_out": [1, 14],
        },
    }
    log = Path(assets["training_log"]["path"]).read_text(
        encoding="utf-8", errors="replace"
    )
    checks = {
        "recovery_artifacts_frozen": True,
        "training_readback_exact": (
            "T98_HIDDEN_EXPERT_CONTINUATION="
            "strata=8,broad=1,isolated=7,"
            "gate=always_on,"
            "actor_updates=negative_adapter_location_only"
            in log
        ),
        "source_cpu_remap_exact": (
            remap_structure
            and max(remap_deltas.values(), default=0.0) == 0.0
            and t112.finite_tree(cpu_source)
        ),
        "exact_always_on_transform": (
            transform["node_count_exact"]
            and transform["abi_exact"]
            and transform["initializers_exact"]
            and transform["replacement_count"] == 1
            and transform["negative_gate_consumer_count"] == 0
        ),
        "step_zero_tree_exact": (
            restore_structure
            and max(restore_deltas.values(), default=0.0) == 0.0
        ),
        "update_structure_exact": update_structure,
        "only_negative_expert_actor_changed": (
            bool(expert_deltas)
            and all(value > 0.0 for value in expert_deltas.values())
            and bool(protected_deltas)
            and all(value == 0.0 for value in protected_deltas.values())
        ),
        "normalizer_bit_exact": (
            bool(normalizer_deltas)
            and all(value == 0.0 for value in normalizer_deltas.values())
        ),
        "every_critic_leaf_changed": (
            bool(critic_deltas)
            and all(value > 0.0 for value in critic_deltas.values())
        ),
        "trees_finite": t112.finite_tree(initial) and t112.finite_tree(final),
        "step_zero_trace_exact": (
            step_zero_trace["rows"]
            == thresholds["step_zero_trace_bit_exact_rows"]
            and step_zero_trace["bit_exact_rows"]
            == step_zero_trace["rows"]
            and step_zero_trace["maximum_abs_error"] == 0.0
            and step_zero_trace["always_on_identity_rows"]
            == step_zero_trace["rows"]
        ),
        "step_zero_random_chain_exact": (
            step_zero_chain["steps"]
            == thresholds["step_zero_random_chain_bit_exact_steps"]
            and step_zero_chain["bit_exact_steps"]
            == step_zero_chain["steps"]
            and step_zero_chain["maximum_abs_error"] == 0.0
        ),
        "postupdate_trace_action_binding": (
            postupdate["raw_changed_fraction"]
            >= thresholds["minimum_trace_raw_action_changed_fraction"]
            and postupdate["final_changed_fraction"]
            >= thresholds["minimum_trace_final_action_changed_fraction"]
            and postupdate["always_on_identity_rows"]
            == postupdate["rows"]
            and postupdate["maximum_hidden_delta"] == 0.0
        ),
        "postupdate_random_action_binding": (
            random_binding["changed_steps"] > 0
            and random_binding["maximum_raw_action_delta"]
            >= thresholds["minimum_random_raw_action_delta"]
        ),
        "graph_abi_and_cpu_chain_exact": all(
            item["io"]["inputs"] == expected_io["inputs"]
            and item["io"]["outputs"] == expected_io["outputs"]
            and item["io"]["providers"][0] == "CPUExecutionProvider"
            and item["chain"]["finite"]
            and item["chain"]["steps"] == 256
            for item in graph_contracts.values()
        ),
        "no_additional_optimizer_behavior_hosted_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    original_rule = prereg["recovery"]["decision_rule"]
    result: dict[str, Any] = {
        "schema_version": "open_duck.t112b_cpu_recovery_result.v1",
        "status": (
            "PASS_T112B_READ_ONLY_CPU_RECOVERY"
            if passed
            else "HOLD_T112B_READ_ONLY_CPU_RECOVERY"
        ),
        "decision": (
            original_rule["pass_decision"]
            if passed
            else original_rule["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "attribution": prereg["attribution"],
        "source_remap": {
            "structure_exact": remap_structure,
            "maximum_abs_error": max(remap_deltas.values(), default=0.0),
        },
        "always_on_transform": transform,
        "training_artifacts": {
            "initial_checkpoint": assets["checkpoints"][0],
            "final_checkpoint": assets["checkpoints"][1],
            "graphs": graph_contracts,
            "log": assets["training_log"],
        },
        "tree_contract": {
            "negative_expert_actor_leaf_deltas": expert_deltas,
            "protected_mature_actor_leaf_deltas": protected_deltas,
            "normalizer_leaf_deltas": normalizer_deltas,
            "critic_leaf_deltas": critic_deltas,
        },
        "causal_contract": {
            "step_zero_trace": step_zero_trace,
            "step_zero_random_chain": step_zero_chain,
            "postupdate_trace": postupdate,
            "postupdate_random": random_binding,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "recovered_prior_optimizer_steps": 1024,
            "additional_optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "simulator_behavior_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "hosted_preregistration": passed,
            "hosted_training": False,
            "behavior_evaluation": False,
            "policy_promotion": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    result["result_sha256"] = build.canonical_sha256(result)
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T112B read-only CPU recovery result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Failed checks: `{failed}`",
                (
                    "- Step-zero trace / chain exact: "
                    f"`{step_zero_trace['bit_exact_rows']}/"
                    f"{step_zero_trace['rows']} / "
                    f"{step_zero_chain['bit_exact_steps']}/"
                    f"{step_zero_chain['steps']}`"
                ),
                (
                    "- Updated raw / deployed changed fraction: "
                    f"`{postupdate['raw_changed_fraction']:.6f} / "
                    f"{postupdate['final_changed_fraction']:.6f}`"
                ),
                "- Additional optimizer / behavior / hosted / robot: `0/0/0/0`",
                f"- Result SHA-256: `{result['result_sha256']}`",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"failed_checks={failed}")
    print(f"result_sha256={result['result_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
