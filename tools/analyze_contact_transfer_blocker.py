#!/usr/bin/env python3
"""Audit whether the current target source actually demands weight transfer.

This is an offline analysis helper. It reads compact curation/contact summary
JSON files only; it does not run simulation, train, deploy, SSH, or touch the
robot.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CURATIONS = [
    ROOT
    / "outputs"
    / "analysis"
    / "target_generator_dynamic_roll_lateral_fix_robust_modes_curation_50.json",
    ROOT / "outputs" / "analysis" / "target_generator_dynamic_roll_lateral_fix_window_curation_100.json",
    ROOT / "outputs" / "analysis" / "target_generator_dynamic_roll_lateral_fix_window_curation_150.json",
]
DEFAULT_REFERENCE_CONTACT = (
    ROOT / "outputs" / "analysis" / "reference_contact_compatibility_v20.json"
)
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "CONTACT_TRANSFER_BLOCKER_AUDIT.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "contact_transfer_blocker_audit.json"


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and np.isfinite(float(value))


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def stats(values: list[Any]) -> dict[str, float | None]:
    data = [float(value) for value in values if finite(value)]
    if not data:
        return {"min": None, "mean": None, "p50": None, "p95": None, "max": None}
    return {
        "min": float(np.min(data)),
        "mean": float(np.mean(data)),
        "p50": float(np.percentile(data, 50)),
        "p95": float(np.percentile(data, 95)),
        "max": float(np.max(data)),
    }


def pct_contact(row: dict[str, Any], key: str) -> float:
    contact = row.get("contact_pct") or {}
    return float(contact.get(key, 0.0) or 0.0)


def source_seed(name: str) -> str:
    stem = Path(name).stem
    return stem if stem else name


def rows_from_curation(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in ("curated_seed_windows", "review_motion_hints", "rejected_dataset_seeds"):
        for row in payload.get(key, []) or []:
            item = dict(row)
            item["_tier_list"] = key
            rows.append(item)
    return rows


def summarize_curation(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    rows = rows_from_curation(payload)
    curated = [row for row in payload.get("curated_seed_windows", []) or []]
    rejected = [row for row in payload.get("rejected_dataset_seeds", []) or []]
    review = [row for row in payload.get("review_motion_hints", []) or []]

    def compact(row: dict[str, Any]) -> dict[str, Any]:
        single = pct_contact(row, "10") + pct_contact(row, "01")
        each = min(pct_contact(row, "10"), pct_contact(row, "01"))
        return {
            "tier": row.get("tier"),
            "source_name": row.get("source_name"),
            "seed": source_seed(str(row.get("source_name"))),
            "mode": row.get("mode"),
            "ticks": [row.get("start_tick"), row.get("end_tick")],
            "mean_vx_m_s": row.get("mean_vx_m_s"),
            "double_support_pct": pct_contact(row, "11"),
            "single_support_pct": single,
            "min_each_single_support_pct": each,
            "contact_transitions": row.get("contact_transitions"),
            "sent_target_velocity_p95_rad_s": row.get("sent_target_velocity_p95_rad_s"),
            "body_pitch_abs_p95_rad": row.get("body_pitch_abs_p95_rad"),
            "base_height_min_m": row.get("base_height_min_m"),
            "reasons": row.get("reasons") or [],
        }

    curated_compact = [compact(row) for row in curated]
    rows_compact = [compact(row) for row in rows]
    pass_weight_transfer = [
        row
        for row in curated_compact
        if float(row["double_support_pct"]) <= args.max_double_support_pct
        and float(row["single_support_pct"]) >= args.min_single_support_pct
        and float(row["min_each_single_support_pct"]) >= args.min_each_single_support_pct
    ]
    best_by_weight_transfer = sorted(
        rows_compact,
        key=lambda row: (
            float(row["single_support_pct"]),
            -float(row["double_support_pct"]),
            float(row.get("mean_vx_m_s") or -999.0),
        ),
        reverse=True,
    )[:5]
    return {
        "path": str(path),
        "name": path.name,
        "source_status": payload.get("status"),
        "criteria": payload.get("criteria"),
        "counts": {
            "rows": len(rows),
            "curated": len(curated),
            "review": len(review),
            "rejected": len(rejected),
            "curated_weight_transfer_pass": len(pass_weight_transfer),
        },
        "curated_stats": {
            "mean_vx_m_s": stats([row.get("mean_vx_m_s") for row in curated]),
            "double_support_pct": stats([row["double_support_pct"] for row in curated_compact]),
            "single_support_pct": stats([row["single_support_pct"] for row in curated_compact]),
            "min_each_single_support_pct": stats(
                [row["min_each_single_support_pct"] for row in curated_compact]
            ),
            "sent_target_velocity_p95_rad_s": stats(
                [row.get("sent_target_velocity_p95_rad_s") for row in curated]
            ),
        },
        "best_weight_transfer_rows": best_by_weight_transfer,
    }


def summarize_reference_contact(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    payload = json.loads(path.read_text())
    runs = []
    for run in payload.get("runs", []) or []:
        actual = run.get("actual_contact_pct") or {}
        reference = run.get("reference_contact_pct") or {}
        runs.append(
            {
                "label": run.get("label"),
                "samples": run.get("samples"),
                "mismatch_pct": run.get("mismatch_pct"),
                "actual_double_support_pct": actual.get("11", 0.0),
                "reference_double_support_pct": reference.get("11", 0.0),
                "actual_single_support_pct": float(actual.get("10", 0.0) or 0.0)
                + float(actual.get("01", 0.0) or 0.0),
                "reference_single_support_pct": float(reference.get("10", 0.0) or 0.0)
                + float(reference.get("01", 0.0) or 0.0),
                "dominant_mismatch_pairs": sorted(
                    [
                        {"pair": pair, "pct": pct}
                        for pair, pct in (run.get("pair_pct") or {}).items()
                        if pair.split("->")[0] != pair.split("->")[1]
                    ],
                    key=lambda item: float(item["pct"]),
                    reverse=True,
                )[:3],
            }
        )
    return {"path": str(path), "runs": runs}


def gate(payload: dict[str, Any], args: argparse.Namespace) -> str:
    curated_runs = [run for run in payload["curations"] if run["counts"]["curated"] > 0]
    any_weight_transfer_target = any(
        run["counts"]["curated_weight_transfer_pass"] > 0 for run in curated_runs
    )
    any_long_curated = any(
        run["counts"]["curated"] > 0 and ("100" in run["name"] or "150" in run["name"])
        for run in curated_runs
    )
    reference = payload.get("reference_contact")
    high_reference_mismatch = False
    if reference:
        high_reference_mismatch = any(
            float(run.get("mismatch_pct") or 0.0) >= args.max_reference_mismatch_pct
            for run in reference.get("runs", [])
        )
    if not any_weight_transfer_target:
        return "HOLD_TARGET_SOURCE_DOUBLE_SUPPORT"
    if not any_long_curated:
        return "HOLD_TARGET_SOURCE_TOO_SHORT"
    if high_reference_mismatch:
        return "HOLD_POLICY_CONTACT_EXECUTION"
    return "PASS_CONTACT_TRANSFER_SOURCE_READY"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Contact Transfer Blocker Audit",
        "",
        f"status: `{payload['status']}`",
        "",
        "This offline audit separates two different failure explanations:",
        "",
        "1. the target/demo source itself mostly stays in double support, or",
        "2. the target/demo source asks for single support but closed-loop execution cannot realize it.",
        "",
        "No simulation, training, robot SSH, deployment, or hardware motion was run.",
        "",
        "## Target Fragment Sources",
        "",
        "| source | status | curated | wt-pass | double support mean/p95 | single support mean/p95 | min side mean | sent vel p95 mean |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for run in payload["curations"]:
        stats_payload = run["curated_stats"]
        lines.append(
            "| {name} | `{status}` | {curated} | {wt_pass} | {ds_mean}/{ds_p95} | {ss_mean}/{ss_p95} | {side_mean} | {vel_mean} |".format(
                name=run["name"],
                status=run["source_status"],
                curated=run["counts"]["curated"],
                wt_pass=run["counts"]["curated_weight_transfer_pass"],
                ds_mean=fmt(stats_payload["double_support_pct"]["mean"], 2),
                ds_p95=fmt(stats_payload["double_support_pct"]["p95"], 2),
                ss_mean=fmt(stats_payload["single_support_pct"]["mean"], 2),
                ss_p95=fmt(stats_payload["single_support_pct"]["p95"], 2),
                side_mean=fmt(stats_payload["min_each_single_support_pct"]["mean"], 2),
                vel_mean=fmt(stats_payload["sent_target_velocity_p95_rad_s"]["mean"], 4),
            )
        )
    lines.extend(
        [
            "",
            "Weight-transfer target criteria used by this audit:",
            "",
            f"- double_support_pct <= `{payload['thresholds']['max_double_support_pct']}`",
            f"- single_support_pct >= `{payload['thresholds']['min_single_support_pct']}`",
            f"- min_each_single_support_pct >= `{payload['thresholds']['min_each_single_support_pct']}`",
            "",
            "## Best Available Weight-Transfer Rows",
            "",
            "| source | tier | seed | ticks | vx | double | single | min side | reasons |",
            "|---|---|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for run in payload["curations"]:
        for row in run["best_weight_transfer_rows"][:3]:
            lines.append(
                "| {source} | `{tier}` | `{seed}` | `{ticks}` | {vx} | {double} | {single} | {side} | `{reasons}` |".format(
                    source=run["name"],
                    tier=row.get("tier"),
                    seed=row.get("seed"),
                    ticks=f"{row.get('ticks', [None, None])[0]}-{row.get('ticks', [None, None])[1]}",
                    vx=fmt(row.get("mean_vx_m_s")),
                    double=fmt(row.get("double_support_pct"), 2),
                    single=fmt(row.get("single_support_pct"), 2),
                    side=fmt(row.get("min_each_single_support_pct"), 2),
                    reasons=", ".join(row.get("reasons") or []),
                )
            )
    reference = payload.get("reference_contact")
    if reference:
        lines.extend(
            [
                "",
                "## Reference Rollout Contact Mismatch",
                "",
                "| run | samples | mismatch | actual double | reference double | actual single | reference single | top mismatch |",
                "|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for run in reference["runs"]:
            top = run["dominant_mismatch_pairs"][0] if run["dominant_mismatch_pairs"] else {}
            lines.append(
                "| {label} | {samples} | {mismatch} | {actual_double} | {reference_double} | {actual_single} | {reference_single} | `{pair}` {pct} |".format(
                    label=run["label"],
                    samples=run["samples"],
                    mismatch=fmt(run["mismatch_pct"], 2),
                    actual_double=fmt(run["actual_double_support_pct"], 2),
                    reference_double=fmt(run["reference_double_support_pct"], 2),
                    actual_single=fmt(run["actual_single_support_pct"], 2),
                    reference_single=fmt(run["reference_single_support_pct"], 2),
                    pair=top.get("pair", "NA"),
                    pct=fmt(top.get("pct"), 2),
                )
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
        ]
    )
    if payload["status"] == "HOLD_TARGET_SOURCE_DOUBLE_SUPPORT":
        lines.extend(
            [
                "The current curated dynamic-roll/lateral-fix fragments do not clear",
                "the weight-transfer criteria. Their short successful windows mostly",
                "move forward while staying in double support, and longer 100/150 tick",
                "windows have no curated passes.",
                "",
                "Next branch: do not train BC/PPO from these fragments as if they are",
                "stepping demonstrations. Build or optimize a target source that",
                "explicitly produces sustained single-support alternation first.",
            ]
        )
    elif payload["status"] == "HOLD_POLICY_CONTACT_EXECUTION":
        lines.extend(
            [
                "A target source appears to request useful single support, but",
                "closed-loop execution still mismatches contact timing. Next branch:",
                "make contact/weight-shift execution the objective before adding",
                "another joint-target prior.",
            ]
        )
    elif payload["status"] == "HOLD_TARGET_SOURCE_TOO_SHORT":
        lines.extend(
            [
                "A short target source clears contact transfer, but no longer",
                "100-150 tick source does. Extend the target generator before PPO.",
            ]
        )
    else:
        lines.extend(
            [
                "A candidate source clears the contact-transfer checks. It can move",
                "to a reviewed imitation/BC smoke only after the reward preflight also",
                "passes.",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--curation-json",
        action="append",
        default=None,
        help="Compact target curation JSON. May be repeated.",
    )
    parser.add_argument("--reference-contact-json", default=str(DEFAULT_REFERENCE_CONTACT))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--max-double-support-pct", type=float, default=75.0)
    parser.add_argument("--min-single-support-pct", type=float, default=20.0)
    parser.add_argument("--min-each-single-support-pct", type=float, default=5.0)
    parser.add_argument("--max-reference-mismatch-pct", type=float, default=30.0)
    args = parser.parse_args()

    curation_paths = [
        Path(item) if Path(item).is_absolute() else ROOT / item
        for item in (args.curation_json or [str(path) for path in DEFAULT_CURATIONS])
    ]
    curations = []
    for path in curation_paths:
        if not path.exists():
            raise SystemExit(f"Missing curation JSON: {path}")
        curations.append(summarize_curation(path, args))

    reference_path = Path(args.reference_contact_json)
    if not reference_path.is_absolute():
        reference_path = ROOT / reference_path
    reference = summarize_reference_contact(reference_path)
    payload = {
        "thresholds": {
            "max_double_support_pct": args.max_double_support_pct,
            "min_single_support_pct": args.min_single_support_pct,
            "min_each_single_support_pct": args.min_each_single_support_pct,
            "max_reference_mismatch_pct": args.max_reference_mismatch_pct,
        },
        "curations": curations,
        "reference_contact": reference,
    }
    payload["status"] = gate(payload, args)

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
