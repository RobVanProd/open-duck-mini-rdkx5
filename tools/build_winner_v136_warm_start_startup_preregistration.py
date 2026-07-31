#!/usr/bin/env python3
"""Preregister the paired V136 warm-start startup screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/run_winner_v136_warm_start_startup_screen.py"
COMPOSER = ROOT / "tools/compose_winner_v136_warm_start_evaluator.py"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V135_CONTRACT = ANALYSIS / "winner_v135_phase_consistent_hidden_contract.json"
V135_VECTOR = ANALYSIS / "winner_v135_phase_consistent_hidden_vector.json"
OUTPUT = ANALYSIS / "winner_v136_warm_start_startup_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V136_WARM_START_STARTUP_PREREGISTRATION_20260725.md"
)
EXPECTED = {
    "runner": (
        "6d1a407614c39a9c46b336ea77d23dc6917305f53fc7c8c5a4ec11fef723b80c"
    ),
    "v126_preregistration": (
        "eb40f17d9c08b8362f068567e1620bdafef21ad9123a633c9536f3637a31c899"
    ),
    "base_preregistration": (
        "c8f986ceb24863f33c1fc99170548d2e255cb6a26737d3f74762f8dcd4485a24"
    ),
    "v135_contract": (
        "068d8f450a72c584111b1855bd302f1be334367dd87f6a328e3be4f7c495dc85"
    ),
    "v135_vector": (
        "5f0eaefd2f9c5e8555345959b180f26095fa7a0175b9c151864a37490644f8c8"
    ),
    "composition_manifest": (
        "39e842470828208dfea08b17d936d3f0e6f0d45b8f9813a1edd139692e4a6f74"
    ),
    "composed_evaluator": (
        "1539ba18b5b207a15538a8a8611475f5c73bcd7164f2fe039cad8b279a587e43"
    ),
    "composer": (
        "b14f50fcfc814ec3e994efb850d1a1792e37bdbead1b8616bc767521855caee8"
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
            raise FileExistsError(f"refusing to overwrite V136: {path}")
    evaluator_root = args.evaluator_root.resolve()
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator = Path(manifest["output"]["path"])
    v135 = json.loads(V135_CONTRACT.read_text(encoding="utf-8"))
    input_hashes = {
        "runner": sha256(RUNNER),
        "v126_preregistration": sha256(V126_PREREG),
        "base_preregistration": sha256(BASE_PREREG),
        "v135_contract": sha256(V135_CONTRACT),
        "v135_vector": sha256(V135_VECTOR),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator),
        "composer": sha256(COMPOSER),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v135_contract_green": (
            v135.get("status")
            == "PASS_WINNER_V135_PHASE_CONSISTENT_HIDDEN_CONTRACT"
            and v135.get("decision")
            == "EARN_ONE_V136_WARM_START_STARTUP_SCREEN_PREREGISTRATION"
        ),
        "evaluator_composition_green": (
            manifest.get("status")
            == "PASS_WINNER_V136_WARM_START_EVALUATOR_COMPOSITION"
        ),
        "paired_zero_and_warm_initialization": True,
        "two_plants_x_point_08_only": True,
        "duration_64_ticks_only": True,
        "no_oracle_or_training": True,
        "formal_behavior_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v136.warm_start_startup_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V136_WARM_START_STARTUP_SCREEN"
            if not failed
            else "HOLD_WINNER_V136_WARM_START_STARTUP_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "question": (
            "Does the phase-consistent x=0 recurrent state remove the "
            "measured x=.08 startup torque violation under both actuator "
            "fits without relying on the oracle?"
        ),
        "matrix": {
            "checkpoint": "V121_TRAIN_MATCHED_FINAL",
            "plants": [
                "P30_ALL_JOINT",
                "P31_34_PITCH_WITH_P30_NONPITCH",
            ],
            "initializations": ["zero", "warm"],
            "command_x_m_s": 0.08,
            "ticks": 64,
            "cells": 4,
            "oracle": False,
        },
        "limits": {
            "torque_nm": 1.91229675,
            "current_a": 2.5,
            "strict_current_a": 2.0,
            "strict_current_max_run_ticks": 99,
            "pitch_tracking_p95_rad": 0.20,
        },
        "pass_rule": {
            "baseline": (
                "both zero-state cells reproduce at least one torque event"
            ),
            "warm_safety": (
                "both warm cells have zero torque/current events and peak "
                "torque/current inside the unchanged limits"
            ),
            "warm_behavior": (
                "both warm cells complete 64 ticks with tracking <=.20, "
                "zero saturation, and zero rate excess"
            ),
            "causal_direction": (
                "warm peak torque is no worse than zero-state in each plant"
            ),
            "state": "first h_in exactly matches its declared population",
        },
        "stop_rule": (
            "if any pass rule fails, close the warm-start mechanism; do not "
            "change the selected tick, average states, or try another hidden "
            "vector"
        ),
        "authority": {
            "startup_screen": not failed,
            "dual_checkpoint_preregistration": False,
            "formal_behavior": False,
            "training": False,
            "hosted_training": False,
            "full_matrix": False,
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
        "# Winner V136 warm-start startup preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Four paired 64-tick x=.08 CPU cells; no oracle.\n"
        "- Any failure closes the exact warm-state formulation without "
        "searching another state.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
