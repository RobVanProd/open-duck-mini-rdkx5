#!/usr/bin/env python3
"""Run the preregistered one-cell T32 final margin causal A/B."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t35_t32_margin_causality_preregistration.json"
OUTPUT = ANALYSIS / "t35_t32_margin_causality_result.json"
OUTPUT_MD = ANALYSIS / "T35_T32_MARGIN_CAUSALITY_RESULT_20260727.md"
CACHE_ROOT = (
    Path(r"D:\CodexArtifacts\open-duck-policy")
    / "t35_t32_margin_causality_v1"
)

sys.path.insert(0, str(ROOT / "tools"))
from run_t6_corrected_robustness_screen import (  # noqa: E402
    behavior_row,
    classify_behavior,
    exact_override_readback,
    trace_summary,
)
from run_t8_state_coherent_handoff import (  # noqa: E402
    read_trace,
    state_handoff_summary,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = dict(value)
    payload.pop("result_sha256", None)
    return hashlib.sha256(
        json.dumps(
            payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def receipt(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def verify(prereg: dict[str, Any]) -> None:
    expected = prereg["preregistered_contract_sha256"]
    actual = hashlib.sha256(
        json.dumps(
            {
                key: value
                for key, value in prereg.items()
                if key != "preregistered_contract_sha256"
            },
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()
    if actual != expected:
        raise ValueError("changed T35 preregistration")
    if prereg["status"] != "PREREGISTERED_T35_T32_MARGIN_CAUSAL_AB":
        raise ValueError("T35 preregistration is not green")
    for item in prereg["frozen_inputs"].values():
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed T35 frozen input: {path}")
    for item in [
        prereg["pre_margin_policy"],
        prereg["fit"],
        prereg["calibrator"],
        prereg["reference_feature_table"],
        prereg["wrapped_failure"]["trace"],
    ]:
        path = Path(item["path"])
        if sha256(path) != item["sha256"]:
            raise ValueError(f"changed T35 evaluated input: {path}")


def require_clean_worktree() -> str:
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status.strip():
        raise RuntimeError("formal T35 execution requires a clean worktree")
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def vector_error(
    left: dict[str, Any],
    right: dict[str, Any],
    key: str,
) -> float:
    return float(
        np.max(
            np.abs(
                np.asarray(left[key], dtype=np.float64)
                - np.asarray(right[key], dtype=np.float64)
            )
        )
    )


def write_result(payload: dict[str, Any]) -> None:
    payload["result_sha256"] = canonical_sha256(payload)
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(
        "\n".join(
            [
                "# T35 T32 margin-causality result",
                "",
                f"status: `{payload['status']}`",
                "",
                f"decision: `{payload['decision']}`",
                "",
                (
                    "- wrapped intervention events: "
                    f"`{payload['wrapped_failure']['intervention_count']}`"
                ),
                (
                    "- pre-margin cell executed: "
                    f"`{payload['execution']['formal_behavior_cells'] == 1}`"
                ),
                (
                    "- pre-margin cell green: "
                    f"`{payload.get('pre_margin_cell', {}).get('cell_green')}`"
                ),
                "",
                (
                    "T32 remains closed. No training, hosted compute, Gate 5, "
                    "RDK-X5, robot, torque, or motion is authorized."
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("refusing outcome execution without --execute")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    verify(prereg)
    commit = require_clean_worktree()
    interventions = prereg["wrapped_failure"]["intervention_events"]
    if not interventions:
        payload: dict[str, Any] = {
            "schema_version": "open_duck.t35_t32_margin_causality_result.v1",
            "status": "PASS_T35_NO_RUNTIME_MARGIN_INTERVENTION",
            "decision": (
                "ATTRIBUTE_T32_ACTOR_STATE_DRIFT_WITHOUT_MARGIN_INTERVENTION"
            ),
            "preregistered_contract_sha256": prereg[
                "preregistered_contract_sha256"
            ],
            "repository_commit": commit,
            "wrapped_failure": prereg["wrapped_failure"],
            "causal_comparison": {
                "strict_margin_intervened_before_failure": False,
                "pre_margin_cell_required": False,
            },
            "execution": {
                "cpu_only": True,
                "formal_behavior_cells": 0,
                "optimizer_steps": 0,
            },
            "authority": {
                "persistence_mechanism_review": True,
                "training": False,
                "colab": False,
                "gate5": False,
                "rdkx5_or_robot": False,
                "torque_or_motion": False,
            },
        }
        write_result(payload)
        print(payload["status"])
        print(f"decision={payload['decision']}")
        print(f"result_sha256={payload['result_sha256']}")
        print(f"sha256={sha256(OUTPUT)}")
        return 0

    CACHE_ROOT.mkdir(parents=True, exist_ok=False)
    trace_dir = CACHE_ROOT / "traces"
    trace_dir.mkdir()
    evaluation_path = CACHE_ROOT / "evaluation.json"
    stdout_path = CACHE_ROOT / "stdout.log"
    policy = prereg["pre_margin_policy"]
    cell = prereg["cell"]
    condition = cell["condition"]
    command = [
        sys.executable,
        prereg["frozen_inputs"]["worker"]["path"],
        "--formal",
        "--policy",
        policy["path"],
        "--policy-sha256",
        policy["sha256"],
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
            condition["override"],
            separators=(",", ":"),
            sort_keys=True,
        ),
        "--commands",
        str(cell["command_x_m_s"]),
        "--seed",
        str(cell["seed"]),
        "--duration-s",
        str(cell["duration_s"]),
        "--trace-dir",
        str(trace_dir),
        "--output-json",
        str(evaluation_path),
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
                CACHE_ROOT.parent / "jax_compilation_cache"
            ),
            "XLA_PYTHON_CLIENT_PREALLOCATE": "false",
        }
    )
    with stdout_path.open("w", encoding="utf-8") as stream:
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
    trace_path = (
        trace_dir
        / (
            f"x0.077_seed{cell['seed']}_"
            f"{Path(policy['path']).stem}.jsonl"
        )
    )
    if (
        completed.returncode != 0
        or not evaluation_path.is_file()
        or not trace_path.is_file()
    ):
        raise RuntimeError(
            f"T35 worker failed: {completed.returncode}; {stdout_path}"
        )
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    if evaluation.get("formal") is not True or len(evaluation["runs"]) != 1:
        raise ValueError("T35 worker returned the wrong formal matrix")
    run = evaluation["runs"][0]
    records = read_trace(trace_path)
    behavior = classify_behavior(
        behavior_row(run),
        prereg["behavior_contract"],
    )
    protection = trace_summary(
        trace_path,
        prereg["protection_contract"],
    )
    handoff = state_handoff_summary(run, records)
    readback = exact_override_readback(
        run.get("dynamics_override"),
        condition["override"],
    )
    trace_valid = (
        protection["ticks_contiguous_from_zero"]
        and protection["rows"] == behavior["samples"]
    )
    source_green = (
        trace_valid
        and behavior["core_pass"]
        and behavior["replacement_quality_pass"]
        and protection["duration_protection_pass"]
        and protection["maximum_full_measured_vector_excess_rad_s"] == 0.0
        and handoff["all_checks_pass"]
        and readback
    )
    wrapped_path = Path(prereg["wrapped_failure"]["trace"]["path"])
    wrapped = read_trace(wrapped_path)
    first_intervention = int(
        prereg["wrapped_failure"]["first_intervention_tick"]
    )
    compare_ticks = min(first_intervention, len(records), len(wrapped))
    comparison_keys = [
        "action",
        "qpos",
        "qvel",
        "obs_state",
        "applied_target_rad",
        "sent_target_rad",
    ]
    pre_intervention_errors = {
        key: max(
            (
                vector_error(records[index], wrapped[index], key)
                for index in range(compare_ticks)
            ),
            default=0.0,
        )
        for key in comparison_keys
    }
    pre_intervention_exact = all(
        value == 0.0 for value in pre_intervention_errors.values()
    )
    valid_result = (
        trace_valid
        and handoff["all_checks_pass"]
        and readback
        and pre_intervention_exact
    )
    if not valid_result:
        status = "INVALID_T35_T32_MARGIN_CAUSAL_AB"
        decision = "ZERO_POLICY_DECISION_WEIGHT"
    elif source_green:
        status = "PASS_T35_T32_MARGIN_IS_CAUSAL"
        decision = "CLOSE_HARD_DEPLOYMENT_MARGIN_MECHANISM"
    else:
        status = "PASS_T35_T32_MARGIN_NOT_SUFFICIENT_CAUSE"
        decision = "ATTRIBUTE_T32_CONTINUED_TRAINING_ACTOR_STATE_DRIFT"
    source_limit = float(
        prereg["margin"]["saturation_observation_threshold_abs"]
    )
    source_margin_events = [
        {
            "tick": int(row["tick"]),
            "joint_index": joint_index,
            "action": float(value),
        }
        for row in records
        for joint_index, value in enumerate(row["action"])
        if abs(float(value)) >= source_limit
    ]
    payload = {
        "schema_version": "open_duck.t35_t32_margin_causality_result.v1",
        "status": status,
        "decision": decision,
        "preregistered_contract_sha256": prereg[
            "preregistered_contract_sha256"
        ],
        "repository_commit": commit,
        "pre_margin_cell": {
            "behavior": behavior,
            "protection": protection,
            "handoff": handoff,
            "override_readback_exact": readback,
            "trace_valid": trace_valid,
            "cell_green": source_green,
            "trace": receipt(trace_path),
            "margin_event_count": len(source_margin_events),
            "first_margin_event": (
                source_margin_events[0] if source_margin_events else None
            ),
        },
        "wrapped_failure": prereg["wrapped_failure"],
        "causal_comparison": {
            "ticks_compared_before_first_intervention": compare_ticks,
            "pre_intervention_errors": pre_intervention_errors,
            "pre_intervention_exact": pre_intervention_exact,
            "pre_margin_samples": behavior["samples"],
            "wrapped_samples": prereg["wrapped_failure"]["samples"],
            "pre_margin_cell_green": source_green,
        },
        "execution": {
            "cpu_only": True,
            "formal_behavior_cells": 1,
            "optimizer_steps": 0,
            "command": command,
            "evaluation": receipt(evaluation_path),
            "stdout": receipt(stdout_path),
        },
        "authority": {
            "persistence_mechanism_review": valid_result,
            "training": False,
            "colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    write_result(payload)
    print(status)
    print(f"decision={decision}")
    print(f"pre_margin_green={source_green}")
    print(f"pre_margin_samples={behavior['samples']}")
    print(f"wrapped_samples={prereg['wrapped_failure']['samples']}")
    print(f"result_sha256={payload['result_sha256']}")
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if valid_result else 1


if __name__ == "__main__":
    raise SystemExit(main())
