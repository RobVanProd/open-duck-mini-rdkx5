#!/usr/bin/env python3
"""Preregister one deterministic V116 multi-joint rate projection."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CORRECTION = (
    ANALYSIS / "winner_v115_nominal_failure_attribution_v2_correction.json"
)
SOURCE_CONTRACT = ANALYSIS / "winner_v115_postexport_transform_contract.json"
TRANSFORM = ROOT / "tools/build_winner_v116_rate_projection_policies.py"
OUTPUT = ANALYSIS / "winner_v116_rate_projection_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V116_RATE_PROJECTION_PREREGISTRATION_20260724.md"
)
EXPECTED_HASHES = {
    "v115_attribution_correction": (
        "fe970d631f0c089a4cddc5abcb63b527b69450f993aa4985013762982a5fae80"
    ),
    "v115_source_contract": (
        "bcbc71eda01eae4a50435a1c9356a048ae4fceec78c4f8f5382d223b7df88ac3"
    ),
    "transform_tool": (
        "cf0907ac316726812e9d9379e8356b408cb61cee3e6f2bfeae946e0fcb0cbdc0"
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
    parser.add_argument("--source-root", type=Path, required=True)
    args = parser.parse_args()
    for path in (OUTPUT, MARKDOWN):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V116: {path}")
    source_root = args.source_root.resolve()
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    source_contract = json.loads(
        SOURCE_CONTRACT.read_text(encoding="utf-8")
    )
    hashes = {
        "v115_attribution_correction": sha256(CORRECTION),
        "v115_source_contract": sha256(SOURCE_CONTRACT),
        "transform_tool": sha256(TRANSFORM),
    }
    sources = [
        {
            "id": (
                "V116_RATE_PROJECTED_HALF"
                if row["step"] == 1_003_520
                else "V116_RATE_PROJECTED_FINAL"
            ),
            "step": row["step"],
            "filename": Path(row["output_path"]).name,
            "output_filename": (
                "V116_RATE_PROJECTED_1003520.onnx"
                if row["step"] == 1_003_520
                else "V116_RATE_PROJECTED_2007040.onnx"
            ),
            "sha256": row["output_sha256"],
            "bytes": row["output_bytes"],
        }
        for row in source_contract["policies"]
    ]
    source_files_exact = all(
        (source_root / row["filename"]).stat().st_size == row["bytes"]
        and sha256(source_root / row["filename"]) == row["sha256"]
        for row in sources
    )
    joints = correction["derivation"]["joints"]
    projection = {
        "formula": correction["derivation"]["formula"],
        "affected_joints": correction["derivation"]["affected_joints"],
        "current_rate_limit_rad_s": [
            row["current_rate_limit_rad_s"] for row in joints
        ],
        "selected_rate_limit_rad_s": [
            row["selected_rate_limit_rad_s"] for row in joints
        ],
        "current_normalized_action_delta": [
            row["current_normalized_action_delta"] for row in joints
        ],
        "selected_normalized_action_delta": [
            row["selected_normalized_action_delta"] for row in joints
        ],
        "candidate_vectors": 1,
        "scalar_search": False,
        "apply_identically_to_both_checkpoints": True,
    }
    checks = {
        "attribution_correction_exact": (
            hashes["v115_attribution_correction"]
            == EXPECTED_HASHES["v115_attribution_correction"]
            and correction.get("status")
            == "PASS_WINNER_V115_NOMINAL_FAILURE_ATTRIBUTION_V2_REPORTING_CORRECTED"
            and correction.get("failed_checks") == []
            and correction.get("authority", {}).get(
                "rate_projection_preregistration_authorized"
            )
            is True
        ),
        "source_contract_exact": (
            hashes["v115_source_contract"]
            == EXPECTED_HASHES["v115_source_contract"]
            and source_contract.get("status")
            == "PASS_WINNER_V115_POSTEXPORT_TRANSFORM_CONTRACT"
        ),
        "transform_tool_exact": (
            hashes["transform_tool"] == EXPECTED_HASHES["transform_tool"]
        ),
        "all_hashes_exact": hashes == EXPECTED_HASHES,
        "two_source_files_exact": source_files_exact and len(sources) == 2,
        "one_vector_only": projection["candidate_vectors"] == 1,
        "no_scalar_search": projection["scalar_search"] is False,
        "both_checkpoints_required": True,
        "formal_behavior_cells_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": "winner_v116.rate_projection_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V116_RATE_PROJECTION"
            if not failed
            else "HOLD_WINNER_V116_RATE_PROJECTION_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": hashes,
        "sources": sources,
        "projection": projection,
        "execution_now": {
            "policies_transformed": 0,
            "formal_behavior_cells": 0,
            "training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "cpu_transform_authorized": not failed,
            "behavior_evaluation_authorized": False,
            "training_authorized": False,
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
        "# Winner-v116 rate projection preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "One evidence-derived rate vector is frozen for both post-update "
        "policies. It changes only `max_action_delta`; no weights, nodes, "
        "observation fields, action scale, gate, training, or behavior cell "
        "may change here.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
