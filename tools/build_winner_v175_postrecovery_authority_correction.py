#!/usr/bin/env python3
"""Correct V175's post-recovery authority to require deployment wrapping."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
VALIDATION = ANALYSIS / "winner_v175_recovered_training_validation.json"
V121_TRANSFORM = ANALYSIS / "winner_v121_deployment_transform_contract.json"
OUTPUT = ANALYSIS / "winner_v175_postrecovery_authority_correction.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V175_POSTRECOVERY_AUTHORITY_CORRECTION_20260725.md"
)
EXPECTED = {
    "validation": (
        "62d21c0aa931a0667b9ee7996a28d39ec3826eda5f37368d1e91b65dd68e3b51"
    ),
    "v121_transform": (
        "4bd5eab5343cd8401db1789773fa3cc345727d903cb31222e0ea9870f0e9e640"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V175: {path}")
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    transform = json.loads(V121_TRANSFORM.read_text(encoding="utf-8"))
    hashes = {
        "validation": sha256(VALIDATION),
        "v121_transform": sha256(V121_TRANSFORM),
    }
    checks = {
        "input_hashes_exact": hashes == EXPECTED,
        "recovery_validation_green": (
            validation.get("status")
            == "PASS_WINNER_V175_RECOVERED_TRAINING_VALIDATION"
            and validation.get("failed_checks") == []
        ),
        "recovered_graphs_are_raw_training_exports": (
            [row["sha256"] for row in validation["onnx"]]
            == [
                (
                    "2d3cfb686a9c9643d9414a99a10e4db3aee7fc8f63cbc2fd81f107b487cf1311"
                ),
                (
                    "e66bd607c01c22a8f732322cd3d7bb46b4208573aa0afed15712de68b8de104e"
                ),
                (
                    "35a12863095f3da7be73b7cf1a3ade8f6d3b61930a951944542a115c2ac7e26d"
                ),
            ]
        ),
        "v121_deployment_hierarchy_green": (
            transform.get("status")
            == "PASS_WINNER_V121_DEPLOYMENT_TRANSFORM_CONTRACT"
            and transform.get("failed_checks") == []
        ),
        "no_behavior_training_or_hardware": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": (
            "winner_v175.postrecovery_authority_correction.v1"
        ),
        "status": (
            "PASS_WINNER_V175_POSTRECOVERY_AUTHORITY_CORRECTION"
            if not failed
            else "HOLD_WINNER_V175_POSTRECOVERY_AUTHORITY_CORRECTION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": hashes,
        "correction": {
            "superseded_authority": (
                "nominal_behavior_preregistration_authorized"
            ),
            "correct_authority": (
                "deployment_transform_preregistration_authorized"
            ),
            "reason": (
                "the recovered 954,952-byte ONNX files are raw training "
                "exports; the exact frozen V121 deployment hierarchy must be "
                "applied uniformly before any nominal behavior cell"
            ),
            "evidence_or_metric_change": False,
            "training_or_transform_change": False,
        },
        "authority": {
            "deployment_transform_preregistration_authorized": not failed,
            "transform_execution_authorized": False,
            "behavior_evaluation_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V175 post-recovery authority correction\n\n"
        f"- Status: `{payload['status']}`\n"
        "- The recovered ONNX files are raw training exports.\n"
        "- Apply the exact V121 deployment hierarchy uniformly to half and "
        "final before behavior evaluation.\n"
        "- This correction changes no evidence, metric, policy parameter, or "
        "gate.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
