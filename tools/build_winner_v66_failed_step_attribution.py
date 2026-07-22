#!/usr/bin/env python3
"""Preregister the zero-update Winner-v66 failed-step attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v66_failed_step_attribution_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V66_FAILED_STEP_ATTRIBUTION_PREREGISTRATION_20260722.md"
V65B_RESULT = ANALYSIS / "winner_v65b_isolated_persistent_teacher_training_result.json"
V65B_CONTRACT = ANALYSIS / "winner_v65b_isolated_persistent_teacher_training_preregistration.json"
V65B_RESULT_SHA256 = "2c3a8798b8de5b95ea7adbb9eeac5bc7c83539a452ca7ef69e98232df9135c74"
SOURCE_COUNT = 574
ATTEMPT_COUNT = 575
ROLLOUT_UPDATE_INDEX = 574
FRACTIONS = (0.0625, 0.125, 0.25, 0.5, 0.75, 1.0)

sys.path.insert(0, str(ROOT / "tools"))
import build_winner_v65b_preregistration_path_correction as v65b  # noqa: E402


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


def replace_exact(source: str, old: str, new: str, *, count: int = 1) -> str:
    actual = source.count(old)
    if actual != count:
        raise ValueError(
            f"Winner-v66 transform changed: expected {count}, found {actual}: {old!r}"
        )
    return source.replace(old, new)


def replace_region(source: str, start: str, end: str, replacement: str) -> str:
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"Winner-v66 region markers changed: {start!r} / {end!r}")
    left = source.index(start)
    right = source.index(end, left)
    return source[:left] + replacement + source[right:]


def classify_failed_step(
    *,
    loss_before: float,
    inherited_full_loss: float,
    inherited_gradient_dot_delta: float,
    inherited_fraction_losses: Sequence[float],
    negative_gradient_fraction_losses: Sequence[float],
) -> tuple[str, str]:
    if inherited_full_loss < loss_before:
        return "FAILED_STEP_DID_NOT_REPRODUCE", "STOP_REPRODUCTION_MISMATCH"
    inherited_partial_descent = any(
        loss < loss_before
        for fraction, loss in zip(FRACTIONS, inherited_fraction_losses, strict=True)
        if fraction < 1.0
    )
    gradient_descent = any(loss < loss_before for loss in negative_gradient_fraction_losses)
    if inherited_gradient_dot_delta >= 0.0 and gradient_descent:
        return (
            "INHERITED_ADAM_MOMENT_DIRECTION_OPPOSES_TEACHER",
            "PREREGISTER_ONE_FRESH_MOMENT_TEACHER_STEP_PROOF",
        )
    if inherited_gradient_dot_delta < 0.0 and inherited_partial_descent:
        return (
            "INHERITED_ADAM_FULL_STEP_OVERSHOOT",
            "PREREGISTER_ONE_DETERMINISTIC_BACKTRACKED_ADAM_STEP_PROOF",
        )
    if gradient_descent:
        return (
            "INHERITED_ADAM_DIRECTION_OR_CURVATURE_FAILURE",
            "PREREGISTER_ONE_NEGATIVE_GRADIENT_STEP_PROOF",
        )
    if all(loss == loss_before for loss in negative_gradient_fraction_losses):
        return "FLOAT32_TEACHER_PLATEAU", "STOP_ISOLATED_TEACHER_ROUTE"
    return "UNRESOLVED_FAILED_STEP_GEOMETRY", "STOP_FOR_REVIEW"


VALIDATE_PREREGISTRATION = '''def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v66.failed_step_attribution_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V66_FAILED_STEP_ATTRIBUTION"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_COUNT_575_ATTRIBUTION_ONLY"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or value.get("diagnostic", {}).get("source_optimizer_count")
        != SOURCE_COMPLETED_UPDATES
        or value.get("diagnostic", {}).get("rollout_update_index")
        != SOURCE_COMPLETED_UPDATES
        or value.get("diagnostic", {}).get("attempted_optimizer_count") != 575
        or value.get("diagnostic", {}).get("fractions")
        != [0.0625, 0.125, 0.25, 0.5, 0.75, 1.0]
    ):
        raise ValueError("Winner-v66 preregistration changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v66 source manifest absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v66 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v66 source manifest changed")


'''

VALIDATE_SOURCE = '''def validate_source_snapshot(
    snapshot: Mapping[str, Any], v21: Any, source_result: Mapping[str, Any]
) -> None:
    if set(snapshot) != {"parameters", "optimizer", "metadata", "target_mean", "target_std"}:
        raise ValueError("Winner-v66 source snapshot state schema changed")
    metadata = snapshot["metadata"]
    final_receipt = source_result["artifacts"]["snapshots"][-1]
    if (
        metadata.get("schema_version") != "winner_v21.predictor_preserving_snapshot.v1"
        or metadata.get("stage") != "isolated_persistent_teacher_joint_stage2"
        or metadata.get("completed_updates") != SOURCE_COMPLETED_UPDATES
        or metadata.get("source_completed_updates") != 555
        or metadata.get("root_seed") != 120120
        or metadata.get("learning_rate") != 0.0001
        or metadata.get("formal_support_cells") != 0
        or metadata.get("locomotion_steps") != 0
        or metadata.get("robot_or_rdk_access") != 0
        or metadata.get("objective", {}).get("update_gradient")
        != "full_action_persistent_teacher_only"
        or metadata.get("objective", {}).get("attention_or_flat_transport_added") is not False
        or int(np.asarray(snapshot["optimizer"]["count"])) != SOURCE_COMPLETED_UPDATES
        or final_receipt.get("completed_updates") != SOURCE_COMPLETED_UPDATES
        or set(snapshot["optimizer"]["m"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(snapshot["optimizer"]["v"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(v21.joint_trainable_parameters(snapshot["parameters"]))
        != set(v21.JOINT_TRAINABLE_KEYS)
    ):
        raise ValueError("Winner-v66 source snapshot metadata changed")
    for name in ("target_mean", "target_std"):
        array = np.asarray(snapshot[name])
        if array.shape != (50,) or array.dtype != np.dtype(np.float32) or not np.all(np.isfinite(array)):
            raise ValueError(f"Winner-v66 source {name} schema changed")
    if np.any(np.asarray(snapshot["target_std"]) <= 0.0):
        raise ValueError("Winner-v66 source target_std is not positive")
    for tree in (snapshot["parameters"], snapshot["optimizer"]["m"], snapshot["optimizer"]["v"]):
        if not all(np.all(np.isfinite(np.asarray(item))) for item in tree.values()):
            raise ValueError("Winner-v66 source snapshot contains nonfinite arrays")


'''

SOURCE_EVIDENCE = '''    source_result = json.loads(V45_RESULT.read_text(encoding="utf-8"))
    teacher_result = json.loads(V22_RESULT.read_text(encoding="utf-8"))
    if (
        source_result.get("status")
        != "STOPPED_WINNER_V65B_STRICT_DESCENT_AT_575"
        or source_result.get("decision")
        != "PREREGISTER_WINNER_V66_FAILED_STEP_ATTRIBUTION_ONLY"
        or source_result.get("failed_checks") != []
        or source_result.get("execution", {}).get("last_durable_optimizer_count")
        != SOURCE_COMPLETED_UPDATES
        or source_result.get("execution", {}).get("failed_attempt_optimizer_count") != 575
        or source_result.get("execution", {}).get("successful_optimizer_updates") != 19
        or teacher_result.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or teacher_result.get("failed_checks") != []
    ):
        raise ValueError("Winner-v66 source evidence changed")
'''

DIAGNOSTIC = '''        raw_after, proposed_optimizer = training.adam_step(
            before, gradients, optimizer, learning_rate=training.STAGE2_LEARNING_RATE,
            beta1=training.ADAM_BETA1, beta2=training.ADAM_BETA2,
            epsilon=training.ADAM_EPSILON,
        )
        after = training.clamp_stage2_parameters(raw_after)
        full.validate_log_std(after)
        teacher_loss_after, teacher_metrics_after = static_teacher_objective(after)

        def tree_dot(left, right):
            return float(sum(
                np.sum(
                    np.asarray(left[key], dtype=np.float64)
                    * np.asarray(right[key], dtype=np.float64)
                )
                for key in sorted(left)
            ))

        def tree_l2(tree):
            return float(np.sqrt(sum(
                np.sum(np.square(np.asarray(value, dtype=np.float64)))
                for value in tree.values()
            )))

        adam_delta = jax.tree_util.tree_map(
            lambda old, new: jnp.asarray(new, dtype=jnp.float32)
            - jnp.asarray(old, dtype=jnp.float32),
            before,
            after,
        )
        raw_adam_delta = jax.tree_util.tree_map(
            lambda old, new: jnp.asarray(new, dtype=jnp.float32)
            - jnp.asarray(old, dtype=jnp.float32),
            before,
            raw_after,
        )
        scaled_gradient_l2 = tree_l2(gradients)
        adam_delta_l2 = tree_l2(adam_delta)
        if scaled_gradient_l2 <= 0.0 or adam_delta_l2 <= 0.0:
            raise ValueError("Winner-v66 zero failed-step direction")
        negative_gradient_delta = jax.tree_util.tree_map(
            lambda value: -jnp.asarray(value, dtype=jnp.float32)
            * jnp.asarray(adam_delta_l2 / scaled_gradient_l2, dtype=jnp.float32),
            gradients,
        )

        def fraction_rows(delta):
            rows = []
            for fraction in preregistration["diagnostic"]["fractions"]:
                trial = jax.tree_util.tree_map(
                    lambda old, change: jnp.asarray(old, dtype=jnp.float32)
                    + jnp.asarray(fraction, dtype=jnp.float32)
                    * jnp.asarray(change, dtype=jnp.float32),
                    before,
                    delta,
                )
                trial = training.clamp_stage2_parameters(trial)
                full.validate_log_std(trial)
                trial_loss, trial_metrics = static_teacher_objective(trial)
                rows.append({
                    "fraction": float(fraction),
                    "loss": float(trial_loss),
                    "loss_delta": float(trial_loss) - float(teacher_loss),
                    "maximum_selected_action_delta": float(
                        trial_metrics["maximum_selected_action_delta"]
                    ),
                })
            return rows

        inherited_rows = fraction_rows(adam_delta)
        negative_gradient_rows = fraction_rows(negative_gradient_delta)
        classification, decision = v66_builder.classify_failed_step(
            loss_before=float(teacher_loss),
            inherited_full_loss=float(teacher_loss_after),
            inherited_gradient_dot_delta=tree_dot(teacher_gradients, adam_delta),
            inherited_fraction_losses=[row["loss"] for row in inherited_rows],
            negative_gradient_fraction_losses=[row["loss"] for row in negative_gradient_rows],
        )
        checks = {
            "source_count_574_and_rollout_index_574_exact": rollout_update_index == 574
            and int(np.asarray(optimizer["count"])) == 574,
            "failed_full_inherited_adam_step_reproduced": float(teacher_loss_after)
            >= float(teacher_loss),
            "proposed_optimizer_count_575_exact": int(np.asarray(proposed_optimizer["count"])) == 575,
            "fraction_grid_exact": [row["fraction"] for row in inherited_rows]
            == [0.0625, 0.125, 0.25, 0.5, 0.75, 1.0]
            and [row["fraction"] for row in negative_gradient_rows]
            == [0.0625, 0.125, 0.25, 0.5, 0.75, 1.0],
            "all_losses_directions_and_metrics_finite": training.finite_tree({
                "teacher_loss": teacher_loss,
                "teacher_loss_after": teacher_loss_after,
                "teacher_metrics": teacher_metrics,
                "teacher_metrics_after": teacher_metrics_after,
                "teacher_gradients": teacher_gradients,
                "scaled_gradients": gradients,
                "raw_after": raw_after,
                "after": after,
                "proposed_optimizer": proposed_optimizer,
                "inherited_rows": inherited_rows,
                "negative_gradient_rows": negative_gradient_rows,
            }),
            "no_update_snapshot_graph_support_or_robot_commit": not any(
                (args.work_root / "snapshots").iterdir()
            ) and not any((args.work_root / "graphs").iterdir()),
        }
        failed_checks = sorted(name for name, passed in checks.items() if not passed)
        if failed_checks:
            raise ValueError(f"Winner-v66 attribution invalid: {failed_checks}")
        result = {
            "schema_version": "winner_v66.failed_step_attribution_result.v1",
            "status": "PASS_WINNER_V66_FAILED_STEP_ATTRIBUTION",
            "classification": classification,
            "decision": decision,
            "source": {
                "snapshot": source_receipt,
                "optimizer_count": int(np.asarray(optimizer["count"])),
                "rollout_update_index": rollout_update_index,
                "attempted_optimizer_count": int(np.asarray(proposed_optimizer["count"])),
                "episode_receipts_sha256": episode_hash,
            },
            "loss_geometry": {
                "teacher_loss_before": float(teacher_loss),
                "inherited_adam_full_loss": float(teacher_loss_after),
                "inherited_adam_full_loss_delta": float(teacher_loss_after)
                - float(teacher_loss),
                "teacher_gradient_dot_inherited_adam_delta": tree_dot(
                    teacher_gradients, adam_delta
                ),
                "scaled_teacher_gradient_dot_inherited_adam_delta": tree_dot(
                    gradients, adam_delta
                ),
                "adam_delta_l2": adam_delta_l2,
                "raw_adam_delta_l2": tree_l2(raw_adam_delta),
                "scaled_teacher_gradient_l2": scaled_gradient_l2,
                "clamp_delta_l2": tree_l2(jax.tree_util.tree_map(
                    lambda raw, clamped: jnp.asarray(clamped, dtype=jnp.float32)
                    - jnp.asarray(raw, dtype=jnp.float32),
                    raw_after,
                    after,
                )),
                "per_leaf_teacher_gradient_dot_inherited_adam_delta": {
                    key: tree_dot(
                        {key: teacher_gradients[key]}, {key: adam_delta[key]}
                    )
                    for key in sorted(teacher_gradients)
                },
                "inherited_adam_fraction_rows": inherited_rows,
                "negative_gradient_norm_matched_fraction_rows": negative_gradient_rows,
            },
            "checks": {key: bool(value) for key, value in checks.items()},
            "failed_checks": [],
            "execution": {
                "rollout_episode_slots": 80,
                "scheduled_rollout_ticks": 20000,
                "counterfactual_optimizer_proposals": 1,
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
            json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\\n",
            encoding="utf-8",
        )
        print(result["status"])
        print(f"classification={classification}")
        print(f"decision={decision}")
        print(f"sha256={sha256(args.output)}")
        return 0'''


def transformed_source() -> tuple[str, str]:
    source, _ = v65b.corrected_source()
    source = replace_exact(source, "Winner-v65", "Winner-v66", count=30)
    source = replace_exact(source, "winner_v65", "winner_v66", count=4)
    source = replace_exact(source, "WINNER_V65", "WINNER_V66", count=4)
    source = replace_exact(
        source,
        'import winner_v56_first_tick_teacher_mapping as v56  # noqa: E402',
        '''import winner_v56_first_tick_teacher_mapping as v56  # noqa: E402
import build_winner_v66_failed_step_attribution as v66_builder  # noqa: E402''',
    )
    source = replace_exact(
        source,
        'PREREGISTRATION = ANALYSIS / "winner_v66b_isolated_persistent_teacher_training_preregistration.json"',
        'PREREGISTRATION = ANALYSIS / "winner_v66_failed_step_attribution_preregistration.json"',
    )
    source = replace_exact(
        source,
        'V45_RESULT = ANALYSIS / "winner_v64b_isolated_persistent_teacher_step_result.json"',
        'V45_RESULT = ANALYSIS / "winner_v65b_isolated_persistent_teacher_training_result.json"',
    )
    source = replace_exact(source, "UPDATES = 100", "UPDATES = 1")
    source = replace_exact(
        source, "SOURCE_COMPLETED_UPDATES = 555", "SOURCE_COMPLETED_UPDATES = 574"
    )
    source = replace_region(
        source, "def validate_preregistration", "def validate_artifact", VALIDATE_PREREGISTRATION
    )
    source = replace_region(
        source, "def validate_source_snapshot", "def graph_receipt", VALIDATE_SOURCE
    )
    source = replace_exact(
        source,
        '    parser.add_argument("--source-graph", type=Path, required=True)\n',
        "",
    )
    source = replace_exact(
        source,
        '    parser.add_argument("--isolated-persistent-teacher-training-authorized", action="store_true")',
        '    parser.add_argument("--failed-step-attribution-authorized", action="store_true")',
    )
    source = replace_exact(
        source,
        "if not args.offline_cpu_only or not args.isolated_persistent_teacher_training_authorized:",
        "if not args.offline_cpu_only or not args.failed_step_attribution_authorized:",
    )
    source = replace_exact(
        source,
        '"Winner-v66 requires --offline-cpu-only --isolated-persistent-teacher-training-authorized"',
        '"Winner-v66 requires --offline-cpu-only --failed-step-attribution-authorized"',
    )
    source = replace_region(
        source,
        '    source_result = json.loads(V45_RESULT.read_text(encoding="utf-8"))',
        '    source_receipt = preregistration["source_checkpoint"]["snapshot"]',
        SOURCE_EVIDENCE,
    )
    source = replace_exact(
        source,
        '    source_graph_receipt = preregistration["source_checkpoint"]["graph"]\n',
        "",
    )
    source = replace_exact(
        source, '    validate_artifact(args.source_graph, source_graph_receipt, "source graph")\n', ""
    )
    source = replace_exact(
        source,
        '''        after, optimizer = training.adam_step(
            before, gradients, optimizer, learning_rate=training.STAGE2_LEARNING_RATE,
            beta1=training.ADAM_BETA1, beta2=training.ADAM_BETA2,
            epsilon=training.ADAM_EPSILON,
        )
        after = training.clamp_stage2_parameters(after)
        full.validate_log_std(after)
        teacher_loss_after, teacher_metrics_after = static_teacher_objective(after)
        if not float(teacher_loss_after) < float(teacher_loss):
            raise ValueError(
                f"Winner-v66 same-batch teacher loss did not decrease at {completed_updates}"
            )''',
        DIAGNOSTIC,
    )
    transformed_hash = hashlib.sha256(source.encode()).hexdigest()
    compile(source, "winner_v66_failed_step_attribution_transformed.py", "exec")
    return source, transformed_hash


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v66 contract: {path}")
    stopped = json.loads(V65B_RESULT.read_text(encoding="utf-8"))
    v65_contract = json.loads(V65B_CONTRACT.read_text(encoding="utf-8"))
    source, transformed_hash = transformed_source()
    final_snapshot = stopped.get("artifacts", {}).get("snapshots", [])[-1]
    if (
        sha256(V65B_RESULT) != V65B_RESULT_SHA256
        or stopped.get("status") != "STOPPED_WINNER_V65B_STRICT_DESCENT_AT_575"
        or stopped.get("decision")
        != "PREREGISTER_WINNER_V66_FAILED_STEP_ATTRIBUTION_ONLY"
        or stopped.get("execution", {}).get("last_durable_optimizer_count")
        != SOURCE_COUNT
        or stopped.get("execution", {}).get("failed_attempt_optimizer_count")
        != ATTEMPT_COUNT
        or final_snapshot.get("completed_updates") != SOURCE_COUNT
        or final_snapshot.get("sha256")
        != "e255988ee27bbb3fb6b7842c01da69a68941e3127eb7ed0c7d707236da33ebce"
        or len(FRACTIONS) != 6
        or source.count("v66_builder.classify_failed_step") != 1
    ):
        raise ValueError("Winner-v66 selection evidence changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in {
            "builder": Path("tools/build_winner_v66_failed_step_attribution.py"),
            "runner": Path("tools/run_winner_v66_failed_step_attribution.py"),
            "tests": Path("tests/test_winner_v66_failed_step_attribution.py"),
            "v65b_stopped_result": Path(
                "outputs/analysis/winner_v65b_isolated_persistent_teacher_training_result.json"
            ),
            "v65b_contract": Path(
                "outputs/analysis/winner_v65b_isolated_persistent_teacher_training_preregistration.json"
            ),
            "v65b_builder": Path(
                "tools/build_winner_v65b_preregistration_path_correction.py"
            ),
            "v65_builder": Path(
                "tools/build_winner_v65_isolated_persistent_teacher_training.py"
            ),
        }.items()
    }
    value = {
        "schema_version": "winner_v66.failed_step_attribution_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V66_FAILED_STEP_ATTRIBUTION",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_COUNT_575_ATTRIBUTION_ONLY",
        "source_checkpoint": {
            "completed_updates": SOURCE_COUNT,
            "optimizer_count": SOURCE_COUNT,
            "snapshot": final_snapshot,
        },
        "teacher_checkpoint": v65_contract["teacher_checkpoint"],
        "diagnostic": {
            "source_optimizer_count": SOURCE_COUNT,
            "rollout_update_index": ROLLOUT_UPDATE_INDEX,
            "attempted_optimizer_count": ATTEMPT_COUNT,
            "environments": 80,
            "ticks_per_environment": 250,
            "fractions": list(FRACTIONS),
            "directions": {
                "inherited_adam": (
                    "exact inherited moments/count and frozen learning rate; parameter "
                    "delta evaluated after the inherited clamp"
                ),
                "negative_gradient_norm_matched": (
                    "instantaneous negative scaled teacher gradient normalized to the "
                    "clamped inherited-Adam delta L2 norm"
                ),
            },
            "classification_order": [
                "FAILED_STEP_DID_NOT_REPRODUCE",
                "INHERITED_ADAM_MOMENT_DIRECTION_OPPOSES_TEACHER",
                "INHERITED_ADAM_FULL_STEP_OVERSHOOT",
                "INHERITED_ADAM_DIRECTION_OR_CURVATURE_FAILURE",
                "FLOAT32_TEACHER_PLATEAU",
                "UNRESOLVED_FAILED_STEP_GEOMETRY",
            ],
            "coefficient_or_checkpoint_selection": False,
        },
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "stop_rules": [
            "stop if the immutable count-574 snapshot or stopped result differs",
            "stop if update-index 574 rollout receipts or transition contracts differ",
            "stop unless the inherited full step reproduces non-descent",
            "do not persist either counterfactual parameter or optimizer proposal",
            "do not evaluate support behavior or select a checkpoint",
        ],
        "authority": {
            "pass_authorizes_only": (
                "the single one-step proof named by the preregistered classification"
            ),
            "attention_or_flat_transport_selected": False,
            "support_gate_authorized": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
        "transformation": {
            "base": "Winner-v65b corrected isolated-teacher runner",
            "transformed_source_sha256": transformed_hash,
            "zero_update_early_return": True,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v66 failed-step attribution preregistration",
                "",
                "- Source / attempted optimizer counts: `574 / 575`",
                "- Rollout: update index `574`, `80 x 250`, CPU only",
                "- Fixed fractions: `1/16, 1/8, 1/4, 1/2, 3/4, 1`",
                "- Directions: inherited Adam delta and norm-matched negative teacher gradient",
                "- Committed updates / snapshots / ONNX / support / robot: `0 / 0 / 0 / 0 / 0`",
                "- Attention or flat-transport equation selected: `false`",
                f"- Transformed source SHA-256: `{transformed_hash}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
