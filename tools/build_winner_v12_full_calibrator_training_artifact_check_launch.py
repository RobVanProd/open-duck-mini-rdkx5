#!/usr/bin/env python3
"""Freeze one raw-ZIP verification launch for the completed Winner-v12 training."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v12_full_calibrator_training_artifact_check_launch.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V12_FULL_CALIBRATOR_TRAINING_ARTIFACT_CHECK_LAUNCH_20260721.md"
)
EXPECTED_RUN_ID = 29808732634
EXPECTED_RUN_ATTEMPT = 1
EXPECTED_RUN_HEAD_SHA = "30ba44b2461d0f11da77ebfe42ac30446682c22d"
EXPECTED_ARTIFACT_NAME = f"winner-v12-full-calibrator-training-{EXPECTED_RUN_ID}"
SOURCE_PATHS = {
    "builder": Path(
        "tools/build_winner_v12_full_calibrator_training_artifact_check_launch.py"
    ),
    "workflow": Path(
        ".github/workflows/winner-v12-full-calibrator-training-artifact-check.yml"
    ),
    "artifact_verifier": Path(
        "tools/check_winner_v12_full_calibrator_training_artifact.py"
    ),
    "artifact_verifier_tests": Path(
        "tests/test_winner_v12_full_calibrator_training_artifact_check.py"
    ),
    "artifact_check_importer": Path(
        "tools/import_winner_v12_full_calibrator_training_artifact_check.py"
    ),
    "artifact_check_importer_tests": Path(
        "tests/test_winner_v12_full_calibrator_training_artifact_check_import.py"
    ),
    "support_contract_builder": Path(
        "tools/build_winner_v12_calibrator_support_gate_cpu_contract.py"
    ),
    "support_contract_builder_tests": Path(
        "tests/test_winner_v12_calibrator_support_gate_cpu_contract_builder.py"
    ),
    "training_launch_contract": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_launch_contract.json"
    ),
    "training_authorization_claim": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_authorization_claim.json"
    ),
    "corrected_cpu_result": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_cpu_contract_result_v2.json"
    ),
    "training_preregistration": Path(
        "outputs/analysis/winner_v12_full_calibrator_training_preregistration.json"
    ),
    "training_runner": Path("tools/run_winner_v12_full_calibrator_training.py"),
    "cpu_smoke": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
    "training_primitives": Path("patches/winner_v12_calibrator_training.py"),
    "deployable_network": Path("patches/winner_v12_decomposed_backend_networks.py"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def require_sha256(value: str, label: str) -> None:
    if len(value) != 64 or any(
        character not in "0123456789abcdef" for character in value
    ):
        raise ValueError(f"{label} SHA-256 is malformed")


def validate_launch_inputs(
    *,
    artifact_id: int,
    artifact_name: str,
    artifact_digest: str,
    artifact_zip_sha256: str,
    training_result_sha256: str,
) -> None:
    require_sha256(artifact_zip_sha256, "artifact ZIP")
    require_sha256(training_result_sha256, "training result")
    if (
        artifact_id <= 0
        or artifact_name != EXPECTED_ARTIFACT_NAME
        or artifact_digest != f"sha256:{artifact_zip_sha256}"
    ):
        raise ValueError("training artifact launch attribution changed")


def source_manifest() -> dict[str, dict[str, str]]:
    return {
        name: {
            "path": str(relative).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / relative),
        }
        for name, relative in SOURCE_PATHS.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-id", type=int, required=True)
    parser.add_argument("--artifact-name", required=True)
    parser.add_argument("--artifact-digest", required=True)
    parser.add_argument("--artifact-zip-sha256", required=True)
    parser.add_argument("--training-result-sha256", required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(
                f"refusing to overwrite artifact-check launch: {path}"
            )
    validate_launch_inputs(
        artifact_id=args.artifact_id,
        artifact_name=args.artifact_name,
        artifact_digest=args.artifact_digest,
        artifact_zip_sha256=args.artifact_zip_sha256,
        training_result_sha256=args.training_result_sha256,
    )
    sources = source_manifest()
    payload = {
        "schema_version": "winner_v12.full_calibrator_training_artifact_check_launch.v1",
        "status": "PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_ARTIFACT_CHECK_LAUNCH_FROZEN",
        "decision": "AUTHORIZE_ONE_RAW_ZIP_ARTIFACT_VERIFICATION_ONLY",
        "repository_attribution": {
            "repository": "RobVanProd/open-duck-mini-rdkx5",
            "github_run_id": EXPECTED_RUN_ID,
            "github_run_attempt": EXPECTED_RUN_ATTEMPT,
            "github_run_head_sha": EXPECTED_RUN_HEAD_SHA,
            "github_artifact_id": args.artifact_id,
            "github_artifact_name": args.artifact_name,
            "github_artifact_digest": args.artifact_digest,
        },
        "expected_hashes": {
            "artifact_zip_sha256": args.artifact_zip_sha256,
            "training_result_sha256": args.training_result_sha256,
        },
        "execution_now": {
            "artifact_verifications": 0,
            "formal_support_cells": 0,
            "locomotion_training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
            "pass_authorizes_only": "the already preregistered zero-cell support-gate CPU contract",
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v12 full-calibrator artifact-check launch",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                f"- Training run: `{EXPECTED_RUN_ID}` attempt `{EXPECTED_RUN_ATTEMPT}`",
                f"- Training head: `{EXPECTED_RUN_HEAD_SHA}`",
                f"- Artifact ID: `{args.artifact_id}`",
                f"- Artifact ZIP SHA-256: `{args.artifact_zip_sha256}`",
                f"- Training result SHA-256: `{args.training_result_sha256}`",
                "- Formal support cells / locomotion / robot access: `0 / 0 / 0`",
                "",
                "This launch authorizes one independent verification of the exact raw",
                "GitHub artifact ZIP. It does not authorize support cells, locomotion,",
                "deployment, Gate 5, or robot access.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": payload["status"], "sha256": lf_sha256(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
