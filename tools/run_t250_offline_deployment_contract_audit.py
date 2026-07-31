#!/usr/bin/env python3
"""Run the preregistered T250 CPU-only deployment-contract audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable, Mapping

import numpy as np
import onnx
import onnxruntime as ort


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "outputs" / "analysis"
PREREG = ANALYSIS / "t250_offline_deployment_contract_audit_preregistration.json"
RESULT = ANALYSIS / "t250_offline_deployment_contract_audit_result.json"
HANDOFF = ANALYSIS / "t250_gate5_policy_handoff_manifest.json"
MARKDOWN = ANALYSIS / "T250_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT_RESULT_20260731.md"
sys.path.insert(0, str(ROOT / "tools"))
from run_t136_static_calibration_router_transform import (  # noqa: E402
    canonical_sha256,
    receipt,
    sha256,
)


EXPECTED_HANDOFF_CHECKS = {
    "applied_target_observer_preserved",
    "applied_target_slot_continuity",
    "calibration_ticks_exact",
    "calibrator_sha_exact",
    "context_finite",
    "context_immutable",
    "context_shape",
    "first_hidden_zero",
    "first_previous_action_matches_calibration",
    "full_observation_traced",
    "graph_authoritative_no_host_delta",
    "handoff_state_preserved",
    "phase_reset_exact",
    "policy_hidden_zero",
    "previous_action_preserved",
    "recurrent_state_chains_exact",
    "response_enabled",
    "zero_home_return_ticks",
}
POLICY_INPUTS = {
    "obs": [1, 115],
    "previous_action": [1, 14],
    "h_in": [1, 64],
    "calibration_context": [1, 64],
}
POLICY_OUTPUTS = {
    "continuous_actions": [1, 14],
    "previous_action_out": [1, 14],
    "h_out": [1, 64],
}
CALIBRATOR_INPUTS = {
    "obs": [1, 115],
    "previous_action": [1, 14],
    "h_in": [1, 64],
}
CALIBRATOR_OUTPUTS = {
    "calibration_actions": [1, 14],
    "previous_action_out": [1, 14],
    "h_out": [1, 64],
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_receipt(value: Mapping[str, Any]) -> Path:
    path = Path(value["path"])
    if (
        not path.is_file()
        or path.stat().st_size != int(value["bytes"])
        or sha256(path) != value["sha256"]
    ):
        raise RuntimeError(f"changed T250 input: {path}")
    return path


def shape_of(value: Any) -> list[int | str | None]:
    return [item if isinstance(item, (int, str)) else None for item in value.shape]


def inspect_graph(
    path: Path,
    expected_inputs: Mapping[str, list[int]],
    expected_outputs: Mapping[str, list[int]],
    *,
    chain_ticks: int,
    context: np.ndarray | None = None,
) -> dict[str, Any]:
    model = onnx.load(str(path))
    onnx.checker.check_model(model)
    options = ort.SessionOptions()
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(
        str(path), sess_options=options, providers=["CPUExecutionProvider"]
    )
    inputs = {row.name: shape_of(row) for row in session.get_inputs()}
    outputs = {row.name: shape_of(row) for row in session.get_outputs()}
    checks = {
        "input_names_and_shapes_exact": inputs == dict(expected_inputs),
        "output_names_and_shapes_exact": outputs == dict(expected_outputs),
        "input_order_exact": [row.name for row in session.get_inputs()]
        == list(expected_inputs),
        "output_order_exact": [row.name for row in session.get_outputs()]
        == list(expected_outputs),
        "all_inputs_float32": all(row.type == "tensor(float)" for row in session.get_inputs()),
        "all_outputs_float32": all(row.type == "tensor(float)" for row in session.get_outputs()),
        "cpu_provider_only": session.get_providers() == ["CPUExecutionProvider"],
        "onnx_checker_passes": True,
    }
    if not all(checks.values()):
        raise RuntimeError(f"ONNX ABI check failed for {path}: {checks}")

    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)
    rng = np.random.default_rng(250_200_704)
    context_before = None if context is None else hashlib.sha256(context.tobytes()).hexdigest()
    max_abs_action = 0.0
    for tick in range(chain_ticks):
        obs = rng.normal(0.0, 0.05, size=(1, 115)).astype(np.float32)
        obs[:, 3:6] = np.asarray([0.0, 0.0, 9.81], dtype=np.float32)
        obs[:, 6:13] = 0.0
        obs[:, 6] = np.float32((0.0, 0.074, 0.077, 0.08)[tick % 4])
        obs[:, 97:99] = 1.0
        angle = np.float32((tick % 50) * (2.0 * np.pi / 50.0))
        obs[:, 99] = np.cos(angle, dtype=np.float32)
        obs[:, 100] = np.sin(angle, dtype=np.float32)
        feed = {"obs": obs, "previous_action": previous, "h_in": hidden}
        if context is not None:
            feed["calibration_context"] = context
            names = ["continuous_actions", "previous_action_out", "h_out"]
        else:
            names = ["calibration_actions", "previous_action_out", "h_out"]
        action, previous_out, hidden_out = session.run(names, feed)
        if not (
            action.shape == (1, 14)
            and previous_out.shape == (1, 14)
            and hidden_out.shape == (1, 64)
            and np.all(np.isfinite(action))
            and np.all(np.isfinite(previous_out))
            and np.all(np.isfinite(hidden_out))
            and np.array_equal(action, previous_out)
        ):
            raise RuntimeError(f"stateful chain failed for {path} at tick {tick}")
        max_abs_action = max(max_abs_action, float(np.max(np.abs(action))))
        previous = previous_out.astype(np.float32, copy=True)
        hidden = hidden_out.astype(np.float32, copy=True)
    context_after = None if context is None else hashlib.sha256(context.tobytes()).hexdigest()
    chain_checks = {
        "chain_ticks_exact": chain_ticks,
        "outputs_finite": True,
        "action_equals_previous_action_out": True,
        "context_immutable": context_before == context_after,
        "max_abs_action": max_abs_action,
    }
    return {
        "artifact": receipt(path),
        "inputs": inputs,
        "outputs": outputs,
        "node_count": len(model.graph.node),
        "initializer_count": len(model.graph.initializer),
        "opsets": {str(row.domain): int(row.version) for row in model.opset_import},
        "abi_checks": checks,
        "chain": chain_checks,
        "final_previous_action": previous[0].astype(float).tolist(),
        "final_hidden_sha256": hashlib.sha256(hidden.tobytes()).hexdigest(),
    }


def calibrator_context(path: Path) -> tuple[np.ndarray, dict[str, Any]]:
    audit = inspect_graph(
        path,
        CALIBRATOR_INPUTS,
        CALIBRATOR_OUTPUTS,
        chain_ticks=250,
    )
    options = ort.SessionOptions()
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(
        str(path), sess_options=options, providers=["CPUExecutionProvider"]
    )
    previous = np.zeros((1, 14), dtype=np.float32)
    hidden = np.zeros((1, 64), dtype=np.float32)
    obs = np.zeros((1, 115), dtype=np.float32)
    obs[:, 3:6] = np.asarray([0.0, 0.0, 9.81], dtype=np.float32)
    obs[:, 97:99] = 1.0
    obs[:, 99] = 1.0
    for _ in range(250):
        action, previous, hidden = session.run(
            ["calibration_actions", "previous_action_out", "h_out"],
            {"obs": obs, "previous_action": previous, "h_in": hidden},
        )
        if not np.array_equal(action, previous):
            raise RuntimeError("calibrator action/previous_action_out mismatch")
    audit["synthetic_context_sha256"] = hashlib.sha256(hidden.tobytes()).hexdigest()
    audit["synthetic_context_finite"] = bool(np.all(np.isfinite(hidden)))
    return hidden.astype(np.float32, copy=True), audit


def handoff_checks(value: Mapping[str, Any]) -> bool:
    checks = value.get("checks") or {}
    return (
        value.get("all_checks_pass") is True
        and EXPECTED_HANDOFF_CHECKS.issubset(checks)
        and all(checks[name] is True for name in EXPECTED_HANDOFF_CHECKS)
    )


def iter_t249_evaluations(t249b: Mapping[str, Any]) -> Iterable[tuple[dict[str, Any], dict[str, Any]]]:
    for row in t249b["block_manifests"]:
        manifest_path = verify_receipt(row["manifest"])
        manifest = load(manifest_path)
        evaluation_path = verify_receipt(manifest["evaluation"])
        yield manifest, load(evaluation_path)


def main() -> int:
    for path in (RESULT, HANDOFF, MARKDOWN):
        if path.exists():
            raise FileExistsError("refusing to overwrite T250 result")
    if subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip():
        raise RuntimeError("T250 execution requires a clean worktree")

    prereg = load(PREREG)
    prereg_basis = {
        key: value
        for key, value in prereg.items()
        if key != "preregistered_contract_sha256"
    }
    if (
        prereg["status"]
        != "PREREGISTERED_T250_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT"
        or prereg["failed_checks"]
        or canonical_sha256(prereg_basis)
        != prereg["preregistered_contract_sha256"]
    ):
        raise RuntimeError("T250 preregistration changed")
    frozen_paths = {
        name: verify_receipt(value)
        for name, value in prereg["frozen_inputs"].items()
    }
    t249b = load(frozen_paths["t249b_full_r2_result"])
    t249 = load(frozen_paths["t249_execution_contract"])
    t247 = load(frozen_paths["t247_transform_result"])
    t247b = load(frozen_paths["t247_reporting_recovery"])
    t8 = load(frozen_paths["t8_handoff_result"])

    t249b_basis = {
        key: value for key, value in t249b.items() if key != "result_sha256"
    }
    policies = sorted(t249["policies"], key=lambda row: int(row["step"]))
    selected = policies[-1]
    witness = policies[0]
    selected_path = verify_receipt(selected)
    witness_path = verify_receipt(witness)
    calibrator_path = verify_receipt(t249["calibrator"])
    reference_path = verify_receipt(t249["reference_feature_table"])
    fit_paths = {row["fit_id"]: verify_receipt(row) for row in t249["fits"]}

    context, calibrator_audit = calibrator_context(calibrator_path)
    policy_audits = {
        "persistence_witness": inspect_graph(
            witness_path,
            POLICY_INPUTS,
            POLICY_OUTPUTS,
            chain_ticks=256,
            context=context,
        ),
        "deployment_terminal": inspect_graph(
            selected_path,
            POLICY_INPUTS,
            POLICY_OUTPUTS,
            chain_ticks=256,
            context=context,
        ),
    }

    t237 = load(Path(t249["reused_evidence"]["conditions_1_through_16"]["path"]))
    t248 = load(Path(t249["reused_evidence"]["condition_17"]["path"]))
    inherited_cells = []
    for block in t237["blocks"]:
        if int(block["condition_index"]) <= 16:
            inherited_cells.extend(block["result"]["cells"])
    for block in t248["blocks"]:
        inherited_cells.extend(block["result"]["cells"])
    inherited_handoff_green = all(
        cell["cell_green"] and handoff_checks(cell["handoff"])
        for cell in inherited_cells
    )

    fresh_runs: list[dict[str, Any]] = []
    selected_golden_manifest = None
    selected_golden_evaluation = None
    for manifest, evaluation in iter_t249_evaluations(t249b):
        for run in evaluation["runs"]:
            response = run["response_calibration"]
            response_green = (
                response["enabled"]
                and response["calibration_ticks"] == 250
                and response["home_return_ticks"] == 0
                and response["handoff_state_preserved"]
                and response["locomotion_hidden_exact_zero"]
                and response["locomotion_previous_action_matches_calibration"]
                and response["applied_target_observation_matches_bridge"]
                and response["locomotion_phase_reset"] == [1.0, 0.0]
                and response["context_shape"] == [1, 64]
                and response["context_finite"]
            )
            fresh_runs.append(
                {
                    "condition_id": manifest["block_contract"]["condition"]["id"],
                    "checkpoint_id": manifest["block_contract"]["policy"]["checkpoint_id"],
                    "fit_id": manifest["block_contract"]["fit"]["fit_id"],
                    "command_x": float(run["command_x"]),
                    "status": run["status"],
                    "response_handoff_green": bool(response_green),
                }
            )
        contract = manifest["block_contract"]
        if (
            contract["condition"]["id"] == "KP_HI"
            and contract["policy"]["checkpoint_id"] == selected["checkpoint_id"]
            and contract["fit"]["fit_id"] == "p30"
        ):
            selected_golden_manifest = manifest
            selected_golden_evaluation = evaluation

    if selected_golden_manifest is None or selected_golden_evaluation is None:
        raise RuntimeError("T250 frozen golden block not found")
    golden_run = next(
        row
        for row in selected_golden_evaluation["runs"]
        if float(row["command_x"]) == 0.074
    )
    golden_trace_receipt = next(
        row
        for row in selected_golden_manifest["traces"]
        if "x0.074_" in Path(row["path"]).name
    )
    golden_trace_path = verify_receipt(golden_trace_receipt)
    with golden_trace_path.open("r", encoding="utf-8") as stream:
        golden_row = json.loads(stream.readline())
    golden_obs = np.asarray(golden_row["obs_state"], dtype=np.float32)
    golden_previous = np.asarray(
        golden_row["policy_state_input"]["previous_action"], dtype=np.float32
    )
    golden_hidden = np.asarray(
        golden_row["policy_state_input"]["h_in"], dtype=np.float32
    )
    golden_action = np.asarray(golden_row["action"], dtype=np.float32)
    golden_previous_out = np.asarray(
        golden_row["policy_state_output"]["previous_action_out"], dtype=np.float32
    )
    response = golden_run["response_calibration"]
    calibration_final = np.asarray(response["calibration_final_action"], dtype=np.float32)
    observer_target = np.asarray(
        response["observer_bridge_applied_target_rad"], dtype=np.float32
    )
    golden_checks = {
        "tick_zero": golden_row["tick"] == 0,
        "observation_shape_115": golden_obs.shape == (115,),
        "command_exact": np.array_equal(
            golden_obs[6:13],
            np.asarray([0.074, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32),
        ),
        "history_41_55_preserved": np.array_equal(golden_obs[41:55], calibration_final),
        "history_55_69_preserved": np.array_equal(golden_obs[55:69], calibration_final),
        "history_69_83_preserved": np.array_equal(golden_obs[69:83], calibration_final),
        "p30_observer_83_97_preserved": np.array_equal(golden_obs[83:97], observer_target),
        "phase_reset_exact": np.array_equal(
            golden_obs[99:101], np.asarray([1.0, 0.0], dtype=np.float32)
        ),
        "projected_reference_present": bool(np.count_nonzero(golden_obs[101:115])),
        "locomotion_hidden_zero": np.count_nonzero(golden_hidden) == 0,
        "previous_action_matches_calibrator": np.array_equal(
            golden_previous, calibration_final[None, :]
        ),
        "context_hash_matches_handoff": (
            golden_row["policy_calibration_context_sha256"]
            == response["context_sha256"]
        ),
        "graph_action_authoritative": (
            golden_row["policy_graph_authoritative_output"] is True
            and float(golden_row["policy_host_action_delta_max_abs"]) == 0.0
            and np.array_equal(golden_action[None, :], golden_previous_out)
        ),
    }
    golden_checks = {name: bool(value) for name, value in golden_checks.items()}

    checks = {
        "t249b_result_hash_canonical": (
            canonical_sha256(t249b_basis) == t249b["result_sha256"]
        ),
        "twenty_conditions_and_320_cells_green": (
            t249b["summary"]["all_twenty_conditions_green"]
            and t249b["summary"]["green_conditions"] == 20
            and t249b["summary"]["green_cells"] == 320
        ),
        "inherited_272_cells_handoff_green": (
            len(inherited_cells) == 272 and inherited_handoff_green
        ),
        "fresh_48_cells_handoff_green": (
            len(fresh_runs) == 48
            and all(row["response_handoff_green"] for row in fresh_runs)
        ),
        "all_fresh_worker_runs_complete": all(
            row["status"] == "COMPLETE" for row in fresh_runs
        ),
        "t247_route_exactness_recovered": (
            t247["checks"]["stateful_abi_exact"]
            and t247["checks"]["onnx_checker_passes"]
            and t247b["status"] == "PASS_T247B_REPORTING_RECOVERY"
            and all(t247b["checks"].values())
        ),
        "t8_handoff_contract_green": t8["summary"]["all_handoff_contracts_pass"],
        "calibrator_abi_and_chain_green": (
            all(calibrator_audit["abi_checks"].values())
            and calibrator_audit["chain"]["outputs_finite"]
            and calibrator_audit["synthetic_context_finite"]
        ),
        "both_policy_abis_and_chains_green": all(
            all(row["abi_checks"].values())
            and row["chain"]["outputs_finite"]
            and row["chain"]["action_equals_previous_action_out"]
            and row["chain"]["context_immutable"]
            for row in policy_audits.values()
        ),
        "terminal_checkpoint_selected_by_frozen_rule": (
            selected["checkpoint_id"]
            == prereg["selection_rule"]["selected_checkpoint_id"]
            and int(selected["step"]) == 2_007_040
            and selected["sha256"]
            == prereg["selection_rule"]["selected_sha256"]
        ),
        "golden_first_locomotion_tick_exact": all(golden_checks.values()),
        "p30_observer_fit_present": "p30" in fit_paths,
        "p31_34_robustness_fit_present": "p31_34" in fit_paths,
        "reference_table_present": reference_path.is_file(),
        "zero_simulator_optimizer_hosted_or_robot": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failed = sorted(name for name, passed in checks.items() if not passed)
    passed = not failed

    observation_contract = [
        {"slice": [0, 3], "meaning": "body gyroscope rad/s"},
        {"slice": [3, 6], "meaning": "body accelerometer m/s^2"},
        {"slice": [6, 13], "meaning": "seven-value command"},
        {"slice": [13, 27], "meaning": "joint position minus home rad"},
        {"slice": [27, 41], "meaning": "joint velocity times 0.05"},
        {"slice": [41, 55], "meaning": "final action t-2 during steady locomotion"},
        {"slice": [55, 69], "meaning": "final action t-3 during steady locomotion"},
        {"slice": [69, 83], "meaning": "final action t-4 during steady locomotion"},
        {"slice": [83, 97], "meaning": "fixed-P30 observer realized absolute target rad"},
        {"slice": [97, 99], "meaning": "left/right contacts"},
        {"slice": [99, 101], "meaning": "cosine/sine phase"},
        {"slice": [101, 115], "meaning": "projected reference action"},
    ]
    handoff_basis: dict[str, Any] = {
        "schema_version": "open_duck.t250_gate5_policy_handoff_manifest.v1",
        "status": "AUDITED_POLICY_HANDOFF" if passed else "HOLD_POLICY_HANDOFF",
        "deployment_selection": {
            "rule": "terminal checkpoint at the preregistered 2,007,040-step export",
            "policy": receipt(selected_path),
            "checkpoint_id": selected["checkpoint_id"],
            "step": int(selected["step"]),
            "persistence_witness": receipt(witness_path),
            "persistence_witness_checkpoint_id": witness["checkpoint_id"],
            "metric_ranking_or_cherry_pick": False,
        },
        "required_artifacts": {
            "calibrator": receipt(calibrator_path),
            "projected_reference_table": receipt(reference_path),
            "fixed_p30_runtime_observer_fit": receipt(fit_paths["p30"]),
        },
        "evidence_only_artifacts": {
            "p31_34_physical_robustness_fit": receipt(fit_paths["p31_34"]),
            "full_r2_result": receipt(frozen_paths["t249b_full_r2_result"]),
            "golden_first_locomotion_trace": receipt(golden_trace_path),
        },
        "policy_abi": {
            "inputs": POLICY_INPUTS,
            "outputs": POLICY_OUTPUTS,
            "dtype": "float32",
            "graph_action_is_authoritative": True,
            "continuous_actions_equals_previous_action_out": True,
            "host_action_delta": "forbidden",
        },
        "calibrator_abi": {
            "inputs": CALIBRATOR_INPUTS,
            "outputs": CALIBRATOR_OUTPUTS,
            "dtype": "float32",
        },
        "observation_contract": observation_contract,
        "action_contract": {
            "joint_order": [
                "left_hip_yaw", "left_hip_roll", "left_hip_pitch",
                "left_knee", "left_ankle", "right_hip_yaw",
                "right_hip_roll", "right_hip_pitch", "right_knee",
                "right_ankle", "neck_yaw", "head_pitch",
                "head_roll", "head_yaw",
            ],
            "normalized_action_shape": [1, 14],
            "absolute_target": "home_rad + 0.25 * final_action",
            "inherited_absolute_target_slew_rad_s": 5.24,
            "envelope_monitor_rad_s": 3.75,
        },
        "two_stage_handoff": {
            "calibration_ticks": 250,
            "calibration_observation_command_6_13": [0.0] * 7,
            "calibration_observation_phase_99_101": [1.0, 0.0],
            "calibration_observation_reference_101_115": [0.0] * 14,
            "home_return_ticks": 0,
            "physical_joint_sensor_contact_and_imu_state": "preserved",
            "fixed_p30_observer_state": "preserved",
            "action_history": "preserve final three calibrator actions",
            "locomotion_previous_action": "final calibrator previous_action_out",
            "locomotion_hidden_h_in": [0.0] * 64,
            "calibration_context": "final calibrator h_out, immutable during locomotion",
            "locomotion_phase_99_101": [1.0, 0.0],
            "locomotion_command": "operator-requested command",
            "first_locomotion_observation": "refresh after phase reset with preserved physical and observer state",
        },
        "runtime_integration_boundary": {
            "versioned_115d_path_default_enabled": False,
            "frozen_101d_v1_contract_changed": False,
            "policy_or_calibrator_binary_committed": False,
            "p31_34_used_to_switch_runtime_observer": False,
            "must_pass_offline_runtime_equivalence_before_x5_staging": True,
            "must_pass_no_motion_x5_cpu_inference_and_timing_before_gate5": True,
        },
        "authority": {
            "versioned_runtime_integration_preregistration": passed,
            "policy_binary_staging": False,
            "x5_execution": False,
            "gate5": False,
            "robot_motion": False,
            "grounded_replay": False,
        },
    }
    handoff = {**handoff_basis, "handoff_sha256": canonical_sha256(handoff_basis)}
    HANDOFF.write_text(
        json.dumps(handoff, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    result_basis: dict[str, Any] = {
        "schema_version": "open_duck.t250_offline_deployment_contract_audit_result.v1",
        "status": (
            "PASS_T250_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT"
            if passed
            else "HOLD_T250_OFFLINE_DEPLOYMENT_CONTRACT_AUDIT"
        ),
        "decision": (
            prereg["decision_rule"]["pass"]
            if passed
            else prereg["decision_rule"]["fail"]
        ),
        "preregistered_contract_sha256": prereg["preregistered_contract_sha256"],
        "full_r2": {
            "conditions": 20,
            "cells": 320,
            "green_cells": int(t249b["summary"]["green_cells"]),
            "both_checkpoints": True,
            "both_measured_fits": True,
            "commands_x_m_s": [0.0, 0.074, 0.077, 0.08],
        },
        "selected_policy": receipt(selected_path),
        "persistence_witness": receipt(witness_path),
        "calibrator": calibrator_audit,
        "policy_graphs": policy_audits,
        "handoff_population": {
            "inherited_cells": len(inherited_cells),
            "fresh_cells": len(fresh_runs),
            "total_cells": len(inherited_cells) + len(fresh_runs),
        },
        "golden_first_locomotion_tick": {
            "trace": receipt(golden_trace_path),
            "checks": golden_checks,
            "calibration_final_action": calibration_final.astype(float).tolist(),
            "p30_observer_target_rad": observer_target.astype(float).tolist(),
            "context_sha256": response["context_sha256"],
        },
        "checks": checks,
        "failed_checks": failed,
        "handoff_manifest": receipt(HANDOFF),
        "execution": {
            "platform": "cpu",
            "calibrator_chain_ticks": 250,
            "policy_chain_ticks": 512,
            "simulator_steps": 0,
            "behavior_cells": 0,
            "optimizer_steps": 0,
            "hosted_compute_units": 0,
            "robot_or_rdk_access": 0,
        },
        "authority": {
            "versioned_runtime_integration_preregistration": passed,
            "training": False,
            "hosted": False,
            "policy_staging": False,
            "gate5": False,
            "rdkx5_or_robot": False,
        },
    }
    result = {**result_basis, "result_sha256": canonical_sha256(result_basis)}
    RESULT.write_text(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    MARKDOWN.write_text(
        "# T250 offline deployment-contract audit result\n\n"
        f"- Status: `{result['status']}`\n"
        f"- Decision: `{result['decision']}`\n"
        "- Full R2: `20/20 conditions; 320/320 cells`\n"
        f"- Selected policy SHA-256: `{selected['sha256']}`\n"
        "- Handoff: `250 calibration; 0 home return; preserved previous action/observer; zero locomotion hidden; phase 0`\n"
        "- Frozen 101-D runtime changed: `NO`\n"
        "- Simulator/optimizer/hosted/robot: `0/0/0/0`\n"
        "- Gate 5: `NOT_AUTHORIZED`\n"
        f"- Result SHA-256: `{result['result_sha256']}`\n"
        f"- Handoff SHA-256: `{handoff['handoff_sha256']}`\n",
        encoding="utf-8",
        newline="\n",
    )
    print(result["status"])
    print(f"decision={result['decision']}")
    print(f"result_sha256={result['result_sha256']}")
    print(f"handoff_sha256={handoff['handoff_sha256']}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
