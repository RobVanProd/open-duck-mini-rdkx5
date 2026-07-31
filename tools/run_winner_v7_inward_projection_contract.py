#!/usr/bin/env python3
"""Run the frozen winner-v7 inward-rounded final-projection graph contract."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
PREREGISTRATION = ANALYSIS / "winner_v7_inward_projection_preregistration.json"
IMPORTER = ROOT / "tools/import_winner_v7_inward_projection_contract.py"
MARGIN = np.float32(4.0) * np.finfo(np.float32).eps
MAX_PERTURBATION = np.float32(8.0) * np.finfo(np.float32).eps


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def initializers(model: onnx.ModelProto) -> dict[str, np.ndarray]:
    return {
        item.name: np.asarray(numpy_helper.to_array(item))
        for item in model.graph.initializer
    }


def abi(model: onnx.ModelProto) -> dict[str, list[dict[str, Any]]]:
    def describe(values: Any) -> list[dict[str, Any]]:
        rows = []
        for value in values:
            tensor = value.type.tensor_type
            rows.append({
                "name": value.name,
                "dtype": "float32"
                if tensor.elem_type == TensorProto.FLOAT
                else TensorProto.DataType.Name(tensor.elem_type).lower(),
                "shape": [dimension.dim_value for dimension in tensor.shape.dim],
            })
        return rows

    return {
        "inputs": describe(model.graph.input),
        "outputs": describe(model.graph.output),
    }


def transform(source: onnx.ModelProto) -> onnx.ModelProto:
    model = copy.deepcopy(source)
    for node in model.graph.node:
        for index, output in enumerate(node.output):
            if output == "continuous_actions":
                node.output[index] = "v7_source_continuous_actions"
            elif output == "previous_action_out":
                node.output[index] = "v7_source_previous_action_out"
    source_delta = initializers(source)["max_action_delta"].astype(np.float32)
    safe_delta = source_delta - MARGIN
    model.graph.initializer.extend([
        numpy_helper.from_array(safe_delta, name="v7_safe_max_action_delta"),
        numpy_helper.from_array(np.asarray(-1.0, np.float32), name="v7_action_minimum"),
        numpy_helper.from_array(np.asarray(1.0, np.float32), name="v7_action_maximum"),
        numpy_helper.from_array(np.asarray(MARGIN, np.float32), name="v7_inward_margin"),
    ])
    model.graph.node.extend([
        helper.make_node(
            "Clip",
            ["v7_source_continuous_actions", "v7_action_minimum", "v7_action_maximum"],
            ["v7_absolute_action"],
        ),
        helper.make_node(
            "Sub", ["previous_action", "v7_safe_max_action_delta"], ["v7_action_min"]
        ),
        helper.make_node(
            "Add", ["previous_action", "v7_safe_max_action_delta"], ["v7_action_max"]
        ),
        helper.make_node(
            "Min", ["v7_absolute_action", "v7_action_max"], ["v7_action_below_max"]
        ),
        helper.make_node(
            "Max", ["v7_action_below_max", "v7_action_min"], ["continuous_actions"]
        ),
        helper.make_node("Identity", ["continuous_actions"], ["previous_action_out"]),
    ])
    del model.graph.output[:]
    model.graph.output.extend([
        helper.make_tensor_value_info("continuous_actions", TensorProto.FLOAT, [1, 14]),
        helper.make_tensor_value_info("previous_action_out", TensorProto.FLOAT, [1, 14]),
    ])
    model.graph.name = "winner_v7_inward_rounded_protected_base"
    model.producer_name = "open-duck-winner-v7"
    model.ir_version = min(model.ir_version, 10)
    onnx.checker.check_model(model)
    return model


def graph_change_contract(
    source: onnx.ModelProto, transformed: onnx.ModelProto
) -> dict[str, Any]:
    source_inits = initializers(source)
    output_inits = initializers(transformed)
    source_initializers_exact = all(
        name in output_inits and np.array_equal(value, output_inits[name])
        for name, value in source_inits.items()
    )
    original_nodes_exact_after_name_restore = True
    for source_node, output_node in zip(
        source.graph.node, transformed.graph.node[: len(source.graph.node)], strict=True
    ):
        candidate = copy.deepcopy(output_node)
        for index, output in enumerate(candidate.output):
            if output == "v7_source_continuous_actions":
                candidate.output[index] = "continuous_actions"
            elif output == "v7_source_previous_action_out":
                candidate.output[index] = "previous_action_out"
        original_nodes_exact_after_name_restore &= (
            source_node.SerializeToString() == candidate.SerializeToString()
        )
    source_delta = source_inits["max_action_delta"].astype(np.float32)
    safe_delta = output_inits["v7_safe_max_action_delta"].astype(np.float32)
    return {
        "source_initializers_exact": source_initializers_exact,
        "original_nodes_exact_after_output_rename_restore": (
            original_nodes_exact_after_name_restore
        ),
        "appended_node_count": len(transformed.graph.node) - len(source.graph.node),
        "appended_initializer_names": sorted(set(output_inits) - set(source_inits)),
        "input_interface_exact": [
            item.SerializeToString() for item in source.graph.input
        ]
        == [item.SerializeToString() for item in transformed.graph.input],
        "safe_delta_exact": np.array_equal(safe_delta, source_delta - MARGIN),
        "margin_exact": float(output_inits["v7_inward_margin"]) == float(MARGIN),
    }


def random_observation(rng: np.random.Generator, command_x: float) -> np.ndarray:
    obs = rng.normal(0.0, 0.25, (1, 115)).astype(np.float32)
    obs[:, 6] = np.float32(command_x)
    obs[:, 97:99] = 1.0
    return obs


def stress_contract(
    source_session: ort.InferenceSession,
    output_session: ort.InferenceSession,
    source_delta: np.ndarray,
    seed: int,
    cases: int,
) -> dict[str, Any]:
    rng = np.random.Generator(np.random.PCG64(seed))
    strict_bounds = True
    finite = True
    state_equals_action = True
    changed = 0
    maximum_excess = 0.0
    maximum_perturbation = 0.0
    for _ in range(cases):
        obs = random_observation(rng, 0.077)
        previous = rng.uniform(-1.0, 1.0, (1, 14)).astype(np.float32)
        source_action = source_session.run(
            ["continuous_actions"], {"obs": obs, "previous_action": previous}
        )[0]
        action, state = output_session.run(
            ["continuous_actions", "previous_action_out"],
            {"obs": obs, "previous_action": previous},
        )
        excess = np.maximum(np.abs(action - previous) - source_delta, 0.0)
        perturbation = float(np.max(np.abs(action - source_action)))
        maximum_excess = max(maximum_excess, float(np.max(excess)))
        maximum_perturbation = max(maximum_perturbation, perturbation)
        changed += not np.array_equal(action, source_action)
        strict_bounds &= bool(
            np.max(np.abs(action)) <= 1.0 and np.max(excess) == 0.0
        )
        finite &= bool(np.isfinite(action).all() and np.isfinite(state).all())
        state_equals_action &= np.array_equal(action, state)
    return {
        "seed": seed,
        "cases": cases,
        "strict_bounds_without_tolerance": strict_bounds,
        "all_finite": finite,
        "state_equals_action_bit_exact": state_equals_action,
        "changed_cases": changed,
        "maximum_excess": maximum_excess,
        "maximum_perturbation": maximum_perturbation,
    }


def chained_contract(
    source_session: ort.InferenceSession,
    output_session: ort.InferenceSession,
    model_inits: dict[str, np.ndarray],
    seed: int,
    command_x: float,
    ticks: int,
) -> dict[str, Any]:
    rng = np.random.Generator(np.random.PCG64(seed))
    previous = np.zeros((1, 14), dtype=np.float32)
    history = [previous.copy(), previous.copy(), previous.copy()]
    home = model_inits["guard_home"].astype(np.float32)
    source_delta = model_inits["max_action_delta"].astype(np.float32)
    strict_bounds = True
    finite = True
    zero_exact = True
    maximum_excess = 0.0
    maximum_perturbation = 0.0
    changed = 0
    for tick in range(ticks):
        obs = random_observation(rng, command_x)
        phase = np.float32((2.0 * np.pi * tick) / 20.0)
        obs[:, 13:27] = previous * np.float32(0.25)
        obs[:, 27:41] = 0.0
        obs[:, 41:55] = history[0]
        obs[:, 55:69] = history[1]
        obs[:, 69:83] = history[2]
        obs[:, 83:97] = home + previous * np.float32(0.25)
        obs[:, 99:101] = [np.cos(phase), np.sin(phase)]
        source_action = source_session.run(
            ["continuous_actions"], {"obs": obs, "previous_action": previous}
        )[0]
        action, state = output_session.run(
            ["continuous_actions", "previous_action_out"],
            {"obs": obs, "previous_action": previous},
        )
        excess = np.maximum(np.abs(action - previous) - source_delta, 0.0)
        maximum_excess = max(maximum_excess, float(np.max(excess)))
        maximum_perturbation = max(
            maximum_perturbation, float(np.max(np.abs(action - source_action)))
        )
        changed += not np.array_equal(action, source_action)
        strict_bounds &= bool(
            np.max(np.abs(action)) <= 1.0 and np.max(excess) == 0.0
        )
        finite &= bool(np.isfinite(action).all() and np.isfinite(state).all())
        if command_x == 0.0:
            zero_exact &= bool(
                np.array_equal(action, np.zeros_like(action))
                and np.array_equal(state, np.zeros_like(state))
            )
        history = [state.copy(), history[0], history[1]]
        previous = state
    return {
        "seed": seed,
        "command_x": command_x,
        "ticks": ticks,
        "strict_bounds_without_tolerance": strict_bounds,
        "all_finite": finite,
        "zero_action_and_state_exact": zero_exact,
        "changed_ticks": changed,
        "maximum_excess": maximum_excess,
        "maximum_perturbation": maximum_perturbation,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    work_root = args.work_root.resolve()
    output = args.output.resolve()
    if work_root.exists() or output.exists():
        raise FileExistsError("winner-v7 formal output already exists")
    work_root.mkdir(parents=True)
    output.parent.mkdir(parents=True, exist_ok=True)

    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    observed_hashes = {
        "runner": sha256(Path(__file__)),
        "importer": sha256(IMPORTER),
        "numeric_attribution": sha256(
            ANALYSIS / "winner_v6b_numeric_hold_attribution.json"
        ),
        "protected_half": sha256(
            ROOT / preregistration["protected_checkpoints"]["half"]["path"]
        ),
        "protected_final": sha256(
            ROOT / preregistration["protected_checkpoints"]["final"]["path"]
        ),
    }
    if observed_hashes != preregistration["input_hashes"]:
        raise ValueError("winner-v7 frozen input hash mismatch")

    policies = []
    for index, label in enumerate(("half", "final")):
        source_path = ROOT / preregistration["protected_checkpoints"][label]["path"]
        output_path = work_root / f"winner_v7_{label}_inward_projection.onnx"
        source_model = onnx.load(source_path)
        output_model = transform(source_model)
        onnx.save(output_model, output_path)
        source_session = ort.InferenceSession(
            str(source_path), providers=["CPUExecutionProvider"]
        )
        output_session = ort.InferenceSession(
            str(output_path), providers=["CPUExecutionProvider"]
        )
        source_inits = initializers(source_model)
        policies.append({
            "label": label,
            "source_path": str(source_path.relative_to(ROOT)).replace("\\", "/"),
            "source_sha256": sha256(source_path),
            "output_filename": output_path.name,
            "output_sha256": sha256(output_path),
            "output_bytes": output_path.stat().st_size,
            "abi": abi(output_model),
            "graph_change": graph_change_contract(source_model, output_model),
            "stress": stress_contract(
                source_session,
                output_session,
                source_inits["max_action_delta"].astype(np.float32),
                60770 + index,
                4096,
            ),
            "x0_chain": chained_contract(
                source_session,
                output_session,
                source_inits,
                60780 + index,
                0.0,
                256,
            ),
            "moving_chain": chained_contract(
                source_session,
                output_session,
                source_inits,
                60742 + index * 10,
                0.077,
                32,
            ),
        })

    expected_abi = preregistration["expected_abi"]
    checks = {
        "frozen_input_hashes_exact": observed_hashes
        == preregistration["input_hashes"],
        "cpu_provider_only": all(
            row["stress"]["all_finite"] and row["x0_chain"]["all_finite"]
            for row in policies
        ),
        "both_output_abis_exact": all(row["abi"] == expected_abi for row in policies),
        "source_graphs_preserved_except_reviewed_append": all(
            row["graph_change"]["source_initializers_exact"]
            and row["graph_change"]["original_nodes_exact_after_output_rename_restore"]
            and row["graph_change"]["input_interface_exact"]
            and row["graph_change"]["safe_delta_exact"]
            and row["graph_change"]["margin_exact"]
            and row["graph_change"]["appended_node_count"] == 6
            and row["graph_change"]["appended_initializer_names"]
            == [
                "v7_action_maximum",
                "v7_action_minimum",
                "v7_inward_margin",
                "v7_safe_max_action_delta",
            ]
            for row in policies
        ),
        "all_8192_arbitrary_stress_cases_strictly_bounded": all(
            row["stress"]["strict_bounds_without_tolerance"]
            and row["stress"]["state_equals_action_bit_exact"]
            and row["stress"]["changed_cases"] > 0
            for row in policies
        ),
        "both_256_tick_x0_chains_exact_zero": all(
            row["x0_chain"]["zero_action_and_state_exact"]
            and row["x0_chain"]["strict_bounds_without_tolerance"]
            for row in policies
        ),
        "both_32_tick_moving_chains_strictly_bounded": all(
            row["moving_chain"]["strict_bounds_without_tolerance"]
            for row in policies
        ),
        "maximum_perturbation_within_eight_epsilons": all(
            max(
                row["x0_chain"]["maximum_perturbation"],
                row["moving_chain"]["maximum_perturbation"],
            )
            <= float(MAX_PERTURBATION)
            for row in policies
        ),
        "no_behavior_or_training_executed": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_WINNER_V7_INWARD_PROJECTION_TRANSFORM_CONTRACT"
        if not failed
        else "HOLD_WINNER_V7_INWARD_PROJECTION_TRANSFORM_CONTRACT"
    )
    payload = {
        "schema_version": "winner_v7.inward_projection_transform_contract_result.v1",
        "status": status,
        "decision": (
            "AUTHORIZE_SEPARATE_FULL_BEHAVIOR_REVALIDATION_PREREGISTRATION_ONLY"
            if not failed
            else "CLOSE_WINNER_V7_INWARD_PROJECTION_ROUTE"
        ),
        "checks": checks,
        "failed_checks": failed,
        "input_hashes": observed_hashes,
        "preregistration_sha256": sha256(PREREGISTRATION),
        "margin": {
            "normalized_action": float(MARGIN),
            "target_rad": float(MARGIN) * 0.25,
            "rate_rad_s": float(MARGIN) * 0.25 / 0.02,
            "maximum_allowed_perturbation": float(MAX_PERTURBATION),
        },
        "policies": policies,
        "authority": {
            "full_behavior_revalidation_preregistration_design": not failed,
            "behavior_evaluation": False,
            "dynamic_calibrator_or_training": False,
            "colab_gpu_runtime_robot_torque_motion": False,
            "robot_clearance": False,
        },
    }
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(status)
    print(f"RESULT={output}")
    print(f"RESULT_SHA256={sha256(output)}")
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
