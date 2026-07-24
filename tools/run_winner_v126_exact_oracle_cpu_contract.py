#!/usr/bin/env python3
"""Run the preregistered nonformal V126 exact-oracle CPU contract."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
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
)
from run_winner_v3_variable_configuration_behavior import (  # noqa: E402
    actuator_fit,
)


ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v126_exact_oracle_preregistration.json"
PREREG_SHA256 = (
    "6b9e0c45955753f17d78888f4b9004d8bfc73699342828b09d0725183887d307"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
OUTPUT = ANALYSIS / "winner_v126_exact_oracle_cpu_contract.json"
MARKDOWN = ANALYSIS / "WINNER_V126_EXACT_ORACLE_CPU_CONTRACT_20260724.md"


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


def load_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def transition_view(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    keys = (
        "tick",
        "action",
        "policy_state_input",
        "policy_state_output",
        "sent_target_rad",
        "applied_target_rad",
        "actual_position_rad",
        "actuator_force_nm",
        "qpos",
        "qvel",
        "foot_contacts",
        "done",
    )
    return [{key: row[key] for key in keys} for row in rows]


def oracle_view(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "tick": row["tick"],
            "transition": transition_view([row])[0],
            "oracle": row["exact_torque_oracle"],
            "matured": row["exact_torque_oracle_matured_predictions"],
        }
        for row in rows
    ]


def execute_run(
    *,
    row: Mapping[str, Any],
    base_prereg: Mapping[str, Any],
    policy: Path,
    playground: Path,
    trace: Path,
    oracle_enabled: bool,
    torque_limit_nm: float,
    action_delta: tuple[float, ...],
) -> dict[str, Any]:
    with contextlib.redirect_stdout(io.StringIO()):
        result = run_closed_loop_sim(
            ClosedLoopConfig(
                policy_path=policy,
                fit=actuator_fit(base_prereg, str(row["plant"])),
                playground_root=playground,
                command_x=float(row["command_x_m_s"]),
                duration_s=float(row["duration_ticks"]) * 0.02,
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
                winner_v3_configuration_override=row["configuration"],
                winner_v3_sensor_noise_scales=None,
                winner_v3_native_quantization=False,
                winner_v3_additional_action_delay_ticks=0,
                winner_v3_imu_delay_ticks=0,
                winner_v3_home_relative_actuator_gain=True,
                exact_torque_oracle_enabled=oracle_enabled,
                exact_torque_oracle_limit_nm=float(torque_limit_nm),
                exact_torque_oracle_guard_rad=0.165,
                exact_torque_oracle_action_delta=action_delta,
                exact_torque_oracle_force_tolerance_nm=5.0e-6,
                exact_torque_oracle_monotonicity_tolerance_nm=5.0e-6,
                exact_torque_oracle_grid_points=9,
                exact_torque_oracle_bisection_iterations=32,
                exact_torque_oracle_maximum_coordinate_passes=14,
            )
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    if run_root.exists():
        raise FileExistsError(f"refusing to overwrite V126 contract: {run_root}")
    if OUTPUT.exists() or MARKDOWN.exists():
        raise FileExistsError("refusing to overwrite V126 CPU contract result")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if (
        sha256(PREREG) != PREREG_SHA256
        or prereg.get("status")
        != "PREREGISTERED_WINNER_V126_EXACT_ORACLE_SCREEN_AND_V115_PRICE_AUDIT"
        or prereg.get("authority", {}).get("cpu_contract_runs") != 4
        or prereg.get("cpu_contract", {}).get("formal_behavior_cells") != 0
    ):
        raise ValueError("V126 CPU contract preregistration changed")
    run_root.mkdir(parents=True)
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    row = prereg["cpu_contract"]["cell"]
    policy_spec = next(
        item
        for item in prereg["formal_screen"]["policies"]
        if item["id"] == row["checkpoint_id"]
    )
    policy_root = Path(prereg["external_inputs"]["policy_root"])
    playground = Path(prereg["external_inputs"]["playground"])
    policy = policy_root / policy_spec["filename"]
    if (
        sha256(policy) != policy_spec["sha256"]
        or sha256(REFERENCE)
        != prereg["sources"][REFERENCE.name]["sha256"]
        or not playground.is_dir()
    ):
        raise ValueError("V126 CPU contract external input changed")
    action_delta = tuple(float(value) for value in prereg["oracle"]["action_delta"])
    run_specs = (
        ("baseline", False, 1.91229675),
        ("default_off", True, 100.0),
        ("exact_a", True, 1.91229675),
        ("exact_b", True, 1.91229675),
    )
    runs: dict[str, dict[str, Any]] = {}
    rows_by_label: dict[str, list[dict[str, Any]]] = {}
    for label, enabled, limit in run_specs:
        trace = run_root / f"{label}.jsonl"
        result = execute_run(
            row=row,
            base_prereg=base_prereg,
            policy=policy,
            playground=playground,
            trace=trace,
            oracle_enabled=enabled,
            torque_limit_nm=limit,
            action_delta=action_delta,
        )
        rows = load_rows(trace) if trace.is_file() else []
        rows_by_label[label] = rows
        mode = ((result.get("modes") or {}).get("fitted") or {})
        runs[label] = {
            "status": result.get("status"),
            "samples": mode.get("samples"),
            "termination_reason": mode.get("termination_reason"),
            "oracle": mode.get("exact_torque_oracle"),
            "trace_path": str(trace),
            "trace_sha256": sha256(trace) if trace.is_file() else None,
            "transition_sha256": canonical_sha256(transition_view(rows)),
            "oracle_view_sha256": canonical_sha256(oracle_view(rows)),
        }
    default_off_exact = (
        transition_view(rows_by_label["baseline"])
        == transition_view(rows_by_label["default_off"])
    )
    repeat_exact = (
        oracle_view(rows_by_label["exact_a"])
        == oracle_view(rows_by_label["exact_b"])
    )
    exact_summaries = [
        runs[label]["oracle"] for label in ("exact_a", "exact_b")
    ]
    checks = {
        "cpu_only": jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices()),
        "four_runs_exact": len(runs) == 4
        and all(item["samples"] == 8 for item in runs.values())
        and all(
            item["termination_reason"] == "duration_complete"
            for item in runs.values()
        ),
        "all_trace_values_finite": all(
            all(
                math.isfinite(float(value))
                for row_value in transition_view(rows)
                for value in np.asarray(
                    row_value["actuator_force_nm"], dtype=float
                ).reshape(-1)
            )
            for rows in rows_by_label.values()
        ),
        "default_off_transition_exact": default_off_exact,
        "exact_repeat_bit_exact": repeat_exact,
        "matured_predictions_present": all(
            int(item["matured_predictions"]) > 0
            for item in exact_summaries
        ),
        "causal_predictions_exact": all(
            bool(item["prediction_exact"]) for item in exact_summaries
        ),
        "zero_nonempty_residual_violations": all(
            bool(item["only_empty_or_prehistory_residuals"])
            for item in exact_summaries
        ),
        "formal_behavior_cells_zero": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    payload = {
        "schema_version": "winner_v126.exact_oracle_cpu_contract.v1",
        "status": (
            "PASS_WINNER_V126_EXACT_ORACLE_CPU_CONTRACT"
            if not failed
            else "HOLD_WINNER_V126_EXACT_ORACLE_CPU_CONTRACT"
        ),
        "checks": checks,
        "failed_checks": failed,
        "runs": runs,
        "run_root": str(run_root),
        "formal_behavior_cells_executed": 0,
        "source_hashes": {
            "preregistration": sha256(PREREG),
            "runner": sha256(Path(__file__).resolve()),
            "projector": sha256(ROOT / "tools/exact_torque_oracle.py"),
            "evaluator": sha256(ROOT / "tools/closed_loop_sim_eval_v126.py"),
            "policy": sha256(policy),
            "reference": sha256(REFERENCE),
        },
        "authority": {
            "formal_screen_cells_authorized": 16 if not failed else 0,
            "v115_read_only_audit": not failed,
            "training": False,
            "hosted_or_colab": False,
            "rdkx5_or_robot": False,
            "gate5": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner-v126 exact-oracle CPU contract\n\n"
        f"Status: `{payload['status']}`\n\n"
        f"Default-off transition exact: `{default_off_exact}`.\n\n"
        f"Exact-repeat bit exact: `{repeat_exact}`.\n\n"
        f"Failed checks: `{failed}`.\n\n"
        "A pass authorizes only the preregistered read-only V115 price audit "
        "and 16-cell zero-credit CPU oracle screen. It authorizes no training, "
        "hosted compute, Gate 5, RDK-X5, robot, torque, or motion.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "failed_checks": failed,
                "output_sha256": sha256(OUTPUT),
            }
        ),
        flush=True,
    )
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
