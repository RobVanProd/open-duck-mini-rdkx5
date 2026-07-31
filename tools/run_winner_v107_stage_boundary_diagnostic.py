#!/usr/bin/env python3
"""Run the preregistered V105 stage-boundary diagnostic on CPU."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Iterable, Mapping

import jax


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
    CALIBRATOR_SHA256,
    REFERENCE,
    json_finite,
    missing_trace_audit,
    response_trace_audit,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v107_stage_boundary_preregistration.json"
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
RESULT_JSON = ANALYSIS / "winner_v107_stage_boundary_result.json"
RESULT_MD = ANALYSIS / "WINNER_V107_STAGE_BOUNDARY_RESULT_20260724.md"
PREREG_SHA256 = (
    "740fb79bda4be79e2d1d7739b917035bdb4c326f49142bd975fc1acdbf24eec8"
)
MATRIX_SHA256 = (
    "0ee5b189aaba40c70e4f34b4aec00118ac5923536fe78bf56c61c085bed3704d"
)


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()


def cpu_environment_exact(backend: str, platforms: Iterable[str]) -> bool:
    observed = list(platforms)
    return backend == "cpu" and bool(observed) and all(
        platform == "cpu" for platform in observed
    )


def stage_decision(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    ordered = sorted(
        rows, key=lambda row: int(row["cumulative_optimizer_steps"])
    )
    passing = [row for row in ordered if row["all_four_cells_pass"]]
    if not ordered[0]["all_four_cells_pass"]:
        return {
            "status": "EXPANDED_INITIAL_FAILED",
            "first_passing_checkpoint": None,
            "first_failing_checkpoint_after_pass": ordered[0]["id"],
            "selected_causal_boundary": (
                "EXPANSION_EXPORT_OR_CALIBRATION_PREFIX_INTEGRATION"
            ),
        }
    for index, row in enumerate(ordered[1:], start=1):
        if not row["all_four_cells_pass"]:
            return {
                "status": "FIRST_TRAINING_TRANSITION_LOCATED",
                "first_passing_checkpoint": ordered[index - 1]["id"],
                "first_failing_checkpoint_after_pass": row["id"],
                "selected_causal_boundary": (
                    f"{ordered[index - 1]['id']}_TO_{row['id']}"
                ),
            }
    return {
        "status": "NO_NOMINAL_COLLAPSE_AT_FROZEN_BOUNDARIES",
        "first_passing_checkpoint": passing[0]["id"] if passing else None,
        "first_failing_checkpoint_after_pass": None,
        "selected_causal_boundary": None,
    }


def cell_stem(row: Mapping[str, Any]) -> str:
    return (
        f"{str(row['checkpoint_id']).lower()}_"
        f"{str(row['plant']).lower()}_"
        f"x{float(row['command_x_m_s']):.3f}_"
        f"seed{int(row['seed'])}"
    )


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
        "schema_version": "winner_v107.stage_boundary_cell.v1",
        "status": "HOLD_WINNER_V107_STAGE_BOUNDARY_CELL",
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
        "readback_checks": {
            "environment_readback_present": result.get("env") is not None
        },
        "trace": missing_trace_audit(trace_path),
        "response_contract": {
            "checks": {},
            "failed_checks": ["trace_missing"],
            "pass": False,
            "context_sha256": None,
            "trace_rows": 0,
        },
        "robot_clearance": False,
        "training_or_simulator_reward_selection_weight": 0,
    }


def execute_cell(
    row: Mapping[str, Any],
    prereg: Mapping[str, Any],
    *,
    policy: Path,
    playground: Path,
    calibrator: Path,
    trace_path: Path,
    cpu_only: bool,
) -> dict[str, Any]:
    transport = row["transport"]
    base_row = {
        "condition_group": "NOMINAL",
        "condition_id": f"V107_{row['checkpoint_id']}",
        "seed": int(row["seed"]),
        "step": int(row["cumulative_optimizer_steps"]),
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
                policy_context_input_name="calibration_context",
                policy_graph_authoritative_output=True,
                response_calibrator_path=calibrator,
                response_calibrator_sha256=CALIBRATOR_SHA256,
                response_calibration_ticks=250,
                response_home_return_ticks=250,
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
    response = response_trace_audit(trace_path, result)
    readback = readback_checks(base_row, result, prereg)
    _, failures, metrics = classify_cell(base_row, result, trace, readback)
    failures = [reason for reason in failures if reason != "cpu_only"]
    if not cpu_only:
        failures.append("cpu_only")
    if not response["pass"]:
        failures.extend(
            f"response_{name}" for name in response["failed_checks"]
        )
    failures = sorted(set(failures))
    metrics["checks"]["cpu_only"] = cpu_only
    metrics["response_contract"] = response
    return {
        "schema_version": "winner_v107.stage_boundary_cell.v1",
        "status": (
            "PASS_WINNER_V107_STAGE_BOUNDARY_CELL"
            if not failures
            else "HOLD_WINNER_V107_STAGE_BOUNDARY_CELL"
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
        "readback_checks": readback,
        "model_readback": (result.get("env") or {}).get(
            "winner_v3_configuration_readback"
        ),
        "candidate_gate": result.get("candidate_gate"),
        "trace": trace,
        "response_contract": response,
        "robot_clearance": False,
        "training_or_simulator_reward_selection_weight": 0,
    }


def execute(
    *,
    artifact_root: Path,
    playground: Path,
    calibrator: Path,
    run_root: Path,
) -> dict[str, Any]:
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise RuntimeError("CUDA_VISIBLE_DEVICES must be empty")
    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("JAX_PLATFORMS must be cpu")
    if sha256(PREREG) != PREREG_SHA256:
        raise ValueError("Winner-v107 preregistration changed")
    preregistration = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        preregistration.get("status")
        != "PREREGISTERED_WINNER_V107_STAGE_BOUNDARY_DIAGNOSTIC"
        or preregistration.get("failed_checks") != []
        or preregistration.get("matrix", {}).get("sha256") != MATRIX_SHA256
        or preregistration.get("authority", {}).get(
            "formal_behavior_cells_authorized"
        )
        != 20
    ):
        raise ValueError("Winner-v107 preregistration is not passing")
    if run_root.exists():
        raise FileExistsError(f"refusing to overwrite V107 run root: {run_root}")
    if RESULT_JSON.exists() or RESULT_MD.exists():
        raise FileExistsError("refusing to overwrite V107 result")
    if sha256(calibrator) != CALIBRATOR_SHA256:
        raise ValueError("Winner-v107 calibrator changed")
    if not playground.exists():
        raise FileNotFoundError(playground)
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("Winner-v107 execution requires a clean worktree")

    checkpoints = {
        row["id"]: row for row in preregistration["checkpoints"]
    }
    for row in checkpoints.values():
        path = artifact_root / row["relative_path"]
        if sha256(path) != row["sha256"]:
            raise ValueError(f"checkpoint changed: {row['id']}")
    matrix = preregistration["matrix"]["rows"]
    if len(matrix) != 20 or canonical_sha256(matrix) != MATRIX_SHA256:
        raise ValueError("Winner-v107 matrix changed")

    cells_root = run_root / "cells"
    traces_root = run_root / "traces"
    cells_root.mkdir(parents=True)
    traces_root.mkdir(parents=True)
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    backend = jax.default_backend()
    device_platforms = [device.platform for device in jax.devices()]
    cpu_only = cpu_environment_exact(backend, device_platforms)
    started = time.time()
    cells: list[dict[str, Any]] = []
    for index, matrix_row in enumerate(matrix, start=1):
        checkpoint = checkpoints[matrix_row["checkpoint_id"]]
        row = {
            **matrix_row,
            "relative_path": checkpoint["relative_path"],
            "aliases": checkpoint["aliases"],
            "cumulative_optimizer_steps": checkpoint[
                "cumulative_optimizer_steps"
            ],
        }
        stem = cell_stem(row)
        trace_path = traces_root / f"{stem}.jsonl"
        try:
            cell = execute_cell(
                row,
                base_prereg,
                policy=artifact_root / checkpoint["relative_path"],
                playground=playground,
                calibrator=calibrator,
                trace_path=trace_path,
                cpu_only=cpu_only,
            )
        except Exception as exc:  # fail closed and preserve the one run
            cell = early_return_cell(
                row=row,
                policy=artifact_root / checkpoint["relative_path"],
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

    per_checkpoint = []
    for checkpoint in preregistration["checkpoints"]:
        subset = [
            cell
            for cell in cells
            if cell["identity"]["checkpoint_id"] == checkpoint["id"]
        ]
        finite_metrics = [
            cell["metrics"]
            for cell in subset
            if cell["metrics"].get("worst_tracking_p95_rad") is not None
        ]
        moving = [
            cell["metrics"].get("mean_local_vx_m_s")
            for cell in subset
            if float(cell["identity"]["command_x_m_s"]) > 0.0
            and cell["metrics"].get("mean_local_vx_m_s") is not None
        ]
        per_checkpoint.append(
            {
                "id": checkpoint["id"],
                "aliases": checkpoint["aliases"],
                "sha256": checkpoint["sha256"],
                "cumulative_optimizer_steps": checkpoint[
                    "cumulative_optimizer_steps"
                ],
                "cells": len(subset),
                "passing_cells": sum(cell["pass"] for cell in subset),
                "all_four_cells_pass": len(subset) == 4
                and all(cell["pass"] for cell in subset),
                "failures_by_reason": {
                    reason: sum(
                        reason in cell["failure_reasons"] for cell in subset
                    )
                    for reason in sorted(
                        {
                            reason
                            for cell in subset
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
                "worst_current_p95_a": (
                    max(
                        float(item["worst_current_p95_a"])
                        for item in finite_metrics
                    )
                    if finite_metrics
                    else None
                ),
                "minimum_moving_mean_vx_m_s": min(moving) if moving else None,
            }
        )

    validity = {
        "matrix_20_exact": len(cells) == 20,
        "all_cell_files_written": len(list(cells_root.glob("*.json"))) == 20,
        "cpu_environment_exact": cpu_only,
        "all_policy_hashes_exact": all(
            cell["policy"]["sha256"]
            == checkpoints[cell["identity"]["checkpoint_id"]]["sha256"]
            for cell in cells
        ),
        "no_runner_exceptions": all(
            not str(cell["simulator"]["status"]).startswith("RUNNER_EXCEPTION_")
            for cell in cells
        ),
        "all_payloads_finite": all(
            math.isfinite(float(value))
            for cell in cells
            for value in [cell["identity"]["command_x_m_s"]]
        ),
    }
    failed_validity = sorted(
        name for name, passed in validity.items() if not passed
    )
    decision = stage_decision(per_checkpoint)
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
    result = {
        "schema_version": "winner_v107.stage_boundary_result.v1",
        "status": (
            "PASS_WINNER_V107_STAGE_BOUNDARY_DIAGNOSTIC"
            if not failed_validity
            else "INVALID_WINNER_V107_STAGE_BOUNDARY_DIAGNOSTIC"
        ),
        "failed_validity_checks": failed_validity,
        "validity_checks": validity,
        "decision": decision,
        "cells": len(cells),
        "passing_cells": sum(cell["pass"] for cell in cells),
        "per_checkpoint": per_checkpoint,
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
            "calibrator": sha256(calibrator),
            "reference_features": sha256(REFERENCE),
        },
        "authority": {
            "causal_boundary_selected": (
                not failed_validity
                and decision["selected_causal_boundary"] is not None
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
    lines = [
        "# Winner-v107 stage-boundary result",
        "",
        f"Status: `{result['status']}`",
        f"Decision: `{decision['status']}`",
        f"Selected causal boundary: `{decision['selected_causal_boundary']}`",
        "",
        "| checkpoint | cells | pass | all pass | worst tracking | "
        "worst current | minimum moving vx |",
        "|---|---:|---:|---|---:|---:|---:|",
    ]
    for row in per_checkpoint:
        lines.append(
            f"| {row['id']} | {row['cells']} | {row['passing_cells']} | "
            f"`{row['all_four_cells_pass']}` | "
            f"{row['worst_tracking_p95_rad']} | {row['worst_current_p95_a']} | "
            f"{row['minimum_moving_mean_vx_m_s']} |"
        )
    lines.extend(
        [
            "",
            "This diagnostic localizes a causal boundary only. It cannot select "
            "a deployment checkpoint, authorize training, open Gate 5, or clear "
            "the policy for any robot action.",
            "",
        ]
    )
    RESULT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "decision": result["decision"],
            }
        )
    )
    return result


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--playground", type=Path, required=True)
    parser.add_argument("--calibrator", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = execute(
        artifact_root=args.artifact_root.resolve(),
        playground=args.playground.resolve(),
        calibrator=args.calibrator.resolve(),
        run_root=args.run_root.resolve(),
    )
    return 0 if not result["failed_validity_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
