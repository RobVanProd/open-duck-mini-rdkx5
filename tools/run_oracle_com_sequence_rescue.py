#!/usr/bin/env python3
"""Deterministic bounded beam screen for oracle COM sequence rescue."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["JAX_PLATFORMS"] = "cpu"

import numpy as np

from actuator_bridge_model import ActuatorBridgeModel, params_from_fit
from closed_loop_sim_eval import quat_wxyz_to_pitch, quat_wxyz_to_roll
from oracle_phase_com_controller import CORRECTED_JOINT_INDICES, project_combined_action
from run_oracle_phase_com_authority import initialize_native, endpoint_model


ROOT = Path(__file__).resolve().parents[1]
STATE_ROOT = ROOT / "outputs/analysis/oracle_com_viability_funnel_states"
TRACE_ROOT = ROOT / "outputs/analysis/oracle_phase_com_compensation_traces/formal"
RECORD_ROOT = ROOT / "outputs/analysis/oracle_com_sequence_rescue_states"
OUTPUT_JSON = ROOT / "outputs/analysis/oracle_com_sequence_rescue_result.json"
OUTPUT_MD = ROOT / "outputs/analysis/ORACLE_COM_SEQUENCE_RESCUE_RESULT.md"
FIT_PATH = ROOT / "outputs/analysis/fixed_target_p30_actuator_fit_20260712.json"
SEED = 167931544
HORIZONS = (8, 16, 32)
BLOCK_TICKS = 4
BEAM_WIDTH = 16
AMPLITUDES = (-0.08, -0.04, 0.04, 0.08)
RESIDUAL_ACTIONS = ((None, 0.0),) + tuple((joint, amp) for joint in CORRECTED_JOINT_INDICES for amp in AMPLITUDES)
MAX_ACTION_DELTA = np.asarray([.41919997, .41919997, .12, .12, .12, .41919997, .41919997, .41919997, .41919997, .41919997, .41919997, .10, .08, .10], dtype=np.float64)
PITCH_LIMITS = np.asarray([1.5, 1.5, 1.5, 1.25, 1.0, 1.25], dtype=np.float64)
TRACKING_LIMIT = 0.20
VELOCITY_MARGIN = 0.03
ATTITUDE_MARGIN = 0.05
MIN_BASE_HEIGHT = 0.12
MAX_NO_SUPPORT_RUN = 1


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def nominal_traces() -> list[tuple[Path, list[dict[str, Any]]]]:
    paths = sorted(TRACE_ROOT.glob(f"NOMINAL_T2_EQUAL_*_p*_x0.077_seed{SEED}.jsonl"))
    if len(paths) != 4:
        raise RuntimeError(f"expected four nominal x=.077 traces, found {len(paths)}")
    return [(p, load_rows(p)) for p in paths]


def nominal_envelope(rows_by: list[list[dict[str, Any]]], tick: int, horizon: int) -> dict[str, float]:
    means = [float(np.mean([row["local_linvel_m_s"][0] for row in rows[tick : tick + horizon]])) for rows in rows_by]
    pitch = max(abs(float(rows[min(tick + horizon - 1, len(rows) - 1)]["oracle_state"]["pitch_rad"])) for rows in rows_by)
    roll = max(abs(float(rows[min(tick + horizon - 1, len(rows) - 1)]["oracle_state"]["roll_rad"])) for rows in rows_by)
    return {"vx_mean_min": min(means) - VELOCITY_MARGIN, "vx_mean_max": max(means) + VELOCITY_MARGIN, "pitch_abs_max": pitch + ATTITUDE_MARGIN, "roll_abs_max": roll + ATTITUDE_MARGIN}


def clone_bridge(source: ActuatorBridgeModel) -> ActuatorBridgeModel:
    out = ActuatorBridgeModel(source.params, initial_target=source.value)
    out._queues = [queue.copy() for queue in source._queues]
    return out


def restore_bridge(payload: dict[str, Any], fit: dict[str, Any]) -> ActuatorBridgeModel:
    out = ActuatorBridgeModel(params_from_fit(fit), initial_target=np.asarray(payload["bridge_value_rad"], dtype=float))
    out._queues = [np.asarray(queue, dtype=float).tolist() for queue in payload["bridge_queues_rad"]]
    return out


def clone_data(mujoco: Any, model: Any, source: Any) -> Any:
    out = mujoco.MjData(model)
    out.qpos[:] = source.qpos
    out.qvel[:] = source.qvel
    out.ctrl[:] = source.ctrl
    if out.act.size:
        out.act[:] = source.act
    out.time = source.time
    out.qacc_warmstart[:] = source.qacc_warmstart
    mujoco.mj_forward(model, out)
    return out


def local_velocity(data: Any) -> np.ndarray:
    w, x, y, z = np.asarray(data.qpos[3:7], dtype=float)
    rot = np.asarray([[1 - 2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
    return rot.T @ np.asarray(data.qvel[:3], dtype=float)


def contacts_for(data: Any, env: Any) -> np.ndarray:
    contacts = np.zeros(2, dtype=bool)
    floor = int(env._floor_geom_id)
    feet = np.asarray(env._feet_geom_id, dtype=int)
    for i in range(int(data.ncon)):
        pair = {int(data.contact[i].geom1), int(data.contact[i].geom2)}
        for side, foot in enumerate(feet):
            contacts[side] |= floor in pair and int(foot) in pair
    return contacts


def base_action(rows: list[dict[str, Any]], nominal: list[dict[str, Any]], tick: int) -> np.ndarray:
    source = rows if tick < len(rows) else nominal
    return np.asarray(source[min(tick, len(source)-1)]["policy_base_action"], dtype=np.float32)


def new_node(data: Any, bridge: ActuatorBridgeModel, payload: dict[str, Any]) -> dict[str, Any]:
    return {"data": data, "bridge": bridge, "previous_final": np.asarray(payload["previous_final_action"], dtype=np.float32), "previous_sent": np.asarray(payload["previous_sent_target_rad"], dtype=float), "sequence": [], "vx": [], "pitch": [], "roll": [], "com_margin": [], "contacts": [], "tracking": [], "residual_l1": 0.0, "saturation": 0, "max_rate_excess": 0.0, "max_envelope_excess": 0.0, "no_support_run": 0, "max_no_support_run": 0, "survives": True}


def expand(*, mujoco: Any, model: Any, env: Any, node: dict[str, Any], rows: list[dict[str, Any]], nominal: list[dict[str, Any]], start_tick: int, depth: int, action_order: int, joint: int | None, amplitude: float) -> dict[str, Any]:
    out = {key: (value.copy() if isinstance(value, list) else value) for key, value in node.items() if key not in {"data", "bridge"}}
    out["data"] = clone_data(mujoco, model, node["data"])
    out["bridge"] = clone_bridge(node["bridge"])
    out["previous_final"] = node["previous_final"].copy()
    out["previous_sent"] = node["previous_sent"].copy()
    out["sequence"] = node["sequence"] + [{"block": depth, "joint_index": joint, "amplitude": amplitude, "action_order": action_order}]
    home = np.asarray(env._default_actuator, dtype=float)
    action_scale = float(env._config.action_scale)
    joint_ids = np.asarray(model.actuator_trnid[:, 0], dtype=int)
    qpos_addrs = np.asarray(model.jnt_qposadr[joint_ids], dtype=int)
    for within in range(BLOCK_TICKS):
        tick = start_tick + depth * BLOCK_TICKS + within
        base = base_action(rows, nominal, tick)
        residual = np.zeros(14, dtype=np.float32)
        if joint is not None:
            residual[joint] = amplitude
        actual_pre = np.asarray(out["data"].qpos[qpos_addrs], dtype=float)
        final, projection = project_combined_action(base_action=base, residual_action=residual, previous_final_action=out["previous_final"], actual_position_rad=actual_pre, default_position_rad=home, action_scale_rad=action_scale, max_action_delta=MAX_ACTION_DELTA, actual_centered_guard_rad=.2)
        low, high = np.asarray(projection["guard_low_action"], dtype=float), np.asarray(projection["guard_high_action"], dtype=float)
        envelope = max(float(np.max(np.maximum(np.abs(np.asarray(final)-out["previous_final"])-MAX_ACTION_DELTA, 0))), float(np.max(np.maximum(low-final, 0))), float(np.max(np.maximum(final-high, 0))))
        out["max_envelope_excess"] = max(out["max_envelope_excess"], 0.0 if envelope <= 1e-7 else envelope)
        out["saturation"] += int(np.any(np.abs(final) >= 1.0 - 1e-7))
        target = home + np.asarray(final, dtype=float) * action_scale
        sent = np.clip(target, out["previous_sent"] - float(env._config.max_motor_velocity)*float(env.dt), out["previous_sent"] + float(env._config.max_motor_velocity)*float(env.dt))
        rates = np.abs((sent-out["previous_sent"])[np.asarray(CORRECTED_JOINT_INDICES)] / float(env.dt))
        excess = float(np.max(np.maximum(rates-PITCH_LIMITS, 0)))
        out["max_rate_excess"] = max(out["max_rate_excess"], 0.0 if excess <= 1e-5 else excess)
        applied = out["bridge"].step(sent, float(env.dt))
        out["data"].ctrl[:] = applied
        for _ in range(int(env.n_substeps)):
            mujoco.mj_step(model, out["data"])
        actual = np.asarray(out["data"].qpos[qpos_addrs], dtype=float)
        track = np.abs(applied-actual)[np.asarray(CORRECTED_JOINT_INDICES)]
        quat = np.asarray(out["data"].qpos[3:7], dtype=float)
        pitch, roll = quat_wxyz_to_pitch(quat), quat_wxyz_to_roll(quat)
        contacts = contacts_for(out["data"], env)
        out["no_support_run"] = out["no_support_run"] + 1 if not np.any(contacts) else 0
        out["max_no_support_run"] = max(out["max_no_support_run"], out["no_support_run"])
        feet = np.asarray(out["data"].site_xpos[env._feet_site_id], dtype=float)
        support = np.mean(feet[contacts] if np.any(contacts) else feet, axis=0)
        com = np.asarray(out["data"].subtree_com[0], dtype=float)
        out["vx"].append(float(local_velocity(out["data"])[0])); out["pitch"].append(pitch); out["roll"].append(roll)
        out["com_margin"].append(float(np.linalg.norm((com-support)[:2]))); out["contacts"].append(contacts.astype(int).tolist()); out["tracking"].extend(track.tolist())
        out["residual_l1"] += float(np.sum(np.abs(residual)))
        finite = np.all(np.isfinite(out["data"].qpos)) and np.all(np.isfinite(out["data"].qvel))
        out["survives"] &= bool(finite and float(out["data"].qpos[2]) >= MIN_BASE_HEIGHT)
        out["previous_final"], out["previous_sent"] = final.copy(), sent.copy()
    return out


def summarize(node: dict[str, Any], envelope: dict[str, float], tick: int) -> dict[str, Any]:
    mean_vx = float(np.mean(node["vx"]))
    tracking = float(np.percentile(node["tracking"], 95)) if node["tracking"] else math.inf
    hard = bool(node["survives"] and node["max_no_support_run"] <= MAX_NO_SUPPORT_RUN and tracking <= TRACKING_LIMIT and node["saturation"] == 0 and node["max_rate_excess"] == 0 and node["max_envelope_excess"] == 0 and max(map(abs,node["pitch"])) <= envelope["pitch_abs_max"] and max(map(abs,node["roll"])) <= envelope["roll_abs_max"])
    direction = mean_vx > 0.0 if tick >= 4 else mean_vx >= envelope["vx_mean_min"]
    valid = hard and direction and envelope["vx_mean_min"] <= mean_vx <= envelope["vx_mean_max"]
    return {"valid": valid, "hard_valid": hard, "velocity_direction_valid": direction, "velocity_envelope_valid": envelope["vx_mean_min"] <= mean_vx <= envelope["vx_mean_max"], "mean_body_vx_m_s": mean_vx, "tracking_p95_rad": tracking, "max_abs_pitch_rad": max(map(abs,node["pitch"])), "max_abs_roll_rad": max(map(abs,node["roll"])), "terminal_com_support_distance_m": node["com_margin"][-1], "contacts": node["contacts"], "saturation_ticks": node["saturation"], "max_rate_excess_rad_s": node["max_rate_excess"], "max_envelope_excess_normalized": node["max_envelope_excess"], "residual_l1": node["residual_l1"], "sequence": node["sequence"], "nominal_envelope": envelope}


def rank(node: dict[str, Any], envelope: dict[str, float], tick: int) -> tuple[Any, ...]:
    s = summarize(node, envelope, tick)
    return (int(s["hard_valid"]), int(s["velocity_direction_valid"]), int(s["velocity_envelope_valid"]), -abs(s["mean_body_vx_m_s"]-.077), -s["max_abs_pitch_rad"], -s["max_abs_roll_rad"], -s["terminal_com_support_distance_m"], -s["residual_l1"], tuple(-item["action_order"] for item in s["sequence"]))


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--contract-only", action="store_true"); args = parser.parse_args()
    nominal = nominal_traces(); nominal_rows = [rows for _, rows in nominal]
    checks = {"cpu_environment": os.environ.get("CUDA_VISIBLE_DEVICES") == "" and os.environ.get("JAX_PLATFORMS") == "cpu", "horizons_exact": HORIZONS == (8,16,32), "basis_exact": len(RESIDUAL_ACTIONS) == 25 and {j for j,a in RESIDUAL_ACTIONS if j is not None} == set(CORRECTED_JOINT_INDICES), "fixed_beam": BEAM_WIDTH == 16 and BLOCK_TICKS == 4, "four_nominal_envelope_traces": len(nominal) == 4}
    if args.contract_only:
        print(json.dumps({"status":"PASS_SEQUENCE_RESCUE_INPUT_CONTRACT","checks":checks,"nominal_trace_hashes":{str(p):sha256(p) for p,_ in nominal}},indent=2,sort_keys=True)); return 0 if all(checks.values()) else 1
    localization = json.loads((ROOT/"outputs/analysis/oracle_com_failure_localization.json").read_text())
    states = [row for row in localization["state_index"] if row["design_subset"]]
    fit = json.loads(FIT_PATH.read_text()); mujoco, env = initialize_native(); models = {"X_NEG":endpoint_model(mujoco,env.mj_model,-.05),"X_POS":endpoint_model(mujoco,env.mj_model,.05)}
    RECORD_ROOT.mkdir(parents=True,exist_ok=True); outcomes=[]
    for index,state_ref in enumerate(states):
        payload=json.loads(Path(state_ref["path"]).read_text()); rows=load_rows(Path(payload["source_trace"])); matched=load_rows(Path(payload["matched_nominal_trace"])); model=models[payload["condition"]]
        data=mujoco.MjData(model); data.qpos[:]=payload["qpos"]; data.qvel[:]=payload["qvel"]; data.ctrl[:]=payload["ctrl"]; mujoco.mj_forward(model,data)
        beam=[new_node(data,restore_bridge(payload,fit),payload)]; by_horizon={}
        for depth in range(max(HORIZONS)//BLOCK_TICKS):
            expanded=[]
            for node in beam:
                for order,(joint,amp) in enumerate(RESIDUAL_ACTIONS):
                    expanded.append(expand(mujoco=mujoco,model=model,env=env,node=node,rows=rows,nominal=matched,start_tick=int(payload["tick"]),depth=depth,action_order=order,joint=joint,amplitude=amp))
            partial_h=(depth+1)*BLOCK_TICKS; env_now=nominal_envelope(nominal_rows,int(payload["tick"]),partial_h)
            expanded.sort(key=lambda n:rank(n,env_now,int(payload["tick"])),reverse=True); beam=expanded[:BEAM_WIDTH]
            if partial_h in HORIZONS:
                summaries=[summarize(n,env_now,int(payload["tick"])) for n in beam]; valid=[s for s in summaries if s["valid"]]
                by_horizon[str(partial_h)]={"valid_sequence_exists":bool(valid),"best":(valid[0] if valid else summaries[0]),"beam_candidates_retained":len(beam)}
        successful=[h for h in HORIZONS if by_horizon[str(h)]["valid_sequence_exists"]]
        record={"schema_version":"oracle_com_sequence_rescue_state.v1","state_path":state_ref["path"],"state_sha256":state_ref["sha256"],"condition":payload["condition"],"policy":payload["policy"],"tick":payload["tick"],"ticks_to_recorded_termination":payload["ticks_to_recorded_termination"],"horizons":by_horizon,"minimum_successful_horizon":min(successful) if successful else None}
        out=RECORD_ROOT/f"{payload['condition']}_{payload['policy']}_tick{int(payload['tick']):03d}.json"; out.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n"); outcomes.append(record|{"record_path":str(out),"record_sha256":sha256(out)})
        print(f"sequence {index+1}/{len(states)} {payload['condition']} {payload['policy']} tick={payload['tick']} min_h={record['minimum_successful_horizon']}",flush=True)
    horizon_pass={str(h):all(row["horizons"][str(h)]["valid_sequence_exists"] for row in outcomes) for h in HORIZONS}
    advance=any(horizon_pass.values()); decision="PASS_SEQUENCE_RESCUE_ADVANCE_TO_ONLINE" if advance else "HOLD_LOCAL_AUTHORITY_NOT_COMPOSABLE"
    earliest={}
    for condition in ("X_NEG","X_POS"):
        subset=[r for r in outcomes if r["condition"]==condition and r["minimum_successful_horizon"] is None]
        earliest[condition]=None if not subset else min(subset,key=lambda r:r["tick"])["tick"]
    result={"schema_version":"oracle_com_sequence_rescue_result.v1","status":"PASS_SEQUENCE_SCREEN_COMPLETE","decision":decision,"advance_to_stage_c":advance,"checks":checks,"search":{"horizons":list(HORIZONS),"block_ticks":BLOCK_TICKS,"beam_width":BEAM_WIDTH,"actions_per_expansion":len(RESIDUAL_ACTIONS),"corrected_joint_indices":list(CORRECTED_JOINT_INDICES),"amplitudes":list(AMPLITUDES),"velocity_margin_m_s":VELOCITY_MARGIN,"attitude_margin_rad":ATTITUDE_MARGIN,"tracking_limit_rad":TRACKING_LIMIT},"states_total":len(outcomes),"horizon_pass_all_states":horizon_pass,"earliest_no_valid_state_tick":earliest,"states":outcomes,"execution":{"cpu_only":True,"training":False,"gpu_or_igpu":False,"hosted":False,"robot_or_rdk":False}}
    OUTPUT_JSON.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    lines=["# Oracle COM Sequence Rescue Result","",f"status: `PASS_SEQUENCE_SCREEN_COMPLETE`",f"decision: `{decision}`","","| horizon | valid states | total | advances |","|---:|---:|---:|---|"]
    for h in HORIZONS:
        count=sum(r["horizons"][str(h)]["valid_sequence_exists"] for r in outcomes); lines.append(f"| {h} | {count} | {len(outcomes)} | {horizon_pass[str(h)]} |")
    lines += ["",f"Earliest no-valid state: X_NEG tick {earliest['X_NEG']}; X_POS tick {earliest['X_POS']}.","",f"Final Stage-B token: `{decision}`","","No closest sequence is promoted. Stage C is authorized only when one frozen horizon passes every design state.",""]
    OUTPUT_MD.write_text("\n".join(lines)); print(json.dumps({"decision":decision,"states":len(outcomes),"horizon_pass":horizon_pass},sort_keys=True)); return 0


if __name__=="__main__": raise SystemExit(main())
