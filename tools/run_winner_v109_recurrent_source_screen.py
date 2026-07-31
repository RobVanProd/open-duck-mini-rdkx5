#!/usr/bin/env python3
"""Run the preregistered recurrent-source screen with the corrected current gate."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Iterable, Mapping

import jax
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from closed_loop_sim_eval import ClosedLoopConfig, run_closed_loop_sim  # noqa: E402
from run_winner_v3_variable_configuration_behavior import (  # noqa: E402
    actuator_fit,
    classify_cell,
    readback_checks,
    sha256,
    trace_audit,
)
from run_winner_v103_response_conditioned_behavior import (  # noqa: E402
    REFERENCE,
    json_finite,
    missing_trace_audit,
)
from run_winner_v107_stage_boundary_diagnostic import (  # noqa: E402
    cpu_environment_exact,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v109_recurrent_source_preregistration.json"
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
RESULT_JSON = ANALYSIS / "winner_v109_recurrent_source_result.json"
RESULT_MD = ANALYSIS / "WINNER_V109_RECURRENT_SOURCE_RESULT_20260724.md"
PREREG_SHA256 = (
    "b64578fa873d5397dfa96c4e089ec6757b255e30a69a90d2a353306d14933736"
)
MATRIX_SHA256 = (
    "9835cd79c64dd1a2b7ccbd1cc05d91a6c1b31dcfef31faf7ab1d2bfdf85ef11e"
)
CURRENT_NM_PER_A = 0.784532
PEAK_CURRENT_MAX_A = 2.5
STRICT_OVERCURRENT_A = 2.0
MAX_STRICT_OVERCURRENT_RUN_TICKS = 99


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def policy_path(policy_root: Path, row: Mapping[str, Any]) -> Path:
    filename = (
        f"R64_ZERO_INIT_RECURRENT_ADAPTER_{int(row['step'])}.onnx"
    )
    return policy_root / filename


def cell_stem(row: Mapping[str, Any]) -> str:
    return (
        f"{str(row['checkpoint_id']).lower()}_"
        f"{str(row['plant']).lower()}_"
        f"x{float(row['command_x_m_s']):.3f}_"
        f"seed{int(row['seed'])}"
    )


def longest_true_run(values: np.ndarray) -> int:
    longest = 0
    current = 0
    for value in values:
        if bool(value):
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def prospective_current_metrics(actuator_force_nm: np.ndarray) -> dict[str, Any]:
    force = np.asarray(actuator_force_nm, dtype=np.float64)
    if force.ndim != 2 or force.shape[1] != 14 or force.shape[0] == 0:
        raise ValueError("actuator_force_nm must have shape [ticks, 14]")
    if not np.all(np.isfinite(force)):
        raise ValueError("actuator_force_nm must be finite")
    current = np.abs(force) / CURRENT_NM_PER_A
    peak_by_joint = np.max(current, axis=0)
    p95_by_joint = np.percentile(current, 95.0, axis=0)
    longest_overcurrent_by_joint = np.asarray(
        [
            longest_true_run(current[:, index] > STRICT_OVERCURRENT_A)
            for index in range(14)
        ],
        dtype=np.int64,
    )
    peak_pass = bool(np.all(peak_by_joint <= PEAK_CURRENT_MAX_A))
    duration_pass = bool(
        np.all(
            longest_overcurrent_by_joint
            <= MAX_STRICT_OVERCURRENT_RUN_TICKS
        )
    )
    return {
        "conversion_nm_per_a": CURRENT_NM_PER_A,
        "samples": int(force.shape[0]),
        "peak_current_a_by_joint": peak_by_joint.tolist(),
        "worst_peak_current_a": float(np.max(peak_by_joint)),
        "p95_current_a_by_joint": p95_by_joint.tolist(),
        "worst_p95_current_a_diagnostic_only": float(
            np.max(p95_by_joint)
        ),
        "longest_strict_over_2a_run_ticks_by_joint": (
            longest_overcurrent_by_joint.tolist()
        ),
        "worst_strict_over_2a_run_ticks": int(
            np.max(longest_overcurrent_by_joint)
        ),
        "checks": {
            "current_peak_at_most_2p5": peak_pass,
            "overcurrent_gt_2a_at_most_99_consecutive_ticks": duration_pass,
        },
        "pass": peak_pass and duration_pass,
    }


def current_metrics_from_trace(trace_path: Path) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in trace_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    return prospective_current_metrics(
        np.asarray([row["actuator_force_nm"] for row in rows], dtype=float)
    )


def max_or_none(values: Iterable[float | int]) -> float | int | None:
    rows = list(values)
    return max(rows) if rows else None


def early_return_cell(
    *,
    row: Mapping[str, Any],
    policy: Path,
    result: Mapping[str, Any],
    trace_path: Path,
    cpu_only: bool,
) -> dict[str, Any]:
    status = str(result.get("status") or "MISSING_STATUS")
    return {
        "schema_version": "winner_v109.recurrent_source_cell.v1",
        "status": "HOLD_WINNER_V109_RECURRENT_SOURCE_CELL",
        "pass": False,
        "failure_reasons": [
            f"simulator_early_return_{status}",
            "trace_missing",
        ]
        + ([] if cpu_only else ["cpu_only"]),
        "identity": dict(row),
        "policy": {"path": str(policy), "sha256": sha256(policy)},
        "simulator": {
            "status": result.get("status"),
            "error": result.get("error"),
            "result_keys": sorted(result),
        },
        "metrics": {
            "samples": 0,
            "termination_reason": "simulator_early_return",
            "mean_local_vx_m_s": None,
            "worst_tracking_p95_rad": None,
            "worst_current_p95_a": None,
            "checks": {"cpu_only": cpu_only},
        },
        "prospective_current_gate": {
            "checks": {},
            "pass": False,
        },
        "readback_checks": {
            "environment_readback_present": result.get("env") is not None
        },
        "trace": missing_trace_audit(trace_path),
        "robot_clearance": False,
        "training_or_simulator_reward_selection_weight": 0,
    }


def execute_cell(
    row: Mapping[str, Any],
    prereg: Mapping[str, Any],
    *,
    policy: Path,
    playground: Path,
    trace_path: Path,
    cpu_only: bool,
) -> dict[str, Any]:
    transport = row["transport"]
    base_row = {
        "condition_group": "NOMINAL",
        "condition_id": "V109_RECURRENT_SOURCE",
        "seed": int(row["seed"]),
        "step": int(row["step"]),
        "plant": row["plant"],
        "command_x_m_s": float(row["command_x_m_s"]),
        "duration_ticks": int(row["duration_ticks"]),
        "configuration": row["configuration"],
        "transport": transport,
    }
    with contextlib.redirect_stdout(io.StringIO()):
        result = run_closed_loop_sim(
            ClosedLoopConfig(
                policy_path=policy,
                fit=actuator_fit(prereg, str(row["plant"])),
                playground_root=playground,
                command_x=float(row["command_x_m_s"]),
                duration_s=12.0,
                bridge_mode="fitted",
                expected_observation_dim=115,
                task="flat_terrain_backlash",
                seed=int(row["seed"]),
                eval_role="candidate",
                reset_mode="home-support",
                policy_obs_input_name="obs",
                policy_action_output_name="continuous_actions",
                policy_state_input_names=("h_in", "previous_action"),
                policy_state_output_names=("h_out", "previous_action_out"),
                policy_graph_authoritative_output=True,
                policy_applied_target_observation=True,
                reference_feature_table_path=REFERENCE,
                reference_start_phase=0,
                trace_jsonl=trace_path,
                trace_full_obs=True,
                winner_v3_configuration_override=row["configuration"],
                winner_v3_sensor_noise_scales=transport[
                    "sensor_noise_scales"
                ],
                winner_v3_native_quantization=bool(
                    transport["native_quantization"]
                ),
                winner_v3_additional_action_delay_ticks=int(
                    transport["additional_action_delay_ticks"]
                ),
                winner_v3_imu_delay_ticks=int(
                    transport["imu_delay_ticks"]
                ),
                winner_v3_home_relative_actuator_gain=True,
            )
        )
    if result.get("env") is None or not trace_path.exists():
        return early_return_cell(
            row=row,
            policy=policy,
            result=result,
            trace_path=trace_path,
            cpu_only=cpu_only,
        )

    trace = trace_audit(trace_path)
    readback = readback_checks(base_row, result, prereg)
    _, failures, metrics = classify_cell(base_row, result, trace, readback)
    failures = [
        reason
        for reason in failures
        if reason not in {"current_p95_at_most_0p65", "cpu_only"}
    ]
    metrics["checks"].pop("current_p95_at_most_0p65", None)
    current = current_metrics_from_trace(trace_path)
    for name, passed in current["checks"].items():
        metrics["checks"][name] = passed
        if not passed:
            failures.append(name)
    if not cpu_only:
        failures.append("cpu_only")
    metrics["checks"]["cpu_only"] = cpu_only
    failures = sorted(set(failures))
    return {
        "schema_version": "winner_v109.recurrent_source_cell.v1",
        "status": (
            "PASS_WINNER_V109_RECURRENT_SOURCE_CELL"
            if not failures
            else "HOLD_WINNER_V109_RECURRENT_SOURCE_CELL"
        ),
        "pass": not failures,
        "failure_reasons": failures,
        "identity": dict(row),
        "policy": {"path": str(policy), "sha256": sha256(policy)},
        "simulator": {
            "status": result.get("status"),
            "error": result.get("error"),
        },
        "metrics": metrics,
        "prospective_current_gate": current,
        "readback_checks": readback,
        "model_readback": (result.get("env") or {}).get(
            "winner_v3_configuration_readback"
        ),
        "candidate_gate": result.get("candidate_gate"),
        "trace": trace,
        "robot_clearance": False,
        "training_or_simulator_reward_selection_weight": 0,
    }


def execute(
    *, policy_root: Path, playground: Path, run_root: Path
) -> dict[str, Any]:
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise RuntimeError("CUDA_VISIBLE_DEVICES must be empty")
    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("JAX_PLATFORMS must be cpu")
    preregistration = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        sha256(PREREG) != PREREG_SHA256
        or preregistration.get("status")
        != "PREREGISTERED_WINNER_V109_RECURRENT_SOURCE_SCREEN"
        or preregistration.get("failed_checks") != []
        or preregistration.get("matrix", {}).get("sha256") != MATRIX_SHA256
        or preregistration.get("authority", {}).get(
            "formal_behavior_cells_authorized"
        )
        != 16
    ):
        raise ValueError("Winner-v109 preregistration is not passing")
    if run_root.exists():
        raise FileExistsError(f"refusing to overwrite V109 run root: {run_root}")
    if RESULT_JSON.exists() or RESULT_MD.exists():
        raise FileExistsError("refusing to overwrite V109 result")
    if not playground.exists():
        raise FileNotFoundError(playground)
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("Winner-v109 execution requires a clean worktree")

    matrix = preregistration["matrix"]["rows"]
    if len(matrix) != 16 or canonical_sha256(matrix) != MATRIX_SHA256:
        raise ValueError("Winner-v109 matrix changed")
    policy_specs = {
        row["id"]: row for row in preregistration["policies"]
    }
    for checkpoint_id, spec in policy_specs.items():
        path = policy_root / spec["filename"]
        if sha256(path) != spec["sha256"]:
            raise ValueError(f"policy changed: {checkpoint_id}")

    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    cells_root = run_root / "cells"
    traces_root = run_root / "traces"
    cells_root.mkdir(parents=True)
    traces_root.mkdir(parents=True)
    backend = jax.default_backend()
    device_platforms = [device.platform for device in jax.devices()]
    cpu_only = cpu_environment_exact(backend, device_platforms)
    started = time.time()
    cells: list[dict[str, Any]] = []
    for index, row in enumerate(matrix, start=1):
        stem = cell_stem(row)
        trace_path = traces_root / f"{stem}.jsonl"
        policy = policy_path(policy_root, row)
        try:
            cell = execute_cell(
                row,
                base_prereg,
                policy=policy,
                playground=playground,
                trace_path=trace_path,
                cpu_only=cpu_only,
            )
        except Exception as exc:  # fail closed and preserve the one run
            cell = early_return_cell(
                row=row,
                policy=policy,
                result={
                    "status": f"RUNNER_EXCEPTION_{type(exc).__name__}",
                    "error": str(exc),
                },
                trace_path=trace_path,
                cpu_only=cpu_only,
            )
        cell = json_finite(cell)
        cell_path = cells_root / f"{stem}.json"
        cell_path.write_text(
            json.dumps(cell, allow_nan=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        cell["cell_sha256"] = sha256(cell_path)
        cells.append(cell)
        print(
            json.dumps(
                {
                    "completed_cells": index,
                    "total_cells": len(matrix),
                    "passing_cells": sum(item["pass"] for item in cells),
                    "elapsed_s": time.time() - started,
                }
            ),
            flush=True,
        )

    checkpoint_rows = []
    for checkpoint_id in policy_specs:
        selected = [
            cell
            for cell in cells
            if cell["identity"]["checkpoint_id"] == checkpoint_id
        ]
        checkpoint_rows.append(
            {
                "checkpoint_id": checkpoint_id,
                "step": int(selected[0]["identity"]["step"]),
                "cells": len(selected),
                "passing_cells": sum(cell["pass"] for cell in selected),
                "all_eight_cells_pass": len(selected) == 8
                and all(cell["pass"] for cell in selected),
                "worst_tracking_p95_rad": max_or_none(
                    float(cell["metrics"]["worst_tracking_p95_rad"])
                    for cell in selected
                    if cell["metrics"]["worst_tracking_p95_rad"] is not None
                ),
                "worst_peak_current_a": max_or_none(
                    float(
                        cell["prospective_current_gate"][
                            "worst_peak_current_a"
                        ]
                    )
                    for cell in selected
                    if "worst_peak_current_a"
                    in cell["prospective_current_gate"]
                ),
                "worst_strict_over_2a_run_ticks": max_or_none(
                    int(
                        cell["prospective_current_gate"][
                            "worst_strict_over_2a_run_ticks"
                        ]
                    )
                    for cell in selected
                    if "worst_strict_over_2a_run_ticks"
                    in cell["prospective_current_gate"]
                ),
            }
        )
    persistent_pass = len(checkpoint_rows) == 2 and all(
        row["all_eight_cells_pass"] for row in checkpoint_rows
    )
    decision = {
        "status": (
            "PERSISTENT_RECURRENT_SOURCE_PASS"
            if persistent_pass
            else "REJECT_RECURRENT_SOURCE"
        ),
        "protected_source_selected_for_extension": persistent_pass,
        "hosted_training_authorized": False,
        "next_action": (
            "build a minimal zero-initialized response-conditioned extension "
            "that preserves the recurrent actor exactly"
            if persistent_pass
            else "do not train from this recurrent source; attribute the "
            "failed frozen metrics first"
        ),
    }
    validity = {
        "matrix_16_exact": len(cells) == 16,
        "all_cell_files_written": len(list(cells_root.glob("*.json"))) == 16,
        "cpu_environment_exact": cpu_only,
        "policy_hashes_exact": all(
            cell["policy"]["sha256"]
            == policy_specs[cell["identity"]["checkpoint_id"]]["sha256"]
            for cell in cells
        ),
        "no_runner_exceptions": all(
            not str(cell["simulator"]["status"]).startswith(
                "RUNNER_EXCEPTION_"
            )
            for cell in cells
        ),
        "all_payloads_finite": all(
            math.isfinite(float(cell["identity"]["command_x_m_s"]))
            for cell in cells
        ),
        "old_p95_current_not_used_for_pass_fail": all(
            "current_p95_at_most_0p65"
            not in cell["metrics"].get("checks", {})
            and "current_p95_at_most_0p65"
            not in cell["failure_reasons"]
            for cell in cells
        ),
    }
    failed_validity = sorted(
        name for name, passed in validity.items() if not passed
    )
    cell_manifest = [
        {
            "identity": cell["identity"],
            "pass": cell["pass"],
            "failure_reasons": cell["failure_reasons"],
            "cell_sha256": cell["cell_sha256"],
            "trace_sha256": cell["trace"].get("sha256"),
        }
        for cell in cells
    ]
    finite_metrics = [
        cell["metrics"]
        for cell in cells
        if cell["metrics"].get("worst_tracking_p95_rad") is not None
    ]
    moving = [
        cell["metrics"].get("mean_local_vx_m_s")
        for cell in cells
        if float(cell["identity"]["command_x_m_s"]) > 0.0
        and cell["metrics"].get("mean_local_vx_m_s") is not None
    ]
    summary = {
        "cells": len(cells),
        "passing_cells": sum(cell["pass"] for cell in cells),
        "persistent_both_checkpoint_pass": persistent_pass,
        "failures_by_reason": {
            reason: sum(reason in cell["failure_reasons"] for cell in cells)
            for reason in sorted(
                {
                    reason
                    for cell in cells
                    for reason in cell["failure_reasons"]
                }
            )
        },
        "worst_tracking_p95_rad": (
            max(
                float(item["worst_tracking_p95_rad"])
                for item in finite_metrics
            )
            if finite_metrics
            else None
        ),
        "worst_current_p95_a_diagnostic_only": max(
            (
                float(
                    cell["prospective_current_gate"][
                        "worst_p95_current_a_diagnostic_only"
                    ]
                )
                for cell in cells
                if "worst_p95_current_a_diagnostic_only"
                in cell["prospective_current_gate"]
            ),
            default=None,
        ),
        "worst_peak_current_a": max(
            (
                float(
                    cell["prospective_current_gate"][
                        "worst_peak_current_a"
                    ]
                )
                for cell in cells
                if "worst_peak_current_a"
                in cell["prospective_current_gate"]
            ),
            default=None,
        ),
        "worst_strict_over_2a_run_ticks": max(
            (
                int(
                    cell["prospective_current_gate"][
                        "worst_strict_over_2a_run_ticks"
                    ]
                )
                for cell in cells
                if "worst_strict_over_2a_run_ticks"
                in cell["prospective_current_gate"]
            ),
            default=None,
        ),
        "minimum_moving_mean_vx_m_s": min(moving) if moving else None,
    }
    result = {
        "schema_version": "winner_v109.recurrent_source_result.v1",
        "status": (
            "PASS_WINNER_V109_RECURRENT_SOURCE_SCREEN"
            if not failed_validity
            else "INVALID_WINNER_V109_RECURRENT_SOURCE_SCREEN"
        ),
        "failed_validity_checks": failed_validity,
        "validity_checks": validity,
        "decision": decision,
        "summary": summary,
        "per_checkpoint": checkpoint_rows,
        "cell_manifest_sha256": canonical_sha256(cell_manifest),
        "run_root": str(run_root),
        "wall_seconds": time.time() - started,
        "cpu_environment": {
            "jax_backend": backend,
            "device_platforms": device_platforms,
            "device_strings": [str(device) for device in jax.devices()],
        },
        "input_hashes": {
            "preregistration": sha256(PREREG),
            "reference_features": sha256(REFERENCE),
            "policies": {
                checkpoint_id: sha256(
                    policy_root / spec["filename"]
                )
                for checkpoint_id, spec in policy_specs.items()
            },
        },
        "authority": {
            "protected_source_selected_for_extension": (
                not failed_validity and persistent_pass
            ),
            "minimal_extension_contract_authorized": (
                not failed_validity and persistent_pass
            ),
            "hosted_training_authorized": False,
            "checkpoint_selection_authorized": False,
            "gate5_authorized": False,
            "robot_clearance": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    result = json_finite(result)
    RESULT_JSON.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    RESULT_MD.write_text(
        "# Winner-v109 corrected recurrent-source screen\n\n"
        f"Status: `{result['status']}`\n\n"
        f"Decision: `{decision['status']}`\n\n"
        f"Passing cells: `{summary['passing_cells']}/16`\n\n"
        f"Persistent both-checkpoint pass: "
        f"`{summary['persistent_both_checkpoint_pass']}`\n\n"
        f"Worst tracking p95: `{summary['worst_tracking_p95_rad']}` rad\n\n"
        f"Worst peak current: `{summary['worst_peak_current_a']}` A\n\n"
        "The 0.65 A p95 value is diagnostic only. Pass/fail uses peak <=2.5 A "
        "and fewer than 100 consecutive ticks strictly above 2 A. This screen "
        "cannot authorize hosted training, Gate 5, robot use, torque, or "
        "motion.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "decision": result["decision"],
                "summary": result["summary"],
            }
        ),
        flush=True,
    )
    return result


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--policy-root", type=Path, required=True)
    parser.add_argument("--playground", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = execute(
        policy_root=args.policy_root.resolve(),
        playground=args.playground.resolve(),
        run_root=args.run_root.resolve(),
    )
    return 0 if not result["failed_validity_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
