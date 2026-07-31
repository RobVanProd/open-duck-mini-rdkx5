#!/usr/bin/env python3
"""Report the current Phase 2 trainable-policy branch decision.

This is read-only/offline. It does not train, SSH, deploy, run robot tests, or
change runtime behavior. It consolidates the latest z=0.0075 rough+push
evidence so Phase 2 does not silently continue a closed branch or launch domain
randomization from a warm-start that already fails the task-matched gate.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_TRAINABLE_POLICY_BRANCH_DECISION.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_trainable_policy_branch_decision.json"

DEFAULT_RATE150_Z0075_DECISION = (
    ROOT
    / "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_z0075_intermediate_push_decision.json"
)
DEFAULT_RATE150_Z0075_SCREEN = (
    ROOT
    / "outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_phase_modulated_rate150_z0075_x008_intermediate_push_screen.json"
)
DEFAULT_ITER24_DECISION = (
    ROOT / "outputs/analysis/phase2_z0075_iter24_live_oracle_seed2_active_history_context_rate150_decision.json"
)
DEFAULT_ITER27_DECISION = (
    ROOT / "outputs/analysis/phase2_z0075_iter27_live_oracle_seed6_active_history_context_rate150_decision.json"
)
DEFAULT_PPO_TRACE_DECISION = ROOT / "outputs/analysis/ppo_loc_iter24_step0_trace_failure_decision.json"
DEFAULT_TRAINABLE_SCREEN_DECISION = ROOT / "outputs/analysis/ppo_trainable_warmstart_z0075_push_decision.json"


def now_utc() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    p = Path(path)
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


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


def first_aggregate(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not payload:
        return {}
    aggregate = payload.get("aggregate")
    if not isinstance(aggregate, dict) or not aggregate:
        return {}
    first = next(iter(aggregate.values()))
    return first if isinstance(first, dict) else {}


def stat(aggregate: dict[str, Any], name: str, key: str = "mean") -> Any:
    value = aggregate.get(name)
    if isinstance(value, dict):
        return value.get(key)
    return value


def summarize_z0075_deployable(path: Path, screen_path: Path) -> dict[str, Any]:
    payload = read_json(path)
    out = {"artifact": artifact(path)}
    if payload is None:
        out["status"] = "MISSING_Z0075_DEPLOYABLE_DECISION"
        return out
    aggregate = first_aggregate(read_json(screen_path))
    out.update(
        {
            "status": payload.get("status"),
            "screen_artifact": artifact(screen_path),
            "policy": payload.get("policy"),
            "pass_count": stat(aggregate, "duration_complete_count"),
            "fall_count": stat(aggregate, "fall_count"),
            "track_ratio_mean": stat(aggregate, "track_ratio"),
            "mean_vx_m_s": stat(aggregate, "mean_local_vx_m_s"),
            "max_tracking_p95_rad": stat(aggregate, "max_tracking_p95_rad", "max"),
            "max_p95_velocity_excess_rad_s": stat(aggregate, "max_pitch_vel_limit_excess_rad_s", "max"),
            "max_instant_velocity_excess_rad_s": stat(
                aggregate, "max_pitch_vel_max_limit_excess_rad_s", "max"
            ),
        }
    )
    return out


def summarize_live_oracle(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    out = {"artifact": artifact(path)}
    if payload is None:
        out["status"] = "MISSING_LIVE_ORACLE_DECISION"
        return out
    gate = payload.get("gate") if isinstance(payload.get("gate"), dict) else {}
    if isinstance(gate.get("x008"), dict):
        x008 = gate["x008"]
        seeds = x008.get("seeds") if isinstance(x008.get("seeds"), dict) else {}
        seed_rows = list(seeds.values())
        pass_count = sum(1 for row in seed_rows if row.get("status") == "PASS_CANDIDATE_SIM_GATE")
        fall_count = sum(1 for row in seed_rows if row.get("status") != "PASS_CANDIDATE_SIM_GATE")
        max_velocity_excess = max((row.get("max_vel_excess") or 0.0 for row in seed_rows), default=None)
        seed_summary: Any = seed_rows
    else:
        pass_count = gate.get("pass_count")
        fall_count = gate.get("fall_count")
        max_velocity_excess = gate.get("max_velocity_envelope_excess_rad_s")
        seed_summary = gate.get("seeds")
    candidate = payload.get("candidate")
    if isinstance(candidate, dict):
        candidate_path = candidate.get("path")
        candidate_sha = candidate.get("onnx_sha256")
    else:
        candidate_path = candidate
        candidate_sha = None
    out.update(
        {
            "status": payload.get("status"),
            "candidate": candidate_path,
            "candidate_sha256": candidate_sha,
            "pass_count": pass_count,
            "fall_count": fall_count,
            "max_velocity_envelope_excess_rad_s": max_velocity_excess,
            "seeds": seed_summary,
            "recommended_next": (payload.get("decision") or {}).get("recommended_next")
            if isinstance(payload.get("decision"), dict)
            else None,
        }
    )
    return out


def summarize_ppo_trace(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    out = {"artifact": artifact(path)}
    if payload is None:
        out["status"] = "MISSING_PPO_TRACE_DECISION"
        return out
    seed_results = payload.get("seed_results") or []
    out.update(
        {
            "status": payload.get("status"),
            "policy": payload.get("policy"),
            "manifest": payload.get("manifest"),
            "trace_sweep": payload.get("trace_sweep"),
            "seed_count": len(seed_results),
            "nearest_distance_p95_max": max(
                (row.get("nearest_distance_p95") or 0.0 for row in seed_results), default=None
            ),
            "nearest_action_l1_p95_max": max(
                (row.get("nearest_action_l1_p95") or 0.0 for row in seed_results), default=None
            ),
            "decision": payload.get("decision"),
        }
    )
    return out


def summarize_trainable_screen(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    out = {"artifact": artifact(path)}
    if payload is None:
        out["status"] = "MISSING_TRAINABLE_SCREEN_DECISION"
        return out
    candidates = payload.get("candidates") if isinstance(payload.get("candidates"), dict) else {}
    out.update(
        {
            "status": payload.get("status"),
            "gate": payload.get("gate"),
            "candidate_count": len(candidates),
            "candidates": {
                name: {
                    "onnx": row.get("onnx"),
                    "sha256": row.get("sha256"),
                    "pass_count": row.get("pass_count"),
                    "total_count": row.get("total_count"),
                    "fall_count": row.get("fall_count"),
                    "track_ratio_mean": row.get("track_ratio_mean"),
                    "mean_vx_m_s": row.get("mean_vx_m_s"),
                    "decision": row.get("decision"),
                }
                for name, row in candidates.items()
                if isinstance(row, dict)
            },
            "decision": payload.get("decision"),
        }
    )
    return out


def decide(payload: dict[str, Any]) -> tuple[str, str, list[str]]:
    live_iter27 = payload["iter27_live_oracle"].get("status")
    ppo_screen = payload["trainable_warmstart_screen"].get("status")
    ppo_trace = payload["ppo_step0_trace"].get("status")
    z0075 = payload["z0075_deployable_boundary"].get("status")

    if (
        live_iter27 == "HOLD_ITER27_LIVE_ORACLE_MULTI_SEED_REGRESSION"
        and ppo_screen == "HOLD_NO_TASK_MATCHED_TRAINABLE_WARMSTART"
        and ppo_trace == "HOLD_PPO_LOC_STEP0_CLOSED_LOOP_INSTABILITY"
    ):
        return (
            "HOLD_TASK_MATCHED_TRAINABLE_POLICY_MISSING",
            "Phase 2 has in-envelope deployable walkers, but no trainable PPO/DR warm-start currently preserves the z=0.0075 rough+push behavior. BC-only live-oracle continuation is closed as-is, and long domain-randomization training should not launch until a task-matched step-0 trainable policy clears the gate.",
            [
                "Use Iter24 as the latest useful deployable analysis baseline, not Iter25/26/27.",
                "Do not continue scalar anchor weighting or BC-only live-oracle relabeling as the next default branch.",
                "Build a trainable policy class/objective that preserves the deployable baseline under the canonical z=0.0075 push gate before any DR escalation.",
                "Acceptable next branches: recurrent/hidden-state actor with explicit export, validation-aware mixture/ensemble diagnostic, or PPO fine-tuning only after a task-matched behavior-preserving step-0 gate passes.",
            ],
        )

    if str(z0075).startswith("HOLD"):
        return (
            "HOLD_DEPLOYABLE_BOUNDARY_NOT_ROBUST_ENOUGH",
            "The deployable baseline itself still holds at the z=0.0075 intermediate-push boundary. Improve the deployable behavior before building a trainable DR parent.",
            ["Use the z=0.0075 seed0/seed7 boundary as the next deployable robustness target."],
        )

    return (
        "HOLD_PHASE2_BRANCH_EVIDENCE_INCOMPLETE",
        "The required branch evidence is missing or inconsistent. Regenerate the current z=0.0075 deployable, live-oracle, PPO trace, and trainable warm-start decisions before launching training.",
        ["Regenerate missing decision artifacts and rerun this reporter."],
    )


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    status = payload["status"]
    z = payload["z0075_deployable_boundary"]
    iter24 = payload["iter24_live_oracle"]
    iter27 = payload["iter27_live_oracle"]
    ppo_trace = payload["ppo_step0_trace"]
    screen = payload["trainable_warmstart_screen"]

    lines = [
        "# Phase 2 Trainable Policy Branch Decision",
        "",
        f"status: `{status}`",
        "",
        "## Executive Summary",
        "",
        payload["summary"],
        "",
        "Robot validation remains blocked. No robot tests, SSH, deployment, grounded replay, "
        "runtime behavior change, or training was performed by this reporter.",
        "",
        "## Current Evidence",
        "",
        "### Deployable Boundary",
        "",
        f"- status: `{z.get('status')}`",
        f"- policy: `{z.get('policy')}`",
        f"- duration_complete_count: `{z.get('pass_count')}`",
        f"- fall_count: `{z.get('fall_count')}`",
        f"- mean track ratio: `{z.get('track_ratio_mean')}`",
        f"- mean vx: `{z.get('mean_vx_m_s')}`",
        f"- max tracking p95: `{z.get('max_tracking_p95_rad')}`",
        f"- max p95 velocity excess: `{z.get('max_p95_velocity_excess_rad_s')}`",
        f"- max instantaneous velocity excess: `{z.get('max_instant_velocity_excess_rad_s')}`",
        "",
        "Interpretation: this is useful deployable behavior, but the harder z=0.0075 "
        "intermediate-push boundary is still a hold, not a promotion gate.",
        "",
        "### Live-Oracle BC Loop",
        "",
        f"- Iter24 status: `{iter24.get('status')}`",
        f"- Iter24 candidate: `{iter24.get('candidate')}`",
        f"- Iter24 compact pass/fall: `{iter24.get('pass_count')}` / `{iter24.get('fall_count')}`",
        f"- Iter27 status: `{iter27.get('status')}`",
        f"- Iter27 candidate: `{iter27.get('candidate')}`",
        f"- Iter27 compact pass/fall: `{iter27.get('pass_count')}` / `{iter27.get('fall_count')}`",
        f"- Iter27 max velocity-envelope excess: `{iter27.get('max_velocity_envelope_excess_rad_s')}`",
        "",
        "Interpretation: Iter27 regressed relative to Iter24. Continuing the same BC-only "
        "live-oracle rung as-is is closed for now.",
        "",
        "### PPO-Compatible Warm-Starts",
        "",
        f"- trainable screen status: `{screen.get('status')}`",
        f"- candidate count: `{screen.get('candidate_count')}`",
        "",
        "| candidate | pass/total | falls | track ratio mean | mean vx | decision |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for name, row in (screen.get("candidates") or {}).items():
        lines.append(
            f"| `{name}` | `{row.get('pass_count')}/{row.get('total_count')}` | "
            f"`{row.get('fall_count')}` | `{row.get('track_ratio_mean')}` | "
            f"`{row.get('mean_vx_m_s')}` | {row.get('decision')} |"
        )
    lines.extend(
        [
            "",
            f"- PPO trace status: `{ppo_trace.get('status')}`",
            f"- PPO trace policy: `{ppo_trace.get('policy')}`",
            f"- nearest distance p95 max: `{ppo_trace.get('nearest_distance_p95_max')}`",
            f"- nearest action L1 p95 max: `{ppo_trace.get('nearest_action_l1_p95_max')}`",
            "",
            "Interpretation: the PPO-loc regression is not explained by missing local "
            "manifest coverage or a large local action-fit error. The failed step-0 "
            "checkpoint is not a valid DR parent.",
            "",
            "## Decision",
            "",
            "Do not launch long Phase 2 domain-randomization training from any current "
            "PPO-compatible checkpoint. First produce a task-matched trainable policy "
            "whose step-0 export clears the z=0.0075 rough+push corrected-bridge gate.",
            "",
            "Required next conditions before DR escalation:",
            "",
        ]
    )
    for item in payload["next_required"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Gate To Reopen Training",
            "",
            "A new trainable parent must pass, at minimum:",
            "",
            "- task: `rough_terrain_backlash`",
            "- terrain_hfield_z_scale: `0.0075`",
            "- reset: `home-support`, `reset_settle_ticks=10`",
            "- bridge: corrected fitted actuator bridge",
            "- command: `x=0.08`",
            "- push: `0.075-0.125`, interval `1.0-1.5s`",
            "- seeds: `0,1,2,6,7` compact screen before full 8-seed promotion",
            "- corrected velocity-envelope excess: `0`",
            "",
            "Only after this step-0 behavior-preservation gate passes should staged "
            "domain randomization resume.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "generated_at": now_utc(),
        "scope": "offline_phase2_trainable_policy_branch_decision",
        "z0075_deployable_boundary": summarize_z0075_deployable(
            args.rate150_z0075_decision, args.rate150_z0075_screen
        ),
        "iter24_live_oracle": summarize_live_oracle(args.iter24_decision),
        "iter27_live_oracle": summarize_live_oracle(args.iter27_decision),
        "ppo_step0_trace": summarize_ppo_trace(args.ppo_trace_decision),
        "trainable_warmstart_screen": summarize_trainable_screen(args.trainable_screen_decision),
    }
    status, summary, next_required = decide(payload)
    payload["status"] = status
    payload["summary"] = summary
    payload["next_required"] = next_required
    payload["guardrails"] = [
        "No robot tests.",
        "No SSH.",
        "No deploy.",
        "No grounded replay.",
        "No runtime behavior change.",
        "Do not launch DR from a step-0 checkpoint that fails the task-matched gate.",
    ]
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rate150-z0075-decision", type=Path, default=DEFAULT_RATE150_Z0075_DECISION)
    parser.add_argument("--rate150-z0075-screen", type=Path, default=DEFAULT_RATE150_Z0075_SCREEN)
    parser.add_argument("--iter24-decision", type=Path, default=DEFAULT_ITER24_DECISION)
    parser.add_argument("--iter27-decision", type=Path, default=DEFAULT_ITER27_DECISION)
    parser.add_argument("--ppo-trace-decision", type=Path, default=DEFAULT_PPO_TRACE_DECISION)
    parser.add_argument("--trainable-screen-decision", type=Path, default=DEFAULT_TRAINABLE_SCREEN_DECISION)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload(args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, args.output_md)
    print(payload["status"])
    print(rel(args.output_md))
    print(rel(args.output_json))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
