#!/usr/bin/env python3
"""Summarize what blocks the weight-transfer gate across score artifacts.

This is an offline analysis helper. It reads compact score JSONs and reports
which constraints are currently binding. It does not run simulation, train,
deploy, SSH, or touch the robot.
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from typing import Any

import numpy as np

from check_weight_transfer_target_gate import DEFAULT_PATTERNS, ROOT, artifact_label, resolve


DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "WEIGHT_TRANSFER_GATE_FAILURE_ANALYSIS.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "weight_transfer_gate_failure_analysis.json"


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def expand_default_inputs() -> list[Path]:
    paths: set[Path] = set()
    for pattern in DEFAULT_PATTERNS:
        paths.update(resolve(item) for item in glob.glob(str(resolve(pattern))))
    return sorted(paths)


def seed_rows_from_result(
    artifact: str,
    window_samples: int | None,
    result: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for seed, metrics in (result.get("seeds") or {}).items():
        if not isinstance(metrics, dict):
            continue
        row = {
            "artifact": artifact,
            "mode": result.get("mode"),
            "window_samples": window_samples,
            "seed": str(seed),
            "min_seed_score": result.get("min_seed_score"),
            "mean_seed_score": result.get("mean_seed_score"),
        }
        row.update(metrics)
        rows.append(row)
    return rows


def read_rows(paths: list[Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    artifact_summaries = []
    rows = []
    for path in paths:
        if not path.exists():
            artifact_summaries.append({"path": str(path), "label": artifact_label(path), "status": "MISSING"})
            continue
        payload = json.loads(path.read_text())
        label = artifact_label(path)
        results = payload.get("results") or []
        if not isinstance(results, list):
            results = []
        artifact_summaries.append(
            {
                "path": str(path),
                "label": label,
                "status": payload.get("status", "UNKNOWN"),
                "window_samples": payload.get("window_samples"),
                "mode_count": payload.get("mode_count"),
                "robust_mode_count": payload.get("robust_mode_count"),
                "results": len(results),
            }
        )
        for result in results:
            if isinstance(result, dict):
                rows.extend(seed_rows_from_result(label, payload.get("window_samples"), result))
    return rows, artifact_summaries


def finite_float(value: Any) -> float | None:
    try:
        data = float(value)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(data):
        return None
    return data


def passes(row: dict[str, Any], key: str, threshold: float, op: str) -> bool:
    value = finite_float(row.get(key))
    if value is None:
        return False
    if op == ">=":
        return value >= threshold
    return value <= threshold


def metric_checks(args: argparse.Namespace) -> list[tuple[str, str, float, str]]:
    return [
        ("mean_vx_m_s", "forward_velocity", args.min_mean_vx, ">="),
        ("forward_displacement_m", "forward_displacement", args.min_forward_displacement_m, ">="),
        ("vy_abs_p95_m_s", "lateral_velocity", args.max_vy_abs_p95, "<="),
        ("body_pitch_abs_p95_rad", "body_pitch", args.max_pitch_abs_p95, "<="),
        ("base_height_min_m", "base_height", args.min_base_height, ">="),
        ("double_support_pct", "double_support", args.max_double_support_pct, "<="),
        ("single_support_pct", "single_support", args.min_single_support_pct, ">="),
        ("min_single_support_side_pct", "support_balance", args.min_each_single_support_pct, ">="),
        ("contact_transitions", "contact_transitions", args.min_contact_transitions, ">="),
        ("sent_target_velocity_p95_rad_s", "target_velocity", args.max_sent_velocity_p95, "<="),
        ("joint_tracking_p95_rad", "joint_tracking", args.max_tracking_p95, "<="),
    ]


def row_failures(row: dict[str, Any], args: argparse.Namespace) -> list[str]:
    failures = []
    for key, label, threshold, op in metric_checks(args):
        value = finite_float(row.get(key))
        if value is None:
            failures.append(f"{label}:missing")
        elif op == ">=" and value < threshold:
            failures.append(label)
        elif op == "<=" and value > threshold:
            failures.append(label)
    if row.get("done_inside_window"):
        failures.append("done_inside_window")
    return failures


def pass_count(row: dict[str, Any], args: argparse.Namespace) -> int:
    return sum(
        1
        for key, _label, threshold, op in metric_checks(args)
        if passes(row, key, threshold, op)
    )


def metric_summary(rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    summary = {}
    for key, label, threshold, op in metric_checks(args):
        values = [finite_float(row.get(key)) for row in rows]
        values = [value for value in values if value is not None]
        if values:
            if op == ">=":
                best = max(values)
                worst = min(values)
                best_ratio = best / threshold if abs(threshold) > 1.0e-12 else None
            else:
                best = min(values)
                worst = max(values)
                best_ratio = threshold / best if abs(best) > 1.0e-12 else None
            pass_rows = [
                row
                for row in rows
                if passes(row, key, threshold, op)
            ]
            summary[label] = {
                "key": key,
                "threshold": threshold,
                "op": op,
                "observed": len(values),
                "pass_rows": len(pass_rows),
                "pass_pct": len(pass_rows) / len(rows) * 100.0 if rows else 0.0,
                "best": best,
                "worst": worst,
                "best_ratio": best_ratio,
            }
        else:
            summary[label] = {
                "key": key,
                "threshold": threshold,
                "op": op,
                "observed": 0,
                "pass_rows": 0,
                "pass_pct": 0.0,
                "best": None,
                "worst": None,
                "best_ratio": None,
            }
    return summary


def top_rows(
    rows: list[dict[str, Any]],
    args: argparse.Namespace,
    *,
    key: str,
    reverse: bool,
    limit: int,
    filter_fn=None,
) -> list[dict[str, Any]]:
    filtered = [row for row in rows if finite_float(row.get(key)) is not None]
    if filter_fn is not None:
        filtered = [row for row in filtered if filter_fn(row)]
    filtered.sort(key=lambda row: finite_float(row.get(key)) or 0.0, reverse=reverse)
    return [compact_row(row, args) for row in filtered[:limit]]


def compact_row(row: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    failures = row_failures(row, args)
    return {
        "artifact": row.get("artifact"),
        "mode": row.get("mode"),
        "seed": row.get("seed"),
        "window_samples": row.get("window_samples"),
        "pass_count": pass_count(row, args),
        "failures": failures,
        "mean_vx_m_s": row.get("mean_vx_m_s"),
        "forward_displacement_m": row.get("forward_displacement_m"),
        "vy_abs_p95_m_s": row.get("vy_abs_p95_m_s"),
        "body_pitch_abs_p95_rad": row.get("body_pitch_abs_p95_rad"),
        "base_height_min_m": row.get("base_height_min_m"),
        "double_support_pct": row.get("double_support_pct"),
        "single_support_pct": row.get("single_support_pct"),
        "min_single_support_side_pct": row.get("min_single_support_side_pct"),
        "contact_transitions": row.get("contact_transitions"),
        "sent_target_velocity_p95_rad_s": row.get("sent_target_velocity_p95_rad_s"),
        "joint_tracking_p95_rad": row.get("joint_tracking_p95_rad"),
    }


def classify(rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    stable = [
        row
        for row in rows
        if passes(row, "vy_abs_p95_m_s", args.max_vy_abs_p95, "<=")
        and passes(row, "body_pitch_abs_p95_rad", args.max_pitch_abs_p95, "<=")
        and passes(row, "base_height_min_m", args.min_base_height, ">=")
        and passes(row, "sent_target_velocity_p95_rad_s", args.max_sent_velocity_p95, "<=")
        and passes(row, "joint_tracking_p95_rad", args.max_tracking_p95, "<=")
    ]
    support_ready = [
        row
        for row in rows
        if passes(row, "double_support_pct", args.max_double_support_pct, "<=")
        and passes(row, "single_support_pct", args.min_single_support_pct, ">=")
        and passes(row, "min_single_support_side_pct", args.min_each_single_support_pct, ">=")
        and passes(row, "contact_transitions", args.min_contact_transitions, ">=")
    ]
    forward_ready = [
        row
        for row in rows
        if passes(row, "mean_vx_m_s", args.min_mean_vx, ">=")
        and passes(row, "forward_displacement_m", args.min_forward_displacement_m, ">=")
    ]
    return {
        "rows": len(rows),
        "stable_actuator_rows": len(stable),
        "support_ready_rows": len(support_ready),
        "forward_ready_rows": len(forward_ready),
        "stable_and_support_rows": len([row for row in stable if row in support_ready]),
        "stable_and_forward_rows": len([row for row in stable if row in forward_ready]),
        "support_and_forward_rows": len([row for row in support_ready if row in forward_ready]),
        "all_three_rows": len([row for row in rows if row in stable and row in support_ready and row in forward_ready]),
        "best_forward_among_stable": top_rows(
            stable,
            args,
            key="mean_vx_m_s",
            reverse=True,
            limit=5,
        ),
        "best_support_among_stable": top_rows(
            stable,
            args,
            key="single_support_pct",
            reverse=True,
            limit=5,
        ),
        "best_lateral_among_forwardish": top_rows(
            rows,
            args,
            key="vy_abs_p95_m_s",
            reverse=False,
            limit=5,
            filter_fn=lambda row: (finite_float(row.get("mean_vx_m_s")) or -999.0) >= 0.02,
        ),
        "closest_by_pass_count": sorted(
            [compact_row(row, args) for row in rows],
            key=lambda row: (row["pass_count"], float(row.get("mean_vx_m_s") or -999.0)),
            reverse=True,
        )[:10],
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Weight-Transfer Gate Failure Analysis",
        "",
        f"status: `{payload['status']}`",
        "",
        "This offline report scans compact target-source score artifacts and",
        "summarizes which parts of `PASS_WEIGHT_TRANSFER_TARGET` are currently",
        "binding. It does not run simulation, training, robot SSH, deployment, or",
        "hardware tests.",
        "",
        "## Dataset",
        "",
        f"- score artifacts: `{len(payload['artifacts'])}`",
        f"- seed rows scanned: `{payload['class_summary']['rows']}`",
        "",
        "## Constraint Pass Rates",
        "",
        "| constraint | threshold | observed | pass rows | pass pct | best | worst |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for label, item in payload["metric_summary"].items():
        lines.append(
            "| {label} | `{op} {threshold}` | {observed} | {passes} | {pass_pct} | {best} | {worst} |".format(
                label=label,
                op=item["op"],
                threshold=fmt(item["threshold"]),
                observed=item["observed"],
                passes=item["pass_rows"],
                pass_pct=fmt(item["pass_pct"], 2),
                best=fmt(item["best"]),
                worst=fmt(item["worst"]),
            )
        )
    summary = payload["class_summary"]
    lines.extend(
        [
            "",
            "## Combination Counts",
            "",
            "| bucket | rows |",
            "|---|---:|",
            f"| stable_actuator_rows | {summary['stable_actuator_rows']} |",
            f"| support_ready_rows | {summary['support_ready_rows']} |",
            f"| forward_ready_rows | {summary['forward_ready_rows']} |",
            f"| stable_and_support_rows | {summary['stable_and_support_rows']} |",
            f"| stable_and_forward_rows | {summary['stable_and_forward_rows']} |",
            f"| support_and_forward_rows | {summary['support_and_forward_rows']} |",
            f"| all_three_rows | {summary['all_three_rows']} |",
            "",
            "## Best Forward Rows Among Stable/Actuator-Safe Rows",
            "",
            "| artifact | seed | vx | dx | double | single | min side | failures |",
            "|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in summary["best_forward_among_stable"]:
        lines.append(row_line(row))
    lines.extend(
        [
            "",
            "## Best Support Rows Among Stable/Actuator-Safe Rows",
            "",
            "| artifact | seed | vx | dx | double | single | min side | failures |",
            "|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in summary["best_support_among_stable"]:
        lines.append(row_line(row))
    lines.extend(
        [
            "",
            "## Closest Rows By Gate Count",
            "",
            "| artifact | seed | pass count | vx | double | single | min side | failures |",
            "|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in summary["closest_by_pass_count"]:
        lines.append(
            "| {artifact} | `{seed}` | {pass_count} | {vx} | {double} | {single} | {side} | `{failures}` |".format(
                artifact=f"`{row['artifact']}`",
                seed=row["seed"],
                pass_count=row["pass_count"],
                vx=fmt(row.get("mean_vx_m_s")),
                double=fmt(row.get("double_support_pct"), 2),
                single=fmt(row.get("single_support_pct"), 2),
                side=fmt(row.get("min_single_support_side_pct"), 2),
                failures=", ".join(row["failures"]),
            )
        )
    lines.extend(["", "## Decision", "", "```text", payload["status"], "```", ""])
    if payload["status"] == "HOLD_FORWARD_IMPULSE_PRIMARY":
        lines.append(
            "The closest rows are generally stable and actuator-safe, but forward "
            "velocity/displacement remains far below the gate. The next target "
            "source needs an explicit propulsion mechanism after support loading, "
            "not only stronger contact alternation."
        )
    elif payload["status"] == "HOLD_SUPPORT_TRANSFER_PRIMARY":
        lines.append(
            "Forward motion appears in some rows, but useful left/right single "
            "support is missing. The next target source should prioritize body "
            "loading and swing unweighting before push."
        )
    else:
        lines.append(
            "No row family combines forward progress, support transfer, and "
            "stable actuator-safe behavior. The next branch should remain a "
            "structured target-source design, not PPO/BC."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def row_line(row: dict[str, Any]) -> str:
    return "| {artifact} | `{seed}` | {vx} | {dx} | {double} | {single} | {side} | `{failures}` |".format(
        artifact=f"`{row['artifact']}`",
        seed=row["seed"],
        vx=fmt(row.get("mean_vx_m_s")),
        dx=fmt(row.get("forward_displacement_m")),
        double=fmt(row.get("double_support_pct"), 2),
        single=fmt(row.get("single_support_pct"), 2),
        side=fmt(row.get("min_single_support_side_pct"), 2),
        failures=", ".join(row["failures"]),
    )


def infer_status(class_summary: dict[str, Any]) -> str:
    if class_summary["all_three_rows"] > 0:
        return "PASS_WEIGHT_TRANSFER_COMPONENT_ROW_EXISTS"
    if class_summary["stable_and_support_rows"] > 0 and class_summary["stable_and_forward_rows"] == 0:
        return "HOLD_FORWARD_IMPULSE_PRIMARY"
    if class_summary["stable_and_forward_rows"] > 0 and class_summary["stable_and_support_rows"] == 0:
        return "HOLD_SUPPORT_TRANSFER_PRIMARY"
    return "HOLD_NO_COMBINED_FORWARD_SUPPORT_SOURCE"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--score-json", action="append", default=None)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--min-mean-vx", type=float, default=0.04)
    parser.add_argument("--min-forward-displacement-m", type=float, default=0.004)
    parser.add_argument("--max-vy-abs-p95", type=float, default=0.12)
    parser.add_argument("--max-pitch-abs-p95", type=float, default=0.35)
    parser.add_argument("--min-base-height", type=float, default=0.145)
    parser.add_argument("--max-double-support-pct", type=float, default=75.0)
    parser.add_argument("--min-single-support-pct", type=float, default=20.0)
    parser.add_argument("--min-each-single-support-pct", type=float, default=5.0)
    parser.add_argument("--min-contact-transitions", type=int, default=2)
    parser.add_argument("--max-sent-velocity-p95", type=float, default=3.75)
    parser.add_argument("--max-tracking-p95", type=float, default=0.12)
    args = parser.parse_args()

    paths = [resolve(item) for item in args.score_json] if args.score_json else expand_default_inputs()
    rows, artifacts = read_rows(paths)
    metrics = metric_summary(rows, args)
    classes = classify(rows, args)
    payload = {
        "artifacts": artifacts,
        "metric_summary": metrics,
        "class_summary": classes,
    }
    payload["status"] = infer_status(classes)

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={payload['status']}")
    print(f"rows={len(rows)}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
