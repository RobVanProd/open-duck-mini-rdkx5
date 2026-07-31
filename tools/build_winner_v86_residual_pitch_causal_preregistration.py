#!/usr/bin/env python3
"""Preregister the read-only Winner-v86 residual pitch-output diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v86_residual_pitch_causal_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V86_RESIDUAL_PITCH_CAUSAL_PREREGISTRATION_20260722.md"
V85_RESULT = ANALYSIS / "winner_v85_integrated_support_gate_result.json"
V85_RESULT_SHA256 = "ea25f93a79157e0dac380d3c2f6d7ddf596ae4cfd1c951245cb4cb4b2ddcc4e4"
ARMS = ("graph", "full_teacher", "pitch_teacher", "nonpitch_zero")


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


def failed_pairs(value: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for checkpoint in value["checkpoint_results"]:
        for population in ("core_model_plant_cells", "sensor_transport_plant_cells"):
            for cell in checkpoint[population]:
                if not cell["support_pass"]:
                    rows.append(
                        {
                            "checkpoint_label": checkpoint["label"],
                            "checkpoint_update": checkpoint["update"],
                            "configuration_id": cell["configuration_id"],
                            "plant": cell["plant"],
                            "formal_cell_sha256": canonical_sha256(cell),
                        }
                    )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite Winner-v86 contract: {path}")
    formal = json.loads(V85_RESULT.read_text(encoding="utf-8"))
    pairs = failed_pairs(formal)
    expected = {
        ("half", "COM_CORNER_01", "P30_ALL_JOINT"),
        ("half", "COM_CORNER_01", "P31_34_PITCH_WITH_P30_NONPITCH"),
        ("half", "COM_CORNER_03", "P30_ALL_JOINT"),
        ("half", "COM_CORNER_03", "P31_34_PITCH_WITH_P30_NONPITCH"),
        ("final", "COM_X_NEG", "P30_ALL_JOINT"),
        ("final", "COM_X_NEG", "P31_34_PITCH_WITH_P30_NONPITCH"),
        ("final", "COM_CORNER_01", "P30_ALL_JOINT"),
        ("final", "COM_CORNER_01", "P31_34_PITCH_WITH_P30_NONPITCH"),
        ("final", "COM_CORNER_03", "P30_ALL_JOINT"),
        ("final", "COM_CORNER_03", "P31_34_PITCH_WITH_P30_NONPITCH"),
        ("final", "DISCOVERY_03", "P30_ALL_JOINT"),
        ("final", "DISCOVERY_03", "P31_34_PITCH_WITH_P30_NONPITCH"),
    }
    observed = {
        (row["checkpoint_label"], row["configuration_id"], row["plant"])
        for row in pairs
    }
    if (
        sha256(V85_RESULT) != V85_RESULT_SHA256
        or formal.get("status") != "HOLD_WINNER_V85_INTEGRATED_SUPPORT_GATE"
        or formal.get("decision") != "DO_NOT_SELECT_WINNER_V84_DEPLOYMENT_POLICY"
        or formal.get("selected_checkpoint") is not None
        or formal.get("authority", {}).get("robot_clearance") is not False
        or formal.get("execution", {}).get("formal_support_cells") != 248
        or observed != expected
        or len(pairs) != 12
    ):
        raise ValueError("Winner-v86 source failures changed")
    source_paths = {
        "builder": Path("tools/build_winner_v86_residual_pitch_causal_preregistration.py"),
        "runner": Path("tools/run_winner_v86_residual_pitch_causal.py"),
        "tests": Path("tests/test_winner_v86_residual_pitch_causal.py"),
        "v85_result": V85_RESULT.relative_to(ROOT),
        "v85_preregistration": Path(
            "outputs/analysis/winner_v85_integrated_support_gate_preregistration.json"
        ),
        "v85_builder": Path("tools/build_winner_v85_integrated_support_gate_preregistration.py"),
        "v84_result": Path(
            "outputs/analysis/winner_v84_negative_gradient_pitch_head_continuation_result.json"
        ),
        "v80_result": Path("outputs/analysis/winner_v80_pitch_action_head_step_result.json"),
        "v80c_builder": Path("tools/build_winner_v80c_action_boundary_check_correction.py"),
        "v48_intervention": Path("tools/run_winner_v48_static_teacher_causal_diagnostic.py"),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v86.residual_pitch_causal_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V86_RESIDUAL_PITCH_CAUSAL_DIAGNOSTIC",
        "decision": "AUTHORIZE_ONE_READ_ONLY_12_PAIR_FOUR_ARM_DIAGNOSTIC_ONLY",
        "causal_question": (
            "After the localized Winner-v84 correction, are all twelve residual "
            "half/final plant failures still rescued specifically by replacing the "
            "six pitch outputs with the replay-bound static teacher?"
        ),
        "frozen_source": {
            "v85_result_sha256": V85_RESULT_SHA256,
            "failure_pairs": pairs,
            "failure_pair_count": 12,
            "checkpoint_labels_updates": {"half": 705, "final": 755},
            "arms": list(ARMS),
            "diagnostic_cells": 48,
            "teacher_table": "the exact complete replay-bound table used by Winner-v80/v84",
            "predictor_failure_recorded_but_not_modified": True,
        },
        "classification_rule": (
            "Use the unchanged Winner-v48 failed-pair classifier independently for "
            "each exact pair; select a subsequent mechanism only from the complete "
            "12-pair classification counts."
        ),
        "checks": {
            "all_12_graph_cells_bit_exact_to_v85": True,
            "all_12_source_graph_cells_fail": True,
            "exact_48_cells": True,
            "all_previous_action_chains_exact": True,
            "all_jax_onnx_hidden_errors_at_most_1e_7": True,
            "all_values_finite": True,
        },
        "execution_now": {
            "diagnostic_cells": 0,
            "optimizer_updates": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "diagnostic_authorized": True,
            "result_authorizes": "causal diagnosis and a separate prospective mechanism preregistration only",
            "training_authorized_now": False,
            "support_gate_authorized_now": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v86 residual pitch-output causal preregistration",
                "",
                "- Population: `12 exact failed endpoint/configuration/plant pairs × 4 arms = 48 cells`",
                "- Checkpoints: exact Winner-v84 counts `705 / 755`",
                "- Arms: graph / full teacher / pitch teacher / non-pitch zero",
                "- Predictor failure: recorded, not modified in this diagnostic",
                "- Optimizer updates / support-gate cells / robot access: `0 / 0 / 0`",
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
