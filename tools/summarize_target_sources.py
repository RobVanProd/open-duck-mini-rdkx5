#!/usr/bin/env python3
"""Summarize low-command target-source evidence.

This is an offline analysis tool. It consumes compact JSON artifacts produced
by the target primitive, reference rollout, curation, and objective-scoring
tools. It does not run simulation, train, deploy, SSH, or touch the robot.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "TARGET_SOURCE_AUDIT.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "target_source_audit.json"


@dataclass(frozen=True)
class SourceSpec:
    name: str
    kind: str
    objective_json: str | None = None
    curation_json: str | None = None
    rollout_json: str | None = None
    contact_json: str | None = None


DEFAULT_SOURCES = [
    SourceSpec(
        name="contact_break",
        kind="primitive",
        objective_json="outputs/analysis/target_objective_score_contact_break_50.json",
        curation_json="outputs/analysis/target_generator_contact_break_window_curation_50.json",
    ),
    SourceSpec(
        name="lift_pulse",
        kind="primitive",
        objective_json="outputs/analysis/target_objective_score_lift_pulse_50.json",
        curation_json="outputs/analysis/target_generator_lift_pulse_window_curation_50.json",
    ),
    SourceSpec(
        name="foot_clearance_probe",
        kind="primitive",
        objective_json="outputs/analysis/target_objective_score_foot_clearance_probe_50.json",
        curation_json="outputs/analysis/target_generator_foot_clearance_probe_window_curation_50.json",
    ),
    SourceSpec(
        name="dynamic_roll",
        kind="primitive",
        objective_json="outputs/analysis/target_objective_score_dynamic_roll_50.json",
        curation_json="outputs/analysis/target_generator_dynamic_roll_window_curation_50.json",
    ),
    SourceSpec(
        name="dynamic_roll_refine",
        kind="primitive",
        objective_json="outputs/analysis/target_objective_score_dynamic_roll_refine_50.json",
        curation_json="outputs/analysis/target_generator_dynamic_roll_refine_window_curation_50.json",
    ),
    SourceSpec(
        name="reference_contact_gated_projected",
        kind="reference",
        rollout_json="outputs/analysis/reference_motion_rollout_v20_contact_gated_projected.json",
        curation_json="outputs/analysis/realized_window_contact_gated_reference_curation.json",
    ),
    SourceSpec(
        name="reference_contact_synchronized_projected",
        kind="reference",
        rollout_json="outputs/analysis/reference_motion_rollout_v20_contact_synchronized_projected.json",
        curation_json="outputs/analysis/realized_window_contact_synchronized_reference_curation.json",
        contact_json="outputs/analysis/reference_contact_compatibility_v20_with_contact_adaptations.json",
    ),
]


def load_json(path_text: str | None) -> dict[str, Any] | None:
    if not path_text:
        return None
    path = ROOT / path_text if not Path(path_text).is_absolute() else Path(path_text)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, str):
        return value
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def nested_get(row: dict[str, Any], *keys: str) -> Any:
    current: Any = row
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def best_objective_row(objective: dict[str, Any] | None) -> dict[str, Any] | None:
    if not objective:
        return None
    results = objective.get("results") or []
    return results[0] if results else None


def curation_counts(curation: dict[str, Any] | None) -> dict[str, Any]:
    if not curation:
        return {}
    counts = dict(curation.get("counts") or {})
    diversity = curation.get("diversity") or {}
    if diversity:
        counts["curated_source_files"] = diversity.get("curated_source_files")
        counts["curated_modes"] = diversity.get("curated_modes")
    elif curation.get("curated_seed_windows") is not None:
        sources = {
            str(row.get("source_name"))
            for row in curation.get("curated_seed_windows") or []
            if row.get("source_name")
        }
        modes = {
            str(row.get("mode"))
            for row in curation.get("curated_seed_windows") or []
            if row.get("mode")
        }
        counts["curated_source_files"] = len(sources)
        counts["curated_modes"] = len(modes)
    return counts


def reference_rollout_summary(rollout: dict[str, Any] | None) -> dict[str, Any]:
    if not rollout:
        return {}
    aggregate = rollout.get("aggregate") or {}
    return {
        "rollout_status": rollout.get("status"),
        "falls": aggregate.get("falls"),
        "duration_complete": aggregate.get("duration_complete"),
        "track_ratio_mean": aggregate.get("track_ratio_mean"),
        "vx_mean": aggregate.get("vx_mean"),
        "vy_abs_p95_mean": aggregate.get("vy_abs_p95_mean"),
        "contact_mismatch_pct_mean": aggregate.get("reference_contact_mismatch_pct_mean"),
    }


def contact_compat_summary(contact: dict[str, Any] | None, label_hint: str) -> dict[str, Any]:
    if not contact:
        return {}
    runs = contact.get("runs") or []
    if len(runs) == 1:
        run = runs[0]
    else:
        matches = [run for run in runs if label_hint in str(run.get("label", ""))]
        run = matches[0] if matches else (runs[-1] if runs else {})
    return {
        "reference_contact_mismatch_pct": run.get("mismatch_pct"),
        "actual_11_pct": nested_get(run, "actual_contact_pct", "11"),
        "reference_11_pct": nested_get(run, "reference_contact_pct", "11"),
    }


def source_summary(spec: SourceSpec) -> dict[str, Any]:
    objective = load_json(spec.objective_json)
    curation = load_json(spec.curation_json)
    rollout = load_json(spec.rollout_json)
    contact = load_json(spec.contact_json)
    best = best_objective_row(objective)
    seed2 = (best or {}).get("seeds", {}).get("seed_002", {})
    seed0 = (best or {}).get("seeds", {}).get("seed_000", {})
    counts = curation_counts(curation)
    summary = {
        "name": spec.name,
        "kind": spec.kind,
        "status": (
            (objective or {}).get("status")
            or (rollout or {}).get("status")
            or (curation or {}).get("status")
            or "MISSING"
        ),
        "objective_status": (objective or {}).get("status"),
        "robust_mode_count": (objective or {}).get("robust_mode_count"),
        "mode_count": (objective or {}).get("mode_count"),
        "best_mode": (best or {}).get("mode"),
        "best_pass_seed_count": (best or {}).get("pass_seed_count"),
        "seed0_vx": seed0.get("mean_vx_m_s"),
        "seed0_vy95": seed0.get("vy_abs_p95_m_s"),
        "seed0_contact_dominance": seed0.get("contact_dominance_pct"),
        "seed0_contact_transitions": seed0.get("contact_transitions"),
        "seed0_failures": seed0.get("hard_failures") or [],
        "seed2_vx": seed2.get("mean_vx_m_s"),
        "seed2_vy95": seed2.get("vy_abs_p95_m_s"),
        "seed2_contact_dominance": seed2.get("contact_dominance_pct"),
        "seed2_contact_transitions": seed2.get("contact_transitions"),
        "seed2_foot_z95": seed2.get("foot_site_z_p95_m"),
        "seed2_failures": seed2.get("hard_failures") or [],
        "curation_status": (curation or {}).get("status"),
        "curated_50_windows": counts.get("pass_curated_seed_windows"),
        "review_motion_hints": counts.get("review_motion_hints"),
        "curated_source_files": counts.get("curated_source_files"),
        "curated_modes": counts.get("curated_modes"),
    }
    summary.update(reference_rollout_summary(rollout))
    summary.update(contact_compat_summary(contact, spec.name))
    return summary


def gate_status(summaries: list[dict[str, Any]]) -> str:
    for item in summaries:
        if (
            item.get("robust_mode_count")
            and int(item["robust_mode_count"]) > 0
            and item.get("curated_source_files")
            and int(item["curated_source_files"]) >= 2
        ):
            return "PASS_TARGET_SOURCE_READY"
    return "HOLD_NO_TARGET_SOURCE_READY"


def recommendation(summaries: list[dict[str, Any]]) -> str:
    dynamic_roll = next(
        (item for item in summaries if item.get("name") == "dynamic_roll"),
        None,
    )
    if dynamic_roll and dynamic_roll.get("curation_status") == "PASS_CURATED_DATASET_SEED_READY":
        return (
            "Dynamic hip-roll is the strongest current target-source family: "
            "it produced 50-sample curated windows from seed_000 and seed_002, "
            "but no same-mode robust pass. The next search should stay in the "
            "broad dynamic-roll family and optimize the best near-pass by "
            "reducing seed_000 lateral velocity while preserving seed_002 "
            "forward progress and contact transitions."
        )
    primitive_seed2_failures = [
        reason
        for item in summaries
        if item.get("kind") == "primitive"
        for reason in item.get("seed2_failures", [])
    ]
    if primitive_seed2_failures.count("single_contact_pattern_dominates") >= 2:
        return (
            "Build a contact-state or IK/reference target source. The current "
            "joint-space primitive family repeatedly preserves forward/lateral "
            "metrics but fails seed2 contact alternation."
        )
    return "Continue target-source audit before training."


def audit_sources() -> dict[str, Any]:
    summaries = [source_summary(spec) for spec in DEFAULT_SOURCES]
    return {
        "status": gate_status(summaries),
        "sources": summaries,
        "recommendation": recommendation(summaries),
        "training_permission": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Target Source Audit",
        "",
        f"status: `{payload['status']}`",
        "",
        "This summarizes compact target-source evidence. It does not run",
        "simulation, training, SSH, deployment, or robot tests.",
        "",
        "## Source Summary",
        "",
        "| source | kind | status | robust_modes | curated_50 | sources | seed0_vx | seed0_vy95 | seed2_vx | seed2_vy95 | seed2_contact | seed2_trans | seed2_foot_z95 | rollout_falls | contact_mismatch |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in payload["sources"]:
        lines.append(
            "| {name} | {kind} | `{status}` | {robust} | {curated} | {sources} | {seed0_vx} | {seed0_vy} | {seed2_vx} | {seed2_vy} | {contact} | {trans} | {foot_z} | {falls} | {mismatch} |".format(
                name=item["name"],
                kind=item["kind"],
                status=item["status"],
                robust=fmt(item.get("robust_mode_count"), 0),
                curated=fmt(item.get("curated_50_windows"), 0),
                sources=fmt(item.get("curated_source_files"), 0),
                seed0_vx=fmt(item.get("seed0_vx")),
                seed0_vy=fmt(item.get("seed0_vy95")),
                seed2_vx=fmt(item.get("seed2_vx")),
                seed2_vy=fmt(item.get("seed2_vy95")),
                contact=fmt(item.get("seed2_contact_dominance")),
                trans=fmt(item.get("seed2_contact_transitions"), 0),
                foot_z=fmt(item.get("seed2_foot_z95")),
                falls=fmt(item.get("falls"), 0),
                mismatch=fmt(
                    item.get("reference_contact_mismatch_pct")
                    or item.get("contact_mismatch_pct_mean")
                ),
            )
        )
    lines.extend(
        [
            "",
            "## Seed 2 Failures",
            "",
            "| source | seed0_failures | seed2_failures |",
            "|---|---|---|",
        ]
    )
    for item in payload["sources"]:
        seed0_failures = ", ".join(item.get("seed0_failures") or [])
        seed2_failures = ", ".join(item.get("seed2_failures") or [])
        lines.append(
            f"| {item['name']} | `{seed0_failures or 'NA'}` | `{seed2_failures or 'NA'}` |"
        )
    lines.extend(
        [
            "",
            "## Recommendation",
            "",
            payload["recommendation"],
            "",
            "## Gate",
            "",
            "- Training remains blocked until a target source has robust 50-sample windows across seed_000 and seed_002.",
            "- A source with only seed_000 curated windows is evidence, not permission to train.",
            "- A source-diverse dataset without a same-mode robust pass is evidence, not permission to train, unless that gate is explicitly relaxed in a reviewed experiment.",
            "- A reference rollout with low contact mismatch but falls/negative progress is not a BC target.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()
    payload = audit_sources()
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={payload['status']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
