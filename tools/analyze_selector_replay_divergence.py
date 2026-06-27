#!/usr/bin/env python3
"""Compare selector sequence replay traces against their source traces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from eval_reference_motion_rollout import percentile


ROOT = Path(__file__).resolve().parents[1]


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and np.isfinite(float(value))


def fmt(value: Any) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.4f}"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def contact(values: Any) -> str:
    if not isinstance(values, list | tuple) or len(values) < 2:
        return "??"
    return f"{int(values[0])}{int(values[1])}"


def vector(row: dict[str, Any], key: str) -> np.ndarray | None:
    value = row.get(key)
    if not isinstance(value, list):
        return None
    arr = np.asarray(value, dtype=float).reshape(-1)
    return arr if arr.size else None


def abs_errors(values: list[float]) -> dict[str, float] | None:
    data = [abs(float(value)) for value in values if finite(value)]
    if not data:
        return None
    return {
        "mean": float(np.mean(data)),
        "p50": percentile(data, 50),
        "p95": percentile(data, 95),
        "max": float(np.max(data)),
    }


def compare_trace(source_path: Path, replay_path: Path, *, prefix_end_tick: int) -> dict[str, Any]:
    source_rows = {int(row["tick"]): row for row in read_jsonl(source_path) if "tick" in row}
    replay_rows = read_jsonl(replay_path)
    action_errors = []
    pitch_errors = []
    height_errors = []
    vx_errors = []
    vy_errors = []
    contact_mismatches = []
    first_large_divergence = None
    compared = 0
    compared_prefix = 0
    for replay in replay_rows:
        tick = int(replay.get("tick", -1))
        source = source_rows.get(tick)
        if source is None:
            continue
        compared += 1
        if tick < prefix_end_tick:
            compared_prefix += 1
        src_action = vector(source, "action")
        replay_action = vector(replay, "action")
        if src_action is not None and replay_action is not None and src_action.shape == replay_action.shape:
            action_errors.append(float(np.max(np.abs(src_action - replay_action))))
        pitch_error = float(replay.get("body_pitch_rad", 0.0)) - float(source.get("body_pitch_rad", 0.0))
        height_error = float(replay.get("base_height_m", 0.0)) - float(source.get("base_height_m", 0.0))
        src_vel = source.get("local_linvel_m_s") or [0.0, 0.0, 0.0]
        replay_vel = replay.get("local_linvel_m_s") or [0.0, 0.0, 0.0]
        vx_error = float(replay_vel[0]) - float(src_vel[0]) if len(src_vel) > 0 and len(replay_vel) > 0 else 0.0
        vy_error = float(replay_vel[1]) - float(src_vel[1]) if len(src_vel) > 1 and len(replay_vel) > 1 else 0.0
        pitch_errors.append(pitch_error)
        height_errors.append(height_error)
        vx_errors.append(vx_error)
        vy_errors.append(vy_error)
        mismatch = contact(source.get("foot_contacts")) != contact(replay.get("foot_contacts"))
        contact_mismatches.append(mismatch)
        if first_large_divergence is None and (
            abs(pitch_error) > 0.05 or abs(height_error) > 0.03 or abs(vy_error) > 0.25 or mismatch
        ):
            first_large_divergence = {
                "tick": tick,
                "pitch_error_rad": pitch_error,
                "height_error_m": height_error,
                "vx_error_m_s": vx_error,
                "vy_error_m_s": vy_error,
                "source_contact": contact(source.get("foot_contacts")),
                "replay_contact": contact(replay.get("foot_contacts")),
            }
    return {
        "source_path": str(source_path),
        "replay_path": str(replay_path),
        "samples": len(replay_rows),
        "compared_ticks": compared,
        "compared_prefix_ticks": compared_prefix,
        "prefix_end_tick": prefix_end_tick,
        "action_max_abs_error": abs_errors(action_errors),
        "pitch_abs_error_rad": abs_errors(pitch_errors),
        "height_abs_error_m": abs_errors(height_errors),
        "vx_abs_error_m_s": abs_errors(vx_errors),
        "vy_abs_error_m_s": abs_errors(vy_errors),
        "contact_mismatch_pct": 100.0 * sum(contact_mismatches) / max(len(contact_mismatches), 1),
        "first_large_divergence": first_large_divergence,
    }


def status(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "HOLD_NO_DIVERGENCE_ROWS"
    early = [
        row
        for row in rows
        if row.get("first_large_divergence")
        and int(row["first_large_divergence"].get("tick", 10**9)) < int(row.get("prefix_end_tick") or 0)
    ]
    if early:
        return "HOLD_REPLAY_DIVERGES_BEFORE_SELECTOR_WINDOW"
    return "PASS_REPLAY_PREFIX_MATCHES_SOURCE"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Selector Replay Divergence",
        "",
        f"status: `{payload['status']}`",
        "",
        "This compares bounded sequence replay traces against their source traces. It does not step simulation, train, deploy, SSH, run robot tests, or change runtime behavior.",
        "",
        "| policy | seed | samples | prefix_end | action_err95 | pitch_err95 | height_err95 | vy_err95 | contact_mismatch_% | first_divergence |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["rows"]:
        first = row.get("first_large_divergence") or {}
        lines.append(
            f"| {row['policy_name'][:36]} | {row['seed']} | {row['samples']} | {row['prefix_end_tick']} | "
            f"{fmt((row.get('action_max_abs_error') or {}).get('p95'))} | "
            f"{fmt((row.get('pitch_abs_error_rad') or {}).get('p95'))} | "
            f"{fmt((row.get('height_abs_error_m') or {}).get('p95'))} | "
            f"{fmt((row.get('vy_abs_error_m_s') or {}).get('p95'))} | "
            f"{fmt(row.get('contact_mismatch_pct'))} | `{first.get('tick', 'NA')}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Early divergence before `prefix_end` means open-loop prefix replay cannot reliably recreate the source state.",
            "- If the replay diverges before the selector window, use state-aligned replay or a closed-loop selector before BC/export.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay-json", default="outputs/analysis/relabelled_selector_sequence_replay_top3_5s.json")
    parser.add_argument("--manifest", default="outputs/analysis/relabelled_selector_replay_manifest.json")
    parser.add_argument("--output-md", default="outputs/analysis/RELABELLED_SELECTOR_REPLAY_DIVERGENCE.md")
    parser.add_argument("--output-json", default="outputs/analysis/relabelled_selector_replay_divergence.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    replay = json.loads((ROOT / args.replay_json).read_text())
    manifest = json.loads((ROOT / args.manifest).read_text())
    entries = {entry["entry_id"]: entry for entry in manifest.get("entries") or []}
    rows = []
    for policy_name, policy in (replay.get("rollout", {}).get("policies") or {}).items():
        entry_ids = policy.get("entry_ids") or []
        entry = entries.get(entry_ids[0]) if entry_ids else None
        if entry is None:
            continue
        for seed, seed_row in (policy.get("seeds") or {}).items():
            trace = seed_row.get("trace")
            if not trace:
                continue
            row = compare_trace(
                Path(entry["source_path"]),
                Path(trace),
                prefix_end_tick=int(entry["start_tick"]),
            )
            row["policy_name"] = policy_name
            row["seed"] = seed
            row["rollout_status"] = seed_row.get("status")
            rows.append(row)
    payload = {
        "status": status(rows),
        "replay_json": args.replay_json,
        "manifest": args.manifest,
        "rows": rows,
    }
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_markdown(payload, output_md)
    print(f"status={payload['status']}")
    print(f"rows={len(rows)}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
