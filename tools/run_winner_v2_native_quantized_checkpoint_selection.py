#!/usr/bin/env python3
"""Plan or execute the frozen native-quantized winner-v2 selection matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from aggregate_ground_up_robustness_r1 import summarize  # noqa: E402
from build_winner_v2_native_quantized_eval_policies import (  # noqa: E402
    SOURCE_POLICIES,
    numpy_quantize_observation,
    valid_binary_contacts,
)
from evaluate_ground_up_policy import evaluate, write_markdown  # noqa: E402


PREREG = (
    ROOT
    / "outputs/analysis/winner_v2_native_quantized_checkpoint_selection_preregistration.json"
)
TRANSFORM_CONTRACT = ROOT / "outputs/analysis/winner_v2_native_quantized_eval_contract.json"
WRAPPER_MANIFEST = (
    ROOT / "outputs/analysis/winner_v2_native_quantized_eval_policies/manifest.json"
)
RUNNER_CONTRACT = (
    ROOT
    / "outputs/analysis/winner_v2_native_quantized_checkpoint_selection_runner_contract.json"
)
RUNNER_CONTRACT_MD = (
    ROOT
    / "outputs/analysis/WINNER_V2_NATIVE_QUANTIZED_SELECTION_RUNNER_CONTRACT_20260719.md"
)
OUT = ROOT / "outputs/analysis/winner_v2_native_quantized_checkpoint_selection"
RESULT_JSON = (
    ROOT
    / "outputs/analysis/winner_v2_native_quantized_checkpoint_selection_result.json"
)
RESULT_MD = (
    ROOT
    / "outputs/analysis/WINNER_V2_NATIVE_QUANTIZED_CHECKPOINT_SELECTION_RESULT_20260719.md"
)
PLAYGROUND = Path("/tmp/ground_up_reset_estimator_eval_composed_20260715")
P30_FIT = ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
PLANT_FITS = {
    "p30": P30_FIT,
    "p31_34": ROOT / "outputs/analysis/fixed_target_p31_34_actuator_fit_20260712.json",
}
REFERENCE = ROOT / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
SEED = 167931544
COMMANDS = (0.0, 0.074, 0.077, 0.080)
STEPS = (512000, 1024000)
HOME_RAD = np.asarray(
    json.loads(
        (ROOT / "artifacts/runtime_handoff/rdkx5_native_20260719/policy_contract.json").read_text()
    )["action_contract"]["home_rad"],
    dtype=np.float64,
)
CONSERVATIVE_RATE_LIMITS_RAD_S = np.asarray(
    [
        5.24,
        5.24,
        1.50,
        1.50,
        1.50,
        5.24,
        5.24,
        5.24,
        5.24,
        5.24,
        5.24,
        1.25,
        1.00,
        1.25,
    ],
    dtype=np.float64,
)
X0_GATE = {
    "samples": 600,
    "termination_reason": "duration_complete",
    "candidate_gate_status": "PASS_CANDIDATE_SIM_GATE",
    "maximum_absolute_mean_local_velocity_m_s": 0.02,
    "maximum_body_pitch_p95_rad": 0.25,
    "minimum_base_height_m": 0.12,
    "maximum_pitch_tracking_p95_rad": 0.20,
    "maximum_action_saturation_pct": 0.0,
    "maximum_rate_excess_rad_s": 0.0,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def wrapper_rows() -> dict[int, dict[str, Any]]:
    payload = json.loads(WRAPPER_MANIFEST.read_text())
    return {int(row["step"]): row for row in payload["policies"]}


def matrix_plan() -> list[dict[str, Any]]:
    wrappers = wrapper_rows()
    return [
        {
            "step": step,
            "source_policy": str(SOURCE_POLICIES[step].relative_to(ROOT)),
            "source_policy_sha256": sha256(SOURCE_POLICIES[step]),
            "wrapper_policy": wrappers[step]["wrapper"],
            "wrapper_policy_sha256": wrappers[step]["wrapper_sha256"],
            "observer_fit": "p30",
            "observer_fit_sha256": sha256(P30_FIT),
            "plant_fit": plant_name,
            "plant_fit_sha256": sha256(plant_path),
            "commands_x_m_s": list(COMMANDS),
            "seed": SEED,
            "ticks": 600,
            "cells": len(COMMANDS),
        }
        for plant_name, plant_path in PLANT_FITS.items()
        for step in STEPS
    ]


def plan_contract() -> dict[str, Any]:
    prereg = json.loads(PREREG.read_text())
    contract = json.loads(TRANSFORM_CONTRACT.read_text())
    plan = matrix_plan()
    runner = Path(__file__).resolve()
    checks = {
        "preregistration_passes": prereg["status"]
        == "PREREGISTERED_BEFORE_TRANSFORM_OR_BEHAVIOR_OUTCOMES",
        "transform_contract_passes": contract["status"]
        == "PASS_WINNER_V2_NATIVE_QUANTIZED_EVAL_CONTRACT"
        and contract["formal_behavior_cells_executed"] == 0,
        "matrix_is_exactly_16_cells": len(plan) == 4
        and sum(int(row["cells"]) for row in plan) == 16,
        "matrix_axes_exact": {row["step"] for row in plan} == set(STEPS)
        and {row["plant_fit"] for row in plan} == set(PLANT_FITS)
        and all(row["commands_x_m_s"] == list(COMMANDS) for row in plan)
        and all(row["seed"] == SEED and row["ticks"] == 600 for row in plan),
        "p30_observer_only": all(row["observer_fit"] == "p30" for row in plan),
        "all_wrapper_hashes_match_contract": all(
            any(
                int(item["step"]) == row["step"]
                and item["wrapper_sha256"] == row["wrapper_policy_sha256"]
                for item in contract["policies"]
            )
            for row in plan
        ),
        "frozen_evaluator_hash_exact": sha256(TOOLS / "closed_loop_sim_eval.py")
        == prereg["frozen_hashes"]["closed_loop_sim_eval.py"],
        "playground_exists": PLAYGROUND.exists(),
        "output_root_absent_before_formal_run": not OUT.exists(),
        "decision_artifacts_absent_before_formal_run": not RESULT_JSON.exists()
        and not RESULT_MD.exists(),
        "zero_formal_behavior_cells": True,
    }
    failed = [name for name, passed in checks.items() if not passed]
    payload = {
        "schema_version": "winner_v2.native_quantized_selection_runner_contract.v1",
        "status": (
            "PASS_WINNER_V2_NATIVE_QUANTIZED_SELECTION_RUNNER_CONTRACT"
            if not failed
            else "HOLD_WINNER_V2_NATIVE_QUANTIZED_SELECTION_RUNNER_CONTRACT"
        ),
        "failed_checks": failed,
        "checks": checks,
        "formal_behavior_cells_executed": 0,
        "runner_path": str(runner.relative_to(ROOT)),
        "runner_sha256": sha256(runner),
        "supporting_tool_hashes": {
            name: sha256(TOOLS / name)
            for name in (
                "closed_loop_sim_eval.py",
                "evaluate_ground_up_policy.py",
                "aggregate_ground_up_robustness_r1.py",
                "build_winner_v2_native_quantized_eval_policies.py",
            )
        },
        "preregistration_sha256": sha256(PREREG),
        "transform_contract_sha256": sha256(TRANSFORM_CONTRACT),
        "wrapper_manifest_sha256": sha256(WRAPPER_MANIFEST),
        "plan": plan,
        "environment": {
            "CUDA_VISIBLE_DEVICES": os.environ["CUDA_VISIBLE_DEVICES"],
            "JAX_PLATFORMS": os.environ["JAX_PLATFORMS"],
            "robot_or_rdk_access": False,
        },
    }
    RUNNER_CONTRACT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Winner-v2 Native-Quantized Selection Runner Contract",
        "",
        f"status: `{payload['status']}`",
        "",
        "Formal behavior cells executed: `0`.",
        "",
    ]
    lines.extend(
        f"- `{name}`: `{'PASS' if passed else 'FAIL'}`"
        for name, passed in checks.items()
    )
    lines.extend(
        [
            "",
            "A pass authorizes one execution of the frozen 16-cell CPU matrix only. "
            "It does not select a checkpoint before outcomes or authorize hardware.",
            "",
        ]
    )
    RUNNER_CONTRACT_MD.write_text("\n".join(lines))
    return payload


def eval_args(
    wrapper: Path, plant_fit: Path, trace_dir: Path
) -> argparse.Namespace:
    return argparse.Namespace(
        policy=str(wrapper),
        playground_root=str(PLAYGROUND),
        fit=str(plant_fit),
        policy_observer_fit=str(P30_FIT),
        reference_feature_table=str(REFERENCE),
        reference_start_phase=0,
        expected_observation_dim=115,
        policy_state_input_names="previous_action",
        policy_state_output_names="previous_action_out",
        policy_applied_target_observation=True,
        policy_reset_com_estimator_input=False,
        trace_dir=trace_dir,
        trace_full_obs=True,
        trace_com_accelerometer_map_ticks="",
        commands=",".join(str(value) for value in COMMANDS),
        seeds=str(SEED),
        duration_s=12.0,
        minimum_emergence_duration_s=1.08,
        task="flat_terrain_backlash",
        eval_dynamics_override_json=None,
        reset_mode="home-support",
        policy_action_rate_limit_rad_s=None,
        policy_action_rate_limit_joint_indices="2,3,4,11,12,13",
        policy_action_rate_limit_values="",
    )


def enrich_trace(trace_path: Path) -> dict[str, Any]:
    rows = [json.loads(line) for line in trace_path.read_text().splitlines() if line]
    max_delta_by_slice = {"gyro": 0.0, "accel": 0.0, "position": 0.0, "velocity": 0.0}
    slice_map = {
        "gyro": slice(0, 3),
        "accel": slice(3, 6),
        "position": slice(13, 27),
        "velocity": slice(27, 41),
    }
    finite = True
    contiguous = True
    unchanged_exact = True
    contacts_binary_exact = True
    max_envelope_excess = 0.0
    previous_sent = HOME_RAD.copy()
    for index, row in enumerate(rows):
        contiguous &= int(row["tick"]) == index
        pre = np.asarray(row["obs_state"], dtype=np.float32)
        post = numpy_quantize_observation(pre[None, :])[0]
        finite &= bool(
            pre.shape == (115,)
            and post.shape == (115,)
            and np.all(np.isfinite(pre))
            and np.all(np.isfinite(post))
        )
        unchanged_exact &= bool(
            np.array_equal(pre[6:13], post[6:13])
            and np.array_equal(pre[41:115], post[41:115])
        )
        contacts_binary_exact &= valid_binary_contacts(pre) and bool(
            np.array_equal(pre[97:99], post[97:99])
        )
        delta = post.astype(np.float64) - pre.astype(np.float64)
        for name, item in slice_map.items():
            max_delta_by_slice[name] = max(
                max_delta_by_slice[name], float(np.max(np.abs(delta[item])))
            )
        sent = np.asarray(row["sent_target_rad"], dtype=np.float64)
        rate = np.abs(sent - previous_sent) / 0.02
        raw_excess = float(np.max(np.maximum(rate - CONSERVATIVE_RATE_LIMITS_RAD_S, 0.0)))
        excess = 0.0 if raw_excess <= 1.0e-5 else raw_excess
        max_envelope_excess = max(max_envelope_excess, excess)
        previous_sent = sent
        row["policy_input_pre_native_quantization"] = pre.astype(float).tolist()
        row["policy_input_post_native_quantization"] = post.astype(float).tolist()
        row["policy_input_native_quantization_delta"] = delta.tolist()
        row["conservative_envelope_excess_rad_s"] = excess
    trace_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    )
    return {
        "path": str(trace_path.relative_to(ROOT)),
        "sha256": sha256(trace_path),
        "rows": len(rows),
        "ticks_contiguous": contiguous,
        "finite_pre_post_float32_115": finite,
        "unchanged_slices_bit_exact": unchanged_exact,
        "contacts_binary_and_exact": contacts_binary_exact,
        "max_abs_quantization_delta_by_slice": max_delta_by_slice,
        "max_conservative_envelope_excess_rad_s": max_envelope_excess,
    }


def write_cell_artifacts(
    *,
    stem: str,
    step: int,
    plant_name: str,
    wrapper_hash: str,
    source_hash: str,
    run: dict[str, Any],
    trace_audit: dict[str, Any],
) -> tuple[Path, Path, dict[str, Any]]:
    cells_dir = OUT / "cells"
    cells_dir.mkdir(parents=True, exist_ok=True)
    command = float(run["command_x"])
    name = f"{stem}_x{command:.3f}_seed{SEED}"
    json_path = cells_dir / f"{name}.json"
    md_path = cells_dir / f"{name}.md"
    gate = run["candidate_gate"]
    emergence = run["emergence"]
    fitted = run["modes"]["fitted"]
    metrics = gate["metrics"]
    pass_cell = (
        int(fitted["samples"]) == 600
        and fitted["termination_reason"] == "duration_complete"
        and gate["status"] == "PASS_CANDIDATE_SIM_GATE"
        and float(metrics["max_action_saturation_pct"]) == 0.0
        and float(metrics["max_sent_target_velocity_limit_excess_rad_s"]) == 0.0
        and float(metrics["max_sent_target_velocity_max_limit_excess_rad_s"]) == 0.0
        and float(metrics["max_pitch_tracking_p95_rad"]) <= 0.20
        and trace_audit["max_conservative_envelope_excess_rad_s"] == 0.0
        and trace_audit["rows"] == 600
        and trace_audit["ticks_contiguous"]
        and trace_audit["finite_pre_post_float32_115"]
        and trace_audit["unchanged_slices_bit_exact"]
        and trace_audit["contacts_binary_and_exact"]
        and (
            command == 0.0
            or (
                bool(emergence["pass"])
                and int(emergence["left_contact_transition_count"]) > 0
                and int(emergence["right_contact_transition_count"]) > 0
            )
        )
        and (
            command != 0.0
            or (
                abs(float(emergence["mean_velocity_x_m_s"])) <= 0.02
                and float(metrics["max_abs_body_pitch_p95_rad"]) <= 0.25
                and float(metrics["min_base_height_m"]) >= 0.12
            )
        )
    )
    payload = {
        "schema_version": "winner_v2.native_quantized_selection_cell.v1",
        "status": "PASS_NATIVE_QUANTIZED_CELL" if pass_cell else "HOLD_NATIVE_QUANTIZED_CELL",
        "pass": pass_cell,
        "step": step,
        "plant_fit": plant_name,
        "plant_fit_sha256": sha256(PLANT_FITS[plant_name]),
        "observer_fit": "p30",
        "observer_fit_sha256": sha256(P30_FIT),
        "source_policy_sha256": source_hash,
        "eval_wrapper_sha256": wrapper_hash,
        "command_x_m_s": command,
        "seed": SEED,
        "run": run,
        "trace_audit": trace_audit,
        "training_reward_selection_weight": 0,
        "robot_clearance": False,
    }
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    md_path.write_text(
        "\n".join(
            [
                f"# Native-Quantized Cell — {stem} x={command:.3f}",
                "",
                f"status: `{payload['status']}`",
                "",
                f"- checkpoint: `{step}`",
                f"- plant fit: `{plant_name}`",
                f"- samples: `{fitted['samples']}`",
                f"- tracking p95: `{metrics['max_pitch_tracking_p95_rad']}` rad",
                f"- mean vx: `{emergence['mean_velocity_x_m_s']}` m/s",
                f"- saturation: `{metrics['max_action_saturation_pct']}` percent",
                f"- conservative envelope excess: `{trace_audit['max_conservative_envelope_excess_rad_s']}` rad/s",
                f"- trace SHA-256: `{trace_audit['sha256']}`",
                "",
            ]
        )
    )
    return json_path, md_path, payload


def execute() -> dict[str, Any]:
    prereg = json.loads(PREREG.read_text())
    transform_contract = json.loads(TRANSFORM_CONTRACT.read_text())
    runner_contract = json.loads(RUNNER_CONTRACT.read_text())
    runner = Path(__file__).resolve()
    if runner_contract["status"] != "PASS_WINNER_V2_NATIVE_QUANTIZED_SELECTION_RUNNER_CONTRACT":
        raise RuntimeError("runner contract is not passing")
    if runner_contract["formal_behavior_cells_executed"] != 0:
        raise RuntimeError("runner contract is not zero-outcome")
    if runner_contract["runner_sha256"] != sha256(runner):
        raise RuntimeError("runner hash changed after its zero-outcome contract")
    if OUT.exists() or RESULT_JSON.exists() or RESULT_MD.exists():
        raise RuntimeError("formal output already exists; no retry or overwrite is permitted")
    if transform_contract["status"] != "PASS_WINNER_V2_NATIVE_QUANTIZED_EVAL_CONTRACT":
        raise RuntimeError("transform contract is not passing")

    OUT.mkdir(parents=True)
    wrappers = wrapper_rows()
    matrices: list[dict[str, Any]] = []
    cells: list[dict[str, Any]] = []
    trace_audits: list[dict[str, Any]] = []
    for plant_name, plant_fit in PLANT_FITS.items():
        for step in STEPS:
            source = SOURCE_POLICIES[step]
            wrapper = ROOT / wrappers[step]["wrapper"]
            stem = f"plant_{plant_name}_T2_EQUAL_{step}_native_quantized"
            trace_dir = OUT / "traces" / stem
            trace_dir.mkdir(parents=True)
            payload = evaluate(eval_args(wrapper, plant_fit, trace_dir))
            for run in payload["runs"]:
                trace_path = Path(run["trace_jsonl"])
                audit = enrich_trace(trace_path)
                trace_audits.append(audit)
                run["native_quantization_trace_audit"] = audit
                cell_json, cell_md, cell = write_cell_artifacts(
                    stem=stem,
                    step=step,
                    plant_name=plant_name,
                    wrapper_hash=sha256(wrapper),
                    source_hash=sha256(source),
                    run=run,
                    trace_audit=audit,
                )
                cell["cell_json"] = str(cell_json.relative_to(ROOT))
                cell["cell_json_sha256"] = sha256(cell_json)
                cell["cell_md"] = str(cell_md.relative_to(ROOT))
                cell["cell_md_sha256"] = sha256(cell_md)
                cells.append(cell)
            payload["native_quantization"] = {
                "source_policy": str(source.relative_to(ROOT)),
                "source_policy_sha256": sha256(source),
                "eval_wrapper": str(wrapper.relative_to(ROOT)),
                "eval_wrapper_sha256": sha256(wrapper),
                "observer_fit_sha256": sha256(P30_FIT),
                "plant_fit_sha256": sha256(plant_fit),
                "scope": "native finite register representation only",
            }
            matrix_json = OUT / f"{stem}.json"
            matrix_md = OUT / f"{stem}.md"
            matrix_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
            write_markdown(payload, matrix_md)
            summary = summarize(matrix_json, X0_GATE, SEED)
            summary["max_conservative_envelope_excess_rad_s"] = max(
                audit["max_conservative_envelope_excess_rad_s"]
                for audit in trace_audits[-4:]
            )
            summary["all_cell_artifacts_pass"] = all(cell["pass"] for cell in cells[-4:])
            summary["matrix_pass"] = bool(
                summary["matrix_pass"]
                and summary["max_conservative_envelope_excess_rad_s"] == 0.0
                and summary["all_cell_artifacts_pass"]
            )
            matrices.append(
                {
                    "plant_fit": plant_name,
                    "plant_fit_sha256": sha256(plant_fit),
                    "observer_fit": "p30",
                    "observer_fit_sha256": sha256(P30_FIT),
                    "step": step,
                    "source_policy_sha256": sha256(source),
                    "eval_wrapper_sha256": sha256(wrapper),
                    "eval_json": str(matrix_json.relative_to(ROOT)),
                    "eval_json_sha256": sha256(matrix_json),
                    "eval_md": str(matrix_md.relative_to(ROOT)),
                    "eval_md_sha256": sha256(matrix_md),
                    "summary": summary,
                }
            )

    unique_cells = {
        (int(cell["step"]), cell["plant_fit"], float(cell["command_x_m_s"]), int(cell["seed"]))
        for cell in cells
    }
    expected_cells = {
        (step, plant, command, SEED)
        for step in STEPS
        for plant in PLANT_FITS
        for command in COMMANDS
    }
    validity_checks = {
        "preregistration_exact": prereg["status"]
        == "PREREGISTERED_BEFORE_TRANSFORM_OR_BEHAVIOR_OUTCOMES",
        "transform_contract_exact": transform_contract["status"]
        == "PASS_WINNER_V2_NATIVE_QUANTIZED_EVAL_CONTRACT",
        "runner_contract_exact": runner_contract["status"]
        == "PASS_WINNER_V2_NATIVE_QUANTIZED_SELECTION_RUNNER_CONTRACT"
        and runner_contract["runner_sha256"] == sha256(runner),
        "all_16_cells_present": len(cells) == 16 and unique_cells == expected_cells,
        "all_four_matrices_present": len(matrices) == 4,
        "all_cpu_only": all(
            json.loads((ROOT / row["eval_json"]).read_text())["execution"]["platform"]
            == "cpu"
            for row in matrices
        ),
        "all_trace_contracts_pass": len(trace_audits) == 16
        and all(
            audit["rows"] == 600
            and audit["ticks_contiguous"]
            and audit["finite_pre_post_float32_115"]
            and audit["unchanged_slices_bit_exact"]
            and audit["contacts_binary_and_exact"]
            for audit in trace_audits
        ),
        "all_source_wrapper_fit_hashes_exact": all(
            row["source_policy_sha256"] == sha256(SOURCE_POLICIES[int(row["step"])])
            and row["eval_wrapper_sha256"]
            == wrappers[int(row["step"])]["wrapper_sha256"]
            and row["observer_fit_sha256"] == sha256(P30_FIT)
            and row["plant_fit_sha256"] == sha256(PLANT_FITS[row["plant_fit"]])
            for row in matrices
        ),
        "no_training_reward_selection": all(
            int(cell["training_reward_selection_weight"]) == 0 for cell in cells
        ),
    }
    failed_validity = [name for name, passed in validity_checks.items() if not passed]
    per_checkpoint: dict[str, dict[str, Any]] = {}
    for step in STEPS:
        step_matrices = [row for row in matrices if int(row["step"]) == step]
        per_checkpoint[str(step)] = {
            "all_eight_cells_pass": len(step_matrices) == 2
            and all(row["summary"]["matrix_pass"] for row in step_matrices),
            "worst_pitch_tracking_p95_rad": max(
                row["summary"]["worst_nominal_tracking_p95_rad"] for row in step_matrices
            ),
            "minimum_moving_mean_local_vx_m_s": min(
                row["summary"]["minimum_nominal_vx_m_s"] for row in step_matrices
            ),
            "source_policy_sha256": sha256(SOURCE_POLICIES[step]),
            "eval_wrapper_sha256": wrappers[step]["wrapper_sha256"],
        }

    selected_step: int | None = None
    if failed_validity:
        decision = "INVALID_NATIVE_QUANTIZED_SELECTION_STUDY"
    elif not all(item["all_eight_cells_pass"] for item in per_checkpoint.values()):
        decision = "HOLD_NATIVE_QUANTIZED_PERSISTENCE_NO_SELECTION"
    else:
        selected_step = min(
            STEPS,
            key=lambda step: (
                per_checkpoint[str(step)]["worst_pitch_tracking_p95_rad"],
                -per_checkpoint[str(step)]["minimum_moving_mean_local_vx_m_s"],
                0 if step == 512000 else 1,
            ),
        )
        decision = f"SELECT_WINNER_V2_{selected_step}_NATIVE_QUANTIZED"

    result = {
        "schema_version": "winner_v2.native_quantized_checkpoint_selection_result.v1",
        "status": (
            "PASS_NATIVE_QUANTIZED_CHECKPOINT_SELECTED"
            if selected_step is not None
            else (
                "HOLD_NATIVE_QUANTIZED_CHECKPOINT_SELECTION"
                if not failed_validity
                else "INVALID_NATIVE_QUANTIZED_CHECKPOINT_SELECTION"
            )
        ),
        "decision": decision,
        "selected_step": selected_step,
        "selected_onnx_sha256": (
            sha256(SOURCE_POLICIES[selected_step]) if selected_step is not None else "NOT_READY"
        ),
        "validity_checks": validity_checks,
        "failed_validity_checks": failed_validity,
        "matrix_cells": len(cells),
        "matrices": matrices,
        "per_checkpoint": per_checkpoint,
        "selection_order": prereg["selection_order"],
        "runner_path": str(runner.relative_to(ROOT)),
        "runner_sha256": sha256(runner),
        "runner_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "preregistration_sha256": sha256(PREREG),
        "transform_contract_sha256": sha256(TRANSFORM_CONTRACT),
        "runner_contract_sha256": sha256(RUNNER_CONTRACT),
        "authority": {
            "runtime_v2_acceptance_of_selected_binary": selected_step is not None,
            "gate_5": "NOT_AUTHORIZED",
            "deployment": False,
            "rdk_x5_or_robot_access": False,
            "robot_clearance": False,
            "remaining_real_build_com_fields": 46,
        },
    }
    RESULT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Winner-v2 Native-Quantized Checkpoint Selection Result",
        "",
        f"status: `{result['status']}`",
        f"decision: `{decision}`",
        f"selected ONNX SHA-256: `{result['selected_onnx_sha256']}`",
        "",
        "| checkpoint | all 8 cells pass | worst tracking p95 | minimum moving vx | source SHA-256 |",
        "|---:|---|---:|---:|---|",
    ]
    for step in STEPS:
        item = per_checkpoint[str(step)]
        lines.append(
            f"| {step} | `{item['all_eight_cells_pass']}` | "
            f"{item['worst_pitch_tracking_p95_rad']:.12f} | "
            f"{item['minimum_moving_mean_local_vx_m_s']:.12f} | "
            f"`{item['source_policy_sha256']}` |"
        )
    lines.extend(
        [
            "",
            "The selection rule was frozen before these representation outcomes. "
            "Training and simulator reward had zero selection weight. The selected "
            "identity, if any, is the original policy graph; the quantized wrapper is "
            "evaluation-only because the native runtime supplies register-quantized inputs.",
            "",
            "This result covers finite native input representation only. It does not "
            "cover sensor bias/noise/age or real torso COM, and it does not authorize "
            "Gate 5, deployment, RDK-X5/robot access, torque, motors, or robot clearance.",
            "",
        ]
    )
    RESULT_MD.write_text("\n".join(lines))
    return result


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--plan-only", action="store_true")
    group.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    if args.plan_only:
        result = plan_contract()
        print(RUNNER_CONTRACT_MD.relative_to(ROOT))
        print(RUNNER_CONTRACT.relative_to(ROOT))
        return 0 if not result["failed_checks"] else 1
    result = execute()
    print(RESULT_MD.relative_to(ROOT))
    print(RESULT_JSON.relative_to(ROOT))
    return 1 if result["failed_validity_checks"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
