#!/usr/bin/env python3
"""Curate mined realized-motion windows into dataset-readiness tiers.

This tool consumes the compact manifest from mine_realized_target_windows.py and
applies stricter filters for supervised seed-material readiness. It intentionally
does not slice or export raw traces.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "outputs" / "analysis" / "realized_target_window_mine.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "REALIZED_TARGET_WINDOW_CURATION.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "realized_target_window_curation.json"


def value(window: dict[str, Any], key: str, default: float) -> float:
    item = window.get(key)
    if item is None:
        return default
    return float(item)


def contact_dominance(window: dict[str, Any]) -> float:
    contacts = window.get("contact_pct") or {}
    if not contacts:
        return 0.0
    return max(float(item) for item in contacts.values())


def classify(window: dict[str, Any], args: argparse.Namespace) -> tuple[str, list[str]]:
    reasons = []
    if value(window, "mean_vx_m_s", -1.0) < args.min_mean_vx:
        reasons.append("low_forward_velocity")
    if value(window, "vy_abs_p95_m_s", 999.0) > args.max_vy_abs_p95:
        reasons.append("high_lateral_velocity")
    if value(window, "body_pitch_abs_p95_rad", 999.0) > args.max_pitch_abs_p95:
        reasons.append("high_body_pitch")
    if value(window, "base_height_min_m", -1.0) < args.min_base_height:
        reasons.append("low_base_height")
    if value(window, "action_saturation_pct", 0.0) > args.max_action_saturation_pct:
        reasons.append("action_saturation")
    if value(window, "sent_target_velocity_p95_rad_s", 999.0) > args.max_sent_velocity_p95:
        reasons.append("high_sent_target_velocity")
    if value(window, "joint_tracking_p95_rad", 999.0) > args.max_tracking_p95:
        reasons.append("high_tracking_error")
    margin = window.get("ticks_until_done_after_window")
    if margin is not None and int(margin) < args.min_done_margin:
        reasons.append("short_done_margin")
    if contact_dominance(window) > args.max_contact_dominance_pct:
        reasons.append("single_contact_pattern_dominates")

    if not reasons:
        return "PASS_CURATED_SEED_WINDOW", reasons

    hard_reasons = {
        "low_forward_velocity",
        "low_base_height",
        "action_saturation",
        "high_sent_target_velocity",
        "high_tracking_error",
    }
    if any(reason in hard_reasons for reason in reasons):
        return "REJECT_DATASET_SEED", reasons
    return "REVIEW_MOTION_HINT_ONLY", reasons


def fmt(item: Any, digits: int = 4) -> str:
    if item is None:
        return "NA"
    return f"{float(item):.{digits}f}"


def compact_window(window: dict[str, Any], tier: str, reasons: list[str]) -> dict[str, Any]:
    source_name = Path(str(window.get("source_path"))).name
    return {
        "tier": tier,
        "reasons": reasons,
        "source_path": window.get("source_path"),
        "source_name": source_name,
        "mode": window.get("mode"),
        "start_tick": window.get("start_tick"),
        "end_tick": window.get("end_tick"),
        "mean_vx_m_s": window.get("mean_vx_m_s"),
        "vy_abs_p95_m_s": window.get("vy_abs_p95_m_s"),
        "body_pitch_abs_p95_rad": window.get("body_pitch_abs_p95_rad"),
        "base_height_min_m": window.get("base_height_min_m"),
        "action_saturation_pct": window.get("action_saturation_pct"),
        "sent_target_velocity_p95_rad_s": window.get("sent_target_velocity_p95_rad_s"),
        "joint_tracking_p95_rad": window.get("joint_tracking_p95_rad"),
        "ticks_until_done_after_window": window.get("ticks_until_done_after_window"),
        "contact_pct": window.get("contact_pct"),
        "contact_dominance_pct": contact_dominance(window),
    }


def manifest_windows(source: dict[str, Any]) -> list[dict[str, Any]]:
    windows = []
    seen = set()
    for trace in source.get("traces", []):
        for window in trace.get("candidate_windows", []):
            key = (
                window.get("source_path"),
                window.get("mode"),
                window.get("start_tick"),
                window.get("end_tick"),
            )
            if key in seen:
                continue
            seen.add(key)
            windows.append(window)
    if windows:
        return windows
    return list(source.get("top_windows", []))


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    counts = payload["counts"]
    diversity = payload["diversity"]
    lines = [
        "# Realized Target Window Curation",
        "",
        f"status: `{payload['status']}`",
        "",
        "This applies stricter dataset-readiness filters to the mined realized",
        "motion windows. It does not export raw traces or start training.",
        "",
        "## Criteria",
        "",
    ]
    for key, item in payload["criteria"].items():
        lines.append(f"- {key}: `{item}`")
    lines.extend(
        [
            "",
            "## Counts",
            "",
            f"- mined_windows: `{counts['mined_windows']}`",
            f"- pass_curated_seed_windows: `{counts['pass_curated_seed_windows']}`",
            f"- review_motion_hints: `{counts['review_motion_hints']}`",
            f"- rejected_dataset_seeds: `{counts['rejected_dataset_seeds']}`",
            f"- curated_source_files: `{diversity['curated_source_files']}`",
            f"- curated_modes: `{diversity['curated_modes']}`",
            f"- curated_source_mode_pairs: `{diversity['curated_source_mode_pairs']}`",
            "",
            "## Curated Seed Windows",
            "",
            "| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    curated = payload["curated_seed_windows"]
    if not curated:
        lines.append("| NA | NA | NA | NA | NA | NA | NA | NA | NA | NA | NA |")
    for window in curated:
        lines.append(
            "| {source} | `{mode}` | {ticks} | {vx} | {vy} | {pitch} | {height} | {vel} | {track} | {margin} | {contact} |".format(
                source=Path(str(window["source_path"])).name,
                mode=window["mode"],
                ticks=f"{window['start_tick']}-{window['end_tick']}",
                vx=fmt(window["mean_vx_m_s"]),
                vy=fmt(window["vy_abs_p95_m_s"]),
                pitch=fmt(window["body_pitch_abs_p95_rad"]),
                height=fmt(window["base_height_min_m"]),
                vel=fmt(window["sent_target_velocity_p95_rad_s"]),
                track=fmt(window["joint_tracking_p95_rad"]),
                margin=window["ticks_until_done_after_window"],
                contact=fmt(window["contact_dominance_pct"]),
            )
        )
    lines.extend(
        [
            "",
            "## Top Review-Only Motion Hints",
            "",
            "| source | mode | ticks | vx | reasons |",
            "|---|---|---|---:|---|",
        ]
    )
    review = payload["review_motion_hints"][:15]
    if not review:
        lines.append("| NA | NA | NA | NA | NA |")
    for window in review:
        lines.append(
            "| {source} | `{mode}` | {ticks} | {vx} | `{reasons}` |".format(
                source=Path(str(window["source_path"])).name,
                mode=window["mode"],
                ticks=f"{window['start_tick']}-{window['end_tick']}",
                vx=fmt(window["mean_vx_m_s"]),
                reasons=", ".join(window["reasons"]),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.",
            "- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.",
            "- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", default=str(DEFAULT_INPUT))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--min-curated-windows", type=int, default=8)
    parser.add_argument("--min-mean-vx", type=float, default=0.04)
    parser.add_argument("--max-vy-abs-p95", type=float, default=0.12)
    parser.add_argument("--max-pitch-abs-p95", type=float, default=0.35)
    parser.add_argument("--min-base-height", type=float, default=0.145)
    parser.add_argument("--max-action-saturation-pct", type=float, default=1.0)
    parser.add_argument("--max-sent-velocity-p95", type=float, default=2.5)
    parser.add_argument("--max-tracking-p95", type=float, default=0.12)
    parser.add_argument("--min-done-margin", type=int, default=50)
    parser.add_argument("--max-contact-dominance-pct", type=float, default=95.0)
    parser.add_argument("--min-source-files", type=int, default=2)
    parser.add_argument("--min-source-mode-pairs", type=int, default=2)
    args = parser.parse_args()

    source = json.loads(Path(args.input_json).read_text())
    windows = manifest_windows(source)
    classified = [compact_window(window, *classify(window, args)) for window in windows]
    curated = [window for window in classified if window["tier"] == "PASS_CURATED_SEED_WINDOW"]
    review = [window for window in classified if window["tier"] == "REVIEW_MOTION_HINT_ONLY"]
    rejected = [window for window in classified if window["tier"] == "REJECT_DATASET_SEED"]
    source_files = {window["source_name"] for window in curated}
    modes = {str(window["mode"]) for window in curated}
    source_mode_pairs = {
        (window["source_name"], str(window["mode"])) for window in curated
    }

    if len(curated) < args.min_curated_windows:
        status = "HOLD_INSUFFICIENT_CURATED_WINDOWS"
    elif len(source_files) < args.min_source_files:
        status = "HOLD_INSUFFICIENT_CURATED_DIVERSITY"
    elif len(source_mode_pairs) < args.min_source_mode_pairs:
        status = "HOLD_INSUFFICIENT_CURATED_DIVERSITY"
    else:
        status = "PASS_CURATED_DATASET_SEED_READY"
    payload = {
        "status": status,
        "criteria": {
            "min_curated_windows": args.min_curated_windows,
            "min_mean_vx": args.min_mean_vx,
            "max_vy_abs_p95": args.max_vy_abs_p95,
            "max_pitch_abs_p95": args.max_pitch_abs_p95,
            "min_base_height": args.min_base_height,
            "max_action_saturation_pct": args.max_action_saturation_pct,
            "max_sent_velocity_p95": args.max_sent_velocity_p95,
            "max_tracking_p95": args.max_tracking_p95,
            "min_done_margin": args.min_done_margin,
            "max_contact_dominance_pct": args.max_contact_dominance_pct,
            "min_source_files": args.min_source_files,
            "min_source_mode_pairs": args.min_source_mode_pairs,
        },
        "input_json": str(Path(args.input_json)),
        "counts": {
            "mined_windows": len(windows),
            "pass_curated_seed_windows": len(curated),
            "review_motion_hints": len(review),
            "rejected_dataset_seeds": len(rejected),
        },
        "diversity": {
            "curated_source_files": len(source_files),
            "curated_source_file_names": sorted(source_files),
            "curated_modes": len(modes),
            "curated_source_mode_pairs": len(source_mode_pairs),
        },
        "curated_seed_windows": curated,
        "review_motion_hints": review,
        "rejected_dataset_seeds": rejected,
    }

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={status}")
    print(f"curated_seed_windows={len(curated)}")
    print(f"review_motion_hints={len(review)}")
    print(f"rejected_dataset_seeds={len(rejected)}")
    print(f"curated_source_files={len(source_files)}")
    print(f"curated_source_mode_pairs={len(source_mode_pairs)}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
