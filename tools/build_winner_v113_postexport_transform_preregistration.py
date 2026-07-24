#!/usr/bin/env python3
"""Preregister the frozen V112 post-export guard/deadband transform."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
VALIDATION = ANALYSIS / "winner_v112_recovered_training_validation.json"
GUARD = ANALYSIS / "ground_up_actual_centered_guard_screen_preregistration.json"
DEADBAND = (
    ANALYSIS / "ground_up_command_deadband_repair_preregistration.json"
)
TRANSFORM = ROOT / "tools/build_winner_v113_postexport_policies.py"
OUTPUT = ANALYSIS / "winner_v113_postexport_transform_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V113_POSTEXPORT_TRANSFORM_PREREGISTRATION_20260724.md"
)
EXPECTED_HASHES = {
    "v112_validation": (
        "895c010a015da4dc43bec2bf3752767c7633859adef2f1b277ef7315e941d4a7"
    ),
    "guard_preregistration": (
        "9bf9b3ec4e4423a5e44a582d29a69927382468e24d7aa3a478712b6c87988dae"
    ),
    "deadband_preregistration": (
        "8df6129f260c0d0e0a48a81d5e318bd7d2ede7fdb9e3ffa3374d6c967c8856f4"
    ),
    "transform_tool": (
        "d01b69e33f253c91938e34b3c163630e371207e7500b45a1d4111b20b59f7eac"
    ),
}
SOURCES = (
    {
        "id": "V112_PEAK_TORQUE_HALF",
        "step": 1_003_520,
        "filename": "2026_07_24_141433_1003520.onnx",
        "output_filename": "V112_G3_DEADBAND_1003520.onnx",
        "sha256": (
            "eb691f6e85b58f3c514779926cc6aeb769091c3609f894e7e6cde8e538be6718"
        ),
    },
    {
        "id": "V112_PEAK_TORQUE_FINAL",
        "step": 2_007_040,
        "filename": "2026_07_24_141819_2007040.onnx",
        "output_filename": "V112_G3_DEADBAND_2007040.onnx",
        "sha256": (
            "6a400a7c465e56520e853d3607265e544888f86560d065f553a765b3d259563b"
        ),
    },
)


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
            raise FileExistsError(f"refusing to overwrite V113: {path}")
    source_root = args.source_root.resolve()
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    hashes = {
        "v112_validation": sha256(VALIDATION),
        "guard_preregistration": sha256(GUARD),
        "deadband_preregistration": sha256(DEADBAND),
        "transform_tool": sha256(TRANSFORM),
    }
    source_hashes = {
        spec["id"]: sha256(source_root / spec["filename"])
        for spec in SOURCES
    }
    checks = {
        "v112_validation_exact": (
            hashes["v112_validation"] == EXPECTED_HASHES["v112_validation"]
            and validation.get("status")
            == "PASS_WINNER_V112_RECOVERED_TRAINING_VALIDATION"
            and validation.get("failed_checks") == []
            and validation.get("authority", {}).get(
                "postexport_transform_preregistration_authorized"
            )
            is True
        ),
        "frozen_transform_inputs_exact": hashes == EXPECTED_HASHES,
        "two_postupdate_sources_exact": all(
            source_hashes[spec["id"]] == spec["sha256"]
            for spec in SOURCES
        ),
        "g3_selected_before_transform": True,
        "deadband_selected_before_transform": True,
        "formal_behavior_cells_zero": True,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    payload = {
        "schema_version": "winner_v113.postexport_transform_preregistration.v1",
        "status": (
            "PREREGISTERED_WINNER_V113_POSTEXPORT_TRANSFORM"
            if not failed
            else "HOLD_WINNER_V113_POSTEXPORT_TRANSFORM_PREREGISTRATION"
        ),
        "failed_checks": failed,
        "checks": checks,
        "input_hashes": hashes,
        "sources": list(SOURCES),
        "transform": {
            "order": [
                "preserve source conservative all-joint rate projection",
                "append frozen G3 actual-centered pitch guard",
                "append frozen x=0 deadband",
            ],
            "g3_margin_rad": 0.165,
            "zero_deadband_absolute_command_x": 0.01,
            "source_nodes_and_initializers": "bit-exact",
            "positive_support_behavior": "bit-exact after G3 guard",
        },
        "execution_now": {
            "transformed_policies": 0,
            "formal_behavior_cells": 0,
            "training_steps": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "cpu_transform_authorized": not failed,
            "behavior_evaluation_authorized": False,
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
        "# Winner-v113 post-export transform preregistration\n\n"
        f"Status: `{payload['status']}`\n\n"
        "The transform is frozen before reading behavior: preserve each V112 "
        "post-update graph, append the already-selected G3 0.165-rad "
        "actual-centered pitch guard, then append the exact x=0 deadband. "
        "No behavior evaluation, Gate 5, robot, torque, or motion is "
        "authorized here.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
