#!/usr/bin/env python3
"""Narrow shape-corrected wrapper for the frozen Winner-v41 screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))

import run_winner_v41_static_equilibrium_target_feasibility as v41  # noqa: E402


CORRECTION = ANALYSIS / "winner_v41_v2_runner_correction_preregistration.json"
FAILURE_RECEIPT = ANALYSIS / "winner_v41_first_attempt_failure_receipt.json"


def lf_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_correction(value: Mapping[str, Any]) -> None:
    if (
        value.get("status") != "PREREGISTERED_WINNER_V41_V2_RUNNER_CORRECTION"
        or value.get("decision") != "AUTHORIZE_ONE_CORRECTED_CPU_ONLY_V41_SCREEN"
        or value.get("correction") != {
            "old_call": "v38.expand_mirrored_blocks(coordinates[None, :])",
            "new_call": "coordinates @ v38.MIRROR_MATRIX.T into the same six indices",
            "changed_behavior": "accept exactly one three-coordinate static target",
            "unchanged_behavior": (
                "grid, basis, action boundary, plants, duration, selection, pass rule, "
                "execution counts, and authority"
            ),
        }
    ):
        raise ValueError("Winner-v41-v2 correction changed")
    if value.get("execution_now") != {
        "static_target_candidates": 0,
        "candidate_plant_cells": 0,
        "optimizer_updates": 0,
        "locomotion_training_steps": 0,
        "robot_or_rdk_access": 0,
    }:
        raise ValueError("Winner-v41-v2 execution authority changed")
    sources = value.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise ValueError("Winner-v41-v2 sources are absent")
    for name, item in sources.items():
        if item.get("hash_mode") != "lf" or lf_sha256(ROOT / item["path"]) != item.get("sha256"):
            raise ValueError(f"Winner-v41-v2 source changed: {name}")
    if canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v41-v2 source manifest changed")


def expand_static_target(blocks: Any) -> np.ndarray:
    values = np.asarray(blocks, dtype=np.float32)
    if values.shape != (1, 3) or not np.all(np.isfinite(values)):
        raise ValueError("Winner-v41-v2 static target shape changed")
    expanded = np.zeros((1, 14), dtype=np.float32)
    expanded[:, np.asarray(v41.PITCH_INDICES, dtype=np.int64)] = (
        values @ v41.v38.MIRROR_MATRIX.T
    )
    return expanded


def output_path(argv: list[str]) -> Path:
    if "--output" not in argv:
        raise ValueError("Winner-v41-v2 output argument absent")
    index = argv.index("--output")
    if index + 1 >= len(argv):
        raise ValueError("Winner-v41-v2 output argument incomplete")
    return Path(argv[index + 1])


def main() -> int:
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    validate_correction(correction)
    failure = json.loads(FAILURE_RECEIPT.read_text(encoding="utf-8"))
    if (
        failure.get("status") != "INVALID_WINNER_V41_FIRST_ATTEMPT_NO_RESULT"
        or failure.get("github_run", {}).get("run_id") != 29901924055
        or failure.get("work_executed", {}).get("candidate_plant_cells") != 0
    ):
        raise ValueError("Winner-v41 first-attempt receipt changed")
    v41.v38.expand_mirrored_blocks = expand_static_target
    code = v41.main()
    path = output_path(sys.argv[1:])
    result = json.loads(path.read_text(encoding="utf-8"))
    if result.get("schema_version") != "winner_v41.static_equilibrium_target_feasibility_result.v1":
        raise ValueError("Winner-v41 base result changed")
    result["schema_version"] = "winner_v41.static_equilibrium_target_feasibility_result.v2"
    result["correction"] = {
        "first_attempt_run_id": 29901924055,
        "first_attempt_candidate_plant_cells": 0,
        "failure_receipt_lf_sha256": lf_sha256(FAILURE_RECEIPT),
        "correction_preregistration_lf_sha256": lf_sha256(CORRECTION),
        "correction_runner_lf_sha256": lf_sha256(Path(__file__)),
        "scope": "single-target mirror expansion shape only",
    }
    result["sources"] = {
        **result["sources"],
        "correction_preregistration_lf_sha256": lf_sha256(CORRECTION),
        "correction_runner_lf_sha256": lf_sha256(Path(__file__)),
        "first_attempt_failure_receipt_lf_sha256": lf_sha256(FAILURE_RECEIPT),
    }
    path.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
