#!/usr/bin/env python3
"""Audit target-window curation results for cross-seed robustness.

This is an offline analysis tool. It consumes compact curation JSON files,
groups windows by primitive/mode and source seed, and reports whether any mode
passes curation across multiple seeds. It does not run simulation or training.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUTS = [
    ROOT / "outputs" / "analysis" / "target_generator_lateral_contact_window_curation_50.json",
    ROOT / "outputs" / "analysis" / "target_generator_seed2_balance_window_curation_50.json",
]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "TARGET_SEED_ROBUSTNESS_AUDIT.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "target_seed_robustness_audit.json"
TIER_RANK = {
    "PASS_CURATED_SEED_WINDOW": 3,
    "REVIEW_MOTION_HINT_ONLY": 2,
    "REJECT_DATASET_SEED": 1,
}


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def source_seed(source_name: str) -> str:
    name = Path(source_name).stem
    if name.startswith("seed_"):
        return name
    return source_name


def all_windows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for key in ("curated_seed_windows", "review_motion_hints", "rejected_dataset_seeds"):
        for window in payload.get(key, []):
            row = dict(window)
            row["_tier_list"] = key
            rows.append(row)
    return rows


def best_window(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None

    def key(row: dict[str, Any]) -> tuple[float, float, float, float]:
        return (
            TIER_RANK.get(str(row.get("tier")), 0),
            -len(row.get("reasons") or []),
            float(row.get("mean_vx_m_s") or -999.0),
            -float(row.get("vy_abs_p95_m_s") or 999.0),
        )

    return max(rows, key=key)


def compact(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "tier": row.get("tier"),
        "reasons": row.get("reasons") or [],
        "source_name": row.get("source_name"),
        "seed": source_seed(str(row.get("source_name"))),
        "mode": row.get("mode"),
        "start_tick": row.get("start_tick"),
        "end_tick": row.get("end_tick"),
        "mean_vx_m_s": row.get("mean_vx_m_s"),
        "vy_abs_p95_m_s": row.get("vy_abs_p95_m_s"),
        "body_pitch_abs_p95_rad": row.get("body_pitch_abs_p95_rad"),
        "base_height_min_m": row.get("base_height_min_m"),
        "sent_target_velocity_p95_rad_s": row.get("sent_target_velocity_p95_rad_s"),
        "joint_tracking_p95_rad": row.get("joint_tracking_p95_rad"),
        "contact_dominance_pct": row.get("contact_dominance_pct"),
    }


def audit_file(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    by_mode_seed: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    reason_counts = Counter()
    seed2_reason_counts = Counter()
    rows = all_windows(payload)
    for row in rows:
        mode = str(row.get("mode"))
        seed = source_seed(str(row.get("source_name")))
        by_mode_seed[(mode, seed)].append(row)
        for reason in row.get("reasons") or []:
            reason_counts[str(reason)] += 1
            if seed == "seed_002":
                seed2_reason_counts[str(reason)] += 1

    modes = sorted({mode for mode, _seed in by_mode_seed})
    mode_rows = []
    robust_modes = []
    near_misses = []
    for mode in modes:
        seed_rows = {
            seed: compact(best_window(by_mode_seed.get((mode, seed), [])))
            for seed in sorted({seed for item_mode, seed in by_mode_seed if item_mode == mode})
        }
        curated_seeds = [
            seed
            for seed, row in seed_rows.items()
            if row and row.get("tier") == "PASS_CURATED_SEED_WINDOW"
        ]
        seed0 = seed_rows.get("seed_000")
        seed2 = seed_rows.get("seed_002")
        item = {
            "mode": mode,
            "seeds": seed_rows,
            "curated_seeds": curated_seeds,
            "curated_seed_count": len(curated_seeds),
        }
        mode_rows.append(item)
        if len(curated_seeds) >= 2:
            robust_modes.append(item)
        elif (
            seed0
            and seed0.get("tier") == "PASS_CURATED_SEED_WINDOW"
            and seed2
            and seed2.get("tier") == "REVIEW_MOTION_HINT_ONLY"
        ):
            near_misses.append(item)

    near_misses.sort(
        key=lambda item: (
            -float((item["seeds"].get("seed_002") or {}).get("mean_vx_m_s") or -999.0),
            len((item["seeds"].get("seed_002") or {}).get("reasons") or []),
        )
    )
    status = (
        "PASS_SEED_ROBUST_TARGETS"
        if robust_modes
        else "HOLD_SEED2_LATERAL_CONTACT"
        if seed2_reason_counts
        else "HOLD_NO_SEED_ROBUST_TARGETS"
    )
    return {
        "input_json": str(path),
        "source_status": payload.get("status"),
        "status": status,
        "counts": {
            "windows": len(rows),
            "modes": len(modes),
            "robust_modes": len(robust_modes),
            "seed0_curated_seed2_review_near_misses": len(near_misses),
        },
        "reason_counts": dict(reason_counts),
        "seed2_reason_counts": dict(seed2_reason_counts),
        "robust_modes": robust_modes,
        "seed2_near_misses": near_misses[:20],
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Target Seed Robustness Audit",
        "",
        f"status: `{payload['status']}`",
        "",
        "This audits compact target-window curation outputs for modes that pass",
        "across multiple source seeds. It does not run simulation or training.",
        "",
        "## Inputs",
        "",
        "| input | source_status | status | modes | robust_modes | seed0_curated_seed2_review |",
        "|---|---|---|---:|---:|---:|",
    ]
    for result in payload["results"]:
        lines.append(
            "| {input} | `{source_status}` | `{status}` | {modes} | {robust} | {near} |".format(
                input=Path(result["input_json"]).name,
                source_status=result["source_status"],
                status=result["status"],
                modes=result["counts"]["modes"],
                robust=result["counts"]["robust_modes"],
                near=result["counts"]["seed0_curated_seed2_review_near_misses"],
            )
        )
    lines.extend(["", "## Seed 2 Reason Counts", ""])
    total_reasons = Counter()
    for result in payload["results"]:
        total_reasons.update(result.get("seed2_reason_counts", {}))
    if total_reasons:
        for reason, count in total_reasons.most_common():
            lines.append(f"- `{reason}`: `{count}`")
    else:
        lines.append("- `none`")

    lines.extend(
        [
            "",
            "## Top Seed 2 Near Misses",
            "",
            "| input | mode | seed0_vx | seed2_vx | seed2_vy95 | seed2_contact_max | seed2_reasons |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )
    any_near = False
    for result in payload["results"]:
        for item in result["seed2_near_misses"][:10]:
            any_near = True
            seed0 = item["seeds"].get("seed_000") or {}
            seed2 = item["seeds"].get("seed_002") or {}
            lines.append(
                "| {input} | `{mode}` | {seed0_vx} | {seed2_vx} | {seed2_vy} | {seed2_contact} | `{reasons}` |".format(
                    input=Path(result["input_json"]).name,
                    mode=item["mode"],
                    seed0_vx=fmt(seed0.get("mean_vx_m_s")),
                    seed2_vx=fmt(seed2.get("mean_vx_m_s")),
                    seed2_vy=fmt(seed2.get("vy_abs_p95_m_s")),
                    seed2_contact=fmt(seed2.get("contact_dominance_pct")),
                    reasons=", ".join(seed2.get("reasons") or []),
                )
            )
    if not any_near:
        lines.append("| NA | NA | NA | NA | NA | NA | NA |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `PASS_SEED_ROBUST_TARGETS` requires at least one mode curated on multiple seeds.",
            "- Current holds mean the primitive family can generate motion, but not robustly across reset seeds.",
            "- Do not train from single-source curated windows as if they were a general target dataset.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-json",
        action="append",
        default=[],
        help="Curation JSON to audit. Repeat for multiple files.",
    )
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    input_paths = [Path(item) for item in args.input_json] or list(DEFAULT_INPUTS)
    results = [audit_file(path) for path in input_paths]
    status = (
        "PASS_SEED_ROBUST_TARGETS"
        if any(result["status"] == "PASS_SEED_ROBUST_TARGETS" for result in results)
        else "HOLD_SEED2_LATERAL_CONTACT"
        if any(result["status"] == "HOLD_SEED2_LATERAL_CONTACT" for result in results)
        else "HOLD_NO_SEED_ROBUST_TARGETS"
    )
    payload = {"status": status, "results": results}
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={status}")
    for result in results:
        print(
            f"{Path(result['input_json']).name}: robust_modes={result['counts']['robust_modes']} "
            f"near_misses={result['counts']['seed0_curated_seed2_review_near_misses']}"
        )
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
