#!/usr/bin/env python3
"""Run T112's preregistered always-on expert train-through CPU contract."""

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

from flax.training import orbax_utils
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
import run_t109_always_on_expert_transform as t109  # noqa: E402
from run_winner_v111_peak_torque_cpu_smoke import tree_errors  # noqa: E402


PREREG = ANALYSIS / "t112_always_on_trainthrough_preregistration.json"
RESULT = ANALYSIS / "t112_always_on_trainthrough_result.json"
MARKDOWN = ANALYSIS / "T112_ALWAYS_ON_TRAINTHROUGH_RESULT_20260729.md"
WORK = Path(
    "D:/CodexArtifacts/open-duck-policy/t112_always_on_trainthrough_cpu_v1"
)
CPU_SOURCE = WORK / "t100c_half_cpu_remap"
OUTPUT = WORK / "smoke"
INSPECTION = WORK / "inspection"
EXPECTED = WORK / "t100c_half_expected_always_on.onnx"
EXTRA_HEAD = "negative_adapter_location"


def validate_prereg(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T112_ALWAYS_ON_TRAINTHROUGH_CPU_CONTRACT"
        or value.get("failed_checks")
        or t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T112 preregistration identity changed")
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
        raise RuntimeError("T112 composed source inventory changed")


def finite_tree(value: Any) -> bool:
    return all(
        bool(np.all(np.isfinite(np.asarray(leaf))))
        for leaf in jax.tree_util.tree_leaves(value)
    )


def cpu_remap(
    source_path: Path, topology_path: Path
) -> tuple[Any, dict[str, Any]]:
    topology = ocp.PyTreeCheckpointer().restore(str(topology_path))
    source = t98.restore_tree(source_path, topology)
    checkpointer = ocp.PyTreeCheckpointer()
    checkpointer.save(
        str(CPU_SOURCE),
        source,
        save_args=orbax_utils.save_args_from_target(source),
    )
    restored = t98.restore_tree(CPU_SOURCE, source)
    structure, deltas = tree_errors(source, restored)
    return restored, {
        "source": t20.directory_receipt(source_path),
        "topology": t20.directory_receipt(topology_path),
        "cpu_remap": t20.directory_receipt(CPU_SOURCE),
        "structure_exact": structure,
        "maximum_abs_error": max(deltas.values(), default=0.0),
        "tree_finite": finite_tree(restored),
    }


def inspection_sessions(
    expected: Path, actual: Path, label: str
) -> tuple[ort.InferenceSession, ort.InferenceSession]:
    INSPECTION.mkdir(parents=True, exist_ok=True)
    left = t98.inspection_graph(
        expected,
        INSPECTION / f"expected_{label}.onnx",
        {"raw_continuous_actions": [1, 14]},
    )
    right = t98.inspection_graph(
        actual,
        INSPECTION / f"actual_{label}.onnx",
        {
            "raw_continuous_actions": [1, 14],
            "negative_adapter_location": [1, 14],
            "conditional_adapter_location": [1, 14],
        },
    )
    return (
        ort.InferenceSession(str(left), providers=["CPUExecutionProvider"]),
        ort.InferenceSession(str(right), providers=["CPUExecutionProvider"]),
    )


def trace_equivalence(
    expected: Path, actual: Path, cases: list[dict[str, Any]]
) -> dict[str, Any]:
    left, right = inspection_sessions(expected, actual, "step0")
    left_names = [
        "continuous_actions",
        "previous_action_out",
        "h_out",
        "raw_continuous_actions",
    ]
    right_names = [
        *left_names,
        "negative_adapter_location",
        "conditional_adapter_location",
    ]
    exact = 0
    maximum_error = 0.0
    identity_rows = 0
    for case in cases:
        expected_values = left.run(left_names, case["feed"])
        actual_values = right.run(right_names, case["feed"])
        errors = [
            t98.max_abs(a, b)
            for a, b in zip(
                expected_values, actual_values[:4], strict=True
            )
        ]
        maximum_error = max(maximum_error, *errors)
        exact += int(
            all(
                np.array_equal(a, b)
                for a, b in zip(
                    expected_values, actual_values[:4], strict=True
                )
            )
        )
        identity_rows += int(
            np.array_equal(actual_values[4], actual_values[5])
        )
    return {
        "rows": len(cases),
        "bit_exact_rows": exact,
        "maximum_abs_error": maximum_error,
        "always_on_identity_rows": identity_rows,
    }


def update_binding(
    initial: Path, final: Path, cases: list[dict[str, Any]]
) -> dict[str, Any]:
    left, right = inspection_sessions(initial, final, "update")
    left_names = [
        "continuous_actions",
        "previous_action_out",
        "h_out",
        "raw_continuous_actions",
    ]
    right_names = [
        *left_names,
        "negative_adapter_location",
        "conditional_adapter_location",
    ]
    rows: list[dict[str, float | bool]] = []
    for case in cases:
        before = left.run(left_names, case["feed"])
        after = right.run(right_names, case["feed"])
        rows.append(
            {
                "final_delta": t98.max_abs(before[0], after[0]),
                "previous_delta": t98.max_abs(before[1], after[1]),
                "hidden_delta": t98.max_abs(before[2], after[2]),
                "raw_delta": t98.max_abs(before[3], after[3]),
                "always_on_identity": np.array_equal(after[4], after[5]),
            }
        )
    epsilon = 1.0e-7
    return {
        "rows": len(rows),
        "raw_changed_rows": sum(
            float(row["raw_delta"]) > epsilon for row in rows
        ),
        "raw_changed_fraction": sum(
            float(row["raw_delta"]) > epsilon for row in rows
        )
        / len(rows),
        "final_changed_rows": sum(
            float(row["final_delta"]) > epsilon for row in rows
        ),
        "final_changed_fraction": sum(
            float(row["final_delta"]) > epsilon for row in rows
        )
        / len(rows),
        "maximum_raw_action_delta": max(
            float(row["raw_delta"]) for row in rows
        ),
        "maximum_final_action_delta": max(
            float(row["final_delta"]) for row in rows
        ),
        "maximum_hidden_delta": max(
            float(row["hidden_delta"]) for row in rows
        ),
        "always_on_identity_rows": sum(
            bool(row["always_on_identity"]) for row in rows
        ),
    }


def random_update_binding(
    initial: Path, final: Path, steps: int = 256
) -> dict[str, Any]:
    left = ort.InferenceSession(
        str(
            t98.inspection_graph(
                initial,
                INSPECTION / "random_initial.onnx",
                {"raw_continuous_actions": [1, 14]},
            )
        ),
        providers=["CPUExecutionProvider"],
    )
    right = ort.InferenceSession(
        str(
            t98.inspection_graph(
                final,
                INSPECTION / "random_final.onnx",
                {"raw_continuous_actions": [1, 14]},
            )
        ),
        providers=["CPUExecutionProvider"],
    )
    rng = np.random.default_rng(1120001)
    maximum_raw_delta = 0.0
    changed = 0
    for _ in range(steps):
        feed = {
            "obs": rng.normal(size=(1, 115)).astype(np.float32),
            "previous_action": rng.uniform(
                -0.5, 0.5, size=(1, 14)
            ).astype(np.float32),
            "h_in": rng.normal(size=(1, 64)).astype(np.float32),
        }
        before = left.run(["raw_continuous_actions"], feed)[0]
        after = right.run(["raw_continuous_actions"], feed)[0]
        delta = t98.max_abs(before, after)
        maximum_raw_delta = max(maximum_raw_delta, delta)
        changed += int(delta > 1.0e-7)
    return {
        "steps": steps,
        "changed_steps": changed,
        "maximum_raw_action_delta": maximum_raw_delta,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu-contract-authorized", action="store_true")
    args = parser.parse_args()
    if not args.cpu_contract_authorized:
        raise PermissionError("T112 requires --cpu-contract-authorized")
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T112 result: {path}")
    if WORK.exists():
        raise FileExistsError(f"refusing to reuse T112 work root: {WORK}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T112 execution requires a clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    validate_prereg(prereg)
    WORK.mkdir(parents=True)
    playground = Path(prereg["playground"]["path"])
    source_path = Path(prereg["assets"]["source_checkpoint"]["path"])
    source_graph = Path(prereg["assets"]["source_raw_onnx"]["path"])
    topology = Path(prereg["assets"]["cpu_topology_template"]["path"])
    reference = Path(prereg["assets"]["reference_features"]["path"])
    gate_asset = Path(prereg["assets"]["hidden_gate_static_asset"]["path"])
    source, remap = cpu_remap(source_path, topology)
    transform = t109.transform(source_graph, EXPECTED)

    command = t98.training_command(
        python=Path(sys.executable),
        playground=playground,
        output=OUTPUT,
        reference=reference,
        restore=CPU_SOURCE,
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
            f"T112 CPU training failed rc={completed.returncode}\n"
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
        raise RuntimeError("T112 export steps changed")

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

    cases = t98.trace_cases(prereg)
    step_zero_trace = trace_equivalence(EXPECTED, graphs[0], cases)
    step_zero_chain = t98.compare_random_chain(EXPECTED, graphs[0])
    postupdate = update_binding(graphs[0], graphs[1024], cases)
    random_binding = random_update_binding(graphs[0], graphs[1024])
    graph_contracts = {
        str(step): {
            "receipt": t20.receipt(graph),
            "io": t98.graph_io(graph),
            "chain": t98.graph_chain(graph),
        }
        for step, graph in sorted(graphs.items())
    }
    thresholds = prereg["thresholds"]
    readback = (
        "T98_HIDDEN_EXPERT_CONTINUATION="
        "strata=8,broad=1,isolated=7,"
        "gate=always_on,"
        "actor_updates=negative_adapter_location_only"
    )
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
    checks = {
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
        "source_cpu_remap_exact": (
            remap["structure_exact"]
            and remap["maximum_abs_error"] == 0.0
            and remap["tree_finite"]
        ),
        "exact_always_on_transform": (
            transform["node_count_exact"]
            and transform["abi_exact"]
            and transform["initializers_exact"]
            and transform["replacement_exact"]
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
        "trees_finite": finite_tree(initial) and finite_tree(final),
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
        "no_formal_behavior_hosted_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed
    result: dict[str, Any] = {
        "schema_version": "open_duck.t112_always_on_trainthrough_result.v1",
        "status": (
            "PASS_T112_ALWAYS_ON_TRAINTHROUGH_CPU_CONTRACT"
            if passed
            else "HOLD_T112_ALWAYS_ON_TRAINTHROUGH_CPU_CONTRACT"
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
        "source_remap": remap,
        "always_on_transform": transform,
        "training": {
            "command": command,
            "elapsed_seconds": elapsed,
            "log": t20.receipt(log),
            "initial_checkpoint": t20.directory_receipt(checkpoints[0]),
            "final_checkpoint": t20.directory_receipt(checkpoints[1024]),
            "graphs": graph_contracts,
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
                "# T112 always-on train-through CPU result",
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
                    "- Updated trace raw / deployed changed fraction: "
                    f"`{postupdate['raw_changed_fraction']:.6f} / "
                    f"{postupdate['final_changed_fraction']:.6f}`"
                ),
                (
                    "- Random maximum raw-action delta: "
                    f"`{random_binding['maximum_raw_action_delta']:.9f}`"
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
