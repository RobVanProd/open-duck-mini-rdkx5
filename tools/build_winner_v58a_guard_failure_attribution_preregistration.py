#!/usr/bin/env python3
"""Freeze one zero-update attribution of the interrupted Winner-v58 guard."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path[:0] = [str(TOOLS), str(PATCHES)]

OUTPUT = ANALYSIS / "winner_v58a_guard_failure_attribution_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V58A_GUARD_FAILURE_ATTRIBUTION_PREREGISTRATION_20260722.md"
V58_PREREG = ANALYSIS / "winner_v58_integrated_first_tick_training_preregistration.json"
V57_RESULT = ANALYSIS / "winner_v57_first_tick_teacher_one_update_result.json"
INTERRUPTED_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-mini-rdkx5\winner-v58-integrated-first-tick-training"
)
SOURCE_SNAPSHOT = (
    INTERRUPTED_ROOT
    / "snapshots"
    / "snapshot_integrated_first_tick_teacher_update_476.npz"
)
STDERR_LOG = Path(
    r"D:\CodexArtifacts\open-duck-mini-rdkx5\winner-v58-integrated-first-tick-training.stderr.log"
)
EXPECTED_SOURCE_SHA256 = "9835cbf06c612b369a041910f1eb7ccc795ee64aeb7790120796363b1b03bb54"

CUSTOM_SOURCES = {
    "v58a_builder": Path(
        "tools/build_winner_v58a_guard_failure_attribution_preregistration.py"
    ),
    "v58a_runner": Path("tools/run_winner_v58a_guard_failure_attribution.py"),
    "v58a_tests": Path("tests/test_winner_v58a_guard_failure_attribution.py"),
    "v58_preregistration": Path(
        "outputs/analysis/winner_v58_integrated_first_tick_training_preregistration.json"
    ),
    "v58_transform_builder": Path(
        "tools/build_winner_v58_integrated_first_tick_training_preregistration.py"
    ),
}


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


def _replace_function(source: str, name: str, replacement: str) -> tuple[str, dict[str, Any]]:
    start = source.index(f"def {name}(")
    end = source.index("\ndef ", start + 1)
    old = source[start:end]
    value = source[:start] + replacement + "\n" + source[end + 1 :]
    return value, {
        "old_sha256": hashlib.sha256(old.encode()).hexdigest(),
        "new_sha256": hashlib.sha256(replacement.encode()).hexdigest(),
        "replacement_count": 1,
    }


def transformed_source() -> tuple[str, list[dict[str, Any]]]:
    import build_winner_v58_integrated_first_tick_training_preregistration as v58

    source, _ = v58.transformed_source()
    receipts: list[dict[str, Any]] = []

    def replace(old: str, new: str, count: int = 1) -> None:
        nonlocal source
        actual = source.count(old)
        if actual != count:
            raise ValueError(
                f"Winner-v58a transform count changed: expected {count}, "
                f"found {actual}: {old!r}"
            )
        source = source.replace(old, new)
        receipts.append(
            {
                "old_sha256": hashlib.sha256(old.encode()).hexdigest(),
                "new_sha256": hashlib.sha256(new.encode()).hexdigest(),
                "replacement_count": count,
            }
        )

    replace(
        '"""Run the one frozen 100-update Winner-v58 integrated first-tick-teacher CPU arm."""',
        '"""Attribute the interrupted Winner-v58 pre-update guard with zero updates."""',
    )
    replace(
        '"winner_v58_integrated_first_tick_training_preregistration.json"',
        '"winner_v58a_guard_failure_attribution_preregistration.json"',
    )
    replace("UPDATES = 100", "UPDATES = 1")
    replace("SOURCE_COMPLETED_UPDATES = 454", "SOURCE_COMPLETED_UPDATES = 476")
    replace(
        "integrated_first_tick_teacher_training_authorized",
        "guard_failure_attribution_authorized",
        1,
    )
    replace(
        "--integrated-first-tick-teacher-training-authorized",
        "--guard-failure-attribution-authorized",
        2,
    )

    validate_preregistration = '''def validate_preregistration(value: Mapping[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "winner_v58a.guard_failure_attribution_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V58A_GUARD_FAILURE_ATTRIBUTION"
        or value.get("decision")
        != "AUTHORIZE_ONE_ZERO_UPDATE_WINNER_V58_GUARD_ATTRIBUTION_ONLY"
        or value.get("execution_now") != {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v58a preregistration identity changed")
    diagnostic = value.get("diagnostic", {})
    if (
        diagnostic.get("source_completed_updates") != SOURCE_COMPLETED_UPDATES
        or diagnostic.get("rollout_update_index") != 476
        or diagnostic.get("would_complete_update") != 477
        or diagnostic.get("environments") != 80
        or diagnostic.get("ticks_per_environment") != 250
        or diagnostic.get("optimizer_updates") != 0
        or diagnostic.get("all_original_guard_predicates_reported") is not True
    ):
        raise ValueError("Winner-v58a diagnostic scope changed")
    authority = value.get("authority", {})
    if (
        authority.get("diagnostic_authorized") is not True
        or authority.get("retry_authorized") is not False
        or authority.get("formal_support_gate_authorized") is not False
        or authority.get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v58a authority changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v58a sources are absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v58a source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v58a source manifest changed")
'''
    source, receipt = _replace_function(
        source, "validate_preregistration", validate_preregistration
    )
    receipts.append(receipt)

    validate_source_snapshot = '''def validate_source_snapshot(snapshot: Mapping[str, Any], v21: Any, source_result: Mapping[str, Any]) -> None:
    if set(snapshot) != {"parameters", "optimizer", "metadata", "target_mean", "target_std"}:
        raise ValueError("Winner-v58a source snapshot state schema changed")
    metadata = snapshot["metadata"]
    if (
        metadata.get("schema_version") != "winner_v21.predictor_preserving_snapshot.v1"
        or metadata.get("stage") != "integrated_first_tick_teacher_joint_stage2"
        or metadata.get("completed_updates") != SOURCE_COMPLETED_UPDATES
        or metadata.get("source_completed_updates") != 454
        or metadata.get("source_snapshot_sha256") != source_result["snapshot"]["sha256"]
        or metadata.get("teacher_snapshot_sha256")
        != source_result["teacher"]["snapshot_sha256"]
        or metadata.get("root_seed") != 120120
        or metadata.get("learning_rate") != 0.0001
        or metadata.get("first_tick_teacher_scale") != float(v56.RESET_TEACHER_SCALE)
        or metadata.get("formal_support_cells") != 0
        or metadata.get("locomotion_steps") != 0
        or metadata.get("robot_or_rdk_access") != 0
        or int(np.asarray(snapshot["optimizer"]["count"])) != SOURCE_COMPLETED_UPDATES
        or set(snapshot["optimizer"]["m"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(snapshot["optimizer"]["v"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(v21.joint_trainable_parameters(snapshot["parameters"]))
        != set(v21.JOINT_TRAINABLE_KEYS)
    ):
        raise ValueError("Winner-v58a source snapshot metadata changed")
    for name in ("target_mean", "target_std"):
        array = np.asarray(snapshot[name])
        if array.shape != (50,) or array.dtype != np.dtype(np.float32) or not np.all(np.isfinite(array)):
            raise ValueError(f"Winner-v58a source {name} schema changed")
    if np.any(np.asarray(snapshot["target_std"]) <= 0.0):
        raise ValueError("Winner-v58a source target_std is not positive")
    for tree in (snapshot["parameters"], snapshot["optimizer"]["m"], snapshot["optimizer"]["v"]):
        if not all(np.all(np.isfinite(np.asarray(item))) for item in tree.values()):
            raise ValueError("Winner-v58a source snapshot contains nonfinite arrays")
'''
    source, receipt = _replace_function(
        source, "validate_source_snapshot", validate_source_snapshot
    )
    receipts.append(receipt)

    guard_start = source.index(
        "        if (\n"
        '            float(ppo_metrics["sampled_hidden_replay_max_abs_error"]) > 1.0e-6'
    )
    guard_end = source.index("        after, optimizer = training.adam_step(", guard_start)
    old_guard = source[guard_start:guard_end]
    diagnostic = '''        allowed_reset_keys = [
            "action_bias", "action_weight", "hidden_bias", "obs_weight"
        ]
        observed_reset_keys = sorted(
            key for key, value in reset_gradient_max.items() if value > 0.0
        )
        original_guard_checks = {
            "hidden_replay_at_most_1e_6":
                float(ppo_metrics["sampled_hidden_replay_max_abs_error"]) <= 1.0e-6,
            "predictor_stored_successor_count_exact":
                int(predictor_metrics["stored_successor_transition_count"]) == expected_stored,
            "predictor_stored_successor_count_positive": expected_stored > 0,
            "prefix_anchor_selected_elements_exact":
                int(anchor_metrics["selected_elements"]) == v29.EXPECTED_ANCHOR_ELEMENTS,
            "full_action_teacher_selected_elements_exact":
                int(teacher_metrics["selected_elements"]) == selected_elements,
            "full_action_teacher_selected_rows_exact": selected_rows == 22,
            "full_action_teacher_selected_elements_positive": selected_elements > 0,
            "prefix_anchor_allowed_gradients_positive":
                all(anchor_gradient_max[key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS),
            "prefix_anchor_forbidden_gradients_zero":
                all(anchor_gradient_max[key] == 0.0 for key in v29.NON_ANCHOR_GRADIENT_KEYS),
            "full_action_teacher_allowed_gradients_positive":
                all(teacher_gradient_max[key] > 0.0 for key in v29.ANCHOR_GRADIENT_KEYS),
            "full_action_teacher_forbidden_gradients_zero":
                all(teacher_gradient_max[key] == 0.0 for key in v29.NON_ANCHOR_GRADIENT_KEYS),
            "first_tick_sample_count_exact": int(reset_metrics["sample_count"]) == 44,
            "first_tick_selected_elements_exact":
                int(reset_metrics["selected_elements"]) == 616,
            "first_tick_nonzero_gradient_leaf_set_exact":
                observed_reset_keys == allowed_reset_keys,
            "first_tick_forbidden_gradients_zero": all(
                reset_gradient_max[key] == 0.0
                for key in reset_gradient_max
                if key not in set(allowed_reset_keys)
            ),
        }
        failed_original = sorted(
            name for name, passed in original_guard_checks.items() if not passed
        )
        finite_preupdate = training.finite_tree({
            "ppo_loss": ppo_loss,
            "ppo_metrics": ppo_metrics,
            "predictor_loss": predictor_loss,
            "predictor_metrics": predictor_metrics,
            "anchor_loss": anchor_loss,
            "anchor_metrics": anchor_metrics,
            "teacher_loss": teacher_loss,
            "teacher_metrics": teacher_metrics,
            "reset_loss": reset_loss,
            "reset_metrics": reset_metrics,
            "ppo_gradients": ppo_gradients,
            "predictor_gradients": predictor_gradients,
            "anchor_gradients": anchor_gradients,
            "teacher_gradients": teacher_gradients,
            "reset_gradients": reset_gradients,
            "combined_gradients": gradients,
        })
        attribution_complete = bool(failed_original) and bool(finite_preupdate)
        only_allowed_reset_support_changed = failed_original == [
            "first_tick_nonzero_gradient_leaf_set_exact"
        ] and original_guard_checks["first_tick_forbidden_gradients_zero"]
        result = {
            "schema_version": "winner_v58a.guard_failure_attribution_result.v1",
            "status": (
                "PASS_WINNER_V58A_GUARD_FAILURE_ATTRIBUTION"
                if attribution_complete
                else "HOLD_WINNER_V58A_GUARD_FAILURE_ATTRIBUTION"
            ),
            "decision": (
                "AUTHORIZE_OVERSTRICT_GUARD_RETRY_PREREGISTRATION_ONLY"
                if attribution_complete and only_allowed_reset_support_changed
                else "DO_NOT_RETRY_WINNER_V58"
            ),
            "classification": (
                "ALLOWED_FIRST_TICK_GRADIENT_SUPPORT_CHANGED"
                if only_allowed_reset_support_changed
                else "OTHER_OR_INCOMPLETE_PREUPDATE_GUARD_FAILURE"
            ),
            "checks": {
                "source_count_476_exact": True,
                "rollout_index_476_exact": rollout_update_index == 476,
                "would_complete_477_exact": completed_updates == 477,
                "all_original_guard_predicates_reported":
                    len(original_guard_checks) == 15,
                "at_least_one_original_guard_predicate_failed": bool(failed_original),
                "all_preupdate_values_finite": bool(finite_preupdate),
                "optimizer_count_unchanged_at_476":
                    int(np.asarray(optimizer["count"])) == 476,
            },
            "failed_checks": [],
            "original_guard_checks": original_guard_checks,
            "failed_original_guard_predicates": failed_original,
            "metrics": {
                "sampled_hidden_replay_max_abs_error":
                    float(ppo_metrics["sampled_hidden_replay_max_abs_error"]),
                "expected_stored_successor_transitions": expected_stored,
                "observed_stored_successor_transitions":
                    int(predictor_metrics["stored_successor_transition_count"]),
                "selected_anchor_elements": int(anchor_metrics["selected_elements"]),
                "selected_teacher_rows": selected_rows,
                "selected_teacher_elements": selected_elements,
                "selected_reset_samples": int(reset_metrics["sample_count"]),
                "selected_reset_elements": int(reset_metrics["selected_elements"]),
                "reset_gradient_max_abs": reset_gradient_max,
                "observed_nonzero_reset_gradient_leaves": observed_reset_keys,
                "allowed_reset_gradient_leaves": allowed_reset_keys,
                "anchor_gradient_max_abs": anchor_gradient_max,
                "teacher_gradient_max_abs": teacher_gradient_max,
                "combined_gradient_max_abs": common.tree_max_abs(gradients),
                "ppo_loss": float(ppo_loss),
                "predictor_loss": float(predictor_loss),
                "anchor_loss": float(anchor_loss),
                "full_action_teacher_loss": float(teacher_loss),
                "first_tick_teacher_loss": float(reset_loss),
                "first_tick_raw_mse": float(reset_metrics["raw_reset_mse"]),
                "first_tick_quantized_mse": float(reset_metrics["quantized_reset_mse"]),
                "first_tick_pitch_rms": float(reset_metrics["pitch_rms"]),
                "first_tick_nonpitch_rms": float(reset_metrics["nonpitch_rms"]),
            },
            "execution": {
                "rollout_update_indices": [476],
                "scheduled_episode_slots": 20_000,
                "optimizer_updates": 0,
                "formal_support_cells": 0,
                "locomotion_steps": 0,
                "robot_or_rdk_access": 0,
            },
            "authority": {
                "robot_clearance": False,
                "retry_executed": False,
                "formal_support_gate_executed": False,
                "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
                "pass_authorizes_only": "a separate retry preregistration when the sole failure is the allowed-gradient nonzero guard",
            },
        }
        result["failed_checks"] = sorted(
            name for name, passed in result["checks"].items() if not passed
        )
        if result["failed_checks"]:
            result["status"] = "HOLD_WINNER_V58A_GUARD_FAILURE_ATTRIBUTION"
            result["decision"] = "DO_NOT_RETRY_WINNER_V58"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\\n",
            encoding="utf-8",
        )
        print(result["status"])
        return 0

'''
    source = source[:guard_start] + diagnostic + source[guard_end:]
    receipts.append(
        {
            "old_sha256": hashlib.sha256(old_guard.encode()).hexdigest(),
            "new_sha256": hashlib.sha256(diagnostic.encode()).hexdigest(),
            "replacement_count": 1,
        }
    )
    replace("Winner-v58", "Winner-v58a", source.count("Winner-v58"))
    compile(source, "winner_v58a_guard_failure_attribution.py", "exec")
    return source, receipts


def _snapshot_manifest() -> list[dict[str, Any]]:
    import winner_v22_normalized_predictor_v2 as v22v2

    files = sorted((INTERRUPTED_ROOT / "snapshots").glob("*.npz"))
    expected = list(range(455, 477))
    observed: list[int] = []
    rows: list[dict[str, Any]] = []
    for path in files:
        snapshot = v22v2.load_snapshot(path)
        metadata = snapshot["metadata"]
        completed = int(metadata.get("completed_updates", -1))
        observed.append(completed)
        if (
            metadata.get("stage") != "integrated_first_tick_teacher_joint_stage2"
            or metadata.get("source_completed_updates") != 454
            or int(snapshot["optimizer"]["count"]) != completed
            or metadata.get("formal_support_cells") != 0
            or metadata.get("robot_or_rdk_access") != 0
        ):
            raise ValueError(f"Winner-v58 interrupted snapshot changed: {path}")
        rows.append(
            {
                "completed_updates": completed,
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    if observed != expected:
        raise ValueError(
            f"Winner-v58 interrupted snapshot chain changed: {observed!r}"
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v58a evidence: {path}")
    if not SOURCE_SNAPSHOT.is_file() or sha256(SOURCE_SNAPSHOT) != EXPECTED_SOURCE_SHA256:
        raise ValueError("Winner-v58a source snapshot changed")
    if not STDERR_LOG.is_file() or "changed at 477" not in STDERR_LOG.read_text(
        encoding="utf-8"
    ):
        raise ValueError("Winner-v58 interruption log changed")
    v58 = json.loads(V58_PREREG.read_text(encoding="utf-8"))
    v57 = json.loads(V57_RESULT.read_text(encoding="utf-8"))
    if (
        v58.get("status")
        != "PREREGISTERED_WINNER_V58_INTEGRATED_FIRST_TICK_TEACHER_TRAINING"
        or v58.get("decision")
        != "AUTHORIZE_ONE_100_UPDATE_INTEGRATED_FIRST_TICK_TEACHER_ARM_ONLY"
        or v57.get("status")
        != "PASS_WINNER_V57_FIRST_TICK_TEACHER_ONE_UPDATE_CPU_PROOF"
    ):
        raise ValueError("Winner-v58a source authority changed")
    snapshots = _snapshot_manifest()
    transformed, receipts = transformed_source()
    sources = dict(v58["sources"])
    for name, path in CUSTOM_SOURCES.items():
        sources[name] = {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
    payload = {
        "schema_version": "winner_v58a.guard_failure_attribution_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V58A_GUARD_FAILURE_ATTRIBUTION",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_WINNER_V58_GUARD_ATTRIBUTION_ONLY",
        "interruption": {
            "failed_before_optimizer_update": 477,
            "last_committed_update": 476,
            "stderr": {
                "path": str(STDERR_LOG),
                "bytes": STDERR_LOG.stat().st_size,
                "sha256": sha256(STDERR_LOG),
            },
            "snapshot_chain": snapshots,
        },
        "source_checkpoint": {
            "snapshot": snapshots[-1],
            "graph": v58["source_checkpoint"]["graph"],
            "parent_v57_snapshot_sha256": v57["snapshot"]["sha256"],
        },
        "teacher_checkpoint": v58["teacher_checkpoint"],
        "objective": v58["objective"],
        "diagnostic": {
            "source_completed_updates": 476,
            "rollout_update_index": 476,
            "would_complete_update": 477,
            "environments": 80,
            "ticks_per_environment": 250,
            "optimizer_updates": 0,
            "all_original_guard_predicates_reported": True,
        },
        "execution_now": {
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "transformation": {
            "base_v58_transformed_source_sha256": v58["transformation"][
                "transformed_source_sha256"
            ],
            "transformed_source_sha256": hashlib.sha256(
                transformed.encode()
            ).hexdigest(),
            "replacements": receipts,
            "replacement_groups": len(receipts),
        },
        "selection_rule": {
            "if_only_allowed_first_tick_gradient_support_changed": (
                "authorize only a separately preregistered retry with forbidden-gradient locality retained"
            ),
            "otherwise": "do not retry Winner-v58",
            "no_metric_or_coefficient_search": True,
        },
        "authority": {
            "robot_clearance": False,
            "diagnostic_authorized": True,
            "retry_authorized": False,
            "formal_support_gate_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v58a guard-failure attribution preregistration",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Interrupted source / diagnostic rollout: `476 / 476`",
                "- Would-complete update: `477`",
                "- Snapshot chain: `455..476` (`22` atomic snapshots)",
                "- Optimizer updates / support cells / robot access: `0 / 0 / 0`",
                "- Retry authorization: `false`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
