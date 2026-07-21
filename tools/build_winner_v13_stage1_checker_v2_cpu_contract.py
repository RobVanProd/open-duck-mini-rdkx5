#!/usr/bin/env python3
"""Freeze the Winner-v13 Stage-1 corrected-checker CPU contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v13_stage1_checker_v2_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V13_STAGE1_CHECKER_V2_CPU_CONTRACT_20260721.md"
INVALID = ANALYSIS / "winner_v13_normalized_response_stage1_invalid_attribution.json"
SERIALIZATION_ATTRIBUTION = (
    ANALYSIS / "winner_v13_stage1_checker_v2_cpu_serialization_failure_attribution.json"
)
SOURCES = {
    "builder": Path("tools/build_winner_v13_stage1_checker_v2_cpu_contract.py"),
    "runner": Path("tools/run_winner_v13_stage1_checker_v2_cpu_contract.py"),
    "tests": Path("tests/test_winner_v13_stage1_checker_v2_cpu_contract.py"),
    "workflow": Path(".github/workflows/winner-v13-stage1-checker-v2-cpu-contract.yml"),
    "invalid_attribution": Path(
        "outputs/analysis/winner_v13_normalized_response_stage1_invalid_attribution.json"
    ),
    "serialization_failure_attribution": Path(
        "outputs/analysis/winner_v13_stage1_checker_v2_cpu_serialization_failure_attribution.json"
    ),
    "v13_primitives": Path("patches/winner_v13_normalized_calibrator_training.py"),
    "network": Path("patches/winner_v12_decomposed_backend_networks.py"),
    "onnx_checker": Path("tools/run_winner_v12_calibrator_cpu_smoke.py"),
}


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--markdown", type=Path, default=MARKDOWN)
    args = parser.parse_args()
    for path in (args.output, args.markdown):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite checker-v2 contract: {path}")
    invalid = json.loads(INVALID.read_text(encoding="utf-8"))
    if (
        invalid.get("status") != "INVALID_WINNER_V13_STAGE1_DECISION_CONTRACT"
        or invalid.get("required_correction", {}).get("cpu_contract_before_rerun")
        is not True
    ):
        raise ValueError("invalid attribution does not select this CPU contract")
    serialization = json.loads(SERIALIZATION_ATTRIBUTION.read_text(encoding="utf-8"))
    if (
        serialization.get("status") != "INVALID_ZERO_RESULT_SERIALIZATION_FAILURE"
        or serialization.get("artifact", {}).get("result_present") is not False
        or serialization.get("decision")
        != "CORRECT_SERIALIZATION_AND_LAUNCH_FRESH_ZERO_CELL_CONTRACT"
    ):
        raise ValueError("serialization attribution does not select a fresh contract")
    sources = {
        name: {
            "path": str(path).replace("\\", "/"),
            "hash_mode": "lf",
            "sha256": lf_sha256(ROOT / path),
        }
        for name, path in SOURCES.items()
    }
    payload = {
        "schema_version": "winner_v13.stage1_checker_v2_cpu_contract.v2",
        "status": "FROZEN_WINNER_V13_STAGE1_CHECKER_V2_CPU_CONTRACT",
        "decision": "AUTHORIZE_ONE_ZERO_CELL_CHECKER_PROOF_ONLY",
        "correction": {
            "cases": 256,
            "seed": 131314,
            "comparison": (
                "ONNX and JAX receive the identical observation, externally realized "
                "previous_action, and h_in on every independent case"
            ),
            "maximum_error": 1e-7,
            "action_semantics": (
                "A zero action head produces exact zero only when previous_action permits "
                "it; otherwise the frozen slew projection returns a bounded step toward zero."
            ),
            "learning_rate_for_fresh_run": 0.0001,
            "serialization": "all comparison checks are converted to native bool",
        },
        "pass_rule": (
            "All same-input action/state checks, standard deployable graph checks, and the "
            "correct learning-rate assertion must pass."
        ),
        "execution_now": {
            "optimizer_updates": 0,
            "simulation_cells": 0,
            "formal_support_cells": 0,
            "locomotion_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "robot_clearance": False,
            "pass_authorizes_only": "a fresh corrected Stage-1 v2 preregistration",
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
    }
    args.output.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v13 Stage-1 corrected-checker CPU contract",
                "",
                f"- Status: `{payload['status']}`",
                f"- Decision: `{payload['decision']}`",
                "- Same-input cases: `256`",
                "- Optimizer / simulator / locomotion / robot: `0 / 0 / 0 / 0`",
                "- Correct Stage-1 learning rate: `1e-4`",
                "",
                "This proves the checker correction without training. A pass authorizes",
                "only a fresh corrected Stage-1 preregistration.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
