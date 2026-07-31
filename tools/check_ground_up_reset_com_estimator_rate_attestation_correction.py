#!/usr/bin/env python3
"""Contract the reset-estimator rate-attestation correction without allocation."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Callable


os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

REPO = Path(__file__).resolve().parents[1]
LAUNCHER = REPO / "tools/launch_ground_up_reset_com_estimator_colab.py"
JOB = REPO / "tools/colab_ground_up_reset_com_estimator_training.py"
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_RATE_ATTESTATION_CORRECTION_PREREGISTRATION_20260715.md"
PRIOR_RESULT = REPO / "outputs/analysis/ground_up_reset_com_estimator_hosted_launch_result.json"
PRIOR_RAW = REPO / "outputs/analysis/ground_up_reset_com_estimator_hosted_run_20260715/recovery/GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_launch.json"
HOSTED_PACKAGE = REPO / "outputs/analysis/ground_up_reset_com_estimator_hosted_package_contract.json"
CLI_SESSION_SOURCE = Path(
    "/home/lsd/.local/share/uv/tools/google-colab-cli/lib/python3.12/"
    "site-packages/colab_cli/commands/session.py"
)
EXPECTED_HASHES = {
    "launcher": "97f2d45f17ec58958e243568ab3b9fca15ad5a95f67d3fd75092abab948c3abe",
    "job": "a3e5fc38994cecd65d89fdc6b9ede23c2433e917b84583dfcced42c161e79d67",
    "prereg": "5efb869fe8a73b655868b50b1d735c86479dd9b3312623343f10a9b274ed635a",
    "prior_result": "49ecebf66c9c1f30ce743957d48b6b128da45acea0f0918c0061cf6e9237828a",
    "prior_raw": "823c0875b280c1ebce8b9fa0dfb2acf74248e73cef5f4b17572aa92c15d8ed14",
    "hosted_package": "96144a54c880a18e83e459a83e0eed771b1bc9bb55c8f147e7efc725cf4fc9c4",
    "cli_session_source": "59d50c3fe04bfcd1eaa7e2441e79d5e2bed2d0201c469c37e5e614351bbe0c1c",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_launcher() -> Any:
    spec = importlib.util.spec_from_file_location("corrected_reset_launcher", LAUNCHER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load corrected launcher")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def colab_sessions() -> str:
    completed = subprocess.run(
        ["colab", "sessions"], text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, timeout=30, check=True,
    )
    return completed.stdout


def must_fail(function: Callable[[], Any]) -> bool:
    try:
        function()
    except (TypeError, ValueError):
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source_archive = args.source_archive.resolve()
    output = args.output.resolve()

    paths = {
        "launcher": LAUNCHER,
        "job": JOB,
        "prereg": PREREG,
        "prior_result": PRIOR_RESULT,
        "prior_raw": PRIOR_RAW,
        "hosted_package": HOSTED_PACKAGE,
        "cli_session_source": CLI_SESSION_SOURCE,
    }
    actual_hashes = {name: sha256(path) for name, path in paths.items()}
    launcher = load_launcher()
    prior_result = json.loads(PRIOR_RESULT.read_text())
    prior_raw = json.loads(PRIOR_RAW.read_text())
    hosted_package = json.loads(HOSTED_PACKAGE.read_text())
    source = LAUNCHER.read_text()
    cli_source = CLI_SESSION_SOURCE.read_text()

    fixed_now = datetime(2026, 7, 15, 21, 0, 0, tzinfo=timezone.utc)
    validate = launcher.validate_compute_attestation
    nominal = validate(1.07, 91.29, fixed_now.isoformat(), now=fixed_now)
    ceiling = validate(3.0, 91.29, fixed_now.isoformat(), now=fixed_now)
    old_boundary = validate(
        1.07, 91.29,
        (fixed_now - timedelta(seconds=600)).isoformat(), now=fixed_now,
    )
    future_boundary = validate(
        1.07, 91.29,
        (fixed_now + timedelta(seconds=60)).isoformat(), now=fixed_now,
    )
    invalid_attestations = {
        "rate_above_ceiling": must_fail(
            lambda: validate(3.000001, 91.29, fixed_now.isoformat(), now=fixed_now)
        ),
        "balance_below_floor": must_fail(
            lambda: validate(1.07, 1.999999, fixed_now.isoformat(), now=fixed_now)
        ),
        "stale": must_fail(
            lambda: validate(
                1.07, 91.29,
                (fixed_now - timedelta(seconds=600.000001)).isoformat(),
                now=fixed_now,
            )
        ),
        "future": must_fail(
            lambda: validate(
                1.07, 91.29,
                (fixed_now + timedelta(seconds=60.000001)).isoformat(),
                now=fixed_now,
            )
        ),
        "naive_timestamp": must_fail(
            lambda: validate(1.07, 91.29, "2026-07-15T21:00:00", now=fixed_now)
        ),
        "bad_timestamp": must_fail(
            lambda: validate(1.07, 91.29, "not-a-time", now=fixed_now)
        ),
        "zero_rate": must_fail(
            lambda: validate(0.0, 91.29, fixed_now.isoformat(), now=fixed_now)
        ),
        "negative_rate": must_fail(
            lambda: validate(-1.0, 91.29, fixed_now.isoformat(), now=fixed_now)
        ),
        "nan_rate": must_fail(
            lambda: validate(math.nan, 91.29, fixed_now.isoformat(), now=fixed_now)
        ),
        "infinite_rate": must_fail(
            lambda: validate(math.inf, 91.29, fixed_now.isoformat(), now=fixed_now)
        ),
        "nan_balance": must_fail(
            lambda: validate(1.07, math.nan, fixed_now.isoformat(), now=fixed_now)
        ),
        "naive_now": must_fail(
            lambda: validate(
                1.07, 91.29, fixed_now.isoformat(),
                now=datetime(2026, 7, 15, 21, 0, 0),
            )
        ),
    }

    captured_status = prior_raw["commands"][1]["stdout"]
    launcher.validate_session_status(captured_status)
    invalid_statuses = {
        "wrong_session": must_fail(
            lambda: launcher.validate_session_status(
                captured_status.replace(launcher.SESSION, "wrong-session")
            )
        ),
        "wrong_hardware": must_fail(
            lambda: launcher.validate_session_status(
                captured_status.replace("Hardware: T4", "Hardware: L4")
            )
        ),
        "wrong_variant": must_fail(
            lambda: launcher.validate_session_status(
                captured_status.replace("Variant: GPU", "Variant: DEFAULT")
            )
        ),
        "wrong_state": must_fail(
            lambda: launcher.validate_session_status(
                captured_status.replace("Status: IDLE", "Status: BUSY")
            )
        ),
        "extra_line": must_fail(
            lambda: launcher.validate_session_status(captured_status + "extra\n")
        ),
    }

    sessions_before = colab_sessions()
    observed_at = datetime.now(timezone.utc).isoformat()
    with tempfile.TemporaryDirectory(prefix="reset_estimator_rate_contract_") as temporary:
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
                "--compute-rate-per-hour", "1.07",
                "--available-compute-units", "91.29",
                "--rate-observed-at", observed_at,
                "--plan-output", str(plan_path),
            ],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=120, check=True,
            env={**os.environ, "JAX_PLATFORMS": "cpu", "CUDA_VISIBLE_DEVICES": ""},
        )
        dry_result = json.loads(completed.stdout.strip().splitlines()[-1])
        plan = json.loads(plan_path.read_text())
        staged = {
            entry.name: {
                "sha256": sha256(entry),
                "bytes": entry.stat().st_size,
                "is_file": entry.is_file(),
                "is_symlink": entry.is_symlink(),
            }
            for entry in sorted(assets.iterdir())
        }
        missing = subprocess.run(
            [
                "python3", str(LAUNCHER),
                "--assets", str(assets),
                "--recovery-dir", str(root / "missing-recovery"),
                "--plan-output", str(root / "missing-plan.json"),
            ],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=30, check=False,
        )
    sessions_after = colab_sessions()

    job = launcher.load_job()
    attestation = plan["compute_attestation"]
    main_source = source[source.index("def main()") :]
    checks = {
        "frozen_source_hashes_exact": actual_hashes == EXPECTED_HASHES,
        "prior_failed_launch_exact": prior_result.get("decision")
        == "STOP_NO_RETRY_STATUS_RATE_UNAVAILABLE"
        and prior_result.get("execution", {}).get("training_steps") == 0
        and prior_raw.get("status") == "FAIL_HOSTED_LAUNCH_OR_RECOVERY"
        and len(prior_raw.get("commands", [])) == 2
        and prior_raw.get("session_stop_passed") is True,
        "hosted_package_and_job_unchanged": hosted_package.get("status")
        == "PASS_RESET_COM_ESTIMATOR_HOSTED_PACKAGE_CONTRACT"
        and actual_hashes["job"] == EXPECTED_HASHES["job"],
        "cli_version_and_source_exact": launcher.cli_version("colab").get(
            "parsed_version"
        ) == "0.6.0"
        and actual_hashes["cli_session_source"]
        == EXPECTED_HASHES["cli_session_source"],
        "cli_has_no_rate_or_balance_surface": "Usage rate" not in cli_source
        and "compute_rate" not in cli_source
        and "compute_units" not in cli_source,
        "attestation_precedes_launch_call": main_source.index(
            "compute_attestation = validate_compute_attestation("
        ) < main_source.index("record = launch(")
        and source.count("record = launch(") == 1,
        "required_attestation_cli_surface": all(
            fragment in source
            for fragment in (
                'parser.add_argument("--compute-rate-per-hour", type=float, required=True)',
                'parser.add_argument("--available-compute-units", type=float, required=True)',
                'parser.add_argument("--rate-observed-at", required=True)',
            )
        ) and missing.returncode == 2
        and "--compute-rate-per-hour" in missing.stdout
        and "--available-compute-units" in missing.stdout
        and "--rate-observed-at" in missing.stdout,
        "nominal_projection_exact": nominal["source"]
        == "COLAB_RESOURCES_UI_OPERATOR_ATTESTATION"
        and abs(nominal["projected_max_compute_units"] - 0.7133333333333334)
        < 1e-12,
        "ceiling_projection_exact": ceiling["projected_max_compute_units"] == 2.0,
        "freshness_boundaries_exact": old_boundary["age_seconds"] == 600.0
        and future_boundary["age_seconds"] == -60.0,
        "invalid_attestations_fail": all(invalid_attestations.values()),
        "captured_t4_status_passes_without_rate": "Usage rate" not in captured_status,
        "wrong_session_identity_states_fail": all(invalid_statuses.values()),
        "postallocation_status_no_rate_parse": "validate_session_status(status_result[\"stdout\"])"
        in source and "parse_rate" not in source,
        "dry_run_passes_without_allocation": dry_result.get("status")
        == "PASS_DRY_RUN_NO_ALLOCATION"
        and dry_result.get("session_created") is False
        and plan.get("allocation_authorized") is False,
        "plan_attestation_exact": attestation["source"]
        == "COLAB_RESOURCES_UI_OPERATOR_ATTESTATION"
        and attestation["compute_rate_per_hour"] == 1.07
        and attestation["available_compute_units"] == 91.29
        and attestation["maximum_age_seconds"] == 600.0
        and attestation["maximum_future_seconds"] == 60.0
        and attestation["minimum_available_compute_units"] == 2.0
        and abs(attestation["projected_max_compute_units"] - 0.7133333333333334)
        < 1e-12,
        "exact_staged_asset_set_and_hashes": len(staged) == 19
        and set(staged) == set(job.EXPECTED_HASHES)
        and all(
            item["is_file"] and not item["is_symlink"]
            and item["sha256"] == job.EXPECTED_HASHES[name]
            for name, item in staged.items()
        ),
        "prior_lifecycle_invariants_retained": plan["session"]
        == "open-duck-reset-estimator-t4"
        and plan["accelerator"] == "T4"
        and plan["maximum_session_seconds"] == 2400.0
        and plan["maximum_compute_units"] == 2.0
        and plan["stop_reserve_seconds"] == 120.0
        and plan["commands"]["status"]
        == ["colab", "status", "--session", "open-duck-reset-estimator-t4"]
        and plan["commands"]["stop"]
        == ["colab", "stop", "--session", "open-duck-reset-estimator-t4"],
        "session_inventory_unchanged": sessions_before == sessions_after,
        "zero_remote_mutation_and_training": sessions_before == sessions_after,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_RESET_COM_ESTIMATOR_RATE_ATTESTATION_LAUNCH_CORRECTION_CONTRACT"
        if not failed
        else "FAIL_RESET_COM_ESTIMATOR_RATE_ATTESTATION_LAUNCH_CORRECTION_CONTRACT"
    )
    payload = {
        "schema_version": "ground_up_reset_estimator_rate_attestation_correction_contract.v1",
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "source_hashes": actual_hashes,
        "cli_audit": {
            "version": "0.6.0",
            "session_source_sha256": actual_hashes["cli_session_source"],
            "rate_or_balance_output_surface": False,
            "captured_status": captured_status,
        },
        "boundary_tests": {
            "nominal": nominal,
            "ceiling": ceiling,
            "old_boundary": old_boundary,
            "future_boundary": future_boundary,
            "invalid_attestations": invalid_attestations,
            "invalid_statuses": invalid_statuses,
        },
        "dry_run": {"result": dry_result, "plan": plan},
        "staged_assets": staged,
        "session_inventory": {"before": sessions_before, "after": sessions_after},
        "execution": {
            "colab_sessions_created": 0,
            "remote_upload_bytes": 0,
            "training_processes": 0,
            "training_steps": 0,
            "local_gpu_or_igpu": False,
            "robot_or_rdk": False,
        },
        "authority": {
            "allocation_now": False,
            "training_now": False,
            "fresh_operator_attestation_required": True,
            "new_explicit_user_approval_required": True,
            "behavior_evaluation": False,
            "robot_or_rdk": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
