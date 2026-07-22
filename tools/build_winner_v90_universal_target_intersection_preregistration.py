#!/usr/bin/env python3
"""Preregister the saved-result-only Winner-v90 universal-target audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs/analysis"
OUTPUT = ANALYSIS / "winner_v90_universal_target_intersection_preregistration.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V90_UNIVERSAL_TARGET_INTERSECTION_PREREGISTRATION_20260722.md"
)
V89_RESULT = ANALYSIS / "winner_v89_teacher_gradient_transfer_result.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"
V89_RESULT_SHA256 = "0197add105f174eb856613fa62d773fa633841266724f4d76a791fd2fd250a20"
V42_RESULT_SHA256 = "ff1f12d556661548df272ef4b5a6c5f69bd614d2e54d3d7e17654be6de9ebc1c"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
            raise FileExistsError(f"refusing to overwrite Winner-v90 contract: {path}")
    gradient = json.loads(V89_RESULT.read_text(encoding="utf-8"))
    table = json.loads(V42_RESULT.read_text(encoding="utf-8"))
    if (
        sha256(V89_RESULT) != V89_RESULT_SHA256
        or gradient.get("classification") != "STATIC_TEACHER_GRADIENT_NONTRANSFERABLE"
        or gradient.get("selected_gradient_group_for_step_proof") is not None
        or sha256(V42_RESULT) != V42_RESULT_SHA256
        or table.get("status") != "PASS_WINNER_V42_STATIC_TARGET_TEACHER_TABLE"
        or table.get("classification") != "FULL_FAILURE_SET_STATIC_TARGET_TEACHER_TABLE_EXISTS"
        or len(table.get("configuration_results", [])) != 15
        or table.get("execution", {}).get("candidate_plant_cells") != 21870
    ):
        raise ValueError("Winner-v90 source evidence changed")
    source_paths = {
        "builder": Path(
            "tools/build_winner_v90_universal_target_intersection_preregistration.py"
        ),
        "runner": Path("tools/run_winner_v90_universal_target_intersection.py"),
        "tests": Path("tests/test_winner_v90_universal_target_intersection.py"),
        "v89_result": V89_RESULT.relative_to(ROOT),
        "v42_result": V42_RESULT.relative_to(ROOT),
        "v41_grid": Path("tools/run_winner_v41_static_equilibrium_target_feasibility.py"),
    }
    sources = {
        name: {"path": path.as_posix(), "hash_mode": "lf", "sha256": lf_sha256(ROOT / path)}
        for name, path in source_paths.items()
    }
    value = {
        "schema_version": "winner_v90.universal_target_intersection_preregistration.v1",
        "status": "PREREGISTERED_WINNER_V90_UNIVERSAL_TARGET_INTERSECTION_AUDIT",
        "decision": "AUTHORIZE_ONE_SAVED_V42_RESULT_INTERSECTION_AUDIT_ONLY",
        "question": (
            "Did the per-configuration V42 selector create contradictory labels "
            "despite one or more exact grid targets being support-valid for all 15 "
            "configurations and both actuator plants?"
        ),
        "frozen_source": {
            "v89_result_sha256": V89_RESULT_SHA256,
            "v42_result_sha256": V42_RESULT_SHA256,
            "configurations": 15,
            "candidates_per_configuration": 729,
            "actuator_plants": 2,
            "candidate_plant_cells_already_captured": 21870,
            "grid_values": [-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0],
            "grid_dimensions": 3,
        },
        "intersection": {
            "membership": (
                "candidate_index has shared_support_pass true in every one of the "
                "15 captured configuration tables"
            ),
            "required_readback": (
                "all tables contain candidate indices 0..728 in order and each "
                "coordinate hash matches the reconstructed V41 float32 grid"
            ),
            "empty_decision": "NO_UNIVERSAL_STATIC_TARGET_IN_CAPTURED_GRID",
            "nonempty_decision": (
                "select exactly one universal target by the frozen aggregate V41 key"
            ),
        },
        "selection_key_largest_first": [
            "support_pass_count across 30 captured cells",
            "minimum valid ticks",
            "sum valid ticks",
            "minimum base z",
            "negative maximum absolute tilt",
            "negative maximum final-window gyro norm",
            "negative squared coordinate norm",
            "negative candidate index",
        ],
        "execution_now": {
            "saved_candidate_receipts_read": 0,
            "new_simulation_cells": 0,
            "optimizer_updates": 0,
            "snapshot_or_onnx_writes": 0,
            "robot_or_rdk_access": 0,
        },
        "sources": sources,
        "source_manifest_sha256": canonical_sha256(sources),
        "authority": {
            "saved_result_audit_authorized": True,
            "result_authorizes": (
                "one separate full-124-cell universal-target CPU feasibility gate "
                "preregistration only if the intersection is nonempty"
            ),
            "training_authorized_now": False,
            "support_gate_authorized_now": False,
            "checkpoint_selection_authorized": False,
            "deployment_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_robot_serial_gpio_i2c_torque_motion": False,
        },
    }
    args.output.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.markdown.write_text(
        "\n".join(
            [
                "# Winner-v90 universal-target intersection preregistration",
                "",
                "- Input: exact captured V42 `15 x 729 x 2` result",
                "- New simulation / optimizer updates / policy artifacts / robot access: `0 / 0 / 0 / 0`",
                "- Intersection: candidate must pass every configuration under both plants",
                "- Selection: unchanged V41 key aggregated over all 30 captured cells",
                "- Result authority: separate 124-cell CPU feasibility preregistration only",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(value["status"])
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
