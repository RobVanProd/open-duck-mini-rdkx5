#!/usr/bin/env python3
"""Preregister the bounded Winner-v68 backtracked-Adam continuation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v68_backtracked_adam_continuation_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V68_BACKTRACKED_ADAM_CONTINUATION_PREREGISTRATION_20260722.md"
V67_RESULT = ANALYSIS / "winner_v67_backtracked_adam_step_result.json"
V67_CORRECTION = ANALYSIS / "winner_v67b_source_decision_correction.json"
V65_CONTRACT = ANALYSIS / "winner_v65b_isolated_persistent_teacher_training_preregistration.json"
V67_RESULT_SHA256 = "90614ecfe5a5383b1e27809049a737cfc6f59cb6abb1b29284c65416442c6b66"
SOURCE_COUNT = 575
UPDATES = 80
HALF_COUNT = 605
FINAL_COUNT = 655
FRACTIONS = (1.0, 0.5, 0.25, 0.125, 0.0625)

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
            f"Winner-v68 transform changed: expected {count}, found {actual}: {old!r}"
        )
    return source.replace(old, new)


def replace_region(source: str, start: str, end: str, replacement: str) -> str:
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"Winner-v68 region markers changed: {start!r} / {end!r}")
    left = source.index(start)
    right = source.index(end, left)
    return source[:left] + replacement + source[right:]


def select_first_descent(
    rows: Sequence[Mapping[str, float]], loss_before: float
) -> Mapping[str, float] | None:
    for expected, row in zip(FRACTIONS, rows, strict=True):
        if float(row["fraction"]) != expected:
            raise ValueError("Winner-v68 backtracking order changed")
        if float(row["loss"]) < loss_before:
            return row
    return None


VALIDATE_PREREGISTRATION = '''def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v68.backtracked_adam_continuation_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V68_BACKTRACKED_ADAM_CONTINUATION"
        or value.get("decision")
        != "AUTHORIZE_ONE_80_UPDATE_BACKTRACKED_ADAM_ARM_ONLY"
        or value.get("execution_now")
        != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v68 preregistration identity changed")
    frozen = value.get("frozen_training", {})
    if (
        frozen.get("source_completed_updates") != SOURCE_COMPLETED_UPDATES
        or frozen.get("continuation_optimizer_updates") != UPDATES
        or frozen.get("final_optimizer_count") != FINAL_COMPLETED_UPDATES
        or frozen.get("persistent_checkpoints")
        != {"half": HALF_COMPLETED_UPDATES, "final": FINAL_COMPLETED_UPDATES}
        or frozen.get("fractions_largest_first")
        != [1.0, 0.5, 0.25, 0.125, 0.0625]
        or frozen.get("environments_per_update") != 80
        or frozen.get("ticks_per_environment") != 250
        or value.get("objective", {}).get("update_gradient")
        != "full_action_persistent_teacher_only"
    ):
        raise ValueError("Winner-v68 frozen training changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v68 source manifest absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v68 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v68 source manifest changed")


'''

VALIDATE_SOURCE = '''def validate_source_snapshot(
    snapshot: Mapping[str, Any], v21: Any, source_result: Mapping[str, Any]
) -> None:
    if set(snapshot) != {"parameters", "optimizer", "metadata", "target_mean", "target_std"}:
        raise ValueError("Winner-v68 source snapshot state schema changed")
    metadata = snapshot["metadata"]
    if (
        metadata.get("schema_version") != "winner_v21.predictor_preserving_snapshot.v1"
        or metadata.get("stage") != "backtracked_persistent_teacher_joint_stage2"
        or metadata.get("completed_updates") != SOURCE_COMPLETED_UPDATES
        or metadata.get("source_completed_updates") != 574
        or metadata.get("source_snapshot_sha256")
        != source_result["source"]["snapshot"]["sha256"]
        or metadata.get("root_seed") != 120120
        or metadata.get("learning_rate") != 0.0001
        or metadata.get("accepted_backtracking_fraction") != 0.25
        or metadata.get("formal_support_cells") != 0
        or metadata.get("locomotion_steps") != 0
        or metadata.get("robot_or_rdk_access") != 0
        or int(np.asarray(snapshot["optimizer"]["count"])) != SOURCE_COMPLETED_UPDATES
        or set(snapshot["optimizer"]["m"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(snapshot["optimizer"]["v"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(v21.joint_trainable_parameters(snapshot["parameters"]))
        != set(v21.JOINT_TRAINABLE_KEYS)
    ):
        raise ValueError("Winner-v68 source snapshot metadata changed")
    for name in ("target_mean", "target_std"):
        array = np.asarray(snapshot[name])
        if array.shape != (50,) or array.dtype != np.dtype(np.float32) or not np.all(np.isfinite(array)):
            raise ValueError(f"Winner-v68 source {name} schema changed")
    if np.any(np.asarray(snapshot["target_std"]) <= 0.0):
        raise ValueError("Winner-v68 source target_std is not positive")
    for tree in (snapshot["parameters"], snapshot["optimizer"]["m"], snapshot["optimizer"]["v"]):
        if not all(np.all(np.isfinite(np.asarray(item))) for item in tree.values()):
            raise ValueError("Winner-v68 source snapshot contains nonfinite arrays")


'''

SOURCE_EVIDENCE = '''    source_result = json.loads(V45_RESULT.read_text(encoding="utf-8"))
    teacher_result = json.loads(V22_RESULT.read_text(encoding="utf-8"))
    if (
        source_result.get("status") != "PASS_WINNER_V67_BACKTRACKED_ADAM_STEP"
        or source_result.get("decision")
        != "PREREGISTER_BOUNDED_DETERMINISTIC_BACKTRACKED_ADAM_CONTINUATION_ONLY"
        or source_result.get("failed_checks") != []
        or source_result.get("execution", {}).get("optimizer_updates") != 1
        or source_result.get("optimization", {}).get("optimizer_count_after")
        != SOURCE_COMPLETED_UPDATES
        or source_result.get("optimization", {}).get("accepted_fraction") != 0.25
        or teacher_result.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or teacher_result.get("failed_checks") != []
    ):
        raise ValueError("Winner-v68 source evidence changed")
'''

BACKTRACK = '''        raw_after, optimizer_after = training.adam_step(
            before, gradients, optimizer, learning_rate=training.STAGE2_LEARNING_RATE,
            beta1=training.ADAM_BETA1, beta2=training.ADAM_BETA2,
            epsilon=training.ADAM_EPSILON,
        )
        full_after = training.clamp_stage2_parameters(raw_after)
        full.validate_log_std(full_after)
        full_loss, _ = static_teacher_objective(full_after)
        full_delta = jax.tree_util.tree_map(
            lambda old, new: jnp.asarray(new, dtype=jnp.float32)
            - jnp.asarray(old, dtype=jnp.float32),
            before,
            full_after,
        )
        backtracking_rows = []
        backtracking_trials = []
        for fraction in preregistration["frozen_training"]["fractions_largest_first"]:
            trial = jax.tree_util.tree_map(
                lambda old, change: jnp.asarray(old, dtype=jnp.float32)
                + jnp.asarray(fraction, dtype=jnp.float32)
                * jnp.asarray(change, dtype=jnp.float32),
                before,
                full_delta,
            )
            trial = training.clamp_stage2_parameters(trial)
            full.validate_log_std(trial)
            loss, _ = static_teacher_objective(trial)
            backtracking_rows.append({
                "fraction": float(fraction),
                "loss": float(loss),
                "loss_delta": float(loss) - float(teacher_loss),
            })
            backtracking_trials.append(trial)
        accepted_row = v68_builder.select_first_descent(
            backtracking_rows, float(teacher_loss)
        )
        if accepted_row is None:
            raise ValueError(
                f"Winner-v68 backtracking found no strict descent at {completed_updates}"
            )
        accepted_index = next(
            index for index, row in enumerate(backtracking_rows) if row is accepted_row
        )
        after = backtracking_trials[accepted_index]
        accepted_fraction = float(accepted_row["fraction"])
        optimizer = optimizer_after
        teacher_loss_after, teacher_metrics_after = static_teacher_objective(after)
        if not float(teacher_loss_after) < float(teacher_loss):
            raise ValueError(
                f"Winner-v68 accepted step did not decrease at {completed_updates}"
            )'''


def transformed_source() -> tuple[str, str]:
    source, _ = v65b.corrected_source()
    source = replace_exact(source, "Winner-v65", "Winner-v68", count=30)
    source = replace_exact(source, "winner_v65", "winner_v68", count=4)
    source = replace_exact(source, "WINNER_V65", "WINNER_V68", count=4)
    source = replace_exact(
        source,
        'import winner_v56_first_tick_teacher_mapping as v56  # noqa: E402',
        '''import winner_v56_first_tick_teacher_mapping as v56  # noqa: E402
import build_winner_v68_backtracked_adam_continuation as v68_builder  # noqa: E402''',
    )
    source = replace_exact(
        source,
        'PREREGISTRATION = ANALYSIS / "winner_v68b_isolated_persistent_teacher_training_preregistration.json"',
        'PREREGISTRATION = ANALYSIS / "winner_v68_backtracked_adam_continuation_preregistration.json"',
    )
    source = replace_exact(
        source,
        'V45_RESULT = ANALYSIS / "winner_v64b_isolated_persistent_teacher_step_result.json"',
        'V45_RESULT = ANALYSIS / "winner_v67_backtracked_adam_step_result.json"',
    )
    source = replace_exact(source, "UPDATES = 100", "UPDATES = 80")
    source = replace_exact(
        source, "SOURCE_COMPLETED_UPDATES = 555", "SOURCE_COMPLETED_UPDATES = 575"
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
                f"Winner-v68 same-batch teacher loss did not decrease at {completed_updates}"
            )''',
        BACKTRACK,
    )
    source = replace_exact(
        source,
        '''            "full_action_teacher_loss_delta": float(teacher_loss_after) - float(teacher_loss),''',
        '''            "full_action_teacher_loss_delta": float(teacher_loss_after) - float(teacher_loss),
            "full_adam_teacher_loss": float(full_loss),
            "accepted_backtracking_fraction": accepted_fraction,
            "backtracking_rows": backtracking_rows,''',
    )
    source = replace_exact(
        source,
        '"stage": "isolated_persistent_teacher_joint_stage2"',
        '"stage": "backtracked_persistent_teacher_joint_stage2"',
        count=1,
    )
    source = replace_exact(
        source,
        '== "isolated_persistent_teacher_joint_stage2"',
        '== "backtracked_persistent_teacher_joint_stage2"',
        count=1,
    )
    source = replace_exact(
        source,
        '"snapshot_isolated_persistent_teacher_update_{completed_updates:03d}.npz"',
        '"snapshot_backtracked_adam_update_{completed_updates:03d}.npz"',
    )
    source = replace_exact(
        source, "list(range(556, 656))", "list(range(576, 656))"
    )
    source = replace_exact(source, "exact_100", "exact_80", count=2)
    source = replace_exact(source, "all_100", "all_80", count=11)
    source = replace_exact(source, "len(metrics) == 100", "len(metrics) == 80")
    source = replace_exact(source, "len(snapshots) == 100", "len(snapshots) == 80")
    source = replace_exact(
        source,
        '"source_snapshot_graph_and_optimizer_count_555_exact"',
        '"source_snapshot_graph_and_optimizer_count_575_exact"',
    )
    source = replace_exact(
        source,
        '"completed_updates": 555, "optimizer_count": 555',
        '"completed_updates": 575, "optimizer_count": 575',
    )
    source = replace_exact(
        source,
        '"completed_updates": 555,',
        '"completed_updates": 575,',
        count=1,
    )
    source = replace_exact(
        source,
        '"status": "PASS_WINNER_V68_INTEGRATED_FIRST_TICK_TEACHER_TRAINING_ARTIFACT" if not failed else "HOLD_WINNER_V68_INTEGRATED_FIRST_TICK_TEACHER_TRAINING_ARTIFACT",',
        '"status": "PASS_WINNER_V68_BACKTRACKED_ADAM_CONTINUATION" if not failed else "HOLD_WINNER_V68_BACKTRACKED_ADAM_CONTINUATION",',
    )
    source = replace_exact(
        source,
        '"decision": "AUTHORIZE_INTEGRATED_FIRST_TICK_TEACHER_SUPPORT_GATE_PREREGISTRATION_ONLY" if not failed else "DO_NOT_EVALUATE_WINNER_V68_POLICY",',
        '"decision": "AUTHORIZE_UNCHANGED_PERSISTENCE_GATE_FOR_COUNTS_605_AND_655_ONLY" if not failed else "DO_NOT_EVALUATE_WINNER_V68_POLICY",',
    )
    source = replace_exact(
        source,
        '"optimizer_updates": 100, "scheduled_episode_slots": 2_000_000,',
        '"optimizer_updates": 80, "rollout_episode_slots": 6_400, "scheduled_rollout_ticks": 1_600_000,',
    )
    source = replace_exact(
        source,
        '"v64b_result_lf_sha256": lf_sha256(V45_RESULT),',
        '"v67_result_lf_sha256": lf_sha256(V45_RESULT),',
    )
    source = replace_exact(
        source,
        '"pass_authorizes_only": "a separate frozen isolated persistent-teacher support gate preregistration",',
        '"pass_authorizes_only": "the unchanged frozen persistence gate for counts 605 and 655",',
    )
    transformed_hash = hashlib.sha256(source.encode()).hexdigest()
    compile(source, "winner_v68_backtracked_adam_continuation_transformed.py", "exec")
    return source, transformed_hash


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v68 contract: {path}")
    source_result = json.loads(V67_RESULT.read_text(encoding="utf-8"))
    correction = json.loads(V67_CORRECTION.read_text(encoding="utf-8"))
    v65_contract = json.loads(V65_CONTRACT.read_text(encoding="utf-8"))
    source, transformed_hash = transformed_source()
    if (
        sha256(V67_RESULT) != V67_RESULT_SHA256
        or source_result.get("status") != "PASS_WINNER_V67_BACKTRACKED_ADAM_STEP"
        or source_result.get("decision")
        != "PREREGISTER_BOUNDED_DETERMINISTIC_BACKTRACKED_ADAM_CONTINUATION_ONLY"
        or source_result.get("optimization", {}).get("optimizer_count_after")
        != SOURCE_COUNT
        or source_result.get("optimization", {}).get("accepted_fraction") != 0.25
        or correction.get("v67b", {}).get("replacement_count") != 1
        or source.count("v68_builder.select_first_descent") != 1
    ):
        raise ValueError("Winner-v68 selection evidence changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in {
            "builder": Path("tools/build_winner_v68_backtracked_adam_continuation.py"),
            "runner": Path("tools/run_winner_v68_backtracked_adam_continuation.py"),
            "tests": Path("tests/test_winner_v68_backtracked_adam_continuation.py"),
            "v67_result": Path(
                "outputs/analysis/winner_v67_backtracked_adam_step_result.json"
            ),
            "v67_correction": Path(
                "outputs/analysis/winner_v67b_source_decision_correction.json"
            ),
            "v65_builder": Path(
                "tools/build_winner_v65_isolated_persistent_teacher_training.py"
            ),
            "v65b_builder": Path(
                "tools/build_winner_v65b_preregistration_path_correction.py"
            ),
        }.items()
    }
    value = {
        "schema_version": "winner_v68.backtracked_adam_continuation_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V68_BACKTRACKED_ADAM_CONTINUATION",
        "decision": "AUTHORIZE_ONE_80_UPDATE_BACKTRACKED_ADAM_ARM_ONLY",
        "source_checkpoint": {
            "completed_updates": SOURCE_COUNT,
            "optimizer_count": SOURCE_COUNT,
            "snapshot": source_result["snapshot"],
            "graph": source_result["graph"],
        },
        "teacher_checkpoint": v65_contract["teacher_checkpoint"],
        "frozen_training": {
            "source_completed_updates": SOURCE_COUNT,
            "source_optimizer_count": SOURCE_COUNT,
            "continuation_optimizer_updates": UPDATES,
            "final_optimizer_count": FINAL_COUNT,
            "persistent_checkpoints": {"half": HALF_COUNT, "final": FINAL_COUNT},
            "fractions_largest_first": list(FRACTIONS),
            "acceptance_rule": "first strict same-batch persistent-teacher loss descent",
            "optimizer_moments": "advance exactly once per accepted update",
            "environments_per_update": 80,
            "ticks_per_environment": 250,
            "training_root_seed": 120120,
            "learning_rate": 0.0001,
            "persistent_snapshots": True,
        },
        "objective": {
            "update_gradient": "full_action_persistent_teacher_only",
            "persistent_teacher": v65_contract["objective"]["persistent_teacher"],
            "monitor_only_excluded_from_update": v65_contract["objective"][
                "monitor_only_excluded_from_update"
            ],
            "attention_or_flat_transport_added": False,
            "coefficient_or_length_search": False,
        },
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "post_training_selection": {
            "authorized_now": False,
            "checkpoint_rule": (
                "both count-605 and count-655 endpoints must pass the unchanged "
                "persistence gate; training loss or accepted fractions cannot select"
            ),
        },
        "stop_rules": [
            "stop if the exact count-575 snapshot, graph, Adam state, or teacher differs",
            "stop if any rollout, transition, teacher mask, or monitor contract differs",
            "stop if no frozen backtracking fraction strictly descends on an update",
            "stop on any snapshot or endpoint ONNX round-trip mismatch",
            "do not inspect support behavior or select a checkpoint in this workflow",
        ],
        "authority": {
            "training_authorized": True,
            "pass_authorizes_only": (
                "preregistration of the unchanged persistence gate for counts 605 and 655"
            ),
            "formal_support_gate_authorized": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
        "transformation": {
            "base": "Winner-v65b isolated-teacher continuation runner",
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
                "# Winner-v68 backtracked-Adam continuation preregistration",
                "",
                "- Source / half / final optimizer counts: `575 / 605 / 655`",
                "- Updates: `80`, each `80 x 250`, CPU only",
                "- Fractions, largest first: `1, 1/2, 1/4, 1/8, 1/16`",
                "- Acceptance: first strict same-batch teacher-loss descent",
                "- Atomic snapshots: every accepted update",
                "- Endpoint ONNX: count `605` and `655` only",
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
