#!/usr/bin/env python3
"""Stage, plan, or launch the single epsilon-aware reset-estimator T4 job."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Any


REPO = Path(__file__).resolve().parents[1]
BASE = REPO / "tools/launch_ground_up_reset_com_estimator_colab.py"
HOSTED = REPO / "tools/colab_ground_up_reset_com_estimator_training.py"
WRAPPER = REPO / "tools/colab_ground_up_reset_com_estimator_epsilon_aware_training.py"
ULP_JSON = REPO / "outputs/analysis/ground_up_reset_com_estimator_action_distribution_ulp_sensitivity.json"
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_EPSILON_AWARE_HOSTED_EXPANSION_CORRECTION_PREREGISTRATION_20260715.md"
CONTRACT = REPO / "outputs/analysis/ground_up_reset_com_estimator_epsilon_aware_expansion_contract.json"
SESSION = "open-duck-reset-estimator-epsilon2-t4"
ACCELERATOR = "T4"
MAX_SESSION_SECONDS = 2_400.0
STOP_RESERVE_SECONDS = 120.0
COMPUTE_UNITS = "UNMEASURED"
REMOTE = Path("/content")
MANIFEST_NAME = "GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_manifest.json"
ARTIFACT_NAME = "GROUND_UP_RESET_COM_ESTIMATOR_TRAINING_artifacts.tar.gz"
EXPECTED_EXTRA = {
    HOSTED.name: "a3e5fc38994cecd65d89fdc6b9ede23c2433e917b84583dfcced42c161e79d67",
    WRAPPER.name: "fc8e03fa7f0469a825a10a7fa70bdae81a45c2f7333b279f260984d39983f9ca",
    ULP_JSON.name: "a30df798a2dd659f0299c92586fb4b1eb48047a0323bb727426e59dcc95d9c7e",
    PREREG.name: "22daea5aaddf8d480d5748d3c1d1053ff6dd7bff2d4ab04af2b69750d73a5947",
    CONTRACT.name: "a8e1c75dc9719350e106f22abf8473d93a73405f4d992c6fde2d31509b3e9032",
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


def expected_assets(source_archive: Path) -> tuple[dict[str, Path], dict[str, str], Any, Any]:
    base = load(BASE, "epsilon_wall_base")
    job = base.load_job()
    sources = base.asset_sources(source_archive.resolve(), job)
    sources.update({HOSTED.name: HOSTED, WRAPPER.name: WRAPPER, ULP_JSON.name: ULP_JSON,
                    PREREG.name: PREREG, CONTRACT.name: CONTRACT})
    expected = {**job.EXPECTED_HASHES, **EXPECTED_EXTRA}
    if set(sources) != set(expected) or len(expected) != 24:
        raise RuntimeError("epsilon-aware upload set changed")
    return sources, expected, base, job


def stage_assets(destination: Path, source_archive: Path) -> dict[str, Any]:
    if destination.exists():
        raise FileExistsError(destination)
    sources, expected, _base, job = expected_assets(source_archive)
    for name, source in sources.items():
        if not source.is_file() or source.is_symlink() or sha256(source) != expected[name]:
            raise ValueError(f"invalid source asset: {source}")
    destination.mkdir(parents=True)
    for name, source in sources.items():
        shutil.copy2(source, destination / name)
    job.validate_assets(destination)
    return {"status": "PASS_EXACT_ASSET_STAGING", "asset_count": len(expected),
            "hashes": validate_assets(destination, expected)}


def validate_assets(destination: Path, expected: dict[str, str]) -> dict[str, str]:
    children = list(destination.iterdir()) if destination.is_dir() else []
    if len(children) != len(expected) or any(path.is_symlink() or not path.is_file() for path in children):
        raise ValueError("staged asset cardinality/type changed")
    actual = {path.name: sha256(path) for path in children}
    if actual != expected:
        raise ValueError("staged asset hashes changed")
    return actual


def command(command: list[str], timeout: float, check: bool = True) -> dict[str, Any]:
    started = time.monotonic()
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, timeout=timeout, check=False)
    result = {"command": command, "returncode": completed.returncode,
              "stdout": completed.stdout, "elapsed_seconds": time.monotonic() - started}
    if check and completed.returncode != 0:
        raise RuntimeError(json.dumps(result, sort_keys=True))
    return result


def remaining(started: float) -> float:
    return MAX_SESSION_SECONDS - (time.monotonic() - started)


def work_timeout(started: float, label: str) -> float:
    value = remaining(started) - STOP_RESERVE_SECONDS
    if value <= 0:
        raise TimeoutError(f"stop reserve reached before {label}")
    return value


def validate_status(value: str) -> None:
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    pattern = re.compile(rf"^\[{re.escape(SESSION)}\] [^|]+ \| Hardware: T4 \| Variant: GPU \| Status: IDLE$")
    if len(lines) != 1 or pattern.fullmatch(lines[0]) is None:
        raise ValueError("named session is not the exact idle T4")


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    if path.exists() or temporary.exists():
        raise FileExistsError(path)
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def build_plan(assets: Path, recovery: Path, colab: str, expected: dict[str, str]) -> dict[str, Any]:
    manifest = recovery / MANIFEST_NAME
    artifact = recovery / ARTIFACT_NAME
    record = recovery / "GROUND_UP_RESET_COM_ESTIMATOR_EPSILON_AWARE_launch.json"
    for path in (manifest, artifact, record):
        if path.exists() or path.with_suffix(path.suffix + ".tmp").exists():
            raise FileExistsError(path)
    uploads = [[colab, "upload", "--session", SESSION, str((assets / name).resolve()),
                str(REMOTE / name)] for name in sorted(expected)]
    return {
        "schema_version": "ground_up_reset_estimator_epsilon_aware_wall_plan.v1",
        "status": "PASS_DRY_RUN_PLAN", "session": SESSION, "accelerator": ACCELERATOR,
        "maximum_session_seconds": MAX_SESSION_SECONDS,
        "stop_reserve_seconds": STOP_RESERVE_SECONDS,
        "compute_units": COMPUTE_UNITS, "asset_hashes": expected,
        "commands": {
            "new": [colab, "new", "--session", SESSION, "--gpu", ACCELERATOR],
            "status": [colab, "status", "--session", SESSION],
            "uploads": uploads,
            "exec_prefix": [colab, "exec", "--session", SESSION, "--file", str(WRAPPER.resolve())],
            "downloads": [
                [colab, "download", "--session", SESSION, str(REMOTE / MANIFEST_NAME), str(manifest) + ".tmp"],
                [colab, "download", "--session", SESSION, str(REMOTE / ARTIFACT_NAME), str(artifact) + ".tmp"],
            ],
            "stop": [colab, "stop", "--session", SESSION],
        },
        "recovery": {"manifest": str(manifest), "artifact": str(artifact),
                     "launch_record": str(record)},
        "allocation_authorized": False,
    }


def launch(plan: dict[str, Any], colab: str, base: Any, job: Any) -> dict[str, Any]:
    started = time.monotonic()
    record: dict[str, Any] = {"schema_version": "ground_up_reset_estimator_epsilon_aware_wall_launch.v1",
                              "status": "RUNNING", "plan": plan, "commands": [],
                              "compute_units": COMPUTE_UNITS, "session_stop": None}
    created = False
    manifest = Path(plan["recovery"]["manifest"]); artifact = Path(plan["recovery"]["artifact"])
    manifest_tmp = manifest.with_suffix(manifest.suffix + ".tmp")
    artifact_tmp = artifact.with_suffix(artifact.suffix + ".tmp")
    try:
        created = True
        record["commands"].append(command(plan["commands"]["new"], min(120, work_timeout(started, "allocation"))))
        status = command(plan["commands"]["status"], min(60, work_timeout(started, "status")))
        record["commands"].append(status); validate_status(status["stdout"])
        for item in plan["commands"]["uploads"]:
            record["commands"].append(command(item, work_timeout(started, "upload")))
        timeout = work_timeout(started, "execution")
        executed = command([*plan["commands"]["exec_prefix"], "--timeout", f"{timeout:.3f}"], timeout)
        record["commands"].append(executed)
        remote = base.extract_remote_result(executed["stdout"]); record["remote_result"] = remote
        for item in plan["commands"]["downloads"]:
            record["commands"].append(command(item, work_timeout(started, "download")))
        record["download_verification"] = base.verify_downloads(manifest_tmp, artifact_tmp, remote, job)
        manifest_tmp.replace(manifest); artifact_tmp.replace(artifact)
        record["status"] = "PASS_HOSTED_ARTIFACTS_RECOVERED"
    except Exception as error:
        record["status"] = "FAIL_HOSTED_LAUNCH_OR_RECOVERY"; record["error"] = repr(error)
        raise
    finally:
        if created:
            try:
                record["session_stop"] = command(plan["commands"]["stop"], max(1, min(120, remaining(started))), check=False)
            except Exception as error:
                record["session_stop"] = {"returncode": None, "error": repr(error)}
        record["session_elapsed_seconds"] = time.monotonic() - started
        record["session_stop_passed"] = isinstance(record["session_stop"], dict) and record["session_stop"].get("returncode") == 0
        record["session_wall_within_ceiling"] = record["session_elapsed_seconds"] <= MAX_SESSION_SECONDS
        if record["status"] == "PASS_HOSTED_ARTIFACTS_RECOVERED" and not (
            record["session_stop_passed"] and record["session_wall_within_ceiling"]
        ):
            record["status"] = "FAIL_HOSTED_CLEANUP_OR_SESSION_CEILING"
        write_json_atomic(Path(plan["recovery"]["launch_record"]), record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--recovery-dir", type=Path, required=True)
    parser.add_argument("--source-archive", type=Path, required=True)
    parser.add_argument("--stage-assets", action="store_true")
    parser.add_argument("--plan-output", type=Path, required=True)
    parser.add_argument("--allow-colab-allocation", action="store_true")
    parser.add_argument("--colab-bin", default="colab")
    args = parser.parse_args()
    sources, expected, base, job = expected_assets(args.source_archive.resolve())
    del sources
    assets = args.assets.resolve(); recovery = args.recovery_dir.resolve()
    staging = stage_assets(assets, args.source_archive.resolve()) if args.stage_assets else None
    validate_assets(assets, expected); recovery.mkdir(parents=True, exist_ok=True)
    version = base.cli_version(args.colab_bin)
    plan = build_plan(assets, recovery, args.colab_bin, expected)
    plan["cli_version"] = version; plan["asset_staging"] = staging
    plan["allocation_authorized"] = bool(args.allow_colab_allocation)
    write_json_atomic(args.plan_output.resolve(), plan)
    if not args.allow_colab_allocation:
        print(json.dumps({"status": "PASS_DRY_RUN_NO_ALLOCATION", "session_created": False,
                          "plan": str(args.plan_output.resolve())}, sort_keys=True))
        return 0
    record = launch(plan, args.colab_bin, base, job)
    print(json.dumps({"status": record["status"], **plan["recovery"]}, sort_keys=True))
    return 0 if record["status"] == "PASS_HOSTED_ARTIFACTS_RECOVERED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
