#!/usr/bin/env python3
"""Stage, dry-run, or explicitly launch the reset-estimator Colab job."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Any


REPO = Path(__file__).resolve().parents[1]
JOB = REPO / "tools/colab_ground_up_reset_com_estimator_training.py"
SESSION = "open-duck-reset-estimator-t4"
ACCELERATOR = "T4"
MAX_SESSION_SECONDS = 2_400.0
MAX_COMPUTE_UNITS = 2.0
REMOTE_ROOT = Path("/content")
REMOTE_MANIFEST = REMOTE_ROOT / "GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_manifest.json"
REMOTE_ARTIFACT = REMOTE_ROOT / "GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_artifacts.tar.gz"
RESULT_PREFIX = "GROUND_UP_RESET_ESTIMATOR_RESULT="
EXPECTED_CLI_VERSION = "0.6.0"
EXPECTED_JOB_SHA256 = "a3e5fc38994cecd65d89fdc6b9ede23c2433e917b84583dfcced42c161e79d67"
RATE_PATTERN = re.compile(
    r"Usage rate:\s*approximately\s*([0-9]+(?:\.[0-9]+)?)\s*per hour",
    re.IGNORECASE,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_job() -> Any:
    spec = importlib.util.spec_from_file_location("reset_estimator_colab_job", JOB)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load hosted job")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def asset_sources(source_archive: Path, job: Any) -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    for name in job.PATCHES:
        mapping[name] = REPO / "patches" / name
    mapping[job.ACTOR_SOURCE] = REPO / "patches/reference_residual_hard_vector_ppo_networks.py"
    mapping[job.FEATURE_TABLE] = REPO / "outputs/analysis" / job.FEATURE_TABLE
    mapping[job.SOURCE_ARCHIVE] = source_archive
    mapping[job.PREREG] = REPO / "outputs/analysis" / job.PREREG
    mapping[job.CPU_PACKAGE] = REPO / "outputs/analysis" / job.CPU_PACKAGE
    mapping[job.CPU_EXPANSION] = REPO / "outputs/analysis" / job.CPU_EXPANSION
    if set(mapping) != set(job.EXPECTED_HASHES):
        raise RuntimeError("asset source map differs from hosted job hash map")
    return mapping


def stage_assets(destination: Path, source_archive: Path, job: Any) -> dict[str, Any]:
    if destination.exists():
        raise FileExistsError(f"staged asset destination already exists: {destination}")
    sources = asset_sources(source_archive.resolve(), job)
    for name, source in sources.items():
        if not source.is_file() or source.is_symlink():
            raise FileNotFoundError(f"asset source must be a regular nonsymlink file: {source}")
        if sha256(source) != job.EXPECTED_HASHES[name]:
            raise ValueError(f"asset source hash mismatch: {source}")
    destination.mkdir(parents=True)
    copied: list[dict[str, Any]] = []
    for name in sorted(sources):
        target = destination / name
        shutil.copy2(sources[name], target)
        copied.append({"name": name, "bytes": target.stat().st_size, "sha256": sha256(target)})
    validated = job.validate_assets(destination)
    return {
        "status": "PASS_EXACT_ASSET_STAGING",
        "destination": str(destination),
        "assets": copied,
        "validated_hashes": validated,
    }


def validate_staged_assets(assets: Path, job: Any) -> dict[str, str]:
    if not assets.is_dir() or assets.is_symlink():
        raise ValueError("assets must be a real directory")
    children = list(assets.iterdir())
    if any(child.is_symlink() or not child.is_file() for child in children):
        raise ValueError("every staged asset must be a regular nonsymlink file")
    names = {child.name for child in children}
    if names != set(job.EXPECTED_HASHES):
        raise ValueError(
            f"staged asset set mismatch: missing={sorted(set(job.EXPECTED_HASHES)-names)} "
            f"extra={sorted(names-set(job.EXPECTED_HASHES))}"
        )
    return job.validate_assets(assets)


def command_result(
    command: list[str], *, timeout: float | None = None, check: bool = True,
) -> dict[str, Any]:
    started = time.monotonic()
    completed = subprocess.run(
        command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        timeout=timeout, check=False,
    )
    result = {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "elapsed_seconds": time.monotonic() - started,
    }
    if check and completed.returncode != 0:
        raise RuntimeError(json.dumps(result, sort_keys=True))
    return result


def cli_version(colab: str) -> dict[str, Any]:
    result = command_result([colab, "version"], timeout=30)
    match = re.search(r"Version:\s*([^\s]+)", result["stdout"])
    version = match.group(1) if match else None
    if version != EXPECTED_CLI_VERSION:
        raise RuntimeError(f"unexpected Colab CLI version: {version}")
    result["parsed_version"] = version
    return result


def parse_rate(status_output: str) -> float:
    match = RATE_PATTERN.search(status_output)
    if not match:
        raise ValueError("Colab status omitted the approximate compute-unit rate")
    rate = float(match.group(1))
    if not math.isfinite(rate) or rate <= 0.0:
        raise ValueError(f"invalid Colab compute-unit rate: {rate}")
    return rate


def remaining_seconds(started: float) -> float:
    return MAX_SESSION_SECONDS - (time.monotonic() - started)


def require_remaining(started: float, label: str) -> float:
    remaining = remaining_seconds(started)
    if remaining <= 0.0:
        raise TimeoutError(f"session wall ceiling reached before {label}")
    return remaining


def build_plan(assets: Path, recovery: Path, colab: str, job: Any) -> dict[str, Any]:
    uploads = [
        {
            "local": str((assets / name).resolve()),
            "remote": str(REMOTE_ROOT / name),
            "sha256": job.EXPECTED_HASHES[name],
            "bytes": (assets / name).stat().st_size,
        }
        for name in sorted(job.EXPECTED_HASHES)
    ]
    manifest_final = recovery / REMOTE_MANIFEST.name
    artifact_final = recovery / REMOTE_ARTIFACT.name
    launch_record = recovery / "GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_launch.json"
    for path in (manifest_final, artifact_final, launch_record):
        if path.exists() or path.with_suffix(path.suffix + ".tmp").exists():
            raise FileExistsError(f"recovery output already exists: {path}")
    commands = {
        "new": [colab, "new", "--session", SESSION, "--gpu", ACCELERATOR],
        "status": [colab, "status", "--session", SESSION],
        "uploads": [
            [colab, "upload", "--session", SESSION, item["local"], item["remote"]]
            for item in uploads
        ],
        "exec_prefix": [
            colab, "exec", "--session", SESSION, "--file", str(JOB.resolve()),
            "--timeout", "<remaining_session_seconds>",
        ],
        "downloads": [
            [colab, "download", "--session", SESSION, str(REMOTE_MANIFEST), str(manifest_final) + ".tmp"],
            [colab, "download", "--session", SESSION, str(REMOTE_ARTIFACT), str(artifact_final) + ".tmp"],
        ],
        "stop": [colab, "stop", "--session", SESSION],
    }
    return {
        "schema_version": "ground_up_reset_estimator_colab_launch_plan.v1",
        "status": "PASS_DRY_RUN_PLAN",
        "session": SESSION,
        "accelerator": ACCELERATOR,
        "maximum_session_seconds": MAX_SESSION_SECONDS,
        "maximum_compute_units": MAX_COMPUTE_UNITS,
        "job": {"path": str(JOB), "sha256": sha256(JOB)},
        "uploads": uploads,
        "commands": commands,
        "recovery": {
            "manifest": str(manifest_final),
            "artifact": str(artifact_final),
            "launch_record": str(launch_record),
        },
        "allocation_authorized": False,
    }


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    if path.exists() or temporary.exists():
        raise FileExistsError(f"refusing to overwrite: {path}")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def extract_remote_result(stdout: str) -> dict[str, Any]:
    matches = [line[len(RESULT_PREFIX):] for line in stdout.splitlines() if line.startswith(RESULT_PREFIX)]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one hosted result marker, found {len(matches)}")
    result = json.loads(matches[0])
    if result.get("status") != "PASS_TRAINING_ARTIFACT_CONTRACT_ONLY":
        raise RuntimeError(f"hosted result did not pass: {result}")
    if result.get("behavior_status") != "UNEVALUATED":
        raise RuntimeError("hosted result behavior status changed")
    return result


def verify_downloads(
    manifest_tmp: Path, artifact_tmp: Path, remote_result: dict[str, Any], job: Any,
) -> dict[str, Any]:
    if sha256(manifest_tmp) != remote_result["manifest"]["sha256"]:
        raise ValueError("downloaded manifest hash mismatch")
    if sha256(artifact_tmp) != remote_result["artifact"]["sha256"]:
        raise ValueError("downloaded artifact hash mismatch")
    if artifact_tmp.stat().st_size != remote_result["artifact"]["bytes"]:
        raise ValueError("downloaded artifact byte count mismatch")
    manifest = json.loads(manifest_tmp.read_text())
    checks = {
        "status_exact": manifest.get("status") == "PASS_TRAINING_ARTIFACT_CONTRACT_ONLY",
        "behavior_unevaluated": manifest.get("behavior_status") == "UNEVALUATED",
        "arm_exact": manifest.get("arm", {}).get("name") == job.ARM_NAME,
        "steps_exact": manifest.get("arm", {}).get("checkpoint_steps") == job.EXPECTED_STEPS,
        "input_hashes_exact": manifest.get("input_hashes") == job.EXPECTED_HASHES,
        "limits_exact": manifest.get("execution", {}).get("maximum_hosted_seconds")
        == job.MAX_HOSTED_SECONDS
        and manifest.get("execution", {}).get("maximum_compute_units")
        == job.MAX_COMPUTE_UNITS,
        "single_process_no_resume": manifest.get("execution", {}).get("session_count") == 1
        and manifest.get("execution", {}).get("training_process_count") == 1
        and manifest.get("execution", {}).get("resume") is False,
        "reward_nonselective": manifest.get("selection", {}).get("training_reward_used") is False,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise ValueError(f"downloaded manifest contract failed: {failed}")
    return {
        "checks": checks,
        "manifest_sha256": sha256(manifest_tmp),
        "artifact_sha256": sha256(artifact_tmp),
        "artifact_bytes": artifact_tmp.stat().st_size,
    }


def launch(
    plan: dict[str, Any], assets: Path, recovery: Path, colab: str, job: Any,
) -> dict[str, Any]:
    session_started = time.monotonic()
    record: dict[str, Any] = {
        "schema_version": "ground_up_reset_estimator_colab_launch.v1",
        "status": "RUNNING",
        "plan": plan,
        "commands": [],
        "session_stop": None,
    }
    session_created = False
    manifest_final = Path(plan["recovery"]["manifest"])
    artifact_final = Path(plan["recovery"]["artifact"])
    manifest_tmp = manifest_final.with_suffix(manifest_final.suffix + ".tmp")
    artifact_tmp = artifact_final.with_suffix(artifact_final.suffix + ".tmp")
    try:
        new_result = command_result(plan["commands"]["new"], timeout=120)
        record["commands"].append(new_result)
        session_created = True
        status_result = command_result(
            plan["commands"]["status"], timeout=min(60.0, require_remaining(session_started, "status"))
        )
        record["commands"].append(status_result)
        rate = parse_rate(status_result["stdout"])
        projected_units = rate * MAX_SESSION_SECONDS / 3600.0
        record["compute_rate_per_hour"] = rate
        record["projected_max_compute_units"] = projected_units
        if projected_units > MAX_COMPUTE_UNITS:
            raise RuntimeError(
                f"projected compute use {projected_units} exceeds {MAX_COMPUTE_UNITS}"
            )
        for upload_command in plan["commands"]["uploads"]:
            result = command_result(
                upload_command,
                timeout=require_remaining(session_started, "asset upload"),
            )
            record["commands"].append(result)
        exec_timeout = max(1.0, require_remaining(session_started, "hosted execution"))
        exec_command = [
            colab, "exec", "--session", SESSION, "--file", str(JOB.resolve()),
            "--timeout", f"{exec_timeout:.3f}",
        ]
        exec_result = command_result(exec_command, timeout=exec_timeout + 30.0)
        record["commands"].append(exec_result)
        remote_result = extract_remote_result(exec_result["stdout"])
        record["remote_result"] = remote_result
        for download_command in plan["commands"]["downloads"]:
            result = command_result(
                download_command,
                timeout=require_remaining(session_started, "artifact download"),
            )
            record["commands"].append(result)
        verification = verify_downloads(manifest_tmp, artifact_tmp, remote_result, job)
        record["download_verification"] = verification
        manifest_tmp.replace(manifest_final)
        artifact_tmp.replace(artifact_final)
        record["status"] = "PASS_HOSTED_ARTIFACTS_RECOVERED"
    except Exception as error:
        record["status"] = "FAIL_HOSTED_LAUNCH_OR_RECOVERY"
        record["error"] = repr(error)
        raise
    finally:
        if session_created:
            record["session_stop"] = command_result(
                plan["commands"]["stop"], timeout=120, check=False
            )
        record["session_elapsed_seconds"] = time.monotonic() - session_started
        record["session_wall_within_ceiling_before_stop"] = (
            record["session_elapsed_seconds"] <= MAX_SESSION_SECONDS
        )
        record_path = Path(plan["recovery"]["launch_record"])
        if not record_path.exists() and not record_path.with_suffix(record_path.suffix + ".tmp").exists():
            write_json_atomic(record_path, record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--recovery-dir", type=Path, required=True)
    parser.add_argument("--source-archive", type=Path)
    parser.add_argument("--stage-assets", action="store_true")
    parser.add_argument("--allow-colab-allocation", action="store_true")
    parser.add_argument("--plan-output", type=Path, required=True)
    parser.add_argument("--colab-bin", default="colab")
    args = parser.parse_args()
    if sha256(JOB) != EXPECTED_JOB_SHA256:
        raise RuntimeError("hosted job changed after launch preregistration")
    job = load_job()
    assets = args.assets.resolve()
    recovery = args.recovery_dir.resolve()
    staging = None
    if args.stage_assets:
        if args.source_archive is None:
            raise ValueError("--stage-assets requires --source-archive")
        staging = stage_assets(assets, args.source_archive.resolve(), job)
    validate_staged_assets(assets, job)
    recovery.mkdir(parents=True, exist_ok=True)
    version = cli_version(args.colab_bin)
    plan = build_plan(assets, recovery, args.colab_bin, job)
    plan["cli_version"] = version
    plan["asset_staging"] = staging
    write_json_atomic(args.plan_output.resolve(), plan)
    if not args.allow_colab_allocation:
        print(json.dumps({
            "status": "PASS_DRY_RUN_NO_ALLOCATION",
            "plan": str(args.plan_output.resolve()),
            "session_created": False,
        }, sort_keys=True))
        return 0
    plan["allocation_authorized"] = True
    record = launch(plan, assets, recovery, args.colab_bin, job)
    print(json.dumps({
        "status": record["status"],
        "launch_record": plan["recovery"]["launch_record"],
        "manifest": plan["recovery"]["manifest"],
        "artifact": plan["recovery"]["artifact"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
