#!/usr/bin/env python3
"""Run the frozen bounded Winner-v81 pitch-action-head continuation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import types
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

import build_winner_v81_pitch_action_head_continuation_preregistration as builder  # noqa: E402
import run_winner_v46_static_target_teacher_training as v46  # noqa: E402
import run_winner_v63_persistent_teacher_conflict_attribution as v63  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v81_pitch_action_head_continuation_preregistration.json"
V80_RESULT = ANALYSIS / "winner_v80_pitch_action_head_step_result.json"
FULL_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
SOURCE_COUNT = builder.SOURCE_COUNT
HALF_COUNT = builder.HALF_COUNT
FINAL_COUNT = builder.FINAL_COUNT
FRACTIONS = tuple(builder.FRACTIONS)
PITCH_INDICES = (2, 3, 4, 11, 12, 13)
NONPITCH_INDICES = tuple(index for index in range(14) if index not in PITCH_INDICES)


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


def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v81.pitch_action_head_continuation_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V81_PITCH_ACTION_HEAD_CONTINUATION"
        or value.get("decision")
        != "AUTHORIZE_ONE_99_UPDATE_PITCH_ACTION_HEAD_CONTINUATION_ONLY"
        or value.get("continuation", {}).get("optimizer_updates") != 99
        or value.get("continuation", {}).get("source_optimizer_count") != SOURCE_COUNT
        or value.get("continuation", {}).get("half_optimizer_count") != HALF_COUNT
        or value.get("continuation", {}).get("final_optimizer_count") != FINAL_COUNT
        or value.get("continuation", {}).get("fractions_largest_first")
        != list(FRACTIONS)
        or value.get("continuation", {}).get("snapshot_every_accepted_update")
        is not True
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v81 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v81 source manifest absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v81 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v81 source manifest changed")


def v80_module() -> Any:
    import build_winner_v80c_action_boundary_check_correction as v80c

    source, _ = v80c.corrected_source()
    module = types.ModuleType("winner_v81_v80_reviewed_step")
    module.__file__ = str(ROOT / "tools/run_winner_v80c_action_boundary_check_correction.py")
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


def set_target_slices(base: Any, target: Any, jnp: Any) -> Any:
    pitch = jnp.asarray(PITCH_INDICES, dtype=jnp.int32)
    result = jnp.asarray(base)
    if result.ndim == 2:
        return result.at[:, pitch].set(jnp.asarray(target)[:, pitch])
    if result.ndim == 1:
        return result.at[pitch].set(jnp.asarray(target)[pitch])
    raise ValueError("Winner-v81 mutable moment rank changed")


def gradient_dot_delta(gradient: Mapping[str, Any], delta: Mapping[str, Any]) -> float:
    return float(
        np.dot(
            np.asarray(gradient["action_weight"], dtype=np.float64)[:, PITCH_INDICES].ravel(),
            np.asarray(delta["action_weight"], dtype=np.float64)[:, PITCH_INDICES].ravel(),
        )
        + np.dot(
            np.asarray(gradient["action_bias"], dtype=np.float64)[list(PITCH_INDICES)],
            np.asarray(delta["action_bias"], dtype=np.float64)[list(PITCH_INDICES)],
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-snapshot", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--pitch-action-head-continuation-authorized", action="store_true")
    args = parser.parse_args()
    if (
        not args.offline_cpu_only
        or not args.pitch_action_head_continuation_authorized
    ):
        raise PermissionError(
            "Winner-v81 requires --offline-cpu-only "
            "--pitch-action-head-continuation-authorized"
        )
    if args.work_root.exists() or args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v81 evidence")

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
        raise ValueError("Winner-v81 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    proof = json.loads(V80_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V80_RESULT) != builder.V80_RESULT_SHA256
        or proof.get("status") != "PASS_WINNER_V80_PITCH_ACTION_HEAD_STEP"
        or proof.get("failed_checks") != []
    ):
        raise ValueError("Winner-v81 source proof changed")
    v80 = v80_module()
    v80.validate_artifact(args.source_snapshot, proof["snapshot"], "source snapshot")
    snapshot = v22v2.load_snapshot(args.source_snapshot)
    if (
        int(np.asarray(snapshot["optimizer"]["count"])) != SOURCE_COUNT
        or snapshot["metadata"].get("completed_updates") != SOURCE_COUNT
        or snapshot["metadata"].get("stage")
        != "pitch_action_head_teacher_joint_stage2"
    ):
        raise ValueError("Winner-v81 source snapshot boundary changed")

    smoke, gate, _ = v80.configured_stack()
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v81 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v81 canonical fit changed")
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
        or any(
            identifiers.count(name) != 2
            for name in v80.TRAINING_TEACHER_IDS
        )
        or any(name in identifiers for name in heldout_ids)
    ):
        raise ValueError("Winner-v81 population changed")
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
    snapshot_manifest: list[dict[str, Any]] = []
    checkpoints: list[dict[str, Any]] = []

    for completed_count in range(SOURCE_COUNT + 1, FINAL_COUNT + 1):
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

        (loss_before, objective_metrics), raw_gradient = jax.value_and_grad(
            objective, has_aux=True
        )(before)
        scaled_gradient = {
            key: jnp.asarray(value, dtype=jnp.float32)
            * jnp.asarray(v80.PITCH_TEACHER_SCALE, dtype=jnp.float32)
            for key, value in raw_gradient.items()
        }
        gradient = v80.project_pitch_head_gradient(scaled_gradient, jnp)

        def proposal(*, reset_moments: bool):
            work_m = {key: jnp.zeros_like(value) for key, value in optimizer["m"].items()}
            work_v = {key: jnp.zeros_like(value) for key, value in optimizer["v"].items()}
            if not reset_moments:
                work_m["action_weight"] = set_target_slices(
                    work_m["action_weight"], optimizer["m"]["action_weight"], jnp
                )
                work_v["action_weight"] = set_target_slices(
                    work_v["action_weight"], optimizer["v"]["action_weight"], jnp
                )
                work_m["action_bias"] = set_target_slices(
                    work_m["action_bias"], optimizer["m"]["action_bias"], jnp
                )
                work_v["action_bias"] = set_target_slices(
                    work_v["action_bias"], optimizer["v"]["action_bias"], jnp
                )
            work_optimizer = {
                "count": jnp.asarray(optimizer["count"]),
                "m": work_m,
                "v": work_v,
            }
            proposed_raw, proposed_optimizer = training.adam_step(
                before,
                gradient,
                work_optimizer,
                learning_rate=training.STAGE2_LEARNING_RATE,
                beta1=training.ADAM_BETA1,
                beta2=training.ADAM_BETA2,
                epsilon=training.ADAM_EPSILON,
            )
            proposed = training.clamp_stage2_parameters(proposed_raw)
            delta = {
                key: jnp.asarray(proposed[key], dtype=jnp.float32)
                - jnp.asarray(before[key], dtype=jnp.float32)
                for key in before
            }
            rows = []
            trials = []
            for fraction in FRACTIONS:
                trial = {
                    key: jnp.asarray(before[key], dtype=jnp.float32)
                    + jnp.asarray(fraction, dtype=jnp.float32) * delta[key]
                    for key in before
                }
                trial = training.clamp_stage2_parameters(trial)
                trial_loss, _ = objective(trial)
                rows.append(
                    {
                        "fraction": float(fraction),
                        "loss": float(trial_loss),
                        "loss_delta": float(trial_loss) - float(loss_before),
                    }
                )
                trials.append(trial)
            accepted_index = next(
                (
                    index
                    for index, row in enumerate(rows)
                    if row["loss"] < float(loss_before)
                ),
                None,
            )
            return {
                "optimizer": proposed_optimizer,
                "delta": delta,
                "dot": gradient_dot_delta(gradient, delta),
                "rows": rows,
                "trials": trials,
                "accepted_index": accepted_index,
            }

        selected = proposal(reset_moments=False)
        moment_reset = False
        if selected["accepted_index"] is None and selected["dot"] >= 0.0:
            selected = proposal(reset_moments=True)
            moment_reset = True
        if selected["accepted_index"] is None:
            result = {
                "schema_version": "winner_v81.pitch_action_head_continuation_result.v1",
                "status": "HOLD_WINNER_V81_PITCH_ACTION_HEAD_CONTINUATION",
                "decision": "DO_NOT_RUN_PERSISTENCE_GATE",
                "stop": {
                    "attempted_completed_count": completed_count,
                    "loss_before": float(loss_before),
                    "gradient_dot_proposed_delta": selected["dot"],
                    "moment_reset_attempted": moment_reset,
                    "backtracking_rows": selected["rows"],
                },
                "snapshot_manifest": snapshot_manifest,
                "persistent_checkpoints": checkpoints,
                "execution": {
                    "optimizer_updates": len(metrics),
                    "formal_support_cells": 0,
                    "locomotion_steps": 0,
                    "robot_or_rdk_access": 0,
                },
                "authority": preregistration["authority"],
            }
            args.output.write_text(
                json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            print(result["status"], flush=True)
            return 2

        accepted_index = int(selected["accepted_index"])
        accepted = selected["trials"][accepted_index]
        accepted_row = selected["rows"][accepted_index]
        loss_after, metrics_after = objective(accepted)
        parameters_after = v21.merge_joint_trainable(parameters, accepted)
        proposed_optimizer = selected["optimizer"]
        optimizer_after = {
            "count": jnp.asarray(proposed_optimizer["count"]),
            "m": {key: jnp.asarray(value) for key, value in optimizer["m"].items()},
            "v": {key: jnp.asarray(value) for key, value in optimizer["v"].items()},
        }
        for moment in ("m", "v"):
            optimizer_after[moment]["action_weight"] = set_target_slices(
                optimizer_after[moment]["action_weight"],
                proposed_optimizer[moment]["action_weight"],
                jnp,
            )
            optimizer_after[moment]["action_bias"] = set_target_slices(
                optimizer_after[moment]["action_bias"],
                proposed_optimizer[moment]["action_bias"],
                jnp,
            )
        predictor_before = v22.normalized_predictor_loss(
            before, batch, target_mean, target_std
        )[0]
        predictor_after = v22.normalized_predictor_loss(
            accepted, batch, target_mean, target_std
        )[0]
        local_unselected_exact = bool(
            v80.unselected_elements_exact(before, accepted)
            and v80.unselected_elements_exact(optimizer["m"], optimizer_after["m"])
            and v80.unselected_elements_exact(optimizer["v"], optimizer_after["v"])
        )
        selected_deltas = v80.selected_delta_metrics(before, accepted)
        update_valid = bool(
            float(loss_after) < float(loss_before)
            and all(
                row["loss"] >= float(loss_before)
                for row in selected["rows"][:accepted_index]
            )
            and np.array_equal(np.asarray(predictor_before), np.asarray(predictor_after))
            and local_unselected_exact
            and all(value > 0.0 for value in selected_deltas.values())
            and int(np.asarray(optimizer_after["count"])) == completed_count
            and boundary["realized_equals_numpy_bit_exact"]
            and boundary["numpy_equals_jax_bit_exact"]
            and training.finite_tree(
                {
                    "parameters": parameters_after,
                    "optimizer": optimizer_after,
                    "loss_before": loss_before,
                    "loss_after": loss_after,
                    "objective_metrics": objective_metrics,
                    "metrics_after": metrics_after,
                }
            )
        )
        if not update_valid:
            raise ValueError(f"Winner-v81 update {completed_count} invariant failed")
        snapshot_path = (
            args.work_root
            / "snapshots"
            / f"snapshot_pitch_action_head_update_{completed_count}.npz"
        )
        receipt = v22v2.save_snapshot(
            snapshot_path,
            parameters_after,
            optimizer_after,
            {
                "stage": "pitch_action_head_continuation_joint_stage2",
                "completed_updates": completed_count,
                "source_completed_updates": SOURCE_COUNT,
                "source_snapshot_sha256": proof["snapshot"]["sha256"],
                "teacher_snapshot_sha256": snapshot["metadata"][
                    "teacher_snapshot_sha256"
                ],
                "objective": preregistration["objective"],
                "root_seed": 120120,
                "learning_rate": float(training.STAGE2_LEARNING_RATE),
                "accepted_backtracking_fraction": accepted_row["fraction"],
                "moment_reset_applied": moment_reset,
                "formal_support_cells": 0,
                "locomotion_steps": 0,
                "robot_or_rdk_access": 0,
            },
            snapshot["target_mean"],
            snapshot["target_std"],
        )
        loaded = v22v2.load_snapshot(snapshot_path)
        readback_exact = bool(
            v63.tree_bit_exact(parameters_after, loaded["parameters"])
            and np.array_equal(optimizer_after["count"], loaded["optimizer"]["count"])
            and v63.tree_bit_exact(optimizer_after["m"], loaded["optimizer"]["m"])
            and v63.tree_bit_exact(optimizer_after["v"], loaded["optimizer"]["v"])
            and loaded["metadata"].get("completed_updates") == completed_count
        )
        if not readback_exact:
            raise ValueError(f"Winner-v81 snapshot {completed_count} readback changed")
        snapshot_manifest.append({"completed_updates": completed_count, **receipt})
        metric = {
            "completed_updates": completed_count,
            "rollout_update_index": rollout_update_index,
            "episode_receipts_sha256": episode_hash,
            "loss_before": float(loss_before),
            "loss_after": float(loss_after),
            "loss_delta": float(loss_after) - float(loss_before),
            "accepted_fraction": accepted_row["fraction"],
            "moment_reset_applied": moment_reset,
            "gradient_dot_proposed_delta": selected["dot"],
            "selected_teacher_elements": int(
                np.asarray(objective_metrics["selected_elements"])
            ),
            "predictor_loss_before": float(predictor_before),
            "predictor_loss_after": float(predictor_after),
            "selected_parameter_max_abs_delta": selected_deltas,
            "unselected_parameters_and_moments_bit_exact": local_unselected_exact,
            "snapshot_readback_exact": readback_exact,
            "action_boundary_exact": True,
        }
        metrics.append(metric)
        parameters = parameters_after
        optimizer = optimizer_after
        if completed_count in {HALF_COUNT, FINAL_COUNT}:
            label = "half" if completed_count == HALF_COUNT else "final"
            graph = v46.graph_receipt(
                smoke=smoke,
                networks=networks,
                training=training,
                parameters=parameters,
                observations=observations,
                path=args.work_root / "graphs" / f"winner_v81_{label}.onnx",
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
            f"loss={float(loss_before):.10f}->{float(loss_after):.10f} "
            f"reset={moment_reset}",
            flush=True,
        )

    final_trainable = v21.joint_trainable_parameters(parameters)
    source_trainable = v21.joint_trainable_parameters(source_parameters)
    source_unselected_exact = bool(
        v80.unselected_elements_exact(source_trainable, final_trainable)
        and v80.unselected_elements_exact(source_optimizer["m"], optimizer["m"])
        and v80.unselected_elements_exact(source_optimizer["v"], optimizer["v"])
    )
    checks = {
        "exact_99_updates_657_through_755": (
            len(metrics) == 99
            and [row["completed_updates"] for row in metrics]
            == list(range(657, 756))
        ),
        "every_update_strict_same_batch_descent": all(
            row["loss_after"] < row["loss_before"] for row in metrics
        ),
        "same_batch_predictor_loss_bit_exact_every_update": all(
            row["predictor_loss_after"] == row["predictor_loss_before"]
            for row in metrics
        ),
        "all_unselected_parameter_and_moment_elements_bit_exact": (
            source_unselected_exact
            and all(
                row["unselected_parameters_and_moments_bit_exact"] for row in metrics
            )
        ),
        "all_99_snapshots_digest_readback_exact": (
            len(snapshot_manifest) == 99
            and all(row["snapshot_readback_exact"] for row in metrics)
        ),
        "half_and_final_stateful_onnx_contracts_exact": (
            [(row["label"], row["completed_updates"]) for row in checkpoints]
            == [("half", HALF_COUNT), ("final", FINAL_COUNT)]
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
        "all_action_boundaries_exact": all(row["action_boundary_exact"] for row in metrics),
        "all_metrics_finite": all(
            math.isfinite(value)
            for row in metrics
            for key, value in row.items()
            if key in {
                "loss_before",
                "loss_after",
                "loss_delta",
                "gradient_dot_proposed_delta",
                "predictor_loss_before",
                "predictor_loss_after",
            }
        ),
        "no_posthoc_length_coefficient_or_checkpoint_change": True,
        "formal_support_selection_deployment_robot_zero": True,
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    if failed_checks:
        raise ValueError(f"Winner-v81 continuation invalid: {failed_checks}")
    result = {
        "schema_version": "winner_v81.pitch_action_head_continuation_result.v1",
        "status": "PASS_WINNER_V81_PITCH_ACTION_HEAD_CONTINUATION",
        "decision": "AUTHORIZE_UNCHANGED_PERSISTENCE_GATE_FOR_COUNTS_705_AND_755_ONLY",
        "source": proof["snapshot"],
        "metrics": metrics,
        "snapshot_manifest": snapshot_manifest,
        "persistent_checkpoints": checkpoints,
        "checks": {key: bool(value) for key, value in checks.items()},
        "failed_checks": [],
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
