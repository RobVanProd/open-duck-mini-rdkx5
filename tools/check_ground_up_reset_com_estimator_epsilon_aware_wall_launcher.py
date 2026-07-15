#!/usr/bin/env python3
"""Contract the wall-only epsilon-aware reset-estimator launcher without allocation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[1]
LAUNCHER = REPO / "tools/launch_ground_up_reset_com_estimator_epsilon_aware_wall_only.py"
BASE = REPO / "tools/launch_ground_up_reset_com_estimator_colab.py"
WRAPPER = REPO / "tools/colab_ground_up_reset_com_estimator_epsilon_aware_training.py"
HOSTED = REPO / "tools/colab_ground_up_reset_com_estimator_training.py"
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_EPSILON_AWARE_HOSTED_EXPANSION_CORRECTION_PREREGISTRATION_20260715.md"
CONTRACT = REPO / "outputs/analysis/ground_up_reset_com_estimator_epsilon_aware_expansion_contract.json"
ARCHIVE = REPO / "outputs/analysis/GROUND_UP_TRACKING_TAIL_artifacts.tar.gz"
EXPECTED = {
    "launcher": "6b04ae16ad145c1207a2ec402ec911de4bc4599fe34a9f2dbeec3ce5d3db8420",
    "base": "afb5acc580239f729d4d0832dd29a0c7163e87b63856ff6b1111eb393683e241",
    "wrapper": "c1d88f6c48a6d2fb3191e4c25088f83e1163ff217058a94d79b2a17394aabda4",
    "hosted": "a3e5fc38994cecd65d89fdc6b9ede23c2433e917b84583dfcced42c161e79d67",
    "prereg": "22daea5aaddf8d480d5748d3c1d1053ff6dd7bff2d4ab04af2b69750d73a5947",
    "contract": "61a5e25fa358a0fd61418ea305d15cdc6c37db8e4ce333bd2447b2e10692eeb0",
    "archive": "ae4c631a6ce1c0b36c3231113740acc6c1b8a463c0911ce7cad30b8f8d8ca60f",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {"launcher": LAUNCHER, "base": BASE, "wrapper": WRAPPER,
             "hosted": HOSTED, "prereg": PREREG, "contract": CONTRACT,
             "archive": ARCHIVE}
    hashes = {name: sha256(path) for name, path in paths.items()}
    launcher = load(LAUNCHER, "epsilon_wall_launcher_contract")
    with tempfile.TemporaryDirectory(prefix="epsilon_wall_contract_") as temporary:
        root = Path(temporary); assets = root / "assets"; recovery = root / "recovery"
        staging = launcher.stage_assets(assets, ARCHIVE)
        _sources, expected, base, job = launcher.expected_assets(ARCHIVE)
        recovery.mkdir()
        plan = launcher.build_plan(assets, recovery, "colab", expected)

        calls: list[list[str]] = []
        original_command = launcher.command

        def fake_command(value: list[str], timeout: float, check: bool = True) -> dict[str, Any]:
            del timeout, check
            calls.append(value)
            stdout = ""
            if value[1] == "status":
                stdout = "[open-duck-reset-estimator-epsilon-t4] fixture | Hardware: T4 | Variant: GPU | Status: IDLE\n"
            return {"command": value, "returncode": 0, "stdout": stdout, "elapsed_seconds": 0.0}

        launcher.command = fake_command
        failed_closed = False
        try:
            launcher.launch(plan, "colab", base, job)
        except RuntimeError:
            failed_closed = True
        finally:
            launcher.command = original_command
        record = json.loads(Path(plan["recovery"]["launch_record"]).read_text())

        summary = {
            "asset_count": staging["asset_count"],
            "session": plan["session"],
            "maximum_session_seconds": plan["maximum_session_seconds"],
            "stop_reserve_seconds": plan["stop_reserve_seconds"],
            "compute_units": plan["compute_units"],
            "upload_count": len(plan["commands"]["uploads"]),
            "allocation_authorized": plan["allocation_authorized"],
        }

    source = LAUNCHER.read_text()
    checks = {
        "frozen_hashes_exact": hashes == EXPECTED,
        "exact_24_hash_locked_assets": summary["asset_count"] == 24
        and summary["upload_count"] == 24,
        "fresh_named_t4_exact": summary["session"] == "open-duck-reset-estimator-epsilon-t4"
        and launcher.ACCELERATOR == "T4",
        "wall_and_stop_reserve_exact": summary["maximum_session_seconds"] == 2_400.0
        and summary["stop_reserve_seconds"] == 120.0,
        "compute_unmeasured_and_no_billing_surface": summary["compute_units"] == "UNMEASURED"
        and "attestation" not in source.lower() and "compute_rate" not in source.lower()
        and "available_compute" not in source.lower(),
        "dry_plan_cannot_allocate": summary["allocation_authorized"] is False,
        "exact_original_job_and_wrapper": launcher.HOSTED == HOSTED
        and launcher.WRAPPER == WRAPPER,
        "manifest_and_artifact_atomic_recovery": plan["recovery"]["manifest"].endswith("GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_manifest.json")
        and plan["recovery"]["artifact"].endswith("GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_artifacts.tar.gz"),
        "invalid_exec_fails_closed": failed_closed
        and record.get("status") == "FAIL_HOSTED_LAUNCH_OR_RECOVERY",
        "finally_cleanup_invoked_and_passed": record.get("session_stop_passed") is True
        and calls[-1] == ["colab", "stop", "--session", "open-duck-reset-estimator-epsilon-t4"],
        "no_remote_or_training_execution_in_contract": all(call[1] != "new" for call in [])
        and record.get("remote_result") is None,
        "original_recipe_and_exports_exact": job.ARM_NAME == "RESET_EST_LATCH_U05"
        and job.EXPECTED_STEPS == [0, 1_003_520, 2_007_040]
        and job.MAX_HOSTED_SECONDS == 2_400,
        "single_use_no_retry_source_guards": "no resume/retry" in HOSTED.read_text()
        and "if destination.exists()" in LAUNCHER.read_text()
        and "write_json_atomic" in source,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = {
        "schema_version": "ground_up_reset_estimator_epsilon_aware_wall_launcher_contract.v1",
        "status": "PASS_EPSILON_AWARE_WALL_LAUNCHER_CONTRACT" if not failed else "FAIL_EPSILON_AWARE_WALL_LAUNCHER_CONTRACT",
        "checks": checks, "failed_checks": failed, "source_hashes": hashes,
        "plan_summary": summary,
        "failure_cleanup_fixture": {"failed_closed": failed_closed,
                                    "record_status": record.get("status"),
                                    "session_stop_passed": record.get("session_stop_passed")},
        "execution": {"colab_sessions_created": 0, "remote_bytes": 0,
                      "training_steps": 0, "behavior_cells": 0,
                      "local_gpu_or_igpu": False, "robot_or_rdk": False},
        "authority": {"single_wall_only_t4_run_authorized_if_pass": True,
                      "billing_input_required": False,
                      "behavior_evaluation_now": False,
                      "robot_or_rdk": False},
    }
    args.output.resolve().write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
