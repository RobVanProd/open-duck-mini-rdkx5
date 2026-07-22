#!/usr/bin/env python3
"""Bind the unchanged reviewed 248+64-cell support gate to Winner-v84."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import build_winner_v76_integrated_support_gate_preregistration as v76  # noqa: E402


ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v85_integrated_support_gate_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V85_INTEGRATED_SUPPORT_GATE_PREREGISTRATION_20260722.md"
TRAINING_RESULT = (
    ANALYSIS / "winner_v84_negative_gradient_pitch_head_continuation_result.json"
)
TRAINING_PREREGISTRATION = (
    ANALYSIS / "winner_v84_negative_gradient_pitch_head_continuation_preregistration.json"
)
BASE_PREREGISTRATION = ANALYSIS / "winner_v12_full_calibrator_training_preregistration.json"
TRAINING_RESULT_SHA256 = "f720361087d4188b7d65a3da76e53bb93c1fd4774918dd4d4da7b10516764bae"
TEACHER_SNAPSHOT_SHA256 = "ddc8c4b905bb9acac2d7d48c3e9c1f0c0ca0173a1ba21f375740b051bc48c806"
HALF_UPDATE = 705
FINAL_UPDATE = 755


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


def replace_exact(
    source: str,
    old: str,
    new: str,
    receipts: list[dict[str, Any]],
    *,
    count: int,
) -> str:
    actual = source.count(old)
    if actual != count:
        raise ValueError(
            f"Winner-v85 transform changed: expected {count}, found {actual}: {old!r}"
        )
    receipts.append(
        {
            "old_sha256": hashlib.sha256(old.encode()).hexdigest(),
            "new_sha256": hashlib.sha256(new.encode()).hexdigest(),
            "replacement_count": actual,
        }
    )
    return source.replace(old, new)


def replace_region(source: str, start: str, end: str, replacement: str) -> str:
    if source.count(start) != 1 or source.count(end) != 1:
        raise ValueError(f"Winner-v85 region markers changed: {start!r} / {end!r}")
    left = source.index(start)
    right = source.index(end, left)
    return source[:left] + replacement + source[right:]


VALIDATE_SNAPSHOT = '''def _validate_snapshot(snapshot: Mapping[str, Any], *, expected_stage: str) -> None:
    if smoke is None or training is None or v21 is None:
        raise AssertionError("Winner-v85 snapshot dependencies were not loaded")
    if _TRAINING is None:
        raise AssertionError("Winner-v85 training evidence was not loaded")
    if set(snapshot) != {"parameters", "optimizer", "metadata", "target_mean", "target_std"}:
        raise ValueError("Winner-v85 checkpoint state schema changed")
    metadata = snapshot["metadata"]
    update = metadata.get("completed_updates")
    if (
        metadata.get("schema_version") != SNAPSHOT_SCHEMA
        or metadata.get("stage") != expected_stage
        or update not in {705, 755}
        or metadata.get("source_completed_updates") != 675
        or metadata.get("source_snapshot_sha256") != _TRAINING["source_snapshot"]["sha256"]
        or metadata.get("teacher_snapshot_sha256") != "ddc8c4b905bb9acac2d7d48c3e9c1f0c0ca0173a1ba21f375740b051bc48c806"
        or metadata.get("objective") != _TRAINING["objective"]
        or metadata.get("root_seed") != 120120
        or metadata.get("learning_rate") != 0.0001
        or metadata.get("optimizer_m_and_v_transition") != "all elements bit-exact preserved"
        or metadata.get("formal_support_cells") != 0
        or metadata.get("locomotion_steps") != 0
        or metadata.get("robot_or_rdk_access") != 0
        or int(np.asarray(snapshot["optimizer"]["count"])) != update
        or set(snapshot["optimizer"]["m"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(snapshot["optimizer"]["v"]) != set(v21.JOINT_TRAINABLE_KEYS)
        or set(v21.joint_trainable_parameters(snapshot["parameters"])) != set(v21.JOINT_TRAINABLE_KEYS)
    ):
        raise ValueError("Winner-v85 checkpoint metadata changed")
    for name in ("target_mean", "target_std"):
        value = np.asarray(snapshot[name])
        if value.shape != (50,) or value.dtype != np.dtype(np.float32) or not np.all(np.isfinite(value)):
            raise ValueError(f"Winner-v85 {name} schema changed")
    if np.any(np.asarray(snapshot["target_std"]) <= 0.0):
        raise ValueError("Winner-v85 target_std is not positive")
    for tree in (snapshot["parameters"], snapshot["optimizer"]["m"], snapshot["optimizer"]["v"]):
        if not all(np.all(np.isfinite(np.asarray(value))) for value in tree.values()):
            raise ValueError("Winner-v85 checkpoint contains nonfinite arrays")


'''


VALIDATE_PREREGISTRATION = '''def validate_preregistration(value: Mapping[str, Any]) -> None:
    if _TRAINING is None:
        raise AssertionError("Winner-v85 training result was not loaded")
    if (
        value.get("schema_version") != "winner_v85.integrated_support_gate_preregistration.v1"
        or value.get("status") != "PREREGISTERED_WINNER_V85_INTEGRATED_SUPPORT_GATE"
        or value.get("decision") != "AUTHORIZE_ONE_FROZEN_WINNER_V85_248_CELL_GATE_ONLY"
        or value.get("execution_now") != {
            "formal_support_cells": 0,
            "heldout_repeat_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        }
        or value.get("pass_rule") != {
            "all_124_main_cells_at_both_checkpoints": True,
            "all_32_heldout_repeats_at_both_checkpoints": True,
            "all_16_heldout_contexts_separate_at_both_checkpoints": True,
            "learned_prediction_beats_constant_per_plant": True,
            "closest_checkpoint_selection": False,
        }
        or value.get("selection_rule") != {
            "selected_only_if_every_pass_rule_is_true_at_both_checkpoints": True,
            "selected_checkpoint_if_pass": "final",
            "selected_update_if_pass": 755,
            "selection_basis": "fixed terminal endpoint after half/final persistence",
            "metric_ranking_or_closest_result": False,
            "no_selection_if_hold": True,
        }
    ):
        raise ValueError("Winner-v85 preregistration identity changed")
    gate = value.get("future_frozen_support_gate", {})
    if (
        gate.get("cells_per_checkpoint") != 124
        or gate.get("checkpoint_labels") != ["half", "final"]
        or gate.get("duration_ticks") != 250
        or gate.get("all_cells_at_both_checkpoints_must_pass") is not True
        or gate.get("selection_by_closest_result") is not False
        or gate.get("predictor_scoring", {}).get("head_output_coordinates") != "normalized"
        or gate.get("predictor_scoring", {}).get("physical_support_population_thresholds_seeds_unchanged") is not True
    ):
        raise ValueError("Winner-v85 gate dimensions changed")
    bound = value.get("training_artifact", {})
    expected = {
        "source_snapshot": _TRAINING["source_snapshot"],
        "source_graph": _TRAINING["source_graph"],
        "objective": _TRAINING["objective"],
        "teacher_snapshot_sha256": "ddc8c4b905bb9acac2d7d48c3e9c1f0c0ca0173a1ba21f375740b051bc48c806",
    }
    if any(bound.get(name) != item for name, item in expected.items()):
        raise ValueError("Winner-v85 training binding changed")
    if (
        bound.get("result", {}).get("sha256") != sha256(TRAINING_RESULT)
        or bound.get("result", {}).get("bytes") != TRAINING_RESULT.stat().st_size
    ):
        raise ValueError("Winner-v85 training-result receipt changed")
    sources = value.get("sources")
    if not isinstance(sources, dict):
        raise ValueError("Winner-v85 source manifest is absent")
    for name, item in sources.items():
        if set(item) != {"hash_mode", "path", "sha256"} or item["hash_mode"] != "lf" or lf_sha256(ROOT / item["path"]) != item["sha256"]:
            raise ValueError(f"Winner-v85 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v85 source manifest changed")


'''


def transformed_source() -> tuple[str, list[dict[str, Any]]]:
    source, _ = v76.transformed_source()
    receipts: list[dict[str, Any]] = []
    for old, new, count in (
        ("Winner-v76", "Winner-v85", 26),
        ("winner_v76", "winner_v85", 3),
        ("WINNER_V76", "WINNER_V85", 6),
        (
            "winner_v75_functional_numeric_guard_continuation_result.json",
            "winner_v84_negative_gradient_pitch_head_continuation_result.json",
            1,
        ),
        (
            "winner_v75_functional_numeric_guard_continuation_preregistration.json",
            "winner_v84_negative_gradient_pitch_head_continuation_preregistration.json",
            1,
        ),
        (
            "PASS_WINNER_V75_FUNCTIONAL_NUMERIC_GUARD_CONTINUATION",
            "PASS_WINNER_V84_NEGATIVE_GRADIENT_PITCH_HEAD_CONTINUATION",
            1,
        ),
        (
            "AUTHORIZE_UNCHANGED_PERSISTENCE_GATE_FOR_COUNTS_605_AND_655_ONLY",
            "AUTHORIZE_UNCHANGED_PERSISTENCE_GATE_FOR_COUNTS_705_AND_755_ONLY",
            1,
        ),
        (
            "SELECT_WINNER_V75_FINAL_FOR_OFFLINE_RUNTIME_FREEZE_ONLY",
            "SELECT_WINNER_V84_FINAL_FOR_OFFLINE_RUNTIME_FREEZE_ONLY",
            1,
        ),
        (
            "DO_NOT_SELECT_WINNER_V75_DEPLOYMENT_POLICY",
            "DO_NOT_SELECT_WINNER_V84_DEPLOYMENT_POLICY",
            1,
        ),
        ("605", "705", 3),
        ("655", "755", 7),
        ("602", "675", 1),
        (
            "fresh_moment_safeguarded_teacher_joint_stage2",
            "negative_gradient_pitch_action_head_continuation",
            1,
        ),
        (
            "snapshot_fresh_moment_safeguarded_update_",
            "snapshot_negative_gradient_pitch_head_update_",
            1,
        ),
        ("winner_v71_", "winner_v84_", 1),
        ("Winner-v71 does not authorize the gate", "Winner-v84 does not authorize the gate", 1),
    ):
        source = replace_exact(source, old, new, receipts, count=count)
    source = replace_region(source, "def _validate_snapshot", "def load_snapshot_for_reviewed_gate", VALIDATE_SNAPSHOT)
    source = replace_region(source, "def validate_preregistration", "def finalize_result", VALIDATE_PREREGISTRATION)
    compile(source, "winner_v85_integrated_support_gate.py", "exec")
    return source, receipts


def checkpoint(training: dict[str, Any], label: str, update: int) -> dict[str, Any]:
    snapshot = next(
        row for row in training["snapshot_manifest"] if row["completed_updates"] == update
    )
    persistent = next(
        row
        for row in training["persistent_checkpoints"]
        if row["label"] == label and row["completed_updates"] == update
    )
    return {"snapshot": snapshot, "graph": persistent["graph"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v85 contract: {path}")
    training = json.loads(TRAINING_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(TRAINING_RESULT) != TRAINING_RESULT_SHA256
        or training.get("status")
        != "PASS_WINNER_V84_NEGATIVE_GRADIENT_PITCH_HEAD_CONTINUATION"
        or training.get("decision")
        != "AUTHORIZE_UNCHANGED_PERSISTENCE_GATE_FOR_COUNTS_705_AND_755_ONLY"
        or training.get("failed_checks") != []
        or training.get("execution", {}).get("optimizer_updates") != 80
        or training.get("execution", {}).get("formal_support_cells") != 0
        or training.get("authority", {}).get("robot_clearance") is not False
        or [row.get("completed_updates") for row in training["persistent_checkpoints"]]
        != [HALF_UPDATE, FINAL_UPDATE]
    ):
        raise ValueError("Winner-v84 does not authorize Winner-v85 preregistration")
    base = json.loads(BASE_PREREGISTRATION.read_text(encoding="utf-8"))
    gate = json.loads(json.dumps(base["future_frozen_support_gate"]))
    if (
        gate.get("cells_per_checkpoint") != 124
        or gate.get("checkpoint_labels") != ["half", "final"]
        or gate.get("duration_ticks") != 250
        or gate.get("all_cells_at_both_checkpoints_must_pass") is not True
        or gate.get("selection_by_closest_result") is not False
    ):
        raise ValueError("reviewed support-gate definition changed")
    gate["predictor_scoring"] = {
        "head_output_coordinates": "normalized",
        "evaluated_coordinates": "raw through exact in-memory affine projection",
        "learned_error": "mean(square((prediction_raw - target_raw) / target_std))",
        "constant_error": "mean(square((target_mean - target_raw) / target_std))",
        "projection": {
            "auxiliary_hidden_weight": "normalized_weight * target_std",
            "auxiliary_action_weight": "normalized_weight * target_std",
            "auxiliary_bias": "normalized_bias * target_std + target_mean",
        },
        "physical_support_population_thresholds_seeds_unchanged": True,
        "checkpoint_and_onnx_bytes_unchanged": True,
    }
    transformed, receipts = transformed_source()
    source_paths = {
        "builder": Path("tools/build_winner_v85_integrated_support_gate_preregistration.py"),
        "gate_runner": Path("tools/run_winner_v85_integrated_support_gate.py"),
        "gate_tests": Path("tests/test_winner_v85_integrated_support_gate.py"),
        "training_result": TRAINING_RESULT.relative_to(ROOT),
        "training_preregistration": TRAINING_PREREGISTRATION.relative_to(ROOT),
        "training_runner": Path("tools/run_winner_v84_negative_gradient_pitch_head_continuation.py"),
        "v76_builder": Path("tools/build_winner_v76_integrated_support_gate_preregistration.py"),
        "v76_runner": Path("tools/run_winner_v76_integrated_support_gate.py"),
        "v53_reviewed_gate_runner": Path("tools/run_winner_v53_full_action_teacher_support_gate.py"),
        "base_gate_preregistration": Path(
            "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
        ),
        "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
        "calibrator_design": Path(
            "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
        ),
        "variable_configuration_domain": Path(
            "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
        ),
        "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
        "normalized_checkpoint": Path("patches/winner_v22_normalized_predictor_v2.py"),
        "coordinate_adapter": Path("patches/winner_v22_normalized_support_gate.py"),
        "joint_recurrent": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
        "runtime_observer": Path(
            "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"
        ),
        "canonical_p30_fit": Path(
            "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
        ),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    payload = {
        "schema_version": "winner_v85.integrated_support_gate_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V85_INTEGRATED_SUPPORT_GATE",
        "decision": "AUTHORIZE_ONE_FROZEN_WINNER_V85_248_CELL_GATE_ONLY",
        "causal_question": (
            "Does Winner-v84 preserve the complete inherited variable-configuration, "
            "plant, sensor, transport, context, predictor, and repeatability envelope "
            "at both original persistence checkpoints?"
        ),
        "binding_change_only": (
            "The reviewed Winner-v12 evaluator, 248-cell population, 64 repeats, "
            "thresholds, seeds, P30/P31-34 plants, and all-or-nothing rule are unchanged. "
            "Only exact Winner-v84 count-705/count-755 artifacts are bound read-only."
        ),
        "training_artifact": {
            "result": {
                "path": TRAINING_RESULT.relative_to(ROOT).as_posix(),
                "bytes": TRAINING_RESULT.stat().st_size,
                "sha256": sha256(TRAINING_RESULT),
            },
            "source_snapshot": training["source_snapshot"],
            "source_graph": training["source_graph"],
            "teacher_snapshot_sha256": TEACHER_SNAPSHOT_SHA256,
            "objective": training["objective"],
            "half": checkpoint(training, "half", HALF_UPDATE),
            "final": checkpoint(training, "final", FINAL_UPDATE),
        },
        "future_frozen_support_gate": gate,
        "execution_now": {
            "formal_support_cells": 0,
            "heldout_repeat_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "pass_rule": {
            "all_124_main_cells_at_both_checkpoints": True,
            "all_32_heldout_repeats_at_both_checkpoints": True,
            "all_16_heldout_contexts_separate_at_both_checkpoints": True,
            "learned_prediction_beats_constant_per_plant": True,
            "closest_checkpoint_selection": False,
        },
        "selection_rule": {
            "selected_only_if_every_pass_rule_is_true_at_both_checkpoints": True,
            "selected_checkpoint_if_pass": "final",
            "selected_update_if_pass": FINAL_UPDATE,
            "selection_basis": "fixed terminal endpoint after half/final persistence",
            "metric_ranking_or_closest_result": False,
            "no_selection_if_hold": True,
        },
        "transformation": {
            "base_v76_transformed_source_sha256": hashlib.sha256(
                v76.transformed_source()[0].encode()
            ).hexdigest(),
            "transformed_source_sha256": hashlib.sha256(transformed.encode()).hexdigest(),
            "replacements": receipts,
            "replacement_groups": len(receipts),
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "formal_support_gate_authorized": True,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "offline selection and asset freeze for separately authorized suspended Gate 5"
            ),
        },
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v85 integrated support-gate preregistration",
                "",
                "- Population: `124` main cells per checkpoint; `248` total",
                "- Repeats: `32` heldout cells per checkpoint; `64` total",
                "- Checkpoints: exact Winner-v84 counts `705 / 755`",
                "- Pass: every check at both checkpoints; no closest result",
                "- Selection after pass: fixed final endpoint at count `755`",
                "- Locomotion training / robot access in this gate: `0 / 0`",
                f"- Transformed source SHA-256: `{hashlib.sha256(transformed.encode()).hexdigest()}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
