#!/usr/bin/env python3
"""Summarize the current Phase 2 robustness-training state.

This reporter is offline-only and read-only. It does not train, SSH, deploy,
touch the robot, or modify runtime behavior. It records the current corrected
rate165 Phase 2 state so follow-on planning does not fall back to stale
pre-correction or scalar-support branches.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "PHASE2_CURRENT_STATUS.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "phase2_current_status.json"

DEFAULT_CANDIDATE_DECISION = (
    ROOT / "outputs/analysis/phase2_corrected_live_oracle_iter1_rate165_candidate_decision_20260703.json"
)
DEFAULT_RATE165_X008_GATE = (
    ROOT / "outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter1_phase_contact_rate165_x008_gate.json"
)
DEFAULT_RATE165_X0_GATE = (
    ROOT / "outputs/analysis/phase2_z0026_corrected_source_live_oracle_iter1_phase_contact_rate165_x0_gate.json"
)
DEFAULT_PPO_WARMSTART_FIDELITY = (
    ROOT / "outputs/analysis/phase2_rate165_ppo_loc_warmstart_step0_export_fidelity.json"
)
DEFAULT_STAGE_A_RESULT = ROOT / "outputs/analysis/phase2_stage_a_rate165_narrow_flat_result.json"
DEFAULT_MOTION_PRESERVE_RESULT = (
    ROOT / "outputs/analysis/phase2_rate165_motion_preserve_cpu2240_result.json"
)
DEFAULT_COLAB_SESSION_STATUS = ROOT / "outputs/analysis/phase2_colab_session_status.json"


def now_utc() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def artifact(path: Path) -> dict[str, Any]:
    return {
        "path": rel(path),
        "exists": path.exists(),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
    }


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def aggregate_metric(gate: dict[str, Any] | None, name: str, stat: str = "mean") -> Any:
    if gate is None:
        return None
    aggregate = gate.get("aggregate") or {}
    if not aggregate:
        return None
    first_policy = next(iter(aggregate.values()), {})
    value = first_policy.get(name)
    if isinstance(value, dict):
        return value.get(stat)
    return value


def gate_summary(path: Path) -> dict[str, Any]:
    data = read_json(path)
    out: dict[str, Any] = {"artifact": artifact(path)}
    if data is None:
        out["status"] = "MISSING_GATE"
        return out

    results = data.get("results") or []
    statuses = [row.get("status") for row in results]
    pass_count = statuses.count("PASS_CANDIDATE_SIM_GATE")
    fall_count = aggregate_metric(data, "fall_count")
    duration_count = aggregate_metric(data, "duration_complete_count")
    config = data.get("config") or {}
    out.update(
        {
            "status": "PASS_GATE" if pass_count == len(results) and results else "HOLD_GATE",
            "command_x": config.get("command_x"),
            "task": config.get("task"),
            "terrain_hfield_z_scale": config.get("terrain_hfield_z_scale"),
            "reset_mode": config.get("reset_mode"),
            "bridge_mode": config.get("bridge_mode"),
            "duration_s": config.get("duration_s"),
            "seeds": config.get("seeds"),
            "pass_count": pass_count,
            "total_count": len(results),
            "fall_count": fall_count,
            "duration_complete_count": duration_count,
            "track_ratio_mean": aggregate_metric(data, "track_ratio"),
            "mean_local_vx_m_s": aggregate_metric(data, "mean_local_vx_m_s"),
            "max_pitch_vel_p95_rad_s": aggregate_metric(data, "max_pitch_vel_p95_rad_s", "max"),
            "max_tracking_p95_rad": aggregate_metric(data, "max_tracking_p95_rad", "max"),
            "p95_velocity_excess_rad_s": aggregate_metric(
                data, "max_pitch_vel_limit_excess_rad_s", "max"
            ),
            "max_velocity_excess_rad_s": aggregate_metric(
                data, "max_pitch_vel_max_limit_excess_rad_s", "max"
            ),
            "single_support_pct": aggregate_metric(data, "single_support_pct"),
            "double_support_pct": aggregate_metric(data, "double_support_pct"),
        }
    )
    return out


def summarize_candidate(path: Path) -> dict[str, Any]:
    data = read_json(path)
    out: dict[str, Any] = {"artifact": artifact(path)}
    if data is None:
        out["status"] = "MISSING_CANDIDATE_DECISION"
        return out
    out.update(
        {
            "status": data.get("status"),
            "candidate_dir": data.get("candidate_dir"),
            "candidate_onnx": data.get("candidate_onnx"),
            "candidate_onnx_sha256": data.get("candidate_onnx_sha256"),
            "candidate_npz": data.get("candidate_npz"),
            "candidate_npz_sha256": data.get("candidate_npz_sha256"),
            "scope": data.get("scope"),
            "fit": data.get("fit"),
            "x008_gate": data.get("x008_gate"),
            "x0_gate": data.get("x0_gate"),
        }
    )
    return out


def summarize_stage_a(path: Path) -> dict[str, Any]:
    data = read_json(path)
    out: dict[str, Any] = {"artifact": artifact(path)}
    if data is None:
        out["status"] = "MISSING_STAGE_A_RESULT"
        return out
    out.update(
        {
            "status": data.get("status"),
            "training": data.get("training"),
            "x008_gate": data.get("x008_gate"),
            "checkpoint_triage_seed0": data.get("checkpoint_triage_seed0"),
        }
    )
    return out


def summarize_motion_preserve(path: Path) -> dict[str, Any]:
    data = read_json(path)
    out: dict[str, Any] = {"report_artifact": artifact(path)}
    if data is None:
        out["status"] = "MISSING_MOTION_PRESERVE_RESULT"
        return out
    out.update(data)
    return out


def summarize_fidelity(path: Path) -> dict[str, Any]:
    data = read_json(path)
    out: dict[str, Any] = {"artifact": artifact(path)}
    if data is None:
        out["status"] = "MISSING_WARMSTART_FIDELITY"
        return out
    out.update(data)
    return out


def decide(payload: dict[str, Any]) -> tuple[str, str]:
    candidate_ok = payload["candidate"].get("status") == "PASS_OFFLINE_CORRECTED_BRIDGE_CANDIDATE_READY"
    x008_ok = payload["rate165_x008_gate"].get("status") == "PASS_GATE"
    x0_ok = payload["rate165_x0_gate"].get("status") == "PASS_GATE"
    stage_a_hold = str(payload["stage_a_result"].get("status", "")).startswith("HOLD")
    motion_hold = str(payload["motion_preserve_result"].get("status", "")).startswith("HOLD")

    if candidate_ok and x008_ok and x0_ok and stage_a_hold and motion_hold:
        return (
            "HOLD_PHASE2_PPO_DR_STANDSTILL_REGRESSION",
            "The corrected rate165 candidate is still the offline baseline, but both the full Stage A PPO/DR run and the tiny motion-preservation PPO smoke collapse the walking warm-start into double-support standstill. Do not launch another scalar PPO/DR run from this recipe. Next offline work should use a phase-aware/live-oracle student or another training structure that preserves single support before reintroducing domain randomization.",
        )
    if candidate_ok and x008_ok and x0_ok:
        return (
            "PASS_PHASE2_RATE165_BASELINE_READY",
            "The corrected rate165 baseline gates pass. Run only a bounded training experiment that explicitly preserves single-support walking before widening randomization.",
        )
    return (
        "HOLD_PHASE2_BASELINE_EVIDENCE_INCOMPLETE",
        "The corrected rate165 baseline evidence is missing or no longer passes; restore the canonical corrected-bridge x=0.08 and x=0.0 gates before Phase 2 training.",
    )


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    candidate = payload["candidate"]
    x008 = payload["rate165_x008_gate"]
    x0 = payload["rate165_x0_gate"]
    stage_a = payload["stage_a_result"]
    motion = payload["motion_preserve_result"]
    fidelity = payload["ppo_warmstart_fidelity"]

    lines = [
        "# Phase 2 Current Status",
        "",
        f"status: `{payload['status']}`",
        f"generated_at: `{payload['generated_at']}`",
        "",
        "## Scope",
        "",
        "Offline-only Phase 2 robustness training status. This report does not",
        "SSH, deploy, run robot tests, start training, or change runtime behavior.",
        "",
        "## Corrected Rate165 Baseline",
        "",
        f"- candidate status: `{candidate.get('status')}`",
        f"- candidate ONNX: `{candidate.get('candidate_onnx')}`",
        f"- candidate ONNX sha256: `{candidate.get('candidate_onnx_sha256')}`",
        f"- candidate NPZ sha256: `{candidate.get('candidate_npz_sha256')}`",
        f"- corrected decision artifact: `{candidate['artifact']['path']}`",
        "",
        "| gate | status | pass/total | x | z | vx mean | track ratio | single support | double support | max vel p95 | max tracking p95 | vel excess |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, gate in [("rate165_x008", x008), ("rate165_x0", x0)]:
        lines.append(
            "| {name} | `{status}` | {pass_count}/{total_count} | {x} | {z} | {vx} | {track} | {single} | {double} | {vel} | {tracking} | {excess} |".format(
                name=name,
                status=gate.get("status"),
                pass_count=gate.get("pass_count", 0),
                total_count=gate.get("total_count", 0),
                x=fmt(gate.get("command_x"), 3),
                z=fmt(gate.get("terrain_hfield_z_scale"), 4),
                vx=fmt(gate.get("mean_local_vx_m_s"), 4),
                track=fmt(gate.get("track_ratio_mean"), 4),
                single=fmt(gate.get("single_support_pct"), 4),
                double=fmt(gate.get("double_support_pct"), 4),
                vel=fmt(gate.get("max_pitch_vel_p95_rad_s"), 4),
                tracking=fmt(gate.get("max_tracking_p95_rad"), 4),
                excess=fmt(gate.get("max_velocity_excess_rad_s"), 4),
            )
        )

    lines.extend(
        [
            "",
            "## PPO-Compatible Warm-Start",
            "",
            f"- fidelity artifact: `{fidelity['artifact']['path']}`",
            f"- status: `{fidelity.get('status')}`",
            f"- p95 abs error: `{fmt((fidelity.get('fidelity') or {}).get('p95_abs_error'), 10)}`",
            f"- max abs error: `{fmt((fidelity.get('fidelity') or {}).get('max_abs_error'), 10)}`",
            "",
            "## Failed PPO / Domain-Randomization Attempts",
            "",
            "### Stage A A100 Narrow Flat",
            "",
            f"- status: `{stage_a.get('status')}`",
            f"- artifact: `{stage_a['artifact']['path']}`",
            f"- final step: `{(stage_a.get('training') or {}).get('final_step')}`",
            f"- final ONNX sha256: `{(stage_a.get('training') or {}).get('final_onnx_sha256')}`",
        ]
    )
    stage_gate = stage_a.get("x008_gate") or {}
    lines.extend(
        [
            f"- x=0.08 gate: `{stage_gate.get('status')}`",
            f"- mean vx: `{fmt(stage_gate.get('mean_local_vx_m_s'), 4)} m/s`",
            f"- track ratio: `{fmt(stage_gate.get('track_ratio'), 4)}`",
            f"- single support: `{fmt(stage_gate.get('single_support_pct'), 4)}%`",
            f"- double support: `{fmt(stage_gate.get('double_support_pct'), 4)}%`",
            f"- corrected velocity excess: `{fmt(stage_gate.get('max_velocity_excess_rad_s'), 4)}`",
            "",
            "### Motion-Preservation CPU2240 Smoke",
            "",
            f"- status: `{motion.get('status')}`",
            f"- artifact: `{motion['report_artifact']['path']}`",
            f"- exported ONNX sha256: `{(motion.get('artifact') or {}).get('onnx_sha256')}`",
        ]
    )
    motion_x008 = motion.get("x008_compact_gate") or {}
    motion_x0 = motion.get("x000_compact_gate") or {}
    lines.extend(
        [
            f"- x=0.08 compact gate: `{motion_x008.get('status')}`",
            f"- x=0.08 mean vx: `{fmt(motion_x008.get('mean_local_vx_m_s'), 4)} m/s`",
            f"- x=0.08 track ratio: `{fmt(motion_x008.get('track_ratio'), 4)}`",
            f"- x=0.08 single/double support: `{fmt(motion_x008.get('single_support_pct'), 4)}% / {fmt(motion_x008.get('double_support_pct'), 4)}%`",
            f"- x=0.0 compact gate: `{motion_x0.get('status')}`",
            "",
            "## Decision",
            "",
            f"- next_status: `{payload['status']}`",
            f"- next_action: {payload['next_action']}",
            "",
            "## Guardrails",
            "",
            "- Do not advance to push/terrain DR stages from the rejected Stage A run.",
            "- Do not scale the CPU2240 motion-preservation recipe into another long A100 run.",
            "- Keep the corrected bridge and per-joint corrected velocity envelope authoritative.",
            "- No robot, SSH, deploy, grounded replay, or runtime behavior change is authorized by this report.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-decision", default=str(DEFAULT_CANDIDATE_DECISION))
    parser.add_argument("--rate165-x008-gate", default=str(DEFAULT_RATE165_X008_GATE))
    parser.add_argument("--rate165-x0-gate", default=str(DEFAULT_RATE165_X0_GATE))
    parser.add_argument("--ppo-warmstart-fidelity", default=str(DEFAULT_PPO_WARMSTART_FIDELITY))
    parser.add_argument("--stage-a-result", default=str(DEFAULT_STAGE_A_RESULT))
    parser.add_argument("--motion-preserve-result", default=str(DEFAULT_MOTION_PRESERVE_RESULT))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    payload: dict[str, Any] = {
        "generated_at": now_utc(),
        "candidate": summarize_candidate(Path(args.candidate_decision)),
        "rate165_x008_gate": gate_summary(Path(args.rate165_x008_gate)),
        "rate165_x0_gate": gate_summary(Path(args.rate165_x0_gate)),
        "ppo_warmstart_fidelity": summarize_fidelity(Path(args.ppo_warmstart_fidelity)),
        "stage_a_result": summarize_stage_a(Path(args.stage_a_result)),
        "motion_preserve_result": summarize_motion_preserve(Path(args.motion_preserve_result)),
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
    }
    status, next_action = decide(payload)
    payload["status"] = status
    payload["next_action"] = next_action

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(status)
    return 0 if status.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
