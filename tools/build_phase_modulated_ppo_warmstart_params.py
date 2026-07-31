#!/usr/bin/env python3
"""Build a phase-modulated PPO step-0 checkpoint from a BC parent NPZ.

This is the trainable warm-start bridge for Phase 2 DR. It preserves the
phase/context modulation used by the passing parent instead of compressing that
parent into Brax's default plain PPO MLP.

Offline-only: no PPO updates, robot tests, SSH, deploy, or grounded replay.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import sys
from typing import Any

import numpy as np

from build_ppo_bc_warmstart_params import action_diff, load_trace_observations, run_onnx


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def set_config(config: Any, key: str, value: Any) -> None:
    try:
        config[key] = value
    except Exception:
        setattr(config, key, value)


def main() -> int:
    args = parse_args()
    os.environ.setdefault("JAX_PLATFORMS", "cpu")
    os.environ.setdefault("JAX_PLATFORM_NAME", "cpu")
    sys.path.insert(0, str(Path(args.playground_path).resolve()))

    import jax
    import jax.numpy as jnp
    from brax.training.acme import running_statistics, specs
    from flax.training import orbax_utils
    from mujoco_playground.config import locomotion_params
    from orbax import checkpoint as ocp
    from playground.common.export_onnx import export_onnx
    from playground.common.phase_modulated_ppo import (
        make_phase_modulated_ppo_networks,
        make_policy_params_from_npz,
    )

    bc = np.load(args.bc_npz, allow_pickle=True)
    context_indices = [int(v) for v in bc["context_indices"].tolist()]
    trunk_hidden = [int(v) for v in bc["trunk_hidden_sizes"].tolist()]
    context_hidden = [int(v) for v in bc["context_hidden_sizes"].tolist()]
    activation = str(bc["activation"][0])
    modulation_scale = float(bc["modulation_scale"][0])

    ppo_params = locomotion_params.brax_ppo_config("BerkeleyHumanoidJoystickFlatTerrain")
    set_config(ppo_params.network_factory, "policy_network_kind", "phase_modulated")
    set_config(ppo_params.network_factory, "phase_modulated_context_indices", tuple(context_indices))
    set_config(ppo_params.network_factory, "phase_modulated_context_hidden_sizes", tuple(context_hidden))
    set_config(ppo_params.network_factory, "phase_modulated_policy_hidden_sizes", tuple(trunk_hidden))
    set_config(ppo_params.network_factory, "phase_modulated_activation", activation)
    set_config(ppo_params.network_factory, "phase_modulated_scale", modulation_scale)

    obs_shape = {
        "state": (101,),
        "privileged_state": (212,),
    }
    ppo_network = make_phase_modulated_ppo_networks(
        obs_shape,
        14,
        policy_hidden_layer_sizes=trunk_hidden,
        context_hidden_layer_sizes=context_hidden,
        context_indices=context_indices,
        activation=activation,
        init_scale_logit=float(args.scale_logit),
        modulation_scale=modulation_scale,
        value_hidden_layer_sizes=getattr(
            ppo_params.network_factory, "value_hidden_layer_sizes", (256,) * 5
        ),
        distribution_type=getattr(
            ppo_params.network_factory, "distribution_type", "tanh_normal"
        ),
    )
    key_policy, key_value = jax.random.split(jax.random.PRNGKey(args.seed))
    policy = copy.deepcopy(ppo_network.policy_network.init(key_policy))
    policy = make_policy_params_from_npz(args.bc_npz, scale_logit=float(args.scale_logit))
    value = ppo_network.value_network.init(key_value)

    obs_specs = {
        "state": specs.Array((101,), jnp.dtype("float32")),
        "privileged_state": specs.Array((212,), jnp.dtype("float32")),
    }
    normalizer = running_statistics.init_state(obs_specs)
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
        "PASS_PHASE_MODULATED_PPO_WARMSTART_STEP0_EXPORT_FIDELITY"
        if fidelity["p95_abs_error"] <= args.pass_p95_abs_error
        and fidelity["max_abs_error"] <= args.pass_max_abs_error
        else "HOLD_PHASE_MODULATED_PPO_WARMSTART_STEP0_EXPORT_FIDELITY"
    )

    report = {
        "status": status,
        "bc_npz": args.bc_npz,
        "bc_npz_sha256": sha256_file(Path(args.bc_npz)),
        "reference_onnx": args.reference_onnx,
        "reference_onnx_sha256": sha256_file(Path(args.reference_onnx)),
        "output_checkpoint": args.output_checkpoint,
        "output_checkpoint_abs": str(checkpoint_dir),
        "output_onnx": args.output_onnx,
        "output_onnx_sha256": sha256_file(export_path),
        "manifest": args.manifest,
        "samples_checked": int(obs.shape[0]),
        "scale_logit": float(args.scale_logit),
        "scale_std": float(np.log1p(np.exp(float(args.scale_logit))) + 0.001),
        "architecture": {
            "policy_network_kind": "phase_modulated",
            "trunk_hidden_sizes": trunk_hidden,
            "context_hidden_sizes": context_hidden,
            "context_indices": context_indices,
            "activation": activation,
            "modulation_scale": modulation_scale,
            "output_mode": "tanh_normal_logits_with_phase_modulated_loc",
        },
        "fidelity": fidelity,
        "pass_thresholds": {
            "p95_abs_error": float(args.pass_p95_abs_error),
            "max_abs_error": float(args.pass_max_abs_error),
        },
        "mapping": {
            "bc_trunk": "policy params trunk_0..N",
            "bc_context": "policy params context_0..N",
            "bc_output": "policy params output loc layer",
            "scale_logits": "policy params scale_logits constant initialization",
            "value_network": "fresh PPO value initialization",
            "normalizer": "Brax running-stat normalizer kept for critic; actor uses fixed BC normalizers",
        },
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    write_markdown(Path(args.output_md), report)
    print(status)
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0 if status.startswith("PASS_") else 1


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fidelity = report["fidelity"]
    arch = report["architecture"]
    lines = [
        "# Phase-Modulated PPO Warm-Start Step-0 Export Fidelity",
        "",
        f"status: `{report['status']}`",
        "",
        "This is an offline PPO-param construction and export check. It did not",
        "run PPO updates, SSH, deploy, run robot tests, grounded replay, or",
        "change robot runtime behavior.",
        "",
        "## Inputs",
        "",
        f"- BC NPZ: `{report['bc_npz']}`",
        f"- BC NPZ sha256: `{report['bc_npz_sha256']}`",
        f"- reference ONNX: `{report['reference_onnx']}`",
        f"- reference ONNX sha256: `{report['reference_onnx_sha256']}`",
        f"- manifest: `{report['manifest']}`",
        "",
        "## Outputs",
        "",
        f"- checkpoint: `{report['output_checkpoint']}`",
        f"- checkpoint absolute path: `{report['output_checkpoint_abs']}`",
        f"- exported ONNX: `{report['output_onnx']}`",
        f"- exported ONNX sha256: `{report['output_onnx_sha256']}`",
        "",
        "## Architecture",
        "",
        f"- policy network kind: `{arch['policy_network_kind']}`",
        f"- trunk hidden sizes: `{arch['trunk_hidden_sizes']}`",
        f"- context hidden sizes: `{arch['context_hidden_sizes']}`",
        f"- context indices: `{arch['context_indices']}`",
        f"- activation: `{arch['activation']}`",
        f"- modulation scale: `{arch['modulation_scale']}`",
        f"- output mode: `{arch['output_mode']}`",
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
        "If this passes, the exported PPO step-0 policy reproduces the",
        "phase-modulated parent ONNX at the action level while preserving a",
        "restorable PPO checkpoint shape. The next gate is the standard",
        "corrected-bridge x=0.08 and x=0.0 full8 sweep from this exported ONNX",
        "before any domain-randomized PPO updates.",
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
        default="outputs/analysis/phase_modulated_ppo_warmstart_step0_checkpoint",
    )
    parser.add_argument(
        "--output-onnx",
        default="outputs/analysis/phase_modulated_ppo_warmstart_step0.onnx",
    )
    parser.add_argument(
        "--output-md",
        default="outputs/analysis/PHASE_MODULATED_PPO_WARMSTART_STEP0_FIDELITY.md",
    )
    parser.add_argument(
        "--output-json",
        default="outputs/analysis/phase_modulated_ppo_warmstart_step0_fidelity.json",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
