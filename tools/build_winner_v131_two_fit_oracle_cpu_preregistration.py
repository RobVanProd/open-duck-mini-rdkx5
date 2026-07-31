#!/usr/bin/env python3
"""Preregister the two-cell V131 exact two-fit oracle CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/run_winner_v131_two_fit_oracle_cpu_contract.py"
COMPOSER = ROOT / "tools/compose_winner_v131_two_fit_oracle_evaluator.py"
PROJECTOR = ROOT / "tools/exact_torque_oracle_two_fit.py"
V130 = ANALYSIS / "winner_v130_oracle_correction_feature_audit.json"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
OUTPUT = ANALYSIS / "winner_v131_two_fit_oracle_cpu_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V131_TWO_FIT_ORACLE_CPU_PREREGISTRATION_20260724.md"
)
EXPECTED = {
    "runner": (
        "da26e195dae23d59968d01cb2b05d4c8277d24f09989df0bb02c2aa8c870fc91"
    ),
    "v130_result": (
        "7b4078c3ea18c3a3e1d129de3329cca8e71d178d93b836ba37f552544bed33d7"
    ),
    "v126_preregistration": (
        "eb40f17d9c08b8362f068567e1620bdafef21ad9123a633c9536f3637a31c899"
    ),
    "base_preregistration": (
        "c8f986ceb24863f33c1fc99170548d2e255cb6a26737d3f74762f8dcd4485a24"
    ),
    "composition_manifest": (
        "6dc9332fe32b275f3f1788a017c626b830fae71458c5d9d0286051499332562d"
    ),
    "composed_evaluator": (
        "3e71d2c9fce67aee83528c60b1bf888deda160d8f53035eff7b30ba64e46161b"
    ),
    "composer": (
        "4e37d442b2234525d1d4e0a3d5a162b7f131b1f9b5245e3f2b46104f1f60e25c"
    ),
    "two_fit_projector": (
        "c9894fa982d0837fbd6281dc778248365c9079e60680c928fd34a50c2e55eb27"
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
    evaluator_root = args.evaluator_root.resolve()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V131: {path}")
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    v130 = json.loads(V130.read_text(encoding="utf-8"))
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    input_hashes = {
        "runner": sha256(RUNNER),
        "v130_result": sha256(V130),
        "v126_preregistration": sha256(V126_PREREG),
        "base_preregistration": sha256(BASE_PREREG),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator_path),
        "composer": sha256(COMPOSER),
        "two_fit_projector": sha256(PROJECTOR),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v130_rejects_static_linear_readout": (
            v130.get("status")
            == "PASS_WINNER_V130_ORACLE_CORRECTION_FEATURE_AUDIT"
            and v130.get("decision") == "NO_OBSERVATION_RESIDUAL_TRAINING"
        ),
        "v126_single_fit_teacher_exists": (
            v126.get("status")
            == "PREREGISTERED_WINNER_V126_ALL_TICK_SUPREME_CLIP"
        ),
        "composition_green": (
            manifest.get("status")
            == "PASS_WINNER_V131_TWO_FIT_EVALUATOR_COMPOSITION"
        ),
        "two_nonformal_cells_only": True,
        "zero_training_or_behavior_gate": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v131.two_fit_oracle_cpu_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V131_TWO_FIT_ORACLE_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V131_TWO_FIT_ORACLE_CPU_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "mechanism": {
            "source_policy": "V121_TRAIN_MATCHED_FINAL",
            "active_plants": [
                "P30_ALL_JOINT",
                "P31_34_PITCH_WITH_P30_NONPITCH",
            ],
            "shadow_fit": "the other measured fit in each active cell",
            "projection": (
                "alternate exact simulator projections until one action is "
                "inside the frozen torque box under both measured fits"
            ),
            "action_constraints": (
                "absolute + frozen rate + actual-centered guard remain supreme"
            ),
        },
        "matrix": {
            "cells": 2,
            "command_x_m_s": 0.08,
            "duration_ticks": 64,
            "seed": 167931544,
            "formal_behavior_cells": 0,
        },
        "pass_rule": {
            "duration": "both cells complete all 64 ticks",
            "coverage": "all 128 moving rows use the two-fit oracle",
            "common_action": "robust_safe true and zero empty rows on every tick",
            "nontrivial": "at least one shared projection occurs",
            "primary_fit": (
                "prediction exact, zero prediction mismatches, and zero "
                "nonempty residual torque violations"
            ),
        },
        "stop_rule": (
            "any failed contract check closes the two-fit teacher screen "
            "without an eight-cell run or training"
        ),
        "authority": {
            "cpu_contract": not failed,
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
        "# Winner V131 two-fit oracle CPU preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Two x=.08 cells, 64 ticks each, CPU only.\n"
        "- Every action must be torque-safe under both measured actuator fits.\n"
        "- No behavior gate, training, Colab, RDK, torque, or motion is "
        "authorized.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
