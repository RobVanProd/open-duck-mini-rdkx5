#!/usr/bin/env python3
"""Run the frozen Winner-v103 response-conditioned CPU behavior gate."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
import os
import subprocess
import sys
import tarfile
import time
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from closed_loop_sim_eval import ClosedLoopConfig, run_closed_loop_sim  # noqa: E402
from run_winner_v3_variable_configuration_behavior import (  # noqa: E402
    actuator_fit,
    canonical_sha256,
    cell_stem,
    classify_cell,
    condition_plan,
    finite_tree,
    matrix_plan,
    readback_checks,
    sha256,
    trace_audit,
)

ANALYSIS = ROOT / "outputs/analysis"
PREREG = ANALYSIS / "winner_v103_response_conditioned_behavior_preregistration.json"
BASE_PREREG = (
    ANALYSIS / "winner_v3_variable_configuration_replacement_preregistration.json"
)
RUNNER_CONTRACT = (
    ANALYSIS / "winner_v103_response_conditioned_behavior_runner_contract.json"
)
REFERENCE = ANALYSIS / "ground_up_projected_reference_feature_table.npz"
CELLS = ANALYSIS / "winner_v103_response_conditioned_cells"
TRACES = ANALYSIS / "winner_v103_response_conditioned_traces"
CONDITIONS = ANALYSIS / "winner_v103_response_conditioned_conditions"
RESULT_JSON = ANALYSIS / "winner_v103_response_conditioned_result.json"
RESULT_MD = (
    ANALYSIS / "WINNER_V103_RESPONSE_CONDITIONED_RESULT_20260722.md"
)
CALIBRATOR_SHA256 = (
    "cb3380ed99b3e9d7e9000904a210227aa397db2a064aa80d8f70e77c8339783b"
)
MATRIX_PLAN_SHA256 = (
    "10b5d3e407636d276275f3f39145233c3cd63688c3229235411ed2734651e073"
)
ELIGIBLE_STEPS = (1_003_520, 2_007_040)
EXPECTED_RUNNER_CONTRACT_STATUS = (
    "PASS_WINNER_V103_RESPONSE_CONDITIONED_BEHAVIOR_RUNNER_CONTRACT"
)


def json_finite(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): json_finite(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_finite(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        if math.isnan(value):
            return None
        return 1.0e308 if value > 0.0 else -1.0e308
    return value


def step_from_name(path: Path) -> int:
    try:
        return int(path.stem.rsplit("_", 1)[1])
    except (IndexError, ValueError) as exc:
        raise ValueError(f"cannot parse checkpoint step from {path.name}") from exc


def safe_extract(archive_path: Path, destination: Path) -> Path:
    if destination.exists():
        raise FileExistsError(
            f"refusing to overwrite extracted V102 artifact: {destination}"
        )
    destination.mkdir(parents=True)
    destination_root = destination.resolve()
    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        for member in members:
            target = (destination / member.name).resolve()
            if destination_root != target and destination_root not in target.parents:
                raise ValueError(f"unsafe V102 archive member: {member.name}")
        archive.extractall(destination, members=members, filter="data")
    roots = [
        path
        for path in destination.iterdir()
        if path.is_dir() and path.name == "winner_v102_response_conditioned_curriculum"
    ]
    if len(roots) != 1:
        raise ValueError(f"unexpected V102 artifact roots: {roots}")
    return roots[0]


def load_hosted_artifact(
    *,
    artifact_json: Path,
    artifact_archive: Path,
    extract_root: Path,
) -> dict[str, Any]:
    payload = json.loads(artifact_json.read_text(encoding="utf-8"))
    if (
        payload.get("status")
        != "PASS_WINNER_V102_RESPONSE_CONDITIONED_TRAINING_ARTIFACT"
        or payload.get("failed_checks") != []
        or payload.get("checks", {}).get("formal_behavior_cells_zero") is not True
        or len(payload.get("stages", [])) != 3
    ):
        raise ValueError("Winner-v102 hosted artifact is not a passing zero-cell result")
    artifact = payload.get("artifact") or {}
    observed_archive_sha256 = sha256(artifact_archive)
    if (
        observed_archive_sha256 != artifact.get("sha256")
        or artifact_archive.stat().st_size != int(artifact.get("bytes", -1))
    ):
        raise ValueError("Winner-v102 hosted archive identity changed")

    stages = payload["stages"]
    final_stage = stages[-1]
    if (
        final_stage.get("id") != "DOMAIN_100_PERCENT"
        or final_stage.get("checkpoint_steps") != [0, *ELIGIBLE_STEPS]
        or final_stage.get("onnx_steps") != [0, *ELIGIBLE_STEPS]
    ):
        raise ValueError("Winner-v102 full-domain export set changed")
    hosted_graphs = {
        int(row["step"]): row
        for row in final_stage.get("onnx", [])
        if int(row["step"]) in ELIGIBLE_STEPS
    }
    if set(hosted_graphs) != set(ELIGIBLE_STEPS):
        raise ValueError("Winner-v102 eligible graph receipts are incomplete")
    for step, row in hosted_graphs.items():
        if (
            row.get("abi_exact") is not True
            or row.get("initializers_finite") is not True
            or row.get("x0_action_exact_zero") is not True
            or row.get("x0_previous_action_out_exact_zero") is not True
            or row.get("x0_hidden_finite") is not True
            or not isinstance(row.get("sha256"), str)
        ):
            raise ValueError(f"Winner-v102 graph receipt failed at step {step}")

    extracted = safe_extract(artifact_archive, extract_root)
    stage_roots = [
        path
        for path in extracted.iterdir()
        if path.is_dir() and path.name == "stage3_domain_100_percent"
    ]
    if len(stage_roots) != 1:
        raise ValueError("Winner-v102 full-domain stage directory is missing")
    graphs = {
        step_from_name(path): path
        for path in stage_roots[0].glob("*.onnx")
        if step_from_name(path) in ELIGIBLE_STEPS
    }
    if set(graphs) != set(ELIGIBLE_STEPS):
        raise ValueError("extracted Winner-v102 eligible graphs are incomplete")
    for step, path in graphs.items():
        if sha256(path) != hosted_graphs[step]["sha256"]:
            raise ValueError(f"Winner-v102 extracted graph hash changed at {step}")
    return {
        "artifact_json": str(artifact_json.resolve()),
        "artifact_json_sha256": sha256(artifact_json),
        "artifact_archive": str(artifact_archive.resolve()),
        "artifact_archive_sha256": observed_archive_sha256,
        "extracted_root": str(extracted),
        "policy_paths": {step: graphs[step] for step in ELIGIBLE_STEPS},
        "policy_hashes": {
            step: hosted_graphs[step]["sha256"] for step in ELIGIBLE_STEPS
        },
    }


def response_trace_audit(
    path: Path,
    result: Mapping[str, Any],
) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    fitted = [row for row in rows if row.get("mode") == "fitted"]
    mode = ((result.get("modes") or {}).get("fitted") or {})
    response = mode.get("response_calibration") or {}
    context_hashes = {
        row.get("policy_calibration_context_sha256") for row in fitted
    }
    checks = {
        "calibration_enabled": response.get("enabled") is True,
        "calibration_ticks_exact": response.get("calibration_ticks") == 250,
        "home_return_ticks_exact": response.get("home_return_ticks") == 250,
        "calibrator_hash_exact": (
            response.get("calibrator_sha256") == CALIBRATOR_SHA256
        ),
        "context_shape_exact": response.get("context_shape") == [1, 64],
        "context_finite": response.get("context_finite") is True,
        "phase_reset_exact": response.get("locomotion_phase_reset") == [1.0, 0.0],
        "hidden_reset_exact": response.get("locomotion_hidden_exact_zero") is True,
        "previous_action_reset_exact": (
            response.get("locomotion_previous_action_exact_zero") is True
        ),
        "graph_authoritative_every_tick": bool(fitted)
        and all(row.get("policy_graph_authoritative_output") is True for row in fitted),
        "host_action_delta_exact_zero": bool(fitted)
        and all(row.get("policy_host_action_delta_max_abs") == 0.0 for row in fitted),
        "context_immutable_every_tick": len(context_hashes) == 1
        and None not in context_hashes
        and response.get("context_sha256") in context_hashes,
        "policy_io_exact": (result.get("policy_io") or {}).get("obs_input_name")
        == "obs"
        and (result.get("policy_io") or {}).get("action_output_name")
        == "continuous_actions"
        and (result.get("policy_io") or {}).get("state_input_names")
        == ["h_in", "previous_action"]
        and (result.get("policy_io") or {}).get("state_output_names")
        == ["h_out", "previous_action_out"]
        and (result.get("policy_io") or {}).get("context_input_name")
        == "calibration_context"
        and (result.get("policy_io") or {}).get("context_input_shape") == [1, 64],
    }
    return {
        "checks": checks,
        "failed_checks": sorted(name for name, passed in checks.items() if not passed),
        "pass": all(checks.values()),
        "context_sha256": response.get("context_sha256"),
        "trace_rows": len(fitted),
    }


def missing_trace_audit(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "sha256": None,
        "rows": 0,
        "ticks_contiguous": False,
        "required_fields_every_tick": False,
        "all_values_finite": False,
        "reset_h_exact_zero": False,
        "reset_previous_action_exact_zero": False,
    }


def execute_cell(
    row: Mapping[str, Any],
    prereg: Mapping[str, Any],
    *,
    policy_paths: Mapping[int, Path],
    policy_hashes: Mapping[int, str],
    playground: Path,
    calibrator: Path,
) -> dict[str, Any]:
    stem = cell_stem(row)
    trace_path = TRACES / f"{stem}.jsonl"
    transport = row["transport"]
    policy_path = policy_paths[int(row["step"])]
    with contextlib.redirect_stdout(io.StringIO()):
        result = run_closed_loop_sim(
            ClosedLoopConfig(
                policy_path=policy_path,
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
                winner_v3_sensor_noise_scales=transport["sensor_noise_scales"],
                winner_v3_native_quantization=bool(
                    transport["native_quantization"]
                ),
                winner_v3_additional_action_delay_ticks=int(
                    transport["additional_action_delay_ticks"]
                ),
                winner_v3_imu_delay_ticks=int(transport["imu_delay_ticks"]),
                winner_v3_home_relative_actuator_gain=True,
            )
        )
    trace = trace_audit(trace_path) if trace_path.exists() else missing_trace_audit(
        trace_path
    )
    response = (
        response_trace_audit(trace_path, result)
        if trace_path.exists()
        else {
            "checks": {},
            "failed_checks": ["trace_missing"],
            "pass": False,
            "context_sha256": None,
            "trace_rows": 0,
        }
    )
    readback = readback_checks(row, result, prereg)
    passed, failures, metrics = classify_cell(row, result, trace, readback)
    if not response["pass"]:
        failures.extend(
            f"response_{name}" for name in response["failed_checks"]
        )
        passed = False
    metrics["response_contract"] = response
    payload = {
        "schema_version": "winner_v103.response_conditioned_cell.v1",
        "status": (
            "PASS_WINNER_V103_RESPONSE_CONDITIONED_CELL"
            if passed
            else "HOLD_WINNER_V103_RESPONSE_CONDITIONED_CELL"
        ),
        "pass": passed,
        "failure_reasons": sorted(set(failures)),
        "identity": dict(row),
        "policy": {
            "path": str(policy_path),
            "sha256": policy_hashes[int(row["step"])],
        },
        "calibrator": {
            "path": str(calibrator),
            "sha256": CALIBRATOR_SHA256,
        },
        "actuator_plant_sha256": canonical_sha256(
            actuator_fit(prereg, str(row["plant"]))
        ),
        "metrics": metrics,
        "readback_checks": readback,
        "model_readback": (result.get("env") or {}).get(
            "winner_v3_configuration_readback"
        ),
        "actuator_sensor_transport_readback": (result.get("env") or {}).get(
            "winner_v3_actuator_sensor_transport_readback"
        ),
        "candidate_gate": result.get("candidate_gate"),
        "trace": trace,
        "response_contract": response,
        "training_or_simulator_reward_selection_weight": 0,
        "robot_clearance": False,
    }
    payload = json_finite(payload)
    path = CELLS / f"{stem}.json"
    path.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    payload["cell_path"] = str(path.relative_to(ROOT))
    payload["cell_sha256"] = sha256(path)
    return payload


def exception_cell(
    row: Mapping[str, Any],
    *,
    policy_paths: Mapping[int, Path],
    policy_hashes: Mapping[int, str],
    calibrator: Path,
    error: Exception,
) -> dict[str, Any]:
    stem = cell_stem(row)
    trace_path = TRACES / f"{stem}.jsonl"
    trace = missing_trace_audit(trace_path)
    response = {
        "checks": {},
        "failed_checks": ["runner_exception"],
        "pass": False,
        "context_sha256": None,
        "trace_rows": 0,
    }
    payload = {
        "schema_version": "winner_v103.response_conditioned_cell.v1",
        "status": "HOLD_WINNER_V103_RESPONSE_CONDITIONED_CELL",
        "pass": False,
        "failure_reasons": [f"runner_exception_{type(error).__name__}"],
        "error": f"{type(error).__name__}: {error}",
        "identity": dict(row),
        "policy": {
            "path": str(policy_paths[int(row["step"])]),
            "sha256": policy_hashes[int(row["step"])],
        },
        "calibrator": {
            "path": str(calibrator),
            "sha256": CALIBRATOR_SHA256,
        },
        "actuator_plant_sha256": None,
        "metrics": {
            "samples": 0,
            "termination_reason": "runner_exception",
            "candidate_gate_status": None,
            "mean_local_vx_m_s": None,
            "worst_tracking_p95_rad": float("inf"),
            "worst_current_p95_a": float("inf"),
            "checks": {"cpu_only": False},
            "response_contract": response,
        },
        "readback_checks": {"runner_exception": False},
        "model_readback": None,
        "actuator_sensor_transport_readback": None,
        "candidate_gate": None,
        "trace": trace,
        "response_contract": response,
        "training_or_simulator_reward_selection_weight": 0,
        "robot_clearance": False,
    }
    payload = json_finite(payload)
    path = CELLS / f"{stem}.json"
    path.write_text(
        json.dumps(payload, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    payload["cell_path"] = str(path.relative_to(ROOT))
    payload["cell_sha256"] = sha256(path)
    return payload


def write_condition(
    condition: Mapping[str, Any],
    cells: list[Mapping[str, Any]],
) -> dict[str, Any]:
    stem = f"{condition['group'].lower()}_{condition['id'].lower()}"
    passed = len(cells) == 16 and all(cell["pass"] for cell in cells)
    summary = {
        "schema_version": "winner_v103.response_conditioned_condition.v1",
        "status": (
            "PASS_WINNER_V103_RESPONSE_CONDITIONED_CONDITION"
            if passed
            else "HOLD_WINNER_V103_RESPONSE_CONDITIONED_CONDITION"
        ),
        "pass": passed,
        "condition": dict(condition),
        "cells": [
            {
                "step": cell["identity"]["step"],
                "plant": cell["identity"]["plant"],
                "command_x_m_s": cell["identity"]["command_x_m_s"],
                "pass": cell["pass"],
                "failure_reasons": cell["failure_reasons"],
                "worst_tracking_p95_rad": cell["metrics"][
                    "worst_tracking_p95_rad"
                ],
                "worst_current_p95_a": cell["metrics"]["worst_current_p95_a"],
                "mean_local_vx_m_s": cell["metrics"]["mean_local_vx_m_s"],
                "context_sha256": cell["response_contract"]["context_sha256"],
                "cell_path": cell["cell_path"],
                "cell_sha256": cell["cell_sha256"],
                "trace_path": cell["trace"]["path"],
                "trace_sha256": cell["trace"]["sha256"],
            }
            for cell in cells
        ],
    }
    json_path = CONDITIONS / f"{stem}.json"
    md_path = CONDITIONS / f"{stem}.md"
    json_path.write_text(
        json.dumps(summary, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        f"# Winner-v103 condition — {condition['id']}",
        "",
        f"Status: `{summary['status']}`",
        "",
        "| checkpoint | plant | command x | pass | tracking p95 | current p95 "
        "| mean vx | failures |",
        "|---:|---|---:|---|---:|---:|---:|---|",
    ]
    for cell in summary["cells"]:
        lines.append(
            f"| {cell['step']} | `{cell['plant']}` | "
            f"{cell['command_x_m_s']:.3f} | `{cell['pass']}` | "
            f"{cell['worst_tracking_p95_rad']:.9f} | "
            f"{cell['worst_current_p95_a']:.9f} | "
            f"{cell['mean_local_vx_m_s']} | "
            f"{', '.join(cell['failure_reasons']) or 'none'} |"
        )
    lines.extend(
        [
            "",
            "Training and simulator reward have zero selection weight.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "id": condition["id"],
        "group": condition["group"],
        "pass": summary["pass"],
        "json_path": str(json_path.relative_to(ROOT)),
        "json_sha256": sha256(json_path),
        "md_path": str(md_path.relative_to(ROOT)),
        "md_sha256": sha256(md_path),
    }


def validate_execution_preconditions(
    *,
    runner: Path,
    playground: Path,
    calibrator: Path,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise RuntimeError("CUDA_VISIBLE_DEVICES must be empty")
    if os.environ.get("JAX_PLATFORMS") != "cpu":
        raise RuntimeError("JAX_PLATFORMS must be cpu")
    contract = json.loads(RUNNER_CONTRACT.read_text(encoding="utf-8"))
    if (
        contract.get("status") != EXPECTED_RUNNER_CONTRACT_STATUS
        or contract.get("failed_checks") != []
        or contract.get("formal_behavior_cells_executed") != 0
        or contract.get("formal_runner_sha256") != sha256(runner)
        or contract.get("input_hashes", {}).get("v103_preregistration")
        != sha256(PREREG)
        or contract.get("input_hashes", {}).get("calibrator")
        != CALIBRATOR_SHA256
    ):
        raise RuntimeError("Winner-v103 runner contract is not current and passing")
    for name, expected in contract["supporting_tool_hashes"].items():
        if sha256(TOOLS / name) != expected:
            raise RuntimeError(f"supporting tool changed after contract: {name}")
    if sha256(calibrator) != CALIBRATOR_SHA256:
        raise RuntimeError("response calibrator hash changed")
    if not playground.exists():
        raise RuntimeError(f"composed playground is missing: {playground}")
    if any(
        path.exists()
        for path in (CELLS, TRACES, CONDITIONS, RESULT_JSON, RESULT_MD)
    ):
        raise RuntimeError("formal output exists; retry/resume/overwrite is forbidden")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("formal execution requires a clean worktree")
    prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    plan = matrix_plan(prereg)
    if (
        len(plan) != 1024
        or canonical_sha256(plan) != MATRIX_PLAN_SHA256
        or contract.get("matrix_plan_sha256") != MATRIX_PLAN_SHA256
    ):
        raise RuntimeError("formal matrix differs from the contracted plan")
    return contract, prereg, plan


def zero_cell_plan_contract() -> dict[str, Any]:
    prereg = json.loads(BASE_PREREG.read_text(encoding="utf-8"))
    plan = matrix_plan(prereg)
    conditions = condition_plan(prereg)
    group_counts = {
        group: sum(1 for row in plan if row["condition_group"] == group)
        for group in {row["condition_group"] for row in plan}
    }
    checks = {
        "matrix_count_exact_1024": len(plan) == 1024,
        "condition_count_exact_64": len(conditions) == 64,
        "matrix_plan_sha256_exact": canonical_sha256(plan)
        == MATRIX_PLAN_SHA256,
        "matrix_group_counts_exact": group_counts
        == {
            "NOMINAL": 32,
            "FIXED_ANCHOR": 384,
            "DISCOVERY": 256,
            "HELDOUT": 256,
            "SENSOR_TRANSPORT": 96,
        },
        "matrix_steps_exact": {int(row["step"]) for row in plan}
        == set(ELIGIBLE_STEPS),
        "matrix_plants_exact": {str(row["plant"]) for row in plan}
        == {"P30_ALL_JOINT", "P31_34_PITCH_WITH_P30_NONPITCH"},
        "matrix_commands_exact": {
            float(row["command_x_m_s"]) for row in plan
        }
        == {0.0, 0.074, 0.077, 0.08},
        "duration_exact_600": all(row["duration_ticks"] == 600 for row in plan),
        "formal_outputs_absent": not any(
            path.exists()
            for path in (CELLS, TRACES, CONDITIONS, RESULT_JSON, RESULT_MD)
        ),
    }
    return {
        "pass": all(checks.values()),
        "checks": checks,
        "failed_checks": sorted(name for name, passed in checks.items() if not passed),
        "formal_behavior_cells_executed": 0,
        "matrix_cells": len(plan),
        "condition_count": len(conditions),
        "matrix_plan_sha256": canonical_sha256(plan),
        "group_counts": group_counts,
        "response_cell_template": {
            "observation_dim": 115,
            "action_dim": 14,
            "policy_inputs": [
                "obs",
                "previous_action",
                "h_in",
                "calibration_context",
            ],
            "policy_outputs": [
                "continuous_actions",
                "previous_action_out",
                "h_out",
            ],
            "graph_authoritative_output": True,
            "calibration_ticks": 250,
            "home_return_ticks": 250,
            "calibrator_sha256": CALIBRATOR_SHA256,
            "scored_ticks": 600,
        },
        "selection_rule": {
            "both_checkpoints_must_pass_all_512": True,
            "selected_step_if_both_pass": ELIGIBLE_STEPS[-1],
            "no_closest_or_reward_selection": True,
        },
    }


def execute(
    *,
    artifact_json: Path,
    artifact_archive: Path,
    extract_root: Path,
    playground: Path,
    calibrator: Path,
) -> dict[str, Any]:
    runner = Path(__file__).resolve()
    contract, prereg, plan = validate_execution_preconditions(
        runner=runner,
        playground=playground,
        calibrator=calibrator,
    )
    hosted = load_hosted_artifact(
        artifact_json=artifact_json,
        artifact_archive=artifact_archive,
        extract_root=extract_root,
    )
    policy_paths = hosted.pop("policy_paths")
    policy_hashes = hosted.pop("policy_hashes")

    CELLS.mkdir(parents=True)
    TRACES.mkdir(parents=True)
    CONDITIONS.mkdir(parents=True)
    cells: list[dict[str, Any]] = []
    condition_rows = condition_plan(prereg)
    started = time.time()
    for index, condition in enumerate(condition_rows):
        rows = [
            row
            for row in plan
            if row["condition_group"] == condition["group"]
            and row["condition_id"] == condition["id"]
            and row["seed"] == condition["seed"]
        ]
        condition_cells = []
        for row in rows:
            try:
                cell = execute_cell(
                    row,
                    prereg,
                    policy_paths=policy_paths,
                    policy_hashes=policy_hashes,
                    playground=playground,
                    calibrator=calibrator,
                )
            except Exception as exc:
                cell = exception_cell(
                    row,
                    policy_paths=policy_paths,
                    policy_hashes=policy_hashes,
                    calibrator=calibrator,
                    error=exc,
                )
            cells.append(cell)
            condition_cells.append(cell)
        write_condition(condition, condition_cells)
        print(
            json.dumps(
                {
                    "completed_conditions": index + 1,
                    "total_conditions": len(condition_rows),
                    "completed_cells": len(cells),
                    "passing_cells": sum(cell["pass"] for cell in cells),
                    "elapsed_s": time.time() - started,
                }
            ),
            flush=True,
        )

    unique = {
        (
            cell["identity"]["condition_group"],
            cell["identity"]["condition_id"],
            cell["identity"]["seed"],
            cell["identity"]["step"],
            cell["identity"]["plant"],
            cell["identity"]["command_x_m_s"],
        )
        for cell in cells
    }
    validity = {
        "all_1024_cells_present_unique": len(cells) == 1024
        and len(unique) == 1024,
        "all_cell_trace_and_response_contracts_complete": all(
            cell["trace"]["rows"] == 600
            and cell["trace"]["ticks_contiguous"]
            and cell["trace"]["required_fields_every_tick"]
            and cell["trace"]["all_values_finite"]
            and cell["response_contract"]["pass"]
            and all(cell["readback_checks"].values())
            for cell in cells
        ),
        "all_policy_hashes_exact": all(
            cell["policy"]["sha256"]
            == policy_hashes[int(cell["identity"]["step"])]
            for cell in cells
        ),
        "all_calibrator_hashes_exact": all(
            cell["calibrator"]["sha256"] == CALIBRATOR_SHA256 for cell in cells
        ),
        "all_cpu_only": all(
            cell["metrics"]["checks"]["cpu_only"] for cell in cells
        ),
        "no_training_or_simulator_reward_selection": all(
            cell["training_or_simulator_reward_selection_weight"] == 0
            for cell in cells
        ),
        "all_cell_payloads_finite": all(finite_tree(cell) for cell in cells),
    }
    failed_validity = sorted(name for name, passed in validity.items() if not passed)
    per_checkpoint = {}
    for step in ELIGIBLE_STEPS:
        subset = [cell for cell in cells if int(cell["identity"]["step"]) == step]
        per_checkpoint[str(step)] = {
            "cells": len(subset),
            "passing_cells": sum(cell["pass"] for cell in subset),
            "all_512_cells_pass": len(subset) == 512
            and all(cell["pass"] for cell in subset),
            "worst_tracking_p95_rad": max(
                cell["metrics"]["worst_tracking_p95_rad"] for cell in subset
            ),
            "worst_current_p95_a": max(
                cell["metrics"]["worst_current_p95_a"] for cell in subset
            ),
            "minimum_moving_mean_vx_m_s": min(
                (
                    float(cell["metrics"]["mean_local_vx_m_s"])
                    for cell in subset
                    if float(cell["identity"]["command_x_m_s"]) > 0.0
                    and cell["metrics"]["mean_local_vx_m_s"] is not None
                ),
                default=-1.0e308,
            ),
            "policy_sha256": policy_hashes[step],
        }
    both_pass = not failed_validity and all(
        row["all_512_cells_pass"] for row in per_checkpoint.values()
    )
    selected = (
        {
            "label": "final",
            "full_domain_relative_step": ELIGIBLE_STEPS[-1],
            "locomotion_onnx_path": str(policy_paths[ELIGIBLE_STEPS[-1]]),
            "locomotion_onnx_sha256": policy_hashes[ELIGIBLE_STEPS[-1]],
            "calibrator_onnx_path": str(calibrator),
            "calibrator_onnx_sha256": CALIBRATOR_SHA256,
        }
        if both_pass
        else None
    )
    failures_by_reason: dict[str, int] = {}
    failures_by_group: dict[str, int] = {}
    for cell in cells:
        if cell["pass"]:
            continue
        group = cell["identity"]["condition_group"]
        failures_by_group[group] = failures_by_group.get(group, 0) + 1
        for reason in cell["failure_reasons"]:
            failures_by_reason[reason] = failures_by_reason.get(reason, 0) + 1
    result = {
        "schema_version": "winner_v103.response_conditioned_result.v1",
        "status": (
            "PASS_WINNER_V103_RESPONSE_CONDITIONED_RESULT"
            if both_pass
            else (
                "INVALID_WINNER_V103_RESPONSE_CONDITIONED_RESULT"
                if failed_validity
                else "HOLD_WINNER_V103_RESPONSE_CONDITIONED_RESULT"
            )
        ),
        "decision": (
            "SELECT_FINAL_RESPONSE_CONDITIONED_CHECKPOINT"
            if both_pass
            else "NO_RESPONSE_CONDITIONED_CHECKPOINT_SELECTED"
        ),
        "selected_policy": selected,
        "robot_clearance": both_pass,
        "validity_checks": validity,
        "failed_validity_checks": failed_validity,
        "cells": len(cells),
        "passing_cells": sum(cell["pass"] for cell in cells),
        "failing_cells": sum(not cell["pass"] for cell in cells),
        "per_checkpoint": per_checkpoint,
        "failures_by_group": dict(sorted(failures_by_group.items())),
        "failures_by_reason": dict(sorted(failures_by_reason.items())),
        "hosted_artifact": hosted,
        "matrix_plan_sha256": MATRIX_PLAN_SHA256,
        "runner_sha256": sha256(runner),
        "runner_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "runner_contract_sha256": sha256(RUNNER_CONTRACT),
        "preregistration_sha256": sha256(PREREG),
        "wall_seconds": time.time() - started,
        "training_or_simulator_reward_selection_weight": 0,
        "no_closest_promotion": True,
        "authority": {
            "selected_asset_freeze_and_gate5_preparation": both_pass,
            "robot_clearance": both_pass,
            "runtime_or_gate5_execution": False,
            "rdkx5_or_robot_access": False,
            "torque_or_motion": False,
            "grounded_walking": False,
            "training_or_retry": False,
        },
    }
    result = json_finite(result)
    RESULT_JSON.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Winner-v103 response-conditioned result",
        "",
        f"Status: `{result['status']}`",
        f"Decision: `{result['decision']}`",
        f"Robot clearance: `{result['robot_clearance']}`",
        "",
        f"Cells: `{result['passing_cells']}/{result['cells']}` pass.",
        "",
        "| checkpoint | cells | passing | all pass | worst tracking p95 "
        "| worst current p95 | minimum moving vx |",
        "|---:|---:|---:|---|---:|---:|---:|",
    ]
    for step in ELIGIBLE_STEPS:
        item = per_checkpoint[str(step)]
        lines.append(
            f"| {step} | {item['cells']} | {item['passing_cells']} | "
            f"`{item['all_512_cells_pass']}` | "
            f"{item['worst_tracking_p95_rad']:.9f} | "
            f"{item['worst_current_p95_a']:.9f} | "
            f"{item['minimum_moving_mean_vx_m_s']:.9f} |"
        )
    lines.extend(
        [
            "",
            "Both persistent checkpoints must pass all 512 cells. Only the fixed "
            "final checkpoint is selected when both pass; no reward, closest "
            "metric, or aggregate score can promote a failure.",
            "",
            "A pass permits selected-asset freezing and CPU/mock Gate 5 "
            "preparation only. It does not itself authorize RDK-X5 access, torque, "
            "motion, suspended replay, or grounded walking.",
            "",
        ]
    )
    RESULT_MD.write_text("\n".join(lines), encoding="utf-8")
    return result


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", required=True)
    parser.add_argument("--artifact-json", type=Path, required=True)
    parser.add_argument("--artifact-archive", type=Path, required=True)
    parser.add_argument("--extract-root", type=Path, required=True)
    parser.add_argument("--playground", type=Path, required=True)
    parser.add_argument("--calibrator", type=Path, required=True)
    args = parser.parse_args(argv)
    result = execute(
        artifact_json=args.artifact_json.resolve(),
        artifact_archive=args.artifact_archive.resolve(),
        extract_root=args.extract_root.resolve(),
        playground=args.playground.resolve(),
        calibrator=args.calibrator.resolve(),
    )
    print(
        json.dumps(
            {"status": result["status"], "decision": result["decision"]}
        )
    )
    return 0 if not result["failed_validity_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
