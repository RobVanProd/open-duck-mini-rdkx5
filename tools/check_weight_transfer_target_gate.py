#!/usr/bin/env python3
"""Check compact target-source score artifacts against the weight-transfer gate.

This is an offline gate checker. It reads JSON summaries produced by
score_target_candidates_objective.py or compatible optimizer wrappers. It does
not run simulation, train, deploy, SSH, or touch the robot.
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "WEIGHT_TRANSFER_TARGET_GATE_CHECK.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "weight_transfer_target_gate_check.json"
DEFAULT_PATTERNS = [
    "outputs/analysis/*weight_transfer*_score_100.json",
    "outputs/analysis/*weight_transfer*_score_150.json",
    "outputs/analysis/target_generator_single_support_probe_score_100.json",
    "outputs/analysis/target_generator_single_support_probe_score_150.json",
    "outputs/analysis/contact_weight_transfer_sequence_optimizer_smoke/iteration_00/score.json",
]


def resolve(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else ROOT / path


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def seed_key(seed: str) -> tuple[int, str]:
    digits = "".join(ch for ch in seed if ch.isdigit())
    return (int(digits) if digits else 999999, seed)


def expand_default_inputs() -> list[Path]:
    paths: set[Path] = set()
    for pattern in DEFAULT_PATTERNS:
        paths.update(resolve(item) for item in glob.glob(str(resolve(pattern))))
    return sorted(paths)


def pass_seed(seed: dict[str, Any], args: argparse.Namespace) -> tuple[bool, list[str]]:
    failures: list[str] = []
    checks = [
        ("low_forward_velocity", seed.get("mean_vx_m_s"), args.min_mean_vx, ">="),
        (
            "low_forward_displacement",
            seed.get("forward_displacement_m"),
            args.min_forward_displacement_m,
            ">=",
        ),
        ("high_lateral_velocity", seed.get("vy_abs_p95_m_s"), args.max_vy_abs_p95, "<="),
        ("high_body_pitch", seed.get("body_pitch_abs_p95_rad"), args.max_pitch_abs_p95, "<="),
        ("low_base_height", seed.get("base_height_min_m"), args.min_base_height, ">="),
        ("double_support_dominates", seed.get("double_support_pct"), args.max_double_support_pct, "<="),
        ("too_little_single_support", seed.get("single_support_pct"), args.min_single_support_pct, ">="),
        (
            "single_support_not_balanced",
            seed.get("min_single_support_side_pct"),
            args.min_each_single_support_pct,
            ">=",
        ),
        ("too_few_contact_transitions", seed.get("contact_transitions"), args.min_contact_transitions, ">="),
        (
            "high_sent_target_velocity",
            seed.get("sent_target_velocity_p95_rad_s"),
            args.max_sent_velocity_p95,
            "<=",
        ),
        ("high_tracking_error", seed.get("joint_tracking_p95_rad"), args.max_tracking_p95, "<="),
    ]
    for reason, value, threshold, op in checks:
        if value is None:
            failures.append(f"{reason}:missing")
            continue
        value_f = float(value)
        if op == ">=" and value_f < float(threshold):
            failures.append(reason)
        elif op == "<=" and value_f > float(threshold):
            failures.append(reason)
    if seed.get("done_inside_window"):
        failures.append("done_inside_window")
    return not failures, failures


def normalize_seed_rows(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = result.get("seeds") or {}
    if not isinstance(rows, dict):
        return {}
    return {str(seed): dict(row) for seed, row in rows.items() if isinstance(row, dict)}


def evaluate_result(result: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    seeds = normalize_seed_rows(result)
    seed_checks = {}
    required_ok = True
    for seed in args.required_seeds:
        candidates = [seed, f"seed_{int(seed):03d}"] if str(seed).isdigit() else [seed]
        row = None
        seed_label = None
        for candidate in candidates:
            if candidate in seeds:
                row = seeds[candidate]
                seed_label = candidate
                break
        if row is None:
            required_ok = False
            seed_checks[str(seed)] = {
                "present": False,
                "passes": False,
                "failures": ["missing_seed"],
            }
            continue
        passes, failures = pass_seed(row, args)
        required_ok = required_ok and passes
        seed_checks[str(seed)] = {
            "present": True,
            "source_label": seed_label,
            "passes": passes,
            "failures": failures,
            "metrics": {
                key: row.get(key)
                for key in (
                    "mean_vx_m_s",
                    "forward_displacement_m",
                    "vy_abs_p95_m_s",
                    "body_pitch_abs_p95_rad",
                    "base_height_min_m",
                    "double_support_pct",
                    "single_support_pct",
                    "min_single_support_side_pct",
                    "contact_transitions",
                    "sent_target_velocity_p95_rad_s",
                    "joint_tracking_p95_rad",
                )
            },
        }
    return {
        "mode": result.get("mode"),
        "min_seed_score": result.get("min_seed_score"),
        "mean_seed_score": result.get("mean_seed_score"),
        "declared_passes_all_seeds": bool(result.get("passes_all_seeds")),
        "gate_passes": required_ok,
        "seed_checks": seed_checks,
    }


def evaluate_file(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "label": path.stem, "status": "MISSING", "results": []}
    payload = json.loads(path.read_text())
    results = payload.get("results") or []
    if not isinstance(results, list):
        results = []
    evaluated = [evaluate_result(result, args) for result in results[: args.max_results_per_file]]
    return {
        "path": str(path),
        "label": path.stem,
        "status": payload.get("status", "UNKNOWN"),
        "window_samples": payload.get("window_samples"),
        "mode_count": payload.get("mode_count"),
        "robust_mode_count": payload.get("robust_mode_count"),
        "reason_counts": payload.get("reason_counts") or {},
        "results": evaluated,
        "gate_pass_count": sum(1 for result in evaluated if result["gate_passes"]),
    }


def infer_status(files: list[dict[str, Any]]) -> str:
    if any(file.get("gate_pass_count", 0) > 0 for file in files):
        return "PASS_WEIGHT_TRANSFER_TARGET"
    if not files:
        return "HOLD_NO_GATE_INPUTS"
    if all(file.get("status") == "MISSING" for file in files):
        return "HOLD_NO_GATE_INPUTS"
    return "HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET"


def top_candidates(files: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    rows = []
    for file in files:
        for result in file.get("results", []):
            rows.append(
                {
                    "file": file["label"],
                    "mode": result.get("mode"),
                    "gate_passes": result.get("gate_passes"),
                    "min_seed_score": result.get("min_seed_score"),
                    "mean_seed_score": result.get("mean_seed_score"),
                    "seed_checks": result.get("seed_checks"),
                }
            )
    rows.sort(
        key=lambda row: (
            bool(row.get("gate_passes")),
            float(row.get("min_seed_score") or -999999.0),
            float(row.get("mean_seed_score") or -999999.0),
        ),
        reverse=True,
    )
    return rows[:limit]


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Weight-Transfer Target Gate Check",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an executable offline check of the documented",
        "`PASS_WEIGHT_TRANSFER_TARGET` gate. It reads compact score artifacts only;",
        "it does not run simulation, training, robot SSH, deployment, or hardware tests.",
        "",
        "## Gate Criteria",
        "",
        "| metric | threshold |",
        "|---|---:|",
    ]
    for key, value in payload["criteria"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Inputs",
            "",
            "| artifact | status | window | robust | checked | pass |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for file in payload["files"]:
        lines.append(
            "| `{label}` | `{status}` | {window} | {robust} | {checked} | {passes} |".format(
                label=file["label"],
                status=file.get("status"),
                window=file.get("window_samples", "NA"),
                robust=file.get("robust_mode_count", "NA"),
                checked=len(file.get("results") or []),
                passes=file.get("gate_pass_count", 0),
            )
        )
    lines.extend(
        [
            "",
            "## Top Candidates",
            "",
            "| artifact | mode | pass | min score | seed | vx | dx | double | single | min side | failures |",
            "|---|---|---:|---:|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in payload["top_candidates"]:
        for seed, check in sorted((row.get("seed_checks") or {}).items(), key=lambda item: seed_key(item[0])):
            metrics = check.get("metrics") or {}
            lines.append(
                "| `{file}` | `{mode}` | {passes} | {score} | `{seed}` | {vx} | {dx} | {double} | {single} | {side} | `{failures}` |".format(
                    file=row.get("file"),
                    mode=row.get("mode"),
                    passes="yes" if row.get("gate_passes") else "no",
                    score=fmt(row.get("min_seed_score")),
                    seed=seed,
                    vx=fmt(metrics.get("mean_vx_m_s")),
                    dx=fmt(metrics.get("forward_displacement_m")),
                    double=fmt(metrics.get("double_support_pct"), 2),
                    single=fmt(metrics.get("single_support_pct"), 2),
                    side=fmt(metrics.get("min_single_support_side_pct"), 2),
                    failures=", ".join(check.get("failures") or []),
                )
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "```text",
            payload["status"],
            "```",
            "",
        ]
    )
    if payload["status"] == "PASS_WEIGHT_TRANSFER_TARGET":
        lines.append("At least one compact target-source score passes the documented gate.")
    else:
        lines.append(
            "No checked target source currently proves sustained, seed-robust weight transfer. "
            "Do not use these artifacts as permission for BC/PPO or robot validation."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--score-json",
        action="append",
        default=None,
        help="Score JSON to check. May be repeated. Defaults to known weight-transfer score artifacts.",
    )
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--required-seeds", default="0,2")
    parser.add_argument("--max-results-per-file", type=int, default=3)
    parser.add_argument("--max-report-candidates", type=int, default=8)
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

    args.required_seeds = [item.strip() for item in args.required_seeds.split(",") if item.strip()]
    if args.score_json:
        paths = [resolve(item) for item in args.score_json]
    else:
        paths = expand_default_inputs()
    files = [evaluate_file(path, args) for path in paths]
    payload = {
        "criteria": {
            "required_seeds": args.required_seeds,
            "min_mean_vx": args.min_mean_vx,
            "min_forward_displacement_m": args.min_forward_displacement_m,
            "max_vy_abs_p95": args.max_vy_abs_p95,
            "max_pitch_abs_p95": args.max_pitch_abs_p95,
            "min_base_height": args.min_base_height,
            "max_double_support_pct": args.max_double_support_pct,
            "min_single_support_pct": args.min_single_support_pct,
            "min_each_single_support_pct": args.min_each_single_support_pct,
            "min_contact_transitions": args.min_contact_transitions,
            "max_sent_velocity_p95": args.max_sent_velocity_p95,
            "max_tracking_p95": args.max_tracking_p95,
        },
        "files": files,
    }
    payload["status"] = infer_status(files)
    payload["top_candidates"] = top_candidates(files, args.max_report_candidates)

    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={payload['status']}")
    print(f"inputs={len(files)}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
