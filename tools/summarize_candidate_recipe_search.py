#!/usr/bin/env python3
"""Summarize offline candidate-policy gate reports.

This is an evidence hygiene helper. It reads closed-loop sim eval JSON files
already produced by ``tools/eval_policy_with_actuator_bridge.py`` and creates a
small table of candidate outcomes. It does not import Playground, run MuJoCo,
train, SSH, deploy, or touch the robot.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def is_candidate_eval(payload: dict[str, Any]) -> bool:
    loop = payload.get("closed_loop_sim")
    if not isinstance(loop, dict):
        return False
    return loop.get("eval_role") == "candidate" or bool(loop.get("candidate_gate"))


def discover_json(root: Path) -> list[Path]:
    candidates: list[Path] = []
    patterns = [
        "**/*candidate_gate_x0.json",
        "**/*candidate_gate_x008.json",
        "**/closed_loop_actuator_bridge_eval.json",
    ]
    for pattern in patterns:
        candidates.extend(root.glob(pattern))
    return sorted(set(path for path in candidates if path.is_file()))


def candidate_name_from_path(path: Path) -> str:
    stem = path.stem
    for suffix in (
        "_candidate_gate_x008",
        "_candidate_gate_x0",
        "_gate_x008",
        "_gate_x0",
    ):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    for part in reversed(path.parts):
        for suffix in ("_gate_x008", "_gate_x0", "_candidate_gate_x008", "_candidate_gate_x0"):
            if part.endswith(suffix):
                return part[: -len(suffix)]
    if path.parent.name in {"candidate_gate_x0", "candidate_gate_x008", "gate_x0", "gate_x008"}:
        return path.parent.parent.name
    return path.parent.name


def mode_forward(loop: dict[str, Any], mode: str) -> dict[str, Any]:
    modes = loop.get("modes")
    if not isinstance(modes, dict):
        return {}
    payload = modes.get(mode)
    if not isinstance(payload, dict):
        return {}
    forward = payload.get("forward_motion")
    return forward if isinstance(forward, dict) else {}


def mode_summary(loop: dict[str, Any], mode: str) -> dict[str, Any]:
    modes = loop.get("modes")
    if not isinstance(modes, dict):
        return {}
    payload = modes.get(mode)
    return payload if isinstance(payload, dict) else {}


def extract_row(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    loop = payload["closed_loop_sim"]
    gate = loop.get("candidate_gate") if isinstance(loop.get("candidate_gate"), dict) else {}
    metrics = gate.get("metrics") if isinstance(gate.get("metrics"), dict) else {}
    vanilla = mode_summary(loop, "vanilla")
    fitted = mode_summary(loop, "fitted")
    stress = mode_summary(loop, "stress")
    forward = mode_forward(loop, "vanilla")
    command_x = payload.get("command_x")
    if command_x is None:
        command = vanilla.get("command") if isinstance(vanilla.get("command"), list) else None
        command_x = command[0] if command else None

    return {
        "candidate": candidate_name_from_path(path),
        "path": str(path),
        "status": payload.get("overall_status") or loop.get("status"),
        "command_x": command_x,
        "max_action_saturation_pct": metrics.get("max_action_saturation_pct"),
        "max_pitch_tracking_p95_rad": metrics.get("max_pitch_tracking_p95_rad"),
        "max_sent_target_velocity_p95_rad_s": metrics.get(
            "max_sent_target_velocity_p95_rad_s"
        ),
        "max_abs_body_pitch_p95_rad": metrics.get("max_abs_body_pitch_p95_rad"),
        "min_base_height_m": metrics.get("min_base_height_m"),
        "min_reward_mean": metrics.get("min_reward_mean"),
        "min_forward_command_tracking_ratio": metrics.get(
            "min_forward_command_tracking_ratio"
        ),
        "max_abs_forward_velocity_error_m_s": metrics.get(
            "max_abs_forward_velocity_error_m_s"
        ),
        "vanilla_mean_local_vx_m_s": forward.get("mean_velocity_x_m_s"),
        "vanilla_progress_x_m": forward.get("progress_x_m"),
        "vanilla_termination": vanilla.get("termination_reason"),
        "fitted_termination": fitted.get("termination_reason"),
        "stress_termination": stress.get("termination_reason"),
    }


def dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        key = (
            row.get("candidate"),
            row.get("command_x"),
            row.get("status"),
            row.get("max_pitch_tracking_p95_rad"),
            row.get("min_forward_command_tracking_ratio"),
        )
        current = by_key.get(key)
        if current is None or len(row["path"]) < len(current["path"]):
            by_key[key] = row
    return sorted(
        by_key.values(),
        key=lambda row: (
            row.get("candidate") or "",
            -1.0 if row.get("command_x") is None else float(row["command_x"]),
            row.get("path") or "",
        ),
    )


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def numeric(value: Any) -> float | None:
    return value if isinstance(value, int | float) else None


def status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("status") or "UNKNOWN")
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def x008_frontier(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    x008_rows = [
        row
        for row in rows
        if numeric(row.get("command_x")) is not None
        and abs(float(row["command_x"]) - 0.08) < 1.0e-6
        and numeric(row.get("min_forward_command_tracking_ratio")) is not None
    ]
    return sorted(
        x008_rows,
        key=lambda row: float(row.get("min_forward_command_tracking_ratio") or -999.0),
        reverse=True,
    )[:8]


def write_markdown(rows: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Candidate Recipe Search Summary",
        "",
        "Offline-only summary of candidate sim gates. No robot motion, SSH,",
        "deployment, or runtime behavior change is implied by this report.",
        "",
        "## Status Counts",
        "",
        "| status | count |",
        "|---|---:|",
    ]
    for status, count in status_counts(rows).items():
        lines.append(f"| `{status}` | {count} |")

    lines.extend(
        [
            "",
            "## Best x=0.08 Forward-Progress Attempts",
            "",
            "Sorted by minimum forward command tracking ratio. These are still",
            "offline sim gates only; high progress with falls/posture failures is",
            "not deployable.",
            "",
            "| candidate | status | track ratio | mean vx | pitch p95 | target vel p95 | body pitch p95 | min height |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in x008_frontier(rows):
        lines.append(
            "| `{candidate}` | `{status}` | {ratio} | {vx} | {pitch} | {vel} | {body} | {height} |".format(
                candidate=row.get("candidate"),
                status=row.get("status"),
                ratio=fmt(row.get("min_forward_command_tracking_ratio")),
                vx=fmt(row.get("vanilla_mean_local_vx_m_s")),
                pitch=fmt(row.get("max_pitch_tracking_p95_rad")),
                vel=fmt(row.get("max_sent_target_velocity_p95_rad_s")),
                body=fmt(row.get("max_abs_body_pitch_p95_rad")),
                height=fmt(row.get("min_base_height_m")),
            )
        )

    lines.extend(
        [
            "",
        "## Gate Outcomes",
        "",
        "| candidate | cmd x | status | track ratio | mean vx | pitch p95 | target vel p95 | action sat % | body pitch p95 | min height | terminations |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in rows:
        terminations = "/".join(
            str(row.get(key) or "NA")
            for key in ("vanilla_termination", "fitted_termination", "stress_termination")
        )
        lines.append(
            "| `{candidate}` | {cmd} | `{status}` | {ratio} | {vx} | {pitch} | {vel} | {sat} | {body} | {height} | `{terms}` |".format(
                candidate=row.get("candidate"),
                cmd=fmt(row.get("command_x")),
                status=row.get("status"),
                ratio=fmt(row.get("min_forward_command_tracking_ratio")),
                vx=fmt(row.get("vanilla_mean_local_vx_m_s")),
                pitch=fmt(row.get("max_pitch_tracking_p95_rad")),
                vel=fmt(row.get("max_sent_target_velocity_p95_rad_s")),
                sat=fmt(row.get("max_action_saturation_pct")),
                body=fmt(row.get("max_abs_body_pitch_p95_rad")),
                height=fmt(row.get("min_base_height_m")),
                terms=terminations,
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `PASS_CANDIDATE_SIM_GATE` means the candidate passed the configured",
            "  offline sim gate only. It is not robot approval.",
            "- `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` means the candidate stayed",
            "  stable but did not meaningfully track the commanded forward speed.",
            "- Fall/termination and high saturation candidates are not deployable.",
            "- A useful next recipe should improve x=0.08 tracking ratio while",
            "  keeping action saturation, target velocity, pitch tracking, body",
            "  pitch, and base height inside the current gate thresholds.",
            "",
            "## Source Files",
            "",
        ]
    )
    for row in rows:
        lines.append(f"- `{row['path']}`")
    output.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "roots",
        nargs="*",
        type=Path,
        default=[Path("outputs/analysis")],
        help="Directories to scan for candidate gate JSON files.",
    )
    parser.add_argument("--output-md", type=Path)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    for root in args.roots:
        for path in discover_json(root):
            payload = load_json(path)
            if payload and is_candidate_eval(payload):
                rows.append(extract_row(path, payload))
    rows = dedupe_rows(rows)

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n")
    if args.output_md:
        write_markdown(rows, args.output_md)
    if not args.output_json and not args.output_md:
        print(json.dumps(rows, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
