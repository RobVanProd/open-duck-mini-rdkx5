#!/usr/bin/env python3
"""Run a one-scored-tick T27 integration contract on CPU."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from run_t6_corrected_robustness_screen import exact_override_readback
from run_t8_state_coherent_handoff import (
    read_trace,
    state_handoff_summary,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
OUTPUT = ANALYSIS / "t27_t23_robustness_runner_contract.json"
MARKDOWN = ANALYSIS / "T27_T23_ROBUSTNESS_RUNNER_CONTRACT_20260726.md"
WORKER = ROOT / "tools" / "evaluate_t27_t23_robustness_condition.py"
RUN_ROOT = Path(
    r"D:\CodexArtifacts\open-duck-policy\t27_runner_contract_v1"
)
POLICY = Path(
    r"D:\CodexArtifacts\open-duck-policy\t25_t23_nominal_policies_v1"
    r"\T23_SUPPORT_2007040.onnx"
)
PLAYGROUND = Path(
    r"D:\CodexProjects\Open_Duck_Playground-composed-t19-v6"
)
FIT = ANALYSIS / "fixed_target_p30_actuator_fit_20260712.json"
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
T8_PREREG = ANALYSIS / "t8_state_coherent_handoff_preregistration.json"
T24_RESULT = ANALYSIS / "t24_t23_postexport_result.json"
OVERRIDE = {"floor_friction": 0.5}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def main() -> int:
    if OUTPUT.exists() or MARKDOWN.exists() or RUN_ROOT.exists():
        raise FileExistsError("refusing to overwrite T27 runner contract")
    t8 = json.loads(T8_PREREG.read_text(encoding="utf-8"))
    t24 = json.loads(T24_RESULT.read_text(encoding="utf-8"))
    calibrator = Path(t8["calibrator"]["path"])
    calibrator_sha = t8["calibrator"]["sha256"]
    policy_sha = sha256(POLICY)
    trace_dir = RUN_ROOT / "traces"
    evaluation = RUN_ROOT / "evaluation.json"
    stdout = RUN_ROOT / "stdout.log"
    trace_dir.mkdir(parents=True)
    command = [
        sys.executable,
        str(WORKER),
        "--policy",
        str(POLICY),
        "--policy-sha256",
        policy_sha,
        "--playground-root",
        str(PLAYGROUND),
        "--fit",
        str(FIT),
        "--reference-feature-table",
        str(REFERENCE),
        "--calibrator",
        str(calibrator),
        "--calibrator-sha256",
        calibrator_sha,
        "--override-json",
        json.dumps(OVERRIDE, separators=(",", ":"), sort_keys=True),
        "--commands",
        "0.074",
        "--seed",
        "167931544",
        "--duration-s",
        "0.02",
        "--trace-dir",
        str(trace_dir),
        "--output-json",
        str(evaluation),
    ]
    environment = os.environ.copy()
    environment.update(
        {
            "CUDA_VISIBLE_DEVICES": "",
            "HIP_VISIBLE_DEVICES": "",
            "ROCR_VISIBLE_DEVICES": "",
            "JAX_PLATFORMS": "cpu",
            "JAX_PLATFORM_NAME": "cpu",
            "JAX_COMPILATION_CACHE_DIR": str(
                RUN_ROOT.parent / "jax_compilation_cache"
            ),
            "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
        }
    )
    with stdout.open("w", encoding="utf-8") as stream:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            stdout=stream,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=2400,
            check=False,
        )
    if completed.returncode != 0 or not evaluation.is_file():
        raise RuntimeError(
            f"T27 runner contract failed: returncode={completed.returncode}; "
            f"log={stdout}"
        )
    value = json.loads(evaluation.read_text(encoding="utf-8"))
    run = value["runs"][0]
    trace = Path(run["trace_jsonl"])
    records = read_trace(trace)
    handoff = state_handoff_summary(run, records)
    mode = (run.get("modes") or {}).get("fitted") or {}
    inputs = value["inputs"]
    final_t24 = t24["deployments"]["2007040"]
    checks = {
        "worker_completed_nonformal_smoke": (
            value["status"]
            == "COMPLETE_T27_T23_ROBUSTNESS_CONDITION_BLOCK"
            and value["formal"] is False
            and value["execution"]["formal_behavior_cells"] == 0
            and value["execution"]["contract_smoke_runs"] == 1
        ),
        "one_scored_tick_duration_complete": (
            mode.get("samples") == 1
            and mode.get("termination_reason") == "duration_complete"
        ),
        "exact_support_handoff": handoff["all_checks_pass"],
        "override_readback_exact": exact_override_readback(
            run.get("dynamics_override"), OVERRIDE
        ),
        "worker_inputs_exact": (
            inputs["calibration_ticks"] == 250
            and inputs["home_return_ticks"] == 0
            and inputs["preserve_handoff_state"] is True
            and inputs["policy_context_input_name"]
            == "calibration_context"
            and inputs["eval_dynamics_override"] == OVERRIDE
        ),
        "trace_one_tick_finite_and_contiguous": (
            len(records) == 1
            and int(records[0]["tick"]) == 0
            and all(
                key in records[0]
                for key in (
                    "obs_state",
                    "policy_state_input",
                    "policy_state_output",
                    "actuator_force_nm",
                    "applied_target_rad",
                )
            )
        ),
        "graph_authoritative_no_host_delta": (
            records[0].get("policy_graph_authoritative_output") is True
            and records[0].get("policy_host_action_delta_max_abs") == 0.0
        ),
        "context_is_proven_diagnostic_only": (
            final_t24["context_parity"]["context_is_diagnostic_only"] is True
            and final_t24["context_parity"]["all_outputs_bit_exact"] is True
        ),
        "policy_is_exact_t24_final": (
            policy_sha == final_t24["wrapped"]["sha256"]
        ),
        "cpu_only": value["execution"]["platform"] == "cpu",
    }
    failed = [name for name, passed in checks.items() if not passed]
    result = {
        "schema_version": "open_duck.t27_t23_robustness_runner_contract.v1",
        "status": (
            "PASS_T27_T23_ROBUSTNESS_RUNNER_CONTRACT"
            if not failed
            else "HOLD_T27_T23_ROBUSTNESS_RUNNER_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "inputs": {
            "worker": {
                "path": str(WORKER.resolve()),
                "sha256": sha256(WORKER),
            },
            "policy": {
                "path": str(POLICY.resolve()),
                "sha256": policy_sha,
            },
            "playground": str(PLAYGROUND.resolve()),
            "fit": {"path": str(FIT.resolve()), "sha256": sha256(FIT)},
            "reference": {
                "path": str(REFERENCE.resolve()),
                "sha256": sha256(REFERENCE),
            },
            "calibrator": {
                "path": str(calibrator.resolve()),
                "sha256": calibrator_sha,
            },
            "override": OVERRIDE,
        },
        "execution": {
            "formal_behavior_cells": 0,
            "unscored_support_ticks": 250,
            "scored_contract_ticks": 1,
            "optimizer_steps": 0,
            "hosted_compute": 0,
            "robot_or_rdk_access": 0,
        },
        "evaluation": {
            "path": str(evaluation),
            "sha256": sha256(evaluation),
        },
        "trace": {
            "path": str(trace),
            "sha256": sha256(trace),
            "rows": len(records),
        },
        "handoff": handoff,
        "dynamics_override": run.get("dynamics_override"),
        "authority": {
            "robustness_preregistration_authorized": not failed,
            "formal_robustness_execution_authorized": False,
            "training_authorized": False,
            "gate5_authorized": False,
            "rdkx5_or_robot": False,
        },
    }
    result["result_sha256"] = canonical_sha256(result)
    OUTPUT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# T27 T23 robustness runner contract\n\n"
        f"- Status: `{result['status']}`\n"
        f"- Failed checks: `{failed}`\n"
        "- Execution: 250 unscored support ticks plus one scored CPU tick; "
        "zero formal behavior cells.\n"
        "- The handoff, applied-target continuity, recurrent state, exact "
        "R2 readback, and graph-authoritative action path are all checked.\n"
        "- No training, Gate 5, RDK-X5, robot access, torque, or motion is "
        "authorized.\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(f"failed_checks={failed}")
    print(f"result_sha256={result['result_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
