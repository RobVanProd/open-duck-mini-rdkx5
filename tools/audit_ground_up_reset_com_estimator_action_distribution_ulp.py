#!/usr/bin/env python3
"""Audit the measured hosted actor-output epsilon at the action distribution."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import tarfile
import tempfile
from typing import Any

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

import jax
import jaxlib
import jax.numpy as jnp
import numpy as np
from flax.training import orbax_utils
from orbax import checkpoint as ocp


REPO = Path(__file__).resolve().parents[1]
ARCHIVE = REPO / "outputs/analysis/GROUND_UP_TRACKING_TAIL_artifacts.tar.gz"
RELATIVE = Path("ground_up_tracking_tail_outputs/T2_EQUAL/2026_07_14_190425_1024000")
ACTOR_SOURCE = REPO / "patches/reference_residual_hard_vector_ppo_networks.py"
HOSTED_SOURCE = REPO / "tools/colab_ground_up_reset_com_estimator_training.py"
DIAGNOSTIC = REPO / "outputs/analysis/ground_up_reset_com_estimator_gpu_diagnostic_validity_correction.json"
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_ACTION_DISTRIBUTION_ULP_SENSITIVITY_PREREGISTRATION_20260715.md"
DISTRIBUTION_SOURCE = Path(jax.__file__).parents[1] / "brax/training/distribution.py"
RESTORE_CORRECTION = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_ACTION_DISTRIBUTION_ULP_RESTORE_CORRECTION_20260715.md"
CPU_TEMPLATE = Path("/home/lsd/robots/open-duck-mini-rdkx5/outputs/ground_up_torso_com_cpu_smoke/2026_07_14_180720_0")
EXPECTED = {
    "archive": "ae4c631a6ce1c0b36c3231113740acc6c1b8a463c0911ce7cad30b8f8d8ca60f",
    "actor": "546f375fa3c2f34158f49f1ac07cdc5ff6dc41d1a94322f4334bd48835911630",
    "hosted": "a3e5fc38994cecd65d89fdc6b9ede23c2433e917b84583dfcced42c161e79d67",
    "diagnostic": "6f734d595b207c357f6affb201176db38dc5c5911670a02270c80d4f374bb7b0",
    "prereg": "d895917fd8e5043d05c69ab5cf2add769732d122349c8d49247a6a17221b248e",
    "distribution": "3f9375b179f55ebb76fb337db610fafbf60b53b3d329a2fbbfae365836b1d220",
    "restore_correction": "40f258a2835ab1ffa4855d3f30638320396b9ed5f33edd2c6d09a6f6a1f897e8",
}
EXPECTED_TEMPLATE_HASH = "b37a86f1b736d0d1276e60fb69d1f473683c593dec26f9592b0b794858dbb44a"
EPSILON = 2.0 ** -23
ACTION_BOUNDARY = 1.0e-6
ACTION_SCALE_RAD = 0.25
TARGET_BOUNDARY_RAD = ACTION_BOUNDARY * ACTION_SCALE_RAD
ANALYTIC_TOLERANCE = 1.0e-12


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_directory(path: Path) -> str:
    digest = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        digest.update(str(child.relative_to(path)).encode())
        digest.update(b"\0")
        with child.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def softplus(value: np.ndarray) -> np.ndarray:
    return np.logaddexp(0.0, value)


def metrics(baseline: np.ndarray, perturbed: np.ndarray) -> dict[str, float]:
    base_loc, base_logits = np.split(baseline.astype(np.float64), 2)
    loc, logits = np.split(perturbed.astype(np.float64), 2)
    base_scale = softplus(base_logits) + 0.001
    scale = softplus(logits) + 0.001
    mode_delta = np.tanh(loc) - np.tanh(base_loc)
    scale_delta = scale - base_scale
    return {
        "parameter_linf": float(np.max(np.abs(perturbed - baseline))),
        "mode_linf": float(np.max(np.abs(mode_delta))),
        "scale_linf": float(np.max(np.abs(scale_delta))),
        "target_linf_rad": float(np.max(np.abs(mode_delta)) * ACTION_SCALE_RAD),
        "gaussian_w2_tanh_upper_bound": float(
            np.sqrt(np.sum(np.square(loc - base_loc)) + np.sum(np.square(scale_delta)))
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    inputs = {
        "archive": ARCHIVE,
        "actor": ACTOR_SOURCE,
        "hosted": HOSTED_SOURCE,
        "diagnostic": DIAGNOSTIC,
        "prereg": PREREG,
        "distribution": DISTRIBUTION_SOURCE,
        "restore_correction": RESTORE_CORRECTION,
    }
    hashes = {name: sha256(path) for name, path in inputs.items()}
    diagnostic = json.loads(DIAGNOSTIC.read_text())
    actor_module = load(ACTOR_SOURCE, "ulp_actor")
    hosted_module = load(HOSTED_SOURCE, "ulp_hosted")

    with tempfile.TemporaryDirectory(prefix="reset_estimator_ulp_") as temporary:
        root = Path(temporary)
        with tarfile.open(ARCHIVE, "r:gz") as archive:
            members = [member for member in archive
                       if member.name == str(RELATIVE)
                       or member.name.startswith(str(RELATIVE) + "/")]
            archive.extractall(root, members=members, filter="data")
        source_path = root / RELATIVE
        source_hash = hosted_module.sha256_directory(source_path)
        checkpointer = ocp.PyTreeCheckpointer()
        template = checkpointer.restore(str(CPU_TEMPLATE))
        restore_args = orbax_utils.restore_args_from_target(template)
        source = checkpointer.restore(str(source_path), item=template, restore_args=restore_args)
        networks = actor_module.make_reference_residual_ppo_networks(
            {"state": (115,), "privileged_state": (226,)}, 14
        )
        state = jnp.linspace(-0.25, 0.25, 115, dtype=jnp.float32)[None]
        privileged = jnp.linspace(-0.5, 0.5, 226, dtype=jnp.float32)[None]
        observation = {"state": state, "privileged_state": privileged}
        normalizer = hosted_module.normalizer_state(source[0])
        actor = np.asarray(networks.policy_network.apply(normalizer, source[1], observation))[0]
        critic = np.asarray(networks.value_network.apply(normalizer, source[2], observation))

    scenarios: list[dict[str, Any]] = []
    for coordinate in range(28):
        for sign in (-1.0, 1.0):
            delta = np.zeros(28, dtype=np.float64)
            delta[coordinate] = sign * EPSILON
            scenarios.append({"name": f"coordinate_{coordinate}_{'neg' if sign < 0 else 'pos'}",
                              "coordinate": coordinate, "sign": sign,
                              **metrics(actor.astype(np.float64), actor.astype(np.float64) + delta)})
    for sign in (-1.0, 1.0):
        delta = np.full(28, sign * EPSILON, dtype=np.float64)
        scenarios.append({"name": f"all_{'neg' if sign < 0 else 'pos'}",
                          "coordinate": None, "sign": sign,
                          **metrics(actor.astype(np.float64), actor.astype(np.float64) + delta)})

    maxima = {
        key: max(cell[key] for cell in scenarios)
        for key in ("parameter_linf", "mode_linf", "scale_linf",
                    "target_linf_rad", "gaussian_w2_tanh_upper_bound")
    }
    analytic = {
        "parameter_linf": EPSILON,
        "mode_linf": EPSILON,
        "scale_linf": EPSILON,
        "target_linf_rad": EPSILON * ACTION_SCALE_RAD,
        "gaussian_w2_tanh_upper_bound": math.sqrt(28.0) * EPSILON,
    }
    cells = diagnostic.get("output_equivalence", [])
    checks = {
        "frozen_hashes_exact": hashes == EXPECTED,
        "cpu_only": jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
        and os.environ.get("CUDA_VISIBLE_DEVICES") == ""
        and os.environ.get("JAX_PLATFORMS") == "cpu",
        "source_directory_hash_exact": source_hash
        == "05c0c08468f02b96d7e4316fdae6527c6ee223fba507ce3f6a3221b2561a920e",
        "cpu_template_hash_exact": sha256_directory(CPU_TEMPLATE) == EXPECTED_TEMPLATE_HASH,
        "restored_tree_and_shapes_exact": jax.tree_util.tree_structure(source)
        == jax.tree_util.tree_structure(template)
        and list(np.asarray(source[0]["mean"]["state"]).shape) == [115]
        and list(np.asarray(source[0]["mean"]["privileged_state"]).shape) == [226]
        and list(np.asarray(source[1]["params"]["residual_trunk"]["hidden_0"]["kernel"]).shape) == [115, 512]
        and list(np.asarray(source[2]["params"]["hidden_0"]["kernel"]).shape) == [226, 512]
        and all(np.isfinite(np.asarray(leaf)).all() for leaf in jax.tree_util.tree_leaves(source)),
        "actor_and_critic_finite": actor.shape == (28,)
        and bool(np.isfinite(actor).all()) and bool(np.isfinite(critic).all()),
        "diagnostic_valid_and_exact_envelope": diagnostic.get("status")
        == "PASS_GPU_DIAGNOSTIC_VALIDITY_CORRECTION"
        and diagnostic.get("corrected_classification", {}).get("outcome")
        == "FINITE_GPU_EQUIVALENCE_EXCEEDS_ORIGINAL_1E7"
        and diagnostic.get("corrected_classification", {}).get("maximum_output_error")
        == EPSILON,
        "diagnostic_cells_exact": len(cells) == 3
        and [cell.get("z") for cell in cells] == [-1.0, 0.0, 1.0]
        and all(cell.get("actor_max_abs_error") == EPSILON
                and cell.get("critic_max_abs_error") == 0.0 for cell in cells),
        "scenario_count_and_order_exact": len(scenarios) == 58
        and [cell["name"] for cell in scenarios[:4]]
        == ["coordinate_0_neg", "coordinate_0_pos", "coordinate_1_neg", "coordinate_1_pos"]
        and [cell["name"] for cell in scenarios[-2:]] == ["all_neg", "all_pos"],
        "all_scenario_values_finite": all(
            math.isfinite(value) for cell in scenarios for key, value in cell.items()
            if key not in {"name", "coordinate"}
        ),
        "enumeration_within_analytic_box_bounds": all(
            maxima[key] <= analytic[key] + ANALYTIC_TOLERANCE for key in analytic
        ),
    }
    valid = all(checks.values())
    below = (
        maxima["mode_linf"] <= ACTION_BOUNDARY
        and maxima["scale_linf"] <= ACTION_BOUNDARY
        and maxima["gaussian_w2_tanh_upper_bound"] <= ACTION_BOUNDARY
        and maxima["target_linf_rad"] <= TARGET_BOUNDARY_RAD
    )
    if not valid:
        decision = "INVALID_ULP_SENSITIVITY_AUDIT"
    elif below:
        decision = "ULP_ENVELOPE_BELOW_EXISTING_ACTION_IDENTITY_BOUNDARY"
    else:
        decision = "ULP_ENVELOPE_MATERIALLY_CROSSES_ACTION_IDENTITY_BOUNDARY"
    result = {
        "schema_version": "ground_up_reset_estimator_action_distribution_ulp.v1",
        "tool_sha256": sha256(Path(__file__)),
        "status": "PASS_ACTION_DISTRIBUTION_ULP_SENSITIVITY_AUDIT" if valid else "FAIL_ACTION_DISTRIBUTION_ULP_SENSITIVITY_AUDIT",
        "decision": decision,
        "checks": checks,
        "failed_checks": sorted(name for name, passed in checks.items() if not passed),
        "source_hashes": hashes,
        "source_directory_sha256": source_hash,
        "cpu_template_directory_sha256": sha256_directory(CPU_TEMPLATE),
        "versions": {"jax": jax.__version__, "jaxlib": jaxlib.__version__, "brax": "0.14.2"},
        "baseline": {"actor_distribution_parameters": actor.tolist(),
                     "critic": critic.tolist()},
        "measured_envelope": EPSILON,
        "thresholds": {"action_or_distribution": ACTION_BOUNDARY,
                       "physical_target_rad": TARGET_BOUNDARY_RAD,
                       "analytic_tolerance": ANALYTIC_TOLERANCE},
        "analytic_bounds": analytic,
        "enumerated_maxima": maxima,
        "scenarios": scenarios,
        "execution": {"cpu_only": True, "colab_sessions_created": 0,
                      "training_steps": 0, "behavior_cells": 0,
                      "robot_or_rdk": False},
        "authority": {
            "selected_next_study": "EPSILON_AWARE_HOSTED_EXPANSION_CORRECTION_PREREGISTRATION"
            if decision == "ULP_ENVELOPE_BELOW_EXISTING_ACTION_IDENTITY_BOUNDARY" else None,
            "original_1e_7_result_changed": False,
            "training": False,
            "colab": False,
            "behavior_evaluation": False,
        },
    }
    args.output.resolve().write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "decision": decision,
                      "failed_checks": result["failed_checks"], "maxima": maxima}, sort_keys=True))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
