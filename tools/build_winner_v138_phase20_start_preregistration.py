#!/usr/bin/env python3
"""Preregister the single-phase V138 dual-checkpoint CPU screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/run_winner_v138_phase20_start_screen.py"
AUDITOR = ROOT / "tools/audit_winner_v138_phase20_start.py"
AUDIT = ANALYSIS / "winner_v138_phase20_start_audit_v2.json"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
OUTPUT = ANALYSIS / "winner_v138_phase20_start_preregistration.json"
MARKDOWN = ANALYSIS / "WINNER_V138_PHASE20_START_PREREGISTRATION_20260725.md"
EXPECTED = {
    "runner": (
        "ef12e1c8e1377aae5d2b5005cd54b155e901fa6dd30c6d0e58e339e6cd615af3"
    ),
    "auditor": (
        "e80188ef592097492342390d5276ca82f8714a24f5c4261f551f1882381910d5"
    ),
    "audit": (
        "9046d387dcc8bd59d1c2449138f4c72edea3ae13cdc46ebc6b6ae4f1cee145f7"
    ),
    "v126_preregistration": (
        "eb40f17d9c08b8362f068567e1620bdafef21ad9123a633c9536f3637a31c899"
    ),
    "base_preregistration": (
        "c8f986ceb24863f33c1fc99170548d2e255cb6a26737d3f74762f8dcd4485a24"
    ),
    "composition_manifest": (
        "39e842470828208dfea08b17d936d3f0e6f0d45b8f9813a1edd139692e4a6f74"
    ),
    "composed_evaluator": (
        "1539ba18b5b207a15538a8a8611475f5c73bcd7164f2fe039cad8b279a587e43"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V138: {path}")
    evaluator_root = args.evaluator_root.resolve()
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    input_hashes = {
        "runner": sha256(RUNNER),
        "auditor": sha256(AUDITOR),
        "audit": sha256(AUDIT),
        "v126_preregistration": sha256(V126_PREREG),
        "base_preregistration": sha256(BASE_PREREG),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator_path),
    }
    source_rows = list(v126["matrix"]["rows"])
    matrix = [
        row
        for checkpoint in (
            "V121_TRAIN_MATCHED_FINAL",
            "V121_TRAIN_MATCHED_HALF",
        )
        for row in source_rows
        if row["checkpoint_id"] == checkpoint
    ]
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "audit_green": (
            audit.get("status") == "PASS_WINNER_V138_PHASE20_START_AUDIT"
            and audit.get("selection", {}).get("selected_phase_index") == 20
            and audit.get("selection", {}).get(
                "selection_weight_from_behavior_outcomes"
            )
            == 0
        ),
        "evaluator_composition_green": (
            manifest.get("status")
            == "PASS_WINNER_V136_WARM_START_EVALUATOR_COMPOSITION"
        ),
        "matrix_exact_16": (
            len(matrix) == 16
            and {row["checkpoint_id"] for row in matrix}
            == {
                "V121_TRAIN_MATCHED_HALF",
                "V121_TRAIN_MATCHED_FINAL",
            }
            and {float(row["command_x_m_s"]) for row in matrix}
            == {0.0, 0.074, 0.077, 0.08}
        ),
        "final_checkpoint_evaluated_first": all(
            row["checkpoint_id"] == "V121_TRAIN_MATCHED_FINAL"
            for row in matrix[:8]
        ),
        "one_phase_only": True,
        "zero_policy_weight_changes": True,
        "oracle_disabled": True,
        "sequential_stop_at_first_failure": True,
        "training_not_authorized": True,
        "runtime_contract_change_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v138.phase20_start_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V138_PHASE20_START_SCREEN"
            if not failed
            else "HOLD_WINNER_V138_PHASE20_START_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            key: value
            for key, value in input_hashes.items()
            if key != "auditor"
        },
        "audit_inputs": {
            "auditor_sha256": input_hashes["auditor"],
        },
        "mechanism": {
            "name": "phase20_reference_start",
            "reference_start_phase": 20,
            "period_ticks": 27,
            "selection": (
                "unique minimum pitch-reference L-infinity departure from "
                "home; selected before behavior"
            ),
            "policy_graphs": "frozen V121 half and final",
            "policy_weights_changed": False,
            "reference_waveform_changed": False,
            "phase_frequency_changed": False,
            "oracle": False,
        },
        "matrix": {
            "cells": 16,
            "rows": matrix,
            "ordering": (
                "final checkpoint first because it is the known persistence "
                "blocker; within each checkpoint retain the frozen V126 order"
            ),
            "stop": "stop immediately after the first failing cell",
        },
        "pass_rule": {
            "all_cells": (
                "all 16 complete 600 ticks and pass unchanged gait, tracking, "
                "x=0, saturation, rate, current, and 1.91229675-Nm torque gates"
            ),
            "state": "h_in and previous_action reset to exact zero",
            "phase": "first observation equals phase index 20 within 1e-7",
            "x0": "all deployed actions remain exact zero",
            "oracle": "zero oracle records",
            "persistence": "both frozen checkpoints must pass all eight cells",
        },
        "stop_rule": (
            "the first failure closes phase-20 start; do not evaluate another "
            "phase, alter the selected phase, or train from this result"
        ),
        "green_followup": (
            "a 16/16 pass earns only an explicit observation/phase runtime "
            "contract review and golden-vector reconciliation; it does not "
            "authorize Gate 5 or deployment"
        ),
        "authority": {
            "phase20_behavior_cells": 16 if not failed else 0,
            "other_phase_evaluation": False,
            "runtime_contract_change": False,
            "training": False,
            "hosted_training": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V138 phase-20 start preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- One phase (`20/27`) selected from reference geometry before "
        "behavior.\n"
        "- Frozen V121 final then half, 16 cells maximum, stopping at the "
        "first failure.\n"
        "- No phase sweep, policy change, oracle, training, Colab, runtime "
        "change, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
