#!/usr/bin/env python3
"""Run the frozen Winner-v84 negative-gradient pitch-head continuation."""

from __future__ import annotations

import argparse
import hashlib
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
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

import build_winner_v84_negative_gradient_pitch_head_continuation_preregistration as builder  # noqa: E402
import run_winner_v46_static_target_teacher_training as v46  # noqa: E402
import run_winner_v63_persistent_teacher_conflict_attribution as v63  # noqa: E402
import run_winner_v81_pitch_action_head_continuation as v81  # noqa: E402
import run_winner_v82_count675_direction_precision_attribution as v82  # noqa: E402


PREREGISTRATION = (
    ANALYSIS / "winner_v84_negative_gradient_pitch_head_continuation_preregistration.json"
)
V83_RESULT = ANALYSIS / "winner_v83_count675_negative_gradient_step_result.json"
FULL_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    continuation = value.get("continuation", {})
    if (
        value.get("schema_version")
        != "winner_v84.negative_gradient_pitch_head_continuation_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V84_NEGATIVE_GRADIENT_PITCH_HEAD_CONTINUATION"
        or value.get("decision")
        != "AUTHORIZE_ONE_80_UPDATE_NEGATIVE_GRADIENT_PITCH_HEAD_CONTINUATION_ONLY"
        or continuation.get("optimizer_updates") != builder.CONTINUATION_UPDATES
        or continuation.get("source_optimizer_count") != builder.SOURCE_COUNT
        or continuation.get("half_optimizer_count") != builder.HALF_COUNT
        or continuation.get("final_optimizer_count") != builder.FINAL_COUNT
        or continuation.get("fractions_largest_first") != list(builder.FRACTIONS)
        or continuation.get("optimizer_m_and_v_transition")
        != "all elements bit-exact preserved across all updates"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v84 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v84 source manifest absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or builder.lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v84 source changed: {name}")
    if builder.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v84 source manifest changed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-snapshot", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--negative-gradient-continuation-authorized", action="store_true")
    args = parser.parse_args()
    if (
        not args.offline_cpu_only
        or not args.negative_gradient_continuation_authorized
    ):
        raise PermissionError(
            "Winner-v84 requires --offline-cpu-only "
            "--negative-gradient-continuation-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v84 evidence")

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
        raise ValueError("Winner-v84 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    proof = json.loads(V83_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V83_RESULT) != builder.V83_RESULT_SHA256
        or proof.get("status") != "PASS_WINNER_V83_COUNT675_NEGATIVE_GRADIENT_STEP"
        or proof.get("decision")
        != "PREREGISTER_BOUNDED_NEGATIVE_GRADIENT_PITCH_HEAD_CONTINUATION_ONLY"
        or proof.get("failed_checks") != []
    ):
        raise ValueError("Winner-v84 source proof changed")
    source_receipt = proof["snapshot"]
    v80 = v81.v80_module()
    v80.validate_artifact(args.source_snapshot, source_receipt, "source snapshot")
    snapshot = v22v2.load_snapshot(args.source_snapshot)
    if (
        int(np.asarray(snapshot["optimizer"]["count"])) != builder.SOURCE_COUNT
        or snapshot["metadata"].get("completed_updates") != builder.SOURCE_COUNT
        or snapshot["metadata"].get("stage")
        != "negative_gradient_pitch_action_head_step"
    ):
        raise ValueError("Winner-v84 source snapshot boundary changed")

    smoke, gate, _ = v80.configured_stack()
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v84 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v84 canonical fit changed")
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    full_design = json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8"))
    calibrator_design = gate.load_calibrator_design(full_design)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    population = full.training_population(full_design, domain)
    identifiers = [str(row["id"]) for row in population]
    heldout_ids = ("HELDOUT_04", "HELDOUT_07", "HELDOUT_09", "HELDOUT_15")
    if (
        len(population) != 80
        or any(identifiers.count(name) != 2 for name in v80.TRAINING_TEACHER_IDS)
        or any(name in identifiers for name in heldout_ids)
    ):
        raise ValueError("Winner-v84 population changed")
    table = v80.complete_teacher_table()
    parameters = snapshot["parameters"]
    optimizer = snapshot["optimizer"]
    source_parameters = v63.tree_copy(parameters)
    source_optimizer = {
        "count": np.asarray(optimizer["count"]).copy(),
        "m": v63.tree_copy(optimizer["m"]),
        "v": v63.tree_copy(optimizer["v"]),
    }
    target_mean = jnp.asarray(snapshot["target_mean"], dtype=jnp.float32)
    target_std = jnp.asarray(snapshot["target_std"], dtype=jnp.float32)
    args.work_root.mkdir(parents=True)
    (args.work_root / "snapshots").mkdir()
    (args.work_root / "graphs").mkdir()
    metrics: list[dict[str, Any]] = []
    snapshots: list[dict[str, Any]] = []
    checkpoints: list[dict[str, Any]] = []

    for completed_count in range(builder.SOURCE_COUNT + 1, builder.FINAL_COUNT + 1):
        rollout_update_index = completed_count - 1
        before = v21.joint_trainable_parameters(parameters)
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
            update_index=rollout_update_index,
        )
        full.validate_stage2_masks(batch_np, episodes)
        episode_hash = full.validate_episode_receipts(
            episodes, population, stage=2, update_index=rollout_update_index
        )
        boundary = full.stage2_action_boundary_evidence(batch_np)
        batch = {key: jnp.asarray(value) for key, value in batch_np.items()}

        def objective(values_tree: Mapping[str, Any]):
            return v80.pitch_teacher_loss(
                values_tree,
                batch=batch,
                batch_np=batch_np,
                identifiers=identifiers,
                table=table,
                training=training,
                v29=v29,
                jnp=jnp,
            )

        (loss_value, objective_metrics), raw_gradient = jax.value_and_grad(
            objective, has_aux=True
        )(before)
        loss_before = float(loss_value)
        scaled_gradient = {
            key: jnp.asarray(value, dtype=jnp.float32)
            * jnp.asarray(v80.PITCH_TEACHER_SCALE, dtype=jnp.float32)
            for key, value in raw_gradient.items()
        }
        gradient = v80.project_pitch_head_gradient(scaled_gradient, jnp)
        work_m = {key: jnp.zeros_like(value) for key, value in optimizer["m"].items()}
        work_v = {key: jnp.zeros_like(value) for key, value in optimizer["v"].items()}
        for key in ("action_weight", "action_bias"):
            work_m[key] = v81.set_target_slices(work_m[key], optimizer["m"][key], jnp)
            work_v[key] = v81.set_target_slices(work_v[key], optimizer["v"][key], jnp)
        inherited_optimizer = {
            "count": jnp.asarray(optimizer["count"]),
            "m": work_m,
            "v": work_v,
        }
        adam_raw, adam_optimizer = training.adam_step(
            before,
            gradient,
            inherited_optimizer,
            learning_rate=training.STAGE2_LEARNING_RATE,
            beta1=training.ADAM_BETA1,
            beta2=training.ADAM_BETA2,
            epsilon=training.ADAM_EPSILON,
        )
        adam_proposed = training.clamp_stage2_parameters(adam_raw)
        adam_delta = {
            key: jnp.asarray(adam_proposed[key], dtype=jnp.float32)
            - jnp.asarray(before[key], dtype=jnp.float32)
            for key in before
        }
        gradient_l2 = v82.tree_l2(gradient)
        adam_delta_l2 = v82.tree_l2(adam_delta)
        if gradient_l2 <= 0.0 or adam_delta_l2 <= 0.0:
            raise ValueError(f"Winner-v84 zero direction at count {completed_count}")
        negative_gradient_delta = {
            key: -jnp.asarray(value, dtype=jnp.float32)
            * jnp.asarray(adam_delta_l2 / gradient_l2, dtype=jnp.float32)
            for key, value in gradient.items()
        }
        rows = v82.fraction_rows(
            before=before,
            delta=negative_gradient_delta,
            fractions=builder.FRACTIONS,
            loss_before=loss_before,
            objective=objective,
            training=training,
            jnp=jnp,
        )
        accepted_index = next(
            (index for index, row in enumerate(rows) if row["loss"] < loss_before), None
        )
        if accepted_index is None:
            result = {
                "schema_version": "winner_v84.negative_gradient_pitch_head_continuation_result.v1",
                "status": "HOLD_WINNER_V84_NEGATIVE_GRADIENT_PITCH_HEAD_CONTINUATION",
                "decision": "DO_NOT_RUN_PERSISTENCE_GATE",
                "stop": {
                    "attempted_completed_count": completed_count,
                    "loss_before": loss_before,
                    "adam_delta_l2": adam_delta_l2,
                    "scaled_teacher_gradient_l2": gradient_l2,
                    "backtracking_rows": rows,
                },
                "metrics": metrics,
                "snapshot_manifest": snapshots,
                "persistent_checkpoints": checkpoints,
                "execution": {
                    "optimizer_updates": len(metrics),
                    "formal_support_cells": 0,
                    "locomotion_steps": 0,
                    "robot_or_rdk_access": 0,
                },
                "authority": preregistration["authority"],
                "sources": preregistration["sources"],
                "source_manifest_sha256": preregistration["source_manifest_sha256"],
            }
            args.output.write_text(
                json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            print(result["status"], flush=True)
            print(f"sha256={sha256(args.output)}", flush=True)
            return 2
        accepted_row = rows[accepted_index]
        accepted = {
            key: jnp.asarray(before[key], dtype=jnp.float32)
            + jnp.asarray(accepted_row["fraction"], dtype=jnp.float32)
            * jnp.asarray(negative_gradient_delta[key], dtype=jnp.float32)
            for key in before
        }
        accepted = training.clamp_stage2_parameters(accepted)
        loss_after, _ = objective(accepted)
        parameters_after = v21.merge_joint_trainable(parameters, accepted)
        optimizer_after = {
            "count": jnp.asarray(adam_optimizer["count"]),
            "m": {key: jnp.asarray(value) for key, value in optimizer["m"].items()},
            "v": {key: jnp.asarray(value) for key, value in optimizer["v"].items()},
        }
        predictor_before = v22.normalized_predictor_loss(
            before, batch, target_mean, target_std
        )[0]
        predictor_after = v22.normalized_predictor_loss(
            accepted, batch, target_mean, target_std
        )[0]
        selected_deltas = v80.selected_delta_metrics(before, accepted)
        update_valid = bool(
            float(loss_after) < loss_before
            and all(row["loss"] >= loss_before for row in rows[:accepted_index])
            and v80.unselected_elements_exact(before, accepted)
            and all(value > 0.0 for value in selected_deltas.values())
            and v63.tree_bit_exact(optimizer["m"], optimizer_after["m"])
            and v63.tree_bit_exact(optimizer["v"], optimizer_after["v"])
            and int(np.asarray(optimizer_after["count"])) == completed_count
            and np.array_equal(np.asarray(predictor_before), np.asarray(predictor_after))
            and boundary["realized_equals_numpy_bit_exact"]
            and boundary["numpy_equals_jax_bit_exact"]
            and training.finite_tree(
                {
                    "parameters": parameters_after,
                    "optimizer": optimizer_after,
                    "loss_before": loss_value,
                    "loss_after": loss_after,
                }
            )
        )
        if not update_valid:
            raise ValueError(f"Winner-v84 update {completed_count} invariant failed")
        snapshot_path = (
            args.work_root
            / "snapshots"
            / f"snapshot_negative_gradient_pitch_head_update_{completed_count}.npz"
        )
        receipt = v22v2.save_snapshot(
            snapshot_path,
            parameters_after,
            optimizer_after,
            {
                "stage": "negative_gradient_pitch_action_head_continuation",
                "completed_updates": completed_count,
                "source_completed_updates": builder.SOURCE_COUNT,
                "source_snapshot_sha256": source_receipt["sha256"],
                "teacher_snapshot_sha256": snapshot["metadata"]["teacher_snapshot_sha256"],
                "objective": preregistration["objective"],
                "root_seed": 120120,
                "learning_rate": float(training.STAGE2_LEARNING_RATE),
                "accepted_backtracking_fraction": accepted_row["fraction"],
                "adam_delta_l2": adam_delta_l2,
                "scaled_teacher_gradient_l2": gradient_l2,
                "optimizer_m_and_v_transition": "all elements bit-exact preserved",
                "formal_support_cells": 0,
                "locomotion_steps": 0,
                "robot_or_rdk_access": 0,
            },
            snapshot["target_mean"],
            snapshot["target_std"],
        )
        loaded = v22v2.load_snapshot(snapshot_path)
        readback = bool(
            v63.tree_bit_exact(parameters_after, loaded["parameters"])
            and np.array_equal(optimizer_after["count"], loaded["optimizer"]["count"])
            and v63.tree_bit_exact(optimizer_after["m"], loaded["optimizer"]["m"])
            and v63.tree_bit_exact(optimizer_after["v"], loaded["optimizer"]["v"])
            and loaded["metadata"].get("completed_updates") == completed_count
        )
        if not readback:
            raise ValueError(f"Winner-v84 snapshot {completed_count} readback changed")
        snapshots.append({"completed_updates": completed_count, **receipt})
        metrics.append(
            {
                "completed_updates": completed_count,
                "rollout_update_index": rollout_update_index,
                "episode_receipts_sha256": episode_hash,
                "loss_before": loss_before,
                "loss_after": float(loss_after),
                "loss_delta": float(loss_after) - loss_before,
                "accepted_fraction": accepted_row["fraction"],
                "adam_delta_l2": adam_delta_l2,
                "scaled_teacher_gradient_l2": gradient_l2,
                "selected_teacher_elements": int(
                    np.asarray(objective_metrics["selected_elements"])
                ),
                "predictor_loss_before": float(predictor_before),
                "predictor_loss_after": float(predictor_after),
                "selected_parameter_max_abs_delta": selected_deltas,
                "unselected_parameters_exact": True,
                "optimizer_m_and_v_bit_exact": True,
                "snapshot_readback_exact": True,
                "action_boundary_exact": True,
            }
        )
        parameters = parameters_after
        optimizer = optimizer_after
        if completed_count in {builder.HALF_COUNT, builder.FINAL_COUNT}:
            label = "half" if completed_count == builder.HALF_COUNT else "final"
            graph = v46.graph_receipt(
                smoke=smoke,
                networks=networks,
                training=training,
                parameters=parameters,
                observations=observations,
                path=args.work_root / "graphs" / f"winner_v84_{label}.onnx",
                label=label,
                completed_updates=completed_count,
            )
            checkpoints.append(
                {
                    "label": label,
                    "completed_updates": completed_count,
                    "snapshot": receipt,
                    "graph": graph,
                }
            )
        print(
            f"count={completed_count} fraction={accepted_row['fraction']} "
            f"loss={loss_before:.10f}->{float(loss_after):.10f}",
            flush=True,
        )

    final_trainable = v21.joint_trainable_parameters(parameters)
    source_trainable = v21.joint_trainable_parameters(source_parameters)
    checks = {
        "exact_80_updates_676_through_755": (
            len(metrics) == builder.CONTINUATION_UPDATES
            and [row["completed_updates"] for row in metrics] == list(range(676, 756))
        ),
        "every_update_first_strict_same_batch_descent": all(
            row["loss_after"] < row["loss_before"] for row in metrics
        ),
        "same_batch_predictor_loss_bit_exact_every_update": all(
            row["predictor_loss_after"] == row["predictor_loss_before"] for row in metrics
        ),
        "all_unselected_parameter_elements_bit_exact": (
            v80.unselected_elements_exact(source_trainable, final_trainable)
            and all(row["unselected_parameters_exact"] for row in metrics)
        ),
        "all_optimizer_m_and_v_elements_bit_exact": (
            v63.tree_bit_exact(source_optimizer["m"], optimizer["m"])
            and v63.tree_bit_exact(source_optimizer["v"], optimizer["v"])
            and all(row["optimizer_m_and_v_bit_exact"] for row in metrics)
        ),
        "all_80_snapshots_digest_readback_exact": (
            len(snapshots) == builder.CONTINUATION_UPDATES
            and all(row["snapshot_readback_exact"] for row in metrics)
        ),
        "half_and_final_stateful_onnx_contracts_exact": (
            [(row["label"], row["completed_updates"]) for row in checkpoints]
            == [("half", builder.HALF_COUNT), ("final", builder.FINAL_COUNT)]
            and all(
                row["graph"]["contract"]["abi_exact"]
                and row["graph"]["contract"]["training_only_tensors_absent"]
                and row["graph"]["contract"]["jax_onnx_at_most_1e_7"]
                and row["graph"]["contract"][
                    "previous_action_out_equals_action_bit_exact"
                ]
                for row in checkpoints
            )
        ),
        "all_metrics_finite": all(
            math.isfinite(value)
            for row in metrics
            for key, value in row.items()
            if key
            in {
                "loss_before",
                "loss_after",
                "loss_delta",
                "adam_delta_l2",
                "scaled_teacher_gradient_l2",
                "predictor_loss_before",
                "predictor_loss_after",
            }
        ),
        "no_posthoc_fraction_length_or_checkpoint_change": True,
        "formal_support_selection_deployment_robot_zero": True,
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    if failed_checks:
        raise ValueError(f"Winner-v84 continuation invalid: {failed_checks}")
    result = {
        "schema_version": "winner_v84.negative_gradient_pitch_head_continuation_result.v1",
        "status": "PASS_WINNER_V84_NEGATIVE_GRADIENT_PITCH_HEAD_CONTINUATION",
        "decision": "AUTHORIZE_UNCHANGED_PERSISTENCE_GATE_FOR_COUNTS_705_AND_755_ONLY",
        "source_snapshot": source_receipt,
        "source_graph": proof["graph"],
        "objective": preregistration["objective"],
        "metrics": metrics,
        "snapshot_manifest": snapshots,
        "persistent_checkpoints": checkpoints,
        "checks": {key: bool(value) for key, value in checks.items()},
        "failed_checks": [],
        "execution": {
            "optimizer_updates": len(metrics),
            "rollout_episode_slots": 80 * len(metrics),
            "scheduled_rollout_ticks": 20000 * len(metrics),
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": preregistration["authority"],
        "sources": preregistration["sources"],
        "source_manifest_sha256": preregistration["source_manifest_sha256"],
    }
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"], flush=True)
    print(f"sha256={sha256(args.output)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
