#!/usr/bin/env python3
"""Preregister one deterministic V118 post-G3 rate vector."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
ATTRIBUTION = (
    ANALYSIS / "winner_v117_nominal_failure_attribution.json"
)
SOURCE_CONTRACT = (
    ANALYSIS / "winner_v117_postguard_rate_projection_contract.json"
)
RESULT = ANALYSIS / "winner_v117_nominal_behavior_result.json"
TRANSFORM = ROOT / "tools/build_winner_v118_rate_projection_policies.py"
OUTPUT = ANALYSIS / "winner_v118_rate_projection_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V118_RATE_PROJECTION_PREREGISTRATION_20260724.md"
)
EXPECTED_HASHES = {
    "v117_attribution": (
        "e52efe6c48cb7a25c1d9f15df8cde9d10de830dde2dceddbdc642e97e9d48893"
    ),
    "v117_source_contract": (
        "9aab1d09ffcff7608fa758ea891f4b2a6c54d90b00a056a4478c503514d05beb"
    ),
    "v117_nominal_result": (
        "0a3d04b478e46c5041b52554008cb5e8db800f0a2552932cd60cb8640efee09a"
    ),
    "transform_tool": (
        "31b8a5e7c15b53466b0c1d0ed5d379793dfac5c924282386440476c6f9fbcb25"
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
            raise FileExistsError(f"refusing to overwrite V118: {path}")

    source_root = args.source_root.resolve()
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    source_contract = json.loads(
        SOURCE_CONTRACT.read_text(encoding="utf-8")
    )
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    hashes = {
        "v117_attribution": sha256(ATTRIBUTION),
        "v117_source_contract": sha256(SOURCE_CONTRACT),
        "v117_nominal_result": sha256(RESULT),
        "transform_tool": sha256(TRANSFORM),
    }
    sources = [
        {
            "id": (
                "V118_RATE_PROJECTED_HALF"
                if row["step"] == 1_003_520
                else "V118_RATE_PROJECTED_FINAL"
            ),
            "step": row["step"],
            "filename": Path(row["output_path"]).name,
            "output_filename": (
                "V118_RATE_PROJECTED_1003520.onnx"
                if row["step"] == 1_003_520
                else "V118_RATE_PROJECTED_2007040.onnx"
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
    joints = attribution["derivation"]["joints"]
    source_projection = source_contract["projection"]
    projection = {
        "formula": attribution["derivation"]["formula"],
        "affected_joints": attribution["derivation"]["affected_joints"],
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
        "placement": source_projection["placement"],
        "final_state_feedback": source_projection[
            "final_state_feedback"
        ],
        "command_x_observation_index": source_projection[
            "command_x_observation_index"
        ],
        "zero_deadband_absolute_command_x": source_projection[
            "zero_deadband_absolute_command_x"
        ],
        "home_target_rad": source_projection["home_target_rad"],
        "pitch_chain_action_indices": source_projection[
            "pitch_chain_action_indices"
        ],
        "measured_joint_offset_indices": source_projection[
            "measured_joint_offset_indices"
        ],
        "action_scale_rad": source_projection["action_scale_rad"],
        "g3_margin_rad": source_projection["g3_margin_rad"],
        "candidate_vectors": 1,
        "scalar_search": False,
        "training_steps": 0,
        "apply_identically_to_both_checkpoints": True,
    }
    checks = {
        "all_hashes_exact": hashes == EXPECTED_HASHES,
        "attribution_exact": (
            attribution.get("status")
            == "PASS_WINNER_V117_NOMINAL_FAILURE_ATTRIBUTION"
            and attribution.get("failed_checks") == []
            and attribution.get("decision")
            == "PREREGISTER_ONE_V118_POSTGUARD_RATE_PROJECTION"
            and attribution.get("authority", {}).get(
                "v118_projection_preregistration_authorized"
            )
            is True
            and attribution.get("authority", {}).get(
                "training_authorized"
            )
            is False
        ),
        "source_contract_exact": (
            source_contract.get("status")
            == "PASS_WINNER_V117_POSTGUARD_RATE_PROJECTION_CONTRACT"
            and source_contract.get("failed_checks") == []
        ),
        "nominal_split_exact": (
            result.get("decision", {}).get("status")
            == "REJECT_V117_NOMINAL_POLICY"
            and result["per_checkpoint"][0]["passing_cells"] == 3
            and result["per_checkpoint"][1]["passing_cells"] == 8
        ),
        "two_source_files_exact": (
            source_files_exact and len(sources) == 2
        ),
        "one_vector_only": projection["candidate_vectors"] == 1,
        "no_scalar_search": projection["scalar_search"] is False,
        "training_steps_zero": projection["training_steps"] == 0,
        "correct_postguard_placement_preserved": (
            projection["placement"]
            == "after_G3_before_restored_x0_deadband"
        ),
        "both_checkpoints_required": True,
        "formal_behavior_cells_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": (
            "winner_v118.rate_projection_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V118_RATE_PROJECTION"
            if not failed
            else "HOLD_WINNER_V118_RATE_PROJECTION_PREREGISTRATION"
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
            "colab_compute_units": 0,
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
        "# Winner-v118 rate-projection preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "One V117-response-derived vector is frozen for both policies at the "
        "existing post-G3 limiter. It changes no learned node or weight, "
        "runs no behavior cell, and uses no Colab compute. Both checkpoints "
        "remain mandatory in the next nominal gate.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
