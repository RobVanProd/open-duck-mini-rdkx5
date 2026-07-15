#!/usr/bin/env python3
"""Stage, dry-run, or explicitly launch the frozen T4 expansion diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Any


REPO = Path(__file__).resolve().parents[1]
BASE_LAUNCHER = REPO / "tools/launch_ground_up_reset_com_estimator_colab.py"
HOSTED_SOURCE = REPO / "tools/colab_ground_up_reset_com_estimator_training.py"
WRAPPER = REPO / "tools/colab_ground_up_reset_com_estimator_gpu_expansion_diagnostic.py"
SESSION = "open-duck-reset-estimator-expansion-diag2-t4"
ACCELERATOR = "T4"
MAX_SESSION_SECONDS = 300.0
STOP_RESERVE_SECONDS = 60.0
REMOTE_REPORT = Path("/content/GROUND_UP_RESET_COM_ESTIMATOR_GPU_EXPANSION_DIAGNOSTIC.json")
RESULT_PREFIX = "GROUND_UP_RESET_ESTIMATOR_GPU_EXPANSION_DIAGNOSTIC_RESULT="
EXPECTED_HOSTED_SHA256 = "a3e5fc38994cecd65d89fdc6b9ede23c2433e917b84583dfcced42c161e79d67"
EXPECTED_WRAPPER_SHA256 = "68a6f8c3001bfdce74346a02533ca76e9e122d0a5ea325c827625e6293fe14e4"
EXPECTED_SOURCE_DIRECTORY_SHA256 = "b37a86f1b736d0d1276e60fb69d1f473683c593dec26f9592b0b794858dbb44a"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location("reset_estimator_base_launcher", BASE_LAUNCHER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load base launcher")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def command_result(command: list[str], *, timeout: float, check: bool = True) -> dict[str, Any]:
    started = time.monotonic()
    completed = subprocess.run(
        command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        timeout=timeout, check=False,
    )
    result = {"command": command, "returncode": completed.returncode,
              "stdout": completed.stdout, "elapsed_seconds": time.monotonic() - started}
    if check and completed.returncode != 0:
        raise RuntimeError(json.dumps(result, sort_keys=True))
    return result


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    if path.exists() or temporary.exists():
        raise FileExistsError(path)
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def stage_assets(destination: Path, source_archive: Path) -> dict[str, str]:
    if destination.exists():
        raise FileExistsError(destination)
    base = load_base()
    job = base.load_job()
    sources = base.asset_sources(source_archive, job)
    sources[HOSTED_SOURCE.name] = HOSTED_SOURCE
    sources[WRAPPER.name] = WRAPPER
    expected = {**job.EXPECTED_HASHES,
                HOSTED_SOURCE.name: EXPECTED_HOSTED_SHA256,
                WRAPPER.name: EXPECTED_WRAPPER_SHA256}
    if set(sources) != set(expected):
        raise RuntimeError("diagnostic upload set changed")
    destination.mkdir(parents=True)
    for name, source in sources.items():
        if not source.is_file() or source.is_symlink() or sha256(source) != expected[name]:
            raise ValueError(f"diagnostic source invalid: {source}")
        shutil.copy2(source, destination / name)
    return validate_assets(destination)


def validate_assets(destination: Path) -> dict[str, str]:
    base = load_base()
    expected = {**base.load_job().EXPECTED_HASHES,
                HOSTED_SOURCE.name: EXPECTED_HOSTED_SHA256,
                WRAPPER.name: EXPECTED_WRAPPER_SHA256}
    children = list(destination.iterdir()) if destination.is_dir() else []
    if len(children) != 21 or any(p.is_symlink() or not p.is_file() for p in children):
        raise ValueError("diagnostic staged asset cardinality/type changed")
    actual = {p.name: sha256(p) for p in children}
    if actual != expected:
        raise ValueError("diagnostic staged hashes changed")
    return actual


def remaining(started: float) -> float:
    return MAX_SESSION_SECONDS - (time.monotonic() - started)


def work_timeout(started: float, label: str) -> float:
    value = remaining(started) - STOP_RESERVE_SECONDS
    if value <= 0:
        raise TimeoutError(f"stop reserve reached before {label}")
    return value


def validate_status(text: str) -> None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    pattern = re.compile(
        rf"^\[{re.escape(SESSION)}\] [^|]+ \| Hardware: T4 \| Variant: GPU \| Status: IDLE$"
    )
    if len(lines) != 1 or pattern.fullmatch(lines[0]) is None:
        raise ValueError("diagnostic session is not the exact idle T4")


def build_plan(assets: Path, recovery: Path, colab: str) -> dict[str, Any]:
    report = recovery / REMOTE_REPORT.name
    record = recovery / "GROUND_UP_RESET_COM_ESTIMATOR_GPU_EXPANSION_DIAGNOSTIC_launch.json"
    for path in (report, record):
        if path.exists() or path.with_suffix(path.suffix + ".tmp").exists():
            raise FileExistsError(path)
    uploads = [[colab, "upload", "--session", SESSION, str((assets / name).resolve()),
                str(Path("/content") / name)] for name in sorted(validate_assets(assets))]
    return {
        "schema_version": "ground_up_reset_estimator_gpu_expansion_diagnostic_plan.v1",
        "status": "PASS_DRY_RUN_PLAN", "session": SESSION, "accelerator": ACCELERATOR,
        "maximum_session_seconds": MAX_SESSION_SECONDS,
        "stop_reserve_seconds": STOP_RESERVE_SECONDS,
        "compute_units": "UNMEASURED",
        "uploads": uploads,
        "commands": {
            "new": [colab, "new", "--session", SESSION, "--gpu", ACCELERATOR],
            "status": [colab, "status", "--session", SESSION],
            "uploads": uploads,
            "exec_prefix": [colab, "exec", "--session", SESSION, "--file", str(WRAPPER.resolve())],
            "download": [colab, "download", "--session", SESSION, str(REMOTE_REPORT), str(report) + ".tmp"],
            "stop": [colab, "stop", "--session", SESSION],
        },
        "recovery": {"report": str(report), "launch_record": str(record)},
        "allocation_authorized": False,
    }


def parse_marker(text: str) -> dict[str, Any]:
    values = [json.loads(line[len(RESULT_PREFIX):]) for line in text.splitlines()
              if line.startswith(RESULT_PREFIX)]
    if len(values) != 1 or values[0].get("status") != "PASS_DIAGNOSTIC_REPORT_CAPTURED":
        raise RuntimeError(f"expected one diagnostic marker, found {len(values)}")
    return values[0]


def classify(report: dict[str, Any]) -> dict[str, Any]:
    cells = report.get("output_equivalence", [])
    other_checks = {k: v for k, v in report.get("checks", {}).items()
                    if k != "step_zero_outputs_exact"}
    errors = [cell.get(key) for cell in cells
              for key in ("actor_max_abs_error", "critic_max_abs_error")]
    valid = (
        report.get("source_directory_sha256") == EXPECTED_SOURCE_DIRECTORY_SHA256
        and len(cells) == 3 and [cell.get("z") for cell in cells] == [-1.0, 0.0, 1.0]
        and len(errors) == 6 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in errors)
        and other_checks and all(other_checks.values())
        and any("CudaDevice" in value for value in report.get("devices", []))
    )
    maximum = max(errors) if errors and all(isinstance(v, (int, float)) for v in errors) else None
    if not valid:
        outcome = "INVALID_OR_STRUCTURAL_GPU_EXPANSION"
    elif maximum <= 1e-7:
        outcome = "GPU_EQUIVALENCE_PASSES_ORIGINAL_1E7_NOT_REPRODUCED"
    else:
        outcome = "FINITE_GPU_EQUIVALENCE_EXCEEDS_ORIGINAL_1E7"
    return {"valid": valid, "outcome": outcome, "maximum_output_error": maximum,
            "other_checks": other_checks}


def launch(plan: dict[str, Any], colab: str) -> dict[str, Any]:
    started = time.monotonic()
    record: dict[str, Any] = {"schema_version": "ground_up_reset_estimator_gpu_expansion_diagnostic_launch.v1",
                              "status": "RUNNING", "plan": plan, "commands": [], "session_stop": None}
    created = False
    report_final = Path(plan["recovery"]["report"])
    report_tmp = report_final.with_suffix(report_final.suffix + ".tmp")
    try:
        created = True
        record["commands"].append(command_result(plan["commands"]["new"], timeout=min(90, work_timeout(started, "allocation"))))
        status = command_result(plan["commands"]["status"], timeout=min(30, work_timeout(started, "status")))
        record["commands"].append(status)
        validate_status(status["stdout"])
        record["compute_units"] = "UNMEASURED"
        for command in plan["commands"]["uploads"]:
            record["commands"].append(command_result(command, timeout=work_timeout(started, "upload")))
        exec_command = [*plan["commands"]["exec_prefix"], "--timeout", f"{work_timeout(started, 'diagnostic exec'):.3f}"]
        executed = command_result(exec_command, timeout=work_timeout(started, "diagnostic exec"))
        record["commands"].append(executed)
        marker = parse_marker(executed["stdout"])
        record["marker"] = marker
        record["commands"].append(command_result(plan["commands"]["download"], timeout=work_timeout(started, "report download")))
        if sha256(report_tmp) != marker["report"]["sha256"] or report_tmp.stat().st_size != marker["report"]["bytes"]:
            raise ValueError("diagnostic report recovery mismatch")
        report = json.loads(report_tmp.read_text())
        record["classification"] = classify(report)
        report_tmp.replace(report_final)
        record["status"] = "PASS_GPU_EXPANSION_DIAGNOSTIC_RECOVERED"
    except Exception as error:
        record["status"] = "FAIL_GPU_EXPANSION_DIAGNOSTIC_LAUNCH_OR_RECOVERY"
        record["error"] = repr(error)
        raise
    finally:
        if created:
            try:
                record["session_stop"] = command_result(plan["commands"]["stop"], timeout=max(1, min(60, remaining(started))), check=False)
            except Exception as error:
                record["session_stop"] = {"returncode": None, "error": repr(error)}
        record["session_elapsed_seconds"] = time.monotonic() - started
        record["session_stop_passed"] = isinstance(record["session_stop"], dict) and record["session_stop"].get("returncode") == 0
        record["session_wall_within_ceiling"] = record["session_elapsed_seconds"] <= MAX_SESSION_SECONDS
        if record["status"] == "PASS_GPU_EXPANSION_DIAGNOSTIC_RECOVERED" and (
            not record["session_stop_passed"] or not record["session_wall_within_ceiling"]
        ):
            record["status"] = "FAIL_GPU_EXPANSION_DIAGNOSTIC_CLEANUP_OR_WALL"
        write_json_atomic(Path(plan["recovery"]["launch_record"]), record)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--recovery-dir", type=Path, required=True)
    parser.add_argument("--source-archive", type=Path)
    parser.add_argument("--stage-assets", action="store_true")
    parser.add_argument("--plan-output", type=Path, required=True)
    parser.add_argument("--allow-colab-allocation", action="store_true")
    parser.add_argument("--colab-bin", default="colab")
    args = parser.parse_args()
    if sha256(HOSTED_SOURCE) != EXPECTED_HOSTED_SHA256 or sha256(WRAPPER) != EXPECTED_WRAPPER_SHA256:
        raise RuntimeError("diagnostic sources changed")
    assets, recovery = args.assets.resolve(), args.recovery_dir.resolve()
    if args.stage_assets:
        if args.source_archive is None:
            raise ValueError("--stage-assets requires --source-archive")
        stage_assets(assets, args.source_archive.resolve())
    validate_assets(assets)
    recovery.mkdir(parents=True, exist_ok=True)
    plan = build_plan(assets, recovery, args.colab_bin)
    plan["allocation_authorized"] = bool(args.allow_colab_allocation)
    write_json_atomic(args.plan_output.resolve(), plan)
    if not args.allow_colab_allocation:
        print(json.dumps({"status": "PASS_DRY_RUN_NO_ALLOCATION", "session_created": False,
                          "plan": str(args.plan_output.resolve())}, sort_keys=True))
        return 0
    record = launch(plan, args.colab_bin)
    print(json.dumps({"status": record["status"], "classification": record.get("classification"),
                      "report": plan["recovery"]["report"],
                      "launch_record": plan["recovery"]["launch_record"]}, sort_keys=True))
    return 0 if record["status"] == "PASS_GPU_EXPANSION_DIAGNOSTIC_RECOVERED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
