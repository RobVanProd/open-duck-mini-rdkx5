#!/usr/bin/env python3
"""Preregister the exact V121 hierarchy for both V122 checkpoints."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
VALIDATION = ANALYSIS / "winner_v122_recovered_training_validation.json"
V121_CONTRACT = ANALYSIS / "winner_v121_deployment_transform_contract.json"
TRANSFORM_TOOL = ROOT / "tools/build_winner_v123_deployment_policies.py"
OUTPUT = ANALYSIS / "winner_v123_deployment_transform_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V123_DEPLOYMENT_TRANSFORM_PREREGISTRATION_20260724.md"
)
EXPECTED = {
    "validation": (
        "95e8240fa3aae8226a3f2bf2f9658b43ec61ecfd7356713fc3cd4a46146c1256"
    ),
    "v121_contract": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "transform_tool": (
        "d95276ed5ef165a7b5c9d2e7ac285726aa929a8469f566b1c8b017bdbbbdc642"
    ),
}
SOURCES = [
    {
        "id": "V123_EPISODE_PEAK_HALF",
        "step": 1_003_520,
        "filename": "2026_07_24_205623_1003520.onnx",
        "bytes": 954_952,
        "sha256": (
            "7690fe4fd96243917090389921736c57a6c8bfbe34f8be1280a1d7cfe3000dc1"
        ),
        "output_filename": "winner_v123_episode_peak_half.onnx",
    },
    {
        "id": "V123_EPISODE_PEAK_FINAL",
        "step": 2_007_040,
        "filename": "2026_07_24_210008_2007040.onnx",
        "bytes": 954_952,
        "sha256": (
            "20dcb074efd4db65ecdde0efc8e7250369a4102248c2b65d820b8b6c016e27b6"
        ),
        "output_filename": "winner_v123_episode_peak_final.onnx",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V123: {path}")
    source_root = args.source_root.resolve()
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    v121 = json.loads(V121_CONTRACT.read_text(encoding="utf-8"))
    input_hashes = {
        "validation": sha256(VALIDATION),
        "v121_contract": sha256(V121_CONTRACT),
        "transform_tool": sha256(TRANSFORM_TOOL),
    }
    source_checks = [
        {
            **spec,
            "observed_bytes": (
                source_root / spec["filename"]
            ).stat().st_size,
            "observed_sha256": sha256(
                source_root / spec["filename"]
            ),
        }
        for spec in SOURCES
    ]
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v122_validation_passes": (
            validation.get("status")
            == "PASS_WINNER_V122_RECOVERED_TRAINING_VALIDATION"
            and validation.get("failed_checks") == []
            and validation.get("authority", {}).get(
                "deployment_transform_preregistration_authorized"
            )
            is True
        ),
        "v121_transform_contract_exact_green": (
            v121.get("status")
            == "PASS_WINNER_V121_DEPLOYMENT_TRANSFORM_CONTRACT"
            and v121.get("failed_checks") == []
        ),
        "both_postupdate_raw_sources_exact": all(
            row["observed_bytes"] == row["bytes"]
            and row["observed_sha256"] == row["sha256"]
            for row in source_checks
        ),
        "transform_reused_without_parameter_search": True,
        "formal_behavior_not_run": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": (
            "winner_v123.deployment_transform_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V123_DEPLOYMENT_TRANSFORM"
            if not failed
            else "HOLD_WINNER_V123_DEPLOYMENT_TRANSFORM_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": input_hashes,
        "sources": SOURCES,
        "transform": v121["transform"],
        "classification": {
            "new_training": False,
            "new_transform_parameter": False,
            "checkpoint_selection": False,
            "formal_behavior_cells": 0,
        },
        "authority": {
            "transform_execution_authorized": not failed,
            "behavior_evaluation_authorized": False,
            "full_matrix_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "robot_clearance": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v123 deployment-transform preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "Both V122 post-update raw graphs are frozen. V123 reuses the exact "
        "V121 G3/deadband/trained-delta hierarchy without a new parameter or "
        "training run. No behavior, Gate 5, RDK-X5, or robot authority.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
