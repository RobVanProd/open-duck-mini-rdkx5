#!/usr/bin/env python3
"""Run the preregistered protected-policy no-prefix control on CPU."""

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
    REFERENCE,
    json_finite,
    missing_trace_audit,
)
from run_winner_v107_stage_boundary_diagnostic import (  # noqa: E402
    cpu_environment_exact,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v108_prefix_handoff_preregistration.json"
V107 = ANALYSIS / "winner_v107_stage_boundary_result.json"
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
SOURCE = (
    ROOT
    / "artifacts/runtime_handoff/rdkx5_native_20260719/policies"
    / "T2_EQUAL_512000.onnx"
)
RESULT_JSON = ANALYSIS / "winner_v108_prefix_handoff_result.json"
RESULT_MD = ANALYSIS / "WINNER_V108_PREFIX_HANDOFF_RESULT_20260724.md"
PREREG_SHA256 = (
    "ef0dd3b94c8ebb2ce1d3434e153ab454ae8852d2c9d507e708cbfa9a4f3bbcd7"
)
MATRIX_SHA256 = (
    "3d32af63e21da7453685ac582b95e405ec96e6268fb8ece02f1f8acf6d6e49d0"
)
V107_SHA256 = (
    "3f9bd6f9173131dbb17e9eef570831df5a67fc291bee094fe76b61772f8e6f6a"
)
SOURCE_SHA256 = (
    "99d3afce0dfac127816c6327665c35b3c403e005f25cd0a505dfcb37f01304de"
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


def cell_stem(row: Mapping[str, Any]) -> str:
    return (
        f"protected_source_no_prefix_"
        f"x{float(row['command_x_m_s']):.3f}_seed{int(row['seed'])}"
    )


def early_return_cell(
    *,
    row: Mapping[str, Any],
    result: Mapping[str, Any],
    trace_path: Path,
    cpu_only: bool,
) -> dict[str, Any]:
    status = str(result.get("status") or "MISSING_STATUS")
    return {
        "schema_version": "winner_v108.prefix_handoff_cell.v1",
        "status": "HOLD_WINNER_V108_PREFIX_HANDOFF_CELL",
        "pass": False,
        "failure_reasons": [
            f"simulator_early_return_{status}",
            "trace_missing",
        ]
        + ([] if cpu_only else ["cpu_only"]),
        "identity": dict(row),
        "policy": {"path": str(SOURCE), "sha256": sha256(SOURCE)},
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
        "robot_clearance": False,
        "training_or_simulator_reward_selection_weight": 0,
    }


def execute_cell(
    row: Mapping[str, Any],
    prereg: Mapping[str, Any],
    *,
    playground: Path,
    trace_path: Path,
    cpu_only: bool,
) -> dict[str, Any]:
    transport = row["transport"]
    base_row = {
        "condition_group": "NOMINAL",
        "condition_id": "V108_PROTECTED_SOURCE_NO_PREFIX",
        "seed": int(row["seed"]),
        "step": 512_000,
        "plant": row["plant"],
        "command_x_m_s": float(row["command_x_m_s"]),
        "duration_ticks": int(row["duration_ticks"]),
        "configuration": row["configuration"],
        "transport": transport,
    }
    with contextlib.redirect_stdout(io.StringIO()):
        result = run_closed_loop_sim(
            ClosedLoopConfig(
                policy_path=SOURCE,
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
                policy_state_input_names=("previous_action",),
                policy_state_output_names=("previous_action_out",),
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
            result=result,
            trace_path=trace_path,
            cpu_only=cpu_only,
        )

    trace = trace_audit(trace_path)
    readback = readback_checks(base_row, result, prereg)
    _, failures, metrics = classify_cell(base_row, result, trace, readback)
    failures = [reason for reason in failures if reason != "cpu_only"]
    if not cpu_only:
        failures.append("cpu_only")
    failures = sorted(set(failures))
    metrics["checks"]["cpu_only"] = cpu_only
    return {
        "schema_version": "winner_v108.prefix_handoff_cell.v1",
        "status": (
            "PASS_WINNER_V108_PREFIX_HANDOFF_CELL"
            if not failures
            else "HOLD_WINNER_V108_PREFIX_HANDOFF_CELL"
        ),
        "pass": not failures,
        "failure_reasons": failures,
        "identity": dict(row),
        "policy": {"path": str(SOURCE), "sha256": sha256(SOURCE)},
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
        "robot_clearance": False,
        "training_or_simulator_reward_selection_weight": 0,
    }


def select_attribution(
    *,
    all_source_cells_pass: bool,
    graph_equivalence_exact: bool,
    v107_expanded_initial_passing_cells: int,
) -> dict[str, Any]:
    if (
        all_source_cells_pass
        and graph_equivalence_exact
        and v107_expanded_initial_passing_cells == 1
    ):
        return {
            "status": "PREFIX_PHYSICAL_STATE_HANDOFF_ATTRIBUTED",
            "selected_causal_boundary": (
                "CALIBRATION_PREFIX_PHYSICAL_STATE_HANDOFF"
            ),
            "next_action": (
                "preregister a state-reset versus settle/observer-reset split; "
                "do not change policy weights yet"
            ),
        }
    return {
        "status": "BASELINE_CONTROL_DID_NOT_ISOLATE_PREFIX",
        "selected_causal_boundary": "BASELINE_SEED_OR_EVALUATOR_MISMATCH",
        "next_action": (
            "audit the protected-policy evaluator baseline before any "
            "prefix or training change"
        ),
    }


def execute(*, playground: Path, run_root: Path) -> dict[str, Any]:
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise RuntimeError("CUDA_VISIBLE_DEVICES must be empty")
    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("JAX_PLATFORMS must be cpu")
    preregistration = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        sha256(PREREG) != PREREG_SHA256
        or preregistration.get("status")
        != "PREREGISTERED_WINNER_V108_PREFIX_HANDOFF_DIAGNOSTIC"
        or preregistration.get("failed_checks") != []
        or preregistration.get("matrix", {}).get("sha256") != MATRIX_SHA256
        or preregistration.get("authority", {}).get(
            "formal_behavior_cells_authorized"
        )
        != 4
    ):
        raise ValueError("Winner-v108 preregistration is not passing")
    if sha256(V107) != V107_SHA256:
        raise ValueError("Winner-v107 comparator changed")
    if sha256(SOURCE) != SOURCE_SHA256:
        raise ValueError("protected source changed")
    if run_root.exists():
        raise FileExistsError(f"refusing to overwrite V108 run root: {run_root}")
    if RESULT_JSON.exists() or RESULT_MD.exists():
        raise FileExistsError("refusing to overwrite V108 result")
    if not playground.exists():
        raise FileNotFoundError(playground)
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("Winner-v108 execution requires a clean worktree")

    matrix = preregistration["matrix"]["rows"]
    if len(matrix) != 4 or canonical_sha256(matrix) != MATRIX_SHA256:
        raise ValueError("Winner-v108 matrix changed")
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    v107 = json.loads(V107.read_text(encoding="utf-8"))
    v107_initial = next(
        row
        for row in v107["per_checkpoint"]
        if row["id"] == "EXPANDED_INITIAL"
    )

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
        try:
            cell = execute_cell(
                row,
                base_prereg,
                playground=playground,
                trace_path=trace_path,
                cpu_only=cpu_only,
            )
        except Exception as exc:  # fail closed and preserve the one run
            cell = early_return_cell(
                row=row,
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
    all_source_cells_pass = len(cells) == 4 and all(
        cell["pass"] for cell in cells
    )
    attribution = select_attribution(
        all_source_cells_pass=all_source_cells_pass,
        graph_equivalence_exact=bool(
            preregistration["graph_equivalence"]["exact"]
        ),
        v107_expanded_initial_passing_cells=int(
            v107_initial["passing_cells"]
        ),
    )
    validity = {
        "matrix_4_exact": len(cells) == 4,
        "all_cell_files_written": len(list(cells_root.glob("*.json"))) == 4,
        "cpu_environment_exact": cpu_only,
        "source_policy_hash_exact": all(
            cell["policy"]["sha256"] == SOURCE_SHA256 for cell in cells
        ),
        "no_runner_exceptions": all(
            not str(cell["simulator"]["status"]).startswith("RUNNER_EXCEPTION_")
            for cell in cells
        ),
        "all_payloads_finite": all(
            math.isfinite(float(cell["identity"]["command_x_m_s"]))
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
    summary = {
        "cells": len(cells),
        "passing_cells": sum(cell["pass"] for cell in cells),
        "all_four_cells_pass": all_source_cells_pass,
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
        "worst_current_p95_a": (
            max(float(item["worst_current_p95_a"]) for item in finite_metrics)
            if finite_metrics
            else None
        ),
        "minimum_moving_mean_vx_m_s": min(moving) if moving else None,
    }
    result = {
        "schema_version": "winner_v108.prefix_handoff_result.v1",
        "status": (
            "PASS_WINNER_V108_PREFIX_HANDOFF_DIAGNOSTIC"
            if not failed_validity
            else "INVALID_WINNER_V108_PREFIX_HANDOFF_DIAGNOSTIC"
        ),
        "failed_validity_checks": failed_validity,
        "validity_checks": validity,
        "decision": attribution,
        "summary": summary,
        "v107_expanded_initial": v107_initial,
        "graph_equivalence": preregistration["graph_equivalence"],
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
            "v107_result": sha256(V107),
            "protected_source": sha256(SOURCE),
            "reference_features": sha256(REFERENCE),
        },
        "authority": {
            "causal_boundary_selected": (
                not failed_validity
                and attribution["status"]
                == "PREFIX_PHYSICAL_STATE_HANDOFF_ATTRIBUTED"
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
        "# Winner-v108 calibration-prefix handoff result\n\n"
        f"Status: `{result['status']}`\n\n"
        f"Decision: `{attribution['status']}`\n\n"
        f"Selected causal boundary: "
        f"`{attribution['selected_causal_boundary']}`\n\n"
        f"Protected no-prefix cells: `{summary['passing_cells']}/4`\n\n"
        f"Worst tracking p95: `{summary['worst_tracking_p95_rad']}` rad\n\n"
        f"Worst current p95: `{summary['worst_current_p95_a']}` A\n\n"
        f"Minimum moving mean vx: `{summary['minimum_moving_mean_vx_m_s']}` "
        "m/s\n\n"
        "This diagnostic attributes one preoptimizer integration boundary. "
        "It cannot select a deployment checkpoint, authorize hosted training, "
        "open Gate 5, or clear the policy for robot use.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "decision": result["decision"],
                "summary": result["summary"],
            }
        )
    )
    return result


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--playground", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = execute(
        playground=args.playground.resolve(),
        run_root=args.run_root.resolve(),
    )
    return 0 if not result["failed_validity_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
