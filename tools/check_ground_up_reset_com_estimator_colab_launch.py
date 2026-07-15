#!/usr/bin/env python3
"""Contract the reset-estimator Colab launch helper with zero allocation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")


REPO = Path(__file__).resolve().parents[1]
LAUNCHER = REPO / "tools/launch_ground_up_reset_com_estimator_colab.py"
JOB = REPO / "tools/colab_ground_up_reset_com_estimator_training.py"
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_HOSTED_LAUNCH_PREREGISTRATION_20260715.md"
HOSTED_PACKAGE = REPO / "outputs/analysis/ground_up_reset_com_estimator_hosted_package_contract.json"
CORRECTION = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_LAUNCH_CLEANUP_CORRECTION_PREREGISTRATION_20260715.md"
EXPECTED_HASHES = {
    "launcher": "28ac8fa42ec2959e5020efa5a0880e8fa80039c6022dc7eb55fc95e65c2c0299",
    "job": "a3e5fc38994cecd65d89fdc6b9ede23c2433e917b84583dfcced42c161e79d67",
    "prereg": "1d0e7c47cb44b13a177d9c836c1b6936579bcd29e69f1382e3fdedb0a4768d9f",
    "hosted_package": "96144a54c880a18e83e459a83e0eed771b1bc9bb55c8f147e7efc725cf4fc9c4",
    "cleanup_correction": "5a1f7a71a586a10b8199cbf0b4cb2aadb315d9502e98be23059d48097fd8fa5b",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_launcher() -> Any:
    spec = importlib.util.spec_from_file_location("reset_estimator_launcher", LAUNCHER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load launch helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def colab_sessions() -> str:
    completed = subprocess.run(
        ["colab", "sessions"], text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, timeout=30, check=True,
    )
    return completed.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source_archive = args.source_archive.resolve()
    output = args.output.resolve()
    actual_hashes = {
        "launcher": sha256(LAUNCHER), "job": sha256(JOB),
        "prereg": sha256(PREREG), "hosted_package": sha256(HOSTED_PACKAGE),
        "cleanup_correction": sha256(CORRECTION),
    }
    package = json.loads(HOSTED_PACKAGE.read_text())
    launcher = load_launcher()
    sessions_before = colab_sessions()
    with tempfile.TemporaryDirectory(prefix="reset_estimator_launch_contract_") as temporary:
        root = Path(temporary)
        assets = root / "assets"
        recovery = root / "recovery"
        plan_path = root / "plan.json"
        completed = subprocess.run(
            [
                "python3", str(LAUNCHER),
                "--assets", str(assets),
                "--recovery-dir", str(recovery),
                "--source-archive", str(source_archive),
                "--stage-assets",
                "--plan-output", str(plan_path),
            ],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=120, check=True,
            env={**os.environ, "JAX_PLATFORMS": "cpu", "CUDA_VISIBLE_DEVICES": ""},
        )
        dry_result = json.loads(completed.stdout.strip().splitlines()[-1])
        plan = json.loads(plan_path.read_text())
        asset_entries = sorted(assets.iterdir())
        staged = {
            entry.name: {
                "sha256": sha256(entry), "bytes": entry.stat().st_size,
                "is_file": entry.is_file(), "is_symlink": entry.is_symlink(),
            }
            for entry in asset_entries
        }
    sessions_after = colab_sessions()
    source = LAUNCHER.read_text()
    uploads = plan["commands"]["uploads"]
    upload_names = [Path(command[-1]).name for command in uploads]
    expected_names = sorted(launcher.load_job().EXPECTED_HASHES)
    projected_107 = launcher.parse_rate(
        "Available: 91.29 compute units\nUsage rate: approximately 1.07 per hour"
    ) * launcher.MAX_SESSION_SECONDS / 3600.0
    projected_31 = launcher.parse_rate(
        "Usage rate: approximately 3.10 per hour"
    ) * launcher.MAX_SESSION_SECONDS / 3600.0
    checks = {
        "frozen_source_hashes_exact": actual_hashes == EXPECTED_HASHES,
        "hosted_package_contract_passes": package.get("status")
        == "PASS_RESET_COM_ESTIMATOR_HOSTED_PACKAGE_CONTRACT",
        "cli_version_exact": plan["cli_version"].get("parsed_version") == "0.6.0",
        "dry_run_passes_without_allocation": dry_result.get("status")
        == "PASS_DRY_RUN_NO_ALLOCATION"
        and dry_result.get("session_created") is False
        and plan.get("allocation_authorized") is False,
        "active_sessions_unchanged": sessions_before == sessions_after,
        "session_accelerator_and_limits_exact": plan["session"]
        == "open-duck-reset-estimator-t4"
        and plan["accelerator"] == "T4"
        and plan["maximum_session_seconds"] == 2400.0
        and plan["maximum_compute_units"] == 2.0,
        "stop_reserve_exact": plan["stop_reserve_seconds"] == 120.0
        and launcher.STOP_RESERVE_SECONDS == 120.0,
        "new_status_stop_commands_exact": plan["commands"]["new"]
        == ["colab", "new", "--session", "open-duck-reset-estimator-t4", "--gpu", "T4"]
        and plan["commands"]["status"]
        == ["colab", "status", "--session", "open-duck-reset-estimator-t4"]
        and plan["commands"]["stop"]
        == ["colab", "stop", "--session", "open-duck-reset-estimator-t4"],
        "exact_upload_set_and_remote_root": upload_names == expected_names
        and len(uploads) == len(expected_names)
        and all(Path(command[-1]).parent == Path("/content") for command in uploads),
        "staged_assets_regular_and_hash_exact": set(staged) == set(expected_names)
        and all(item["is_file"] and not item["is_symlink"] for item in staged.values())
        and all(
            staged[name]["sha256"] == launcher.load_job().EXPECTED_HASHES[name]
            for name in expected_names
        ),
        "exact_download_set": [command[4] for command in plan["commands"]["downloads"]]
        == [
            "/content/GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_manifest.json",
            "/content/GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_artifacts.tar.gz",
        ],
        "allocation_flag_required_before_launch_call": "if not args.allow_colab_allocation:"
        in source and source.index("if not args.allow_colab_allocation:")
        < source.index("record = launch("),
        "rate_projection_boundary_operational": abs(projected_107 - 0.7133333333333334) < 1e-12
        and projected_107 <= 2.0 and projected_31 > 2.0
        and "if projected_units > MAX_COMPUTE_UNITS:" in source,
        "cleanup_required_before_allocation_call": source.index("session_created = True")
        < source.index("new_result = command_result("),
        "stop_reserve_applies_to_all_work": all(
            fragment in source
            for fragment in (
                'require_work_remaining(session_started, "allocation")',
                'require_work_remaining(session_started, "status")',
                'require_work_remaining(session_started, "asset upload")',
                'require_work_remaining(session_started, "hosted execution")',
                'require_work_remaining(session_started, "artifact download")',
            )
        ),
        "remaining_time_exec_and_named_cleanup_present": 'colab, "stop", "--session", SESSION'
        in source and "finally:" in source,
        "pass_requires_stop_and_total_wall": 'record["session_stop_passed"] = stop_passed'
        in source and 'not stop_passed or not record["session_wall_within_ceiling"]'
        in source and '"FAIL_HOSTED_CLEANUP_OR_SESSION_CEILING"' in source,
        "no_retry_or_session_reuse_surface": "--resume" not in source
        and "--adopt" not in source and "colab run" not in source,
        "atomic_recovery_present": "manifest_tmp.replace(manifest_final)" in source
        and "artifact_tmp.replace(artifact_final)" in source
        and "temporary.replace(path)" in source,
        "zero_remote_mutation_and_training": sessions_before == sessions_after,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = "PASS_RESET_COM_ESTIMATOR_COLAB_LAUNCH_CONTRACT" if not failed else "FAIL_RESET_COM_ESTIMATOR_COLAB_LAUNCH_CONTRACT"
    payload = {
        "schema_version": "ground_up_reset_com_estimator_colab_launch_contract.v1",
        "status": status, "checks": checks, "failed_checks": failed,
        "source_hashes": actual_hashes,
        "dry_run": {"result": dry_result, "plan": plan},
        "staged_assets": staged,
        "rate_boundary": {
            "rate_1_07_projected_units": projected_107,
            "rate_3_10_projected_units": projected_31,
        },
        "session_inventory": {"before": sessions_before, "after": sessions_after},
        "execution": {
            "training_steps": 0, "colab_sessions_created": 0,
            "remote_upload_bytes": 0, "remote_download_bytes": 0,
            "local_gpu_or_igpu": False, "robot_or_rdk": False,
        },
        "authority": {
            "allocation_now": False, "training_now": False,
            "explicit_user_approval_required": True,
            "behavior_evaluation": False, "robot_or_rdk": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
