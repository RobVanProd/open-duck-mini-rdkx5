#!/usr/bin/env python3
"""Build zero-update T78-half calibration-FiLM T95 assets."""

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
import jax.numpy as jnp
import numpy as np
from orbax import checkpoint as ocp


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
DEFAULT_OUTPUT_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-policy"
    r"\t95_film_conditioned_assets_v1"
)
EXPECTED_CONTEXT_KEYS = {
    "context_film_scale",
}
PARITY_TICKS = 1024


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


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


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


def expand_checkpoint(
    source: list[Any],
    policy_template: dict[str, Any],
) -> tuple[list[Any], dict[str, Any]]:
    expanded = copy.deepcopy(source)
    initialized = flax.core.unfreeze(policy_template)
    source_policy = flax.core.unfreeze(source[1])
    initialized_params = initialized["params"]
    source_params = source_policy["params"]
    added = set(initialized_params) - set(source_params)
    missing = set(source_params) - set(initialized_params)
    if added != EXPECTED_CONTEXT_KEYS or missing:
        raise RuntimeError(
            f"T95 actor expansion changed: added={added}, missing={missing}"
        )
    for key, value in source_params.items():
        initialized_params[key] = copy.deepcopy(value)
    for key in EXPECTED_CONTEXT_KEYS:
        leaves = jax.tree_util.tree_leaves(initialized_params[key])
        if not leaves or any(np.count_nonzero(np.asarray(leaf)) for leaf in leaves):
            raise RuntimeError(f"T95 FiLM path not exact zero: {key}")
    expanded[1] = initialized

    normalizer = expanded[0]
    count = np.float32(np.asarray(normalizer["count"]["lo"]))
    neutral = {
        "calibration_context": 64,
        "policy_previous_action": 14,
    }
    for name, width in neutral.items():
        if name in normalizer["mean"]:
            raise RuntimeError(f"T95 normalizer key already exists: {name}")
        normalizer["mean"][name] = jnp.zeros(width, dtype=jnp.float32)
        normalizer["std"][name] = jnp.ones(width, dtype=jnp.float32)
        normalizer["summed_variance"][name] = jnp.full(
            width,
            count,
            dtype=jnp.float32,
        )
    return expanded, {
        "added_actor_parameter_families": sorted(added),
        "added_normalizer_keys": sorted(neutral),
        "context_parameters_exact_zero": True,
        "source_actor_keys_preserved": sorted(source_params),
    }


def describe_onnx(path: Path) -> dict[str, dict[str, list[int]]]:
    import onnx

    model = onnx.load(path)

    def values(items) -> dict[str, list[int]]:
        return {
            item.name: [
                dim.dim_value for dim in item.type.tensor_type.shape.dim
            ]
            for item in items
        }

    return {
        "inputs": values(model.graph.input),
        "outputs": values(model.graph.output),
    }


def step_zero_parity(
    source_path: Path,
    expanded_path: Path,
) -> dict[str, Any]:
    import onnxruntime as ort

    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    source = ort.InferenceSession(
        str(source_path),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )
    expanded = ort.InferenceSession(
        str(expanded_path),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )
    expected_source = {
        "inputs": {
            "obs": [1, 115],
            "previous_action": [1, 14],
            "h_in": [1, 64],
        },
        "outputs": {
            "continuous_actions": [1, 14],
            "previous_action_out": [1, 14],
            "h_out": [1, 64],
        },
    }
    expected_expanded = {
        "inputs": {
            **expected_source["inputs"],
            "calibration_context": [1, 64],
        },
        "outputs": expected_source["outputs"],
    }
    if describe_onnx(source_path) != expected_source:
        raise RuntimeError("T78-half source ABI changed")
    if describe_onnx(expanded_path) != expected_expanded:
        raise RuntimeError("T95 step-zero ABI changed")

    rng = np.random.Generator(np.random.PCG64(1010121))
    source_previous = np.zeros((1, 14), dtype=np.float32)
    source_hidden = np.zeros((1, 64), dtype=np.float32)
    expanded_previous = source_previous.copy()
    expanded_hidden = source_hidden.copy()
    max_errors = {
        "continuous_actions": 0.0,
        "previous_action_out": 0.0,
        "h_out": 0.0,
    }
    bit_exact = {name: True for name in max_errors}
    zero_actions_exact = True
    for tick in range(PARITY_TICKS):
        observation = rng.normal(
            0.0,
            0.25,
            size=(1, 115),
        ).astype(np.float32)
        observation[:, 101:115] = rng.uniform(
            -0.8,
            0.8,
            size=(1, 14),
        ).astype(np.float32)
        observation[:, 13:27] = rng.uniform(
            -0.12,
            0.12,
            size=(1, 14),
        ).astype(np.float32)
        if tick % 4 == 0:
            observation[:, 6:13] = 0.0
            observation[:, 99:101] = np.asarray(
                [1.0, 0.0],
                dtype=np.float32,
            )
        else:
            observation[:, 6] = np.float32(
                (0.074, 0.077, 0.080)[tick % 3]
            )
        context = rng.normal(
            0.0,
            0.7,
            size=(1, 64),
        ).astype(np.float32)
        source_outputs = source.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": observation,
                "previous_action": source_previous,
                "h_in": source_hidden,
            },
        )
        expanded_outputs = expanded.run(
            ["continuous_actions", "previous_action_out", "h_out"],
            {
                "obs": observation,
                "previous_action": expanded_previous,
                "h_in": expanded_hidden,
                "calibration_context": context,
            },
        )
        for name, left, right in zip(
            max_errors,
            source_outputs,
            expanded_outputs,
            strict=True,
        ):
            max_errors[name] = max(
                max_errors[name],
                float(
                    np.max(
                        np.abs(
                            left.astype(float) - right.astype(float)
                        )
                    )
                ),
            )
            bit_exact[name] &= bool(np.array_equal(left, right))
        if tick % 4 == 0:
            zero_actions_exact &= (
                np.count_nonzero(expanded_outputs[0]) == 0
            )
        source_previous = np.asarray(source_outputs[1], dtype=np.float32)
        source_hidden = np.asarray(source_outputs[2], dtype=np.float32)
        expanded_previous = np.asarray(
            expanded_outputs[1],
            dtype=np.float32,
        )
        expanded_hidden = np.asarray(
            expanded_outputs[2],
            dtype=np.float32,
        )
    return {
        "ticks": PARITY_TICKS,
        "source_io": expected_source,
        "expanded_io": expected_expanded,
        "maximum_abs_errors": max_errors,
        "bit_exact": bit_exact,
        "all_outputs_bit_exact": all(bit_exact.values()),
        "zero_command_actions_exact_zero": bool(zero_actions_exact),
        "arbitrary_context_has_zero_step_effect": all(
            value == 0.0 for value in max_errors.values()
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--cpu-template", type=Path, required=True)
    parser.add_argument("--source-policy", type=Path, required=True)
    parser.add_argument("--calibrator", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("T95 asset build requires --execute")
    playground = args.playground_root.resolve()
    source_path = args.source_checkpoint.resolve()
    cpu_template = args.cpu_template.resolve()
    source_policy = args.source_policy.resolve()
    calibrator = args.calibrator.resolve()
    output = args.output_root.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to reuse T95 assets: {output}")
    if sha256(calibrator) != (
        "0f3aebfd9946a6271fdb14adec3d68d556648f270984639d372c973a7d7dc576"
    ):
        raise RuntimeError("T95 calibrator changed")
    output.mkdir(parents=True)

    sys.path.insert(0, str(playground))
    from playground.common.t10_response_conditioned_v121_networks import (
        export_response_conditioned_v121_onnx,
        make_response_conditioned_v121_ppo_networks,
    )

    observation_size = {
        "state": (115,),
        "privileged_state": (226,),
        "policy_hidden": (64,),
        "calibration_context": (64,),
        "policy_previous_action": (14,),
    }
    networks = make_response_conditioned_v121_ppo_networks(
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
    )
    policy_template = networks.policy_network.init(
        jax.random.PRNGKey(1010121)
    )

    checkpointer = ocp.PyTreeCheckpointer()
    template_tree = checkpointer.restore(str(cpu_template))
    source_tree = checkpointer.restore(
        str(source_path),
        item=template_tree,
        restore_args=orbax_utils.restore_args_from_target(template_tree),
    )
    expanded_tree, expansion = expand_checkpoint(
        source_tree,
        policy_template,
    )
    expanded_checkpoint = output / "expanded_checkpoint"
    checkpointer.save(
        str(expanded_checkpoint),
        expanded_tree,
        force=True,
        save_args=orbax_utils.save_args_from_target(expanded_tree),
    )
    restored = checkpointer.restore(
        str(expanded_checkpoint),
        item=expanded_tree,
        restore_args=orbax_utils.restore_args_from_target(expanded_tree),
    )
    round_trip_structure, round_trip_error = tree_max_error(
        expanded_tree,
        restored,
    )
    step_zero = output / "t95_t78_half_step_zero.onnx"
    export_receipt = export_response_conditioned_v121_onnx(
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
        action_velocity_limits_rad_s=(
            1.0,
            0.75,
            1.4736209064722061,
            1.4300791546702385,
            1.3976470567286015,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.75,
            1.25,
            1.0,
            1.2215287424623966,
        ),
        control_dt=0.02,
        action_scale=0.25,
    )
    parity = step_zero_parity(source_policy, step_zero)
    checks = {
        "cpu_only": (
            jax.default_backend() == "cpu"
            and all(device.platform == "cpu" for device in jax.devices())
        ),
        "source_checkpoint_restored": bool(source_tree),
        "source_actor_keys_preserved": bool(
            expansion["source_actor_keys_preserved"]
        ),
        "exact_one_film_parameter_family_added": (
            set(expansion["added_actor_parameter_families"])
            == EXPECTED_CONTEXT_KEYS
        ),
        "context_parameters_exact_zero": expansion[
            "context_parameters_exact_zero"
        ],
        "neutral_normalizer_keys_added": (
            expansion["added_normalizer_keys"]
            == ["calibration_context", "policy_previous_action"]
        ),
        "expanded_checkpoint_round_trip_exact": (
            round_trip_structure and round_trip_error == 0.0
        ),
        "step_zero_source_action_and_state_bit_exact": parity[
            "all_outputs_bit_exact"
        ],
        "step_zero_arbitrary_context_has_no_effect": parity[
            "arbitrary_context_has_zero_step_effect"
        ],
        "step_zero_x0_exact": parity[
            "zero_command_actions_exact_zero"
        ],
        "step_zero_abi_exact": export_receipt["inputs"]
        == parity["expanded_io"]["inputs"]
        and export_receipt["outputs"]
        == parity["expanded_io"]["outputs"],
        "optimizer_steps_zero": True,
        "simulator_behavior_cells_zero": True,
        "robot_or_rdk_access_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    basis = {
        "schema_version": "open_duck.t95_film_assets.v1",
        "status": (
            "PASS_T95_FILM_CONDITIONED_ASSETS"
            if not failed
            else "HOLD_T95_FILM_CONDITIONED_ASSETS"
        ),
        "failed_checks": failed,
        "checks": checks,
        "sources": {
            "playground_manifest": receipt(
                playground / "T95_COMPOSED_SOURCE_MANIFEST.json"
            ),
            "source_checkpoint": directory_receipt(source_path),
            "cpu_template": directory_receipt(cpu_template),
            "source_policy": receipt(source_policy),
            "calibrator": receipt(calibrator),
            "t93_adapter_audit": receipt(
                ANALYSIS / "t93_adapter_authority_result.json"
            ),
            "t94_calibration_manifold": receipt(
                ANALYSIS / "t94_r2_calibration_manifold_result.json"
            ),
            "t94_reporting_correction": receipt(
                ANALYSIS / "t94_home_offset_reporting_correction.json"
            ),
        },
        "assets": {
            "expanded_checkpoint": directory_receipt(
                expanded_checkpoint
            ),
            "step_zero_onnx": receipt(step_zero),
        },
        "expansion": expansion,
        "checkpoint_round_trip": {
            "structure_exact": round_trip_structure,
            "maximum_abs_error": round_trip_error,
        },
        "step_zero_export": export_receipt,
        "step_zero_parity": parity,
        "execution": {
            "optimizer_steps": 0,
            "simulator_behavior_cells": 0,
            "robot_or_rdk_access": 0,
        },
    }
    manifest = {
        **basis,
        "manifest_sha256": canonical_sha256(basis),
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            manifest,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(manifest["status"])
    print(f"manifest={manifest_path}")
    print(f"manifest_sha256={manifest['manifest_sha256']}")
    print(f"file_sha256={sha256(manifest_path)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
