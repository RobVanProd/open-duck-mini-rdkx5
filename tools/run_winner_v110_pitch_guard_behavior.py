#!/usr/bin/env python3
"""Run the preregistered G3-repaired recurrent behavior screen on CPU."""

from __future__ import annotations

import argparse
import hashlib
import json
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

from run_winner_v103_response_conditioned_behavior import (  # noqa: E402
    REFERENCE,
    json_finite,
)
from run_winner_v107_stage_boundary_diagnostic import (  # noqa: E402
    cpu_environment_exact,
)
from run_winner_v109_recurrent_source_screen import (  # noqa: E402
    execute_cell as execute_v109_cell,
    max_or_none,
    sha256,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v110_pitch_guard_behavior_preregistration.json"
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
RESULT_JSON = ANALYSIS / "winner_v110_pitch_guard_behavior_result.json"
RESULT_MD = ANALYSIS / "WINNER_V110_PITCH_GUARD_BEHAVIOR_RESULT_20260724.md"
PREREG_SHA256 = (
    "7698a551fa88cf1b0ca09503f383242e8735ce30436c189876bf4bde4b11b6d0"
)
PREREG_STATUS = "PREREGISTERED_WINNER_V110_PITCH_GUARD_BEHAVIOR"
MATRIX_SHA256 = (
    "4297e953d16298f62159d7d3b33dc358f0813dd8f3d0d45d10c6963f4ba1ab3b"
)
PEAK_TORQUE_MAX_NM = 1.91229675


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


def torque_metrics_from_trace(trace_path: Path) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in trace_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    force = np.abs(
        np.asarray([row["actuator_force_nm"] for row in rows], dtype=float)
    )
    if force.ndim != 2 or force.shape[1] != 14 or force.shape[0] == 0:
        raise ValueError("actuator force trace must have shape [ticks, 14]")
    if not np.all(np.isfinite(force)):
        raise ValueError("actuator force trace must be finite")
    peak = np.max(force, axis=0)
    passed = bool(np.all(peak <= PEAK_TORQUE_MAX_NM))
    return {
        "peak_torque_nm_by_joint": peak.tolist(),
        "worst_peak_torque_nm": float(np.max(peak)),
        "limit_nm": PEAK_TORQUE_MAX_NM,
        "check": passed,
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
    cell = execute_v109_cell(
        row,
        prereg,
        policy=policy,
        playground=playground,
        trace_path=trace_path,
        cpu_only=cpu_only,
    )
    cell["schema_version"] = "winner_v110.pitch_guard_behavior_cell.v1"
    if not trace_path.exists() or cell["metrics"].get("samples") != 600:
        cell["status"] = "HOLD_WINNER_V110_PITCH_GUARD_BEHAVIOR_CELL"
        return cell
    torque = torque_metrics_from_trace(trace_path)
    cell["prospective_current_gate"]["peak_torque_nm_by_joint"] = torque[
        "peak_torque_nm_by_joint"
    ]
    cell["prospective_current_gate"]["worst_peak_torque_nm"] = torque[
        "worst_peak_torque_nm"
    ]
    cell["prospective_current_gate"]["peak_torque_limit_nm"] = torque[
        "limit_nm"
    ]
    cell["prospective_current_gate"]["checks"][
        "torque_peak_at_most_1p91229675_nm"
    ] = torque["check"]
    cell["prospective_current_gate"]["pass"] = bool(
        cell["prospective_current_gate"]["pass"] and torque["check"]
    )
    cell["metrics"]["checks"][
        "torque_peak_at_most_1p91229675_nm"
    ] = torque["check"]
    failures = set(cell["failure_reasons"])
    if not torque["check"]:
        failures.add("torque_peak_at_most_1p91229675_nm")
    cell["failure_reasons"] = sorted(failures)
    cell["pass"] = not cell["failure_reasons"]
    cell["status"] = (
        "PASS_WINNER_V110_PITCH_GUARD_BEHAVIOR_CELL"
        if cell["pass"]
        else "HOLD_WINNER_V110_PITCH_GUARD_BEHAVIOR_CELL"
    )
    return cell


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
        != PREREG_STATUS
        or preregistration.get("failed_checks") != []
        or preregistration.get("matrix", {}).get("sha256") != MATRIX_SHA256
        or preregistration.get("authority", {}).get(
            "formal_behavior_cells_authorized"
        )
        != 16
    ):
        raise ValueError("Winner-v110 preregistration is not passing")
    if run_root.exists():
        raise FileExistsError(f"refusing to overwrite V110 run root: {run_root}")
    if RESULT_JSON.exists() or RESULT_MD.exists():
        raise FileExistsError("refusing to overwrite V110 result")
    if not playground.exists():
        raise FileNotFoundError(playground)
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("Winner-v110 execution requires a clean worktree")

    matrix = preregistration["matrix"]["rows"]
    if len(matrix) != 16 or canonical_sha256(matrix) != MATRIX_SHA256:
        raise ValueError("Winner-v110 matrix changed")
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
        spec = policy_specs[row["checkpoint_id"]]
        policy = policy_root / spec["filename"]
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
            cell = {
                "schema_version": "winner_v110.pitch_guard_behavior_cell.v1",
                "status": "HOLD_WINNER_V110_PITCH_GUARD_BEHAVIOR_CELL",
                "pass": False,
                "failure_reasons": [
                    f"runner_exception_{type(exc).__name__}"
                ],
                "identity": dict(row),
                "policy": {
                    "path": str(policy),
                    "sha256": sha256(policy),
                },
                "simulator": {
                    "status": f"RUNNER_EXCEPTION_{type(exc).__name__}",
                    "error": str(exc),
                },
                "metrics": {
                    "samples": 0,
                    "worst_tracking_p95_rad": None,
                    "mean_local_vx_m_s": None,
                },
                "prospective_current_gate": {},
                "trace": {
                    "path": str(trace_path),
                    "sha256": None,
                    "rows": 0,
                },
                "robot_clearance": False,
            }
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
                    if cell["metrics"].get("worst_tracking_p95_rad") is not None
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
                "worst_peak_torque_nm": max_or_none(
                    float(
                        cell["prospective_current_gate"][
                            "worst_peak_torque_nm"
                        ]
                    )
                    for cell in selected
                    if "worst_peak_torque_nm"
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
            "SELECT_G3_REPAIRED_RECURRENT_SOURCE"
            if persistent_pass
            else "REJECT_G3_REPAIR"
        ),
        "protected_source_selected_for_extension": persistent_pass,
        "next_action": (
            "contract the minimal response-conditioned extension around the "
            "G3-repaired recurrent actor"
            if persistent_pass
            else "attribute the frozen failure before any continuation"
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
        "complete_manufacturer_gate_reported": all(
            "current_peak_at_most_2p5"
            in cell["metrics"].get("checks", {})
            and "torque_peak_at_most_1p91229675_nm"
            in cell["metrics"].get("checks", {})
            and "overcurrent_gt_2a_at_most_99_consecutive_ticks"
            in cell["metrics"].get("checks", {})
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
    finite_cells = [
        cell for cell in cells if cell["metrics"].get("samples") == 600
    ]
    moving = [
        float(cell["metrics"]["mean_local_vx_m_s"])
        for cell in finite_cells
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
        "worst_tracking_p95_rad": max_or_none(
            float(cell["metrics"]["worst_tracking_p95_rad"])
            for cell in finite_cells
        ),
        "worst_peak_current_a": max_or_none(
            float(
                cell["prospective_current_gate"]["worst_peak_current_a"]
            )
            for cell in finite_cells
        ),
        "worst_peak_torque_nm": max_or_none(
            float(
                cell["prospective_current_gate"]["worst_peak_torque_nm"]
            )
            for cell in finite_cells
        ),
        "worst_strict_over_2a_run_ticks": max_or_none(
            int(
                cell["prospective_current_gate"][
                    "worst_strict_over_2a_run_ticks"
                ]
            )
            for cell in finite_cells
        ),
        "minimum_moving_mean_vx_m_s": min(moving) if moving else None,
    }
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
        "schema_version": "winner_v110.pitch_guard_behavior_result.v1",
        "status": (
            "PASS_WINNER_V110_PITCH_GUARD_BEHAVIOR"
            if not failed_validity
            else "INVALID_WINNER_V110_PITCH_GUARD_BEHAVIOR"
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
        "# Winner-v110 G3 pitch-guard behavior result\n\n"
        f"Status: `{result['status']}`\n\n"
        f"Decision: `{decision['status']}`\n\n"
        f"Passing cells: `{summary['passing_cells']}/16`\n\n"
        f"Persistent pass: `{persistent_pass}`\n\n"
        f"Worst tracking p95: `{summary['worst_tracking_p95_rad']}` rad\n\n"
        f"Worst peak current: `{summary['worst_peak_current_a']}` A\n\n"
        f"Worst peak torque: `{summary['worst_peak_torque_nm']}` N.m\n\n"
        "This CPU screen cannot authorize hosted training, deployment "
        "checkpoint selection, Gate 5, robot use, torque, or motion.\n",
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
