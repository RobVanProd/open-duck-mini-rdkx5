#!/usr/bin/env python3
"""Preregister the eight-cell V131 two-fit oracle teacher screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
RUNNER = ROOT / "tools/run_winner_v131_two_fit_oracle_behavior.py"
CPU_CONTRACT = ANALYSIS / "winner_v131_two_fit_oracle_cpu_contract.json"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
PROJECTOR = ROOT / "tools/exact_torque_oracle_two_fit.py"
OUTPUT = (
    ANALYSIS / "winner_v131_two_fit_oracle_behavior_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_PREREGISTRATION_20260724.md"
)
EXPECTED = {
    "runner": (
        "b17b8baf51fa9a67ff01acb8e316b44046ab806fb672f0b2cb182c2e139cb8b8"
    ),
    "cpu_contract": (
        "73aea66c4d79beef8d78829ff909eac94d39b2289f822a3de8d1a89476ed56a8"
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


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluator-root", type=Path, required=True)
    args = parser.parse_args()
    evaluator_root = args.evaluator_root.resolve()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V131 behavior: {path}")
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    cpu = json.loads(CPU_CONTRACT.read_text(encoding="utf-8"))
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    matrix = [
        row
        for row in v126["matrix"]["rows"]
        if row["checkpoint_id"] == "V121_TRAIN_MATCHED_FINAL"
    ]
    input_hashes = {
        "runner": sha256(RUNNER),
        "cpu_contract": sha256(CPU_CONTRACT),
        "v126_preregistration": sha256(V126_PREREG),
        "base_preregistration": sha256(BASE_PREREG),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator_path),
        "two_fit_projector": sha256(PROJECTOR),
    }
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "cpu_contract_green": (
            cpu.get("status")
            == "PASS_WINNER_V131_TWO_FIT_ORACLE_CPU_CONTRACT"
            and cpu.get("failed_checks") == []
            and cpu.get("decision")
            == "EARN_ONE_V131_FINAL_TEACHER_8_CELL_PREREGISTRATION"
        ),
        "matrix_exact_8": (
            len(matrix) == 8
            and {float(row["command_x_m_s"]) for row in matrix}
            == {0.0, 0.074, 0.077, 0.08}
            and {str(row["plant"]) for row in matrix}
            == {
                "P30_ALL_JOINT",
                "P31_34_PITCH_WITH_P30_NONPITCH",
            }
            and all(int(row["duration_ticks"]) == 600 for row in matrix)
        ),
        "one_source_checkpoint_only": True,
        "full_horizon_cpu_only": True,
        "training_not_authorized": True,
        "robot_surface_absent": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v131.two_fit_oracle_behavior_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR"
            if not failed
            else "HOLD_WINNER_V131_TWO_FIT_ORACLE_BEHAVIOR_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "source": {
            "checkpoint_id": "V121_TRAIN_MATCHED_FINAL",
            "policy_sha256": (
                "bc54ea1bf39e617f76771e7416de91db2ccfe0b1bf903de08faaa64a67ce4aab"
            ),
            "selection": (
                "mechanism-derived teacher; V121 half has zero single-fit "
                "oracle corrections"
            ),
        },
        "matrix": {
            "rows": matrix,
            "sha256": canonical_sha256(matrix),
            "cells": 8,
            "ticks_per_cell": 600,
        },
        "pass_rule": {
            "behavior": "all eight frozen V126 cell criteria pass",
            "moving_rows": (
                "all 3,600 moving ticks have robust_safe=true and zero "
                "empty two-fit intersections"
            ),
            "x0": "all 1,200 rows take the exact zero deadband bypass",
            "nontrivial": "at least one shared projection occurs",
            "primary_prediction": (
                "exact matured force with zero nonempty or unscheduled "
                "residual violation"
            ),
        },
        "stop_rule": (
            "any cell failure closes the two-fit teacher without distillation; "
            "a pass authorizes only a read-only robust-teacher dataset audit"
        ),
        "authority": {
            "formal_behavior_cells": 8 if not failed else 0,
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
        "# Winner V131 two-fit oracle behavior preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Eight CPU cells: one final checkpoint, four commands, two measured "
        "actuator fits, 600 ticks each.\n"
        "- Every moving tick must have one action safe under both fits.\n"
        "- No policy training, Colab, RDK, torque, or motion is authorized.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"matrix_sha256={payload['matrix']['sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
