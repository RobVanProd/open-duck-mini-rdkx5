#!/usr/bin/env python3
"""Run the saved-result-only Winner-v90 universal-target audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
PATCHES = ROOT / "patches"
ANALYSIS = ROOT / "outputs/analysis"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PATCHES))

import build_winner_v90_universal_target_intersection_preregistration as builder  # noqa: E402


PREREGISTRATION = ANALYSIS / "winner_v90_universal_target_intersection_preregistration.json"
V42_RESULT = ANALYSIS / "winner_v42_static_target_teacher_table_result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_preregistration(value: Mapping[str, Any]) -> None:
    frozen = value.get("frozen_source", {})
    if (
        value.get("schema_version")
        != "winner_v90.universal_target_intersection_preregistration.v1"
        or value.get("status")
        != "PREREGISTERED_WINNER_V90_UNIVERSAL_TARGET_INTERSECTION_AUDIT"
        or frozen.get("v42_result_sha256") != builder.V42_RESULT_SHA256
        or frozen.get("configurations") != 15
        or frozen.get("candidates_per_configuration") != 729
        or frozen.get("actuator_plants") != 2
        or frozen.get("candidate_plant_cells_already_captured") != 21870
        or value.get("execution_now")
        != {
            "saved_candidate_receipts_read": 0,
            "new_simulation_cells": 0,
            "optimizer_updates": 0,
            "snapshot_or_onnx_writes": 0,
            "robot_or_rdk_access": 0,
        }
    ):
        raise ValueError("Winner-v90 preregistration identity changed")
    sources = value.get("sources")
    if not isinstance(sources, Mapping) or not sources:
        raise ValueError("Winner-v90 source manifest absent")
    for name, item in sources.items():
        if (
            set(item) != {"hash_mode", "path", "sha256"}
            or item["hash_mode"] != "lf"
            or builder.lf_sha256(ROOT / item["path"]) != item["sha256"]
        ):
            raise ValueError(f"Winner-v90 source changed: {name}")
    if builder.canonical_sha256(sources) != value.get("source_manifest_sha256"):
        raise ValueError("Winner-v90 source manifest changed")


def aggregate_candidate(
    candidate_index: int,
    coordinates: np.ndarray,
    configuration_results: list[Mapping[str, Any]],
) -> dict[str, Any]:
    plant_rows = [
        plant
        for configuration in configuration_results
        for plant in configuration["candidate_receipts"][candidate_index]["plant_results"]
    ]
    support_pass_count = sum(row["support_pass"] for row in plant_rows)
    valid_ticks = [int(row["valid_ticks"]) for row in plant_rows]
    minimum_base_z = min(float(row["minimum_base_z_m"]) for row in plant_rows)
    maximum_tilt = max(float(row["maximum_abs_tilt_rad"]) for row in plant_rows)
    maximum_final_gyro = max(
        float(row["maximum_final_window_gyro_xy_norm_rad_s"]) for row in plant_rows
    )
    key = (
        support_pass_count,
        min(valid_ticks),
        sum(valid_ticks),
        minimum_base_z,
        -maximum_tilt,
        -maximum_final_gyro,
        -float(np.dot(coordinates.astype(np.float64), coordinates.astype(np.float64))),
        -candidate_index,
    )
    return {
        "candidate_index": candidate_index,
        "coordinates": coordinates.astype(float).tolist(),
        "support_pass_count": int(support_pass_count),
        "minimum_valid_ticks": min(valid_ticks),
        "sum_valid_ticks": sum(valid_ticks),
        "minimum_base_z_m": minimum_base_z,
        "maximum_abs_tilt_rad": maximum_tilt,
        "maximum_final_window_gyro_xy_norm_rad_s": maximum_final_gyro,
        "squared_coordinate_norm": float(
            np.dot(coordinates.astype(np.float64), coordinates.astype(np.float64))
        ),
        "selection_key": [float(value) for value in key],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--saved-result-audit-authorized", action="store_true")
    args = parser.parse_args()
    if not args.saved_result_audit_authorized:
        raise PermissionError("Winner-v90 requires --saved-result-audit-authorized")
    if args.output.exists():
        raise FileExistsError("refusing to overwrite Winner-v90 evidence")

    import run_winner_v12_calibrator_cpu_smoke as smoke
    import run_winner_v41_static_equilibrium_target_feasibility as v41

    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    validate_preregistration(preregistration)
    value = json.loads(V42_RESULT.read_text(encoding="utf-8"))
    if sha256(V42_RESULT) != builder.V42_RESULT_SHA256:
        raise ValueError("Winner-v90 V42 result changed")
    configurations = value["configuration_results"]
    grid = v41.candidate_coordinates()
    if len(configurations) != 15 or len(grid) != 729:
        raise ValueError("Winner-v90 source population changed")
    expected_indices = list(range(729))
    membership_sets: list[set[int]] = []
    saved_receipts_read = 0
    all_coordinate_hashes_match = True
    all_indices_exact = True
    all_shared_counts_reproduce = True
    for configuration in configurations:
        receipts = configuration["candidate_receipts"]
        saved_receipts_read += len(receipts)
        all_indices_exact = all_indices_exact and [
            int(row["candidate_index"]) for row in receipts
        ] == expected_indices
        for candidate_index, row in enumerate(receipts):
            all_coordinate_hashes_match = all_coordinate_hashes_match and (
                row["coordinates_sha256"] == smoke.array_sha256(grid[candidate_index])
            )
        shared = {
            int(row["candidate_index"]) for row in receipts if row["shared_support_pass"]
        }
        all_shared_counts_reproduce = all_shared_counts_reproduce and (
            len(shared) == int(configuration["shared_support_pass_count"])
        )
        membership_sets.append(shared)
    intersection = set.intersection(*membership_sets)
    universal_rows = [
        aggregate_candidate(index, grid[index], configurations)
        for index in sorted(intersection)
    ]
    selected = max(universal_rows, key=lambda row: tuple(row["selection_key"])) if universal_rows else None
    all_universal_cells_pass = all(
        row["support_pass_count"] == 30
        and row["minimum_valid_ticks"] == 250
        and row["sum_valid_ticks"] == 7500
        for row in universal_rows
    )
    checks = {
        "exact_15_configuration_tables": len(configurations) == 15,
        "exact_729_candidates_each": saved_receipts_read == 15 * 729,
        "candidate_indices_exact_and_ordered": all_indices_exact,
        "all_coordinate_hashes_match_reconstructed_grid": all_coordinate_hashes_match,
        "all_shared_counts_reproduce": all_shared_counts_reproduce,
        "all_intersection_candidates_pass_all_30_cells": all_universal_cells_pass,
        "no_new_simulation_or_policy_mutation": True,
    }
    failed_checks = sorted(name for name, passed in checks.items() if not passed)
    if failed_checks:
        raise ValueError(f"Winner-v90 audit invalid: {failed_checks}")
    nonempty = bool(universal_rows)
    result = {
        "schema_version": "winner_v90.universal_target_intersection_result.v1",
        "status": "PASS_WINNER_V90_UNIVERSAL_TARGET_INTERSECTION_AUDIT",
        "classification": (
            "UNIVERSAL_STATIC_TARGETS_EXIST_IN_CAPTURED_GRID"
            if nonempty
            else "NO_UNIVERSAL_STATIC_TARGET_IN_CAPTURED_GRID"
        ),
        "decision": (
            "PREREGISTER_FULL_124_CELL_UNIVERSAL_TARGET_FEASIBILITY_GATE"
            if nonempty
            else "DO_NOT_SELECT_UNIVERSAL_STATIC_TARGET"
        ),
        "intersection_count": len(universal_rows),
        "intersection_candidate_indices": [
            row["candidate_index"] for row in universal_rows
        ],
        "universal_candidates": universal_rows,
        "selected_universal_target": selected,
        "checks": {key: bool(item) for key, item in checks.items()},
        "failed_checks": [],
        "execution": {
            "saved_candidate_receipts_read": saved_receipts_read,
            "new_simulation_cells": 0,
            "optimizer_updates": 0,
            "snapshot_or_onnx_writes": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": preregistration["authority"],
        "sources": preregistration["sources"],
        "source_manifest_sha256": preregistration["source_manifest_sha256"],
    }
    args.output.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"intersection_count={len(universal_rows)}")
    print(f"selected_index={selected['candidate_index'] if selected else None}")
    print(f"selected_coordinates={selected['coordinates'] if selected else None}")
    print(f"sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
