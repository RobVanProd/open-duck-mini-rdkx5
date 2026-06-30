#!/usr/bin/env python3
"""Diagnose phase-swing foot clearance against corrected actuator limits.

This tool is offline-only.  It does not train, SSH, deploy, or touch the robot.
It reuses the existing closed-loop candidate evaluator to collect full-state
traces when needed, then computes MuJoCo foot Jacobians from recorded qpos.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
JOINT_NAMES = [
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
]
SIDE_JOINTS = {
    "left": ["left_hip_pitch", "left_knee", "left_ankle"],
    "right": ["right_hip_pitch", "right_knee", "right_ankle"],
}
FOOT_SITE = {"left": "left_foot", "right": "right_foot"}


def finite(value: Any) -> bool:
    return isinstance(value, int | float) and not (
        math.isnan(float(value)) or math.isinf(float(value))
    )


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, int | float):
        return f"{float(value):.{digits}f}"
    return str(value)


def percentile(values: Sequence[float], pct: float) -> float | None:
    data = sorted(float(value) for value in values if finite(value))
    if not data:
        return None
    if len(data) == 1:
        return data[0]
    k = (len(data) - 1) * pct / 100.0
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return data[lo]
    return data[lo] * (hi - k) + data[hi] * (k - lo)


def stats(values: Iterable[float]) -> dict[str, float] | None:
    data = [float(value) for value in values if finite(value)]
    if not data:
        return None
    return {
        "min": min(data),
        "mean": sum(data) / len(data),
        "p50": percentile(data, 50),
        "p95": percentile(data, 95),
        "max": max(data),
    }


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def shell_join(command: Sequence[str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in command)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_trace(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open() as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def corrected_pitch_limits(fit: Mapping[str, Any]) -> dict[str, float]:
    root = fit.get("primary", fit)
    joints = root.get("joints", {}) if isinstance(root, Mapping) else {}
    limits: dict[str, float] = {}
    for names in SIDE_JOINTS.values():
        for joint in names:
            combined = (joints.get(joint) or {}).get("combined") or {}
            value = combined.get("velocity_limit_rad_s")
            if finite(value):
                limits[joint] = float(value)
    return limits


def phase01_from_obs(record: Mapping[str, Any]) -> float | None:
    obs = record.get("obs_state")
    if not isinstance(obs, list) or len(obs) < 101:
        return None
    cos_v = obs[99]
    sin_v = obs[100]
    if not (finite(cos_v) and finite(sin_v)):
        return None
    return float((math.atan2(float(sin_v), float(cos_v)) / (2.0 * math.pi)) % 1.0)


def phase_swing_side(phase01: float, invert: bool = False) -> str:
    # Playground convention used by probe_closed_loop_weight_transfer_teacher.py:
    # phase < 0.5 means left stance / right swing.
    right_swing = phase01 < 0.5
    if invert:
        right_swing = not right_swing
    return "right" if right_swing else "left"


def contiguous_segments(mask: Sequence[bool], min_len: int = 2) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    start = None
    for index, value in enumerate(mask):
        if value and start is None:
            start = index
        is_last = index == len(mask) - 1
        if start is not None and ((not value) or is_last):
            end = index if not value else index + 1
            if end - start >= min_len:
                out.append((start, end))
            start = None
    return out


def best_lag_ticks(commanded: Sequence[float], achieved: Sequence[float], max_lag: int) -> dict[str, Any]:
    cmd = np.asarray([float(v) for v in commanded], dtype=float)
    ach = np.asarray([float(v) for v in achieved], dtype=float)
    if cmd.size < 4 or ach.size != cmd.size:
        return {"ticks": None, "rmse": None, "samples": 0}
    best = None
    # Positive lag means achieved is delayed relative to commanded.
    for lag in range(0, max_lag + 1):
        if lag == 0:
            left, right = cmd, ach
        else:
            left, right = cmd[:-lag], ach[lag:]
        if left.size < 4:
            continue
        rmse = float(np.sqrt(np.mean(np.square(left - right))))
        if best is None or rmse < best["rmse"]:
            best = {"ticks": int(lag), "rmse": rmse, "samples": int(left.size)}
    return best or {"ticks": None, "rmse": None, "samples": 0}


def velocity(arr: np.ndarray, dt_s: float) -> np.ndarray:
    if arr.shape[0] < 2:
        return np.zeros_like(arr)
    diff = np.diff(arr, axis=0) / max(float(dt_s), 1e-9)
    return np.vstack([np.zeros((1,) + diff.shape[1:]), diff])


def run_trace_sweep(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = Path(args.trace_dir)
    trace_seed_list = ",".join(str(seed) for seed in args.seeds)
    command = [
        sys.executable,
        str(ROOT / "tools" / "run_candidate_seed_sweep.py"),
        "--policies",
        str(Path(args.candidate)),
        "--fit-json",
        str(Path(args.fit_json)),
        "--playground-path",
        str(Path(args.playground_path)),
        "--env-python",
        str(Path(args.env_python)),
        "--command-x",
        str(args.command_x),
        "--task",
        str(args.task),
        "--duration",
        str(args.duration),
        "--seeds",
        ",".join(str(seed) for seed in args.seeds),
        "--bridge-mode",
        "fitted",
        "--jax-platform",
        str(args.jax_platform),
        "--closed-loop-timeout-s",
        str(int(args.closed_loop_timeout_s)),
        "--sim-preflight-timeout-s",
        str(int(args.sim_preflight_timeout_s)),
        "--output-dir",
        str(output_dir),
        "--trace-seeds",
        trace_seed_list,
        "--trace-full-obs",
        "--run",
    ]
    if args.terrain_hfield_z_scale is not None:
        command.extend(["--terrain-hfield-z-scale", str(args.terrain_hfield_z_scale)])
    if args.eval_push_enable:
        command.append("--eval-push-enable")
        if args.eval_push_interval_min_s is not None:
            command.extend(["--eval-push-interval-min-s", str(args.eval_push_interval_min_s)])
        if args.eval_push_interval_max_s is not None:
            command.extend(["--eval-push-interval-max-s", str(args.eval_push_interval_max_s)])
        if args.eval_push_magnitude_min is not None:
            command.extend(["--eval-push-magnitude-min", str(args.eval_push_magnitude_min)])
        if args.eval_push_magnitude_max is not None:
            command.extend(["--eval-push-magnitude-max", str(args.eval_push_magnitude_max)])

    result = {
        "command": command,
        "command_shell": shell_join(command),
        "output_dir": str(output_dir),
    }
    if args.no_run_traces:
        result["status"] = "PASS_EXISTING_TRACES_USED"
        return result
    env = os.environ.copy()
    if args.jax_platform:
        env["JAX_PLATFORM_NAME"] = str(args.jax_platform)
        env["JAX_PLATFORMS"] = str(args.jax_platform)
    proc = subprocess.run(
        command,
        cwd=str(ROOT),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=args.sweep_timeout_s,
        check=False,
    )
    result.update(
        {
            "status": "PASS_TRACE_SWEEP" if proc.returncode == 0 else "HOLD_TRACE_SWEEP",
            "returncode": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-12000:],
        }
    )
    return result


def trace_paths(trace_dir: Path, candidate: Path, seeds: Sequence[int]) -> dict[int, Path]:
    label = candidate.parent.name if candidate.name == "candidate.onnx" else candidate.stem
    out: dict[int, Path] = {}
    for seed in seeds:
        candidates = [
            trace_dir / label / f"seed_{seed:03d}" / "trace.jsonl",
            trace_dir / f"seed_{seed:03d}" / "trace.jsonl",
        ]
        for path in candidates:
            if path.exists():
                out[int(seed)] = path
                break
    return out


def load_model(playground_path: Path, task: str):
    import mujoco

    sys.path.insert(0, str(playground_path.resolve()))
    from playground.open_duck_mini_v2 import base, constants

    xml_path = Path(constants.task_to_xml(task))
    model = mujoco.MjModel.from_xml_string(xml_path.read_text(), assets=base.get_assets())
    data = mujoco.MjData(model)
    return mujoco, model, data, xml_path


def model_audit(mujoco, model) -> dict[str, Any]:
    actuator_names = [model.actuator(i).name for i in range(model.nu)]
    joint_names = [model.joint(i).name for i in range(model.njnt)]
    sites = [model.site(i).name for i in range(model.nsite)]
    foot_sites = {
        side: {
            "site_name": name,
            "site_id": int(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, name)),
        }
        for side, name in FOOT_SITE.items()
    }
    for item in foot_sites.values():
        site_id = item["site_id"]
        item["body_id"] = int(model.site_bodyid[site_id])
        item["body_name"] = model.body(item["body_id"]).name
    pitch_dofs = {}
    pitch_qpos = {}
    for joint in [j for names in SIDE_JOINTS.values() for j in names]:
        joint_id = int(mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, joint))
        pitch_dofs[joint] = int(model.jnt_dofadr[joint_id])
        pitch_qpos[joint] = int(model.jnt_qposadr[joint_id])
    return {
        "nq": int(model.nq),
        "nv": int(model.nv),
        "nu": int(model.nu),
        "actuator_names": actuator_names,
        "joint_names": joint_names,
        "sites": sites,
        "foot_sites": foot_sites,
        "pitch_chain_dof_indices": pitch_dofs,
        "pitch_chain_qpos_indices": pitch_qpos,
        "backlash_joint_present": any("backlash" in name for name in joint_names),
    }


def jacobian_vertical_rows(mujoco, model, data, qpos: Sequence[float]) -> dict[str, np.ndarray]:
    qpos_arr = np.asarray(qpos, dtype=float)
    if qpos_arr.shape != (model.nq,):
        raise ValueError(f"qpos shape {qpos_arr.shape} != model.nq {model.nq}")
    data.qpos[:] = qpos_arr
    data.qvel[:] = 0.0
    mujoco.mj_forward(model, data)
    rows = {}
    for side, site_name in FOOT_SITE.items():
        site_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, site_name)
        body_id = int(model.site_bodyid[site_id])
        jacp = np.zeros((3, model.nv), dtype=float)
        jacr = np.zeros((3, model.nv), dtype=float)
        mujoco.mj_jac(model, data, jacp, jacr, data.site_xpos[site_id], body_id)
        rows[side] = jacp[2, :].copy()
    return rows


def classify_seed(
    side_rows: dict[str, dict[str, Any]],
    *,
    high_r: float,
    low_r: float,
    planted_pct_threshold: float,
    latency_ticks_threshold: int,
) -> str:
    classes = [row["classification"] for row in side_rows.values()]
    if any(item == "STRUCTURAL" for item in classes):
        return "STRUCTURAL"
    if any(item == "LATENCY_LIMITED" for item in classes):
        return "LATENCY_LIMITED"
    if any(item == "DISTILLATION" for item in classes):
        return "DISTILLATION"
    if all(item == "FINE_OR_NO_SWING" for item in classes):
        return "FINE_OR_NO_SWING"
    return "MIXED_OR_AMBIGUOUS"


def analyze_seed(
    rows: list[dict[str, Any]],
    *,
    mujoco,
    model,
    data,
    audit: Mapping[str, Any],
    limits: Mapping[str, float],
    dt_s: float,
    invert_phase_map: bool,
    high_r: float,
    low_r: float,
    planted_pct_threshold: float,
    latency_ticks_threshold: int,
    max_lag_ticks: int,
) -> dict[str, Any]:
    if not rows:
        return {"status": "HOLD_EMPTY_TRACE"}
    qpos = np.asarray([row.get("qpos") for row in rows], dtype=float)
    sent = np.asarray([row.get("sent_target_rad") for row in rows], dtype=float)
    actual = np.asarray([row.get("actual_position_rad") for row in rows], dtype=float)
    foot_pos = np.asarray([row.get("foot_site_pos_m") for row in rows], dtype=float)
    contacts = np.asarray([row.get("foot_contacts") for row in rows], dtype=bool)
    phase = [phase01_from_obs(row) for row in rows]
    if qpos.ndim != 2 or qpos.shape[1] != model.nq:
        return {"status": "HOLD_TRACE_MISSING_QPOS", "qpos_shape": list(qpos.shape)}
    if any(value is None for value in phase):
        return {"status": "HOLD_TRACE_MISSING_PHASE"}

    sent_vel = velocity(sent, dt_s)
    actual_vel = velocity(actual, dt_s)
    foot_vel_z = velocity(foot_pos, dt_s)[:, :, 2]
    swing_side = [phase_swing_side(float(p), invert_phase_map) for p in phase]
    seed = rows[0].get("seed")

    side_results: dict[str, Any] = {}
    all_segments: list[dict[str, Any]] = []
    for side in ("left", "right"):
        side_mask = [item == side for item in swing_side]
        segments = contiguous_segments(side_mask, min_len=2)
        joint_names = SIDE_JOINTS[side]
        joint_indices = [JOINT_NAMES.index(name) for name in joint_names]
        dof_indices = [audit["pitch_chain_dof_indices"][name] for name in joint_names]
        side_limits = np.asarray([limits[name] for name in joint_names], dtype=float)
        side_index = 0 if side == "left" else 1
        segment_rows = []
        all_r_values = []
        all_r_by_joint: dict[str, list[float]] = {name: [] for name in joint_names}
        all_ceilings = []
        all_ratios = []
        planted_samples = 0
        swing_samples = 0
        latency_hits = 0
        over_envelope_ratio_hits = 0
        for start, end in segments:
            idx = np.arange(start, end)
            swing_samples += int(idx.size)
            planted = contacts[idx, side_index]
            planted_samples += int(np.sum(planted))
            cmd_rates = sent_vel[idx][:, joint_indices]
            ach_rates = actual_vel[idx][:, joint_indices]
            r_by_sample_joint = np.abs(cmd_rates) / side_limits[None, :]
            r_peak = float(np.max(r_by_sample_joint)) if r_by_sample_joint.size else None
            r_driver_joint = None
            if r_by_sample_joint.size:
                flat_index = int(np.argmax(r_by_sample_joint))
                _, joint_offset = np.unravel_index(flat_index, r_by_sample_joint.shape)
                r_driver_joint = joint_names[joint_offset]
                for joint_offset, joint_name in enumerate(joint_names):
                    all_r_by_joint[joint_name].append(
                        float(np.max(r_by_sample_joint[:, joint_offset]))
                    )
            all_r_values.append(r_peak)

            cmd_vz = []
            ach_vz_jac = []
            ceilings = []
            for sample_index in idx:
                jz = jacobian_vertical_rows(mujoco, model, data, qpos[sample_index])[side]
                jz_side = np.asarray([jz[dof] for dof in dof_indices], dtype=float)
                cmd_vz.append(float(np.dot(jz_side, sent_vel[sample_index, joint_indices])))
                ach_vz_jac.append(float(np.dot(jz_side, actual_vel[sample_index, joint_indices])))
                ceilings.append(float(np.sum(np.abs(jz_side) * side_limits)))
            cmd_vz_arr = np.asarray(cmd_vz, dtype=float)
            ach_vz_arr = np.asarray(ach_vz_jac, dtype=float)
            ceiling_arr = np.asarray(ceilings, dtype=float)
            peak_ceiling = float(np.max(ceiling_arr)) if ceiling_arr.size else None
            peak_achieved = (
                float(np.max(foot_vel_z[idx, side_index])) if idx.size else None
            )
            peak_cmd = float(np.max(cmd_vz_arr)) if cmd_vz_arr.size else None
            achieved_ceiling_ratio = (
                peak_achieved / peak_ceiling
                if finite(peak_achieved) and finite(peak_ceiling) and peak_ceiling > 1e-9
                else None
            )
            if finite(peak_ceiling):
                all_ceilings.append(peak_ceiling)
            if finite(achieved_ceiling_ratio):
                all_ratios.append(achieved_ceiling_ratio)
                if achieved_ceiling_ratio > 1.0:
                    over_envelope_ratio_hits += 1

            cmd_peak_local = int(np.argmax(cmd_vz_arr)) if cmd_vz_arr.size else None
            ach_peak_local = int(np.argmax(ach_vz_arr)) if ach_vz_arr.size else None
            peak_delta_ticks = (
                ach_peak_local - cmd_peak_local
                if cmd_peak_local is not None and ach_peak_local is not None
                else None
            )
            lag = best_lag_ticks(cmd_vz_arr, ach_vz_arr, max_lag_ticks)
            # Keep the lag fit as context, but classify latency only when the
            # achieved vertical-velocity peak occurs after the commanded peak.
            # Short swing windows can make RMSE-based lag fits look delayed even
            # when the achieved peak is earlier; that is not the phase-delay
            # failure this diagnostic is meant to identify.
            latency_limited = bool(
                finite(peak_cmd)
                and peak_cmd > 1.0e-4
                and finite(peak_delta_ticks)
                and peak_delta_ticks >= latency_ticks_threshold
            )
            if latency_limited:
                latency_hits += 1
            contact_broke = bool(np.any(~planted))
            segment_rows.append(
                {
                    "start_tick": int(start),
                    "end_tick": int(end - 1),
                    "samples": int(idx.size),
                    "phase_start": phase[start],
                    "phase_end": phase[end - 1],
                    "contact_broke": contact_broke,
                    "planted_pct": float(np.mean(planted) * 100.0),
                    "rate_utilization_peak": r_peak,
                    "rate_driver_joint": r_driver_joint,
                    "vertical_clearance_ceiling_peak_m_s": peak_ceiling,
                    "achieved_vertical_velocity_peak_m_s": peak_achieved,
                    "commanded_vertical_velocity_peak_m_s": peak_cmd,
                    "achieved_to_ceiling_ratio": achieved_ceiling_ratio,
                    "cmd_to_actual_vz_best_lag": lag,
                    "cmd_peak_to_actual_peak_delta_ticks": peak_delta_ticks,
                    "latency_limited": latency_limited,
                }
            )
        planted_pct = (
            float(planted_samples / swing_samples * 100.0) if swing_samples else None
        )
        r_peak_side = max([v for v in all_r_values if finite(v)], default=None)
        r_by_joint_peak = {
            joint: max([v for v in values if finite(v)], default=None)
            for joint, values in all_r_by_joint.items()
        }
        r_driver_joint_side = None
        finite_joint_peaks = {
            joint: value for joint, value in r_by_joint_peak.items() if finite(value)
        }
        if finite_joint_peaks:
            r_driver_joint_side = max(
                finite_joint_peaks.items(), key=lambda item: item[1]
            )[0]
        ceiling_p50 = percentile(all_ceilings, 50) if all_ceilings else None
        ratio_peak = max([v for v in all_ratios if finite(v)], default=None)
        contact_break_segments = sum(1 for item in segment_rows if item["contact_broke"])
        if not segment_rows:
            classification = "FINE_OR_NO_SWING"
        elif finite(r_peak_side) and r_peak_side > 1.0:
            classification = "STRUCTURAL"
        elif finite(ratio_peak) and ratio_peak > 1.0:
            classification = "STRUCTURAL"
        elif latency_hits and latency_hits >= max(1, math.ceil(len(segment_rows) / 2)):
            classification = "LATENCY_LIMITED"
        elif finite(planted_pct) and planted_pct >= planted_pct_threshold and finite(r_peak_side) and r_peak_side >= high_r:
            classification = "STRUCTURAL"
        elif finite(planted_pct) and planted_pct >= planted_pct_threshold and finite(r_peak_side) and r_peak_side <= low_r:
            classification = "DISTILLATION"
        elif contact_break_segments == len(segment_rows):
            classification = "FINE_OR_NO_SWING"
        else:
            classification = "MIXED_OR_AMBIGUOUS"
        structural_reasons = []
        if finite(r_peak_side) and r_peak_side > 1.0:
            structural_reasons.append("rate_utilization_exceeds_corrected_limit")
        if finite(ratio_peak) and ratio_peak > 1.0:
            structural_reasons.append("achieved_vertical_velocity_exceeds_in_envelope_ceiling")
        if (
            finite(planted_pct)
            and planted_pct >= planted_pct_threshold
            and finite(r_peak_side)
            and r_peak_side >= high_r
        ):
            structural_reasons.append("planted_phase_swing_near_rate_limit")
        side_results[side] = {
            "classification": classification,
            "phase_swing_segments": int(len(segment_rows)),
            "phase_swing_samples": int(swing_samples),
            "contact_broke_segments": int(contact_break_segments),
            "planted_pct_during_phase_swing": planted_pct,
            "rate_utilization_peak": r_peak_side,
            "rate_driver_joint": r_driver_joint_side,
            "rate_utilization_by_joint_peak": r_by_joint_peak,
            "over_envelope_by_rate": bool(finite(r_peak_side) and r_peak_side > 1.0),
            "rate_utilization": stats(all_r_values),
            "vertical_clearance_ceiling_peak_m_s": max(all_ceilings) if all_ceilings else None,
            "vertical_clearance_ceiling_m_s": stats(all_ceilings),
            "achieved_to_ceiling_ratio_peak": ratio_peak,
            "over_envelope_by_ceiling_ratio": bool(
                finite(ratio_peak) and ratio_peak > 1.0
            ),
            "over_envelope_ratio_segment_count": int(over_envelope_ratio_hits),
            "achieved_to_ceiling_ratio": stats(all_ratios),
            "latency_limited_segment_count": int(latency_hits),
            "structural_reasons": structural_reasons,
            "segments": segment_rows,
        }
        all_segments.extend({"side": side, **item} for item in segment_rows)

    return {
        "status": "PASS_SWING_CLEARANCE_ANALYZED",
        "seed": seed,
        "samples": len(rows),
        "termination_reason": "fall_or_nan" if any(row.get("done") for row in rows) else "duration_or_trace_complete",
        "side_results": side_results,
        "aggregate_classification": classify_seed(
            side_results,
            high_r=high_r,
            low_r=low_r,
            planted_pct_threshold=planted_pct_threshold,
            latency_ticks_threshold=latency_ticks_threshold,
        ),
        "phase_swing_segment_count": len(all_segments),
    }


def aggregate_verdict(seed_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    side_counts: dict[str, dict[str, int]] = {"left": {}, "right": {}}
    driver_counts: dict[str, int] = {}
    for result in seed_results:
        cls = str(result.get("aggregate_classification", result.get("status")))
        counts[cls] = counts.get(cls, 0) + 1
        for side in ("left", "right"):
            side_result = (result.get("side_results") or {}).get(side) or {}
            side_cls = str(side_result.get("classification", "UNKNOWN"))
            side_counts[side][side_cls] = side_counts[side].get(side_cls, 0) + 1
            driver = side_result.get("rate_driver_joint")
            if driver:
                driver_counts[str(driver)] = driver_counts.get(str(driver), 0) + 1
    if not counts:
        verdict = "HOLD_INSUFFICIENT_DATA"
    else:
        verdict = max(counts.items(), key=lambda item: item[1])[0]
    side_verdicts = {
        side: (
            max(side_count.items(), key=lambda item: item[1])[0]
            if side_count
            else "HOLD_INSUFFICIENT_DATA"
        )
        for side, side_count in side_counts.items()
    }
    if (
        side_verdicts.get("left") != side_verdicts.get("right")
        and all(
            side_verdicts.get(side)
            in {"STRUCTURAL", "LATENCY_LIMITED", "DISTILLATION"}
            for side in ("left", "right")
        )
    ):
        verdict = "MIXED_LEG_MODES"
    if verdict == "STRUCTURAL":
        branch = "knee-bend-first swing / longer swing duration; targeted per-seed weighting is likely a band-aid"
    elif verdict == "MIXED_LEG_MODES":
        branch = (
            "split fix: structural leg needs gait/geometry or longer swing duration; "
            "latency-limited leg may need phase advance"
        )
    elif verdict == "DISTILLATION":
        branch = "oracle/relabel generation; targeted swing weighting is a symptom-level but aligned fix"
    elif verdict == "LATENCY_LIMITED":
        branch = "phase-advance swing commands relative to the corrected 3-tick actuator delay"
    elif verdict == "FINE_OR_NO_SWING":
        branch = "clearance is not the limiting branch in these traces"
    else:
        branch = "mixed evidence; inspect per-seed windows before training"
    return {
        "verdict": verdict,
        "classification_counts": counts,
        "side_classification_counts": side_counts,
        "side_verdicts": side_verdicts,
        "rate_driver_joint_counts": driver_counts,
        "selected_fix_branch": branch,
    }


def build_markdown(payload: Mapping[str, Any]) -> str:
    lines = [
        "# Phase 2 Swing-Clearance Diagnostic",
        "",
        f"status: `{payload['status']}`",
        f"aggregate_verdict: `{payload['aggregate_verdict']['verdict']}`",
        f"selected_fix_branch: {payload['aggregate_verdict']['selected_fix_branch']}",
        f"side_verdicts: `{payload['aggregate_verdict'].get('side_verdicts')}`",
        f"rate_driver_joint_counts: `{payload['aggregate_verdict'].get('rate_driver_joint_counts')}`",
        "",
        "## Scope",
        "",
        "- Offline sim/analysis only.",
        "- No robot, SSH, deploy, grounded replay, training, relabeling, or candidate modification.",
        "- Swing segmentation is phase-primary; contact is reported only as the achieved outcome.",
        "",
        "## Inputs",
        "",
        f"- candidate: `{payload['inputs']['candidate']}`",
        f"- candidate_sha256: `{payload['inputs']['candidate_sha256']}`",
        f"- corrected_bridge: `{payload['inputs']['fit_json']}`",
        f"- corrected_bridge_sha256: `{payload['inputs']['fit_json_sha256']}`",
        f"- command_x: `{payload['inputs']['command_x']}`",
        f"- task: `{payload['inputs']['task']}`",
        f"- terrain_hfield_z_scale: `{payload['inputs']['terrain_hfield_z_scale']}`",
        f"- seeds: `{payload['inputs']['seeds']}`",
        "",
        "## Audit",
        "",
        f"- MJCF: `{payload['audit']['xml_path']}`",
        f"- nq/nv/nu: `{payload['audit']['model']['nq']}/{payload['audit']['model']['nv']}/{payload['audit']['model']['nu']}`",
        f"- foot sites: `{payload['audit']['model']['foot_sites']}`",
        f"- pitch-chain dof indices: `{payload['audit']['model']['pitch_chain_dof_indices']}`",
        f"- backlash joints present: `{payload['audit']['model']['backlash_joint_present']}`",
        f"- phase convention: `{payload['audit']['phase_convention']}`",
        "",
        "## Corrected Limits",
        "",
        "| joint | limit_rad_s |",
        "|---|---:|",
    ]
    for joint, limit in payload["corrected_pitch_limits_rad_s"].items():
        lines.append(f"| `{joint}` | {fmt(limit)} |")
    lines.extend(
        [
            "",
            "## Per-Seed Classification",
            "",
            "| seed | status | aggregate | left class | left R | left driver | left planted | left achieved/ceiling | right class | right R | right driver | right planted | right achieved/ceiling |",
            "|---:|---|---|---|---:|---|---:|---:|---|---:|---|---:|---:|",
        ]
    )
    for result in payload["seed_results"]:
        sides = result.get("side_results") or {}
        left = sides.get("left") or {}
        right = sides.get("right") or {}
        lines.append(
            f"| {result.get('seed')} | `{result.get('status')}` | `{result.get('aggregate_classification')}` | "
            f"`{left.get('classification')}` | {fmt(left.get('rate_utilization_peak'))} | "
            f"`{left.get('rate_driver_joint')}` | "
            f"{fmt(left.get('planted_pct_during_phase_swing'))} | "
            f"{fmt(left.get('achieved_to_ceiling_ratio_peak'))} | "
            f"`{right.get('classification')}` | {fmt(right.get('rate_utilization_peak'))} | "
            f"`{right.get('rate_driver_joint')}` | "
            f"{fmt(right.get('planted_pct_during_phase_swing'))} | "
            f"{fmt(right.get('achieved_to_ceiling_ratio_peak'))} |"
        )
    lines.extend(
        [
            "",
            "## Per-Seed Structural Reasons",
            "",
            "| seed | left reasons | right reasons | right per-joint R peak |",
            "|---:|---|---|---|",
        ]
    )
    for result in payload["seed_results"]:
        sides = result.get("side_results") or {}
        left = sides.get("left") or {}
        right = sides.get("right") or {}
        lines.append(
            f"| {result.get('seed')} | `{left.get('structural_reasons')}` | "
            f"`{right.get('structural_reasons')}` | "
            f"`{right.get('rate_utilization_by_joint_peak')}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    verdict = payload["aggregate_verdict"]["verdict"]
    if verdict == "STRUCTURAL":
        lines.append(
            "- Phase-commanded swing windows are planted while pitch-chain rate utilization is near the corrected limits. "
            "Clearance is envelope/geometry constrained; per-seed swing weighting is likely a band-aid."
        )
    elif verdict == "MIXED_LEG_MODES":
        lines.append(
            "- The legs have different limiting modes. The structural leg is over the corrected envelope and must not be "
            "treated as a pure latency problem; the latency-limited leg may still benefit from phase advance."
        )
    elif verdict == "DISTILLATION":
        lines.append(
            "- Phase-commanded swing windows are planted while rate utilization has headroom. "
            "The policy/oracle is under-commanding affordable lift; targeted swing relabeling is the right branch."
        )
    elif verdict == "LATENCY_LIMITED":
        lines.append(
            "- Lift is commanded but achieved lift lags by the corrected actuator delay into or beyond the useful swing window. "
            "The next branch should phase-advance swing commands."
        )
    else:
        lines.append(
            "- Evidence is mixed or insufficient; inspect per-window rows in the JSON before training."
        )
    lines.extend(
        [
            "",
            "## Trace Collection",
            "",
            f"- trace_sweep_status: `{payload['trace_sweep']['status']}`",
            f"- trace_dir: `{payload['trace_sweep'].get('output_dir')}`",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_seeds(value: str) -> list[int]:
    out: list[int] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = [int(item) for item in part.split("-", 1)]
            step = 1 if end >= start else -1
            out.extend(range(start, end + step, step))
        else:
            out.append(int(part))
    return sorted(dict.fromkeys(out))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Diagnose phase-swing clearance using MuJoCo foot Jacobians."
    )
    parser.add_argument(
        "--candidate",
        default="policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx",
    )
    parser.add_argument(
        "--fit-json",
        default="outputs/analysis/actuator_response_fit_corrected_knee.json",
    )
    parser.add_argument("--playground-path", default="../Open_Duck_Playground")
    parser.add_argument("--env-python", default="../envs/open-duck-playground/bin/python")
    parser.add_argument("--command-x", type=float, default=0.08)
    parser.add_argument("--task", default="flat_terrain_backlash")
    parser.add_argument("--duration", type=float, default=15.0)
    parser.add_argument("--terrain-hfield-z-scale", type=float, default=0.0024)
    parser.add_argument("--seeds", type=parse_seeds, default=parse_seeds("0-7"))
    parser.add_argument(
        "--trace-dir",
        default="outputs/analysis/phase2_swing_clearance_trace_x008_z0024",
    )
    parser.add_argument(
        "--output-md",
        default="outputs/analysis/PHASE2_SWING_CLEARANCE_DIAGNOSTIC.md",
    )
    parser.add_argument(
        "--output-json",
        default="outputs/analysis/phase2_swing_clearance_diagnostic.json",
    )
    parser.add_argument("--jax-platform", default="cpu")
    parser.add_argument("--closed-loop-timeout-s", type=float, default=900.0)
    parser.add_argument("--sim-preflight-timeout-s", type=float, default=600.0)
    parser.add_argument("--sweep-timeout-s", type=float, default=12000.0)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--high-rate-utilization", type=float, default=0.80)
    parser.add_argument("--low-rate-utilization", type=float, default=0.60)
    parser.add_argument("--planted-pct-threshold", type=float, default=80.0)
    parser.add_argument("--latency-ticks-threshold", type=int, default=2)
    parser.add_argument("--max-lag-ticks", type=int, default=8)
    parser.add_argument("--invert-phase-map", action="store_true")
    parser.add_argument("--no-run-traces", action="store_true")
    parser.add_argument("--eval-push-enable", action="store_true")
    parser.add_argument("--eval-push-interval-min-s", type=float)
    parser.add_argument("--eval-push-interval-max-s", type=float)
    parser.add_argument("--eval-push-magnitude-min", type=float)
    parser.add_argument("--eval-push-magnitude-max", type=float)
    args = parser.parse_args()

    candidate = (ROOT / args.candidate).resolve() if not Path(args.candidate).is_absolute() else Path(args.candidate)
    fit_json = (ROOT / args.fit_json).resolve() if not Path(args.fit_json).is_absolute() else Path(args.fit_json)
    trace_dir = (ROOT / args.trace_dir).resolve() if not Path(args.trace_dir).is_absolute() else Path(args.trace_dir)
    output_md = (ROOT / args.output_md).resolve() if not Path(args.output_md).is_absolute() else Path(args.output_md)
    output_json = (ROOT / args.output_json).resolve() if not Path(args.output_json).is_absolute() else Path(args.output_json)
    playground_path = (ROOT / args.playground_path).resolve() if not Path(args.playground_path).is_absolute() else Path(args.playground_path)

    fit = load_json(fit_json)
    limits = corrected_pitch_limits(fit)
    missing = [joint for names in SIDE_JOINTS.values() for joint in names if joint not in limits]
    if missing:
        raise SystemExit(f"missing corrected velocity limits for {missing}")

    args.candidate = str(candidate)
    args.fit_json = str(fit_json)
    args.playground_path = str(playground_path)
    args.trace_dir = str(trace_dir)
    trace_sweep = run_trace_sweep(args)

    mujoco, model, data, xml_path = load_model(playground_path, args.task)
    audit_model = model_audit(mujoco, model)
    paths = trace_paths(trace_dir, candidate, args.seeds)
    seed_results = []
    for seed in args.seeds:
        path = paths.get(seed)
        if path is None:
            seed_results.append(
                {"status": "HOLD_TRACE_MISSING", "seed": seed, "trace_path": None}
            )
            continue
        rows = load_trace(path)
        # Keep only fitted records if traces contain multiple modes.
        fitted_rows = [row for row in rows if row.get("mode", "fitted") == "fitted"]
        result = analyze_seed(
            fitted_rows,
            mujoco=mujoco,
            model=model,
            data=data,
            audit=audit_model,
            limits=limits,
            dt_s=args.dt_s,
            invert_phase_map=args.invert_phase_map,
            high_r=args.high_rate_utilization,
            low_r=args.low_rate_utilization,
            planted_pct_threshold=args.planted_pct_threshold,
            latency_ticks_threshold=args.latency_ticks_threshold,
            max_lag_ticks=args.max_lag_ticks,
        )
        result["trace_path"] = str(path)
        seed_results.append(result)

    payload = {
        "status": "PASS_SWING_CLEARANCE_DIAGNOSTIC_REPORTED",
        "inputs": {
            "candidate": str(candidate.relative_to(ROOT) if candidate.is_relative_to(ROOT) else candidate),
            "candidate_sha256": sha256(candidate),
            "fit_json": str(fit_json.relative_to(ROOT) if fit_json.is_relative_to(ROOT) else fit_json),
            "fit_json_sha256": sha256(fit_json),
            "command_x": args.command_x,
            "task": args.task,
            "duration_s": args.duration,
            "terrain_hfield_z_scale": args.terrain_hfield_z_scale,
            "seeds": args.seeds,
        },
        "thresholds": {
            "high_rate_utilization": args.high_rate_utilization,
            "low_rate_utilization": args.low_rate_utilization,
            "planted_pct_threshold": args.planted_pct_threshold,
            "latency_ticks_threshold": args.latency_ticks_threshold,
            "max_lag_ticks": args.max_lag_ticks,
        },
        "audit": {
            "xml_path": str(xml_path),
            "model": audit_model,
            "phase_convention": (
                "phase01=atan2(obs[100], obs[99])/(2*pi); phase<0.5 is "
                "left stance/right swing, phase>=0.5 is right stance/left swing"
            ),
            "phase_map_inverted": bool(args.invert_phase_map),
        },
        "corrected_pitch_limits_rad_s": limits,
        "trace_sweep": trace_sweep,
        "seed_results": seed_results,
        "aggregate_verdict": aggregate_verdict(seed_results),
        "robot_touched": False,
        "ssh_used": False,
        "training_started": False,
        "candidate_modified": False,
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(build_markdown(payload))
    print(f"SWING_CLEARANCE_DIAGNOSTIC {payload['aggregate_verdict']['verdict']}")
    print(f"OUTPUT_MD {output_md}")
    print(f"OUTPUT_JSON {output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
