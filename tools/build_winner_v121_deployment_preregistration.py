#!/usr/bin/env python3
"""Preregister the exact trained-delta V121 deployment transform."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
ATTRIBUTION = ANALYSIS / "winner_v120_deployment_hold_attribution.json"
VALIDATION = ANALYSIS / "winner_v119_recovered_training_validation.json"
GUARD_PREREG = (
    ANALYSIS / "ground_up_actual_centered_guard_screen_preregistration.json"
)
DEADBAND_PREREG = (
    ANALYSIS / "ground_up_command_deadband_repair_preregistration.json"
)
TRANSFORM = ROOT / "tools/build_winner_v121_deployment_policies.py"
OUTPUT = ANALYSIS / "winner_v121_deployment_transform_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V121_DEPLOYMENT_TRANSFORM_PREREGISTRATION_20260724.md"
)
EXPECTED = {
    "v120_hold_attribution": (
        "8044fb93502a73701ad636a261d03de541e7a3f30ed68de3c9ac8e923a4fe561"
    ),
    "v119_training_validation": (
        "456121dc7680df6e66915fa67e59f088f718e08db1468d3523795f8dd56abb14"
    ),
    "guard_preregistration": (
        "9bf9b3ec4e4423a5e44a582d29a69927382468e24d7aa3a478712b6c87988dae"
    ),
    "deadband_preregistration": (
        "8df6129f260c0d0e0a48a81d5e318bd7d2ede7fdb9e3ffa3374d6c967c8856f4"
    ),
    "transform_tool": (
        "778841be69753b53d366bf35cf1f45b2d748c4581ac701f18ca7a092f1ed3bf8"
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
            raise FileExistsError(f"refusing to overwrite V121: {path}")
    source_root = args.source_root.resolve()
    attribution = json.loads(ATTRIBUTION.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    guard = json.loads(GUARD_PREREG.read_text(encoding="utf-8"))
    deadband = json.loads(DEADBAND_PREREG.read_text(encoding="utf-8"))
    hashes = {
        "v120_hold_attribution": sha256(ATTRIBUTION),
        "v119_training_validation": sha256(VALIDATION),
        "guard_preregistration": sha256(GUARD_PREREG),
        "deadband_preregistration": sha256(DEADBAND_PREREG),
        "transform_tool": sha256(TRANSFORM),
    }
    raw_rows = {
        int(row["step"]): row for row in validation["onnx"]
    }
    sources = []
    for step in (1_003_520, 2_007_040):
        matches = list(source_root.glob(f"*_{step}.onnx"))
        if len(matches) != 1:
            raise ValueError(f"expected one V119 step {step} graph: {matches}")
        path = matches[0]
        sources.append(
            {
                "id": (
                    "V121_TRAIN_MATCHED_HALF"
                    if step == 1_003_520
                    else "V121_TRAIN_MATCHED_FINAL"
                ),
                "step": step,
                "filename": path.name,
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "output_filename": f"V121_DEPLOYMENT_{step}.onnx",
            }
        )
    guard_contract = guard["guard_contract"]
    selected_guard = next(
        row for row in guard["arms"] if row["name"] == "G3_FULL_TICK_BUFFER"
    )
    train_delta = np.asarray(
        attribution["shared_train_normalized_action_delta"],
        dtype=np.float32,
    )
    action_scale = np.float32(guard_contract["action_scale_rad"])
    control_dt = np.float32(guard_contract["control_dt_s"])
    target_delta = train_delta * action_scale
    effective_rate = target_delta / control_dt
    transform = {
        "order": [
            "raw trained actor action",
            "G3 actual-position-centered guard",
            "x=0 deadband",
            "exact trained previous-action-centered rate projection",
            "restored x=0 deadband and final-action state feedback",
        ],
        "observation_dim": 115,
        "action_dim": 14,
        "home_target_rad": guard_contract["home_target_rad"],
        "measured_joint_offset_indices": guard_contract[
            "measured_joint_offset_indices"
        ],
        "pitch_chain_action_indices": guard_contract[
            "pitch_chain_action_indices"
        ],
        "action_scale_rad": float(action_scale),
        "control_dt_s": float(control_dt),
        "g3_margin_rad": selected_guard["margin_rad"],
        "command_x_observation_index": deadband["transform"][
            "command_x_observation_index"
        ],
        "zero_deadband_absolute_command_x": deadband["transform"][
            "zero_deadband_absolute_command_x"
        ],
        "exact_train_normalized_action_delta": train_delta.tolist(),
        "exact_train_target_delta_rad": target_delta.tolist(),
        "exact_train_effective_rate_rad_s": effective_rate.tolist(),
        "final_state_feedback": "final_bounded_action",
        "candidate_transforms": 1,
        "training_steps": 0,
        "apply_identically_to_both_checkpoints": True,
    }
    checks = {
        "all_input_hashes_exact": hashes == EXPECTED,
        "v120_attribution_exact": (
            attribution.get("status")
            == "PASS_WINNER_V120_DEPLOYMENT_HOLD_ATTRIBUTION"
            and attribution.get("failed_checks") == []
            and attribution.get("authority", {}).get(
                "v121_transform_preregistration_authorized"
            )
            is True
        ),
        "v119_training_validation_exact": (
            validation.get("status")
            == "PASS_WINNER_V119_RECOVERED_TRAINING_VALIDATION"
            and validation.get("failed_checks") == []
        ),
        "two_postupdate_sources_exact": (
            len(sources) == 2
            and all(
                row["sha256"] == raw_rows[row["step"]]["sha256"]
                for row in sources
            )
        ),
        "shared_train_delta_has_fourteen_finite_values": (
            train_delta.shape == (14,) and bool(np.isfinite(train_delta).all())
        ),
        "one_transform_no_search": (
            transform["candidate_transforms"] == 1
            and transform["training_steps"] == 0
        ),
        "both_checkpoints_required": True,
        "formal_behavior_cells_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    value = {
        "schema_version": (
            "winner_v121.deployment_transform_preregistration.v1"
        ),
        "status": (
            "PREREGISTERED_WINNER_V121_DEPLOYMENT_TRANSFORM"
            if not failed
            else "HOLD_WINNER_V121_DEPLOYMENT_TRANSFORM_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": hashes,
        "sources": sources,
        "transform": transform,
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
        "# Winner-v121 deployment transform preregistration\n\n"
        f"Status: `{value['status']}`\n\n"
        "One transform applies the exact shared trained float32 delta to "
        "both post-update checkpoints. No search, training, behavior, Gate "
        "5, RDK-X5, robot, torque, or motion work occurs here.\n",
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
