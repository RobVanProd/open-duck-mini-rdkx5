#!/usr/bin/env python3
"""Summarize deployable-policy branch evidence and recommend the next branch.

This is an offline decision helper. It reads existing analysis JSON artifacts
from candidate gates and curation probes, then writes a compact markdown/json
decision record. It does not train, run simulation, SSH, deploy, or touch the
robot.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "NEXT_DEPLOYABLE_POLICY_BRANCH_DECISION.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "next_deployable_policy_branch_decision.json"


def finite(value: Any) -> bool:
    return isinstance(value, int | float) and value == value and value not in {float("inf"), float("-inf")}


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, str):
        return value
    if finite(value):
        return f"{float(value):.{digits}f}"
    return "NA"


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def custom_rows(path: Path) -> list[dict[str, Any]]:
    data = load_json(path)
    if not data:
        return []
    rows = []
    for row in data.get("rows", []):
        rows.append(
            {
                "status": row.get("overall_status") or row.get("status"),
                "samples": row.get("samples"),
                "termination": row.get("termination_reason"),
                "vx": row.get("vx_mean") or row.get("mean_local_vx"),
                "track_ratio": row.get("track_ratio"),
                "max_pitch_velocity_p95": row.get("max_sent_p95") or row.get("max_pitch_vel_p95"),
                "max_tracking_p95": row.get("max_tracking_p95"),
                "body_pitch_p95": row.get("body_pitch_p95"),
                "base_height_min": row.get("base_height_min"),
            }
        )
    return rows


def run_candidate_rows(path: Path) -> list[dict[str, Any]]:
    data = load_json(path)
    if not data:
        return []
    rows = []
    for result in data.get("results", []):
        summary = result.get("summary") or {}
        rows.append(
            {
                "status": summary.get("overall_status") or result.get("status"),
                "samples": summary.get("samples"),
                "termination": summary.get("termination_reason"),
                "vx": summary.get("mean_local_vx_m_s"),
                "track_ratio": summary.get("track_ratio"),
                "max_pitch_velocity_p95": summary.get("max_pitch_vel_p95_rad_s"),
                "max_tracking_p95": summary.get("max_tracking_p95_rad"),
                "body_pitch_p95": summary.get("body_pitch_p95_rad"),
                "base_height_min": summary.get("base_height_min_m"),
            }
        )
    return rows


def exact_blend_rows(path: Path) -> list[dict[str, Any]]:
    data = load_json(path)
    if not data:
        return []
    rows = []
    for row in data.get("rows", []):
        rows.append(
            {
                "status": row.get("status") or data.get("status"),
                "samples": row.get("samples"),
                "termination": row.get("termination_reason") or row.get("termination"),
                "vx": row.get("mean_local_vx_m_s"),
                "track_ratio": row.get("track_ratio"),
                "max_pitch_velocity_p95": row.get("max_pitch_chain_sent_target_p95_rad_s"),
                "max_tracking_p95": row.get("max_pitch_chain_tracking_p95_rad"),
                "body_pitch_p95": row.get("body_pitch_abs_p95_rad"),
                "base_height_min": row.get("base_height_min_m"),
            }
        )
    return rows


def summarize_rows(name: str, path: str, rows: list[dict[str, Any]], status: str | None = None) -> dict[str, Any]:
    values = {
        "vx": [float(row["vx"]) for row in rows if finite(row.get("vx"))],
        "track_ratio": [float(row["track_ratio"]) for row in rows if finite(row.get("track_ratio"))],
        "max_pitch_velocity_p95": [
            float(row["max_pitch_velocity_p95"]) for row in rows if finite(row.get("max_pitch_velocity_p95"))
        ],
        "max_tracking_p95": [
            float(row["max_tracking_p95"]) for row in rows if finite(row.get("max_tracking_p95"))
        ],
        "body_pitch_p95": [float(row["body_pitch_p95"]) for row in rows if finite(row.get("body_pitch_p95"))],
        "base_height_min": [float(row["base_height_min"]) for row in rows if finite(row.get("base_height_min"))],
    }
    statuses = sorted({str(row.get("status")) for row in rows if row.get("status")})
    terminations = [str(row.get("termination")) for row in rows if row.get("termination")]
    duration_complete = sum(1 for item in terminations if item == "duration_complete")
    falls = sum(1 for item in terminations if item != "duration_complete")
    return {
        "name": name,
        "path": path,
        "status": status or (statuses[0] if len(statuses) == 1 else ",".join(statuses) if statuses else "UNKNOWN"),
        "runs": len(rows),
        "duration_complete": duration_complete,
        "falls_or_terminations": falls,
        "vx_mean": mean(values["vx"]),
        "track_ratio_mean": mean(values["track_ratio"]),
        "max_pitch_velocity_p95_min": min(values["max_pitch_velocity_p95"]) if values["max_pitch_velocity_p95"] else None,
        "max_pitch_velocity_p95_max": max(values["max_pitch_velocity_p95"]) if values["max_pitch_velocity_p95"] else None,
        "max_pitch_velocity_p95_mean": mean(values["max_pitch_velocity_p95"]),
        "max_tracking_p95_min": min(values["max_tracking_p95"]) if values["max_tracking_p95"] else None,
        "max_tracking_p95_max": max(values["max_tracking_p95"]) if values["max_tracking_p95"] else None,
        "max_tracking_p95_mean": mean(values["max_tracking_p95"]),
        "body_pitch_p95_mean": mean(values["body_pitch_p95"]),
        "base_height_min_mean": mean(values["base_height_min"]),
    }


def checkpoint_sweep_summary(path: Path, name: str) -> dict[str, Any] | None:
    data = load_json(path)
    if not data:
        return None
    decisions = data.get("promotion_decisions", [])
    best = None
    for decision in decisions:
        ratio = decision.get("positive_command_tracking_ratio_mean")
        tracking = decision.get("max_pitch_tracking_p95_rad")
        if not finite(ratio):
            continue
        score = float(ratio) - 0.5 * float(tracking or 0.0)
        if best is None or score > best["score"]:
            best = {**decision, "score": score}
    if best is None:
        return None
    return {
        "name": name,
        "path": str(path),
        "status": best.get("status"),
        "policy": best.get("policy_label") or best.get("policy"),
        "positive_command_tracking_ratio_mean": best.get("positive_command_tracking_ratio_mean"),
        "max_pitch_tracking_p95_rad": best.get("max_pitch_tracking_p95_rad"),
        "max_pitch_sent_target_velocity_p95_rad_s": best.get("max_pitch_sent_target_velocity_p95_rad_s"),
        "pass_count": best.get("pass_count"),
        "required_command_count": best.get("required_command_count"),
        "failure_reasons": best.get("failure_reasons"),
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    candidate_specs = [
        (
            "exact selector blend ONNX",
            "outputs/analysis/source_vx_selector_trace_blend080_exact_onnx_multi_seed_fitted_backlash_summary.json",
            exact_blend_rows,
        ),
        (
            "right-knee 4.3 curation",
            "outputs/analysis/source_vx_selector_trace_rk_limited_4p3_blend080_exact_onnx_multi_seed_fitted_backlash_summary.json",
            custom_rows,
        ),
        (
            "pitch-chain 4.3 curation",
            "outputs/analysis/source_vx_selector_trace_pitch_chain_limited_4p3_blend080_exact_onnx_multiseed_fitted_backlash_summary.json",
            run_candidate_rows,
        ),
        (
            "right-knee transition filter",
            "outputs/analysis/source_vx_selector_trace_rk_transition_spike_filtered_blend080_exact_onnx_multiseed_fitted_backlash_summary.json",
            run_candidate_rows,
        ),
        (
            "pitch-chain 4.3 PPO-shape rate student",
            "outputs/analysis/pitch_chain_4p3_ppo_shape_rate_student_multiseed_fitted_backlash.json",
            run_candidate_rows,
        ),
        (
            "pitch-chain 4.3 PPO warm-start step-0",
            "outputs/analysis/pitch_chain_4p3_ppo_shape_rate_student_warmstart_step0_multiseed_fitted_backlash.json",
            run_candidate_rows,
        ),
        (
            "PPO warm-start tracking correction smoke",
            "outputs/analysis/pitch_chain_4p3_ppo_warmstart_tracking_correction_smoke_seed1_seed4_screen.json",
            run_candidate_rows,
        ),
    ]
    candidates = []
    for name, rel_path, reader in candidate_specs:
        path = ROOT / rel_path
        candidates.append(summarize_rows(name, rel_path, reader(path)))

    sweep_summaries = [
        item
        for item in [
            checkpoint_sweep_summary(
                ROOT / "outputs/analysis/actuator_tracking_behavior_prior_weight_blend_sweep.json",
                "behavior-prior PPO weight blend sweep",
            ),
            checkpoint_sweep_summary(
                ROOT
                / "outputs/analysis/actuator_tracking_behavior_prior_probe_local_cpu_checkpoint_sweep/candidate_checkpoint_sweep.json",
                "behavior-prior PPO checkpoint sweep",
            ),
        ]
        if item is not None
    ]

    right_knee_spike_evidence = {
        "right_knee_action_spikes_gt_3p75": 506,
        "right_knee_action_samples": 3992,
        "within_2_ticks_of_contact_transition": 404,
        "source": "computed from source_vx_selector_fitted_bridge_x008_10s_traces in this branch",
    }
    branch_closures = [
        {
            "branch": "uniform pitch-chain clipping",
            "result": "closed",
            "reason": "4.3 rad/s cap across the pitch chain was numerically indistinguishable from right-knee-only 4.3 and still held tracking.",
        },
        {
            "branch": "transition-adjacent sample deletion",
            "result": "closed",
            "reason": "filtering preserved stability but reduced forward progress and raised target-velocity p95.",
        },
        {
            "branch": "post-hoc ONNX weight interpolation",
            "result": "closed",
            "reason": "small blends did not reduce tracking; larger blends regressed toward low progress.",
        },
        {
            "branch": "scalar behavior-prior PPO smoke",
            "result": "closed",
            "reason": "prior PPO smoke and A100 probe improved reward or calmness while losing useful forward motion.",
        },
        {
            "branch": "feed-forward PPO-shape BC smoothing",
            "result": "closed",
            "reason": "pitch-chain 4.3 PPO-shape rate student lowered target velocity and tracking slightly but lost progress and still held the strict fitted-bridge tracking gate.",
        },
        {
            "branch": "static gate-aware source-VX relabeling",
            "result": "closed",
            "reason": "targeted relabeling of strict-gate seed 1/4 states produced only tiny tracking changes and did not clear the same fitted-bridge tracking hold.",
        },
        {
            "branch": "naive PPO tracking-cost correction from BC warm start",
            "result": "closed",
            "reason": "PPO resume/export works, but a tiny tracking-cost correction reduced tracking by nearly freezing; seed 1/4 screen fell to ~0 progress.",
        },
    ]
    recommendation = {
        "status": "PLAN_GATE_AWARE_ROLLOUT_CORRECTION_OR_RECURRENT_STUDENT",
        "recommended_next": "Do not run another clip/filter/weight-blend/feed-forward-BC branch or naive tracking-cost PPO smoke. Build a gate-aware deployable-policy training path that preserves forward behavior explicitly while directly correcting fitted-bridge tracking through the right-knee contact transition.",
        "minimum_requirements": [
            "uses the standard strict fitted-backlash x=0.08 multi-seed gate as the primary score",
            "compares against the exact selector blend and PPO-shape warm-start baselines",
            "preserves duration_complete 8/8 and mean vx near 0.045-0.050 m/s before claiming progress",
            "reduces max pitch velocity p95 below the 3.75 rad/s envelope or explicitly documents why the gate remains held",
            "reduces max tracking p95 materially below the current ~0.27 rad plateau",
            "does not pass by freezing, reversing, or shortening the horizon",
        ],
        "candidate_mechanisms": [
            "DAgger/rollout correction with the strict gate failure states added back to the teacher dataset",
            "recurrent or phase-aware student for the stance-transition discontinuity",
            "trust-region PPO fine-tune from the validated PPO-compatible BC warm start, with loss of forward progress treated as an immediate stop condition",
        ],
    }
    return {
        "status": recommendation["status"],
        "robot_touched": False,
        "candidates": candidates,
        "sweep_summaries": sweep_summaries,
        "right_knee_spike_evidence": right_knee_spike_evidence,
        "branch_closures": branch_closures,
        "recommendation": recommendation,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    rec = payload["recommendation"]
    lines = [
        "# Next Deployable Policy Branch Decision",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline decision artifact. It does not train, run simulation, SSH, deploy, run robot tests, or change runtime behavior.",
        "",
        "## Executive Summary",
        "",
        rec["recommended_next"],
        "",
        "The cheap post-hoc branches are now closed negative. The remaining blocker is the deployable policy's representation/training of the right-knee contact transition, not one missing scalar cap.",
        "",
        "## Candidate Gate Comparison",
        "",
        "| candidate | status | runs | complete | falls/terms | vx mean | track ratio | vel p95 range | tracking p95 range |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in payload["candidates"]:
        lines.append(
            "| {name} | `{status}` | {runs} | {complete} | {falls} | {vx} | {ratio} | {vel_min}-{vel_max} | {trk_min}-{trk_max} |".format(
                name=row["name"],
                status=row["status"],
                runs=row["runs"],
                complete=row["duration_complete"],
                falls=row["falls_or_terminations"],
                vx=fmt(row["vx_mean"]),
                ratio=fmt(row["track_ratio_mean"]),
                vel_min=fmt(row["max_pitch_velocity_p95_min"]),
                vel_max=fmt(row["max_pitch_velocity_p95_max"]),
                trk_min=fmt(row["max_tracking_p95_min"]),
                trk_max=fmt(row["max_tracking_p95_max"]),
            )
        )
    lines.extend(
        [
            "",
            "## PPO / Blend Sweep Evidence",
            "",
            "| sweep | best policy | status | track ratio | max tracking p95 | max velocity p95 | failure reasons |",
            "|---|---|---|---:|---:|---:|---|",
        ]
    )
    for row in payload["sweep_summaries"]:
        lines.append(
            "| {name} | `{policy}` | `{status}` | {ratio} | {tracking} | {velocity} | `{reasons}` |".format(
                name=row["name"],
                policy=row.get("policy"),
                status=row.get("status"),
                ratio=fmt(row.get("positive_command_tracking_ratio_mean")),
                tracking=fmt(row.get("max_pitch_tracking_p95_rad")),
                velocity=fmt(row.get("max_pitch_sent_target_velocity_p95_rad_s")),
                reasons=row.get("failure_reasons"),
            )
        )
    spike = payload["right_knee_spike_evidence"]
    lines.extend(
        [
            "",
            "## Right-Knee Transition Evidence",
            "",
            "```text",
            f"right-knee action-derived velocity > 3.75 rad/s: {spike['right_knee_action_spikes_gt_3p75']} / {spike['right_knee_action_samples']}",
            f"within 2 ticks of contact transition: {spike['within_2_ticks_of_contact_transition']} / {spike['right_knee_action_spikes_gt_3p75']}",
            "```",
            "",
            "## Closed Branches",
            "",
        ]
    )
    for item in payload["branch_closures"]:
        lines.append(f"- `{item['branch']}`: {item['reason']}")
    lines.extend(
        [
            "",
            "## Recommended Next Branch",
            "",
            f"`{rec['status']}`",
            "",
            "Minimum requirements:",
            "",
        ]
    )
    for item in rec["minimum_requirements"]:
        lines.append(f"- {item}")
    lines.extend(["", "Candidate mechanisms:", ""])
    for item in rec["candidate_mechanisms"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Stop Rules",
            "",
            "- Do not run robot validation from any candidate in this table.",
            "- Do not launch another clipping, deletion, or scalar weight-blend branch unless a new diagnostic identifies a different failure mechanism.",
            "- Do not count a run as improvement if it lowers falls by freezing or reducing forward progress.",
            "- Do not relax the fitted actuator envelope to make the candidate pass.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    payload = build_payload(args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={payload['status']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
