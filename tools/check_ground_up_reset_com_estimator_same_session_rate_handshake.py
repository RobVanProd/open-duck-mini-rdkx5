#!/usr/bin/env python3
"""Contract the same-session Colab rate handshake with zero allocation."""

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
import threading
import time
from typing import Any, Callable

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

REPO = Path(__file__).resolve().parents[1]
LAUNCHER = REPO / "tools/launch_ground_up_reset_com_estimator_colab.py"
JOB = REPO / "tools/colab_ground_up_reset_com_estimator_training.py"
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_SAME_SESSION_RATE_HANDSHAKE_PREREGISTRATION_20260715.md"
PRIOR_CONTRACT = REPO / "outputs/analysis/ground_up_reset_com_estimator_rate_attestation_correction_contract.json"
PRIOR_RESULT = REPO / "outputs/analysis/ground_up_reset_com_estimator_hosted_launch_result.json"
HOSTED_PACKAGE = REPO / "outputs/analysis/ground_up_reset_com_estimator_hosted_package_contract.json"
EXPECTED_HASHES = {
    "launcher": "afb5acc580239f729d4d0832dd29a0c7163e87b63856ff6b1111eb393683e241",
    "job": "a3e5fc38994cecd65d89fdc6b9ede23c2433e917b84583dfcced42c161e79d67",
    "prereg": "b395f2c055900979672160462f50255841c756d1d259155ce74724d78c6caa8a",
    "prior_contract": "3d00ca87641f68e8362139c2f0b3690bcffb8cfc6623782966f436301f637ff5",
    "prior_result": "49ecebf66c9c1f30ce743957d48b6b128da45acea0f0918c0061cf6e9237828a",
    "hosted_package": "96144a54c880a18e83e459a83e0eed771b1bc9bb55c8f147e7efc725cf4fc9c4",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_launcher() -> Any:
    spec = importlib.util.spec_from_file_location("handshake_launcher", LAUNCHER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load launcher")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sessions() -> str:
    return subprocess.run(
        ["colab", "sessions"], text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, timeout=30, check=True,
    ).stdout


def fails(function: Callable[[], Any]) -> bool:
    try:
        function()
    except (FileExistsError, TimeoutError, TypeError, ValueError):
        return True
    return False


def payload(rate: float, balance: float, observed: datetime, **overrides: Any) -> dict[str, Any]:
    value = {
        "source": "COLAB_RESOURCES_UI_OPERATOR_ATTESTATION",
        "session": "open-duck-reset-estimator-t4",
        "compute_rate_per_hour": rate,
        "available_compute_units": balance,
        "collector_received_at": observed.isoformat(),
    }
    value.update(overrides)
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "launcher": LAUNCHER, "job": JOB, "prereg": PREREG,
        "prior_contract": PRIOR_CONTRACT, "prior_result": PRIOR_RESULT,
        "hosted_package": HOSTED_PACKAGE,
    }
    hashes = {name: sha256(path) for name, path in paths.items()}
    launcher = load_launcher()
    source = LAUNCHER.read_text()
    prior_contract = json.loads(PRIOR_CONTRACT.read_text())
    prior_result = json.loads(PRIOR_RESULT.read_text())
    hosted_package = json.loads(HOSTED_PACKAGE.read_text())
    fixed = datetime(2026, 7, 15, 21, 30, tzinfo=timezone.utc)
    validate = launcher.validate_attestation_payload
    nominal = validate(payload(1.07, 79.36, fixed), now=fixed)
    ceiling = validate(payload(3.0, 79.36, fixed), now=fixed)
    old_edge = validate(payload(1.07, 79.36, fixed - timedelta(seconds=120)), now=fixed)
    future_edge = validate(payload(1.07, 79.36, fixed + timedelta(seconds=60)), now=fixed)
    invalid = {
        "zero": fails(lambda: validate(payload(0.0, 79.36, fixed), now=fixed)),
        "nan": fails(lambda: validate(payload(math.nan, 79.36, fixed), now=fixed)),
        "over": fails(lambda: validate(payload(3.000001, 79.36, fixed), now=fixed)),
        "balance": fails(lambda: validate(payload(1.07, 1.999999, fixed), now=fixed)),
        "stale": fails(lambda: validate(payload(1.07, 79.36, fixed - timedelta(seconds=120.000001)), now=fixed)),
        "future": fails(lambda: validate(payload(1.07, 79.36, fixed + timedelta(seconds=60.000001)), now=fixed)),
        "source": fails(lambda: validate(payload(1.07, 79.36, fixed, source="wrong"), now=fixed)),
        "session": fails(lambda: validate(payload(1.07, 79.36, fixed, session="wrong"), now=fixed)),
        "schema": fails(lambda: validate({**payload(1.07, 79.36, fixed), "extra": 1}, now=fixed)),
    }

    before = sessions()
    with tempfile.TemporaryDirectory(prefix="reset_estimator_handshake_contract_") as temp:
        root = Path(temp)
        assets, recovery = root / "assets", root / "recovery"
        plan_path, attestation = root / "plan.json", root / "rate.json"
        completed = subprocess.run(
            ["python3", str(LAUNCHER), "--assets", str(assets),
             "--recovery-dir", str(recovery), "--source-archive", str(args.source_archive.resolve()),
             "--stage-assets", "--attestation-file", str(attestation),
             "--plan-output", str(plan_path)],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=120, check=True,
            env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu"},
        )
        dry = json.loads(completed.stdout.strip().splitlines()[-1])
        plan = json.loads(plan_path.read_text())
        staged = {p.name: sha256(p) for p in assets.iterdir()}

        wait_file = root / "wait.json"
        fresh_payload = payload(1.07, 79.36, datetime.now(timezone.utc))
        writer = threading.Thread(
            target=lambda: (time.sleep(0.05), wait_file.write_text(json.dumps(fresh_payload)))
        )
        writer.start()
        waited = launcher.wait_for_compute_attestation(wait_file, time.monotonic())
        writer.join()
        timeout_file = root / "timeout.json"
        original_wait = launcher.ATTESTATION_WAIT_SECONDS
        launcher.ATTESTATION_WAIT_SECONDS = 0.05
        timeout_pass = fails(
            lambda: launcher.wait_for_compute_attestation(timeout_file, time.monotonic())
        )
        launcher.ATTESTATION_WAIT_SECONDS = original_wait
    after = sessions()

    launch_source = source[source.index("def launch(") : source.index("def main()")]
    job = launcher.load_job()
    checks = {
        "sources_exact": hashes == EXPECTED_HASHES,
        "upstream_states_exact": prior_contract["status"] == "PASS_RESET_COM_ESTIMATOR_RATE_ATTESTATION_LAUNCH_CORRECTION_CONTRACT"
        and prior_result["decision"] == "STOP_NO_RETRY_STATUS_RATE_UNAVAILABLE"
        and hosted_package["status"] == "PASS_RESET_COM_ESTIMATOR_HOSTED_PACKAGE_CONTRACT",
        "idle_zero_evidence_frozen": "79.36" in PREREG.read_text() and "0 units/hour" in PREREG.read_text(),
        "handshake_cli_exact": 'parser.add_argument("--attestation-file", type=Path, required=True)' in source
        and "--compute-rate-per-hour" not in source,
        "path_absent_in_dry_run": not attestation.exists() and dry["session_created"] is False,
        "plan_handshake_exact": plan["rate_handshake"]["attestation_file"] == str(attestation)
        and plan["rate_handshake"]["wait_seconds"] == 120.0
        and plan["rate_handshake"]["maximum_age_seconds"] == 120.0
        and plan["rate_handshake"]["maximum_future_seconds"] == 60.0,
        "order_status_wait_upload": launch_source.index("validate_session_status")
        < launch_source.index("wait_for_compute_attestation")
        < launch_source.index("for upload_command"),
        "wait_uses_wall_and_stop_reserve": 'require_work_remaining(session_started, "rate attestation")' in source,
        "cleanup_armed_before_new": launch_source.index("session_created = True")
        < launch_source.index("new_result = command_result("),
        "nominal_projection": abs(nominal["projected_max_compute_units"] - 0.7133333333333334) < 1e-12,
        "ceiling_projection": ceiling["projected_max_compute_units"] == 2.0,
        "freshness_boundaries": old_edge["age_seconds"] == 120.0 and future_edge["age_seconds"] == -60.0,
        "invalid_controls_fail": all(invalid.values()),
        "local_wait_fixture": waited["compute_rate_per_hour"] == 1.07 and waited["available_compute_units"] == 79.36,
        "timeout_fixture": timeout_pass,
        "dry_run_no_allocation": dry["status"] == "PASS_DRY_RUN_NO_ALLOCATION" and plan["allocation_authorized"] is False,
        "assets_exact": len(staged) == 19 and set(staged) == set(job.EXPECTED_HASHES)
        and all(staged[name] == digest for name, digest in job.EXPECTED_HASHES.items()),
        "lifecycle_exact": plan["session"] == "open-duck-reset-estimator-t4"
        and plan["accelerator"] == "T4" and plan["maximum_session_seconds"] == 2400.0
        and plan["maximum_compute_units"] == 2.0 and plan["stop_reserve_seconds"] == 120.0,
        "session_inventory_unchanged": before == after,
        "zero_remote_or_training": before == after,
    }
    failed = sorted(k for k, v in checks.items() if not v)
    status = "PASS_RESET_COM_ESTIMATOR_SAME_SESSION_RATE_HANDSHAKE_CONTRACT" if not failed else "FAIL_RESET_COM_ESTIMATOR_SAME_SESSION_RATE_HANDSHAKE_CONTRACT"
    result = {
        "schema_version": "ground_up_reset_estimator_same_session_rate_handshake_contract.v1",
        "status": status, "checks": checks, "failed_checks": failed,
        "source_hashes": hashes,
        "boundary_tests": {"nominal": nominal, "ceiling": ceiling, "old_edge": old_edge,
                           "future_edge": future_edge, "invalid": invalid,
                           "local_wait": waited, "timeout": timeout_pass},
        "dry_run": {"result": dry, "plan": plan},
        "staged_assets": staged,
        "session_inventory": {"before": before, "after": after},
        "execution": {"sessions_created": 0, "remote_upload_bytes": 0,
                      "training_processes": 0, "training_steps": 0,
                      "local_gpu_or_igpu": False, "robot_or_rdk": False},
        "authority": {"single_interactive_launch_approved": True,
                      "allocation_after_contract": True,
                      "training_only_after_live_rate_pass": True,
                      "behavior_evaluation": False, "robot_or_rdk": False},
    }
    args.output.resolve().write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
