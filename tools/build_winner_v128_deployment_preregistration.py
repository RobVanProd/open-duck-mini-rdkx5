#!/usr/bin/env python3
"""Preregister the exact V121 hierarchy for both V127 checkpoints."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
VALIDATION = ANALYSIS / "winner_v127_recovered_training_validation.json"
V121_CONTRACT = ANALYSIS / "winner_v121_deployment_transform_contract.json"
TRANSFORM_TOOL = ROOT / "tools/build_winner_v128_deployment_policies.py"
OUTPUT = ANALYSIS / "winner_v128_deployment_transform_preregistration.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V128_DEPLOYMENT_TRANSFORM_PREREGISTRATION_20260724.md"
)
EXPECTED = {
    "validation": (
        "d1936251394926a9bbc605e331158fd7a1cd49dbbea9e808093d1f688fec8a80"
    ),
    "v121_contract": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
    "transform_tool": (
        "29c8acf914596984648d0188503793d2de22764e1bd8d6a91a4d9c2a33e17bb6"
    ),
}
SOURCES = [
    {
        "id": "V128_CONSTRAINED_HALF",
        "step": 1_003_520,
        "filename": "2026_07_25_020309_1003520.onnx",
        "bytes": 954_952,
        "sha256": (
            "685c1b7053943d4340346777420198bba6e77eaf8521c5156f6025b1485a8247"
        ),
        "output_filename": "winner_v128_constrained_half.onnx",
    },
    {
        "id": "V128_CONSTRAINED_FINAL",
        "step": 2_007_040,
        "filename": "2026_07_25_020652_2007040.onnx",
        "bytes": 954_952,
        "sha256": (
            "9f67fc3539963f682ba1361debf26ff35961bb9e3b787a3aa8e60fa7bc77a837"
        ),
        "output_filename": "winner_v128_constrained_final.onnx",
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
            raise FileExistsError(f"refusing to overwrite V128: {path}")
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
        "v127_validation_passes": (
            validation.get("status")
            == "PASS_WINNER_V127_RECOVERED_TRAINING_VALIDATION"
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
    payload = {
        "schema_version": (
            "winner_v128.deployment_transform_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V128_DEPLOYMENT_TRANSFORM"
            if not failed
            else "HOLD_WINNER_V128_DEPLOYMENT_TRANSFORM_PREREGISTRATION"
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
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V128 deployment-transform preregistration\n\n"
        f"- Status: `{payload['status']}`\n"
        "- Both V127 post-update sources are frozen.\n"
        "- The exact V121 hierarchy is reused without a new parameter.\n"
        "- No behavior, Gate 5, RDK-X5, or robot authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
