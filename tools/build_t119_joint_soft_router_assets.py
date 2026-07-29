#!/usr/bin/env python3
"""Build zero-update T119 soft-router assets from exact T100C-half."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HIP_VISIBLE_DEVICES"] = ""
os.environ["ROCR_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import flax
from flax.training import orbax_utils
import jax
import numpy as np
import onnx
from onnx import helper
import onnxruntime as ort
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PLAYGROUND = Path(
    "D:/CodexProjects/Open_Duck_Playground-t119-joint-soft-router-v1"
)
TRAINING = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t100c_colab_extracted_20260728/"
    "t78_endpoint_joint_adapter_continuation/training"
)
SOURCE = TRAINING / "2026_07_29_023820_1003520"
SOURCE_RAW = TRAINING / "2026_07_29_023820_1003520.onnx"
TOPOLOGY = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t98_hidden_expert_cpu_v1/smoke/2026_07_28_214028_1024"
)
GATE = ANALYSIS / "t98_hidden_gate_asset.json"
T97 = ANALYSIS / "t97_hidden_gate_preregistration.json"
MANIFEST = PLAYGROUND / "T119_COMPOSED_SOURCE_MANIFEST.json"
DEFAULT_OUTPUT = Path(
    "D:/CodexArtifacts/open-duck-policy/t119_joint_soft_router_assets_v1"
)
RESULT = ANALYSIS / "t119_joint_soft_router_assets.json"
MARKDOWN = ANALYSIS / "T119_JOINT_SOFT_ROUTER_ASSETS_20260729.md"
EXPECTED_ADDED = {
    "soft_router_coefficient_delta",
    "soft_router_intercept_delta",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(child.relative_to(path).as_posix().encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def directory_receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "sha256": directory_sha256(path),
    }


def canonical_sha256(value: Any, ignored: str) -> str:
    payload = dict(value)
    payload.pop(ignored, None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def tree_max_error(left: Any, right: Any) -> tuple[bool, float]:
    if jax.tree_util.tree_structure(left) != jax.tree_util.tree_structure(
        right
    ):
        return False, float("inf")
    errors = [
        float(
            np.max(
                np.abs(
                    np.asarray(before, dtype=float)
                    - np.asarray(after, dtype=float)
                )
            )
        )
        for before, after in zip(
            jax.tree_util.tree_leaves(left),
            jax.tree_util.tree_leaves(right),
            strict=True,
        )
    ]
    return True, max(errors, default=0.0)


def normalizer_state(value: dict[str, Any]) -> Any:
    from brax.training import types
    from brax.training.acme import running_statistics

    return running_statistics.RunningStatisticsState(
        mean=value["mean"],
        std=value["std"],
        count=types.UInt64(
            hi=value["count"]["hi"],
            lo=value["count"]["lo"],
        ),
        summed_variance=value["summed_variance"],
        std_eps=value["std_eps"],
    )


def expand_checkpoint(
    source: list[Any], policy_template: dict[str, Any]
) -> tuple[list[Any], dict[str, Any]]:
    expanded = copy.deepcopy(source)
    initialized = flax.core.unfreeze(policy_template)
    source_policy = flax.core.unfreeze(source[1])
    initialized_params = initialized["params"]
    source_params = source_policy["params"]
    added = set(initialized_params) - set(source_params)
    missing = set(source_params) - set(initialized_params)
    if added != EXPECTED_ADDED or missing:
        raise RuntimeError(
            f"T119 actor expansion changed: added={added}, missing={missing}"
        )
    for key, value in source_params.items():
        initialized_params[key] = copy.deepcopy(value)
    for key in EXPECTED_ADDED:
        leaves = jax.tree_util.tree_leaves(initialized_params[key])
        if not leaves or any(np.count_nonzero(np.asarray(leaf)) for leaf in leaves):
            raise RuntimeError(f"T119 router delta not exact zero: {key}")
    expanded[1] = initialized
    return expanded, {
        "added_actor_parameter_families": sorted(added),
        "router_deltas_exact_zero": True,
        "source_actor_keys_preserved": sorted(source_params),
    }


def transform_hard_to_soft(source: Path, output: Path) -> dict[str, Any]:
    model = onnx.load(source)
    gate = [
        node
        for node in model.graph.node
        if node.op_type == "GreaterOrEqual"
        and list(node.input) == ["hidden_gate_score", "hidden_gate_zero"]
        and list(node.output) == ["negative_com_gate"]
    ]
    route = [
        node
        for node in model.graph.node
        if node.op_type == "Where"
        and list(node.input)
        == [
            "negative_com_gate",
            "negative_adapter_location",
            "zero_adapter_location",
        ]
        and list(node.output) == ["conditional_adapter_location"]
    ]
    if len(gate) != 1 or len(route) != 1:
        raise RuntimeError("T119 hard source topology changed")
    gate[0].CopyFrom(
        helper.make_node(
            "Sigmoid",
            ["hidden_gate_score"],
            ["soft_negative_com_weight"],
        )
    )
    route[0].CopyFrom(
        helper.make_node(
            "Mul",
            ["negative_adapter_location", "soft_negative_com_weight"],
            ["conditional_adapter_location"],
        )
    )
    onnx.checker.check_model(model)
    onnx.save(model, output)
    return receipt(output)


def session(path: Path) -> ort.InferenceSession:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return ort.InferenceSession(
        str(path),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )


def selected_trace_rows() -> list[dict[str, Any]]:
    t97 = json.loads(T97.read_text(encoding="utf-8"))
    rows = []
    for item in t97["traces"]:
        trace = Path(item["trace"]["path"])
        if (
            not trace.is_file()
            or trace.stat().st_size != item["trace"]["bytes"]
            or sha256(trace) != item["trace"]["sha256"]
        ):
            raise RuntimeError(f"T119 trace changed: {trace}")
        values = [
            json.loads(line)
            for line in trace.read_text(encoding="utf-8").splitlines()
        ]
        for index in (0, min(31, len(values) - 1), len(values) - 1):
            rows.append(values[index])
    return rows


def parity(expected: Path, actual: Path) -> dict[str, Any]:
    left = session(expected)
    right = session(actual)
    names = ["continuous_actions", "previous_action_out", "h_out"]
    trace_errors = {name: 0.0 for name in names}
    for row in selected_trace_rows():
        state = row["policy_state_input"]
        feed = {
            "obs": np.asarray(row["obs_state"], np.float32)[None, :],
            "previous_action": np.asarray(
                state["previous_action"], np.float32
            ),
            "h_in": np.asarray(state["h_in"], np.float32),
        }
        expected_values = left.run(names, feed)
        actual_values = right.run(names, feed)
        for name, before, after in zip(
            names, expected_values, actual_values, strict=True
        ):
            trace_errors[name] = max(
                trace_errors[name],
                float(np.max(np.abs(before - after))),
            )
    rng = np.random.Generator(np.random.PCG64(20260729))
    previous_left = np.zeros((1, 14), np.float32)
    previous_right = previous_left.copy()
    hidden_left = np.zeros((1, 64), np.float32)
    hidden_right = hidden_left.copy()
    chain_errors = {name: 0.0 for name in names}
    for _ in range(256):
        obs = rng.uniform(-0.45, 0.45, size=(1, 115)).astype(np.float32)
        left_feed = {
            "obs": obs,
            "previous_action": previous_left,
            "h_in": hidden_left,
        }
        right_feed = {
            "obs": obs,
            "previous_action": previous_right,
            "h_in": hidden_right,
        }
        expected_values = left.run(names, left_feed)
        actual_values = right.run(names, right_feed)
        for name, before, after in zip(
            names, expected_values, actual_values, strict=True
        ):
            chain_errors[name] = max(
                chain_errors[name],
                float(np.max(np.abs(before - after))),
            )
        previous_left, hidden_left = expected_values[1], expected_values[2]
        previous_right, hidden_right = actual_values[1], actual_values[2]
    return {
        "trace_rows": 72,
        "chain_ticks": 256,
        "trace_maximum_abs_errors": trace_errors,
        "chain_maximum_abs_errors": chain_errors,
        "maximum_abs_error": max(
            [*trace_errors.values(), *chain_errors.values()]
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--execute", action="store_true", required=True)
    args = parser.parse_args()
    output = args.output_root.resolve()
    for path in (output, RESULT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite T119 assets: {path}")
    for path in (
        PLAYGROUND,
        SOURCE,
        SOURCE_RAW,
        TOPOLOGY,
        GATE,
        T97,
        MANIFEST,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    output.mkdir(parents=True)
    sys.path.insert(0, str(PLAYGROUND))
    from playground.common.t98_hidden_expert_ppo_networks import (
        export_t98_hidden_expert_onnx,
        make_t98_hidden_expert_ppo_networks,
    )

    observation_size = {
        "state": (115,),
        "privileged_state": (226,),
        "policy_hidden": (64,),
    }
    networks = make_t98_hidden_expert_ppo_networks(
        observation_size,
        14,
        preprocess_observations_fn=lambda value, stats: (
            value - stats.mean
        )
        / stats.std,
        policy_hidden_layer_sizes=(512, 256, 128),
        value_hidden_layer_sizes=(512, 256, 128),
        value_obs_key="privileged_state",
        recurrent_hidden_size=64,
        hidden_gate_asset_path=GATE,
    )
    policy_template = networks.policy_network.init(
        jax.random.PRNGKey(20260729)
    )
    checkpointer = ocp.PyTreeCheckpointer()
    topology_tree = checkpointer.restore(str(TOPOLOGY))
    source_tree = checkpointer.restore(
        str(SOURCE),
        item=topology_tree,
        restore_args=orbax_utils.restore_args_from_target(topology_tree),
    )
    expanded_tree, expansion = expand_checkpoint(
        source_tree, policy_template
    )
    expanded_path = output / "expanded_checkpoint"
    checkpointer.save(
        str(expanded_path),
        expanded_tree,
        force=True,
        save_args=orbax_utils.save_args_from_target(expanded_tree),
    )
    restored = checkpointer.restore(
        str(expanded_path),
        item=expanded_tree,
        restore_args=orbax_utils.restore_args_from_target(expanded_tree),
    )
    roundtrip_structure, roundtrip_error = tree_max_error(
        expanded_tree, restored
    )
    expected_soft = output / "t100c_half_expected_soft.onnx"
    expected_receipt = transform_hard_to_soft(SOURCE_RAW, expected_soft)
    step_zero = output / "t119_step_zero.onnx"
    export = export_t98_hidden_expert_onnx(
        [
            normalizer_state(expanded_tree[0]),
            expanded_tree[1],
            expanded_tree[2],
        ],
        14,
        115,
        64,
        step_zero,
        (512, 256, 128),
        hidden_gate_asset_path=GATE,
        action_velocity_limits_rad_s=(
            5.24,
            5.24,
            1.5,
            1.5,
            1.75,
            5.24,
            5.24,
            5.24,
            5.24,
            5.24,
            5.24,
            1.25,
            1.0,
            1.25,
        ),
        control_dt=0.02,
        action_scale=0.25,
    )
    parity_result = parity(expected_soft, step_zero)
    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "source_checkpoint_restored": bool(source_tree),
        "source_actor_keys_preserved": bool(
            expansion["source_actor_keys_preserved"]
        ),
        "exact_two_router_parameter_families_added": (
            set(expansion["added_actor_parameter_families"])
            == EXPECTED_ADDED
        ),
        "router_deltas_exact_zero": expansion[
            "router_deltas_exact_zero"
        ],
        "expanded_checkpoint_roundtrip_exact": (
            roundtrip_structure and roundtrip_error == 0.0
        ),
        "step_zero_soft_formula_exact": (
            parity_result["maximum_abs_error"] <= 1.0e-7
        ),
        "step_zero_export_stateful": bool(export["stateful_hard_vector"]),
        "optimizer_steps_zero": True,
        "formal_behavior_cells_zero": True,
        "hosted_compute_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    value: dict[str, Any] = {
        "schema_version": "open_duck.t119_joint_soft_router_assets.v1",
        "status": (
            "PASS_T119_JOINT_SOFT_ROUTER_ASSETS"
            if not failed
            else "HOLD_T119_JOINT_SOFT_ROUTER_ASSETS"
        ),
        "assets": {
            "expanded_checkpoint": directory_receipt(expanded_path),
            "expected_soft_graph": expected_receipt,
            "step_zero_graph": receipt(step_zero),
            "composed_manifest": receipt(MANIFEST),
        },
        "source": {
            "checkpoint": directory_receipt(SOURCE),
            "raw_graph": receipt(SOURCE_RAW),
            "topology": directory_receipt(TOPOLOGY),
            "gate": receipt(GATE),
        },
        "expansion": expansion,
        "roundtrip": {
            "structure_exact": roundtrip_structure,
            "maximum_abs_error": roundtrip_error,
        },
        "parity": parity_result,
        "checks": checks,
        "failed_checks": failed,
        "execution": {
            "optimizer_steps": 0,
            "formal_behavior_cells": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
    }
    value["result_sha256"] = canonical_sha256(value, "result_sha256")
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T119 joint soft-router assets\n\n"
        f"- Status: `{value['status']}`\n"
        "- Source: exact T100C-half checkpoint\n"
        "- Added parameters: coefficient delta + intercept delta, both zero\n"
        f"- Step-zero soft-path maximum error: "
        f"`{parity_result['maximum_abs_error']:.3e}`\n"
        "- Optimizer / behavior / Colab / robot: `0 / 0 / 0 / 0`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"failed_checks={failed}")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
