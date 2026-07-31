#!/usr/bin/env python3
"""Run T119's preregistered joint soft-router/expert CPU contract."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import jax
import numpy as np
import onnxruntime as ort
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t55_dynamic_single_support_cpu_contract as t55  # noqa: E402
import run_t98_hidden_expert_cpu_contract as t98  # noqa: E402
from run_winner_v111_peak_torque_cpu_smoke import tree_errors  # noqa: E402


PREREG = ANALYSIS / "t119_joint_soft_router_cpu_preregistration.json"
RESULT = ANALYSIS / "t119_joint_soft_router_cpu_result.json"
MARKDOWN = ANALYSIS / "T119_JOINT_SOFT_ROUTER_CPU_RESULT_20260729.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/t119_joint_soft_router_cpu_v1"
)
OUTPUT = WORK / "smoke"
INSPECTION = WORK / "inspection"
TRAINABLE_ACTOR = {
    "negative_adapter_location",
    "soft_router_coefficient_delta",
    "soft_router_intercept_delta",
}


def validate_prereg(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T119_JOINT_SOFT_ROUTER_CPU_CONTRACT"
        or value.get("failed_checks")
        or t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T119 preregistration identity changed")
    for name, item in value["sources"].items():
        t20.verify_receipt(item, name)
    for name, item in value["assets"].items():
        t20.verify_receipt(item, name)
    playground = Path(value["playground"]["path"])
    inventory = {
        path.relative_to(playground).as_posix(): t20.sha256(path)
        for path in sorted(playground.rglob("*.py"))
    }
    if (
        inventory != value["playground"]["python_inventory"]
        or t20.canonical_sha256(inventory)
        != value["playground"]["python_inventory_sha256"]
    ):
        raise RuntimeError("T119 composed source inventory changed")


def finite_tree(value: Any) -> bool:
    return all(
        bool(np.all(np.isfinite(np.asarray(leaf))))
        for leaf in jax.tree_util.tree_leaves(value)
    )


def inspect_graph(source: Path, destination: Path) -> Path:
    return t98.inspection_graph(
        source,
        destination,
        {
            "raw_continuous_actions": [1, 14],
            "hidden_gate_score": [1, 1],
            "soft_negative_com_weight": [1, 1],
            "negative_adapter_location": [1, 14],
            "conditional_adapter_location": [1, 14],
        },
    )


def inspection_session(path: Path) -> ort.InferenceSession:
    return ort.InferenceSession(
        str(path), providers=["CPUExecutionProvider"]
    )


def step_zero_trace(
    expected: Path, actual: Path, cases: list[dict[str, Any]]
) -> dict[str, Any]:
    INSPECTION.mkdir(parents=True, exist_ok=True)
    left = inspection_session(
        inspect_graph(expected, INSPECTION / "expected_step_zero.onnx")
    )
    right = inspection_session(
        inspect_graph(actual, INSPECTION / "actual_step_zero.onnx")
    )
    names = [
        "continuous_actions",
        "previous_action_out",
        "h_out",
        "raw_continuous_actions",
        "hidden_gate_score",
        "soft_negative_com_weight",
        "negative_adapter_location",
        "conditional_adapter_location",
    ]
    exact = 0
    maximum_error = 0.0
    for case in cases:
        before = left.run(names, case["feed"])
        after = right.run(names, case["feed"])
        errors = [
            t98.max_abs(a, b)
            for a, b in zip(before, after, strict=True)
        ]
        maximum_error = max(maximum_error, *errors)
        exact += int(
            all(
                np.array_equal(a, b)
                for a, b in zip(before, after, strict=True)
            )
        )
    return {
        "rows": len(cases),
        "bit_exact_rows": exact,
        "maximum_abs_error": maximum_error,
    }


def postupdate_binding(
    initial: Path, final: Path, cases: list[dict[str, Any]]
) -> dict[str, Any]:
    left = inspection_session(
        inspect_graph(initial, INSPECTION / "initial_update.onnx")
    )
    right = inspection_session(
        inspect_graph(final, INSPECTION / "final_update.onnx")
    )
    names = [
        "continuous_actions",
        "previous_action_out",
        "h_out",
        "raw_continuous_actions",
        "hidden_gate_score",
        "soft_negative_com_weight",
        "negative_adapter_location",
        "conditional_adapter_location",
    ]
    rows: list[dict[str, Any]] = []
    for case in cases:
        before = left.run(names, case["feed"])
        after = right.run(names, case["feed"])
        rows.append(
            {
                "population": case["population"],
                "label": int(case["label"]),
                "final_delta": t98.max_abs(before[0], after[0]),
                "previous_delta": t98.max_abs(before[1], after[1]),
                "hidden_delta": t98.max_abs(before[2], after[2]),
                "raw_delta": t98.max_abs(before[3], after[3]),
                "score_delta": t98.max_abs(before[4], after[4]),
                "weight_delta": t98.max_abs(before[5], after[5]),
                "expert_delta": t98.max_abs(before[6], after[6]),
                "conditional_delta": t98.max_abs(before[7], after[7]),
                "initial_weight": float(before[5][0, 0]),
                "final_weight": float(after[5][0, 0]),
            }
        )
    epsilon = 1.0e-7

    def summarize(selected: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "rows": len(selected),
            "raw_changed_rows": sum(
                row["raw_delta"] > epsilon for row in selected
            ),
            "final_changed_rows": sum(
                row["final_delta"] > epsilon for row in selected
            ),
            "router_weight_changed_rows": sum(
                row["weight_delta"] > epsilon for row in selected
            ),
            "maximum_raw_action_delta": max(
                row["raw_delta"] for row in selected
            ),
            "maximum_final_action_delta": max(
                row["final_delta"] for row in selected
            ),
            "maximum_router_score_delta": max(
                row["score_delta"] for row in selected
            ),
            "maximum_router_weight_delta": max(
                row["weight_delta"] for row in selected
            ),
            "maximum_expert_delta": max(
                row["expert_delta"] for row in selected
            ),
            "maximum_conditional_delta": max(
                row["conditional_delta"] for row in selected
            ),
            "initial_weight_min": min(
                row["initial_weight"] for row in selected
            ),
            "initial_weight_max": max(
                row["initial_weight"] for row in selected
            ),
            "final_weight_min": min(
                row["final_weight"] for row in selected
            ),
            "final_weight_max": max(
                row["final_weight"] for row in selected
            ),
        }

    nominal = [row for row in rows if row["label"] == -1]
    negative = [row for row in rows if row["label"] == 1]
    if not nominal or not negative:
        raise RuntimeError("T119 trace populations are incomplete")
    return {
        "rows": len(rows),
        "nominal": summarize(nominal),
        "negative_com": summarize(negative),
        "maximum_hidden_delta": max(row["hidden_delta"] for row in rows),
    }


def random_binding(
    initial: Path, final: Path, steps: int = 256
) -> dict[str, Any]:
    left = inspection_session(
        inspect_graph(initial, INSPECTION / "initial_random.onnx")
    )
    right = inspection_session(
        inspect_graph(final, INSPECTION / "final_random.onnx")
    )
    rng = np.random.default_rng(1190001)
    raw_max = 0.0
    weight_max = 0.0
    changed = 0
    for _ in range(steps):
        feed = {
            "obs": rng.normal(size=(1, 115)).astype(np.float32),
            "previous_action": rng.uniform(
                -0.5, 0.5, size=(1, 14)
            ).astype(np.float32),
            "h_in": rng.normal(size=(1, 64)).astype(np.float32),
        }
        names = ["raw_continuous_actions", "soft_negative_com_weight"]
        before = left.run(names, feed)
        after = right.run(names, feed)
        raw_delta = t98.max_abs(before[0], after[0])
        weight_delta = t98.max_abs(before[1], after[1])
        raw_max = max(raw_max, raw_delta)
        weight_max = max(weight_max, weight_delta)
        changed += int(raw_delta > 1.0e-7 and weight_delta > 1.0e-7)
    return {
        "steps": steps,
        "jointly_changed_steps": changed,
        "maximum_raw_action_delta": raw_max,
        "maximum_router_weight_delta": weight_max,
    }


def graph_contract(path: Path) -> dict[str, Any]:
    return {
        "receipt": t20.receipt(path),
        "io": t98.graph_io(path),
        "chain": t98.graph_chain(path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu-contract-authorized", action="store_true")
    args = parser.parse_args()
    if not args.cpu_contract_authorized:
        raise PermissionError("T119 requires --cpu-contract-authorized")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T119 result: {path}")
    if WORK.exists():
        raise FileExistsError(f"refusing to reuse T119 work root: {WORK}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T119 execution requires clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    validate_prereg(prereg)
    WORK.mkdir(parents=True)
    playground = Path(prereg["playground"]["path"])
    source_path = Path(prereg["assets"]["expanded_checkpoint"]["path"])
    expected = Path(prereg["assets"]["expected_soft_graph"]["path"])
    reference = Path(prereg["assets"]["reference_features"]["path"])
    gate_asset = Path(prereg["assets"]["hidden_gate_static_asset"]["path"])
    source = ocp.PyTreeCheckpointer().restore(str(source_path))

    command = t98.training_command(
        python=Path(sys.executable),
        playground=playground,
        output=OUTPUT,
        reference=reference,
        restore=source_path,
        gate_asset=gate_asset,
    )
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=playground,
        env=t55.cpu_environment(playground),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=1800,
    )
    elapsed = time.monotonic() - started
    log = WORK / "training.log"
    log.write_text(completed.stdout, encoding="utf-8", newline="\n")
    if completed.returncode != 0:
        raise RuntimeError(
            f"T119 CPU training failed rc={completed.returncode}\n"
            f"{completed.stdout[-16000:]}"
        )

    checkpoints = {
        int(path.name.rsplit("_", 1)[1]): path
        for path in OUTPUT.iterdir()
        if path.is_dir()
    }
    graphs = {
        int(path.stem.rsplit("_", 1)[1]): path
        for path in OUTPUT.glob("*.onnx")
    }
    if sorted(checkpoints) != [0, 1024] or sorted(graphs) != [0, 1024]:
        raise RuntimeError("T119 export steps changed")

    initial = t98.restore_tree(checkpoints[0], source)
    final = t98.restore_tree(checkpoints[1024], source)
    restore_structure, restore_deltas = tree_errors(source, initial)
    update_structure, update_deltas = tree_errors(initial, final)
    policy_deltas = {
        name: value
        for name, value in update_deltas.items()
        if name.startswith("1/params/")
    }
    trainable_deltas = {
        name: value
        for name, value in policy_deltas.items()
        if any(group in name for group in TRAINABLE_ACTOR)
    }
    protected_deltas = {
        name: value
        for name, value in policy_deltas.items()
        if name not in trainable_deltas
    }
    router_deltas = {
        name: value
        for name, value in trainable_deltas.items()
        if "soft_router_" in name
    }
    expert_deltas = {
        name: value
        for name, value in trainable_deltas.items()
        if "negative_adapter_location" in name
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

    cases = t98.trace_cases(prereg)
    zero_trace = step_zero_trace(expected, graphs[0], cases)
    zero_chain = t98.compare_random_chain(expected, graphs[0])
    binding = postupdate_binding(graphs[0], graphs[1024], cases)
    random = random_binding(graphs[0], graphs[1024])
    graph_contracts = {
        str(step): graph_contract(graph)
        for step, graph in sorted(graphs.items())
    }
    thresholds = prereg["thresholds"]
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
    readback = (
        "T98_HIDDEN_EXPERT_CONTINUATION="
        "strata=8,broad=1,isolated=7,"
        "gate=joint_soft,"
        "actor_updates=negative_adapter_location_plus_soft_router"
    )

    def population_changed(population: dict[str, Any]) -> bool:
        return (
            population["raw_changed_rows"]
            >= thresholds["minimum_changed_rows_each_population"]
            and population["router_weight_changed_rows"]
            >= thresholds["minimum_changed_rows_each_population"]
            and population["maximum_raw_action_delta"]
            >= thresholds["minimum_raw_action_delta"]
            and population["maximum_router_weight_delta"]
            >= thresholds["minimum_router_weight_delta"]
        )

    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "command_exact": (
            "--winner_t98_hidden_expert_continuation" in command
            and command[command.index("--ppo_num_envs") + 1] == "8"
            and command[command.index("--ppo_batch_size") + 1] == "8"
            and command[
                command.index("--winner_t98_hidden_gate_asset_path") + 1
            ]
            == str(gate_asset)
        ),
        "runner_readback_exact": readback in completed.stdout,
        "step_zero_tree_exact": (
            restore_structure
            and max(restore_deltas.values(), default=0.0) == 0.0
        ),
        "update_structure_exact": update_structure,
        "all_trainable_actor_leaves_changed": (
            bool(trainable_deltas)
            and bool(expert_deltas)
            and len(router_deltas) == 2
            and all(value > 0.0 for value in trainable_deltas.values())
        ),
        "protected_mature_actor_bit_exact": (
            bool(protected_deltas)
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
        "trees_finite": finite_tree(initial) and finite_tree(final),
        "step_zero_trace_exact": (
            zero_trace["rows"]
            == thresholds["step_zero_trace_bit_exact_rows"]
            and zero_trace["bit_exact_rows"] == zero_trace["rows"]
            and zero_trace["maximum_abs_error"] == 0.0
        ),
        "step_zero_random_chain_exact": (
            zero_chain["steps"]
            == thresholds["step_zero_random_chain_bit_exact_steps"]
            and zero_chain["bit_exact_steps"] == zero_chain["steps"]
            and zero_chain["maximum_abs_error"] == 0.0
        ),
        "nominal_population_action_and_router_binding": population_changed(
            binding["nominal"]
        ),
        "negative_population_action_and_router_binding": population_changed(
            binding["negative_com"]
        ),
        "protected_hidden_path_exact": (
            binding["maximum_hidden_delta"] == 0.0
        ),
        "random_action_and_router_binding": (
            random["jointly_changed_steps"] > 0
            and random["maximum_raw_action_delta"]
            >= thresholds["minimum_raw_action_delta"]
            and random["maximum_router_weight_delta"]
            >= thresholds["minimum_router_weight_delta"]
        ),
        "graph_abi_and_cpu_chain_exact": all(
            item["io"]["inputs"] == expected_io["inputs"]
            and item["io"]["outputs"] == expected_io["outputs"]
            and item["io"]["providers"][0] == "CPUExecutionProvider"
            and item["chain"]["finite"]
            and item["chain"]["steps"] == 256
            for item in graph_contracts.values()
        ),
        "no_formal_behavior_hosted_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    result: dict[str, Any] = {
        "schema_version": "open_duck.t119_joint_soft_router_cpu_result.v1",
        "status": (
            "PASS_T119_JOINT_SOFT_ROUTER_CPU_CONTRACT"
            if passed
            else "HOLD_T119_JOINT_SOFT_ROUTER_CPU_CONTRACT"
        ),
        "decision": (
            prereg["decision_rule"]["pass_decision"]
            if passed
            else prereg["decision_rule"]["fail_decision"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "training": {
            "command": command,
            "elapsed_seconds": elapsed,
            "log": t20.receipt(log),
            "initial_checkpoint": t20.directory_receipt(checkpoints[0]),
            "final_checkpoint": t20.directory_receipt(checkpoints[1024]),
            "graphs": graph_contracts,
        },
        "tree_contract": {
            "trainable_actor_leaf_deltas": trainable_deltas,
            "router_leaf_deltas": router_deltas,
            "expert_leaf_deltas": expert_deltas,
            "protected_mature_actor_leaf_deltas": protected_deltas,
            "normalizer_leaf_deltas": normalizer_deltas,
            "critic_leaf_deltas": critic_deltas,
        },
        "causal_contract": {
            "step_zero_trace": zero_trace,
            "step_zero_random_chain": zero_chain,
            "postupdate_trace": binding,
            "postupdate_random": random,
        },
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "optimizer_steps": 1024,
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
    result["result_sha256"] = t20.canonical_sha256(result)
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "\n".join(
            [
                "# T119 joint soft-router CPU result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Failed checks: `{failed}`",
                (
                    "- Step-zero trace / chain exact: "
                    f"`{zero_trace['bit_exact_rows']}/{zero_trace['rows']} / "
                    f"{zero_chain['bit_exact_steps']}/{zero_chain['steps']}`"
                ),
                (
                    "- Nominal raw / router changed rows: "
                    f"`{binding['nominal']['raw_changed_rows']} / "
                    f"{binding['nominal']['router_weight_changed_rows']}`"
                ),
                (
                    "- Negative raw / router changed rows: "
                    f"`{binding['negative_com']['raw_changed_rows']} / "
                    f"{binding['negative_com']['router_weight_changed_rows']}`"
                ),
                "- CPU steps / behavior / hosted / robot: `1024/0/0/0`",
                f"- Result SHA-256: `{result['result_sha256']}`",
                "",
                "A pass earns only a separate hosted-run preregistration.",
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
