#!/usr/bin/env python3
"""Preregister V156's one-cell state-triggered causal behavior test."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/run_winner_v156_state_triggered_causal_behavior.py"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS
    / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V141_RESULT = ANALYSIS / "winner_v141_projected_final_behavior_result.json"
V144_CORRECTION = (
    ANALYSIS / "winner_v144_shadow_oracle_reporting_correction.json"
)
V150_CORRECTION = (
    ANALYSIS / "winner_v150_v148_shadow_oracle_reporting_correction.json"
)
V155_RESULT = (
    ANALYSIS / "winner_v155_velocity_gated_phase_residual_result.json"
)
V141_RUNNER = ROOT / "tools/run_winner_v141_projected_final_behavior.py"
OUTPUT = (
    ANALYSIS
    / "winner_v156_state_triggered_causal_behavior_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V156_STATE_TRIGGERED_CAUSAL_BEHAVIOR_PREREGISTRATION_20260725.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    parser.add_argument("--source-trace", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V156: {path}")
    evaluator_root = args.evaluator_root.resolve()
    source_trace = args.source_trace.resolve()
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    v141 = json.loads(V141_RESULT.read_text(encoding="utf-8"))
    v144 = json.loads(V144_CORRECTION.read_text(encoding="utf-8"))
    v150 = json.loads(V150_CORRECTION.read_text(encoding="utf-8"))
    v155 = json.loads(V155_RESULT.read_text(encoding="utf-8"))
    policy = Path(v155["artifact"]["deployed"]["path"])
    local_raw = Path(v155["artifact"]["raw"]["path"])
    paths = {
        "runner": RUNNER,
        "v126_preregistration": V126_PREREG,
        "base_preregistration": BASE_PREREG,
        "v141_result": V141_RESULT,
        "v144_correction": V144_CORRECTION,
        "v150_correction": V150_CORRECTION,
        "v155_result": V155_RESULT,
        "v141_runner": V141_RUNNER,
        "composition_manifest": manifest_path,
        "composed_evaluator": evaluator_path,
        "selected_policy": policy,
        "local_raw": local_raw,
        "source_trace": source_trace,
    }
    input_hashes = {name: sha256(path) for name, path in paths.items()}
    failing = v141["new_final_cells"][1]
    row = failing["identity"]
    checks = {
        "v155_graph_contract_green": (
            v155.get("status")
            == "PASS_WINNER_V155_VELOCITY_GATED_PHASE_RESIDUAL"
            and v155.get("failed_checks") == []
            and v155.get("checks", {}).get("changes_only_right_ankle")
            and v155.get("checks", {}).get(
                "all_39_frozen_negative_rows_outside_gate"
            )
        ),
        "selected_cell_is_exact_v141_torque_only_failure": (
            failing["failure_reasons"]
            == ["torque_peak_at_most_1p91229675_nm"]
            and str(row["plant"]) == "P30_ALL_JOINT"
            and float(row["command_x_m_s"]) == 0.074
            and int(row["seed"]) == 167_931_544
            and int(row["duration_ticks"]) == 600
        ),
        "two_exact_causal_precursors_frozen": (
            v144["causal_result"]["peak_event"]["source_tick"] == 394
            and v150["causal_result"]["event"]["source_tick"] == 583
            and v144["causal_result"]["peak_event"]["joint"] == 13
            and v150["causal_result"]["event"]["joint"] == 13
        ),
        "one_cell_only": True,
        "stop_after_cell": True,
        "training_and_oracle_disabled": True,
        "robot_surface_absent": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v156.state_triggered_causal_behavior_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V156_STATE_TRIGGERED_CAUSAL_BEHAVIOR"
            if not failed
            else "HOLD_WINNER_V156_STATE_TRIGGERED_CAUSAL_BEHAVIOR"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "matrix": {
            "rows": 1,
            "row": row,
            "reason": (
                "the exact P30 x=.074 seed cell that isolated V140's "
                "right-ankle torque event"
            ),
        },
        "causal_contract": {
            "prefix": (
                "source trajectory remains bit-exact through tick 394 "
                "observation and recurrent input"
            ),
            "active_ticks": [394, 583],
            "interventions": (
                "both activations change only right ankle by the frozen "
                "correction"
            ),
            "outcome": (
                "all frozen gait, duration, tracking, torque, current, "
                "saturation, guard, and rate gates pass"
            ),
        },
        "pass_rule": "the one causal cell and every causal check pass",
        "stop_rule": (
            "any failure closes the velocity-gated phase residual; do not "
            "change the feature, threshold, phase, contact, radius, "
            "amplitude, or tolerance"
        ),
        "green_followup": (
            "earn only preregistration of the remaining dual-checkpoint "
            "offline matrix; no deployment or Gate 5"
        ),
        "authority": {
            "behavior_cells": 1 if not failed else 0,
            "additional_behavior": False,
            "training": False,
            "hosted_training": False,
            "policy_deployment": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V156 state-triggered causal behavior preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- One CPU cell: P30, x=.074, seed 167931544, 600 ticks.\n"
        "- Require exact prefix, activations at ticks 394 and 583 only, "
        "and every frozen gate green.\n"
        "- No training, Colab, deployment, Gate 5, or hardware.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
