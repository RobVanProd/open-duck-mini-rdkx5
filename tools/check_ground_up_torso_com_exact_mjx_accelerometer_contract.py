#!/usr/bin/env python3
"""Check the zero-COM-outcome eager-MJX accelerometer replay contract."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("JAX_PLATFORMS", "cpu")

REPO = Path(__file__).resolve().parents[1]
PREREG = REPO / "outputs/analysis/GROUND_UP_TORSO_COM_EAGER_MJX_ACCELEROMETER_REPLAY_PREREGISTRATION_20260715.md"
PRIOR_MANIFEST = REPO / "outputs/analysis/ground_up_torso_com_full_obs_replay_manifest.json"
INVALID_RESULT = REPO / "outputs/analysis/ground_up_torso_com_exact_mjx_accelerometer_map_result.json"
JIT_RESULT = REPO / "outputs/analysis/ground_up_torso_com_mjx_jit_boundary_audit_result.json"
CLOSED_LOOP = REPO / "tools/closed_loop_sim_eval.py"
EVALUATOR = REPO / "tools/evaluate_ground_up_policy.py"
STUDY_TOOL = REPO / "tools/run_ground_up_torso_com_exact_mjx_accelerometer_replay.py"
SOURCE_MATRIX = REPO / "outputs/analysis/ground_up_torso_com_behavior_eval/NOMINAL_A05_DIRECT_1003520_p30.json"

EXPECTED = {
    "prereg": "82cb64126f717ff0e1ca244360eafeab2347cc83ba9da1f0d868dcd7128cd65a",
    "prior_manifest": "ac42abc8a940d97f0c0373ce624eaf2d2f803ac574e0de52c82303c7a759da07",
    "invalid_result": "23b4ad8444fc4eaa9dd83dcffb64b3b070431f3b424a83d71bf9a5b2a5ffcf3b",
    "jit_result": "11a50e76e84e0e0ae67d33dd12d587864ba9a557db27355d97743eab0f717575",
    "closed_loop_pre": "d2c452b19826e4ff9e399bf61fe09e654514c4fc194966871e35fba0850f20d7",
    "evaluator_pre": "347d3e4151d3f634710660b8c11bcce13724c66d33caafb5edbf86ebe2638030",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_study() -> Any:
    spec = importlib.util.spec_from_file_location("exact_mjx_study", STUDY_TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load exact MJX study tool")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def default_off_regression(study: Any) -> dict[str, Any]:
    source = json.loads(SOURCE_MATRIX.read_text())
    manifest = json.loads(PRIOR_MANIFEST.read_text())
    prior = next(
        row for row in manifest["traces"]
        if row["condition"] == "NOMINAL" and row["arm"] == "A05_DIRECT"
        and int(row["step"]) == 1003520 and row["fit"] == "p30"
        and round(float(row["command_x"]), 3) == 0.074
    )
    prior_path = Path(prior["path"])
    if sha256(prior_path) != prior["sha256"]:
        raise ValueError("default-off prior trace hash mismatch")
    with tempfile.TemporaryDirectory(prefix="exact_mjx_default_off_") as temporary:
        root = Path(temporary)
        trace_dir = root / "traces"
        trace_dir.mkdir()
        output = root / "matrix.json"
        command = study.command_for(source, output, trace_dir)
        map_index = command.index("--trace-com-accelerometer-map-ticks")
        del command[map_index : map_index + 2]
        command_index = command.index("--commands")
        command[command_index + 1] = "0.074"
        environment = dict(os.environ)
        environment.update({"CUDA_VISIBLE_DEVICES": "", "JAX_PLATFORMS": "cpu"})
        subprocess.run(command, cwd=REPO, env=environment, check=True)
        payload = json.loads(output.read_text())
        if len(payload.get("runs") or []) != 1:
            raise ValueError("default-off regression run count mismatch")
        generated_path = Path(payload["runs"][0]["trace_jsonl"])
        generated_rows = study.load_rows(generated_path)
        prior_rows = study.load_rows(prior_path)
        exact = generated_rows == prior_rows
        map_fields = sum(
            "torso_com_accelerometer_map" in row for row in generated_rows
        )
        return {
            "exact_field_for_field": exact,
            "generated_sha256": sha256(generated_path),
            "prior_sha256": prior["sha256"],
            "rows": len(generated_rows),
            "map_fields": map_fields,
            "status": payload.get("status"),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("exact CPU environment required")

    prereg_text = PREREG.read_text()
    closed_text = CLOSED_LOOP.read_text()
    evaluator_text = EVALUATOR.read_text()
    manifest = json.loads(PRIOR_MANIFEST.read_text())
    study = load_study()
    actual_sources = {
        "prereg": sha256(PREREG), "prior_manifest": sha256(PRIOR_MANIFEST),
        "invalid_result": sha256(INVALID_RESULT), "jit_result": sha256(JIT_RESULT),
    }
    checks: dict[str, bool] = {}
    checks["frozen_source_hashes_exact"] = actual_sources == {
        key: EXPECTED[key]
        for key in ("prereg", "prior_manifest", "invalid_result", "jit_result")
    }
    checks["preinstrumentation_hashes_frozen_in_prereg"] = (
        EXPECTED["closed_loop_pre"] in prereg_text
        and EXPECTED["evaluator_pre"] in prereg_text
    )
    checks["default_off_config_tuple_exact"] = (
        "trace_com_accelerometer_map_ticks: tuple[int, ...] = ()" in closed_text
    )
    checks["instrumentation_guarded_default_off"] = (
        "if com_accelerometer_map_ticks:" in closed_text
        and "if tick in com_accelerometer_map_ticks:" in closed_text
        and "if com_accelerometer_map is not None:" in closed_text
    )
    checks["validated_eager_runner_exact"] = (
        "com_accelerometer_map_runner = read_com_accelerometer" in closed_text
        and "com_accelerometer_map_runner = jax.jit(read_com_accelerometer)"
        not in closed_text
        and json.loads(JIT_RESULT.read_text()).get("decision")
        == "GENERAL_JIT_FORWARD_DISCREPANCY_OR_UNRESOLVED"
    )
    checks["append_only_trace_field_exact"] = (
        'record["torso_com_accelerometer_map"] = com_accelerometer_map' in closed_text
        and closed_text.count('record["torso_com_accelerometer_map"]') == 1
    )
    checks["mjx_forward_only_branch_static"] = (
        "branch_data = mjx.forward(branch_model, data)" in closed_text
        and '"branch_operation": "mjx.forward_only_no_time_advance"' in closed_text
    )
    checks["cli_default_off_and_trace_required"] = (
        '"--trace-com-accelerometer-map-ticks"' in evaluator_text
        and 'default=""' in evaluator_text
        and 'parser.error("--trace-com-accelerometer-map-ticks requires --trace-dir")' in evaluator_text
    )
    checks["source_12_matrices_36_moving_traces"] = (
        len(study.nominal_sources()) == 12
        and sum(
            row["condition"] == "NOMINAL"
            and round(float(row["command_x"]), 3) in {0.074, 0.077, 0.08}
            for row in manifest["traces"]
        ) == 36
    )

    regression = default_off_regression(study)
    checks["default_off_trace_field_identity_exact"] = regression["exact_field_for_field"]
    checks["default_off_has_zero_map_fields"] = regression["map_fields"] == 0
    checks["default_off_600_rows_and_pass"] = (
        regression["rows"] == 600
        and regression["status"] == "PASS_GAIT_EMERGENCE_CHECKPOINT"
    )
    checks["formal_com_branch_cells_not_executed"] = True

    failed = sorted(name for name, passed in checks.items() if not passed)
    status = (
        "PASS_TORSO_COM_EAGER_MJX_ACCELEROMETER_CONTRACT"
        if not failed else "FAIL_TORSO_COM_EAGER_MJX_ACCELEROMETER_CONTRACT"
    )
    payload = {
        "schema_version": "ground_up_torso_com_eager_mjx_accelerometer_contract.v1",
        "status": status, "checks": checks, "failed_checks": failed,
        "details": {
            "contract_tool_sha256": sha256(Path(__file__)),
            "study_tool_sha256": sha256(STUDY_TOOL),
            "closed_loop_sha256": sha256(CLOSED_LOOP),
            "evaluator_sha256": sha256(EVALUATOR),
            "preinstrumentation_hashes": {
                "closed_loop": EXPECTED["closed_loop_pre"],
                "evaluator": EXPECTED["evaluator_pre"],
            },
            "source_hashes": actual_sources,
            "default_off_regression": regression,
            "planned_matrices": 12, "planned_runs": 36, "planned_cells": 144,
        },
        "execution": {
            "cpu_only": True, "default_off_baseline_runs": 1,
            "default_off_baseline_ticks": 600, "formal_com_cells_executed": 0,
            "training": False, "robot_or_rdk": False,
        },
        "authority": {
            "formal_eager_mjx_replay_if_pass": True, "training": False,
            "gpu_or_igpu": False, "robot_or_rdk": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "failed_checks": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
