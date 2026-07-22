#!/usr/bin/env python3
"""Freeze one zero-update source-gradient contract for the V43 teacher."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v44_static_target_teacher_source_gradient_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V44_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_CONTRACT_20260722.md"
V22_RESULT = ANALYSIS / "winner_v22_normalized_predictor_training_result.json"
V32_PREREG = ANALYSIS / "winner_v32_prefix_right_pitch_anchor_training_preregistration.json"
V32_RESULT = ANALYSIS / "winner_v32_prefix_right_pitch_anchor_training_result.json"
V33_RESULT = ANALYSIS / "winner_v33_prefix_right_pitch_anchor_support_gate_result.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
V43_RESULT = ANALYSIS / "winner_v43_static_target_teacher_abi_cpu_result.json"
TRAINING_TEACHER_IDS = (
    "COM_X_NEG", "COM_CORNER_00", "COM_CORNER_01", "COM_CORNER_02",
    "COM_CORNER_03", "OPTIONAL_AGGREGATE_HEAVY_AFT", "DISCOVERY_02",
    "DISCOVERY_03", "DISCOVERY_06", "DISCOVERY_09", "DISCOVERY_10",
)
HELDOUT_TEACHER_IDS = ("HELDOUT_04", "HELDOUT_07", "HELDOUT_09", "HELDOUT_15")
SOURCES = {
    "builder": Path("tools/build_winner_v44_static_target_teacher_source_gradient_contract.py"),
    "runner": Path("tools/run_winner_v44_static_target_teacher_source_gradient_contract.py"),
    "runner_tests": Path("tests/test_winner_v44_static_target_teacher_source_gradient_contract.py"),
    "preregistration_tests": Path(
        "tests/test_winner_v44_static_target_teacher_source_gradient_preregistration.py"
    ),
    "result_importer": Path(
        "tools/import_winner_v44_static_target_teacher_source_gradient_result.py"
    ),
    "result_importer_tests": Path(
        "tests/test_winner_v44_static_target_teacher_source_gradient_import.py"
    ),
    "workflow": Path(
        ".github/workflows/winner-v44-static-target-teacher-source-gradient.yml"
    ),
    "teacher": Path("patches/winner_v43_static_target_teacher.py"),
    "teacher_tests": Path("tests/test_winner_v43_static_target_teacher.py"),
    "winner_v43_contract": Path(
        "outputs/analysis/winner_v43_static_target_teacher_abi_cpu_contract.json"
    ),
    "winner_v43_result": Path(
        "outputs/analysis/winner_v43_static_target_teacher_abi_cpu_result.json"
    ),
    "winner_v42_result": Path(
        "outputs/analysis/winner_v42_static_target_teacher_table_result.json"
    ),
    "winner_v33_result": Path(
        "outputs/analysis/winner_v33_prefix_right_pitch_anchor_support_gate_result.json"
    ),
    "winner_v32_preregistration": Path(
        "outputs/analysis/winner_v32_prefix_right_pitch_anchor_training_preregistration.json"
    ),
    "winner_v32_result": Path(
        "outputs/analysis/winner_v32_prefix_right_pitch_anchor_training_result.json"
    ),
    "winner_v32_training": Path(
        "tools/run_winner_v32_prefix_right_pitch_anchor_training.py"
    ),
    "winner_v22_result": Path(
        "outputs/analysis/winner_v22_normalized_predictor_training_result.json"
    ),
    "winner_v29_objective": Path("patches/winner_v29_prefix_right_pitch_anchor.py"),
    "winner_v24_objective": Path("patches/winner_v24_symmetric_support_failure_v3.py"),
    "normalized_predictor": Path("patches/winner_v22_normalized_predictor.py"),
    "gradient_composition": Path("patches/winner_v22_normalized_predictor_v2.py"),
    "recurrent_mechanics": Path("patches/winner_v20_joint_recurrent_support.py"),
    "joint_mechanics": Path("patches/winner_v21_predictor_preserving_joint_support.py"),
    "training_mechanics": Path("patches/winner_v12_calibrator_training.py"),
    "full_training": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "environment_preparation": Path("tools/prepare_winner_v15_cpu_environment.py"),
    "configuration_domain": Path(
        "outputs/analysis/winner_v3_variable_configuration_replacement_preregistration.json"
    ),
    "calibrator_design": Path(
        "outputs/analysis/winner_v12_calibrator_training_preregistration.json"
    ),
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


def support_counts(value: dict[str, Any]) -> dict[str, dict[str, int]]:
    output: dict[str, dict[str, int]] = {}
    for row in value["checkpoint_results"]:
        cells = [*row["core_model_plant_cells"], *row["sensor_transport_plant_cells"]]
        output[row["label"]] = {
            "passes": sum(cell["support_pass"] for cell in cells),
            "failures": sum(not cell["support_pass"] for cell in cells),
            "cells": len(cells),
        }
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    if args.output.exists() or args.markdown.exists():
        raise FileExistsError("refusing to overwrite Winner-v44 contract")
    v22 = json.loads(V22_RESULT.read_text(encoding="utf-8"))
    v32_prereg = json.loads(V32_PREREG.read_text(encoding="utf-8"))
    v32 = json.loads(V32_RESULT.read_text(encoding="utf-8"))
    v33 = json.loads(V33_RESULT.read_text(encoding="utf-8"))
    v42 = json.loads(V42_RESULT.read_text(encoding="utf-8"))
    v43 = json.loads(V43_RESULT.read_text(encoding="utf-8"))
    counts = support_counts(v33)
    if counts != {
        "half": {"passes": 99, "failures": 25, "cells": 124},
        "final": {"passes": 94, "failures": 30, "cells": 124},
    }:
        raise ValueError("Winner-v33 source selection evidence changed")
    if (
        v43.get("status") != "PASS_WINNER_V43_STATIC_TARGET_TEACHER_ABI_CPU_CONTRACT"
        or v43.get("decision")
        != "AUTHORIZE_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_CPU_CONTRACT_ONLY"
        or v42.get("status") != "PASS_WINNER_V42_STATIC_TARGET_TEACHER_TABLE"
        or v32.get("status")
        != "PASS_WINNER_V32_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING_ARTIFACT"
        or v22.get("status")
        != "PASS_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING_ARTIFACT"
    ):
        raise ValueError("Winner-v44 source authority changed")
    half = next(row for row in v32["persistent_checkpoints"] if row["label"] == "half")
    if half["completed_updates"] != 251:
        raise ValueError("Winner-v44 half checkpoint changed")
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in SOURCES.items()
    }
    value = {
        "schema_version": "winner_v44.static_target_teacher_source_gradient_contract.v1",
        "status": "PREREGISTERED_WINNER_V44_STATIC_TARGET_TEACHER_SOURCE_GRADIENT_CONTRACT",
        "decision": "AUTHORIZE_ONE_ZERO_UPDATE_SOURCE_GRADIENT_CPU_PROOF_ONLY",
        "source_selection": {
            "candidate_checkpoints": counts,
            "rule": "fewest failures over the identical 124-cell Winner-v33 gate; tie chooses earlier update",
            "selected_label": "half",
            "selected_update": 251,
            "selected_snapshot": half["snapshot"],
            "selected_graph": half["graph"],
            "scope": "training-continuation source only, not deployment checkpoint selection",
        },
        "objective": {
            "rollout_update_index": 251,
            "episode_slots": 80,
            "ticks_per_slot": 250,
            "teacher_configuration_ids": list(TRAINING_TEACHER_IDS),
            "heldout_teacher_configuration_ids_excluded": list(HELDOUT_TEACHER_IDS),
            "teacher_configuration_rows": 22,
            "teacher_action_indices": [2, 3, 4, 11, 12, 13],
            "teacher_target": "Winner-v43 stopped graph-bounded static target",
            "candidate_action": "source deterministic graph-bounded recurrent mean on its exact rollout",
            "baseline": (
                "unchanged Winner-v32 PPO plus normalized-predictor scale "
                "380.9135437011719 plus prefix-anchor scale 197.3112030029297"
            ),
            "scale_rule": (
                "once on the exact update-251 batch, divide baseline-gradient RMS by "
                "raw-teacher-gradient RMS over recurrent-core plus action-head leaves"
            ),
            "default_off": "baseline gradients and all rollout transition arrays bit-exact",
            "no_action_replacement": True,
            "unit_scale_carried_from_v43": False,
        },
        "pass_checks": [
            "bind exact Winner-v32 half snapshot/graph and Winner-v22 teacher snapshot bytes",
            "reproduce the exact 80-slot update-251 CPU rollout and full Winner-v32 baseline objective",
            "select exactly 22 training configuration/plant rows and only six pitch indices",
            "exclude all four heldout configuration labels from the training objective",
            "prove finite nonzero teacher loss and gradients on all six policy leaves",
            "prove exact zero teacher gradient on value, log-std, and predictor leaves",
            "derive one finite positive gradient-RMS scale without tuning",
            "prove default-off gradient and every transition array are bit-exact",
            "prove enabled direct-loss and composed gradients agree within 4e-6",
            "execute no optimizer update, formal support gate, deployment export, or hardware access",
        ],
        "execution_now": {
            "rollout_episode_slots": 0,
            "scheduled_rollout_ticks": 0,
            "optimizer_updates": 0,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "deployable_graph_exports": 0,
            "robot_or_rdk_access": 0,
        },
        "artifact_inputs": {
            "winner_v32": {
                "repository_attribution": v32["repository_attribution"],
                "half": half,
            },
            "winner_v22": {
                "repository_attribution": v32_prereg["teacher_checkpoint"]["repository_attribution"],
                "snapshot": v32_prereg["teacher_checkpoint"]["snapshot"],
            },
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "robot_clearance": False,
            "training_authorized": False,
            "one_update_authorized": False,
            "runtime_implementation_authorized": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": (
                "one separately preregistered CPU-only one-update proof using the exact recorded scale"
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
            "# Winner-v44 static-target teacher source-gradient contract", "",
            f"- Status: `{value['status']}`",
            f"- Decision: `{value['decision']}`",
            "- Source: `Winner-v32 half @ 251` (99/124 versus final 94/124)",
            "- Rollout: `80 x 250 ticks`, CPU-only",
            "- Optimizer / formal gate / training / export / robot: `0 / 0 / 0 / 0 / 0`", "",
            "This chooses a continuation source, not a deployment checkpoint. The sole",
            "derived teacher scale may be used only by a separate one-update CPU proof.", "",
        ]),
        encoding="utf-8",
    )
    print(value["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
