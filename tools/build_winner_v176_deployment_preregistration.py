#!/usr/bin/env python3
"""Preregister the frozen V121 hierarchy for both V175 checkpoints."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
VALIDATION = ANALYSIS / "winner_v175_recovered_training_validation.json"
CORRECTION = (
    ANALYSIS / "winner_v175_postrecovery_authority_correction.json"
)
V121_CONTRACT = ANALYSIS / "winner_v121_deployment_transform_contract.json"
TRANSFORM_TOOL = ROOT / "tools/build_winner_v176_deployment_policies.py"
OUTPUT = ANALYSIS / "winner_v176_deployment_transform_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V176_DEPLOYMENT_TRANSFORM_PREREGISTRATION_20260725.md"
)
EXPECTED = {
    "validation": (
        "62d21c0aa931a0667b9ee7996a28d39ec3826eda5f37368d1e91b65dd68e3b51"
    ),
    "correction": (
        "40e32b63ec9bb53fe8596638e9bd3bab85fa5c467a633b4d4f1c124fdf701213"
    ),
    "v121_contract": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "transform_tool": (
        "1d499d878647d9211360a986efa3c85a9a9d33f83c78b73628e66a4c09a70aec"
    ),
}
SOURCES = [
    {
        "id": "V176_TANGENT_HALF",
        "step": 1_003_520,
        "filename": "2026_07_25_154038_1003520.onnx",
        "bytes": 954_952,
        "sha256": (
            "e66bd607c01c22a8f732322cd3d7bb46b4208573aa0afed15712de68b8de104e"
        ),
        "output_filename": "winner_v176_tangent_half.onnx",
    },
    {
        "id": "V176_TANGENT_FINAL",
        "step": 2_007_040,
        "filename": "2026_07_25_154426_2007040.onnx",
        "bytes": 954_952,
        "sha256": (
            "35a12863095f3da7be73b7cf1a3ade8f6d3b61930a951944542a115c2ac7e26d"
        ),
        "output_filename": "winner_v176_tangent_final.onnx",
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
            raise FileExistsError(f"refusing to overwrite V176: {path}")
    source_root = args.source_root.resolve()
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    v121 = json.loads(V121_CONTRACT.read_text(encoding="utf-8"))
    input_hashes = {
        "validation": sha256(VALIDATION),
        "correction": sha256(CORRECTION),
        "v121_contract": sha256(V121_CONTRACT),
        "transform_tool": sha256(TRANSFORM_TOOL),
    }
    source_checks = [
        {
            **spec,
            "observed_bytes": (source_root / spec["filename"]).stat().st_size,
            "observed_sha256": sha256(source_root / spec["filename"]),
        }
        for spec in SOURCES
    ]
    checks = {
        "all_input_hashes_exact": input_hashes == EXPECTED,
        "v175_validation_passes": (
            validation.get("status")
            == "PASS_WINNER_V175_RECOVERED_TRAINING_VALIDATION"
            and validation.get("failed_checks") == []
        ),
        "postrecovery_authority_correction_exact": (
            correction.get("status")
            == "PASS_WINNER_V175_POSTRECOVERY_AUTHORITY_CORRECTION"
            and correction.get("failed_checks") == []
            and correction.get("authority", {}).get(
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
    payload = {
        "schema_version": (
            "winner_v176.deployment_transform_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V176_DEPLOYMENT_TRANSFORM"
            if not failed
            else "HOLD_WINNER_V176_DEPLOYMENT_TRANSFORM_PREREGISTRATION"
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
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V176 deployment-transform preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Both V175 post-update raw graphs are frozen.\n"
        "- The exact V121 hierarchy is reused without a new parameter.\n"
        "- No behavior, Gate 5, RDK-X5, or robot authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
