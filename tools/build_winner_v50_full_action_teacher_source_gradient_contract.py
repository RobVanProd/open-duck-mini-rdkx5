#!/usr/bin/env python3
"""Freeze the zero-update Winner-v50 source-gradient CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(PATCHES))

import winner_v49_full_action_static_target_teacher as v49  # noqa: E402


OUTPUT = ANALYSIS / "winner_v50_full_action_teacher_source_gradient_contract.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V50_FULL_ACTION_TEACHER_SOURCE_GRADIENT_CONTRACT_20260722.md"
)
V49_RESULT = ANALYSIS / "winner_v49_full_action_teacher_abi_cpu_result.json"
V46_RESULT = ANALYSIS / "winner_v46_static_target_teacher_training_result.json"
V22_RESULT = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
SOURCES = {
    "builder": Path("tools/build_winner_v50_full_action_teacher_source_gradient_contract.py"),
    "runner": Path("tools/run_winner_v50_full_action_teacher_source_gradient_contract.py"),
    "tests": Path("tests/test_winner_v50_full_action_teacher_source_gradient_contract.py"),
    "winner_v49_result": Path(
        "outputs/analysis/winner_v49_full_action_teacher_abi_cpu_result.json"
    ),
    "winner_v49_teacher": Path(
        "patches/winner_v49_full_action_static_target_teacher.py"
    ),
    "winner_v46_result": Path(
        "outputs/analysis/winner_v46_static_target_teacher_training_result.json"
    ),
    "winner_v46_preregistration": Path(
        "outputs/analysis/winner_v46_static_target_teacher_training_preregistration.json"
    ),
    "winner_v46_runner": Path(
        "tools/run_winner_v46_static_target_teacher_training.py"
    ),
    "winner_v22_result": Path(
        "outputs/analysis/winner_v22_normalized_predictor_training_result.json"
    ),
    "winner_v42_result": Path(
        "outputs/analysis/winner_v42_static_target_teacher_table_result.json"
    ),
    "pitch_teacher": Path("patches/winner_v43_static_target_teacher.py"),
    "pitch_training_teacher": Path(
        "tools/run_winner_v44_static_target_teacher_source_gradient_contract.py"
    ),
    "prefix_anchor": Path("patches/winner_v29_prefix_right_pitch_anchor.py"),
    "training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "full_training": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "full_training_preregistration": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
    ),
    "configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v50 contract: {path}")

    v49_result = json.loads(V49_RESULT.read_text(encoding="utf-8"))
    v46_result = json.loads(V46_RESULT.read_text(encoding="utf-8"))
    v22_result = json.loads(V22_RESULT.read_text(encoding="utf-8"))
    final = next(
        row
        for row in v46_result["persistent_checkpoints"]
        if row["label"] == "final"
    )
    teacher_final = next(
        row
        for row in v22_result["persistent_checkpoints"]
        if row["label"] == "final"
    )
    if (
        v49_result.get("status")
        != "PASS_WINNER_V49_FULL_ACTION_TEACHER_ABI_CPU_CONTRACT"
        or v49_result.get("decision")
        != "AUTHORIZE_FULL_ACTION_TEACHER_SOURCE_GRADIENT_PREREGISTRATION_ONLY"
        or v46_result.get("status")
        != "PASS_WINNER_V46_STATIC_TARGET_TEACHER_TRAINING_ARTIFACT"
        or final.get("completed_updates") != 352
        or v22_result.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
        or teacher_final.get("snapshot", {}).get("completed_updates") != 100
    ):
        raise ValueError("Winner-v50 source authority changed")
    sources = {
        name: {
            "path": path.as_posix(),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v50.full_action_teacher_source_gradient_contract.v1",
        "status": "PREREGISTERED_WINNER_V50_FULL_ACTION_TEACHER_SOURCE_GRADIENT_CONTRACT",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_FULL_ACTION_SOURCE_GRADIENT_CPU_PROOF_ONLY",
        "source_selection": {
            "selected_label": "final",
            "selected_update": 352,
            "selected_snapshot": final["snapshot"],
            "selected_graph": final["graph"],
            "rule": (
                "resume the terminal optimizer state of the sole completed Winner-v46 "
                "training arm; this is continuation state, not deployment selection"
            ),
            "deployment_checkpoint_selected": False,
        },
        "objective": {
            "rollout_update_index": 352,
            "episode_slots": 80,
            "ticks_per_slot": 250,
            "teacher_configuration_ids": [
                "COM_X_NEG", "COM_CORNER_00", "COM_CORNER_01", "COM_CORNER_02",
                "COM_CORNER_03", "OPTIONAL_AGGREGATE_HEAVY_AFT", "DISCOVERY_02",
                "DISCOVERY_03", "DISCOVERY_06", "DISCOVERY_09", "DISCOVERY_10",
            ],
            "heldout_teacher_configuration_ids_excluded": [
                "HELDOUT_04", "HELDOUT_07", "HELDOUT_09", "HELDOUT_15"
            ],
            "teacher_configuration_plant_rows": 22,
            "old_supervised_indices": list(v49.PITCH_ACTION_INDICES),
            "new_supervised_indices": list(v49.ACTION_INDICES),
            "old_teacher_scale": float(v49.OLD_PITCH_TEACHER_SCALE),
            "new_teacher_scale": float(v49.FULL_ACTION_TEACHER_SCALE),
            "replacement_rule": (
                "replace the old pitch-only mean with the full-action mean; identical "
                "per-element pitch weight, no additive double-counting"
            ),
            "baseline": (
                "unchanged PPO plus normalized predictor scale 380.9135437011719 "
                "plus prefix-anchor scale 197.3112030029297"
            ),
            "default_off": "the exact old Winner-v46 objective and gradients",
            "no_action_replacement": True,
            "no_scale_search": True,
        },
        "pass_checks": [
            "bind exact V46 final snapshot/graph and V22 teacher snapshot bytes",
            "run the exact 80-slot update-352 CPU rollout without changing transitions",
            "select exactly 22 training configuration/plant rows and exclude heldout labels",
            "preserve old pitch mask/targets and add all eight valid non-pitch elements",
            "prove old and new teacher gradients are finite on policy leaves only",
            "prove replacement changes policy gradients and preserves nonpolicy gradients",
            "prove default-off gradient is bit-exact to the old Winner-v46 objective",
            "prove composed and direct old/new gradients agree within 4e-6",
            "execute no optimizer update, support gate, export, locomotion, or hardware work",
        ],
        "artifact_inputs": {
            "winner_v46_final": final,
            "winner_v22_teacher_snapshot": teacher_final["snapshot"],
        },
        "execution_now": {
            "rollout_episode_slots": 0,
            "scheduled_rollout_ticks": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "deployable_graph_exports": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "one_update_authorized": False,
            "training_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "one separately preregistered CPU-only one-update proof",
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v50 full-action teacher source-gradient contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Continuation source: `Winner-v46 final @ 352`",
                "- Rollout: `80 x 250 ticks`, CPU-only",
                "- Old/new supervised actions: `6 / 14`",
                "- Old/new scale: `58.436370849609375 / 136.35153198242188`",
                "- Optimizer / gate / export / locomotion / robot: `0 / 0 / 0 / 0 / 0`",
                "",
                "This proves gradients at the real continuation state. It neither runs",
                "an update nor selects a deployment checkpoint.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
