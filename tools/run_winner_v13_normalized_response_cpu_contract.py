#!/usr/bin/env python3
"""Run one zero-formal-cell CPU proof for Winner-v13 normalized response."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(PATCHES))
sys.path.insert(0, str(TOOLS))

CONTRACT = ANALYSIS / "winner_v13_normalized_response_cpu_contract.json"
FULL_PREREGISTRATION = (
    ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
)
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
EXPECTED_AUXILIARY_INDICES = np.asarray(
    list(range(0, 6)) + list(range(13, 41)) + list(range(83, 99)),
    dtype=np.int64,
)


def lf_sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    import hashlib

    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_source_manifest(contract: Mapping[str, Any]) -> None:
    sources = contract.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v13 CPU source manifest is absent")
    for name, item in sources.items():
        path = ROOT / item["path"]
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(path) != item["sha256"]
        ):
            raise ValueError(f"Winner-v13 CPU source changed: {name}")
    if canonical_sha256(sources) != contract.get("source_manifest_sha256"):
        raise ValueError("Winner-v13 CPU source-manifest digest changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--zero-cell-contract-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.zero_cell_contract_authorized:
        raise PermissionError(
            "Winner-v13 CPU proof requires --offline-cpu-only "
            "--zero-cell-contract-authorized"
        )
    if args.output.exists() or args.work_root.exists():
        raise FileExistsError("refusing to overwrite Winner-v13 CPU evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
    import onnxruntime as ort
    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v12_full_calibrator_training as full
    import winner_v12_calibrator_training as v12
    import winner_v12_decomposed_backend_networks as networks
    import winner_v13_normalized_calibrator_training as v13

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v13 CPU proof requires CPU-only JAX")
    if not np.array_equal(v13.AUXILIARY_INDICES, EXPECTED_AUXILIARY_INDICES):
        raise ValueError("Winner-v13 auxiliary indices changed")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if (
        contract.get("status") != "FROZEN_WINNER_V13_NORMALIZED_RESPONSE_CPU_CONTRACT"
        or contract.get("decision") != "AUTHORIZE_ONE_ZERO_CELL_CPU_UPDATE_ONLY"
        or contract.get("execution_now")
        != {
            "cpu_contract_optimizer_updates": 0,
            "full_training_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v13 CPU contract changed")
    validate_source_manifest(contract)

    preregistration = json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8"))
    design = json.loads(smoke.CALIBRATOR_PREREG.read_text(encoding="utf-8"))
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    population = full.training_population(preregistration, domain)
    scene = (
        args.playground_root
        / "playground/open_duck_mini_v2/xmls/scene_flat_terrain_backlash.xml"
    )
    if not scene.is_file():
        raise FileNotFoundError(scene)
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    batch_np, episodes, evidence = full.stage1_rollout(
        mujoco,
        scene,
        population,
        design,
        observer_type,
        args.canonical_fit,
        0,
    )
    normalization = evidence.pop("normalization")
    target_mean, target_std = full.validate_stage1_normalization(
        normalization, batch_np
    )
    if not evidence.get("realized_action_chain_exact"):
        raise ValueError("Winner-v13 Stage-1 action chain changed")
    if not evidence.get("fixed_p30_observer_slot_exact"):
        raise ValueError("Winner-v13 Stage-1 applied-target slot changed")
    full.validate_episode_receipts(episodes, population, stage=1, update_index=0)

    valid = np.asarray(batch_np["valid_mask"], dtype=bool)
    valid_targets = np.asarray(batch_np["targets"], dtype=np.float32)[valid]
    contacts = valid_targets[:, 48:50]
    contact_contract = {
        "target_mean": target_mean[48:50].astype(float).tolist(),
        "target_std": target_std[48:50].astype(float).tolist(),
        "all_targets_exactly_one": bool(
            np.array_equal(contacts, np.ones_like(contacts))
        ),
        "normalized_targets_exactly_zero": bool(
            np.array_equal(
                (contacts - target_mean[48:50]) / target_std[48:50],
                np.zeros_like(contacts),
            )
        ),
        "zero_prediction_error_exactly_zero": bool(
            np.array_equal(
                v13.stage1_contact_error_at_constant_target(
                    np.zeros((2,), dtype=np.float32),
                    np.ones((2,), dtype=np.float32),
                    np.ones((2,), dtype=np.float32),
                    np.full((2,), np.float32(1.0e-6), dtype=np.float32),
                ),
                np.zeros((2,), dtype=np.float32),
            )
        ),
    }

    initial = v13.initialize_training_parameters(seed=60720)
    v12_initial = v12.stage1_parameters(initial)
    parameters_before = v13.stage1_parameters(initial)
    optimizer_before = v13.adam_initialize(parameters_before)
    batch = {key: jnp.asarray(value) for key, value in batch_np.items()}
    target_mean_jax = jnp.asarray(target_mean)
    target_std_jax = jnp.asarray(target_std)
    old_loss = v12.stage1_loss(
        v12_initial, batch, target_mean_jax, target_std_jax
    )
    loss_grad = jax.value_and_grad(v13.stage1_loss)
    loss_before, gradients = loss_grad(
        parameters_before, batch, target_mean_jax, target_std_jax
    )
    parameters_after, optimizer_after = v13.adam_step(
        parameters_before,
        gradients,
        optimizer_before,
        learning_rate=v13.STAGE1_LEARNING_RATE,
        beta1=v13.ADAM_BETA1,
        beta2=v13.ADAM_BETA2,
        epsilon=v13.ADAM_EPSILON,
    )
    loss_after = v13.stage1_loss(
        parameters_after, batch, target_mean_jax, target_std_jax
    )
    updated = v13.merge_stage1(initial, parameters_after)
    initial_action_hash = smoke.tree_sha256(
        {key: initial[key] for key in v13.DEPLOYABLE_ACTION_KEYS}
    )
    updated_action_hash = smoke.tree_sha256(
        {key: updated[key] for key in v13.DEPLOYABLE_ACTION_KEYS}
    )
    if not v13.finite_tree(
        {
            "batch": batch_np,
            "normalization": {"mean": target_mean, "std": target_std},
            "loss_before": loss_before,
            "loss_after": loss_after,
            "old_loss": old_loss,
            "gradients": gradients,
            "parameters": updated,
            "optimizer": optimizer_after,
        }
    ):
        raise FloatingPointError("Winner-v13 CPU update is nonfinite")

    args.work_root.mkdir(parents=True, exist_ok=False)
    graph = args.work_root / "winner_v13_normalized_response_zero_cell.onnx"
    networks.export_calibrator_onnx(v13.deployable_parameters(updated), graph)
    observations = np.asarray(batch_np["observations"], dtype=np.float32)[valid][:256]
    graph_contract = smoke.onnx_contract(graph, updated, observations)
    session = ort.InferenceSession(str(graph), providers=["CPUExecutionProvider"])
    graph_actions = session.run(
        ["calibration_actions"],
        {
            "obs": observations[:1],
            "previous_action": np.zeros((1, 14), dtype=np.float32),
            "h_in": np.zeros((1, 64), dtype=np.float32),
        },
    )[0]
    checks = {
        "exact_80_episode_training_population": len(episodes) == 80,
        "valid_transition_count_nonzero": int(np.sum(valid)) > 0,
        "contact_targets_exactly_one": contact_contract["all_targets_exactly_one"],
        "contact_targets_normalize_to_exact_zero": contact_contract[
            "normalized_targets_exactly_zero"
        ],
        "zero_contact_prediction_has_exact_zero_error": contact_contract[
            "zero_prediction_error_exactly_zero"
        ],
        "normalized_initial_loss_below_raw_initial_loss": float(loss_before)
        < float(old_loss),
        "one_update_reduces_same_batch_normalized_loss": float(loss_after)
        < float(loss_before),
        "all_stage1_gradients_nonzero": all(
            float(np.max(np.abs(np.asarray(value)))) > 0.0
            for value in gradients.values()
        ),
        "one_adam_update_exact": int(np.asarray(optimizer_after["count"])) == 1,
        "action_head_bit_exact": initial_action_hash == updated_action_hash,
        "exported_action_exact_zero": bool(
            np.array_equal(graph_actions, np.zeros_like(graph_actions))
        ),
        "onnx_abi_exact": graph_contract["abi_exact"],
        "onnx_training_only_tensors_absent": graph_contract[
            "training_only_tensors_absent"
        ],
        "onnx_jax_error_at_most_1e_7": graph_contract["jax_onnx_at_most_1e_7"],
        "onnx_previous_action_chain_exact": graph_contract[
            "previous_action_out_equals_action_bit_exact"
        ],
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "winner_v13.normalized_response_cpu_contract_result.v1",
        "status": (
            "PASS_WINNER_V13_NORMALIZED_RESPONSE_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V13_NORMALIZED_RESPONSE_CPU_CONTRACT"
        ),
        "decision": (
            "AUTHORIZE_NORMALIZED_RESPONSE_STAGE1_PREREGISTRATION_ONLY"
            if not failed
            else "DO_NOT_TRAIN_WINNER_V13"
        ),
        "checks": checks,
        "failed_checks": failed,
        "objective_evidence": {
            "v12_raw_coordinate_initial_loss": float(old_loss),
            "v13_normalized_coordinate_initial_loss": float(loss_before),
            "v13_normalized_coordinate_post_update_loss": float(loss_after),
            "v12_to_v13_initial_loss_ratio": float(old_loss / loss_before),
            "all_values_finite": all(
                math.isfinite(float(value))
                for value in (old_loss, loss_before, loss_after)
            ),
            "contact_contract": contact_contract,
        },
        "graph_contract": graph_contract,
        "sources": {
            "contract_lf_sha256": lf_sha256(CONTRACT),
            "runner_lf_sha256": lf_sha256(Path(__file__)),
            "v13_primitives_lf_sha256": lf_sha256(
                PATCHES / "winner_v13_normalized_calibrator_training.py"
            ),
        },
        "execution": {
            "cpu_contract_optimizer_updates": 1,
            "full_training_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "a separate normalized-response Stage-1 preregistration",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    for name in failed:
        print(f"FAILED={name}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
