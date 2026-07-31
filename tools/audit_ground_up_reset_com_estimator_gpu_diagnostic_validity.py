#!/usr/bin/env python3
"""Correct the recovered GPU diagnostic validity predicates on CPU."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import tarfile
import tempfile
from typing import Any

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "outputs/analysis/ground_up_reset_com_estimator_gpu_expansion_diagnostic_wall_run_20260715"
PLAN = ROOT / "launch_plan.json"
REPORT = ROOT / "recovery/GROUND_UP_RESET_COM_ESTIMATOR_GPU_EXPANSION_DIAGNOSTIC.json"
LAUNCH = ROOT / "recovery/GROUND_UP_RESET_COM_ESTIMATOR_GPU_EXPANSION_DIAGNOSTIC_launch.json"
ARCHIVE = REPO / "outputs/analysis/GROUND_UP_TRACKING_TAIL_artifacts.tar.gz"
HOSTED = REPO / "tools/colab_ground_up_reset_com_estimator_training.py"
WRAPPER = REPO / "tools/colab_ground_up_reset_com_estimator_gpu_expansion_diagnostic.py"
CONTRACT = REPO / "outputs/analysis/ground_up_reset_com_estimator_gpu_diagnostic_wall_only_contract.json"
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_GPU_DIAGNOSTIC_VALIDITY_CORRECTION_PREREGISTRATION_20260715.md"
EXPECTED = {
    "plan": "380fda02e6d6694ab872ea8f073891bdb672d02af70d566cc3789e1936464bd4",
    "report": "e68e7759ac1754f34966ff5eb420a7f0162de824411b4d2f48f4cfd7a7d9fb97",
    "launch": "4f8870b8841f1f11cbfee16b646110e1bba8a3d57920a6628a00bfc958a2c8ab",
    "archive": "ae4c631a6ce1c0b36c3231113740acc6c1b8a463c0911ce7cad30b8f8d8ca60f",
    "hosted": "a3e5fc38994cecd65d89fdc6b9ede23c2433e917b84583dfcced42c161e79d67",
    "wrapper": "68a6f8c3001bfdce74346a02533ca76e9e122d0a5ea325c827625e6293fe14e4",
    "contract": "54c142cbd3fe8c10daa9bad969ec0e01ffca40d5a8352513f2cb6b1388adb8cb",
    "prereg": "6941a5c8da032147eed0b23e6ea35593573f2d4159fd36794c83b79dd782b567",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_hosted() -> Any:
    spec = importlib.util.spec_from_file_location("validity_hosted", HOSTED)
    if spec is None or spec.loader is None:
        raise RuntimeError(HOSTED)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {"plan": PLAN, "report": REPORT, "launch": LAUNCH, "archive": ARCHIVE,
             "hosted": HOSTED, "wrapper": WRAPPER, "contract": CONTRACT, "prereg": PREREG}
    hashes = {name: sha256(path) for name, path in paths.items()}
    plan, report, launch = (json.loads(path.read_text()) for path in (PLAN, REPORT, LAUNCH))
    hosted = load_hosted()
    relative = hosted.SOURCE_CHECKPOINT_RELATIVE
    with tempfile.TemporaryDirectory(prefix="gpu_diag_validity_") as temporary:
        root = Path(temporary)
        with tarfile.open(ARCHIVE, "r:gz") as archive:
            members = [member for member in archive
                       if member.name == str(relative)
                       or member.name.startswith(str(relative) + "/")]
            archive.extractall(root, members=members, filter="data")
        extracted_hash = hosted.sha256_directory(root / relative)

    status_commands = [entry for entry in launch["commands"]
                       if entry["command"][1] == "status"]
    status_text = status_commands[0]["stdout"] if len(status_commands) == 1 else ""
    t4_status = re.fullmatch(
        r"\[open-duck-reset-estimator-expansion-diag2-t4\] [^|]+ \| Hardware: T4 \| Variant: GPU \| Status: IDLE\n",
        status_text,
    ) is not None
    cells = report.get("output_equivalence", [])
    errors = [cell.get(key) for cell in cells
              for key in ("actor_max_abs_error", "critic_max_abs_error")]
    other_checks = {key: value for key, value in report.get("checks", {}).items()
                    if key != "step_zero_outputs_exact"}
    marker = launch.get("marker", {})
    checks = {
        "frozen_hashes_exact": hashes == EXPECTED,
        "archive_source_hash_matches_report": extracted_hash
        == report.get("source_directory_sha256"),
        "exact_named_t4_gpu_status": t4_status,
        "report_device_exact_cuda0": report.get("devices") == ["cuda:0"],
        "marker_report_hash_exact": marker.get("report", {}).get("sha256") == hashes["report"]
        and marker.get("report", {}).get("bytes") == REPORT.stat().st_size,
        "report_recovered_pass": launch.get("status") == "PASS_GPU_EXPANSION_DIAGNOSTIC_RECOVERED",
        "cleanup_and_wall_pass": launch.get("session_stop_passed") is True
        and launch.get("session_elapsed_seconds", 301) <= 300.0,
        "training_not_started": marker.get("training_started") is False
        and "training_command" not in json.dumps(launch.get("commands", [])),
        "cells_exact": len(cells) == 3
        and [cell.get("z") for cell in cells] == [-1.0, 0.0, 1.0],
        "six_errors_finite": len(errors) == 6
        and all(isinstance(value, (int, float)) and math.isfinite(value) for value in errors),
        "all_other_expansion_checks_pass": bool(other_checks) and all(other_checks.values()),
        "raw_classification_preserved": launch.get("classification", {}).get("outcome")
        == "INVALID_OR_STRUCTURAL_GPU_EXPANSION",
        "compute_usage_unmeasured": plan.get("compute_units") == "UNMEASURED",
    }
    valid = all(checks.values())
    maximum = max(errors) if checks["six_errors_finite"] else None
    if not valid:
        outcome = "INVALID_OR_STRUCTURAL_GPU_EXPANSION"
    elif maximum <= 1e-7:
        outcome = "GPU_EQUIVALENCE_PASSES_ORIGINAL_1E7_NOT_REPRODUCED"
    else:
        outcome = "FINITE_GPU_EQUIVALENCE_EXCEEDS_ORIGINAL_1E7"
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "ground_up_reset_estimator_gpu_diagnostic_validity_correction.v1",
        "status": "PASS_GPU_DIAGNOSTIC_VALIDITY_CORRECTION" if valid else "FAIL_GPU_DIAGNOSTIC_VALIDITY_CORRECTION",
        "checks": checks, "failed_checks": failed,
        "raw_classification": launch.get("classification"),
        "corrected_classification": {"valid": valid, "outcome": outcome,
                                     "maximum_output_error": maximum,
                                     "threshold": 1e-7},
        "source_hashes": hashes,
        "archive_source_directory_sha256": extracted_hash,
        "report_source_directory_sha256": report.get("source_directory_sha256"),
        "devices": {"session_status": status_text, "report": report.get("devices")},
        "output_equivalence": cells,
        "other_checks": other_checks,
        "execution": {"cpu_only": True, "colab_sessions_created": 0,
                      "training_steps": 0, "compute_units": "UNMEASURED",
                      "robot_or_rdk": False},
        "authority": {"selected_next_study": "ACTION_DISTRIBUTION_ULP_SENSITIVITY_AUDIT"
                      if outcome == "FINITE_GPU_EQUIVALENCE_EXCEEDS_ORIGINAL_1E7" else None,
                      "tolerance_relaxation": False, "training": False,
                      "behavior_evaluation": False},
    }
    args.output.resolve().write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "outcome": outcome,
                      "failed_checks": failed}, sort_keys=True))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
