#!/usr/bin/env python3
"""Preregister the zero-update Winner-v69 count-602 attribution."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v69_count602_direction_attribution_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V69_COUNT602_DIRECTION_ATTRIBUTION_PREREGISTRATION_20260722.md"
V68_RESULT = ANALYSIS / "winner_v68_backtracked_adam_continuation_result.json"
V68_CONTRACT = ANALYSIS / "winner_v68_backtracked_adam_continuation_preregistration.json"
V68_RESULT_SHA256 = "87c90a0b7dcaadf1abe6675e6cb293b0de1656e3a07ab085e3d4bbeee1b6ccb1"
SOURCE_COUNT = 601
ATTEMPT_COUNT = 602
ADAM_FRACTIONS = (
    1.0,
    0.5,
    0.25,
    0.125,
    0.0625,
    0.03125,
    0.015625,
    0.0078125,
    0.00390625,
    0.001953125,
    0.0009765625,
)
NEGATIVE_GRADIENT_FRACTIONS = (1.0, 0.5, 0.25, 0.125, 0.0625)

sys.path.insert(0, str(ROOT / "tools"))
import build_winner_v66_failed_step_attribution as v66  # noqa: E402


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
            f"Winner-v69 transform changed: expected {count}, found {actual}: {old!r}"
        )
    return source.replace(old, new)


def replace_region(source: str, start: str, end: str, replacement: str) -> str:
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"Winner-v69 region markers changed: {start!r} / {end!r}")
    left = source.index(start)
    right = source.index(end, left)
    return source[:left] + replacement + source[right:]


def classify_count602(
    *,
    loss_before: float,
    adam_gradient_dot_delta: float,
    adam_losses: Sequence[float],
    negative_gradient_losses: Sequence[float],
) -> tuple[str, str]:
    original_descends = any(loss < loss_before for loss in adam_losses[:5])
    extended_descends = any(loss < loss_before for loss in adam_losses[5:])
    negative_descends = any(loss < loss_before for loss in negative_gradient_losses)
    if original_descends:
        return "ORIGINAL_GRID_EXHAUSTION_DID_NOT_REPRODUCE", "STOP_REPRODUCTION_MISMATCH"
    if adam_gradient_dot_delta >= 0.0 and negative_descends:
        return (
            "INHERITED_ADAM_MOMENT_DIRECTION_OPPOSES_TEACHER",
            "PREREGISTER_ONE_FRESH_MOMENT_TEACHER_STEP_PROOF",
        )
    if adam_gradient_dot_delta < 0.0 and extended_descends:
        return (
            "ADAM_DESCENT_EXISTS_BELOW_FROZEN_GRID",
            "PREREGISTER_ONE_EXTENDED_BACKTRACKED_ADAM_STEP_PROOF",
        )
    if negative_descends:
        return (
            "ADAM_DIRECTION_STALLED_NEGATIVE_GRADIENT_DESCENDS",
            "PREREGISTER_ONE_NEGATIVE_GRADIENT_STEP_PROOF",
        )
    if all(loss == loss_before for loss in negative_gradient_losses):
        return "FLOAT32_TEACHER_PLATEAU", "STOP_ISOLATED_TEACHER_ROUTE"
    return "UNRESOLVED_COUNT602_GEOMETRY", "STOP_FOR_REVIEW"


VALIDATE_PREREGISTRATION = '''def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v69.count602_direction_attribution_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V69_COUNT602_DIRECTION_ATTRIBUTION"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_COUNT602_ATTRIBUTION_ONLY"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or value.get("diagnostic", {}).get("source_optimizer_count")
        != SOURCE_COMPLETED_UPDATES
        or value.get("diagnostic", {}).get("attempted_optimizer_count") != 602
        or value.get("diagnostic", {}).get("adam_fractions")
        != [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625, 0.0078125, 0.00390625, 0.001953125, 0.0009765625]
        or value.get("diagnostic", {}).get("negative_gradient_fractions")
        != [1.0, 0.5, 0.25, 0.125, 0.0625]
    ):
        raise ValueError("Winner-v69 preregistration changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v69 source manifest absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v69 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v69 source manifest changed")


'''

VALIDATE_SOURCE = '''def validate_source_snapshot(
    snapshot: Mapping[str, Any], v21: Any, source_result: Mapping[str, Any]
) -> None:
    if set(snapshot) != {"parameters", "optimizer", "metadata", "target_mean", "target_std"}:
        raise ValueError("Winner-v69 source snapshot state schema changed")
    metadata = snapshot["metadata"]
    final_receipt = source_result["artifacts"]["snapshots"][-1]
    if (
        metadata.get("schema_version") != "winner_v21.predictor_preserving_snapshot.v1"
        or metadata.get("stage") != "backtracked_persistent_teacher_joint_stage2"
        or metadata.get("completed_updates") != SOURCE_COMPLETED_UPDATES
        or metadata.get("source_completed_updates") != 575
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
    ):
        raise ValueError("Winner-v69 source snapshot metadata changed")
    for name in ("target_mean", "target_std"):
        array = np.asarray(snapshot[name])
        if array.shape != (50,) or array.dtype != np.dtype(np.float32) or not np.all(np.isfinite(array)):
            raise ValueError(f"Winner-v69 source {name} schema changed")
    if np.any(np.asarray(snapshot["target_std"]) <= 0.0):
        raise ValueError("Winner-v69 source target_std is not positive")


'''

SOURCE_EVIDENCE = '''    source_result = json.loads(V45_RESULT.read_text(encoding="utf-8"))
    teacher_result = json.loads(V22_RESULT.read_text(encoding="utf-8"))
    if (
        source_result.get("status")
        != "STOPPED_WINNER_V68_BACKTRACKING_GRID_EXHAUSTED_AT_602"
        or source_result.get("decision")
        != "PREREGISTER_WINNER_V69_COUNT_602_DIRECTION_ATTRIBUTION_ONLY"
        or source_result.get("failed_checks") != []
        or source_result.get("execution", {}).get("last_durable_optimizer_count")
        != SOURCE_COMPLETED_UPDATES
        or source_result.get("execution", {}).get("failed_attempt_optimizer_count") != 602
        or teacher_result.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or teacher_result.get("failed_checks") != []
    ):
        raise ValueError("Winner-v69 source evidence changed")
'''

DIAGNOSTIC = '''        raw_after, proposed_optimizer = training.adam_step(
            before, gradients, optimizer, learning_rate=training.STAGE2_LEARNING_RATE,
            beta1=training.ADAM_BETA1, beta2=training.ADAM_BETA2,
            epsilon=training.ADAM_EPSILON,
        )
        full_after = training.clamp_stage2_parameters(raw_after)
        full.validate_log_std(full_after)

        def tree_dot(left, right):
            return float(sum(
                np.sum(np.asarray(left[key], dtype=np.float64) * np.asarray(right[key], dtype=np.float64))
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
            full_after,
        )
        scaled_gradient_l2 = tree_l2(gradients)
        adam_delta_l2 = tree_l2(adam_delta)
        if scaled_gradient_l2 <= 0.0 or adam_delta_l2 <= 0.0:
            raise ValueError("Winner-v69 zero count-602 direction")
        negative_gradient_delta = jax.tree_util.tree_map(
            lambda value: -jnp.asarray(value, dtype=jnp.float32)
            * jnp.asarray(adam_delta_l2 / scaled_gradient_l2, dtype=jnp.float32),
            gradients,
        )

        def fraction_rows(delta, fractions):
            rows = []
            for fraction in fractions:
                trial = jax.tree_util.tree_map(
                    lambda old, change: jnp.asarray(old, dtype=jnp.float32)
                    + jnp.asarray(fraction, dtype=jnp.float32)
                    * jnp.asarray(change, dtype=jnp.float32),
                    before,
                    delta,
                )
                trial = training.clamp_stage2_parameters(trial)
                full.validate_log_std(trial)
                trial_loss, _ = static_teacher_objective(trial)
                rows.append({
                    "fraction": float(fraction),
                    "loss": float(trial_loss),
                    "loss_delta": float(trial_loss) - float(teacher_loss),
                })
            return rows

        adam_rows = fraction_rows(adam_delta, preregistration["diagnostic"]["adam_fractions"])
        negative_rows = fraction_rows(
            negative_gradient_delta,
            preregistration["diagnostic"]["negative_gradient_fractions"],
        )
        gradient_dot_delta = tree_dot(teacher_gradients, adam_delta)
        classification, decision = v69_builder.classify_count602(
            loss_before=float(teacher_loss),
            adam_gradient_dot_delta=gradient_dot_delta,
            adam_losses=[row["loss"] for row in adam_rows],
            negative_gradient_losses=[row["loss"] for row in negative_rows],
        )
        checks = {
            "source_count_601_rollout_index_601_attempt_count_602_exact": rollout_update_index == 601
            and int(np.asarray(optimizer["count"])) == 601
            and int(np.asarray(proposed_optimizer["count"])) == 602,
            "original_backtracking_grid_exhaustion_reproduced": all(
                row["loss"] >= float(teacher_loss) for row in adam_rows[:5]
            ),
            "fraction_grids_exact": [row["fraction"] for row in adam_rows]
            == preregistration["diagnostic"]["adam_fractions"]
            and [row["fraction"] for row in negative_rows]
            == preregistration["diagnostic"]["negative_gradient_fractions"],
            "all_values_finite": training.finite_tree({
                "teacher_loss": teacher_loss,
                "teacher_gradients": teacher_gradients,
                "gradients": gradients,
                "raw_after": raw_after,
                "full_after": full_after,
                "proposed_optimizer": proposed_optimizer,
                "adam_rows": adam_rows,
                "negative_rows": negative_rows,
                "gradient_dot_delta": gradient_dot_delta,
            }),
            "no_update_snapshot_graph_support_or_robot_commit": not any(
                (args.work_root / "snapshots").iterdir()
            ) and not any((args.work_root / "graphs").iterdir()),
        }
        failed_checks = sorted(name for name, passed in checks.items() if not passed)
        if failed_checks:
            raise ValueError(f"Winner-v69 attribution invalid: {failed_checks}")
        result = {
            "schema_version": "winner_v69.count602_direction_attribution_result.v1",
            "status": "PASS_WINNER_V69_COUNT602_DIRECTION_ATTRIBUTION",
            "classification": classification,
            "decision": decision,
            "source": {
                "snapshot": source_receipt,
                "optimizer_count": 601,
                "rollout_update_index": rollout_update_index,
                "attempted_optimizer_count": int(np.asarray(proposed_optimizer["count"])),
                "episode_receipts_sha256": episode_hash,
            },
            "loss_geometry": {
                "teacher_loss_before": float(teacher_loss),
                "teacher_gradient_dot_adam_delta": gradient_dot_delta,
                "scaled_teacher_gradient_dot_adam_delta": tree_dot(gradients, adam_delta),
                "adam_delta_l2": adam_delta_l2,
                "scaled_teacher_gradient_l2": scaled_gradient_l2,
                "adam_fraction_rows": adam_rows,
                "negative_gradient_norm_matched_fraction_rows": negative_rows,
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
    source, _ = v66.transformed_source()
    source = replace_exact(source, "Winner-v66", "Winner-v69", count=30)
    source = replace_exact(source, "winner_v66", "winner_v69", count=6)
    source = replace_exact(source, "WINNER_V66", "WINNER_V69", count=6)
    source = replace_exact(
        source,
        'import build_winner_v69_failed_step_attribution as v66_builder  # noqa: E402',
        'import build_winner_v69_count602_direction_attribution as v69_builder  # noqa: E402',
    )
    source = replace_exact(
        source,
        'PREREGISTRATION = ANALYSIS / "winner_v69_failed_step_attribution_preregistration.json"',
        'PREREGISTRATION = ANALYSIS / "winner_v69_count602_direction_attribution_preregistration.json"',
    )
    source = replace_exact(
        source,
        'V45_RESULT = ANALYSIS / "winner_v65b_isolated_persistent_teacher_training_result.json"',
        'V45_RESULT = ANALYSIS / "winner_v68_backtracked_adam_continuation_result.json"',
    )
    source = replace_exact(
        source, "SOURCE_COMPLETED_UPDATES = 574", "SOURCE_COMPLETED_UPDATES = 601"
    )
    source = replace_region(
        source, "def validate_preregistration", "def validate_artifact", VALIDATE_PREREGISTRATION
    )
    source = replace_region(
        source, "def validate_source_snapshot", "def graph_receipt", VALIDATE_SOURCE
    )
    source = replace_region(
        source,
        '    source_result = json.loads(V45_RESULT.read_text(encoding="utf-8"))',
        '    source_receipt = preregistration["source_checkpoint"]["snapshot"]',
        SOURCE_EVIDENCE,
    )
    source = replace_exact(
        source,
        '    parser.add_argument("--failed-step-attribution-authorized", action="store_true")',
        '    parser.add_argument("--count602-attribution-authorized", action="store_true")',
    )
    source = replace_exact(
        source,
        "if not args.offline_cpu_only or not args.failed_step_attribution_authorized:",
        "if not args.offline_cpu_only or not args.count602_attribution_authorized:",
    )
    source = replace_exact(
        source,
        '"Winner-v69 requires --offline-cpu-only --failed-step-attribution-authorized"',
        '"Winner-v69 requires --offline-cpu-only --count602-attribution-authorized"',
    )
    source = replace_region(
        source,
        "        raw_after, proposed_optimizer = training.adam_step(",
        "        deltas = v20.leaf_max_abs_delta(before, after)",
        DIAGNOSTIC + "\n",
    )
    transformed_hash = hashlib.sha256(source.encode()).hexdigest()
    compile(source, "winner_v69_count602_attribution_transformed.py", "exec")
    return source, transformed_hash


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v69 contract: {path}")
    stopped = json.loads(V68_RESULT.read_text(encoding="utf-8"))
    v68_contract = json.loads(V68_CONTRACT.read_text(encoding="utf-8"))
    source, transformed_hash = transformed_source()
    final_snapshot = stopped.get("artifacts", {}).get("snapshots", [])[-1]
    if (
        sha256(V68_RESULT) != V68_RESULT_SHA256
        or stopped.get("status")
        != "STOPPED_WINNER_V68_BACKTRACKING_GRID_EXHAUSTED_AT_602"
        or stopped.get("decision")
        != "PREREGISTER_WINNER_V69_COUNT_602_DIRECTION_ATTRIBUTION_ONLY"
        or stopped.get("execution", {}).get("last_durable_optimizer_count")
        != SOURCE_COUNT
        or final_snapshot.get("completed_updates") != SOURCE_COUNT
        or final_snapshot.get("sha256")
        != "3e3725f1ae5220569422c9ed7a7e7f33fd8799f2e2d90bef66f1493607ac4078"
        or source.count("v69_builder.classify_count602") != 1
    ):
        raise ValueError("Winner-v69 selection evidence changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in {
            "builder": Path("tools/build_winner_v69_count602_direction_attribution.py"),
            "runner": Path("tools/run_winner_v69_count602_direction_attribution.py"),
            "tests": Path("tests/test_winner_v69_count602_direction_attribution.py"),
            "v68_stopped_result": Path(
                "outputs/analysis/winner_v68_backtracked_adam_continuation_result.json"
            ),
            "v68_contract": Path(
                "outputs/analysis/winner_v68_backtracked_adam_continuation_preregistration.json"
            ),
            "v66_builder": Path("tools/build_winner_v66_failed_step_attribution.py"),
        }.items()
    }
    value = {
        "schema_version": "winner_v69.count602_direction_attribution_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V69_COUNT602_DIRECTION_ATTRIBUTION",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_COUNT602_ATTRIBUTION_ONLY",
        "source_checkpoint": {
            "completed_updates": SOURCE_COUNT,
            "optimizer_count": SOURCE_COUNT,
            "snapshot": final_snapshot,
        },
        "teacher_checkpoint": v68_contract["teacher_checkpoint"],
        "diagnostic": {
            "source_optimizer_count": SOURCE_COUNT,
            "rollout_update_index": SOURCE_COUNT,
            "attempted_optimizer_count": ATTEMPT_COUNT,
            "environments": 80,
            "ticks_per_environment": 250,
            "adam_fractions": list(ADAM_FRACTIONS),
            "negative_gradient_fractions": list(NEGATIVE_GRADIENT_FRACTIONS),
            "original_grid_length": 5,
            "coefficient_or_checkpoint_selection": False,
        },
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "stop_rules": [
            "stop if the immutable count-601 snapshot or V68 stop result differs",
            "stop unless the original five-fraction grid exhaustion reproduces",
            "do not persist either counterfactual parameter or optimizer proposal",
            "do not evaluate support behavior or select a checkpoint",
        ],
        "authority": {
            "pass_authorizes_only": "the single one-step proof named by classification",
            "attention_or_flat_transport_selected": False,
            "support_gate_authorized": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
        "transformation": {
            "base": "Winner-v66 failed-step attribution runner",
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
                "# Winner-v69 count-602 direction attribution preregistration",
                "",
                "- Source / attempted counts: `601 / 602`",
                "- Rollout: update index `601`, `80 x 250`, CPU only",
                "- Adam fractions: original grid plus fixed powers of two through `1/1024`",
                "- Comparison: norm-matched instantaneous negative teacher gradient",
                "- Committed updates / snapshots / ONNX / support / robot: `0 / 0 / 0 / 0 / 0`",
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
