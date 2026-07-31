#!/usr/bin/env python3
"""Freeze the four-cell V140 remaining shadow-oracle census."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = (
    ANALYSIS
    / "winner_v160_remaining_shadow_census_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V160_REMAINING_SHADOW_CENSUS_PREREGISTRATION_20260725.md"
)
V140 = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
V141 = ANALYSIS / "winner_v141_projected_final_behavior_result.json"
V144 = ANALYSIS / "winner_v144_shadow_oracle_reporting_correction.json"
V158 = (
    ANALYSIS / "winner_v158_x077_shadow_census_reporting_correction.json"
)
V159 = ANALYSIS / "winner_v159_cadence_screen_invalidity.json"
V126 = ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
BASE = (
    ANALYSIS
    / "winner_v3_variable_configuration_replacement_preregistration.json"
)
COMPOSER = ROOT / "tools/compose_winner_v144_shadow_oracle_evaluator.py"
PROJECTOR = ROOT / "tools/exact_torque_oracle_two_fit.py"


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
    evaluator_root = args.evaluator_root.resolve()
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator = Path(manifest["output"]["path"])
    v140 = json.loads(V140.read_text(encoding="utf-8"))
    v144 = json.loads(V144.read_text(encoding="utf-8"))
    v158 = json.loads(V158.read_text(encoding="utf-8"))
    v159 = json.loads(V159.read_text(encoding="utf-8"))
    policy = Path(v140["artifacts"]["selected_deployed"]["path"])
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V160: {path}")
    plants_commands = [
        ("P30_ALL_JOINT", 0.080),
        ("P31_34_PITCH_WITH_P30_NONPITCH", 0.074),
        ("P31_34_PITCH_WITH_P30_NONPITCH", 0.077),
        ("P31_34_PITCH_WITH_P30_NONPITCH", 0.080),
    ]
    rows = [
        {
            "calibration_ticks": 0,
            "checkpoint_id": "V140_SELECTED_FINAL",
            "plant": plant,
            "command_x_m_s": command,
            "seed": 167931544,
            "duration_ticks": 600,
            "home_return_ticks": 0,
            "oracle_schedule_ticks": None,
            "configuration": None,
            "policy_sha256": v140["artifacts"]["selected_deployed"][
                "sha256"
            ],
            "step": 2_007_040,
            "transport": {
                "additional_action_delay_ticks": 0,
                "imu_delay_ticks": 0,
                "native_quantization": False,
                "sensor_noise_scales": None,
            },
        }
        for plant, command in plants_commands
    ]
    input_paths = {
        "builder": Path(__file__).resolve(),
        "v140_result": V140,
        "v141_result": V141,
        "v144_reporting_correction": V144,
        "v158_reporting_correction": V158,
        "v159_invalidity": V159,
        "v126_preregistration": V126,
        "base_preregistration": BASE,
        "composer": COMPOSER,
        "projector": PROJECTOR,
        "composition_manifest": manifest_path,
        "composed_evaluator": evaluator,
        "selected_policy": policy,
    }
    checks = {
        "v140_policy_exact": (
            sha256(policy)
            == v140["artifacts"]["selected_deployed"]["sha256"]
        ),
        "v144_x074_census_green": (
            v144.get("status")
            == "PASS_WINNER_V144_SHADOW_ORACLE_REPORTING_CORRECTION"
        ),
        "v158_x077_census_green": (
            v158.get("status")
            == "PASS_WINNER_V158_X077_SHADOW_CENSUS_REPORTING_CORRECTION"
        ),
        "v159_cadence_closed_without_behavior": (
            v159.get("status")
            == "PASS_WINNER_V159_CADENCE_INVALIDITY_ATTRIBUTION"
        ),
        "four_remaining_cells_exact": (
            len(rows) == 4
            and len({(row["plant"], row["command_x_m_s"]) for row in rows})
            == 4
        ),
        "shadow_apply_false": True,
        "full_census_no_behavior_selection": True,
        "cpu_only_no_training_hosted_compute_or_hardware": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v160.remaining_shadow_census_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V160_REMAINING_SHADOW_CENSUS"
            if not failed
            else "HOLD_WINNER_V160_REMAINING_SHADOW_CENSUS_"
            "PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": {
            name: sha256(path) for name, path in input_paths.items()
        },
        "matrix": {
            "cells": len(rows),
            "rows": rows,
            "completion_rule": (
                "run all four cells; physical gate failures are data and "
                "do not stop this read-only census"
            ),
        },
        "method": {
            "policy": "V140 selected final, bit-exact",
            "oracle": "exact two-fit all-tick projector",
            "application": False,
            "trajectory": "unmodified policy action is always committed",
            "labels": (
                "per-tick base/final action, projected joints, empty "
                "intersections, matured predicted force, and actual force"
            ),
        },
        "validity_gates": {
            "trace_rows_each": 600,
            "oracle_rows_each": 600,
            "shadow_action_never_applied": True,
            "all_actual_violations_have_safe_nonempty_precursor": True,
            "cpu_only": True,
        },
        "decision_rule": (
            "a validity-green four-cell census earns only a read-only "
            "V161 command/plant/joint representation audit; it does not "
            "earn training or behavior selection"
        ),
        "authority": {
            "cpu_shadow_diagnostic": not failed,
            "training": False,
            "hosted_training": False,
            "candidate_behavior": False,
            "policy_or_runtime_change": False,
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
        "# Winner V160 remaining shadow census preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Four missing V140 moving cells: P30 x=.080 and P31/34 "
        "x=.074/.077/.080.\n"
        "- Exact two-fit oracle runs shadow-only; policy actions remain "
        "the simulated trajectory.\n"
        "- All four cells run because failures are labels, not selection.\n"
        "- No training, Colab, policy/runtime change, deployment, Gate 5, "
        "or robot.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
