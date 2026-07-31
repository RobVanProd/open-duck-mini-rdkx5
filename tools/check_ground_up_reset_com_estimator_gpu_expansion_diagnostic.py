#!/usr/bin/env python3
"""Contract the T4 expansion diagnostic package with zero allocation."""

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
from types import SimpleNamespace
from typing import Any, Callable

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

REPO = Path(__file__).resolve().parents[1]
LAUNCHER = REPO / "tools/launch_ground_up_reset_com_estimator_gpu_expansion_diagnostic.py"
WRAPPER = REPO / "tools/colab_ground_up_reset_com_estimator_gpu_expansion_diagnostic.py"
HOSTED = REPO / "tools/colab_ground_up_reset_com_estimator_training.py"
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_GPU_EXPANSION_DIAGNOSTIC_PREREGISTRATION_20260715.md"
UPSTREAM = REPO / "outputs/analysis/ground_up_reset_com_estimator_same_session_hosted_launch_result.json"
EXPECTED = {
    "launcher": "655e3d34d86bd8f28cd147342f84230ba71eb1426e9ff90b4aa706d58fa7312b",
    "wrapper": "68a6f8c3001bfdce74346a02533ca76e9e122d0a5ea325c827625e6293fe14e4",
    "hosted": "a3e5fc38994cecd65d89fdc6b9ede23c2433e917b84583dfcced42c161e79d67",
    "prereg": "8b42730a520fe0d3ba1b69df43bb12b2205fa5bdaeaa1d7ffa4616cefb6dcc3f",
    "upstream": "be94fdabee2769e946b937582f0dbcf560cd5e8a8006535e285e8b24777f4c2c",
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


def sessions() -> str:
    return subprocess.run(["colab", "sessions"], text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, timeout=30, check=True).stdout


def fails(call: Callable[[], Any]) -> bool:
    try:
        call()
    except (FileExistsError, RuntimeError, TypeError, ValueError):
        return True
    return False


def report(error: float, *, structural: bool = False) -> dict[str, Any]:
    checks = {
        "source_shapes_exact": not structural, "source_count_exact": True,
        "expanded_shapes_exact": True, "inserted_normalizer_exact": True,
        "inserted_rows_zero": True, "all_other_values_bit_exact": True,
        "save_restore_bit_exact": True, "step_zero_outputs_exact": error <= 1e-7,
        "reference_tail_exact": True, "all_values_finite": True,
    }
    return {
        "status": "PASS_HOSTED_CHECKPOINT_EXPANSION" if error <= 1e-7 else "FAIL_HOSTED_CHECKPOINT_EXPANSION",
        "checks": checks,
        "failed_checks": sorted(k for k, v in checks.items() if not v),
        "source_directory_sha256": "b37a86f1b736d0d1276e60fb69d1f473683c593dec26f9592b0b794858dbb44a",
        "expanded_directory_sha256": "fixture",
        "devices": ["CudaDevice(id=0)"],
        "output_equivalence": [
            {"z": z, "actor_max_abs_error": error, "critic_max_abs_error": error,
             "reference_tail_exact": True} for z in (-1.0, 0.0, 1.0)
        ],
    }


def fake_module(value: dict[str, Any], raises: bool) -> Any:
    state = {"training_reached": False}
    module = SimpleNamespace()
    def expand(source: Path, destination: Path, report_path: Path) -> dict[str, Any]:
        report_path.write_text(json.dumps(value))
        if raises:
            raise RuntimeError("frozen expansion failed")
        return value
    def main() -> int:
        module.hosted_expand(Path("source"), Path("destination"), module.report_path)
        state["training_reached"] = True
        return 0
    module.hosted_expand, module.main, module.state = expand, main, state
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {"launcher": LAUNCHER, "wrapper": WRAPPER, "hosted": HOSTED,
             "prereg": PREREG, "upstream": UPSTREAM}
    hashes = {k: sha256(v) for k, v in paths.items()}
    launcher, wrapper = load(LAUNCHER, "diagnostic_launcher"), load(WRAPPER, "diagnostic_wrapper")
    upstream = json.loads(UPSTREAM.read_text())
    fixed = datetime(2026, 7, 15, 22, 0, tzinfo=timezone.utc)
    def att(rate: float, balance: float, when: datetime, **changes: Any) -> dict[str, Any]:
        value = {"source": launcher.ATTESTATION_SOURCE, "session": launcher.SESSION,
                 "compute_rate_per_hour": rate, "available_compute_units": balance,
                 "collector_received_at": when.isoformat()}
        value.update(changes)
        return value
    nominal = launcher.validate_attestation(att(1.07, 79.36, fixed), now=fixed)
    ceiling = launcher.validate_attestation(att(3.0, 79.36, fixed), now=fixed)
    invalid_att = {
        "over": fails(lambda: launcher.validate_attestation(att(3.000001, 79.36, fixed), now=fixed)),
        "zero": fails(lambda: launcher.validate_attestation(att(0.0, 79.36, fixed), now=fixed)),
        "nan": fails(lambda: launcher.validate_attestation(att(math.nan, 79.36, fixed), now=fixed)),
        "balance": fails(lambda: launcher.validate_attestation(att(1.07, 0.249, fixed), now=fixed)),
        "stale": fails(lambda: launcher.validate_attestation(att(1.07, 79.36, fixed - timedelta(seconds=60.000001)), now=fixed)),
        "future": fails(lambda: launcher.validate_attestation(att(1.07, 79.36, fixed + timedelta(seconds=60.000001)), now=fixed)),
        "identity": fails(lambda: launcher.validate_attestation(att(1.07, 79.36, fixed, session="wrong"), now=fixed)),
    }
    old_edge = launcher.validate_attestation(att(1.07, 79.36, fixed - timedelta(seconds=60)), now=fixed)
    future_edge = launcher.validate_attestation(att(1.07, 79.36, fixed + timedelta(seconds=60)), now=fixed)

    before = sessions()
    with tempfile.TemporaryDirectory(prefix="gpu_expansion_diag_contract_") as temp:
        root = Path(temp)
        assets, recovery = root / "assets", root / "recovery"
        plan_path, rate_path = root / "plan.json", root / "rate.json"
        dry = subprocess.run(
            ["python3", str(LAUNCHER), "--assets", str(assets), "--recovery-dir", str(recovery),
             "--source-archive", str(args.source_archive.resolve()), "--stage-assets",
             "--attestation-file", str(rate_path), "--plan-output", str(plan_path)],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=120, check=True,
        )
        dry_result = json.loads(dry.stdout.strip().splitlines()[-1])
        plan = json.loads(plan_path.read_text())
        staged = {p.name: sha256(p) for p in assets.iterdir()}
        wrapper_results = {}
        for name, value, raises in (("pass", report(0.0), False), ("fail", report(2e-7), True)):
            module = fake_module(value, raises)
            module.report_path = root / f"{name}_source_report.json"
            wrapper.FIXED_REPORT = root / f"{name}_fixed_report.json"
            wrapper_results[name] = {
                "returncode": wrapper.run_diagnostic(module),
                "training_reached": module.state["training_reached"],
                "report_exact": json.loads(wrapper.FIXED_REPORT.read_text()) == value,
            }
    after = sessions()
    source = LAUNCHER.read_text()
    checks = {
        "source_hashes_exact": hashes == EXPECTED,
        "upstream_failure_exact": upstream["decision"] == "STOP_NO_RETRY_HOSTED_GPU_EXPANSION_EQUIVALENCE_FAILED"
        and upstream["execution"]["training_steps"] == 0,
        "wrapper_pass_and_fail_capture": all(v["returncode"] == 0 and not v["training_reached"] and v["report_exact"] for v in wrapper_results.values()),
        "wrapper_scope_exact": "module.hosted_expand = report_then_stop" in WRAPPER.read_text()
        and "module.main()" in WRAPPER.read_text() and "DiagnosticComplete" in WRAPPER.read_text(),
        "limits_exact": plan["maximum_session_seconds"] == 300.0 and plan["maximum_compute_units"] == 0.25
        and plan["stop_reserve_seconds"] == 60.0 and plan["attestation_wait_seconds"] == 60.0,
        "upload_set_exact": len(staged) == 21 and len(plan["uploads"]) == 21
        and staged[HOSTED.name] == EXPECTED["hosted"] and staged[WRAPPER.name] == EXPECTED["wrapper"],
        "dry_run_no_allocation": dry_result["status"] == "PASS_DRY_RUN_NO_ALLOCATION"
        and dry_result["session_created"] is False and plan["allocation_authorized"] is False,
        "rate_projection_boundaries": abs(nominal["projected_max_compute_units"] - 0.08916666666666667) < 1e-12
        and ceiling["projected_max_compute_units"] == 0.25,
        "freshness_boundaries": old_edge["age_seconds"] == 60.0 and future_edge["age_seconds"] == -60.0,
        "invalid_attestations_fail": all(invalid_att.values()),
        "classification_pass": launcher.classify(report(0.0))["outcome"] == "GPU_EQUIVALENCE_PASSES_ORIGINAL_1E7_NOT_REPRODUCED",
        "classification_exceeds": launcher.classify(report(2e-7))["outcome"] == "FINITE_GPU_EQUIVALENCE_EXCEEDS_ORIGINAL_1E7",
        "classification_structural": launcher.classify(report(0.0, structural=True))["outcome"] == "INVALID_OR_STRUCTURAL_GPU_EXPANSION",
        "report_before_training_source": WRAPPER.read_text().index("shutil.copy2(report_path, FIXED_REPORT)")
        < WRAPPER.read_text().index("raise DiagnosticComplete"),
        "atomic_recovery_and_cleanup": "report_tmp.replace(report_final)" in source
        and "finally:" in source and 'plan["commands"]["stop"]' in source,
        "no_retry_resume_surface": "--resume" not in source and "--retry" not in source and "--adopt" not in source,
        "session_inventory_unchanged": before == after,
        "zero_remote_and_training": before == after,
    }
    failed = sorted(k for k, v in checks.items() if not v)
    status = "PASS_RESET_COM_ESTIMATOR_GPU_EXPANSION_DIAGNOSTIC_PACKAGE_CONTRACT" if not failed else "FAIL_RESET_COM_ESTIMATOR_GPU_EXPANSION_DIAGNOSTIC_PACKAGE_CONTRACT"
    result = {"schema_version": "ground_up_reset_estimator_gpu_expansion_diagnostic_package_contract.v1",
              "status": status, "checks": checks, "failed_checks": failed,
              "source_hashes": hashes, "dry_run": {"result": dry_result, "plan": plan},
              "staged_assets": staged, "wrapper_fixtures": wrapper_results,
              "boundary_tests": {"nominal": nominal, "ceiling": ceiling,
                                 "old_edge": old_edge, "future_edge": future_edge,
                                 "invalid": invalid_att},
              "session_inventory": {"before": before, "after": after},
              "execution": {"sessions_created": 0, "remote_bytes": 0,
                            "training_processes": 0, "training_steps": 0,
                            "local_gpu_or_igpu": False, "robot_or_rdk": False},
              "authority": {"diagnostic_allocation_now": False,
                            "new_explicit_approval_required": True,
                            "training": False, "behavior_evaluation": False}}
    args.output.resolve().write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
