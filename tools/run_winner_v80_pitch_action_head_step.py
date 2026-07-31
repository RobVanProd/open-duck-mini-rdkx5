#!/usr/bin/env python3
"""Run one frozen safeguarded pitch-action-head-only teacher step."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

import build_winner_v80_pitch_action_head_step_contract as builder  # noqa: E402
import run_winner_v46_static_target_teacher_training as v46  # noqa: E402
import run_winner_v63_persistent_teacher_conflict_attribution as v63  # noqa: E402
import winner_v43_static_target_teacher as v43  # noqa: E402


CONTRACT = ANALYSIS / "winner_v80_pitch_action_head_step_contract.json"
V75_RESULT = ANALYSIS / "winner_v75_functional_numeric_guard_continuation_result.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
V78_RESULT = ANALYSIS / "winner_v78_missing_teacher_extension_result.json"
FULL_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
SOURCE_COUNT = 655
COMPLETED_COUNT = 656
PITCH_INDICES = tuple(builder.PITCH_INDICES)
NONPITCH_INDICES = tuple(index for index in range(14) if index not in PITCH_INDICES)
TRAINING_TEACHER_IDS = tuple(builder.TRAINING_TEACHER_IDS)
FRACTIONS = tuple(builder.FRACTIONS)
PITCH_TEACHER_SCALE = np.float32(58.436370849609375)


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


def validate_contract(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version") != "winner_v80.pitch_action_head_step_contract.v1"
        or value.get("status") != "PREREGISTERED_WINNER_V80_PITCH_ACTION_HEAD_STEP"
        or value.get("decision")
        != "AUTHORIZE_EXACTLY_ONE_PITCH_ACTION_HEAD_TEACHER_STEP"
        or value.get("step", {}).get("source_optimizer_count") != SOURCE_COUNT
        or value.get("step", {}).get("completed_optimizer_count") != COMPLETED_COUNT
        or value.get("step", {}).get("pitch_action_indices") != list(PITCH_INDICES)
        or value.get("step", {}).get("fractions_largest_first") != list(FRACTIONS)
        or value.get("objective", {}).get("teacher_configuration_ids")
        != list(TRAINING_TEACHER_IDS)
        or value.get("objective", {}).get("pitch_teacher_scale")
        != float(PITCH_TEACHER_SCALE)
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v80 contract identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v80 source manifest is absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v80 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v80 source manifest changed")


def validate_artifact(path: Path, receipt: Mapping[str, Any], label: str) -> None:
    if (
        not path.is_file()
        or path.stat().st_size != int(receipt["bytes"])
        or sha256(path) != receipt["sha256"]
    ):
        raise ValueError(f"Winner-v80 {label} artifact changed")


def configured_stack() -> tuple[Any, Any, Any]:
    import build_winner_v79b_preregistration_path_correction as v79b

    source, _ = v79b.corrected_source()
    namespace: dict[str, Any] = {
        "__file__": str(ROOT / "tools/run_winner_v79b_preregistration_path_correction.py"),
        "__name__": "winner_v80_v79_reviewed_stack",
    }
    exec(compile(source, namespace["__file__"], "exec"), namespace)
    return namespace["configure_v76_modules"]()


def complete_teacher_table() -> dict[str, np.ndarray]:
    table = v43.load_teacher_table(json.loads(V42_RESULT.read_text(encoding="utf-8")))
    extension_result = json.loads(V78_RESULT.read_text(encoding="utf-8"))
    extension = extension_result.get("teacher_table_extension", {}).get("COM_CORNER_07")
    replays = extension_result.get("configuration_result", {}).get(
        "selected_replay_results", []
    )
    if (
        sha256(V78_RESULT) != builder.V78_RESULT_SHA256
        or extension_result.get("status") != "PASS_WINNER_V78_MISSING_TEACHER_EXTENSION"
        or not isinstance(extension, Mapping)
        or extension.get("shared_support_pass") is not True
        or len(replays) != 2
    ):
        raise ValueError("Winner-v80 teacher extension changed")
    action = v43.expand_coordinates(extension["coordinates"])
    expected_hash = v43.array_sha256(action)
    if any(
        replay.get("support_pass") is not True
        or replay.get("terminal") is not None
        or replay.get("raw_target_sha256") != expected_hash
        for replay in replays
    ):
        raise ValueError("Winner-v80 teacher extension replay changed")
    action.setflags(write=False)
    table["COM_CORNER_07"] = action
    if any(name not in table for name in TRAINING_TEACHER_IDS):
        raise ValueError("Winner-v80 training teacher coverage is incomplete")
    return table


def pitch_teacher_batch(
    *,
    identifiers: Sequence[str],
    previous_actions: Any,
    valid_mask: Any,
    table: Mapping[str, np.ndarray],
    training: Any,
    jnp: Any,
) -> tuple[Any, Any, Any]:
    previous = np.asarray(previous_actions, dtype=np.float32)
    valid = np.asarray(valid_mask, dtype=np.float32)
    if (
        previous.ndim != 3
        or previous.shape[-1] != 14
        or valid.shape != previous.shape[:2]
        or len(identifiers) != previous.shape[0]
        or np.any((valid != 0.0) & (valid != 1.0))
    ):
        raise ValueError("Winner-v80 teacher batch shape changed")
    selected = set(TRAINING_TEACHER_IDS)
    if any(identifiers.count(name) != 2 for name in TRAINING_TEACHER_IDS):
        raise ValueError("Winner-v80 teacher population count changed")
    raw = np.zeros_like(previous)
    mask = np.zeros_like(previous)
    pitch = np.asarray(PITCH_INDICES, dtype=np.int64)
    for environment, name in enumerate(identifiers):
        if name not in selected:
            continue
        raw[environment, :, :] = np.asarray(table[name], dtype=np.float32)
        mask[environment, :, pitch] = valid[environment, :, None]
    raw_jax = jnp.asarray(raw, dtype=jnp.float32)
    previous_jax = jnp.asarray(previous, dtype=jnp.float32)
    bounded = training.bounded_action(raw_jax, previous_jax)
    return raw_jax, bounded, jnp.asarray(mask, dtype=jnp.float32)


def pitch_teacher_loss(
    values_tree: Mapping[str, Any],
    *,
    batch: Mapping[str, Any],
    batch_np: Mapping[str, Any],
    identifiers: Sequence[str],
    table: Mapping[str, np.ndarray],
    training: Any,
    v29: Any,
    jnp: Any,
) -> tuple[Any, dict[str, Any]]:
    actions = v29.deterministic_bounded_actions(
        values_tree, batch["observations"], batch["previous_actions"]
    )[1]
    raw, bounded, mask = pitch_teacher_batch(
        identifiers=identifiers,
        previous_actions=batch_np["previous_actions"],
        valid_mask=batch_np["valid_mask"],
        table=table,
        training=training,
        jnp=jnp,
    )
    error = actions - bounded
    denominator = jnp.sum(mask)
    loss = jnp.sum(jnp.square(error) * mask) / denominator
    return loss, {
        "selected_elements": denominator,
        "maximum_selected_action_delta": jnp.max(
            jnp.where(mask > 0.0, jnp.abs(error), jnp.float32(0.0))
        ),
        "raw_target_max_abs": jnp.max(jnp.abs(raw)),
        "bounded_target_max_abs": jnp.max(jnp.abs(bounded)),
    }


def project_pitch_head_gradient(gradient: Mapping[str, Any], jnp: Any) -> dict[str, Any]:
    pitch = jnp.asarray(PITCH_INDICES, dtype=jnp.int32)
    projected = {key: jnp.zeros_like(value) for key, value in gradient.items()}
    projected["action_weight"] = projected["action_weight"].at[:, pitch].set(
        jnp.asarray(gradient["action_weight"])[:, pitch]
    )
    projected["action_bias"] = projected["action_bias"].at[pitch].set(
        jnp.asarray(gradient["action_bias"])[pitch]
    )
    return projected


def unselected_elements_exact(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> bool:
    if set(left) != set(right):
        return False
    for key in left:
        before = np.asarray(left[key])
        after = np.asarray(right[key])
        if key == "action_weight":
            if not np.array_equal(before[:, NONPITCH_INDICES], after[:, NONPITCH_INDICES]):
                return False
        elif key == "action_bias":
            if not np.array_equal(before[list(NONPITCH_INDICES)], after[list(NONPITCH_INDICES)]):
                return False
        elif not np.array_equal(before, after):
            return False
    return True


def selected_delta_metrics(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> dict[str, float]:
    return {
        "action_weight_pitch_max_abs": float(
            np.max(
                np.abs(
                    np.asarray(right["action_weight"])[:, PITCH_INDICES]
                    - np.asarray(left["action_weight"])[:, PITCH_INDICES]
                )
            )
        ),
        "action_bias_pitch_max_abs": float(
            np.max(
                np.abs(
                    np.asarray(right["action_bias"])[list(PITCH_INDICES)]
                    - np.asarray(left["action_bias"])[list(PITCH_INDICES)]
                )
            )
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-snapshot", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--pitch-action-head-step-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.pitch_action_head_step_authorized:
        raise PermissionError(
            "Winner-v80 requires --offline-cpu-only "
            "--pitch-action-head-step-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v80 evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
    import run_winner_v12_full_calibrator_training as full
    import winner_v12_calibrator_training as training
    import winner_v12_decomposed_backend_networks as networks
    import winner_v20_joint_recurrent_support as v20
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor as v22
    import winner_v22_normalized_predictor_v2 as v22v2
    import winner_v29_prefix_right_pitch_anchor as v29

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v80 requires CPU-only JAX")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    validate_contract(contract)
    training_result = json.loads(V75_RESULT.read_text(encoding="utf-8"))
    final = next(
        row for row in training_result["persistent_checkpoints"] if row["label"] == "final"
    )
    source_receipt = final["snapshot"]
    validate_artifact(args.source_snapshot, source_receipt, "source snapshot")
    snapshot = v22v2.load_snapshot(args.source_snapshot)
    metadata = snapshot["metadata"]
    if (
        int(np.asarray(snapshot["optimizer"]["count"])) != SOURCE_COUNT
        or metadata.get("completed_updates") != SOURCE_COUNT
        or metadata.get("stage") != "fresh_moment_safeguarded_teacher_joint_stage2"
        or metadata.get("formal_support_cells") != 0
        or metadata.get("robot_or_rdk_access") != 0
        or set(snapshot["optimizer"]["m"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(snapshot["optimizer"]["v"]) != set(v21.JOINT_TRAINABLE_KEYS)
    ):
        raise ValueError("Winner-v80 source snapshot boundary changed")

    smoke, gate, _ = configured_stack()
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v80 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v80 canonical P30 fit changed")
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    full_design = json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8"))
    calibrator_design = gate.load_calibrator_design(full_design)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    population = full.training_population(full_design, domain)
    identifiers = [str(row["id"]) for row in population]
    heldout_ids = (
        "HELDOUT_04",
        "HELDOUT_07",
        "HELDOUT_09",
        "HELDOUT_15",
    )
    if (
        len(population) != 80
        or any(identifiers.count(name) != 2 for name in TRAINING_TEACHER_IDS)
        or any(name in identifiers for name in heldout_ids)
    ):
        raise ValueError("Winner-v80 training population changed")
    table = complete_teacher_table()

    parameters = snapshot["parameters"]
    source_parameter_copy = v63.tree_copy(parameters)
    source_optimizer_copy = {
        "count": np.asarray(snapshot["optimizer"]["count"]).copy(),
        "m": v63.tree_copy(snapshot["optimizer"]["m"]),
        "v": v63.tree_copy(snapshot["optimizer"]["v"]),
    }
    batch_np, episodes, observations = v20.stage2_rollout(
        smoke=smoke,
        full=full,
        training=training,
        mujoco=mujoco,
        scene=scene,
        population=population,
        preregistration=calibrator_design,
        observer_type=observer_type,
        canonical_fit=args.canonical_fit,
        parameters=parameters,
        update_index=SOURCE_COUNT,
    )
    full.validate_stage2_masks(batch_np, episodes)
    episode_hash = full.validate_episode_receipts(
        episodes, population, stage=2, update_index=SOURCE_COUNT
    )
    boundary = full.stage2_action_boundary_evidence(batch_np)
    batch = {key: jnp.asarray(value) for key, value in batch_np.items()}
    before = v21.joint_trainable_parameters(parameters)

    def objective(values_tree: Mapping[str, Any]):
        return pitch_teacher_loss(
            values_tree,
            batch=batch,
            batch_np=batch_np,
            identifiers=identifiers,
            table=table,
            training=training,
            v29=v29,
            jnp=jnp,
        )

    (loss_before, metrics_before), raw_gradient = jax.value_and_grad(
        objective, has_aux=True
    )(before)
    scaled_gradient = {
        key: jnp.asarray(value, dtype=jnp.float32) * jnp.asarray(PITCH_TEACHER_SCALE)
        for key, value in raw_gradient.items()
    }
    projected_gradient = project_pitch_head_gradient(scaled_gradient, jnp)
    projected_nonzero = {
        key: int(np.count_nonzero(np.asarray(value)))
        for key, value in projected_gradient.items()
    }
    raw_gradient_max = {
        key: float(np.max(np.abs(np.asarray(value))))
        for key, value in raw_gradient.items()
    }

    zero_m = {key: jnp.zeros_like(value) for key, value in snapshot["optimizer"]["m"].items()}
    zero_v = {key: jnp.zeros_like(value) for key, value in snapshot["optimizer"]["v"].items()}
    fresh_optimizer = {
        "count": jnp.asarray(snapshot["optimizer"]["count"]),
        "m": zero_m,
        "v": zero_v,
    }
    proposed_raw, proposed_optimizer = training.adam_step(
        before,
        projected_gradient,
        fresh_optimizer,
        learning_rate=training.STAGE2_LEARNING_RATE,
        beta1=training.ADAM_BETA1,
        beta2=training.ADAM_BETA2,
        epsilon=training.ADAM_EPSILON,
    )
    proposed = training.clamp_stage2_parameters(proposed_raw)
    full_delta = {
        key: jnp.asarray(proposed[key], dtype=jnp.float32)
        - jnp.asarray(before[key], dtype=jnp.float32)
        for key in before
    }
    rows: list[dict[str, float]] = []
    trials: list[dict[str, Any]] = []
    for fraction in FRACTIONS:
        trial = {
            key: jnp.asarray(before[key], dtype=jnp.float32)
            + jnp.asarray(fraction, dtype=jnp.float32) * full_delta[key]
            for key in before
        }
        trial = training.clamp_stage2_parameters(trial)
        loss, _ = objective(trial)
        rows.append(
            {
                "fraction": float(fraction),
                "loss": float(loss),
                "loss_delta": float(loss) - float(loss_before),
            }
        )
        trials.append(trial)
    accepted_index = next(
        (index for index, row in enumerate(rows) if row["loss"] < float(loss_before)),
        None,
    )
    if accepted_index is None:
        result = {
            "schema_version": "winner_v80.pitch_action_head_step_result.v1",
            "status": "HOLD_WINNER_V80_PITCH_ACTION_HEAD_STEP",
            "decision": "DO_NOT_CONTINUE_PITCH_ACTION_HEAD_TRAINING",
            "optimization": {
                "loss_before": float(loss_before),
                "backtracking_rows": rows,
            },
            "execution": {
                "optimizer_updates": 0,
                "formal_support_cells": 0,
                "locomotion_steps": 0,
                "robot_or_rdk_access": 0,
            },
            "authority": contract["authority"],
        }
        args.output.write_text(
            json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(result["status"])
        return 2

    accepted = trials[accepted_index]
    accepted_row = rows[accepted_index]
    loss_after, metrics_after = objective(accepted)
    parameters_after = v21.merge_joint_trainable(parameters, accepted)
    pitch = jnp.asarray(PITCH_INDICES, dtype=jnp.int32)
    optimizer_after = {
        "count": jnp.asarray(proposed_optimizer["count"]),
        "m": {
            key: jnp.asarray(value)
            for key, value in snapshot["optimizer"]["m"].items()
        },
        "v": {
            key: jnp.asarray(value)
            for key, value in snapshot["optimizer"]["v"].items()
        },
    }
    optimizer_after["m"]["action_weight"] = optimizer_after["m"][
        "action_weight"
    ].at[:, pitch].set(proposed_optimizer["m"]["action_weight"][:, pitch])
    optimizer_after["v"]["action_weight"] = optimizer_after["v"][
        "action_weight"
    ].at[:, pitch].set(proposed_optimizer["v"]["action_weight"][:, pitch])
    optimizer_after["m"]["action_bias"] = optimizer_after["m"]["action_bias"].at[
        pitch
    ].set(proposed_optimizer["m"]["action_bias"][pitch])
    optimizer_after["v"]["action_bias"] = optimizer_after["v"]["action_bias"].at[
        pitch
    ].set(proposed_optimizer["v"]["action_bias"][pitch])

    target_mean = jnp.asarray(snapshot["target_mean"], dtype=jnp.float32)
    target_std = jnp.asarray(snapshot["target_std"], dtype=jnp.float32)
    predictor_before = v22.normalized_predictor_loss(
        before, batch, target_mean, target_std
    )[0]
    predictor_after = v22.normalized_predictor_loss(
        accepted, batch, target_mean, target_std
    )[0]
    selected_deltas = selected_delta_metrics(before, accepted)

    (args.work_root / "snapshots").mkdir(parents=True)
    (args.work_root / "graphs").mkdir()
    snapshot_path = (
        args.work_root / "snapshots" / "snapshot_pitch_action_head_update_656.npz"
    )
    snapshot_receipt = v22v2.save_snapshot(
        snapshot_path,
        parameters_after,
        optimizer_after,
        {
            "stage": "pitch_action_head_teacher_joint_stage2",
            "completed_updates": COMPLETED_COUNT,
            "source_completed_updates": SOURCE_COUNT,
            "source_snapshot_sha256": source_receipt["sha256"],
            "teacher_snapshot_sha256": metadata["teacher_snapshot_sha256"],
            "objective": contract["objective"],
            "root_seed": 120120,
            "learning_rate": float(training.STAGE2_LEARNING_RATE),
            "accepted_backtracking_fraction": accepted_row["fraction"],
            "fresh_moment_slices": contract["step"]["fresh_moment_slices"],
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        snapshot["target_mean"],
        snapshot["target_std"],
    )
    loaded = v22v2.load_snapshot(snapshot_path)
    snapshot_exact = bool(
        v63.tree_bit_exact(parameters_after, loaded["parameters"])
        and np.array_equal(optimizer_after["count"], loaded["optimizer"]["count"])
        and v63.tree_bit_exact(optimizer_after["m"], loaded["optimizer"]["m"])
        and v63.tree_bit_exact(optimizer_after["v"], loaded["optimizer"]["v"])
        and loaded["metadata"].get("completed_updates") == COMPLETED_COUNT
        and loaded["metadata"].get("stage")
        == "pitch_action_head_teacher_joint_stage2"
    )
    graph = v46.graph_receipt(
        smoke=smoke,
        networks=networks,
        training=training,
        parameters=parameters_after,
        observations=observations,
        path=args.work_root / "graphs" / "winner_v80_pitch_action_head_update_656.onnx",
        label="proof",
        completed_updates=COMPLETED_COUNT,
    )

    source_unchanged = bool(
        v63.tree_bit_exact(source_parameter_copy, parameters)
        and np.array_equal(source_optimizer_copy["count"], snapshot["optimizer"]["count"])
        and v63.tree_bit_exact(source_optimizer_copy["m"], snapshot["optimizer"]["m"])
        and v63.tree_bit_exact(source_optimizer_copy["v"], snapshot["optimizer"]["v"])
    )
    checks = {
        "exact_12_training_teacher_configurations_each_two_plants": all(
            identifiers.count(name) == 2 for name in TRAINING_TEACHER_IDS
        ),
        "no_heldout_teacher_label": all(name not in identifiers for name in heldout_ids),
        "unprojected_pitch_gradient_nonzero": (
            raw_gradient_max["action_weight"] > 0.0
            and raw_gradient_max["action_bias"] > 0.0
        ),
        "projected_gradient_nonzero_only_on_two_allowed_slices": (
            projected_nonzero["action_weight"] > 0
            and projected_nonzero["action_bias"] > 0
            and all(
                count == 0
                for key, count in projected_nonzero.items()
                if key not in {"action_weight", "action_bias"}
            )
            and np.count_nonzero(
                np.asarray(projected_gradient["action_weight"])[:, NONPITCH_INDICES]
            )
            == 0
            and np.count_nonzero(
                np.asarray(projected_gradient["action_bias"])[list(NONPITCH_INDICES)]
            )
            == 0
        ),
        "first_accepted_fraction_strictly_descends": (
            float(loss_after) < float(loss_before)
            and all(row["loss"] >= float(loss_before) for row in rows[:accepted_index])
        ),
        "same_batch_predictor_loss_bit_exact": bool(
            np.array_equal(np.asarray(predictor_before), np.asarray(predictor_after))
        ),
        "all_unselected_parameter_elements_bit_exact": unselected_elements_exact(
            before, accepted
        ),
        "both_selected_parameter_slices_change": all(
            value > 0.0 for value in selected_deltas.values()
        ),
        "all_unselected_optimizer_moment_elements_bit_exact": (
            unselected_elements_exact(snapshot["optimizer"]["m"], optimizer_after["m"])
            and unselected_elements_exact(snapshot["optimizer"]["v"], optimizer_after["v"])
        ),
        "optimizer_count_655_to_656_exact": int(np.asarray(optimizer_after["count"]))
        == COMPLETED_COUNT,
        "action_boundary_exact": bool(boundary["all_exact"]),
        "source_state_unchanged": source_unchanged,
        "all_parameters_optimizer_losses_metrics_finite": training.finite_tree(
            {
                "parameters": parameters_after,
                "optimizer": optimizer_after,
                "loss_before": loss_before,
                "loss_after": loss_after,
                "metrics_before": metrics_before,
                "metrics_after": metrics_after,
                "predictor_before": predictor_before,
                "predictor_after": predictor_after,
            }
        ),
        "snapshot_readback_exact": snapshot_exact,
        "onnx_abi_exact": graph["contract"]["abi_exact"],
        "onnx_training_only_tensors_absent": graph["contract"][
            "training_only_tensors_absent"
        ],
        "onnx_jax_chain_at_most_1e_7": graph["contract"]["jax_onnx_at_most_1e_7"],
        "onnx_previous_action_chain_exact": graph["contract"][
            "previous_action_out_equals_action_bit_exact"
        ],
        "formal_support_continuation_robot_zero": True,
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    if failed_checks:
        raise ValueError(f"Winner-v80 proof invalid: {failed_checks}")
    result = {
        "schema_version": "winner_v80.pitch_action_head_step_result.v1",
        "status": "PASS_WINNER_V80_PITCH_ACTION_HEAD_STEP",
        "decision": "PREREGISTER_BOUNDED_PITCH_ACTION_HEAD_CONTINUATION_ONLY",
        "source": {
            "snapshot": source_receipt,
            "optimizer_count": SOURCE_COUNT,
            "rollout_update_index": SOURCE_COUNT,
            "episode_receipts_sha256": episode_hash,
        },
        "optimization": {
            "optimizer_count_before": SOURCE_COUNT,
            "optimizer_count_after": int(np.asarray(optimizer_after["count"])),
            "loss_before": float(loss_before),
            "accepted_loss": float(loss_after),
            "accepted_loss_delta": float(loss_after) - float(loss_before),
            "accepted_fraction": accepted_row["fraction"],
            "backtracking_rows": rows,
            "selected_parameter_max_abs_delta": selected_deltas,
            "raw_gradient_leaf_max_abs": raw_gradient_max,
            "projected_gradient_nonzero_counts": projected_nonzero,
            "selected_teacher_elements": int(np.asarray(metrics_before["selected_elements"])),
            "predictor_loss_before": float(predictor_before),
            "predictor_loss_after": float(predictor_after),
        },
        "snapshot": snapshot_receipt,
        "graph": graph,
        "checks": {key: bool(value) for key, value in checks.items()},
        "failed_checks": [],
        "execution": {
            "optimizer_updates": 1,
            "continuation_optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": contract["authority"],
        "sources": contract["sources"],
        "source_manifest_sha256": contract["source_manifest_sha256"],
    }
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"accepted_fraction={accepted_row['fraction']}")
    print(f"loss={float(loss_before)}->{float(loss_after)}")
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
