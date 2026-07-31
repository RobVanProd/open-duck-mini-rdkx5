#!/usr/bin/env python3
"""Run the frozen 16-cell V126 zero-credit exact-oracle screen on CPU."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import jax
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from closed_loop_sim_eval_v126 import (  # noqa: E402
    ClosedLoopConfig,
    run_closed_loop_sim,
)
from run_winner_v103_response_conditioned_behavior import (  # noqa: E402
    REFERENCE,
    json_finite,
    missing_trace_audit,
)
from run_winner_v109_recurrent_source_screen import (  # noqa: E402
    current_metrics_from_trace,
)
from run_winner_v110_pitch_guard_behavior import (  # noqa: E402
    torque_metrics_from_trace,
)
from run_winner_v3_variable_configuration_behavior import (  # noqa: E402
    actuator_fit,
    classify_cell,
    readback_checks,
    trace_audit,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v126_exact_oracle_behavior_preregistration.json"
PREREG_SHA256 = (
    "c869e74e211463d7ff5d932f879f47779d9f326e98d52744424c93659d4091bc"
)
ISOLATION_AMENDMENT = (
    ANALYSIS / "winner_v126_evaluator_isolation_amendment.json"
)
ISOLATION_AMENDMENT_SHA256 = (
    "c79a6c332bddf1e581f7095ce256f82351f17cc2feae231af487152368959238"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
OUTPUT = ANALYSIS / "winner_v126_exact_oracle_behavior_result.json"
MARKDOWN = ANALYSIS / "WINNER_V126_EXACT_ORACLE_BEHAVIOR_RESULT_20260724.md"
TORQUE_LIMIT_NM = 1.91229675


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


def cell_stem(row: Mapping[str, Any]) -> str:
    return (
        f"{str(row['checkpoint_id']).lower()}_"
        f"{str(row['plant']).lower()}_"
        f"x{float(row['command_x_m_s']):.3f}_"
        f"seed{int(row['seed'])}"
    )


def oracle_trace_audit(
    trace_path: Path, mode: Mapping[str, Any]
) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in trace_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    summaries = mode.get("exact_torque_oracle") or {}
    projection_rows = [
        row["exact_torque_oracle"]
        for row in rows
        if isinstance(row.get("exact_torque_oracle"), dict)
    ]
    matured = [
        item
        for row in rows
        for item in row.get("exact_torque_oracle_matured_predictions", [])
    ]
    clip_values = [
        float(item.get("clip_linf", 0.0)) for item in projection_rows
    ]
    projected_joints = [
        int(joint)
        for item in projection_rows
        for joint in item.get("projected_joint_indices", [])
    ]
    empty_joints = [
        int(joint)
        for item in projection_rows
        for joint in item.get("empty_intersection_joint_indices", [])
    ]
    prediction_errors = [
        float(item["prediction_error_nm"]) for item in matured
    ]
    return {
        "rows": len(rows),
        "projection_rows": len(projection_rows),
        "matured_predictions": len(matured),
        "projected_ticks": sum(value > 0.0 for value in clip_values),
        "projected_joint_events": len(projected_joints),
        "empty_intersection_events": len(empty_joints),
        "projected_joint_indices": sorted(set(projected_joints)),
        "empty_intersection_joint_indices": sorted(set(empty_joints)),
        "clip_linf_max": max(clip_values, default=0.0),
        "clip_linf_mean": (
            float(np.mean(clip_values)) if clip_values else 0.0
        ),
        "prediction_error_nm_max": max(prediction_errors, default=0.0),
        "summary": summaries,
        "checks": {
            "all_ticks_have_oracle_record": len(projection_rows) == len(rows),
            "prediction_exact": bool(summaries.get("prediction_exact")),
            "only_empty_or_prehistory_residuals": bool(
                summaries.get("only_empty_or_prehistory_residuals")
            ),
            "zero_nonempty_residual_violations": int(
                summaries.get("nonempty_residual_violations", -1)
            )
            == 0,
            "zero_prediction_mismatches": int(
                summaries.get("prediction_mismatches", -1)
            )
            == 0,
            "zero_unscheduled_residual_violations": int(
                summaries.get("unscheduled_residual_violations", -1)
            )
            == 0,
        },
    }


def execute_cell(
    *,
    row: Mapping[str, Any],
    base_prereg: Mapping[str, Any],
    policy: Path,
    playground: Path,
    trace_path: Path,
    action_delta: tuple[float, ...],
    schedule_ticks: tuple[int, ...],
    cpu_only: bool,
) -> dict[str, Any]:
    with contextlib.redirect_stdout(io.StringIO()):
        result = run_closed_loop_sim(
            ClosedLoopConfig(
                policy_path=policy,
                fit=actuator_fit(base_prereg, str(row["plant"])),
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
                winner_v3_sensor_noise_scales=None,
                winner_v3_native_quantization=False,
                winner_v3_additional_action_delay_ticks=0,
                winner_v3_imu_delay_ticks=0,
                winner_v3_home_relative_actuator_gain=True,
                exact_torque_oracle_enabled=True,
                exact_torque_oracle_limit_nm=TORQUE_LIMIT_NM,
                exact_torque_oracle_guard_rad=0.165,
                exact_torque_oracle_action_delta=action_delta,
                exact_torque_oracle_force_tolerance_nm=5.0e-6,
                exact_torque_oracle_monotonicity_tolerance_nm=5.0e-6,
                exact_torque_oracle_grid_points=9,
                exact_torque_oracle_bisection_iterations=32,
                exact_torque_oracle_maximum_coordinate_passes=14,
                exact_torque_oracle_schedule_ticks=schedule_ticks,
            )
        )
    if result.get("env") is None or not trace_path.is_file():
        return {
            "schema_version": "winner_v126.exact_oracle_behavior_cell.v1",
            "status": "HOLD_WINNER_V126_EXACT_ORACLE_BEHAVIOR_CELL",
            "pass": False,
            "failure_reasons": ["simulator_or_trace_missing"],
            "identity": dict(row),
            "policy": {"path": str(policy), "sha256": sha256(policy)},
            "simulator": {
                "status": result.get("status"),
                "error": result.get("error"),
                "tick": result.get("tick"),
            },
            "trace": (
                trace_audit(trace_path)
                if trace_path.is_file()
                else missing_trace_audit(trace_path)
            ),
            "robot_clearance": False,
        }
    trace = trace_audit(trace_path)
    readback = readback_checks(row, result, base_prereg)
    _, failures, metrics = classify_cell(row, result, trace, readback)
    failures = [
        reason
        for reason in failures
        if reason not in {"current_p95_at_most_0p65", "cpu_only"}
    ]
    metrics["checks"].pop("current_p95_at_most_0p65", None)
    current = current_metrics_from_trace(trace_path)
    torque = torque_metrics_from_trace(trace_path)
    for name, passed in current["checks"].items():
        metrics["checks"][name] = passed
        if not passed:
            failures.append(name)
    metrics["checks"]["torque_peak_at_most_1p91229675_nm"] = torque[
        "check"
    ]
    if not torque["check"]:
        failures.append("torque_peak_at_most_1p91229675_nm")
    metrics["checks"]["cpu_only"] = cpu_only
    if not cpu_only:
        failures.append("cpu_only")
    mode = ((result.get("modes") or {}).get("fitted") or {})
    oracle = oracle_trace_audit(trace_path, mode)
    for name, passed in oracle["checks"].items():
        metrics["checks"][f"oracle_{name}"] = passed
        if not passed:
            failures.append(f"oracle_{name}")
    # Fable's frozen screen permits only torque/current peaks whose source
    # decision was explicitly classified empty (or finite-horizon prehistory).
    # Dwell and every behavioral criterion remain unchanged.
    provenance_clean = (
        oracle["checks"]["zero_nonempty_residual_violations"]
        and oracle["checks"]["zero_prediction_mismatches"]
        and oracle["checks"]["zero_unscheduled_residual_violations"]
    )
    permitted_peak_failures = {
        "current_peak_at_most_2p5",
        "torque_peak_at_most_1p91229675_nm",
    }
    if provenance_clean:
        failures = [
            reason
            for reason in failures
            if reason not in permitted_peak_failures
        ]
    failures = sorted(set(failures))
    return {
        "schema_version": "winner_v126.exact_oracle_behavior_cell.v1",
        "status": (
            "PASS_WINNER_V126_EXACT_ORACLE_BEHAVIOR_CELL"
            if not failures
            else "HOLD_WINNER_V126_EXACT_ORACLE_BEHAVIOR_CELL"
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
        "torque_gate": torque,
        "oracle": oracle,
        "trace": trace,
        "readback_checks": readback,
        "model_readback": (result.get("env") or {}).get(
            "winner_v3_configuration_readback"
        ),
        "training_or_simulator_reward_selection_weight": 0,
        "robot_clearance": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    if run_root.exists():
        raise FileExistsError(f"refusing to overwrite V126 screen: {run_root}")
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite V126 behavior result")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        sha256(PREREG) != PREREG_SHA256
        or prereg.get("status")
        != "PREREGISTERED_WINNER_V126_EXACT_ORACLE_BEHAVIOR"
        or prereg.get("authority", {}).get("formal_screen_cells") != 16
    ):
        raise ValueError("V126 behavior preregistration changed")
    isolation_amendment = json.loads(
        ISOLATION_AMENDMENT.read_text(encoding="utf-8")
    )
    if (
        sha256(ISOLATION_AMENDMENT) != ISOLATION_AMENDMENT_SHA256
        or isolation_amendment.get("status")
        != "PASS_WINNER_V126_EVALUATOR_ISOLATION_AMENDMENT"
        or not all(isolation_amendment.get("checks", {}).values())
    ):
        raise ValueError("V126 evaluator-isolation amendment changed or failed")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("V126 behavior execution requires a clean worktree")
    matrix = prereg["matrix"]["rows"]
    if (
        len(matrix) != 16
        or canonical_sha256(matrix) != prereg["matrix"]["sha256"]
    ):
        raise ValueError("V126 formal matrix changed")
    policy_root = Path(prereg["external_inputs"]["policy_root"])
    playground = Path(prereg["external_inputs"]["playground"])
    policies = {item["id"]: item for item in prereg["policies"]}
    for item in policies.values():
        path = policy_root / item["filename"]
        if sha256(path) != item["sha256"]:
            raise ValueError(f"V126 policy changed: {item['id']}")
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    action_delta = tuple(
        float(value) for value in prereg["oracle"]["action_delta"]
    )
    cells_root = run_root / "cells"
    traces_root = run_root / "traces"
    cells_root.mkdir(parents=True)
    traces_root.mkdir(parents=True)
    cpu_only = jax.default_backend() == "cpu" and all(
        device.platform == "cpu" for device in jax.devices()
    )
    started = time.time()
    cells: list[dict[str, Any]] = []
    for index, row in enumerate(matrix, start=1):
        stem = cell_stem(row)
        trace_path = traces_root / f"{stem}.jsonl"
        policy = policy_root / policies[row["checkpoint_id"]]["filename"]
        try:
            cell = execute_cell(
                row=row,
                base_prereg=base_prereg,
                policy=policy,
                playground=playground,
                trace_path=trace_path,
                action_delta=action_delta,
                schedule_ticks=tuple(
                    int(tick) for tick in row["oracle_schedule_ticks"]
                ),
                cpu_only=cpu_only,
            )
        except Exception as exc:
            cell = {
                "schema_version": (
                    "winner_v126.exact_oracle_behavior_cell.v1"
                ),
                "status": "HOLD_WINNER_V126_EXACT_ORACLE_BEHAVIOR_CELL",
                "pass": False,
                "failure_reasons": [
                    f"runner_exception_{type(exc).__name__}"
                ],
                "identity": dict(row),
                "policy": {"path": str(policy), "sha256": sha256(policy)},
                "simulator": {
                    "status": f"RUNNER_EXCEPTION_{type(exc).__name__}",
                    "error": str(exc),
                },
                "trace": (
                    trace_audit(trace_path)
                    if trace_path.is_file()
                    else missing_trace_audit(trace_path)
                ),
                "robot_clearance": False,
            }
        cell = json_finite(cell)
        cell_path = cells_root / f"{stem}.json"
        cell_path.write_text(
            json.dumps(cell, allow_nan=False, indent=2, sort_keys=True)
            + "\n",
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
                    "latest": {
                        "checkpoint_id": row["checkpoint_id"],
                        "plant": row["plant"],
                        "command_x_m_s": row["command_x_m_s"],
                        "pass": cell["pass"],
                        "failures": cell["failure_reasons"],
                        "oracle": cell.get("oracle"),
                    },
                }
            ),
            flush=True,
        )
    half_id = prereg["decision"]["required_teacher_checkpoint_id"]
    half_cells = [
        cell
        for cell in cells
        if cell["identity"]["checkpoint_id"] == half_id
    ]
    valid = (
        len(cells) == 16
        and len(half_cells) == 8
        and all("runner_exception" not in " ".join(cell["failure_reasons"]) for cell in cells)
    )
    teacher_pass = valid and all(cell["pass"] for cell in half_cells)
    projection_cells = [
        cell
        for cell in cells
        if int((cell.get("oracle") or {}).get("projected_joint_events", 0))
        > 0
    ]
    summary = {
        "cells": len(cells),
        "passing_cells": sum(cell["pass"] for cell in cells),
        "half_cells": len(half_cells),
        "half_passing_cells": sum(cell["pass"] for cell in half_cells),
        "teacher_half_all_eight_pass": teacher_pass,
        "projection_cells": len(projection_cells),
        "projected_joint_events": sum(
            int((cell.get("oracle") or {}).get("projected_joint_events", 0))
            for cell in cells
        ),
        "empty_intersection_events": sum(
            int((cell.get("oracle") or {}).get("empty_intersection_events", 0))
            for cell in cells
        ),
        "prediction_mismatches": sum(
            int(
                ((cell.get("oracle") or {}).get("summary") or {}).get(
                    "prediction_mismatches", 0
                )
            )
            for cell in cells
        ),
        "nonempty_residual_violations": sum(
            int(
                ((cell.get("oracle") or {}).get("summary") or {}).get(
                    "nonempty_residual_violations", 0
                )
            )
            for cell in cells
        ),
        "unscheduled_residual_violations": sum(
            int(
                ((cell.get("oracle") or {}).get("summary") or {}).get(
                    "unscheduled_residual_violations", 0
                )
            )
            for cell in cells
        ),
    }
    payload = {
        "schema_version": "winner_v126.exact_oracle_behavior_result.v1",
        "status": (
            "PASS_WINNER_V126_EXACT_ORACLE_BEHAVIOR_VALID_RESULT"
            if valid
            else "INVALID_WINNER_V126_EXACT_ORACLE_BEHAVIOR_RESULT"
        ),
        "decision": {
            "status": (
                "EARN_ONE_V126_CONSTRAINED_CONTINUATION_CPU_CONTRACT"
                if teacher_pass
                else "CLOSE_V126_CONSTRAINED_CONTINUATION_WITHOUT_HOSTED_RUN"
            ),
            "teacher_half_all_eight_pass": teacher_pass,
        },
        "summary": summary,
        "cells": cells,
        "wall_seconds": time.time() - started,
        "run_root": str(run_root),
        "input_hashes": {
            "preregistration": sha256(PREREG),
            "evaluator_isolation_amendment": sha256(ISOLATION_AMENDMENT),
            "runner": sha256(Path(__file__).resolve()),
            "projector": sha256(ROOT / "tools/exact_torque_oracle.py"),
            "evaluator": sha256(ROOT / "tools/closed_loop_sim_eval_v126.py"),
        },
        "authority": {
            "constrained_continuation_cpu_contract": teacher_pass,
            "training": False,
            "hosted_or_colab": False,
            "gate5": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v126 exact-oracle behavior result\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Decision: `{payload['decision']['status']}`\n\n"
        f"Passing cells: `{summary['passing_cells']}/16`.\n\n"
        f"V121-half teacher cells: `{summary['half_passing_cells']}/8`.\n\n"
        f"Projected joint events: `{summary['projected_joint_events']}`.\n\n"
        f"Prediction mismatches: `{summary['prediction_mismatches']}`.\n\n"
        "A passing teacher authorizes only the separately tested constrained-"
        "continuation CPU contract. It does not authorize hosted training, "
        "Gate 5, RDK-X5, robot, torque, or motion.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "decision": payload["decision"],
                "summary": summary,
            }
        ),
        flush=True,
    )
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
