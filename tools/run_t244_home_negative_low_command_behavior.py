#!/usr/bin/env python3
"""Run T244's one decisive half/P30/home-negative/x=.074 CPU cell."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = (
    ANALYSIS
    / "t244_home_negative_low_command_behavior_preregistration.json"
)
RESULT = ANALYSIS / "t244_home_negative_low_command_behavior_result.json"
MARKDOWN = (
    ANALYSIS / "T244_HOME_NEGATIVE_LOW_COMMAND_BEHAVIOR_RESULT_20260731.md"
)
CACHE = Path(
    "D:/CodexArtifacts/open-duck-policy/"
    "t244_home_negative_low_command_behavior_v1"
)
sys.path.insert(0, str(ROOT / "tools"))
from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    receipt,
    sha256,
)
from run_t242_bounded_router_home_offset import (  # noqa: E402
    corrected_joint_offset_readback,
)
from run_t6_corrected_robustness_screen import (  # noqa: E402
    behavior_row,
    classify_behavior,
    trace_summary,
)
from run_t8_state_coherent_handoff import (  # noqa: E402
    read_trace,
    state_handoff_summary,
)


def verify(value: Mapping[str, Any]) -> None:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != value["bytes"]
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"changed T244 input: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.parse_args()
    if RESULT.exists() or MARKDOWN.exists() or CACHE.exists():
        raise FileExistsError("refusing to overwrite T244 output")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T244 execution requires clean worktree")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T244_HOME_NEGATIVE_LOW_COMMAND_BEHAVIOR"
        or prereg["failed_checks"]
        or canonical_sha256(basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T244 preregistration changed")
    for item in prereg["frozen_inputs"].values():
        verify(item)
    for item in [
        prereg["policy"],
        prereg["fit"],
        prereg["calibrator"],
        prereg["reference_feature_table"],
        prereg["playground"]["manifest"],
        *prereg["repository_inputs"].values(),
    ]:
        verify(item)

    CACHE.mkdir(parents=True)
    trace_dir = CACHE / "traces"
    evaluation_path = CACHE / "evaluation.json"
    stdout_path = CACHE / "stdout.log"
    worker = Path(prereg["repository_inputs"]["worker"]["path"])
    command = [
        sys.executable,
        str(worker),
        "--policy",
        prereg["policy"]["path"],
        "--policy-sha256",
        prereg["policy"]["sha256"],
        "--playground-root",
        prereg["playground"]["path"],
        "--fit",
        prereg["fit"]["path"],
        "--reference-feature-table",
        prereg["reference_feature_table"]["path"],
        "--calibrator",
        prereg["calibrator"]["path"],
        "--calibrator-sha256",
        prereg["calibrator"]["sha256"],
        "--override-json",
        json.dumps(
            prereg["condition"]["override"],
            separators=(",", ":"),
            sort_keys=True,
        ),
        "--commands",
        f"{float(prereg['command_x_m_s']):.3f}",
        "--seed",
        str(prereg["seed"]),
        "--duration-s",
        str(prereg["duration_s"]),
        "--trace-dir",
        str(trace_dir),
        "--output-json",
        str(evaluation_path),
    ]
    started = time.time()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    stdout_path.write_text(
        completed.stdout + completed.stderr,
        encoding="utf-8",
        newline="\n",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"T244 worker failed: {completed.returncode}; {stdout_path}"
        )
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    runs = evaluation.get("runs") or []
    if len(runs) != 1:
        raise RuntimeError("T244 worker did not return exactly one run")
    run = runs[0]
    trace_path = Path(run["trace_jsonl"])
    records = read_trace(trace_path)
    behavior = classify_behavior(
        behavior_row(run), prereg["behavior_contract"]
    )
    protection = trace_summary(
        trace_path, prereg["protection_contract"]
    )
    handoff = state_handoff_summary(run, records)
    readback = corrected_joint_offset_readback(
        run.get("dynamics_override"),
        float(prereg["condition"]["override"]["joint_qpos0_offset_rad"]),
    )
    worker_inputs = evaluation.get("inputs") or {}
    worker_inputs_exact = (
        worker_inputs.get("commands_x_m_s")
        == [float(prereg["command_x_m_s"])]
        and worker_inputs.get("seed") == prereg["seed"]
        and worker_inputs.get("duration_s") == prereg["duration_s"]
        and worker_inputs.get("calibration_ticks") == 250
        and worker_inputs.get("home_return_ticks") == 0
        and worker_inputs.get("preserve_handoff_state") is True
        and worker_inputs.get("expected_observation_dim") == 115
        and worker_inputs.get("expected_action_dim") == 14
        and worker_inputs.get("policy_graph_authoritative_output") is True
        and worker_inputs.get("policy_applied_target_observation") is True
        and worker_inputs.get("eval_dynamics_override")
        == prereg["condition"]["override"]
    )
    trace_valid = (
        protection["ticks_contiguous_from_zero"]
        and protection["rows"] == behavior["samples"] == 600
    )
    cell_green = bool(
        worker_inputs_exact
        and trace_valid
        and behavior["core_pass"]
        and behavior["replacement_quality_pass"]
        and protection["duration_protection_pass"]
        and protection["maximum_full_measured_vector_excess_rad_s"] == 0.0
        and handoff["all_checks_pass"]
        and readback
        and (evaluation.get("execution") or {}).get("platform") == "cpu"
    )
    manifest_basis = {
        "schema_version": "open_duck.t244_behavior_cell_manifest.v1",
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "command": command,
        "evaluation": receipt(evaluation_path),
        "stdout": receipt(stdout_path),
        "trace": receipt(trace_path),
    }
    manifest = {
        **manifest_basis,
        "manifest_sha256": canonical_sha256(manifest_basis),
    }
    manifest_path = CACHE / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    basis_result: dict[str, Any] = {
        "schema_version": (
            "open_duck.t244_home_negative_low_command_behavior_result.v1"
        ),
        "status": (
            "PASS_T244_HOME_NEGATIVE_LOW_COMMAND_BEHAVIOR"
            if cell_green
            else "HOLD_T244_HOME_NEGATIVE_LOW_COMMAND_BEHAVIOR"
        ),
        "decision": (
            prereg["decision_rule"]["pass"]
            if cell_green
            else prereg["decision_rule"]["fail"]
        ),
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "manifest": receipt(manifest_path),
        "cell": {
            "checkpoint_id": prereg["policy"]["checkpoint_id"],
            "fit_id": prereg["fit"]["fit_id"],
            "condition_id": prereg["condition"]["id"],
            "command_x_m_s": prereg["command_x_m_s"],
            "worker_inputs_exact": worker_inputs_exact,
            "execution_platform": (
                evaluation.get("execution") or {}
            ).get("platform"),
            "behavior": behavior,
            "protection": protection,
            "handoff": handoff,
            "trace_valid": trace_valid,
            "override_readback_exact": readback,
            "cell_green": cell_green,
        },
        "execution": {
            "formal_t244_behavior_cells": 1,
            "simulator_steps": len(records),
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
            "wall_seconds": time.time() - started,
        },
        "authority": {
            "remaining_matrix_preregistration": cell_green,
            "training": False,
            "hosted": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    value = {
        **basis_result,
        "result_sha256": canonical_sha256(basis_result),
    }
    RESULT.write_text(
        json.dumps(value, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T244 home-negative low-command behavior result\n\n"
        f"- Status: `{value['status']}`\n"
        f"- Decision: `{value['decision']}`\n"
        f"- Samples: `{behavior['samples']}/600`\n"
        f"- Mean local vx: `{behavior['mean_local_vx_m_s']:.9f}`\n"
        f"- Tracking p95: `{behavior['pitch_tracking_p95_rad']:.9f}`\n"
        "- Optimizer/hosted/robot: `0/0/0`\n"
        f"- Result SHA-256: `{value['result_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(value["status"])
    print(f"decision={value['decision']}")
    print(f"samples={behavior['samples']}/600")
    print(f"result_sha256={value['result_sha256']}")
    return 0 if cell_green else 1


if __name__ == "__main__":
    raise SystemExit(main())
