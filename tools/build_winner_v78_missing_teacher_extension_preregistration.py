#!/usr/bin/env python3
"""Freeze one exact V42-method teacher extension for COM_CORNER_07."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v78_missing_teacher_extension_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V78_MISSING_TEACHER_EXTENSION_PREREGISTRATION_20260722.md"
V76_RESULT = ANALYSIS / "winner_v76_integrated_support_gate_result.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
V77B_INVALID = ANALYSIS / "winner_v77b_residual_teacher_causal_invalid_invocation.json"
V77_RESULT = ANALYSIS / "winner_v77_residual_teacher_causal_result.json"
CONFIGURATION_ID = "COM_CORNER_07"
PLANTS = ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"]
GRID_VALUES = [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0]
TARGETS = 729


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v78 contract: {path}")

    formal = json.loads(V76_RESULT.read_text(encoding="utf-8"))
    final = next(row for row in formal["checkpoint_results"] if row["label"] == "final")
    failures = [row for row in final["core_model_plant_cells"] if not row["support_pass"]]
    failed_ids = {row["configuration_id"] for row in failures}
    v42 = json.loads(V42_RESULT.read_text(encoding="utf-8"))
    teacher_ids = set(v42.get("teacher_table", {}))
    missing = sorted(failed_ids - teacher_ids)
    invalid = json.loads(V77B_INVALID.read_text(encoding="utf-8"))
    if (
        sha256(V76_RESULT)
        != "19e71696f223b2585f80457095cbdf577d91846c6cf16c2bb739c0ef5fa44737"
        or formal.get("status") != "HOLD_WINNER_V76_INTEGRATED_SUPPORT_GATE"
        or len(failures) != 9
        or missing != [CONFIGURATION_ID]
        or v42.get("status") != "PASS_WINNER_V42_STATIC_TARGET_TEACHER_TABLE"
        or invalid.get("status")
        != "INVALID_WINNER_V77B_MISSING_FROZEN_TEACHER_CONFIGURATION"
        or invalid.get("authority", {}).get("diagnostic_cells") != 0
        or invalid.get("failure", {}).get("result_written") is not False
        or V77_RESULT.exists()
    ):
        raise ValueError("Winner-v78 missing-teacher source identity changed")

    source_paths = {
        "builder": Path(
            "tools/build_winner_v78_missing_teacher_extension_preregistration.py"
        ),
        "runner": Path("tools/run_winner_v78_missing_teacher_extension.py"),
        "tests": Path("tests/test_winner_v78_missing_teacher_extension.py"),
        "v77b_invalid_invocation": Path(
            "outputs/analysis/winner_v77b_residual_teacher_causal_invalid_invocation.json"
        ),
        "v77b_correction": Path(
            "outputs/analysis/winner_v77b_population_authorization_correction.json"
        ),
        "v76_result": Path("outputs/analysis/winner_v76_integrated_support_gate_result.json"),
        "v42_result": Path(
            "outputs/analysis/winner_v42_static_target_teacher_table_result.json"
        ),
        "v42_preregistration": Path(
            "outputs/analysis/winner_v42_static_target_teacher_table_preregistration.json"
        ),
        "v42_runner": Path("tools/run_winner_v42_static_target_teacher_table.py"),
        "v41_runner": Path(
            "tools/run_winner_v41_static_equilibrium_target_feasibility.py"
        ),
        "v41_corrected_expansion": Path(
            "tools/run_winner_v41_v2_static_equilibrium_target_feasibility.py"
        ),
        "v34_reviewed_modules": Path(
            "tools/run_winner_v34_prefix_right_pitch_hard_intervention.py"
        ),
        "configuration_domain": Path(
            "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
        ),
        "calibrator_design": Path(
            "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
        ),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v78.missing_teacher_extension_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V78_MISSING_TEACHER_EXTENSION",
        "decision": "AUTHORIZE_ONE_CPU_ONLY_COM_CORNER_07_TEACHER_TABLE",
        "question": (
            "Does the unchanged Winner-v42 729-target equilibrium grid contain a shared "
            "two-plant full-horizon static target for the sole current failure "
            "configuration absent from the frozen teacher table?"
        ),
        "source_attribution": {
            "v76_result_sha256": sha256(V76_RESULT),
            "v76_final_failed_cells": 9,
            "v76_final_failed_configuration_ids": sorted(failed_ids),
            "v42_teacher_configuration_ids": sorted(teacher_ids),
            "missing_teacher_configuration_ids": missing,
            "v77b_invalid_invocation_sha256": sha256(V77B_INVALID),
        },
        "screen": {
            "configuration_ids": [CONFIGURATION_ID],
            "actuator_plants": PLANTS,
            "grid_values": GRID_VALUES,
            "targets_per_configuration": TARGETS,
            "maximum_candidate_plant_cells": TARGETS * len(PLANTS),
            "duration_ticks": 250,
            "selection": "unchanged Winner-v41 deterministic shared-target key",
            "target_semantics": "one selected time-invariant target for COM_CORNER_07",
        },
        "pass_rule": {
            "exact_1_configuration_table": True,
            "exact_729_targets": True,
            "exact_1458_candidate_plant_cells": True,
            "all_candidate_actions_graph_bounded": True,
            "selected_target_replay_exact": True,
            "configuration_has_a_shared_two_plant_support_target": True,
            "closest_result_selection": False,
        },
        "execution_now": {
            "configuration_tables": 0,
            "static_target_candidates": 0,
            "candidate_plant_cells": 0,
            "selected_target_replay_cells": 0,
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "runtime_static_target_or_action_wrapper_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately preregistered residual-teacher causal diagnostic",
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v78 missing-teacher extension preregistration",
                "",
                f"- Configuration: `{CONFIGURATION_ID}`",
                "- Grid / plants / maximum cells: `729 / 2 / 1,458`",
                "- Optimizer / locomotion / robot: `0 / 0 / 0`",
                "- Method and selection key: bit-for-bit inherited from Winner-v42/v41",
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
