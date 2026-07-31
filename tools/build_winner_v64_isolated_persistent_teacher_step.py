#!/usr/bin/env python3
"""Preregister exactly one isolated persistent-teacher Adam step."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v64_isolated_persistent_teacher_step_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V64_ISOLATED_PERSISTENT_TEACHER_STEP_CONTRACT_20260722.md"
V63B_RESULT = ANALYSIS / "winner_v63b_persistent_teacher_conflict_result.json"
V63B_CORRECTION = ANALYSIS / "winner_v63b_training_snapshot_loader_correction.json"
V63B_RESULT_SHA256 = "5e9b44fdcaac5ae87cf8e7050262c51e4b27ebd4b71aa5f3f011e5ad094225fb"

SOURCES = {
    "builder": Path("tools/build_winner_v64_isolated_persistent_teacher_step.py"),
    "runner": Path("tools/run_winner_v64_isolated_persistent_teacher_step.py"),
    "tests": Path("tests/test_winner_v64_isolated_persistent_teacher_step.py"),
    "v63b_result": Path(
        "outputs/analysis/winner_v63b_persistent_teacher_conflict_result.json"
    ),
    "v63b_correction": Path(
        "outputs/analysis/winner_v63b_training_snapshot_loader_correction.json"
    ),
    "v63b_builder": Path(
        "tools/build_winner_v63b_training_snapshot_loader_correction.py"
    ),
    "v63b_runner": Path(
        "tools/run_winner_v63b_training_snapshot_loader_correction.py"
    ),
    "v63_base_runner": Path(
        "tools/run_winner_v63_persistent_teacher_conflict_attribution.py"
    ),
    "v60_result": Path(
        "outputs/analysis/winner_v60_integrated_numeric_guard_training_result.json"
    ),
    "v62_result": Path(
        "outputs/analysis/winner_v62_residual_teacher_causal_result.json"
    ),
    "networks": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "snapshot_io": Path("patches/winner_v22_normalized_predictor_v2.py"),
}

INSERT_POINT = '''    failed = sorted(name for name, passed in checks.items() if not passed)
    valid = not failed'''
INSERTION = '''
    if not valid:
        raise ValueError("Winner-v64 cannot persist an invalid V63 attribution")
    import winner_v12_decomposed_backend_networks as v64_networks
    parameters_after = v21.merge_joint_trainable(parameters, teacher_after)
    leaf_delta = {
        key: float(np.max(np.abs(np.asarray(teacher_after[key]) - np.asarray(before[key]))))
        for key in sorted(before)
    }
    loss_after_value, metrics_after = teacher_objective(teacher_after)
    if V64_WORK_ROOT.exists():
        raise FileExistsError(f"refusing to overwrite Winner-v64 work root: {V64_WORK_ROOT}")
    V64_WORK_ROOT.mkdir(parents=True, exist_ok=False)
    graph_path_v64 = V64_WORK_ROOT / "winner_v64_isolated_persistent_teacher_update_555.onnx"
    v64_networks.export_calibrator_onnx(
        training.deployable_parameters(parameters_after), graph_path_v64
    )
    graph_contract_v64 = smoke.onnx_contract(
        graph_path_v64,
        parameters_after,
        np.asarray(batch_np["observations"][0], dtype=np.float32),
    )
    snapshot_path_v64 = V64_WORK_ROOT / "winner_v64_isolated_persistent_teacher_update_555.npz"
    snapshot_receipt_v64 = v22v2.save_snapshot(
        snapshot_path_v64,
        parameters_after,
        teacher_optimizer,
        {
            "stage": "isolated_persistent_teacher_joint_stage2",
            "completed_updates": 555,
            "source_completed_updates": 554,
            "source_snapshot_sha256": contract["frozen_source"]["snapshot"]["sha256"],
            "objective": contract["v64"]["objective"],
            "root_seed": 120120,
            "learning_rate": float(training.STAGE2_LEARNING_RATE),
            "persistent_teacher_scale": float(v49.FULL_ACTION_TEACHER_SCALE),
            "formal_support_cells": 0,
            "continuation_training_updates": 0,
            "robot_or_rdk_access": 0,
        },
        snapshot["target_mean"],
        snapshot["target_std"],
    )
    loaded_v64 = v22v2.load_snapshot(snapshot_path_v64)
    snapshot_exact_v64 = bool(
        tree_bit_exact(parameters_after, loaded_v64["parameters"])
        and np.array_equal(teacher_optimizer["count"], loaded_v64["optimizer"]["count"])
        and tree_bit_exact(teacher_optimizer["m"], loaded_v64["optimizer"]["m"])
        and tree_bit_exact(teacher_optimizer["v"], loaded_v64["optimizer"]["v"])
        and np.array_equal(snapshot["target_mean"], loaded_v64["target_mean"])
        and np.array_equal(snapshot["target_std"], loaded_v64["target_std"])
        and loaded_v64["metadata"].get("stage")
        == "isolated_persistent_teacher_joint_stage2"
        and loaded_v64["metadata"].get("completed_updates") == 555
    )
    v64_checks = {
        "v63b_attribution_valid": True,
        "same_batch_loss_recomputes_counterfactual_exact": float(loss_after_value)
        == isolated_teacher_loss,
        "same_batch_teacher_loss_strictly_decreases": float(loss_after_value)
        < teacher_loss_float,
        "exactly_one_optimizer_update_554_to_555": int(
            np.asarray(teacher_optimizer["count"])
        )
        == 555,
        "all_12_trainable_leaves_changed": set(leaf_delta) == set(v21.JOINT_TRAINABLE_KEYS)
        and all(value > 0.0 for value in leaf_delta.values()),
        "all_parameters_optimizer_metrics_finite": training.finite_tree(
            {
                "parameters": parameters_after,
                "optimizer": teacher_optimizer,
                "loss_after": loss_after_value,
                "metrics_after": metrics_after,
            }
        ),
        "snapshot_readback_exact": snapshot_exact_v64,
        "onnx_abi_exact": graph_contract_v64["abi_exact"],
        "onnx_training_only_tensors_absent": graph_contract_v64[
            "training_only_tensors_absent"
        ],
        "onnx_jax_chain_at_most_1e_7": graph_contract_v64["jax_onnx_at_most_1e_7"],
        "onnx_previous_action_chain_exact": graph_contract_v64[
            "previous_action_out_equals_action_bit_exact"
        ],
        "formal_support_continuation_robot_zero": True,
    }
    global V64_ARTIFACT
    V64_ARTIFACT = {
        "checks": {key: bool(value) for key, value in v64_checks.items()},
        "optimization": {
            "optimizer_count_before": 554,
            "optimizer_count_after": int(np.asarray(teacher_optimizer["count"])),
            "loss_before": teacher_loss_float,
            "loss_after": float(loss_after_value),
            "loss_delta": float(loss_after_value) - teacher_loss_float,
            "metrics_before": {
                key: float(np.asarray(value)) for key, value in teacher_metrics.items()
            },
            "metrics_after": {
                key: float(np.asarray(value)) for key, value in metrics_after.items()
            },
            "scaled_gradient_max_abs": {
                key: float(np.max(np.abs(np.asarray(value))))
                for key, value in teacher_scaled.items()
            },
            "leaf_max_abs_delta": leaf_delta,
        },
        "snapshot": snapshot_receipt_v64,
        "graph": graph_contract_v64,
    }
'''


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def transformed_source() -> tuple[str, str]:
    import sys

    sys.path.insert(0, str(ROOT / "tools"))
    import build_winner_v63b_training_snapshot_loader_correction as v63b

    source, _ = v63b.corrected_source()
    if source.count(INSERT_POINT) != 1 or "V64_ARTIFACT" in source:
        raise ValueError("Winner-v64 insertion point changed")
    transformed = source.replace(INSERT_POINT, INSERT_POINT + INSERTION)
    return transformed, hashlib.sha256(transformed.encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v64 contract: {path}")
    v63b = json.loads(V63B_RESULT.read_text(encoding="utf-8"))
    correction = json.loads(V63B_CORRECTION.read_text(encoding="utf-8"))
    transformed, transformed_hash = transformed_source()
    if (
        sha256(V63B_RESULT) != V63B_RESULT_SHA256
        or v63b.get("status")
        != "PASS_WINNER_V63B_PERSISTENT_TEACHER_CONFLICT_ATTRIBUTION"
        or v63b.get("classification")
        != "INTEGRATED_STEP_BLOCKS_PERSISTENT_TEACHER_DESCENT"
        or v63b.get("decision")
        != "PREREGISTER_ISOLATED_PERSISTENT_TEACHER_STEP_CONTRACT"
        or v63b["counterfactual_same_batch_steps"]["integrated"][
            "teacher_loss_delta"
        ]
        <= 0.0
        or v63b["counterfactual_same_batch_steps"][
            "teacher_only_with_inherited_adam_state"
        ]["teacher_loss_delta"]
        >= 0.0
        or correction.get("correction", {}).get("identity")
        != "WINNER_V63B_EXACT_TRAINING_SNAPSHOT_LOADER_CORRECTION"
        or transformed.count("V64_ARTIFACT") != 2
    ):
        raise ValueError("Winner-v64 selection evidence changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    value = dict(correction)
    value["v64"] = {
        "identity": "WINNER_V64_ISOLATED_PERSISTENT_TEACHER_STEP",
        "transformed_source_sha256": transformed_hash,
        "insertion_point_sha256": hashlib.sha256(INSERT_POINT.encode()).hexdigest(),
        "insertion_sha256": hashlib.sha256(INSERTION.encode()).hexdigest(),
        "replacement_count": 1,
        "source": {
            "completed_updates": 554,
            "optimizer_count": 554,
            "snapshot_sha256": v63b["source"]["snapshot_sha256"],
            "onnx_sha256": v63b["source"]["onnx_sha256"],
        },
        "objective": {
            "rollout_update_index": 554,
            "loss": "full-14D persistent teacher MSE on the exact frozen on-policy rollout",
            "scale": 136.35153198242188,
            "integrated_ppo_predictor_anchor_first_tick_gradients": False,
            "inherited_adam_state": True,
            "result_optimizer_count": 555,
            "expected_same_batch_loss_before": 0.003402196103706956,
            "expected_same_batch_loss_after": 0.003393699647858739,
            "coefficient_search": False,
            "attention_or_flat_transport_added": False,
        },
        "execution_future": {
            "rollout_episode_slots": 80,
            "scheduled_rollout_ticks": 20000,
            "optimizer_updates": 1,
            "continuation_updates": 0,
            "formal_support_cells": 0,
            "candidate_graph_exports": 1,
            "robot_or_rdk_access": 0,
        },
        "execution_now": {
            "rollout_episode_slots": 0,
            "scheduled_rollout_ticks": 0,
            "optimizer_updates": 0,
            "continuation_updates": 0,
            "formal_support_cells": 0,
            "candidate_graph_exports": 0,
            "robot_or_rdk_access": 0,
        },
        "pass_rule": {
            "v63b_attribution_valid": True,
            "same_batch_loss_recomputes_counterfactual_exact": True,
            "same_batch_teacher_loss_strictly_decreases": True,
            "exactly_one_optimizer_update_554_to_555": True,
            "all_12_trainable_leaves_changed": True,
            "all_parameters_optimizer_metrics_finite": True,
            "snapshot_readback_exact": True,
            "onnx_abi_exact": True,
            "onnx_training_only_tensors_absent": True,
            "onnx_jax_chain_at_most_1e_7": True,
            "onnx_previous_action_chain_exact": True,
            "formal_support_continuation_robot_zero": True,
        },
        "authority": {
            "robot_clearance": False,
            "one_optimizer_update_authorized": True,
            "continuation_training_authorized": False,
            "formal_support_gate_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "one separately preregistered bounded isolated-teacher continuation"
            ),
        },
    }
    value["sources"] = sources
    value["source_manifest_sha256"] = canonical_sha256(sources)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v64 isolated persistent-teacher step contract",
                "",
                "- Source optimizer count: `554`",
                "- Result optimizer count: `555`",
                "- Objective: frozen full-action persistent teacher only",
                "- Inherited Adam state: `yes`",
                "- PPO/predictor/anchor/reset gradients: `excluded`",
                "- Optimizer / continuation / support / robot: `1 / 0 / 0 / 0`",
                f"- Transformed source SHA-256: `{transformed_hash}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("PREREGISTERED_WINNER_V64_ISOLATED_PERSISTENT_TEACHER_STEP")
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
