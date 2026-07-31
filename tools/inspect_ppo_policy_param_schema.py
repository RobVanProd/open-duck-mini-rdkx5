#!/usr/bin/env python3
"""Inspect Brax PPO policy params and compare them with a BC MLP NPZ.

This is an offline utility. It does not train, deploy, SSH, or touch robot
runtime behavior.
"""

from __future__ import annotations

import argparse
import functools
import json
import os
from pathlib import Path
import sys
from typing import Any


def _shape_dtype_tree(tree: Any) -> dict[str, dict[str, Any]]:
    from flax.traverse_util import flatten_dict

    out: dict[str, dict[str, Any]] = {}
    for key, value in flatten_dict(tree, sep="/").items():
        shape = getattr(value, "shape", None)
        dtype = getattr(value, "dtype", None)
        out[str(key)] = {
            "shape": list(shape) if shape is not None else None,
            "dtype": str(dtype) if dtype is not None else None,
        }
    return out


def _load_bc_npz(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    import numpy as np

    payload = np.load(path, allow_pickle=True)
    shapes = {
        key: {
            "shape": list(payload[key].shape),
            "dtype": str(payload[key].dtype),
        }
        for key in payload.files
    }
    return {
        "path": str(path),
        "keys": payload.files,
        "shapes": shapes,
        "hidden_sizes": (
            payload["hidden_sizes"].astype(int).tolist()
            if "hidden_sizes" in payload.files
            else None
        ),
    }


def _write_markdown(path: Path, report: dict[str, Any]) -> None:
    bc = report.get("bc_npz") or {}
    compatibility = report["compatibility"]
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# PPO Policy Param Schema",
        "",
        f"status: `{report['status']}`",
        "",
        "This is an offline schema inspection artifact. It did not train, deploy,",
        "SSH, run robot tests, or change robot runtime behavior.",
        "",
        "## PPO Contract",
        "",
        f"- observation size: `{report['observation_size']}`",
        f"- privileged observation size: `{report['privileged_observation_size']}`",
        f"- action size: `{report['action_size']}`",
        f"- policy hidden sizes: `{report['policy_hidden_layer_sizes']}`",
        f"- value hidden sizes: `{report['value_hidden_layer_sizes']}`",
        f"- distribution type: `{report['distribution_type']}`",
        f"- policy output size: `{report['policy_output_size']}`",
        "",
        "The actor output is a tanh-normal distribution parameter vector. The",
        "export path splits it into action location and scale logits, then exports",
        "`tanh(loc)` as `continuous_actions`.",
        "",
        "```text",
        "hidden_3[:, 0:14]  -> action loc / deployable ONNX action before tanh",
        "hidden_3[:, 14:28] -> scale logits for PPO exploration",
        "```",
        "",
        "## Policy Param Shapes",
        "",
        "| param | shape | dtype |",
        "|---|---:|---|",
    ]
    for key, meta in report["policy_param_shapes"].items():
        lines.append(f"| `{key}` | `{meta['shape']}` | `{meta['dtype']}` |")

    lines += [
        "",
        "## Value Param Shapes",
        "",
        "| param | shape | dtype |",
        "|---|---:|---|",
    ]
    for key, meta in report["value_param_shapes"].items():
        lines.append(f"| `{key}` | `{meta['shape']}` | `{meta['dtype']}` |")

    if bc:
        lines += [
            "",
            "## BC NPZ",
            "",
            f"- path: `{bc['path']}`",
            f"- hidden sizes: `{bc.get('hidden_sizes')}`",
            "",
            "| key | shape | dtype |",
            "|---|---:|---|",
        ]
        for key, meta in bc["shapes"].items():
            lines.append(f"| `{key}` | `{meta['shape']}` | `{meta['dtype']}` |")

    lines += [
        "",
        "## Compatibility",
        "",
        f"- hidden layers match: `{compatibility['hidden_layers_match']}`",
        f"- output loc branch matches BC action output: `{compatibility['output_loc_matches_bc']}`",
        f"- normalizer shape compatible: `{compatibility['normalizer_shape_compatible']}`",
        "",
        "Recommended mapping:",
        "",
        "```text",
        "normalizer.mean['state'] <- bc.norm[0]",
        "normalizer.std['state']  <- bc.norm[1]",
        "policy.params.hidden_0   <- bc.w0/b0",
        "policy.params.hidden_1   <- bc.w1/b1",
        "policy.params.hidden_2   <- bc.w2/b2",
        "policy.params.hidden_3[:, 0:14]  <- bc.w3/b3",
        "policy.params.hidden_3[:, 14:28] <- fresh scale logits",
        "value network <- fresh PPO init",
        "```",
        "",
        "## Decision",
        "",
        "Do not train from this schema alone. The next gate is a step-0 fidelity",
        "test that initializes PPO params from the BC NPZ, evaluates the resulting",
        "deterministic policy, and proves it matches the BC candidate before any",
        "PPO updates.",
        "",
    ]
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--playground-path",
        default="../Open_Duck_Playground",
        help="Open_Duck_Playground checkout path for imports.",
    )
    parser.add_argument(
        "--bc-npz",
        default=None,
        help="Optional BC MLP NPZ candidate to compare against PPO shapes.",
    )
    parser.add_argument("--obs-size", type=int, default=101)
    parser.add_argument("--privileged-obs-size", type=int, default=212)
    parser.add_argument("--action-size", type=int, default=14)
    parser.add_argument(
        "--output-md",
        default="outputs/analysis/PPO_POLICY_PARAM_SCHEMA.md",
    )
    parser.add_argument(
        "--output-json",
        default="outputs/analysis/ppo_policy_param_schema.json",
    )
    args = parser.parse_args()

    # Keep this inspection off the accelerator unless the caller explicitly
    # chooses otherwise before process startup.
    os.environ.setdefault("JAX_PLATFORMS", "cpu")
    sys.path.insert(0, str(Path(args.playground_path).resolve()))

    import jax
    from brax.training.agents.ppo import networks as ppo_networks
    from mujoco_playground.config import locomotion_params

    cfg = locomotion_params.brax_ppo_config("BerkeleyHumanoidJoystickFlatTerrain")
    network_factory = functools.partial(
        ppo_networks.make_ppo_networks, **cfg.network_factory
    )
    obs_shape = {
        "state": (args.obs_size,),
        "privileged_state": (args.privileged_obs_size,),
    }
    ppo_network = network_factory(
        obs_shape,
        args.action_size,
        preprocess_observations_fn=lambda obs, _: obs,
    )
    key_policy, key_value = jax.random.split(jax.random.PRNGKey(0))
    policy_params = ppo_network.policy_network.init(key_policy)
    value_params = ppo_network.value_network.init(key_value)

    bc_npz = _load_bc_npz(Path(args.bc_npz)) if args.bc_npz else None
    policy_shapes = _shape_dtype_tree(policy_params)
    value_shapes = _shape_dtype_tree(value_params)
    policy_output_shape = policy_shapes["params/hidden_3/kernel"]["shape"]
    policy_output_size = policy_output_shape[1]

    compatibility = {
        "hidden_layers_match": False,
        "output_loc_matches_bc": False,
        "normalizer_shape_compatible": False,
    }
    if bc_npz:
        shapes = bc_npz["shapes"]
        compatibility = {
            "hidden_layers_match": (
                shapes.get("w0", {}).get("shape") == [args.obs_size, 512]
                and shapes.get("b0", {}).get("shape") == [512]
                and shapes.get("w1", {}).get("shape") == [512, 256]
                and shapes.get("b1", {}).get("shape") == [256]
                and shapes.get("w2", {}).get("shape") == [256, 128]
                and shapes.get("b2", {}).get("shape") == [128]
            ),
            "output_loc_matches_bc": (
                shapes.get("w3", {}).get("shape") == [128, args.action_size]
                and shapes.get("b3", {}).get("shape") == [args.action_size]
                and policy_output_size == 2 * args.action_size
            ),
            "normalizer_shape_compatible": (
                shapes.get("norm", {}).get("shape") == [2, args.obs_size]
            ),
        }

    status = (
        "PASS_PPO_BC_SCHEMA_COMPATIBLE"
        if all(compatibility.values())
        else "HOLD_PPO_BC_SCHEMA_MISMATCH"
    )
    report = {
        "status": status,
        "jax_backend": jax.default_backend(),
        "jax_devices": [str(device) for device in jax.devices()],
        "observation_size": args.obs_size,
        "privileged_observation_size": args.privileged_obs_size,
        "action_size": args.action_size,
        "policy_hidden_layer_sizes": list(cfg.network_factory.policy_hidden_layer_sizes),
        "value_hidden_layer_sizes": list(cfg.network_factory.value_hidden_layer_sizes),
        "policy_obs_key": cfg.network_factory.policy_obs_key,
        "value_obs_key": cfg.network_factory.value_obs_key,
        "distribution_type": "tanh_normal",
        "policy_output_size": policy_output_size,
        "policy_param_shapes": policy_shapes,
        "value_param_shapes": value_shapes,
        "bc_npz": bc_npz,
        "compatibility": compatibility,
        "recommended_mapping": {
            "normalizer_mean_state": "bc.norm[0]",
            "normalizer_std_state": "bc.norm[1]",
            "policy_hidden_0": "bc.w0/b0",
            "policy_hidden_1": "bc.w1/b1",
            "policy_hidden_2": "bc.w2/b2",
            "policy_hidden_3_loc": "bc.w3/b3 -> columns 0:14",
            "policy_hidden_3_scale_logits": "fresh PPO init or explicit low-variance init",
            "value_network": "fresh PPO init",
        },
    }

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, indent=2))
    _write_markdown(Path(args.output_md), report)

    print(status)
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0 if status.startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
