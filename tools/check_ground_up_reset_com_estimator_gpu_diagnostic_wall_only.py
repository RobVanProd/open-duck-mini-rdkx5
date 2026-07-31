#!/usr/bin/env python3
"""Contract the wall-only GPU expansion diagnostic without allocation."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
from typing import Any

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")
REPO = Path(__file__).resolve().parents[1]
LAUNCHER = REPO / "tools/launch_ground_up_reset_com_estimator_gpu_expansion_diagnostic.py"
WRAPPER = REPO / "tools/colab_ground_up_reset_com_estimator_gpu_expansion_diagnostic.py"
HOSTED = REPO / "tools/colab_ground_up_reset_com_estimator_training.py"
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_GPU_DIAGNOSTIC_WALL_ONLY_CORRECTION_PREREGISTRATION_20260715.md"
TIMEOUT_RESULT = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_RESET_ESTIMATOR_GPU_DIAGNOSTIC_RATE_TIMEOUT_RESULT_20260715.md"
PRIOR_CONTRACT = REPO / "outputs/analysis/ground_up_reset_com_estimator_gpu_expansion_diagnostic_package_contract.json"
EXPECTED = {
    "launcher": "62def0fc04a37283140ad9be1439b0825855d6f5b98a29e3b13f0cc37ca7049d",
    "wrapper": "68a6f8c3001bfdce74346a02533ca76e9e122d0a5ea325c827625e6293fe14e4",
    "hosted": "a3e5fc38994cecd65d89fdc6b9ede23c2433e917b84583dfcced42c161e79d67",
    "prereg": "633cba20bb3a3c5494b0f766d6a54955f599473594af70d8a3292c40709940e6",
    "timeout_result": "9e3e4b6b40b51508849925e684286c9af3872d12bad437e275a1c0d5a1b12bbf",
    "prior_contract": "231458e681c36b717c34ce653cd73b4b94da32d5c491242a499dc75bf7765e27",
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


def fixture(error: float) -> dict[str, Any]:
    checks = {name: True for name in (
        "source_shapes_exact", "source_count_exact", "expanded_shapes_exact",
        "inserted_normalizer_exact", "inserted_rows_zero", "all_other_values_bit_exact",
        "save_restore_bit_exact", "reference_tail_exact", "all_values_finite")}
    checks["step_zero_outputs_exact"] = error <= 1e-7
    return {"status": "PASS_HOSTED_CHECKPOINT_EXPANSION" if error <= 1e-7 else "FAIL_HOSTED_CHECKPOINT_EXPANSION",
            "checks": checks, "failed_checks": [] if error <= 1e-7 else ["step_zero_outputs_exact"],
            "source_directory_sha256": "b37a86f1b736d0d1276e60fb69d1f473683c593dec26f9592b0b794858dbb44a",
            "expanded_directory_sha256": "fixture", "devices": ["CudaDevice(id=0)"],
            "output_equivalence": [{"z": z, "actor_max_abs_error": error,
                                    "critic_max_abs_error": error,
                                    "reference_tail_exact": True}
                                   for z in (-1.0, 0.0, 1.0)]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {"launcher": LAUNCHER, "wrapper": WRAPPER, "hosted": HOSTED,
             "prereg": PREREG, "timeout_result": TIMEOUT_RESULT,
             "prior_contract": PRIOR_CONTRACT}
    hashes = {k: sha256(v) for k, v in paths.items()}
    launcher, wrapper = load(LAUNCHER, "wall_launcher"), load(WRAPPER, "wall_wrapper")
    prior = json.loads(PRIOR_CONTRACT.read_text())
    before = sessions()
    with tempfile.TemporaryDirectory(prefix="wall_only_gpu_diag_contract_") as temp:
        root = Path(temp)
        assets, recovery, plan_path = root / "assets", root / "recovery", root / "plan.json"
        completed = subprocess.run(
            ["python3", str(LAUNCHER), "--assets", str(assets),
             "--recovery-dir", str(recovery), "--source-archive", str(args.source_archive.resolve()),
             "--stage-assets", "--plan-output", str(plan_path)],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=120, check=True,
        )
        dry = json.loads(completed.stdout.strip().splitlines()[-1])
        plan = json.loads(plan_path.read_text())
        staged = {p.name: sha256(p) for p in assets.iterdir()}
        wrapper_checks = {}
        for name, error, raises in (("pass", 0.0, False), ("fail", 2e-7, True)):
            value, state = fixture(error), {"training": False}
            module = SimpleNamespace()
            report_path = root / f"{name}_source.json"
            def expand(source: Path, destination: Path, path: Path, value=value, raises=raises):
                path.write_text(json.dumps(value))
                if raises:
                    raise RuntimeError("fixture failure")
                return value
            def module_main(module=module, state=state, report_path=report_path):
                module.hosted_expand(Path("s"), Path("d"), report_path)
                state["training"] = True
            module.hosted_expand, module.main = expand, module_main
            wrapper.FIXED_REPORT = root / f"{name}_fixed.json"
            result = wrapper.run_diagnostic(module)
            wrapper_checks[name] = result == 0 and not state["training"] and json.loads(wrapper.FIXED_REPORT.read_text()) == value
    after = sessions()
    source = LAUNCHER.read_text()
    launch_source = source[source.index("def launch(") : source.index("def main()")]
    checks = {
        "source_hashes_exact": hashes == EXPECTED,
        "prior_contract_passes": prior["status"] == "PASS_RESET_COM_ESTIMATOR_GPU_EXPANSION_DIAGNOSTIC_PACKAGE_CONTRACT",
        "rate_surface_absent": all(fragment not in source for fragment in (
            "--attestation-file", "validate_attestation", "wait_attestation",
            "compute_rate_per_hour", "MAX_COMPUTE_UNITS")),
        "compute_unmeasured_exact": plan["compute_units"] == "UNMEASURED" and "maximum_compute_units" not in plan,
        "limits_exact": plan["maximum_session_seconds"] == 300.0 and plan["stop_reserve_seconds"] == 60.0,
        "fresh_session_exact": plan["session"] == "open-duck-reset-estimator-expansion-diag2-t4"
        and plan["accelerator"] == "T4",
        "status_precedes_upload": launch_source.index("validate_status") < launch_source.index("for command in plan"),
        "uploads_exact": len(staged) == 21 and len(plan["uploads"]) == 21
        and staged[HOSTED.name] == EXPECTED["hosted"] and staged[WRAPPER.name] == EXPECTED["wrapper"],
        "wrapper_stops_before_training": all(wrapper_checks.values()),
        "classifications_unchanged": launcher.classify(fixture(0.0))["outcome"] == "GPU_EQUIVALENCE_PASSES_ORIGINAL_1E7_NOT_REPRODUCED"
        and launcher.classify(fixture(2e-7))["outcome"] == "FINITE_GPU_EQUIVALENCE_EXCEEDS_ORIGINAL_1E7",
        "atomic_recovery": "report_tmp.replace(report_final)" in source,
        "cleanup_and_wall": "finally:" in source and "session_wall_within_ceiling" in source
        and 'plan["commands"]["stop"]' in source,
        "no_retry_resume": all(fragment not in source for fragment in ("--retry", "--resume", "--adopt")),
        "dry_run_no_allocation": dry["status"] == "PASS_DRY_RUN_NO_ALLOCATION"
        and dry["session_created"] is False and plan["allocation_authorized"] is False,
        "session_inventory_unchanged": before == after,
        "zero_remote_training": before == after,
    }
    failed = sorted(k for k, v in checks.items() if not v)
    status = "PASS_RESET_COM_ESTIMATOR_GPU_DIAGNOSTIC_WALL_ONLY_CONTRACT" if not failed else "FAIL_RESET_COM_ESTIMATOR_GPU_DIAGNOSTIC_WALL_ONLY_CONTRACT"
    result = {"schema_version": "ground_up_reset_estimator_gpu_diagnostic_wall_only_contract.v1",
              "status": status, "checks": checks, "failed_checks": failed,
              "source_hashes": hashes, "dry_run": {"result": dry, "plan": plan},
              "staged_assets": staged, "wrapper_fixtures": wrapper_checks,
              "session_inventory": {"before": before, "after": after},
              "execution": {"sessions_created": 0, "remote_bytes": 0,
                            "training_processes": 0, "training_steps": 0,
                            "compute_units": "UNMEASURED", "robot_or_rdk": False},
              "authority": {"wall_only_diagnostic_authorized": True,
                            "additional_billing_input_required": False,
                            "training": False, "behavior_evaluation": False}}
    args.output.resolve().write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
