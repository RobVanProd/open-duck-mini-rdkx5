#!/usr/bin/env python3
"""Run the corrected 64-tick V126 all-tick supreme-clip CPU contract."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import jax


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from closed_loop_sim_eval_v126_all_tick import (  # noqa: E402
    ClosedLoopConfig,
    run_closed_loop_sim,
)
from run_winner_v103_response_conditioned_behavior import REFERENCE  # noqa: E402
from run_winner_v3_variable_configuration_behavior import (  # noqa: E402
    actuator_fit,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
PREREG_SHA256 = (
    "eb40f17d9c08b8362f068567e1620bdafef21ad9123a633c9536f3637a31c899"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
OUTPUT = ANALYSIS / "winner_v126_all_tick_supreme_clip_cpu_contract.json"
MARKDOWN = (
    ANALYSIS
    / "WINNER_V126_ALL_TICK_SUPREME_CLIP_CPU_CONTRACT_20260724.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    if run_root.exists():
        raise FileExistsError(f"refusing to overwrite all-tick contract: {run_root}")
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite all-tick contract result")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        sha256(PREREG) != PREREG_SHA256
        or prereg.get("status")
        != "PREREGISTERED_WINNER_V126_ALL_TICK_SUPREME_CLIP"
        or prereg.get("authority", {}).get("nonformal_contract_runs") != 1
    ):
        raise ValueError("all-tick supreme-clip preregistration changed")
    spec = prereg["nonformal_contract"]
    row = next(
        row
        for row in prereg["matrix"]["rows"]
        if row["checkpoint_id"] == spec["checkpoint_id"]
        and row["plant"] == spec["plant"]
        and float(row["command_x_m_s"]) == float(spec["command_x_m_s"])
        and int(row["seed"]) == int(spec["seed"])
    )
    policy_spec = next(
        item
        for item in prereg["policies"]
        if item["id"] == row["checkpoint_id"]
    )
    policy = (
        Path(prereg["external_inputs"]["policy_root"])
        / policy_spec["filename"]
    )
    if sha256(policy) != policy_spec["sha256"]:
        raise ValueError("all-tick contract policy changed")
    playground = Path(prereg["external_inputs"]["playground"])
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    run_root.mkdir(parents=True)
    trace = run_root / "trace.jsonl"
    with contextlib.redirect_stdout(io.StringIO()):
        result = run_closed_loop_sim(
            ClosedLoopConfig(
                policy_path=policy,
                fit=actuator_fit(base_prereg, str(row["plant"])),
                playground_root=playground,
                command_x=float(row["command_x_m_s"]),
                duration_s=int(spec["duration_ticks"]) * 0.02,
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
                trace_jsonl=trace,
                trace_full_obs=True,
                winner_v3_home_relative_actuator_gain=True,
                exact_torque_oracle_enabled=True,
                exact_torque_oracle_limit_nm=1.91229675,
                exact_torque_oracle_guard_rad=0.165,
                exact_torque_oracle_action_delta=tuple(
                    float(value)
                    for value in prereg["oracle"]["action_delta"]
                ),
                exact_torque_oracle_force_tolerance_nm=5.0e-6,
                exact_torque_oracle_monotonicity_tolerance_nm=5.0e-6,
                exact_torque_oracle_grid_points=9,
                exact_torque_oracle_bisection_iterations=32,
                exact_torque_oracle_maximum_coordinate_passes=14,
                exact_torque_oracle_schedule_ticks=None,
            )
        )
    simulator_diagnostic = {
        "status": result.get("status"),
        "error": result.get("error"),
        "tick": result.get("tick"),
        "mode": result.get("mode"),
    }
    simulator_diagnostic_path = run_root / "simulator_diagnostic.json"
    simulator_diagnostic_path.write_text(
        json.dumps(
            simulator_diagnostic,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    mode = ((result.get("modes") or {}).get("fitted") or {})
    oracle = mode.get("exact_torque_oracle") or {}
    rows = (
        [
            json.loads(line)
            for line in trace.read_text(encoding="utf-8").splitlines()
            if line
        ]
        if trace.is_file()
        else []
    )
    expected = spec["required"]
    checks = {
        "cpu_only": jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices()),
        "duration_complete_64": mode.get("samples") == 64
        and mode.get("termination_reason") == "duration_complete"
        and len(rows) == 64,
        "all_moving_ticks_probed": int(oracle.get("scheduled_ticks", -1))
        == int(expected["scheduled_ticks"])
        and int(oracle.get("schedule_bypass_ticks", -1))
        == int(expected["schedule_bypass_ticks"]),
        "at_least_one_projection": int(
            oracle.get("projected_joint_events", 0)
        )
        > 0,
        "prediction_exact": bool(oracle.get("prediction_exact")),
        "zero_prediction_mismatches": int(
            oracle.get("prediction_mismatches", -1)
        )
        == 0,
        "zero_nonempty_residual_violations": int(
            oracle.get("nonempty_residual_violations", -1)
        )
        == 0,
        "zero_unscheduled_residual_violations": int(
            oracle.get("unscheduled_residual_violations", -1)
        )
        == 0,
        "formal_behavior_cells_zero": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    payload = {
        "schema_version": (
            "winner_v126.all_tick_supreme_clip_cpu_contract.v1"
        ),
        "status": (
            "PASS_WINNER_V126_ALL_TICK_SUPREME_CLIP_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V126_ALL_TICK_SUPREME_CLIP_CPU_CONTRACT"
        ),
        "checks": checks,
        "failed_checks": failed,
        "oracle": oracle,
        "simulator_status": result.get("status"),
        "trace": {
            "path": str(trace),
            "rows": len(rows),
            "sha256": sha256(trace) if trace.is_file() else None,
        },
        "simulator_diagnostic": {
            **simulator_diagnostic,
            "path": str(simulator_diagnostic_path),
            "sha256": sha256(simulator_diagnostic_path),
        },
        "run_root": str(run_root),
        "input_hashes": {
            "preregistration": sha256(PREREG),
            "runner": sha256(Path(__file__).resolve()),
            "projector": sha256(
                ROOT / "tools/exact_torque_oracle_all_tick.py"
            ),
            "evaluator": sha256(
                ROOT / "tools/closed_loop_sim_eval_v126_all_tick.py"
            ),
            "policy": sha256(policy),
        },
        "formal_behavior_cells_executed": 0,
        "authority": {
            "formal_screen_cells": 16 if not failed else 0,
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
        "# V126 all-tick supreme-clip CPU contract\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"All-tick probes: `{oracle.get('scheduled_ticks')}`.\n\n"
        f"Projected joint events: `{oracle.get('projected_joint_events')}`.\n\n"
        f"Unscheduled residual violations: "
        f"`{oracle.get('unscheduled_residual_violations')}`.\n\n"
        "A pass authorizes only the frozen all-tick 16-cell CPU screen.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "failed_checks": failed,
                "oracle": oracle,
                "output_sha256": sha256(OUTPUT),
            }
        ),
        flush=True,
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
