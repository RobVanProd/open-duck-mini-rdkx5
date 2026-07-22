#!/usr/bin/env python3
"""Preregister one read-only residual-teacher diagnostic after Winner-v76."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v77_residual_teacher_causal_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V77_RESIDUAL_TEACHER_CAUSAL_PREREGISTRATION_20260722.md"
V76_RESULT = ANALYSIS / "winner_v76_integrated_support_gate_result.json"
V76_RESULT_SHA256 = "19e71696f223b2585f80457095cbdf577d91846c6cf16c2bb739c0ef5fa44737"
BASE_RUNNER = ROOT / "tools/run_winner_v62_residual_teacher_causal.py"


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
            f"Winner-v77 transform changed: expected {count}, found {actual}: {old!r}"
        )
    return source.replace(old, new)


def transformed_source() -> tuple[str, str]:
    source = BASE_RUNNER.read_text(encoding="utf-8")
    for old, new in (
        ("Winner-v62", "Winner-v77"),
        ("winner_v62", "winner_v77"),
        ("WINNER_V62", "WINNER_V77"),
        ("winner_v61", "winner_v76"),
        ("WINNER_V61", "WINNER_V76"),
        ("winner_v60", "winner_v75"),
        ("v61", "v76"),
        ("V61", "V76"),
        ("V60", "V75"),
    ):
        count = source.count(old)
        if count <= 0:
            raise ValueError(f"Winner-v77 transform token absent: {old}")
        source = source.replace(old, new)
    source = replace_exact(
        source,
        'V75_RESULT = ANALYSIS / "winner_v75_integrated_numeric_guard_training_result.json"',
        'V75_RESULT = ANALYSIS / "winner_v75_functional_numeric_guard_continuation_result.json"',
    )
    source = replace_exact(
        source,
        'V75_PREREGISTRATION = ANALYSIS / "winner_v75_integrated_numeric_guard_training_preregistration.json"',
        'V75_PREREGISTRATION = ANALYSIS / "winner_v75_functional_numeric_guard_continuation_preregistration.json"',
    )
    source = replace_exact(
        source,
        'or len(value.get("frozen_source", {}).get("failure_pairs", [])) != 13',
        'or len(value.get("frozen_source", {}).get("failure_pairs", [])) != 9',
    )
    source = replace_exact(source, '"failed_pair_count": 13,', '"failed_pair_count": 9,')
    source = replace_exact(source, '"diagnostic_cells": 52,', '"diagnostic_cells": 36,')
    source = replace_exact(
        source,
        '"formal_graph_cells_must_match_v76_bit_exact": True,',
        '"formal_graph_cells_must_match_v76_bit_exact": True,',
    )
    source = replace_exact(
        source,
        'V75_RESULT.read_text(encoding="utf-8"))',
        'V75_RESULT.read_text(encoding="utf-8"))',
        count=1,
    )
    source = replace_exact(
        source,
        'V75_PREREGISTRATION.read_text(encoding="utf-8"))',
        'V75_PREREGISTRATION.read_text(encoding="utf-8"))',
        count=1,
    )
    source = replace_exact(
        source,
        'if snapshot["metadata"]["completed_updates"] != 554:',
        'if snapshot["metadata"]["completed_updates"] != 655:',
    )
    source = replace_exact(source, '"exact_52_cells": len(all_arm_cells) == 52,', '"exact_36_cells": len(all_arm_cells) == 36,')
    source = replace_exact(
        source,
        '"exact_13_cells_per_arm": all(\n            sum(arm in row["arms"] for row in rows) == 13 for arm in ARMS\n        ),',
        '"exact_9_cells_per_arm": all(\n            sum(arm in row["arms"] for row in rows) == 9 for arm in ARMS\n        ),',
    )
    source = replace_exact(
        source,
        '"all_13_graph_cells_bit_exact_to_v76": all(',
        '"all_9_graph_cells_bit_exact_to_v76": all(',
    )
    source = replace_exact(
        source,
        '"all_13_source_graph_cells_fail": support_counts["graph"] == 0,',
        '"all_9_source_graph_cells_fail": support_counts["graph"] == 0,',
    )
    source = replace_exact(
        source,
        '"exact_13_failed_pair_classifications": len(classifications) == 13,',
        '"exact_9_failed_pair_classifications": len(classifications) == 9,',
    )
    source = replace_exact(source, '"update": 554,', '"update": 655,')
    source = replace_exact(
        source,
        'f"- First/post-first pitch RMS means: `{result[\'findings\'][\'first_tick_pitch_rms_mean\']} / {result[\'findings\'][\'post_first_tick_pitch_rms_mean\']}`",',
        'f"- First/post-first pitch RMS means: `{result[\'findings\'][\'first_tick_pitch_rms_mean\']} / {result[\'findings\'][\'post_first_tick_pitch_rms_mean\']}`",',
    )
    transformed_hash = hashlib.sha256(source.encode()).hexdigest()
    compile(source, "winner_v77_residual_teacher_causal.py", "exec")
    return source, transformed_hash


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v77 contract: {path}")
    formal = json.loads(V76_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V76_RESULT) != V76_RESULT_SHA256
        or formal.get("status") != "HOLD_WINNER_V76_INTEGRATED_SUPPORT_GATE"
        or formal.get("decision") != "DO_NOT_SELECT_WINNER_V75_DEPLOYMENT_POLICY"
        or formal.get("selected_checkpoint") is not None
        or formal.get("failed_checks") != ["all_248_main_cells_pass"]
        or formal.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v76 hold identity changed")
    final = next(row for row in formal["checkpoint_results"] if row["label"] == "final")
    failures = [row for row in final["core_model_plant_cells"] if not row["support_pass"]]
    pairs = [
        {"configuration_id": row["configuration_id"], "plant": row["plant"]}
        for row in failures
    ]
    expected_pairs = [
        {"configuration_id": "COM_X_NEG", "plant": "P31_34_PITCH_WITH_P30_NONPITCH"},
        {"configuration_id": "COM_CORNER_01", "plant": "P30_ALL_JOINT"},
        {"configuration_id": "COM_CORNER_01", "plant": "P31_34_PITCH_WITH_P30_NONPITCH"},
        {"configuration_id": "COM_CORNER_03", "plant": "P30_ALL_JOINT"},
        {"configuration_id": "COM_CORNER_03", "plant": "P31_34_PITCH_WITH_P30_NONPITCH"},
        {"configuration_id": "COM_CORNER_07", "plant": "P30_ALL_JOINT"},
        {"configuration_id": "COM_CORNER_07", "plant": "P31_34_PITCH_WITH_P30_NONPITCH"},
        {"configuration_id": "DISCOVERY_03", "plant": "P30_ALL_JOINT"},
        {"configuration_id": "DISCOVERY_03", "plant": "P31_34_PITCH_WITH_P30_NONPITCH"},
    ]
    if pairs != expected_pairs or any(row["terminal"] is None for row in failures):
        raise ValueError("Winner-v76 final failure population changed")
    transformed, transformed_hash = transformed_source()
    source_paths = {
        "builder": Path("tools/build_winner_v77_residual_teacher_causal_preregistration.py"),
        "runner": Path("tools/run_winner_v77_residual_teacher_causal.py"),
        "tests": Path("tests/test_winner_v77_residual_teacher_causal.py"),
        "v76_result": Path("outputs/analysis/winner_v76_integrated_support_gate_result.json"),
        "v76_preregistration": Path("outputs/analysis/winner_v76_integrated_support_gate_preregistration.json"),
        "v76_builder": Path("tools/build_winner_v76_integrated_support_gate_preregistration.py"),
        "v75_result": Path("outputs/analysis/winner_v75_functional_numeric_guard_continuation_result.json"),
        "v75_preregistration": Path("outputs/analysis/winner_v75_functional_numeric_guard_continuation_preregistration.json"),
        "intervention_mechanics": Path("tools/run_winner_v48_static_teacher_causal_diagnostic.py"),
        "prior_causal_result": Path("outputs/analysis/winner_v62_residual_teacher_causal_result.json"),
        "teacher_table": Path("outputs/analysis/winner_v42_static_target_teacher_table_result.json"),
        "base_runner": Path("tools/run_winner_v62_residual_teacher_causal.py"),
        "base_gate_runner": Path("tools/run_winner_v12_calibrator_support_gate.py"),
        "base_gate_preregistration": Path("outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"),
        "variable_configuration_domain": Path("outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v77.residual_teacher_causal_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V77_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC",
        "decision": "AUTHORIZE_ONE_READ_ONLY_36_CELL_CPU_DIAGNOSTIC_ONLY",
        "causal_question": (
            "After isolated persistent-teacher continuation, does the frozen full teacher "
            "still rescue every final Winner-v76 failure, and is the mismatch still "
            "localized to pitch output?"
        ),
        "frozen_source": {
            "v76_result_sha256": V76_RESULT_SHA256,
            "checkpoint_label": "final",
            "completed_updates": 655,
            "snapshot_sha256": final["checkpoint_sha256"],
            "onnx_sha256": final["onnx_sha256"],
            "formal_failed_cells": 9,
            "failure_pairs": pairs,
        },
        "frozen_arms": {
            "graph": "unchanged Winner-v75 final graph",
            "full_teacher": "replace all 14 actor outputs with the frozen V42 target before the unchanged graph bound",
            "pitch_teacher": "replace indices [2,3,4,11,12,13] with the frozen V42 target before the unchanged graph bound",
            "nonpitch_zero": "replace indices [0,1,5,6,7,8,9,10] with zero before the unchanged graph bound",
            "response_state": "retain graph h_out exactly, matching reviewed V48/V54/V62 intervention semantics",
        },
        "frozen_execution": {
            "checkpoint_count": 1,
            "failed_pair_count": 9,
            "arm_count": 4,
            "diagnostic_cells": 36,
            "ticks_per_cell": 250,
            "formal_graph_cells_must_match_v76_bit_exact": True,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "classification": {
            "teacher_insufficient": "full_teacher fails",
            "either_single_intervention_rescues": "pitch_teacher and nonpitch_zero both pass",
            "pitch_output_causal": "pitch_teacher passes and nonpitch_zero fails",
            "nonpitch_output_causal": "nonpitch_zero passes and pitch_teacher fails",
            "pitch_nonpitch_interaction": "full_teacher passes and both single interventions fail",
            "report_first_tick_and_post_first_tick_alignment_separately": True,
            "no_posthoc_threshold_or_arm_change": True,
        },
        "pass_rule": {
            "exact_36_cells": True,
            "all_9_graph_cells_bit_exact_to_v76": True,
            "exact_9_failed_pair_classifications": True,
            "all_previous_action_chains_exact": True,
            "all_jax_onnx_hidden_errors_at_most_1e_7": True,
            "all_values_finite": True,
        },
        "execution_now": {
            "diagnostic_cells": 0,
            "optimizer_updates": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "transformation": {
            "base_v62_runner_lf_sha256": lf_sha256(BASE_RUNNER),
            "transformed_source_sha256": transformed_hash,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "result_authorizes_only": "a separately preregistered mechanism chosen from the frozen classification",
        },
    }
    args.output.write_text(json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v77 residual-teacher causal preregistration",
                "",
                "- Population: `9 exact failed pairs x 4 arms = 36 cells`",
                "- Checkpoint: exact Winner-v75 final update `655`",
                "- Alignment: tick zero and post-tick-zero reported separately",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
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
