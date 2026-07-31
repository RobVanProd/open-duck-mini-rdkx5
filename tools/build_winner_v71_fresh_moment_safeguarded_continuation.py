#!/usr/bin/env python3
"""Preregister the bounded Winner-v71 fresh-moment safeguarded continuation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v71_fresh_moment_safeguarded_continuation_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V71_FRESH_MOMENT_SAFEGUARDED_CONTINUATION_PREREGISTRATION_20260722.md"
V70_RESULT = ANALYSIS / "winner_v70_fresh_moment_step_result.json"
V70_CONTRACT = ANALYSIS / "winner_v70_fresh_moment_step_contract.json"
V70_RESULT_SHA256 = "36156741dde5afeae41c8218fb345cf7699ec474b5a3c552bc5d66a3a7140792"
SOURCE_COUNT = 602
UPDATES = 53
HALF_COUNT = 605
FINAL_COUNT = 655
FRACTIONS = (
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

sys.path.insert(0, str(ROOT / "tools"))
import build_winner_v68_backtracked_adam_continuation as v68  # noqa: E402


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
            f"Winner-v71 transform changed: expected {count}, found {actual}: {old!r}"
        )
    return source.replace(old, new)


def replace_region(source: str, start: str, end: str, replacement: str) -> str:
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"Winner-v71 region markers changed: {start!r} / {end!r}")
    left = source.index(start)
    right = source.index(end, left)
    return source[:left] + replacement + source[right:]


def select_first_descent(
    rows: Sequence[Mapping[str, float]], loss_before: float
) -> Mapping[str, float] | None:
    for expected, row in zip(FRACTIONS, rows, strict=True):
        if float(row["fraction"]) != expected:
            raise ValueError("Winner-v71 safeguard order changed")
        if float(row["loss"]) < loss_before:
            return row
    return None


VALIDATE_PREREGISTRATION = '''def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v71.fresh_moment_safeguarded_continuation_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V71_FRESH_MOMENT_SAFEGUARDED_CONTINUATION"
        or value.get("decision")
        != "AUTHORIZE_ONE_53_UPDATE_FRESH_MOMENT_SAFEGUARDED_ARM_ONLY"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v71 preregistration identity changed")
    frozen = value.get("frozen_training", {})
    if (
        frozen.get("source_completed_updates") != SOURCE_COMPLETED_UPDATES
        or frozen.get("continuation_optimizer_updates") != UPDATES
        or frozen.get("final_optimizer_count") != FINAL_COMPLETED_UPDATES
        or frozen.get("persistent_checkpoints")
        != {"half": HALF_COMPLETED_UPDATES, "final": FINAL_COMPLETED_UPDATES}
        or frozen.get("fractions_largest_first")
        != [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625, 0.0078125, 0.00390625, 0.001953125, 0.0009765625]
        or frozen.get("conditional_moment_reset")
        != "only after inherited grid exhaustion with nonnegative teacher-gradient dot parameter delta"
    ):
        raise ValueError("Winner-v71 frozen training changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v71 source manifest absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v71 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v71 source manifest changed")


'''

VALIDATE_SOURCE = '''def validate_source_snapshot(
    snapshot: Mapping[str, Any], v21: Any, source_result: Mapping[str, Any]
) -> None:
    if set(snapshot) != {"parameters", "optimizer", "metadata", "target_mean", "target_std"}:
        raise ValueError("Winner-v71 source snapshot state schema changed")
    metadata = snapshot["metadata"]
    if (
        metadata.get("schema_version") != "winner_v21.predictor_preserving_snapshot.v1"
        or metadata.get("stage") != "fresh_moment_persistent_teacher_joint_stage2"
        or metadata.get("completed_updates") != SOURCE_COMPLETED_UPDATES
        or metadata.get("source_completed_updates") != 601
        or metadata.get("source_snapshot_sha256")
        != source_result["source"]["snapshot"]["sha256"]
        or metadata.get("root_seed") != 120120
        or metadata.get("learning_rate") != 0.0001
        or metadata.get("accepted_backtracking_fraction") != 0.125
        or metadata.get("reset_moment_keys")
        != sorted(v29.ANCHOR_GRADIENT_KEYS)
        or metadata.get("formal_support_cells") != 0
        or metadata.get("robot_or_rdk_access") != 0
        or int(np.asarray(snapshot["optimizer"]["count"])) != SOURCE_COMPLETED_UPDATES
        or set(snapshot["optimizer"]["m"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(snapshot["optimizer"]["v"]) != set(v21.JOINT_TRAINABLE_KEYS)
    ):
        raise ValueError("Winner-v71 source snapshot metadata changed")
    for name in ("target_mean", "target_std"):
        array = np.asarray(snapshot[name])
        if array.shape != (50,) or array.dtype != np.dtype(np.float32) or not np.all(np.isfinite(array)):
            raise ValueError(f"Winner-v71 source {name} schema changed")


'''

SOURCE_EVIDENCE = '''    source_result = json.loads(V45_RESULT.read_text(encoding="utf-8"))
    teacher_result = json.loads(V22_RESULT.read_text(encoding="utf-8"))
    if (
        source_result.get("status") != "PASS_WINNER_V70_FRESH_MOMENT_STEP"
        or source_result.get("decision")
        != "PREREGISTER_BOUNDED_FRESH_MOMENT_SAFEGUARDED_CONTINUATION_ONLY"
        or source_result.get("failed_checks") != []
        or source_result.get("execution", {}).get("optimizer_updates") != 1
        or source_result.get("optimization", {}).get("optimizer_count_after")
        != SOURCE_COMPLETED_UPDATES
        or source_result.get("optimization", {}).get("accepted_fraction") != 0.125
        or teacher_result.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or teacher_result.get("failed_checks") != []
    ):
        raise ValueError("Winner-v71 source evidence changed")
'''

SAFEGUARD = '''        reset_keys = tuple(sorted(v29.ANCHOR_GRADIENT_KEYS))

        def tree_dot(left, right):
            return float(sum(
                np.sum(np.asarray(left[key], dtype=np.float64) * np.asarray(right[key], dtype=np.float64))
                for key in sorted(left)
            ))

        def propose(candidate_optimizer):
            raw, proposed_optimizer = training.adam_step(
                before, gradients, candidate_optimizer,
                learning_rate=training.STAGE2_LEARNING_RATE,
                beta1=training.ADAM_BETA1, beta2=training.ADAM_BETA2,
                epsilon=training.ADAM_EPSILON,
            )
            full_candidate = training.clamp_stage2_parameters(raw)
            full.validate_log_std(full_candidate)
            delta = jax.tree_util.tree_map(
                lambda old, new: jnp.asarray(new, dtype=jnp.float32)
                - jnp.asarray(old, dtype=jnp.float32),
                before,
                full_candidate,
            )
            rows = []
            trials = []
            for fraction in preregistration["frozen_training"]["fractions_largest_first"]:
                trial = jax.tree_util.tree_map(
                    lambda old, change: jnp.asarray(old, dtype=jnp.float32)
                    + jnp.asarray(fraction, dtype=jnp.float32)
                    * jnp.asarray(change, dtype=jnp.float32),
                    before,
                    delta,
                )
                trial = training.clamp_stage2_parameters(trial)
                full.validate_log_std(trial)
                loss, _ = static_teacher_objective(trial)
                rows.append({
                    "fraction": float(fraction),
                    "loss": float(loss),
                    "loss_delta": float(loss) - float(teacher_loss),
                })
                trials.append(trial)
            selected = v71_builder.select_first_descent(rows, float(teacher_loss))
            selected_index = None if selected is None else next(
                index for index, row in enumerate(rows) if row is selected
            )
            return proposed_optimizer, delta, rows, trials, selected, selected_index

        (
            optimizer_after,
            inherited_delta,
            inherited_rows,
            inherited_trials,
            accepted_row,
            accepted_index,
        ) = propose(optimizer)
        adam_direction_dot = tree_dot(teacher_gradients, inherited_delta)
        moment_reset_applied = False
        active_rows = inherited_rows
        active_trials = inherited_trials
        if accepted_row is None:
            if adam_direction_dot < 0.0:
                raise ValueError(
                    f"Winner-v71 descending Adam direction exhausted grid at {completed_updates}"
                )
            fresh_optimizer = {
                "count": jnp.asarray(optimizer["count"]),
                "m": {
                    key: jnp.zeros_like(value) if key in reset_keys else jnp.asarray(value)
                    for key, value in optimizer["m"].items()
                },
                "v": {
                    key: jnp.zeros_like(value) if key in reset_keys else jnp.asarray(value)
                    for key, value in optimizer["v"].items()
                },
            }
            (
                optimizer_after,
                _,
                reset_rows,
                reset_trials,
                accepted_row,
                accepted_index,
            ) = propose(fresh_optimizer)
            if accepted_row is None:
                raise ValueError(
                    f"Winner-v71 fresh-moment safeguard exhausted grid at {completed_updates}"
                )
            moment_reset_applied = True
            active_rows = reset_rows
            active_trials = reset_trials
        after = active_trials[accepted_index]
        accepted_fraction = float(accepted_row["fraction"])
        optimizer = optimizer_after
        teacher_loss_after, teacher_metrics_after = static_teacher_objective(after)
        if not float(teacher_loss_after) < float(teacher_loss):
            raise ValueError(
                f"Winner-v71 accepted step did not decrease at {completed_updates}"
            )'''


def transformed_source() -> tuple[str, str]:
    source, _ = v68.transformed_source()
    source = replace_exact(source, "Winner-v68", "Winner-v71", count=31)
    source = replace_exact(source, "winner_v68", "winner_v71", count=5)
    source = replace_exact(source, "WINNER_V68", "WINNER_V71", count=4)
    source = replace_exact(
        source,
        'import build_winner_v71_backtracked_adam_continuation as v68_builder  # noqa: E402',
        'import build_winner_v71_fresh_moment_safeguarded_continuation as v71_builder  # noqa: E402',
    )
    source = replace_exact(
        source,
        'PREREGISTRATION = ANALYSIS / "winner_v71_backtracked_adam_continuation_preregistration.json"',
        'PREREGISTRATION = ANALYSIS / "winner_v71_fresh_moment_safeguarded_continuation_preregistration.json"',
    )
    source = replace_exact(
        source,
        'V45_RESULT = ANALYSIS / "winner_v67_backtracked_adam_step_result.json"',
        'V45_RESULT = ANALYSIS / "winner_v70_fresh_moment_step_result.json"',
    )
    source = replace_exact(source, "UPDATES = 80", "UPDATES = 53")
    source = replace_exact(
        source, "SOURCE_COMPLETED_UPDATES = 575", "SOURCE_COMPLETED_UPDATES = 602"
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
    source = replace_region(
        source,
        "        raw_after, optimizer_after = training.adam_step(",
        "        deltas = v20.leaf_max_abs_delta(before, after)",
        SAFEGUARD + "\n",
    )
    source = replace_exact(
        source,
        '''            "accepted_backtracking_fraction": accepted_fraction,
            "backtracking_rows": backtracking_rows,''',
        '''            "accepted_backtracking_fraction": accepted_fraction,
            "moment_reset_applied": moment_reset_applied,
            "adam_direction_dot_teacher_gradient": adam_direction_dot,
            "inherited_backtracking_rows": inherited_rows,
            "active_backtracking_rows": active_rows,''',
    )
    source = replace_exact(
        source,
        '"stage": "backtracked_persistent_teacher_joint_stage2"',
        '"stage": "fresh_moment_safeguarded_teacher_joint_stage2"',
        count=1,
    )
    source = replace_exact(
        source,
        '== "backtracked_persistent_teacher_joint_stage2"',
        '== "fresh_moment_safeguarded_teacher_joint_stage2"',
        count=1,
    )
    source = replace_exact(
        source,
        '"snapshot_backtracked_adam_update_{completed_updates:03d}.npz"',
        '"snapshot_fresh_moment_safeguarded_update_{completed_updates:03d}.npz"',
    )
    source = replace_exact(
        source,
        '''                "learning_rate": float(training.STAGE2_LEARNING_RATE),
                "predictor_scale": float(v22v2.FROZEN_PREDICTOR_SCALE),''',
        '''                "learning_rate": float(training.STAGE2_LEARNING_RATE),
                "accepted_backtracking_fraction": accepted_fraction,
                "moment_reset_applied": moment_reset_applied,
                "reset_moment_keys": list(reset_keys) if moment_reset_applied else [],
                "predictor_scale": float(v22v2.FROZEN_PREDICTOR_SCALE),''',
    )
    source = replace_exact(source, "list(range(576, 656))", "list(range(603, 656))")
    source = replace_exact(source, "exact_80", "exact_53", count=2)
    source = replace_exact(source, "all_80", "all_53", count=11)
    source = replace_exact(source, "len(metrics) == 80", "len(metrics) == 53")
    source = replace_exact(source, "len(snapshots) == 80", "len(snapshots) == 53")
    source = replace_exact(
        source,
        '"source_snapshot_graph_and_optimizer_count_575_exact"',
        '"source_snapshot_graph_and_optimizer_count_602_exact"',
    )
    source = replace_exact(
        source,
        '"completed_updates": 575, "optimizer_count": 575',
        '"completed_updates": 602, "optimizer_count": 602',
    )
    source = replace_exact(
        source,
        '"completed_updates": 575,',
        '"completed_updates": 602,',
        count=1,
    )
    source = replace_exact(
        source,
        '"status": "PASS_WINNER_V71_BACKTRACKED_ADAM_CONTINUATION" if not failed else "HOLD_WINNER_V71_BACKTRACKED_ADAM_CONTINUATION",',
        '"status": "PASS_WINNER_V71_FRESH_MOMENT_SAFEGUARDED_CONTINUATION" if not failed else "HOLD_WINNER_V71_FRESH_MOMENT_SAFEGUARDED_CONTINUATION",',
    )
    source = replace_exact(
        source,
        '"optimizer_updates": 80, "rollout_episode_slots": 6_400, "scheduled_rollout_ticks": 1_600_000,',
        '"optimizer_updates": 53, "rollout_episode_slots": 4_240, "scheduled_rollout_ticks": 1_060_000,',
    )
    source = replace_exact(
        source,
        '"v67_result_lf_sha256": lf_sha256(V45_RESULT),',
        '"v70_result_lf_sha256": lf_sha256(V45_RESULT),',
    )
    transformed_hash = hashlib.sha256(source.encode()).hexdigest()
    compile(source, "winner_v71_fresh_moment_continuation_transformed.py", "exec")
    return source, transformed_hash


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v71 contract: {path}")
    source_result = json.loads(V70_RESULT.read_text(encoding="utf-8"))
    source_contract = json.loads(V70_CONTRACT.read_text(encoding="utf-8"))
    source, transformed_hash = transformed_source()
    if (
        sha256(V70_RESULT) != V70_RESULT_SHA256
        or source_result.get("status") != "PASS_WINNER_V70_FRESH_MOMENT_STEP"
        or source_result.get("decision")
        != "PREREGISTER_BOUNDED_FRESH_MOMENT_SAFEGUARDED_CONTINUATION_ONLY"
        or source_result.get("optimization", {}).get("optimizer_count_after")
        != SOURCE_COUNT
        or source_result.get("optimization", {}).get("accepted_fraction") != 0.125
        or source.count("v71_builder.select_first_descent") != 1
    ):
        raise ValueError("Winner-v71 selection evidence changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in {
            "builder": Path(
                "tools/build_winner_v71_fresh_moment_safeguarded_continuation.py"
            ),
            "runner": Path(
                "tools/run_winner_v71_fresh_moment_safeguarded_continuation.py"
            ),
            "tests": Path(
                "tests/test_winner_v71_fresh_moment_safeguarded_continuation.py"
            ),
            "v70_result": Path("outputs/analysis/winner_v70_fresh_moment_step_result.json"),
            "v70_contract": Path("outputs/analysis/winner_v70_fresh_moment_step_contract.json"),
            "v68_builder": Path("tools/build_winner_v68_backtracked_adam_continuation.py"),
        }.items()
    }
    value = {
        "schema_version": "winner_v71.fresh_moment_safeguarded_continuation_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V71_FRESH_MOMENT_SAFEGUARDED_CONTINUATION",
        "decision": "AUTHORIZE_ONE_53_UPDATE_FRESH_MOMENT_SAFEGUARDED_ARM_ONLY",
        "source_checkpoint": {
            "completed_updates": SOURCE_COUNT,
            "optimizer_count": SOURCE_COUNT,
            "snapshot": source_result["snapshot"],
            "graph": source_result["graph"],
        },
        "teacher_checkpoint": source_contract["teacher_checkpoint"],
        "frozen_training": {
            "source_completed_updates": SOURCE_COUNT,
            "continuation_optimizer_updates": UPDATES,
            "final_optimizer_count": FINAL_COUNT,
            "persistent_checkpoints": {"half": HALF_COUNT, "final": FINAL_COUNT},
            "fractions_largest_first": list(FRACTIONS),
            "conditional_moment_reset": (
                "only after inherited grid exhaustion with nonnegative teacher-gradient dot parameter delta"
            ),
            "reset_keys": "the six teacher-active policy leaves only",
            "environments_per_update": 80,
            "ticks_per_environment": 250,
            "persistent_snapshots": True,
            "snapshot_metadata": [
                "accepted_backtracking_fraction",
                "moment_reset_applied",
                "reset_moment_keys",
            ],
        },
        "objective": {
            "update_gradient": "full_action_persistent_teacher_only",
            "persistent_teacher_scale": 136.35153198242188,
            "attention_or_flat_transport_added": False,
            "coefficient_or_length_search": False,
        },
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "training_authorized": True,
            "pass_authorizes_only": "the unchanged persistence gate for counts 605 and 655",
            "formal_support_gate_authorized": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
        "transformation": {
            "base": "Winner-v68 bounded backtracked-Adam continuation runner",
            "transformed_source_sha256": transformed_hash,
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
                "# Winner-v71 fresh-moment safeguarded continuation preregistration",
                "",
                "- Source / half / final counts: `602 / 605 / 655`",
                "- Remaining updates: `53`, each `80 x 250`, CPU only",
                "- Inherited Adam first; reset six policy moments only on causally verified opposition",
                "- Largest-first safeguard through `1/1024`",
                "- Fraction/reset decision persisted in every snapshot",
                "- Support / checkpoint selection / deployment / robot: `0 / false / false / 0`",
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
