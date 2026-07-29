#!/usr/bin/env python3
"""Run T98's preregistered fixed-hidden-gate expert CPU contract."""

from __future__ import annotations

import argparse
import copy
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
import jax.numpy as jnp
import numpy as np
import onnx
from onnx import TensorProto, helper
import onnxruntime as ort
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs" / "analysis"
sys.path.insert(0, str(TOOLS))

import audit_t97_hidden_gate as t97  # noqa: E402
import run_t20_support_trainthrough_one_update as t20  # noqa: E402
import run_t55_dynamic_single_support_cpu_contract as t55  # noqa: E402
import run_t77_endpoint_joint_adapter_cpu_contract as t77  # noqa: E402
from run_winner_v111_peak_torque_cpu_smoke import tree_errors  # noqa: E402


PREREG = ANALYSIS / "t98_hidden_expert_cpu_preregistration.json"
RESULT = ANALYSIS / "t98_hidden_expert_cpu_result.json"
MARKDOWN = ANALYSIS / "T98_HIDDEN_EXPERT_CPU_RESULT_20260728.md"
WORK = Path("D:/CodexArtifacts/open-duck-policy/t98_hidden_expert_cpu_v1")
MATERIALIZED = WORK / "t78_final_hidden_expert_source"
OUTPUT = WORK / "smoke"
INSPECTION = WORK / "inspection"
EXTRA_HEAD = "negative_adapter_location"


def validate_prereg(value: dict[str, Any]) -> None:
    basis = {
        key: item
        for key, item in value.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        value.get("status")
        != "PREREGISTERED_T98_HIDDEN_EXPERT_CPU_CONTRACT"
        or value.get("failed_checks")
        or t20.canonical_sha256(basis)
        != value.get("preregistered_contract_sha256")
    ):
        raise RuntimeError("T98 preregistration identity changed")
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
        raise RuntimeError("T98 composed source inventory changed")


def restore_tree(path: Path, template: Any) -> Any:
    return ocp.PyTreeCheckpointer().restore(
        str(path),
        item=template,
        restore_args=orbax_utils.restore_args_from_target(template),
    )


def finite_tree(value: Any) -> bool:
    return all(
        bool(np.all(np.isfinite(np.asarray(leaf))))
        for leaf in jax.tree_util.tree_leaves(value)
    )


def strip_extra_head(value: Any) -> Any:
    output = copy.deepcopy(value)
    del output[1]["params"][EXTRA_HEAD]
    return output


def materialize_source(
    source_path: Path,
    topology_template_path: Path,
) -> tuple[Any, Any, dict[str, Any]]:
    checkpointer = ocp.PyTreeCheckpointer()
    topology = checkpointer.restore(str(topology_template_path))
    source = restore_tree(source_path, topology)
    materialized = copy.deepcopy(source)
    shared = source[1]["params"]["adapter_location"]
    materialized[1]["params"][EXTRA_HEAD] = {
        "kernel": jnp.zeros_like(shared["kernel"]),
        "bias": jnp.zeros_like(shared["bias"]),
    }
    checkpointer.save(
        str(MATERIALIZED),
        materialized,
        save_args=orbax_utils.save_args_from_target(materialized),
    )
    restored = restore_tree(MATERIALIZED, materialized)
    restored_structure, restored_deltas = tree_errors(materialized, restored)
    stripped_structure, stripped_deltas = tree_errors(
        source, strip_extra_head(restored)
    )
    return source, restored, {
        "source": t20.directory_receipt(source_path),
        "topology_template": t20.directory_receipt(topology_template_path),
        "materialized": t20.directory_receipt(MATERIALIZED),
        "restored_structure_exact": restored_structure,
        "restored_maximum_abs_error": max(
            restored_deltas.values(), default=0.0
        ),
        "protected_source_structure_exact": stripped_structure,
        "protected_source_maximum_abs_error": max(
            stripped_deltas.values(), default=0.0
        ),
        "extra_head_shapes": {
            key: list(np.asarray(value).shape)
            for key, value in restored[1]["params"][EXTRA_HEAD].items()
        },
        "extra_head_nonzero_count": sum(
            int(np.count_nonzero(np.asarray(value)))
            for value in restored[1]["params"][EXTRA_HEAD].values()
        ),
    }


def training_command(
    *,
    python: Path,
    playground: Path,
    output: Path,
    reference: Path,
    restore: Path,
    gate_asset: Path,
) -> list[str]:
    command = t77.training_command(
        python=python,
        output=output,
        reference=reference,
        restore=restore,
    )
    old = "--winner_t77_endpoint_joint_adapter_continuation"
    command[command.index(old)] = "--winner_t98_hidden_expert_continuation"
    index = command.index("--winner_t98_hidden_expert_continuation") + 1
    command[index:index] = [
        "--winner_t98_hidden_gate_asset_path",
        str(gate_asset),
    ]
    return command


def graph_io(path: Path) -> dict[str, Any]:
    session = ort.InferenceSession(
        str(path), providers=["CPUExecutionProvider"]
    )
    return {
        "inputs": {item.name: list(item.shape) for item in session.get_inputs()},
        "outputs": {
            item.name: list(item.shape) for item in session.get_outputs()
        },
        "providers": session.get_providers(),
    }


def graph_chain(path: Path, steps: int = 256) -> dict[str, Any]:
    session = ort.InferenceSession(
        str(path), providers=["CPUExecutionProvider"]
    )
    rng = np.random.default_rng(20260728)
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)
    maximum_action = 0.0
    maximum_hidden = 0.0
    for _ in range(steps):
        obs = rng.normal(size=(1, 115)).astype(np.float32)
        action, previous_out, hidden_out = session.run(
            None,
            {"obs": obs, "previous_action": previous, "h_in": hidden},
        )
        if not all(
            np.all(np.isfinite(value))
            for value in (action, previous_out, hidden_out)
        ):
            raise RuntimeError("T98 ONNX chain became nonfinite")
        maximum_action = max(
            maximum_action, float(np.max(np.abs(action)))
        )
        maximum_hidden = max(
            maximum_hidden, float(np.max(np.abs(hidden_out)))
        )
        previous = previous_out
        hidden = hidden_out
    return {
        "steps": steps,
        "finite": True,
        "maximum_abs_action": maximum_action,
        "maximum_abs_hidden": maximum_hidden,
    }


def inspection_graph(
    source: Path,
    destination: Path,
    names: dict[str, list[int]],
) -> Path:
    model = onnx.load(source)
    existing = {item.name for item in model.graph.output}
    for name, shape in names.items():
        if name not in existing:
            model.graph.output.append(
                helper.make_tensor_value_info(
                    name, TensorProto.FLOAT, shape
                )
            )
    onnx.checker.check_model(model)
    onnx.save(model, destination)
    return destination


def trace_cases(prereg: dict[str, Any]) -> list[dict[str, Any]]:
    t97_prereg = json.loads(
        Path(prereg["assets"]["t97_preregistration"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    ticks = {int(value) for value in t97_prereg["population"]["ticks"]}
    labels = t97_prereg["population"]["labels"]
    cases: list[dict[str, Any]] = []
    for item in t97_prereg["traces"]:
        found: set[int] = set()
        with Path(item["trace"]["path"]).open(encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                tick = int(row["tick"])
                if tick not in ticks:
                    continue
                found.add(tick)
                cases.append(
                    {
                        "checkpoint_id": item["checkpoint_id"],
                        "fit_id": item["fit_id"],
                        "command_x_m_s": float(item["command_x_m_s"]),
                        "population": item["population"],
                        "tick": tick,
                        "label": int(labels[item["population"]]),
                        "feed": {
                            "obs": np.asarray(
                                row["obs_state"], dtype=np.float32
                            )[None, :],
                            "previous_action": np.asarray(
                                row["policy_state_input"][
                                    "previous_action"
                                ],
                                dtype=np.float32,
                            ),
                            "h_in": np.asarray(
                                row["policy_state_input"]["h_in"],
                                dtype=np.float32,
                            ),
                        },
                    }
                )
        if found != ticks:
            raise RuntimeError("T98 trace case population is incomplete")
    return cases


def max_abs(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.max(np.abs(left - right)))


def compare_step_zero(
    source_graph: Path,
    zero_graph: Path,
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    INSPECTION.mkdir(parents=True, exist_ok=True)
    source_inspection = inspection_graph(
        source_graph,
        INSPECTION / "source.onnx",
        {"raw_continuous_actions": [1, 14]},
    )
    zero_inspection = inspection_graph(
        zero_graph,
        INSPECTION / "zero.onnx",
        {
            "raw_continuous_actions": [1, 14],
            "hidden_gate_score": [1, 1],
            "negative_adapter_location": [1, 14],
            "conditional_adapter_location": [1, 14],
        },
    )
    source_session = ort.InferenceSession(
        str(source_inspection), providers=["CPUExecutionProvider"]
    )
    zero_session = ort.InferenceSession(
        str(zero_inspection), providers=["CPUExecutionProvider"]
    )
    names = [
        "continuous_actions",
        "previous_action_out",
        "h_out",
        "raw_continuous_actions",
    ]
    maximum_error = 0.0
    exact_rows = 0
    classifications = 0
    head_zero_rows = 0
    for case in cases:
        expected = source_session.run(names, case["feed"])
        actual = zero_session.run(
            [
                *names,
                "hidden_gate_score",
                "negative_adapter_location",
                "conditional_adapter_location",
            ],
            case["feed"],
        )
        errors = [
            max_abs(left, right)
            for left, right in zip(expected, actual[:4], strict=True)
        ]
        maximum_error = max(maximum_error, *errors)
        exact_rows += int(
            all(
                np.array_equal(left, right)
                for left, right in zip(
                    expected, actual[:4], strict=True
                )
            )
        )
        score = float(actual[4][0, 0])
        classifications += int(
            (1 if score >= 0.0 else -1) == case["label"]
        )
        head_zero_rows += int(
            np.count_nonzero(actual[5]) == 0
            and np.count_nonzero(actual[6]) == 0
        )
    return {
        "rows": len(cases),
        "bit_exact_rows": exact_rows,
        "maximum_abs_error": maximum_error,
        "gate_correct_rows": classifications,
        "zero_head_rows": head_zero_rows,
    }


def compare_final(
    source_graph: Path,
    final_graph: Path,
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    source_session = ort.InferenceSession(
        str(INSPECTION / "source.onnx"),
        providers=["CPUExecutionProvider"],
    )
    final_inspection = inspection_graph(
        final_graph,
        INSPECTION / "final.onnx",
        {
            "raw_continuous_actions": [1, 14],
            "hidden_gate_score": [1, 1],
            "negative_adapter_location": [1, 14],
            "conditional_adapter_location": [1, 14],
        },
    )
    final_session = ort.InferenceSession(
        str(final_inspection), providers=["CPUExecutionProvider"]
    )
    source_names = [
        "continuous_actions",
        "previous_action_out",
        "h_out",
        "raw_continuous_actions",
    ]
    final_names = [
        *source_names,
        "hidden_gate_score",
        "negative_adapter_location",
        "conditional_adapter_location",
    ]
    rows: list[dict[str, Any]] = []
    for case in cases:
        expected = source_session.run(source_names, case["feed"])
        actual = final_session.run(final_names, case["feed"])
        rows.append(
            {
                "label": case["label"],
                "population": case["population"],
                "gate_correct": (
                    (1 if float(actual[4][0, 0]) >= 0.0 else -1)
                    == case["label"]
                ),
                "final_action_delta": max_abs(expected[0], actual[0]),
                "previous_action_delta": max_abs(expected[1], actual[1]),
                "hidden_delta": max_abs(expected[2], actual[2]),
                "raw_action_delta": max_abs(expected[3], actual[3]),
                "negative_head_abs_max": float(
                    np.max(np.abs(actual[5]))
                ),
                "conditional_head_abs_max": float(
                    np.max(np.abs(actual[6]))
                ),
            }
        )
    nominal = [row for row in rows if row["label"] == -1]
    negative = [row for row in rows if row["label"] == 1]
    epsilon = 1.0e-7
    return {
        "rows": len(rows),
        "gate_correct_rows": sum(row["gate_correct"] for row in rows),
        "hidden_maximum_abs_delta": max(
            row["hidden_delta"] for row in rows
        ),
        "nominal_rows": len(nominal),
        "nominal_raw_bit_exact_rows": sum(
            row["raw_action_delta"] == 0.0 for row in nominal
        ),
        "nominal_final_bit_exact_rows": sum(
            row["final_action_delta"] == 0.0
            and row["previous_action_delta"] == 0.0
            for row in nominal
        ),
        "negative_rows": len(negative),
        "negative_raw_changed_rows": sum(
            row["raw_action_delta"] > epsilon for row in negative
        ),
        "negative_final_changed_rows": sum(
            row["final_action_delta"] > epsilon for row in negative
        ),
        "negative_raw_changed_fraction": sum(
            row["raw_action_delta"] > epsilon for row in negative
        )
        / len(negative),
        "negative_final_changed_fraction": sum(
            row["final_action_delta"] > epsilon for row in negative
        )
        / len(negative),
        "maximum_negative_raw_action_delta": max(
            row["raw_action_delta"] for row in negative
        ),
        "maximum_negative_final_action_delta": max(
            row["final_action_delta"] for row in negative
        ),
        "maximum_negative_head_abs": max(
            row["negative_head_abs_max"] for row in negative
        ),
    }


def compare_random_chain(
    source_graph: Path,
    zero_graph: Path,
    steps: int = 256,
) -> dict[str, Any]:
    source = ort.InferenceSession(
        str(source_graph), providers=["CPUExecutionProvider"]
    )
    zero = ort.InferenceSession(
        str(zero_graph), providers=["CPUExecutionProvider"]
    )
    rng = np.random.default_rng(980001)
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)
    exact = 0
    maximum_error = 0.0
    for _ in range(steps):
        feed = {
            "obs": rng.normal(size=(1, 115)).astype(np.float32),
            "previous_action": previous,
            "h_in": hidden,
        }
        expected = source.run(None, feed)
        actual = zero.run(None, feed)
        errors = [
            max_abs(left, right)
            for left, right in zip(expected, actual, strict=True)
        ]
        maximum_error = max(maximum_error, *errors)
        exact += int(
            all(
                np.array_equal(left, right)
                for left, right in zip(expected, actual, strict=True)
            )
        )
        previous = expected[1]
        hidden = expected[2]
    return {
        "steps": steps,
        "bit_exact_steps": exact,
        "maximum_abs_error": maximum_error,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu-contract-authorized", action="store_true")
    args = parser.parse_args()
    if not args.cpu_contract_authorized:
        raise PermissionError(
            "T98 requires --cpu-contract-authorized"
        )
    for path in (RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T98 result: {path}")
    if WORK.exists():
        raise FileExistsError(f"refusing to reuse T98 work root: {WORK}")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal T98 execution requires a clean worktree")

    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    validate_prereg(prereg)
    WORK.mkdir(parents=True)
    playground = Path(prereg["playground"]["path"])
    source_path = Path(prereg["assets"]["source_checkpoint"]["path"])
    topology = Path(prereg["assets"]["topology_template"]["path"])
    reference = Path(prereg["assets"]["reference_features"]["path"])
    source_graph = Path(prereg["assets"]["source_raw_onnx"]["path"])
    gate_asset = Path(prereg["assets"]["hidden_gate"]["path"])
    source, materialized, materialization = materialize_source(
        source_path, topology
    )

    command = training_command(
        python=Path(sys.executable),
        playground=playground,
        output=OUTPUT,
        reference=reference,
        restore=MATERIALIZED,
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
            f"T98 CPU training failed rc={completed.returncode}\n"
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
        raise RuntimeError("T98 export steps changed")

    initial = restore_tree(checkpoints[0], materialized)
    final = restore_tree(checkpoints[1024], materialized)
    restore_structure, restore_deltas = tree_errors(materialized, initial)
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

    cases = trace_cases(prereg)
    step_zero = compare_step_zero(source_graph, graphs[0], cases)
    random_chain = compare_random_chain(source_graph, graphs[0])
    final_binding = compare_final(source_graph, graphs[1024], cases)
    graph_contracts = {
        str(step): {
            "receipt": t20.receipt(graph),
            "io": graph_io(graph),
            "chain": graph_chain(graph),
        }
        for step, graph in sorted(graphs.items())
    }
    thresholds = prereg["thresholds"]
    readback = (
        "T98_HIDDEN_EXPERT_CONTINUATION="
        "strata=8,broad=1,isolated=7,"
        "gate=fixed_live_hidden,"
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
            and "--winner_t77_endpoint_joint_adapter_continuation"
            not in command
            and "--winner_t66_endpoint_core_continuation" not in command
            and command[command.index("--ppo_num_envs") + 1] == "8"
            and command[command.index("--ppo_batch_size") + 1] == "8"
            and command[
                command.index("--winner_t98_hidden_gate_asset_path") + 1
            ]
            == str(gate_asset)
        ),
        "runner_readback_exact": readback in completed.stdout,
        "materialized_protected_source_exact": (
            materialization["protected_source_structure_exact"]
            and materialization[
                "protected_source_maximum_abs_error"
            ]
            == 0.0
            and materialization["extra_head_nonzero_count"] == 0
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
        "step_zero_trace_outputs_bit_exact": (
            step_zero["rows"] == 72
            and step_zero["bit_exact_rows"] == 72
            and step_zero["maximum_abs_error"] == 0.0
            and step_zero["gate_correct_rows"] == 72
            and step_zero["zero_head_rows"] == 72
        ),
        "step_zero_random_chain_bit_exact": (
            random_chain["steps"] == 256
            and random_chain["bit_exact_steps"] == 256
            and random_chain["maximum_abs_error"] == 0.0
        ),
        "final_gate_and_hidden_exact": (
            final_binding["gate_correct_rows"] == 72
            and final_binding["hidden_maximum_abs_delta"] == 0.0
        ),
        "final_nominal_branch_bit_exact": (
            final_binding["nominal_rows"] == 36
            and final_binding["nominal_raw_bit_exact_rows"] == 36
            and final_binding["nominal_final_bit_exact_rows"] == 36
        ),
        "final_negative_raw_action_binding": (
            final_binding["negative_raw_changed_fraction"]
            >= thresholds["minimum_negative_raw_action_changed_fraction"]
            and final_binding["maximum_negative_raw_action_delta"]
            >= thresholds["minimum_maximum_negative_raw_action_delta"]
        ),
        "final_negative_deployed_action_binding": (
            final_binding["negative_final_changed_fraction"]
            >= thresholds["minimum_negative_final_action_changed_fraction"]
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
        "schema_version": "open_duck.t98_hidden_expert_cpu_result.v1",
        "status": (
            "PASS_T98_HIDDEN_EXPERT_CPU_CONTRACT"
            if passed
            else "HOLD_T98_HIDDEN_EXPERT_CPU_CONTRACT"
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
        "materialization": materialization,
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
            "step_zero_trace": step_zero,
            "step_zero_random_chain": random_chain,
            "postupdate_trace": final_binding,
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
                "# T98 hidden-gated expert CPU result",
                "",
                f"- Status: `{result['status']}`",
                f"- Decision: `{result['decision']}`",
                f"- Failed checks: `{failed}`",
                (
                    "- Step-zero trace / random-chain exact: "
                    f"`{step_zero['bit_exact_rows']}/72 / "
                    f"{random_chain['bit_exact_steps']}/256`"
                ),
                (
                    "- Negative raw/final changed fraction: "
                    f"`{final_binding['negative_raw_changed_fraction']:.6f} / "
                    f"{final_binding['negative_final_changed_fraction']:.6f}`"
                ),
                (
                    "- Nominal raw/final exact rows: "
                    f"`{final_binding['nominal_raw_bit_exact_rows']}/36 / "
                    f"{final_binding['nominal_final_bit_exact_rows']}/36`"
                ),
                "- CPU steps / behavior / hosted / robot: `1024 / 0 / 0 / 0`",
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
