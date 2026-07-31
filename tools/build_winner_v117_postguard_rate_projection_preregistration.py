#!/usr/bin/env python3
"""Preregister the V117 post-G3 conservative rate projection."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
CORRECTION = (
    ANALYSIS
    / "winner_v115_nominal_failure_attribution_v2_correction.json"
)
SOURCE_CONTRACT = (
    ANALYSIS / "winner_v115_postexport_transform_contract.json"
)
V116_HOLD = ANALYSIS / "winner_v116_rate_projection_contract.json"
GUARD_PREREG = (
    ANALYSIS / "ground_up_actual_centered_guard_screen_preregistration.json"
)
DEADBAND_PREREG = (
    ANALYSIS / "ground_up_command_deadband_repair_preregistration.json"
)
TRANSFORM = (
    ROOT / "tools/build_winner_v117_postguard_rate_projection_policies.py"
)
OUTPUT = (
    ANALYSIS
    / "winner_v117_postguard_rate_projection_preregistration.json"
)
MARKDOWN = (
    ANALYSIS
    / "WINNER_V117_POSTGUARD_RATE_PROJECTION_PREREGISTRATION_20260724.md"
)
EXPECTED_HASHES = {
    "v115_attribution_correction": (
        "fe970d631f0c089a4cddc5abcb63b527b69450f993aa4985013762982a5fae80"
    ),
    "v115_source_contract": (
        "bcbc71eda01eae4a50435a1c9356a048ae4fceec78c4f8f5382d223b7df88ac3"
    ),
    "v116_hold_contract": (
        "c5f14055af0efcc5bc7170c0b5cb5e383a43b30a353d85b88f369df535213169"
    ),
    "guard_preregistration": (
        "9bf9b3ec4e4423a5e44a582d29a69927382468e24d7aa3a478712b6c87988dae"
    ),
    "deadband_preregistration": (
        "8df6129f260c0d0e0a48a81d5e318bd7d2ede7fdb9e3ffa3374d6c967c8856f4"
    ),
    "transform_tool": (
        "177f124685531205ecb9c7c79c8aaf367b627c8cbc70cf3b6b246db6999c0fe7"
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
            raise FileExistsError(f"refusing to overwrite V117: {path}")

    source_root = args.source_root.resolve()
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    source_contract = json.loads(
        SOURCE_CONTRACT.read_text(encoding="utf-8")
    )
    v116_hold = json.loads(V116_HOLD.read_text(encoding="utf-8"))
    guard_prereg = json.loads(GUARD_PREREG.read_text(encoding="utf-8"))
    deadband_prereg = json.loads(
        DEADBAND_PREREG.read_text(encoding="utf-8")
    )
    hashes = {
        "v115_attribution_correction": sha256(CORRECTION),
        "v115_source_contract": sha256(SOURCE_CONTRACT),
        "v116_hold_contract": sha256(V116_HOLD),
        "guard_preregistration": sha256(GUARD_PREREG),
        "deadband_preregistration": sha256(DEADBAND_PREREG),
        "transform_tool": sha256(TRANSFORM),
    }
    sources = [
        {
            "id": (
                "V117_POSTGUARD_RATE_PROJECTED_HALF"
                if row["step"] == 1_003_520
                else "V117_POSTGUARD_RATE_PROJECTED_FINAL"
            ),
            "step": row["step"],
            "filename": Path(row["output_path"]).name,
            "output_filename": (
                "V117_POSTGUARD_RATE_PROJECTED_1003520.onnx"
                if row["step"] == 1_003_520
                else "V117_POSTGUARD_RATE_PROJECTED_2007040.onnx"
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
    guard = guard_prereg["guard_contract"]
    selected_guard = next(
        row
        for row in guard_prereg["arms"]
        if row["name"] == "G3_FULL_TICK_BUFFER"
    )
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
        "placement": "after_G3_before_restored_x0_deadband",
        "final_state_feedback": "final_bounded_action",
        "command_x_observation_index": deadband_prereg["transform"][
            "command_x_observation_index"
        ],
        "zero_deadband_absolute_command_x": deadband_prereg["transform"][
            "zero_deadband_absolute_command_x"
        ],
        "home_target_rad": guard["home_target_rad"],
        "pitch_chain_action_indices": guard[
            "pitch_chain_action_indices"
        ],
        "measured_joint_offset_indices": guard[
            "measured_joint_offset_indices"
        ],
        "action_scale_rad": guard["action_scale_rad"],
        "g3_margin_rad": selected_guard["margin_rad"],
        "candidate_vectors": 1,
        "scalar_search": False,
        "training_steps": 0,
        "apply_identically_to_both_checkpoints": True,
    }
    checks = {
        "all_hashes_exact": hashes == EXPECTED_HASHES,
        "attribution_correction_exact": (
            correction.get("status")
            == "PASS_WINNER_V115_NOMINAL_FAILURE_ATTRIBUTION_V2_REPORTING_CORRECTED"
            and correction.get("failed_checks") == []
            and correction.get("authority", {}).get(
                "rate_projection_preregistration_authorized"
            )
            is True
        ),
        "source_contract_exact": (
            source_contract.get("status")
            == "PASS_WINNER_V115_POSTEXPORT_TRANSFORM_CONTRACT"
            and source_contract.get("failed_checks") == []
        ),
        "v116_failure_is_placement_specific": (
            v116_hold.get("status")
            == "HOLD_WINNER_V116_RATE_PROJECTION_CONTRACT"
            and v116_hold.get("failed_checks")
            == ["all_inference_contracts_pass"]
            and v116_hold.get("checks", {}).get(
                "only_max_action_delta_changed"
            )
            is True
            and v116_hold.get("checks", {}).get(
                "all_inference_contracts_pass"
            )
            is False
        ),
        "two_source_files_exact": (
            source_files_exact and len(sources) == 2
        ),
        "one_unchanged_vector_only": (
            projection["candidate_vectors"] == 1
            and projection["scalar_search"] is False
        ),
        "postguard_placement_frozen": (
            projection["placement"]
            == "after_G3_before_restored_x0_deadband"
        ),
        "both_checkpoints_required": True,
        "formal_behavior_cells_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": (
            "winner_v117.postguard_rate_projection_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V117_POSTGUARD_RATE_PROJECTION"
            if not failed
            else "HOLD_WINNER_V117_POSTGUARD_RATE_PROJECTION_PREREGISTRATION"
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
        "decision_rule": {
            "contract_pass": (
                "authorize a separately hash-frozen 16-cell nominal gate"
            ),
            "contract_fail": (
                "hold without behavior evaluation or policy selection"
            ),
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
        "# Winner-v117 post-guard rate-projection preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "V116 proved that changing the inherited pre-G3 initializer cannot "
        "bound the final guarded action. V117 moves the same single frozen "
        "vector after G3, restores x=0 afterward, and feeds back the final "
        "bounded action. No training, behavior, RDK, or robot work occurs.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
