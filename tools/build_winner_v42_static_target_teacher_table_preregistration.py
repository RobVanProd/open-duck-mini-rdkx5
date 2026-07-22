#!/usr/bin/env python3
"""Freeze one static-target teacher table over the exact 15-config failure set."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v42_static_target_teacher_table_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V42_STATIC_TARGET_TEACHER_TABLE_PREREGISTRATION_20260722.md"
V33_RESULT = ANALYSIS / "winner_v33_prefix_right_pitch_anchor_support_gate_result.json"
V41_RESULT = ANALYSIS / "winner_v41_v2_static_equilibrium_target_feasibility_result.json"

CONFIGURATION_IDS = [
    "COM_X_NEG", "COM_CORNER_00", "COM_CORNER_01", "COM_CORNER_02",
    "COM_CORNER_03", "OPTIONAL_AGGREGATE_HEAVY_AFT", "DISCOVERY_02",
    "DISCOVERY_03", "DISCOVERY_06", "DISCOVERY_09", "DISCOVERY_10",
    "HELDOUT_04", "HELDOUT_07", "HELDOUT_09", "HELDOUT_15",
]

SOURCES = {
    "builder": Path("tools/build_winner_v42_static_target_teacher_table_preregistration.py"),
    "runner": Path("tools/run_winner_v42_static_target_teacher_table.py"),
    "runner_tests": Path("tests/test_winner_v42_static_target_teacher_table.py"),
    "preregistration_tests": Path(
        "tests/test_winner_v42_static_target_teacher_table_preregistration.py"
    ),
    "result_importer": Path("tools/import_winner_v42_static_target_teacher_table.py"),
    "result_importer_tests": Path(
        "tests/test_winner_v42_static_target_teacher_table_import.py"
    ),
    "workflow": Path(".github/workflows/winner-v42-static-target-teacher-table.yml"),
    "winner_v33_result": Path(
        "outputs/analysis/winner_v33_prefix_right_pitch_anchor_support_gate_result.json"
    ),
    "winner_v41_result": Path(
        "outputs/analysis/winner_v41_v2_static_equilibrium_target_feasibility_result.json"
    ),
    "winner_v41_base_runner": Path(
        "tools/run_winner_v41_static_equilibrium_target_feasibility.py"
    ),
    "winner_v41_corrected_runner": Path(
        "tools/run_winner_v41_v2_static_equilibrium_target_feasibility.py"
    ),
    "winner_v34_failure_set": Path(
        "tools/run_winner_v34_prefix_right_pitch_hard_intervention.py"
    ),
    "reviewed_mirror_basis": Path("patches/winner_v16_support_action_direction.py"),
    "configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
    "calibrator_design": Path(
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
    ),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "environment_preparation": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "runtime_observer": Path(
        "artifacts/runtime_handoff/rdkx5_native_20260719/observer/winner_v2_contract.py"
    ),
    "canonical_p30_fit": Path(
        "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
    ),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def v33_failure_summary(value: dict[str, Any]) -> tuple[dict[str, int], set[str]]:
    rows = value.get("checkpoint_results")
    if not isinstance(rows, list) or [row.get("label") for row in rows] != [
        "half", "final",
    ]:
        raise ValueError("Winner-v33 checkpoint set changed")
    counts: dict[str, int] = {}
    configurations: set[str] = set()
    for row in rows:
        cells = [
            *row.get("core_model_plant_cells", []),
            *row.get("sensor_transport_plant_cells", []),
        ]
        failures = [cell for cell in cells if cell.get("support_pass") is False]
        counts[row["label"]] = len(failures)
        configurations.update(str(cell.get("configuration_id")) for cell in failures)
    return counts, configurations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v42 preregistration")
    v41 = json.loads(V41_RESULT.read_text(encoding="utf-8"))
    if (
        v41.get("schema_version")
        != "winner_v41.static_equilibrium_target_feasibility_result.v2"
        or v41.get("status")
        != "PASS_WINNER_V41_STATIC_EQUILIBRIUM_TARGET_FEASIBILITY"
        or v41.get("decision") != "AUTHORIZE_STATIC_TARGET_TEACHER_CONTRACT_ONLY"
        or v41.get("summary", {}).get("shared_support_pass_count") != 100
        or v41.get("summary", {}).get("selected_coordinates")
        != [-0.25, -0.25, 0.25]
        or v41.get("authority", {}).get("robot_clearance") is not False
    ):
        raise ValueError("Winner-v41 does not authorize the teacher table")
    v33 = json.loads(V33_RESULT.read_text(encoding="utf-8"))
    failure_counts, failure_configurations = v33_failure_summary(v33)
    if (
        v33.get("status") != "HOLD_WINNER_V33_PREFIX_RIGHT_PITCH_ANCHOR_SUPPORT_GATE"
        or v33.get("decision") != "DO_NOT_TRAIN_RESPONSE_CONDITIONED_LOCOMOTION"
        or failure_counts != {"half": 25, "final": 30}
        or failure_configurations != set(CONFIGURATION_IDS)
    ):
        raise ValueError("Winner-v33 failure source changed")
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v42.static_target_teacher_table_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V42_STATIC_TARGET_TEACHER_TABLE",
        "decision": "AUTHORIZE_ONE_CPU_ONLY_15_CONFIGURATION_TEACHER_TABLE",
        "question": (
            "Does the exact Winner-v41 729-target equilibrium grid contain at least one "
            "shared two-plant full-horizon target for every configuration in the frozen "
            "15-configuration Winner-v33 failure union?"
        ),
        "screen": {
            "configuration_ids": CONFIGURATION_IDS,
            "actuator_plants": ["P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"],
            "grid_values": [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0],
            "targets_per_configuration": 729,
            "maximum_candidate_plant_cells": 21_870,
            "duration_ticks": 250,
            "selection": "unchanged Winner-v41 deterministic shared-target key",
            "target_semantics": "one selected time-invariant target per configuration",
            "evaluation": (
                "All 15 tables execute. Diagnostic best targets for configurations with "
                "zero shared passes are recorded but never promoted."
            ),
        },
        "pass_rule": {
            "exact_15_configuration_tables": True,
            "exact_729_targets_per_configuration": True,
            "exact_21870_candidate_plant_cells": True,
            "all_candidate_actions_graph_bounded": True,
            "all_selected_target_replays_exact": True,
            "every_configuration_has_a_shared_two_plant_support_target": True,
            "closest_result_selection": False,
        },
        "interpretation": {
            "pass": (
                "A full failure-set static-target teacher table exists; authorize only a "
                "separate default-off teacher ABI CPU contract."
            ),
            "hold": (
                "Close the exact static-target teacher-table route. Do not refine the "
                "grid, change the basis, fit only passing configurations, or promote a "
                "diagnostic best."
            ),
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
        "source_results": {
            "winner_v33_result_lf_sha256": lf_sha256(V33_RESULT),
            "winner_v33_support_failure_counts": failure_counts,
            "winner_v33_failure_configuration_ids": sorted(failure_configurations),
            "winner_v41_result_lf_sha256": lf_sha256(V41_RESULT),
            "winner_v41_repository_attribution": v41["repository_attribution"],
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "runtime_static_target_or_action_wrapper_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "one separately frozen static-target teacher ABI CPU contract"
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join([
            "# Winner-v42 static-target teacher-table preregistration", "",
            f"- Status: `{value['status']}`",
            f"- Decision: `{value['decision']}`",
            "- Configurations / targets each / plants: `15 / 729 / 2`",
            "- Maximum candidate-plant cells: `21,870`",
            "- Duration: `250 ticks` per cell",
            "- Optimizer / locomotion training / robot: `0 / 0 / 0`", "",
            value["question"], "",
            "This creates a simulator teacher table only. It does not train, modify",
            "the policy/runtime, select a checkpoint, or grant robot clearance.", "",
        ]),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
