#!/usr/bin/env python3
"""Execute the preregistered CPU-only oracle COM corrective-authority screen."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np

from actuator_bridge_model import ActuatorBridgeModel, load_fit_json, params_from_fit
from closed_loop_sim_eval import ClosedLoopConfig, quat_wxyz_to_pitch, quat_wxyz_to_roll, run_closed_loop_sim
from oracle_phase_com_controller import CORRECTED_JOINT_INDICES, project_combined_action


ROOT = Path(__file__).resolve().parents[1]
PLAYGROUND = Path("/tmp/ground_up_reset_estimator_eval_composed_20260715")
REFERENCE = ROOT / "outputs/analysis/ground_up_projected_reference_feature_table.npz"
FIT = ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
TRACE_ROOT = ROOT / "outputs/analysis/oracle_phase_com_compensation_traces/authority_design"
POLICIES = (
    ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_512000.onnx",
    ROOT / "outputs/analysis/ground_up_dual_fit_conservative_envelope_repair_policies/T2_EQUAL_1024000.onnx",
)
ENDPOINTS = (("X_NEG", -0.05), ("X_POS", 0.05))
TICKS = (0, 4, 8, 12, 16, 20, 24, 28, 32, 36)
HORIZON = 8
AMPLITUDES = (-0.08, -0.04, 0.04, 0.08)
MAX_ACTION_DELTA = np.asarray(
    [.41919997, .41919997, .12, .12, .12, .41919997, .41919997,
     .41919997, .41919997, .41919997, .41919997, .10, .08, .10],
    dtype=np.float64,
)
PITCH_LIMITS = np.asarray([1.5, 1.5, 1.5, 1.25, 1.0, 1.25], dtype=np.float64)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def clone_bridge(source: ActuatorBridgeModel) -> ActuatorBridgeModel:
    output = ActuatorBridgeModel(source.params, initial_target=source.value)
    output._queues = [queue.copy() for queue in source._queues]  # noqa: SLF001
    return output


def initialize_native() -> tuple[Any, Any]:
    import jax
    import mujoco

    if jax.default_backend() != "cpu" or any(device.platform != "cpu" for device in jax.devices()):
        raise RuntimeError(f"non-CPU JAX device: {jax.devices()}")
    sys.path.insert(0, str(PLAYGROUND))
    old = Path.cwd()
    os.chdir(PLAYGROUND)
    try:
        from playground.open_duck_mini_v2 import joystick

        config = joystick.default_config()
        config.reference_feature_table_path = str(REFERENCE.resolve())
        overrides = {
            "push_config.enable": False,
            "lin_vel_x": [0.077, 0.077],
            "lin_vel_y": [0.0, 0.0],
            "ang_vel_yaw": [0.0, 0.0],
            "neck_pitch_range": [0.0, 0.0],
            "head_pitch_range": [0.0, 0.0],
            "head_yaw_range": [0.0, 0.0],
            "head_roll_range": [0.0, 0.0],
            "noise_config.level": 0.0,
            "noise_config.action_min_delay": 0,
            "noise_config.action_max_delay": 1,
            "noise_config.imu_min_delay": 0,
            "noise_config.imu_max_delay": 1,
        }
        env = joystick.Joystick(task="flat_terrain_backlash", config=config, config_overrides=overrides)
    finally:
        os.chdir(old)
    return mujoco, env


def endpoint_model(mujoco: Any, nominal: Any, offset: float) -> Any:
    model = copy.copy(nominal)
    body_id = int(model.body("trunk_assembly").id)
    before = np.asarray(model.body_ipos).copy()
    model.body_ipos[body_id, 0] += float(offset)
    changed = np.argwhere(np.asarray(model.body_ipos) != before).tolist()
    if body_id != 2 or changed != [[2, 0]]:
        raise ValueError(f"invalid COM intervention: body={body_id}, changed={changed}")
    return model


def reconstruct_bridge(rows: list[dict[str, Any]], fit: dict[str, Any], home: np.ndarray, tick: int) -> tuple[ActuatorBridgeModel, np.ndarray, float]:
    bridge = ActuatorBridgeModel(params_from_fit(fit), initial_target=home)
    maximum_error = 0.0
    for row in rows[:tick]:
        applied = bridge.step(row["sent_target_rad"], 0.02)
        maximum_error = max(maximum_error, float(np.max(np.abs(applied - np.asarray(row["applied_target_rad"])))))
    previous_sent = home.copy() if tick == 0 else np.asarray(rows[tick - 1]["sent_target_rad"], dtype=float)
    return bridge, previous_sent, maximum_error


def source_state(rows: list[dict[str, Any]], tick: int, env: Any) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if tick == 0:
        actual = np.asarray(env.get_actuator_joints_qpos(env._init_q), dtype=float)
        return np.asarray(env._init_q, dtype=float), np.zeros(env.mj_model.nv), np.asarray(env._default_actuator, dtype=float), actual
    prior = rows[tick - 1]
    return (
        np.asarray(prior["qpos"], dtype=float),
        np.asarray(prior["qvel"], dtype=float),
        np.asarray(prior["ctrl"], dtype=float),
        np.asarray(prior["actual_position_rad"], dtype=float),
    )


def simulate_branch(
    *, mujoco: Any, model: Any, env: Any, rows: list[dict[str, Any]], tick: int,
    residual_joint: int | None, amplitude: float, bridge: ActuatorBridgeModel,
    previous_sent: np.ndarray,
) -> dict[str, Any]:
    qpos, qvel, ctrl, _actual = source_state(rows, tick, env)
    data = mujoco.MjData(model)
    mujoco.mj_setConst(model, data)
    data.qpos[:] = qpos
    data.qvel[:] = qvel
    data.ctrl[:] = ctrl
    mujoco.mj_forward(model, data)
    home = np.asarray(env._default_actuator, dtype=float)
    action_scale = float(env._config.action_scale)
    joint_ids = np.asarray(model.actuator_trnid[:, 0], dtype=int)
    qpos_addrs = np.asarray(model.jnt_qposadr[joint_ids], dtype=int)
    previous_final = np.zeros(14, dtype=np.float32) if tick == 0 else np.asarray(rows[tick - 1]["action"], dtype=np.float32)
    sent = previous_sent.copy()
    pitch, roll, height, com_distance, tracking = [], [], [], [], []
    actions, sent_rows, applied_rows, actual_rows = [], [], [], []
    max_envelope_excess = 0.0
    max_rate_excess = 0.0
    saturation = 0
    for horizon_index in range(HORIZON):
        base = np.asarray(rows[tick + horizon_index]["action"], dtype=np.float32)
        residual = np.zeros(14, dtype=np.float32)
        if horizon_index == 0 and residual_joint is not None:
            residual[residual_joint] = float(amplitude)
        actual_pre = np.asarray(data.qpos[qpos_addrs], dtype=float)
        final, projection = project_combined_action(
            base_action=base,
            residual_action=residual,
            previous_final_action=previous_final,
            actual_position_rad=actual_pre,
            default_position_rad=home,
            action_scale_rad=action_scale,
            max_action_delta=MAX_ACTION_DELTA,
            actual_centered_guard_rad=0.2,
        )
        rate = np.asarray(projection["rate_bounded_action"], dtype=float)
        guard_low = np.asarray(projection["guard_low_action"], dtype=float)
        guard_high = np.asarray(projection["guard_high_action"], dtype=float)
        max_envelope_excess = max(
            max_envelope_excess,
            float(np.max(np.maximum(np.abs(np.asarray(final, dtype=float) - previous_final) - MAX_ACTION_DELTA, 0.0))),
            float(np.max(np.maximum(guard_low - np.asarray(final, dtype=float), 0.0))),
            float(np.max(np.maximum(np.asarray(final, dtype=float) - guard_high, 0.0))),
        )
        saturation += int(np.any(np.abs(final) >= 1.0 - 1e-7))
        target = home + np.asarray(final, dtype=float) * action_scale
        new_sent = np.clip(target, sent - float(env._config.max_motor_velocity) * float(env.dt), sent + float(env._config.max_motor_velocity) * float(env.dt))
        pitch_delta_rate = np.abs((new_sent - sent)[np.asarray(CORRECTED_JOINT_INDICES)] / float(env.dt))
        measured_rate_excess = float(np.max(np.maximum(pitch_delta_rate - PITCH_LIMITS, 0.0)))
        max_rate_excess = max(
            max_rate_excess,
            0.0 if measured_rate_excess <= 1.0e-5 else measured_rate_excess,
        )
        sent = new_sent
        applied = bridge.step(sent, float(env.dt))
        data.ctrl[:] = applied
        for _ in range(int(env.n_substeps)):
            mujoco.mj_step(model, data)
        quat = np.asarray(data.qpos[3:7], dtype=float)
        actual = np.asarray(data.qpos[qpos_addrs], dtype=float)
        contacts = np.asarray(rows[tick + horizon_index]["oracle_state"]["contacts"], dtype=bool)
        feet = np.asarray(data.site_xpos[env._feet_site_id], dtype=float)
        support = np.mean(feet[contacts] if np.any(contacts) else feet, axis=0)
        com = np.asarray(data.subtree_com[0], dtype=float)
        pitch.append(quat_wxyz_to_pitch(quat))
        roll.append(quat_wxyz_to_roll(quat))
        height.append(float(data.qpos[2]))
        com_distance.append(float(np.linalg.norm((com - support)[:2])))
        tracking.append(np.abs(applied - actual))
        actions.append(final.copy())
        sent_rows.append(sent.copy())
        applied_rows.append(applied.copy())
        actual_rows.append(actual.copy())
        previous_final = final.copy()
    tracking_array = np.asarray(tracking)
    pitch_tracking = tracking_array[:, np.asarray(CORRECTED_JOINT_INDICES)]
    safe = bool(
        np.all(np.isfinite(height))
        and min(height) >= 0.12
        and float(np.percentile(pitch_tracking, 95)) <= 0.2
        and max_rate_excess == 0.0
        and max_envelope_excess <= 1e-7
        and saturation == 0
    )
    return {
        "residual_joint_index": residual_joint,
        "residual_amplitude": amplitude,
        "survives_horizon": bool(np.all(np.isfinite(height)) and min(height) >= 0.12),
        "no_hard_violation": safe,
        "min_base_height_m": min(height),
        "max_abs_pitch_rad": max(abs(value) for value in pitch),
        "max_abs_roll_rad": max(abs(value) for value in roll),
        "terminal_com_support_distance_m": com_distance[-1],
        "residual_l2": abs(amplitude),
        "realized_pitch_change_rad": pitch[-1] - pitch[0],
        "realized_roll_change_rad": roll[-1] - roll[0],
        "tracking_p95_rad": float(np.percentile(pitch_tracking, 95)),
        "saturation_ticks": saturation,
        "max_rate_excess_rad_s": max_rate_excess,
        "max_envelope_excess_normalized": max_envelope_excess,
        "pitch_rad": pitch,
        "roll_rad": roll,
        "base_height_m": height,
        "com_support_distance_m": com_distance,
        "bounded_final_action": np.asarray(actions).tolist(),
        "sent_target_rad": np.asarray(sent_rows).tolist(),
        "applied_target_rad": np.asarray(applied_rows).tolist(),
        "actual_position_rad": np.asarray(actual_rows).tolist(),
    }


def rank_key(row: dict[str, Any], branch_order: int) -> tuple[Any, ...]:
    return (
        int(row["survives_horizon"]),
        int(row["no_hard_violation"]),
        row["min_base_height_m"],
        -row["max_abs_pitch_rad"],
        -row["max_abs_roll_rad"],
        -row["terminal_com_support_distance_m"],
        -row["residual_l2"],
        -branch_order,
    )


def main() -> int:
    TRACE_ROOT.mkdir(parents=True, exist_ok=True)
    fit = json.loads(FIT.read_text())
    design_cells = []
    for policy in POLICIES:
        for condition, offset in ENDPOINTS:
            trace = TRACE_ROOT / f"{condition}_{policy.stem}_p30_x0.077.jsonl"
            result = run_closed_loop_sim(
                ClosedLoopConfig(
                    policy_path=policy, fit=fit, playground_root=PLAYGROUND,
                    command_x=0.077, duration_s=12.0, bridge_mode="fitted",
                    expected_observation_dim=115, expected_action_dim=14,
                    task="flat_terrain_backlash", seed=167931544,
                    eval_role="candidate", reset_mode="home-support",
                    reference_feature_table_path=REFERENCE, reference_start_phase=0,
                    policy_state_input_names=("previous_action",),
                    policy_state_output_names=("previous_action_out",),
                    policy_applied_target_observation=True,
                    eval_dynamics_override={"torso_com_offset_m": [offset, 0.0, 0.0]},
                    trace_jsonl=trace, trace_full_obs=True, trace_oracle_state=True,
                )
            )
            if not trace.exists():
                raise RuntimeError(f"design trace missing: {result}")
            rows = [json.loads(line) for line in trace.read_text().splitlines()]
            readback = ((result.get("insertion_point") or {}).get("dynamics_override") or {})
            design_cells.append({
                "policy": policy.stem, "condition": condition, "offset_m": offset,
                "trace": str(trace), "trace_sha256": sha256(trace), "ticks": len(rows),
                "status": result.get("status"), "readback": readback,
            })
            print(f"design {policy.stem} {condition}: {len(rows)} ticks", flush=True)

    mujoco, env = initialize_native()
    models = {condition: endpoint_model(mujoco, env.mj_model, offset) for condition, offset in ENDPOINTS}
    screen_states = []
    for cell in design_cells:
        rows = [json.loads(line) for line in Path(cell["trace"]).read_text().splitlines()]
        for tick in TICKS:
            if tick + HORIZON > len(rows):
                continue
            bridge, previous_sent, bridge_error = reconstruct_bridge(rows, fit, np.asarray(env._default_actuator, dtype=float), tick)
            if bridge_error > 1e-6:
                raise ValueError(f"bridge reconstruction error {bridge_error}")
            candidates = [(None, 0.0)] + [
                (joint, amplitude)
                for joint in CORRECTED_JOINT_INDICES
                for amplitude in AMPLITUDES
            ]
            branches = []
            for order, (joint, amplitude) in enumerate(candidates):
                row = simulate_branch(
                    mujoco=mujoco, model=models[cell["condition"]], env=env,
                    rows=rows, tick=tick, residual_joint=joint, amplitude=amplitude,
                    bridge=clone_bridge(bridge), previous_sent=previous_sent.copy(),
                )
                row["branch_order"] = order
                branches.append(row)
            baseline = branches[0]
            best = max(branches, key=lambda row: rank_key(row, row["branch_order"]))
            improves = best["branch_order"] != 0 and rank_key(best, best["branch_order"]) > rank_key(baseline, 0)
            predictions = {}
            for joint in CORRECTED_JOINT_INDICES:
                minus = next(row for row in branches if row["residual_joint_index"] == joint and row["residual_amplitude"] == -0.04)
                plus = next(row for row in branches if row["residual_joint_index"] == joint and row["residual_amplitude"] == 0.04)
                predictions[str(joint)] = {
                    "pitch_change_per_normalized_action": (plus["realized_pitch_change_rad"] - minus["realized_pitch_change_rad"]) / 0.08,
                    "roll_change_per_normalized_action": (plus["realized_roll_change_rad"] - minus["realized_roll_change_rad"]) / 0.08,
                }
            state = rows[tick]["oracle_state"]
            screen_states.append({
                "policy": cell["policy"], "condition": cell["condition"],
                "offset_m": cell["offset_m"], "tick": tick,
                "phase_index": state["phase_index"], "phase_fraction": state["phase_fraction"],
                "contacts": state["contacts"], "contact_mode": state["contact_mode"],
                "oracle_features": state["features"],
                "support_relative_com_m": state["support_relative_com_m"],
                "whole_body_com_velocity_m_s": state["whole_body_com_velocity_m_s"],
                "improves": improves, "selected_branch_order": best["branch_order"],
                "selected_residual_action": [best["residual_amplitude"] if index == best["residual_joint_index"] else 0.0 for index in range(14)],
                "baseline": baseline, "selected": best,
                "finite_difference_prediction": predictions,
                "branches": branches,
            })
            print(f"screen {cell['policy']} {cell['condition']} tick={tick} mode={state['contact_mode']} improves={improves}", flush=True)

    groups = []
    authority_pass = True
    for policy in (path.stem for path in POLICIES):
        for condition, _offset in ENDPOINTS:
            subset = [row for row in screen_states if row["policy"] == policy and row["condition"] == condition]
            observed_modes = sorted({row["contact_mode"] for row in subset})
            modes_with_improvement = sorted({row["contact_mode"] for row in subset if row["improves"]})
            improved = sum(row["improves"] for row in subset)
            passed = bool(subset) and improved * 2 >= len(subset) and observed_modes == modes_with_improvement
            authority_pass &= passed
            groups.append({
                "policy": policy, "condition": condition, "states": len(subset),
                "improved_states": improved, "observed_contact_modes": observed_modes,
                "contact_modes_with_improvement": modes_with_improvement, "pass": passed,
            })
    readback_exact = all(
        cell["readback"].get("key") == "torso_com_offset_m"
        and cell["readback"].get("readback", {}).get("body_id") == 2
        and cell["readback"].get("readback", {}).get("body_name") == "trunk_assembly"
        and cell["readback"].get("readback", {}).get("changed_indices") == [[2, 0], [2, 1], [2, 2]]
        and np.count_nonzero(np.asarray(cell["readback"]["value"], dtype=float)) == 1
        for cell in design_cells
    )
    checks = {
        "cpu_only": os.environ.get("CUDA_VISIBLE_DEVICES") == "" and os.environ.get("JAX_PLATFORMS") == "cpu",
        "four_design_cells": len(design_cells) == 4,
        "per_run_body2_x_readback_exact": readback_exact,
        "all_screen_branches_present": all(len(row["branches"]) == 25 for row in screen_states),
        "authority_rule_passed": authority_pass,
    }
    failed = sorted(key for key, value in checks.items() if not value)
    status = "PASS_ORACLE_PHASE_COM_CORRECTIVE_AUTHORITY" if authority_pass and readback_exact else "HOLD_NO_CORRECTIVE_AUTHORITY"
    payload = {
        "schema_version": "oracle_phase_com_corrective_authority.v1",
        "status": status, "decision": status,
        "checks": checks, "failed_checks": failed,
        "design_cells": design_cells, "groups": groups, "screen_states": screen_states,
        "source_hashes": {
            "plan": sha256(ROOT / "outputs/analysis/ORACLE_PHASE_COM_COMPENSATION_PLAN.md"),
            "contract": sha256(ROOT / "outputs/analysis/oracle_phase_com_compensation_contract.json"),
            "default_off": sha256(ROOT / "outputs/analysis/oracle_phase_com_default_off_contract.json"),
            "tool": sha256(Path(__file__)),
            "evaluator": sha256(ROOT / "tools/closed_loop_sim_eval.py"),
        },
        "execution": {"cpu_only": True, "training": False, "robot_or_rdk": False, "formal_matrix_cells": 0},
    }
    output = ROOT / "outputs/analysis/oracle_phase_com_corrective_authority.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    markdown = ROOT / "outputs/analysis/ORACLE_PHASE_COM_CORRECTIVE_AUTHORITY.md"
    lines = [
        "# Oracle Phase-COM Corrective Authority", "",
        f"status: `{status}`", "",
        "| checkpoint | endpoint | improving states | screened | contact-mode coverage | pass |",
        "|---|---|---:|---:|---|---|",
    ]
    for row in groups:
        lines.append(f"| {row['policy']} | {row['condition']} | {row['improved_states']} | {row['states']} | {', '.join(row['contact_modes_with_improvement'])} / {', '.join(row['observed_contact_modes'])} | {row['pass']} |")
    lines.extend(["", "The screen used only CPU simulation, the frozen 25-branch pulse bank and the preregistered eight-tick ranking. No formal 48-cell outcome was read.", ""])
    markdown.write_text("\n".join(lines))
    print(json.dumps({"status": status, "groups": groups}, sort_keys=True))
    return 0 if status == "PASS_ORACLE_PHASE_COM_CORRECTIVE_AUTHORITY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
