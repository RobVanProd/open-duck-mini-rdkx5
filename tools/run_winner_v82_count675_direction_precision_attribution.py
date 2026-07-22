#!/usr/bin/env python3
"""Run the frozen zero-update Winner-v82 count-675 attribution."""

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

import build_winner_v82_count675_direction_precision_attribution_preregistration as builder  # noqa: E402
import run_winner_v81_pitch_action_head_continuation as v81  # noqa: E402


PREREGISTRATION = (
    ANALYSIS / "winner_v82_count675_direction_precision_attribution_preregistration.json"
)
V81_RESULT = ANALYSIS / "winner_v81_pitch_action_head_continuation_result.json"
FULL_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
DOMAIN = ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
PITCH_INDICES = v81.PITCH_INDICES


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    diagnostic = value.get("diagnostic", {})
    if (
        value.get("schema_version")
        != "winner_v82.count675_direction_precision_attribution_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V82_COUNT675_DIRECTION_PRECISION_ATTRIBUTION"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_COUNT675_DIRECTION_PRECISION_ATTRIBUTION_ONLY"
        or value.get("source", {}).get("optimizer_count") != builder.SOURCE_COUNT
        or value.get("source", {}).get("attempted_optimizer_count")
        != builder.ATTEMPT_COUNT
        or diagnostic.get("original_adam_fractions")
        != list(builder.ORIGINAL_FRACTIONS)
        or diagnostic.get("extended_adam_fractions")
        != list(builder.EXTENDED_ADAM_FRACTIONS)
        or diagnostic.get("negative_gradient_fractions")
        != list(builder.NEGATIVE_GRADIENT_FRACTIONS)
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v82 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v82 source manifest absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or builder.lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v82 source changed: {name}")
    if builder.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v82 source manifest changed")


def tree_l2(tree: Mapping[str, Any]) -> float:
    return float(
        np.sqrt(
            sum(
                np.sum(np.square(np.asarray(value, dtype=np.float64)))
                for value in tree.values()
            )
        )
    )


def selected_dot(left: Mapping[str, Any], right: Mapping[str, Any]) -> float:
    return v81.gradient_dot_delta(left, right)


def fraction_rows(
    *,
    before: Mapping[str, Any],
    delta: Mapping[str, Any],
    fractions: Sequence[float],
    loss_before: float,
    objective: Any,
    training: Any,
    jnp: Any,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fraction in fractions:
        trial = {
            key: jnp.asarray(before[key], dtype=jnp.float32)
            + jnp.asarray(fraction, dtype=jnp.float32)
            * jnp.asarray(delta[key], dtype=jnp.float32)
            for key in before
        }
        trial = training.clamp_stage2_parameters(trial)
        trial_loss, _ = objective(trial)
        changed = sum(
            int(
                np.count_nonzero(
                    np.asarray(trial[key]) != np.asarray(before[key])
                )
            )
            for key in before
        )
        max_delta = max(
            float(
                np.max(
                    np.abs(
                        np.asarray(trial[key], dtype=np.float64)
                        - np.asarray(before[key], dtype=np.float64)
                    )
                )
            )
            for key in before
        )
        loss = float(trial_loss)
        rows.append(
            {
                "fraction": float(fraction),
                "loss": loss,
                "loss_delta": loss - loss_before,
                "changed_parameter_elements": changed,
                "max_abs_parameter_delta": max_delta,
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-snapshot", type=Path, required=True)
    parser.add_argument("--playground-root", type=Path, required=True)
    parser.add_argument("--canonical-fit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline-cpu-only", action="store_true")
    parser.add_argument("--count675-attribution-authorized", action="store_true")
    args = parser.parse_args()
    if not args.offline_cpu_only or not args.count675_attribution_authorized:
        raise PermissionError(
            "Winner-v82 requires --offline-cpu-only --count675-attribution-authorized"
        )
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v82 evidence")

    import jax
    import jax.numpy as jnp
    import mujoco
    import run_winner_v12_full_calibrator_training as full
    import winner_v12_calibrator_training as training
    import winner_v20_joint_recurrent_support as v20
    import winner_v21_predictor_preserving_joint_support as v21
    import winner_v22_normalized_predictor_v2 as v22v2
    import winner_v29_prefix_right_pitch_anchor as v29

    if jax.default_backend() != "cpu" or any(
        device.platform != "cpu" for device in jax.devices()
    ):
        raise ValueError("Winner-v82 requires CPU-only JAX")
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    stopped = json.loads(V81_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V81_RESULT) != builder.V81_RESULT_SHA256
        or stopped.get("status")
        != "HOLD_WINNER_V81_PITCH_ACTION_HEAD_CONTINUATION"
        or stopped.get("decision") != "DO_NOT_RUN_PERSISTENCE_GATE"
    ):
        raise ValueError("Winner-v82 source stop changed")
    source_receipt = preregistration["source"]["snapshot"]
    v80 = v81.v80_module()
    v80.validate_artifact(args.source_snapshot, source_receipt, "source snapshot")
    snapshot = v22v2.load_snapshot(args.source_snapshot)
    if (
        int(np.asarray(snapshot["optimizer"]["count"])) != builder.SOURCE_COUNT
        or snapshot["metadata"].get("completed_updates") != builder.SOURCE_COUNT
        or snapshot["metadata"].get("stage")
        != "pitch_action_head_continuation_joint_stage2"
        or snapshot["metadata"].get("source_completed_updates") != 656
        or snapshot["metadata"].get("formal_support_cells") != 0
        or snapshot["metadata"].get("locomotion_steps") != 0
        or snapshot["metadata"].get("robot_or_rdk_access") != 0
    ):
        raise ValueError("Winner-v82 source snapshot boundary changed")

    smoke, gate, _ = v80.configured_stack()
    if smoke.git_output(args.playground_root, "rev-parse", "HEAD") != smoke.CONTROL_COMMIT:
        raise ValueError("Winner-v82 Playground commit changed")
    smoke.validate_playground_tree(args.playground_root)
    if smoke.sha256(args.canonical_fit) != smoke.P30_FIT_LF_SHA256:
        raise ValueError("Winner-v82 canonical fit changed")
    scene = args.playground_root / smoke.SCENE_RELATIVE
    observer_type = smoke.load_runtime_observer(args.canonical_fit)
    full_design = json.loads(FULL_PREREGISTRATION.read_text(encoding="utf-8"))
    calibrator_design = gate.load_calibrator_design(full_design)
    domain = json.loads(DOMAIN.read_text(encoding="utf-8"))
    population = full.training_population(full_design, domain)
    identifiers = [str(row["id"]) for row in population]
    heldout_ids = ("HELDOUT_04", "HELDOUT_07", "HELDOUT_09", "HELDOUT_15")
    if len(population) != 80 or any(
        identifiers.count(name) != 2 for name in v80.TRAINING_TEACHER_IDS
    ) or any(name in identifiers for name in heldout_ids):
        raise ValueError("Winner-v82 population changed")
    table = v80.complete_teacher_table()
    parameters = snapshot["parameters"]
    optimizer = snapshot["optimizer"]
    before = v21.joint_trainable_parameters(parameters)
    batch_np, episodes, _ = v20.stage2_rollout(
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
        update_index=builder.SOURCE_COUNT,
    )
    full.validate_stage2_masks(batch_np, episodes)
    episode_hash = full.validate_episode_receipts(
        episodes, population, stage=2, update_index=builder.SOURCE_COUNT
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

    (loss_value, _), raw_gradient = jax.value_and_grad(objective, has_aux=True)(before)
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
    work_optimizer = {"count": jnp.asarray(optimizer["count"]), "m": work_m, "v": work_v}
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
    adam_delta = {
        key: jnp.asarray(proposed[key], dtype=jnp.float32)
        - jnp.asarray(before[key], dtype=jnp.float32)
        for key in before
    }
    gradient_l2 = tree_l2(gradient)
    adam_delta_l2 = tree_l2(adam_delta)
    if gradient_l2 <= 0.0 or adam_delta_l2 <= 0.0:
        raise ValueError("Winner-v82 zero diagnostic direction")
    negative_gradient_delta = {
        key: -jnp.asarray(value, dtype=jnp.float32)
        * jnp.asarray(adam_delta_l2 / gradient_l2, dtype=jnp.float32)
        for key, value in gradient.items()
    }
    adam_rows = fraction_rows(
        before=before,
        delta=adam_delta,
        fractions=builder.EXTENDED_ADAM_FRACTIONS,
        loss_before=loss_before,
        objective=objective,
        training=training,
        jnp=jnp,
    )
    negative_rows = fraction_rows(
        before=before,
        delta=negative_gradient_delta,
        fractions=builder.NEGATIVE_GRADIENT_FRACTIONS,
        loss_before=loss_before,
        objective=objective,
        training=training,
        jnp=jnp,
    )
    gradient_dot_delta = selected_dot(gradient, adam_delta)
    classification, decision = builder.classify_count675(
        loss_before=loss_before,
        adam_gradient_dot_delta=gradient_dot_delta,
        adam_losses=[row["loss"] for row in adam_rows],
        negative_gradient_losses=[row["loss"] for row in negative_rows],
        adam_parameter_changes=[row["changed_parameter_elements"] for row in adam_rows],
        negative_gradient_parameter_changes=[
            row["changed_parameter_elements"] for row in negative_rows
        ],
    )
    stop = stopped["stop"]
    checks = {
        "source_count674_rollout674_attempt675_exact": (
            int(np.asarray(optimizer["count"])) == 674
            and int(np.asarray(proposed_optimizer["count"])) == 675
        ),
        "original_grid_exhaustion_bit_exact_reproduced": (
            loss_before == stop["loss_before"]
            and [
                {"fraction": row["fraction"], "loss": row["loss"], "loss_delta": row["loss_delta"]}
                for row in adam_rows[: len(builder.ORIGINAL_FRACTIONS)]
            ]
            == stop["backtracking_rows"]
            and gradient_dot_delta == stop["gradient_dot_proposed_delta"]
        ),
        "fraction_grids_exact": (
            [row["fraction"] for row in adam_rows]
            == list(builder.EXTENDED_ADAM_FRACTIONS)
            and [row["fraction"] for row in negative_rows]
            == list(builder.NEGATIVE_GRADIENT_FRACTIONS)
        ),
        "action_boundary_exact": (
            boundary["realized_equals_numpy_bit_exact"]
            and boundary["numpy_equals_jax_bit_exact"]
        ),
        "all_values_finite": training.finite_tree(
            {
                "loss": loss_value,
                "gradient": gradient,
                "adam_delta": adam_delta,
                "negative_gradient_delta": negative_gradient_delta,
                "adam_rows": adam_rows,
                "negative_rows": negative_rows,
                "gradient_dot_delta": gradient_dot_delta,
            }
        ),
        "zero_committed_updates_snapshots_graphs_support_robot": True,
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    if failed_checks:
        raise ValueError(f"Winner-v82 attribution invalid: {failed_checks}")
    loss_ulp = float(np.spacing(np.float32(loss_before)))
    result = {
        "schema_version": "winner_v82.count675_direction_precision_attribution_result.v1",
        "status": "PASS_WINNER_V82_COUNT675_DIRECTION_PRECISION_ATTRIBUTION",
        "classification": classification,
        "decision": decision,
        "source": {
            "snapshot": source_receipt,
            "optimizer_count": 674,
            "rollout_update_index": 674,
            "attempted_optimizer_count": int(np.asarray(proposed_optimizer["count"])),
            "episode_receipts_sha256": episode_hash,
        },
        "loss_geometry": {
            "teacher_loss_before": loss_before,
            "teacher_loss_float32_ulp": loss_ulp,
            "teacher_gradient_dot_adam_delta": gradient_dot_delta,
            "adam_delta_l2": adam_delta_l2,
            "scaled_teacher_gradient_l2": gradient_l2,
            "adam_fraction_rows": adam_rows,
            "negative_gradient_norm_matched_fraction_rows": negative_rows,
        },
        "checks": {key: bool(value) for key, value in checks.items()},
        "failed_checks": [],
        "execution": {
            "rollout_episode_slots": 80,
            "scheduled_rollout_ticks": 20000,
            "counterfactual_optimizer_proposals": 2,
            "committed_optimizer_updates": 0,
            "snapshots_written": 0,
            "onnx_graphs_written": 0,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
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
    print(result["status"])
    print(f"classification={classification}")
    print(f"decision={decision}")
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
