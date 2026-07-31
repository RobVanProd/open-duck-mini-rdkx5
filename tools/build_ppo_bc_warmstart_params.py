#!/usr/bin/env python3
"""Build step-0 Brax PPO params from a PPO-loc BC NPZ.

This constructs the actual `(normalizer, policy, value)` params tuple expected
by the local Playground/Brax PPO runner, exports it through the repo's PPO ONNX
export path, and compares the exported policy against the PPO-loc BC ONNX.

Offline-only: no PPO updates, no robot tests, no SSH, no deploy.
"""

from __future__ import annotations

import argparse
import copy
import functools
import json
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np


def percentile(values: np.ndarray, q: float) -> float | None:
    arr = np.asarray(values, dtype=float).reshape(-1)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return None
    return float(np.percentile(arr, q))


def load_trace_observations(manifest_path: Path, max_samples: int | None) -> np.ndarray:
    manifest = json.loads(manifest_path.read_text())
    rows: list[list[float]] = []
    for entry in manifest.get("entries", []):
        if not entry.get("bc_ready", False):
            continue
        source = Path(entry["source_path"])
        if not source.exists():
            continue
        with source.open() as handle:
            for line in handle:
                record = json.loads(line)
                obs = record.get("obs_state")
                if obs is None:
                    continue
                arr = np.asarray(obs, dtype=np.float32).reshape(-1)
                if arr.shape != (101,):
                    continue
                rows.append(arr.astype(float).tolist())
                if max_samples is not None and len(rows) >= max_samples:
                    return np.asarray(rows, dtype=np.float32)
    if not rows:
        raise ValueError(f"no obs_state rows found in {manifest_path}")
    return np.asarray(rows, dtype=np.float32)


def run_onnx(path: Path, obs: np.ndarray) -> np.ndarray:
    import onnxruntime as ort

    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    out = []
    for row in obs:
        out.append(session.run(["continuous_actions"], {"obs": row[None, :].astype(np.float32)})[0][0])
    return np.asarray(out, dtype=np.float32)


def action_diff(reference: np.ndarray, candidate: np.ndarray) -> dict[str, Any]:
    error = candidate - reference
    abs_error = np.abs(error)
    return {
        "samples": int(reference.shape[0]),
        "mae": float(np.mean(abs_error)),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "p50_abs_error": percentile(abs_error, 50),
        "p95_abs_error": percentile(abs_error, 95),
        "p99_abs_error": percentile(abs_error, 99),
        "max_abs_error": float(np.max(abs_error)) if abs_error.size else None,
    }


def main() -> int:
    args = parse_args()
    os.environ.setdefault("JAX_PLATFORMS", "cpu")
    os.environ.setdefault("JAX_PLATFORM_NAME", "cpu")
    sys.path.insert(0, str(Path(args.playground_path).resolve()))

    import jax
    import jax.numpy as jnp
    from brax.training.acme import running_statistics, specs
    from brax.training.agents.ppo import networks as ppo_networks
    from flax.training import orbax_utils
    from mujoco_playground.config import locomotion_params
    from orbax import checkpoint as ocp
    from playground.common.export_onnx import export_onnx

    bc = np.load(args.bc_npz, allow_pickle=True)
    hidden_sizes = bc["hidden_sizes"].astype(int).tolist()
    if hidden_sizes != [512, 256, 128]:
        raise ValueError(f"expected PPO hidden sizes [512,256,128], got {hidden_sizes}")

    ppo_params = locomotion_params.brax_ppo_config("BerkeleyHumanoidJoystickFlatTerrain")
    network_factory = functools.partial(
        ppo_networks.make_ppo_networks, **ppo_params.network_factory
    )
    obs_shape = {
        "state": (101,),
        "privileged_state": (212,),
    }
    ppo_network = network_factory(
        obs_shape,
        14,
        preprocess_observations_fn=lambda obs, _: obs,
    )
    key_policy, key_value = jax.random.split(jax.random.PRNGKey(args.seed))
    policy = copy.deepcopy(ppo_network.policy_network.init(key_policy))
    value = ppo_network.value_network.init(key_value)

    policy["params"]["hidden_0"]["kernel"] = jnp.asarray(bc["w0"], dtype=jnp.float32)
    policy["params"]["hidden_0"]["bias"] = jnp.asarray(bc["b0"], dtype=jnp.float32)
    policy["params"]["hidden_1"]["kernel"] = jnp.asarray(bc["w1"], dtype=jnp.float32)
    policy["params"]["hidden_1"]["bias"] = jnp.asarray(bc["b1"], dtype=jnp.float32)
    policy["params"]["hidden_2"]["kernel"] = jnp.asarray(bc["w2"], dtype=jnp.float32)
    policy["params"]["hidden_2"]["bias"] = jnp.asarray(bc["b2"], dtype=jnp.float32)

    final_kernel = np.asarray(policy["params"]["hidden_3"]["kernel"], dtype=np.float32).copy()
    final_bias = np.asarray(policy["params"]["hidden_3"]["bias"], dtype=np.float32).copy()
    final_kernel[:, :14] = np.asarray(bc["w3"], dtype=np.float32)
    final_bias[:14] = np.asarray(bc["b3"], dtype=np.float32)
    final_kernel[:, 14:28] = 0.0
    final_bias[14:28] = float(args.scale_logit)
    policy["params"]["hidden_3"]["kernel"] = jnp.asarray(final_kernel, dtype=jnp.float32)
    policy["params"]["hidden_3"]["bias"] = jnp.asarray(final_bias, dtype=jnp.float32)

    obs_specs = {
        "state": specs.Array((101,), jnp.dtype("float32")),
        "privileged_state": specs.Array((212,), jnp.dtype("float32")),
    }
    normalizer = running_statistics.init_state(obs_specs)
    norm = np.asarray(bc["norm"], dtype=np.float32)
    normalizer = normalizer.replace(
        mean={
            **normalizer.mean,
            "state": jnp.asarray(norm[0], dtype=jnp.float32),
        },
        std={
            **normalizer.std,
            "state": jnp.asarray(norm[1], dtype=jnp.float32),
        },
    )
    params = (normalizer, policy, value)

    checkpoint_dir = Path(args.output_checkpoint).resolve()
    checkpoint_dir.parent.mkdir(parents=True, exist_ok=True)
    checkpointer = ocp.PyTreeCheckpointer()
    save_args = orbax_utils.save_args_from_target(params)
    checkpointer.save(str(checkpoint_dir), params, force=True, save_args=save_args)

    export_path = Path(args.output_onnx)
    export_path.parent.mkdir(parents=True, exist_ok=True)
    export_onnx(params, 14, ppo_params, 101, output_path=str(export_path))

    obs = load_trace_observations(Path(args.manifest), args.max_samples)
    reference = run_onnx(Path(args.reference_onnx), obs)
    candidate = run_onnx(export_path, obs)
    fidelity = action_diff(reference, candidate)
    status = (
        "PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY"
        if fidelity["p95_abs_error"] <= args.pass_p95_abs_error
        and fidelity["max_abs_error"] <= args.pass_max_abs_error
        else "HOLD_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY"
    )

    report = {
        "status": status,
        "bc_npz": args.bc_npz,
        "reference_onnx": args.reference_onnx,
        "output_checkpoint": args.output_checkpoint,
        "output_onnx": args.output_onnx,
        "manifest": args.manifest,
        "samples_checked": int(obs.shape[0]),
        "scale_logit": float(args.scale_logit),
        "scale_std": float(np.log1p(np.exp(float(args.scale_logit))) + 0.001),
        "fidelity": fidelity,
        "pass_thresholds": {
            "p95_abs_error": float(args.pass_p95_abs_error),
            "max_abs_error": float(args.pass_max_abs_error),
        },
        "mapping": {
            "bc_w0_b0": "policy.params.hidden_0",
            "bc_w1_b1": "policy.params.hidden_1",
            "bc_w2_b2": "policy.params.hidden_2",
            "bc_w3_b3": "policy.params.hidden_3 columns 0:14",
            "scale_logits": "policy.params.hidden_3 columns 14:28, constant",
            "value_network": "fresh PPO initialization",
        },
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(report, indent=2))
    write_markdown(Path(args.output_md), report)
    print(status)
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0 if status.startswith("PASS_") else 1


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fidelity = report["fidelity"]
    lines = [
        "# PPO BC Warm-Start Step-0 Export Fidelity",
        "",
        f"status: `{report['status']}`",
        "",
        "This is an offline PPO-param construction and export check. It did not",
        "run PPO updates, SSH, deploy, run robot tests, or change robot runtime",
        "behavior.",
        "",
        "## Inputs",
        "",
        f"- BC NPZ: `{report['bc_npz']}`",
        f"- reference ONNX: `{report['reference_onnx']}`",
        f"- manifest: `{report['manifest']}`",
        "",
        "## Outputs",
        "",
        f"- checkpoint: `{report['output_checkpoint']}`",
        f"- exported ONNX: `{report['output_onnx']}`",
        "",
        "## Mapping",
        "",
        "```text",
        "BC w0/b0 -> policy hidden_0",
        "BC w1/b1 -> policy hidden_1",
        "BC w2/b2 -> policy hidden_2",
        "BC w3/b3 -> policy hidden_3 columns 0:14 (loc)",
        "scale logits -> policy hidden_3 columns 14:28",
        "value network -> fresh PPO initialization",
        "```",
        "",
        f"scale_logit: `{report['scale_logit']}`",
        f"initial std after softplus/min_std: `{report['scale_std']:.6f}`",
        "",
        "## Fidelity",
        "",
        f"- samples checked: `{report['samples_checked']}`",
        f"- MAE: `{fidelity['mae']:.8f}`",
        f"- p95 abs error: `{fidelity['p95_abs_error']:.8f}`",
        f"- max abs error: `{fidelity['max_abs_error']:.8f}`",
        "",
        "## Decision",
        "",
        "If this passes, the exported PPO step-0 policy reproduces the PPO-loc BC",
        "ONNX at the action level. The next gate is the standard task-matched",
        "fitted closed-loop candidate sweep using this exported PPO ONNX, still",
        "before any PPO training updates.",
        "",
    ]
    path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-path", default="../Open_Duck_Playground")
    parser.add_argument("--bc-npz", required=True)
    parser.add_argument("--reference-onnx", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--max-samples", type=int, default=2048)
    parser.add_argument("--scale-logit", type=float, default=-2.0)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--pass-p95-abs-error", type=float, default=1.0e-5)
    parser.add_argument("--pass-max-abs-error", type=float, default=1.0e-4)
    parser.add_argument(
        "--output-checkpoint",
        default="outputs/analysis/ppo_bc_warmstart_step0_checkpoint",
    )
    parser.add_argument(
        "--output-onnx",
        default="outputs/analysis/ppo_bc_warmstart_step0.onnx",
    )
    parser.add_argument(
        "--output-md",
        default="outputs/analysis/PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY.md",
    )
    parser.add_argument(
        "--output-json",
        default="outputs/analysis/ppo_bc_warmstart_step0_export_fidelity.json",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
