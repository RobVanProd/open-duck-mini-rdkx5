#!/usr/bin/env python3
"""Run the V141 projected-final eight-cell CPU behavior screen."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["JAX_PLATFORM_NAME"] = "cpu"

import jax
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from run_winner_v103_response_conditioned_behavior import (  # noqa: E402
    REFERENCE,
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
PREREG = ANALYSIS / "winner_v141_projected_final_behavior_preregistration.json"
V121_RESULT = ANALYSIS / "winner_v121_nominal_behavior_result.json"
V126_PREREG = (
    ANALYSIS / "winner_v126_all_tick_supreme_clip_preregistration.json"
)
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
V140_RESULT = ANALYSIS / "winner_v140_preservation_projected_actor_result.json"
OUTPUT = ANALYSIS / "winner_v141_projected_final_behavior_result.json"
MARKDOWN = (
    ANALYSIS / "WINNER_V141_PROJECTED_FINAL_BEHAVIOR_RESULT_20260725.md"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_evaluator(path: Path):
    spec = importlib.util.spec_from_file_location(
        "closed_loop_sim_eval_v141_projected_final", path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load V141 evaluator: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def trace_contract(path: Path, command_x: float) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    first = np.asarray(rows[0]["obs_state"], dtype=np.float64)
    first_h = np.asarray(
        rows[0]["policy_state_input"]["h_in"][0], dtype=np.float32
    )
    first_previous = np.asarray(
        rows[0]["policy_state_input"]["previous_action"][0],
        dtype=np.float32,
    )
    action = np.asarray([row["action"] for row in rows], dtype=np.float64)
    return {
        "rows": len(rows),
        "sha256": sha256(path),
        "first_phase": first[99:101].tolist(),
        "first_phase_linf_error": float(
            np.max(np.abs(first[99:101] - np.asarray([1.0, 0.0])))
        ),
        "first_h_in_linf": float(np.max(np.abs(first_h))),
        "first_previous_action_linf": float(
            np.max(np.abs(first_previous))
        ),
        "x0_action_nonzero_values": (
            int(np.count_nonzero(action))
            if abs(command_x) <= 0.01
            else None
        ),
        "oracle_rows": sum(
            isinstance(row.get("exact_torque_oracle"), dict) for row in rows
        ),
    }


def run_cell(
    *,
    evaluator: Any,
    row: dict[str, Any],
    policy: Path,
    playground: Path,
    base_prereg: dict[str, Any],
    trace_path: Path,
    cpu_only: bool,
) -> dict[str, Any]:
    with contextlib.redirect_stdout(io.StringIO()):
        result = evaluator.run_closed_loop_sim(
            evaluator.ClosedLoopConfig(
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
                exact_torque_oracle_enabled=False,
            )
        )
    if result.get("env") is None or not trace_path.is_file():
        return {
            "status": "HOLD_WINNER_V141_PROJECTED_FINAL_CELL",
            "pass": False,
            "failure_reasons": ["simulator_or_trace_missing"],
            "identity": dict(row),
            "simulator": {
                "status": result.get("status"),
                "error": result.get("error"),
            },
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
    contract = trace_contract(
        trace_path, command_x=float(row["command_x_m_s"])
    )
    for name, passed in current["checks"].items():
        metrics["checks"][name] = passed
        if not passed:
            failures.append(name)
    metrics["checks"]["torque_peak_at_most_1p91229675_nm"] = torque[
        "check"
    ]
    if not torque["check"]:
        failures.append("torque_peak_at_most_1p91229675_nm")
    contract_checks = {
        "phase0_first_observation_exact": (
            contract["first_phase_linf_error"] == 0.0
        ),
        "zero_recurrent_state_exact": (
            contract["first_h_in_linf"] == 0.0
            and contract["first_previous_action_linf"] == 0.0
        ),
        "oracle_disabled": contract["oracle_rows"] == 0,
        "x0_deadband_exact": (
            abs(float(row["command_x_m_s"])) > 0.01
            or contract["x0_action_nonzero_values"] == 0
        ),
        "cpu_only": cpu_only,
    }
    for name, passed in contract_checks.items():
        metrics["checks"][name] = passed
        if not passed:
            failures.append(name)
    failures = sorted(set(failures))
    return {
        "schema_version": "winner_v141.projected_final_cell.v1",
        "status": (
            "PASS_WINNER_V141_PROJECTED_FINAL_CELL"
            if not failures
            else "HOLD_WINNER_V141_PROJECTED_FINAL_CELL"
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
        "policy_contract": contract,
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
    parser.add_argument("--evaluator-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args()
    evaluator_root = args.evaluator_root.resolve()
    run_root = args.run_root.resolve()
    for path in (OUTPUT, MARKDOWN, run_root):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite V141: {path}")
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    v121 = json.loads(V121_RESULT.read_text(encoding="utf-8"))
    v126 = json.loads(V126_PREREG.read_text(encoding="utf-8"))
    base_prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    v140 = json.loads(V140_RESULT.read_text(encoding="utf-8"))
    manifest_path = evaluator_root / "composition_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evaluator_path = Path(manifest["output"]["path"])
    policy = Path(v140["artifacts"]["selected_deployed"]["path"])
    observed_hashes = {
        "runner": sha256(Path(__file__).resolve()),
        "v121_nominal_result": sha256(V121_RESULT),
        "v126_preregistration": sha256(V126_PREREG),
        "base_preregistration": sha256(BASE_PREREG),
        "v140_projection_result": sha256(V140_RESULT),
        "composition_manifest": sha256(manifest_path),
        "composed_evaluator": sha256(evaluator_path),
        "selected_final_policy": sha256(policy),
    }
    if (
        prereg.get("status")
        != "PREREGISTERED_WINNER_V141_PROJECTED_FINAL_BEHAVIOR"
        or prereg.get("failed_checks") != []
        or prereg.get("input_hashes") != observed_hashes
        or v140.get("decision")
        != "EARN_ONE_V141_DUAL_CHECKPOINT_BEHAVIOR_PREREGISTRATION"
    ):
        raise ValueError("V141 preregistration changed")
    evaluator = load_evaluator(evaluator_path)
    playground = Path(v126["external_inputs"]["playground"])
    matrix = prereg["matrix"]["new_final_rows"]
    if len(matrix) != 8:
        raise ValueError("V141 requires eight new final cells")
    run_root.mkdir(parents=True)
    cells_root = run_root / "cells"
    traces_root = run_root / "traces"
    cells_root.mkdir()
    traces_root.mkdir()
    cpu_only = (
        jax.default_backend() == "cpu"
        and all(device.platform == "cpu" for device in jax.devices())
    )
    cells = []
    started = time.time()
    for index, row in enumerate(matrix, start=1):
        stem = (
            f"v140_projected_final_{str(row['plant']).lower()}_"
            f"x{float(row['command_x_m_s']):.3f}_seed{int(row['seed'])}"
        )
        trace_path = traces_root / f"{stem}.jsonl"
        cell = run_cell(
            evaluator=evaluator,
            row=row,
            policy=policy,
            playground=playground,
            base_prereg=base_prereg,
            trace_path=trace_path,
            cpu_only=cpu_only,
        )
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
                    "total_new_cells": 8,
                    "pass": cell["pass"],
                    "failures": cell["failure_reasons"],
                    "identity": row,
                }
            ),
            flush=True,
        )
        if not cell["pass"]:
            break
    reused_half = next(
        row
        for row in v121["per_checkpoint"]
        if row["checkpoint_id"] == "V121_TRAIN_MATCHED_HALF"
    )
    all_pass = (
        reused_half["all_eight_cells_pass"]
        and len(cells) == 8
        and all(cell["pass"] for cell in cells)
    )
    payload = {
        "schema_version": "winner_v141.projected_final_behavior_result.v1",
        "status": (
            "PASS_WINNER_V141_PROJECTED_FINAL_BEHAVIOR"
            if all_pass
            else "HOLD_WINNER_V141_PROJECTED_FINAL_BEHAVIOR"
        ),
        "failed_checks": (
            []
            if all_pass
            else ["combined_reused_half_and_projected_final_16_of_16"]
        ),
        "input_hashes": observed_hashes,
        "reused_half": reused_half,
        "new_final_cells": cells,
        "summary": {
            "reused_half_cells": 8,
            "reused_half_passing": int(reused_half["passing_cells"]),
            "new_final_cells_planned": 8,
            "new_final_cells_completed": len(cells),
            "new_final_cells_passing": sum(cell["pass"] for cell in cells),
            "combined_cells_passing": (
                int(reused_half["passing_cells"])
                + sum(cell["pass"] for cell in cells)
            ),
            "combined_cells_required": 16,
            "elapsed_s": time.time() - started,
        },
        "decision": (
            "EARN_V142_RDK_POLICY_CONTRACT_ALIGNMENT_REVIEW"
            if all_pass
            else "CLOSE_PRESERVATION_PROJECTED_ACTOR"
        ),
        "authority": {
            "rdk_policy_contract_review": all_pass,
            "policy_deployment": False,
            "gate5": False,
            "training": False,
            "hosted_training": False,
            "rdkx5_or_robot": False,
            "torque_or_motion": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    MARKDOWN.write_text(
        "# Winner V141 projected-final behavior\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Reused half: `{reused_half['passing_cells']}/8`; new final: "
        f"`{payload['summary']['new_final_cells_passing']}/"
        f"{len(cells)}`.\n"
        f"- Decision: `{payload['decision']}`\n"
        "- No policy deployment, Gate 5, Colab, or hardware authority.\n",
        encoding="utf-8",
    )
    print(payload["status"])
    print(payload["decision"])
    print(f"sha256={sha256(OUTPUT)}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
