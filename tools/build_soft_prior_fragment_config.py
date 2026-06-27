#!/usr/bin/env python3
"""Build a compact soft-prior config from curated target fragments.

This is an offline preparation tool. It does not train a policy, run PPO, SSH,
deploy, or touch the robot. The output is a compact phase-indexed prior that
can be reviewed before any learner consumes it.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = (
    ROOT / "outputs" / "analysis" / "target_dataset_manifest_dynamic_roll_lateral_fix_robust_modes.json"
)
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "SOFT_PRIOR_FRAGMENT_CONFIG.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "soft_prior_fragment_config.json"

PITCH_CHAIN_JOINTS = {
    "left_hip_pitch": 2,
    "left_knee": 3,
    "left_ankle": 4,
    "right_hip_pitch": 11,
    "right_knee": 12,
    "right_ankle": 13,
}


def finite(value: Any) -> bool:
    return isinstance(value, int | float | np.floating) and math.isfinite(float(value))


def fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "NA"
    return f"{float(value):.{digits}f}"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    for line in path.read_text().splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def percentile(values: Iterable[float], pct: float) -> float | None:
    data = [float(value) for value in values if finite(value)]
    if not data:
        return None
    return float(np.percentile(np.asarray(data, dtype=float), pct))


def stats(values: Iterable[float]) -> dict[str, float | None]:
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


def contact_tuple(values: Any) -> tuple[int, int]:
    if isinstance(values, np.ndarray):
        values = values.astype(int).reshape(-1).tolist()
    if not isinstance(values, list | tuple) or len(values) < 2:
        return (0, 0)
    return (int(values[0]), int(values[1]))


def pattern(values: tuple[int, int]) -> str:
    return f"{int(values[0])}{int(values[1])}"


def load_window(entry: dict[str, Any], joint_indices: list[int]) -> dict[str, Any]:
    source_path = Path(str(entry["source_path"]))
    mode = str(entry["mode"])
    start_tick = int(entry["start_tick"])
    end_tick = int(entry["end_tick"])
    records = [
        record
        for record in read_jsonl(source_path)
        if str(record.get("mode")) == mode and isinstance(record.get("action"), list)
    ]
    by_tick = {int(record["tick"]): record for record in records if "tick" in record}
    actions = []
    contacts = []
    body_pitch_abs = []
    base_height = []
    local_vx = []
    local_vy_abs = []
    for tick in range(start_tick, end_tick + 1):
        record = by_tick.get(tick)
        if record is None:
            continue
        action = np.asarray(record.get("action"), dtype=float).reshape(-1)
        if action.shape != (14,):
            continue
        actions.append(action[joint_indices])
        contacts.append(contact_tuple(record.get("foot_contacts")))
        body_pitch_abs.append(abs(float(record.get("body_pitch_rad", 0.0))))
        base_height.append(float(record.get("base_height_m", 0.0)))
        local_linvel = record.get("local_linvel_m_s") or [0.0, 0.0, 0.0]
        local_vx.append(float(local_linvel[0]) if len(local_linvel) > 0 else 0.0)
        local_vy_abs.append(abs(float(local_linvel[1])) if len(local_linvel) > 1 else 0.0)
    if not actions:
        raise ValueError(f"entry {entry.get('entry_id')} has no usable action window")
    return {
        "entry_id": entry.get("entry_id"),
        "source_name": source_path.name,
        "mode": mode,
        "start_tick": start_tick,
        "end_tick": end_tick,
        "actions": np.asarray(actions, dtype=float),
        "contacts": contacts,
        "body_pitch_abs": np.asarray(body_pitch_abs, dtype=float),
        "base_height": np.asarray(base_height, dtype=float),
        "local_vx": np.asarray(local_vx, dtype=float),
        "local_vy_abs": np.asarray(local_vy_abs, dtype=float),
    }


def build_prior(windows: list[dict[str, Any]], joint_names: list[str], dt_s: float) -> dict[str, Any]:
    window_len = min(window["actions"].shape[0] for window in windows)
    action_stack = np.asarray([window["actions"][:window_len] for window in windows], dtype=float)
    action_mean = np.mean(action_stack, axis=0)
    action_std = np.std(action_stack, axis=0)
    phase_contacts = []
    phase_contact_distribution = []
    for phase in range(window_len):
        counter = Counter(pattern(window["contacts"][phase]) for window in windows)
        total = sum(counter.values())
        phase_contacts.append(counter.most_common(1)[0][0])
        phase_contact_distribution.append(
            {key: count / total for key, count in sorted(counter.items())}
        )
    target_velocity = np.abs(np.diff(action_mean, axis=0) / max(dt_s, 1.0e-9))
    if target_velocity.shape[0] == 0:
        target_velocity = np.zeros_like(action_mean)
    else:
        target_velocity = np.vstack([np.zeros((1, action_mean.shape[1])), target_velocity])
    per_joint_velocity_p95 = {
        joint: percentile(target_velocity[:, index].tolist(), 95)
        for index, joint in enumerate(joint_names)
    }
    per_joint_std_p95 = {
        joint: percentile(action_std[:, index].tolist(), 95)
        for index, joint in enumerate(joint_names)
    }
    return {
        "window_len": window_len,
        "joint_names": joint_names,
        "joint_indices": [PITCH_CHAIN_JOINTS[name] for name in joint_names],
        "dt_s": dt_s,
        "action_mean": action_mean.tolist(),
        "action_std": action_std.tolist(),
        "phase_contact_mode": phase_contacts,
        "phase_contact_distribution": phase_contact_distribution,
        "per_joint_action_std_p95": per_joint_std_p95,
        "per_joint_target_velocity_p95_rad_s": per_joint_velocity_p95,
        "max_target_velocity_p95_rad_s": max(
            value for value in per_joint_velocity_p95.values() if value is not None
        ),
    }


def classify(payload: dict[str, Any], args: argparse.Namespace) -> str:
    summary = payload["summary"]
    prior = payload["prior"]
    if summary["entries"] < args.min_entries:
        return "HOLD_SOFT_PRIOR_INSUFFICIENT_FRAGMENTS"
    if summary["source_files"] < args.min_source_files:
        return "HOLD_SOFT_PRIOR_SOURCE_SKEW"
    if summary["mean_vx_m_s"]["mean"] is None or summary["mean_vx_m_s"]["mean"] < args.min_mean_vx:
        return "HOLD_SOFT_PRIOR_LOW_SOURCE_FORWARD_MOTION"
    if summary["vy_abs_p95_m_s"]["p95"] is not None and summary["vy_abs_p95_m_s"]["p95"] > args.max_vy_p95:
        return "HOLD_SOFT_PRIOR_SOURCE_LATERAL_UNSTABLE"
    if (
        summary["body_pitch_abs_p95_rad"]["p95"] is not None
        and summary["body_pitch_abs_p95_rad"]["p95"] > args.max_pitch_p95
    ):
        return "HOLD_SOFT_PRIOR_SOURCE_PITCH_UNSTABLE"
    if (
        prior["max_target_velocity_p95_rad_s"] is not None
        and prior["max_target_velocity_p95_rad_s"] > args.max_prior_velocity_p95
    ):
        return "HOLD_SOFT_PRIOR_PRIOR_TOO_FAST"
    return "PASS_SOFT_PRIOR_CONFIG_READY"


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    summary = payload["summary"]
    prior = payload["prior"]
    lines = [
        "# Soft-Prior Fragment Config",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is a compact pitch-chain/contact prior distilled from curated",
        "low-command target fragments. It is not a policy, not a target-label",
        "dataset, and not training permission.",
        "",
        "## Inputs",
        "",
        f"- manifest: `{payload['manifest_path']}`",
        f"- dataset_id: `{payload['dataset_id']}`",
        f"- entries: `{summary['entries']}`",
        f"- source_files: `{summary['source_files']}`",
        f"- source_mode_pairs: `{summary['source_mode_pairs']}`",
        f"- window_len: `{prior['window_len']}`",
        f"- joints: `{', '.join(prior['joint_names'])}`",
        "",
        "## Source Metrics",
        "",
        "| metric | min | mean | p50 | p95 | max |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for key in [
        "mean_vx_m_s",
        "vy_abs_p95_m_s",
        "body_pitch_abs_p95_rad",
        "base_height_min_m",
        "contact_dominance_pct",
    ]:
        item = summary[key]
        lines.append(
            f"| {key} | {fmt(item['min'])} | {fmt(item['mean'])} | {fmt(item['p50'])} | {fmt(item['p95'])} | {fmt(item['max'])} |"
        )
    lines.extend(
        [
            "",
            "## Prior Metrics",
            "",
            f"- max target velocity p95: `{fmt(prior['max_target_velocity_p95_rad_s'])}` rad/s",
            "",
            "| joint | action std p95 | target velocity p95 |",
            "|---|---:|---:|",
        ]
    )
    for joint in prior["joint_names"]:
        lines.append(
            f"| {joint} | {fmt(prior['per_joint_action_std_p95'][joint])} | {fmt(prior['per_joint_target_velocity_p95_rad_s'][joint])} |"
        )
    lines.extend(
        [
            "",
            "## Gate",
            "",
            "- `PASS_SOFT_PRIOR_CONFIG_READY` means the compact prior is usable for a default-off smoke evaluator.",
            "- It does not permit PPO, robot validation, or deployment.",
            "- Next required gate: `PASS_SOFT_PRIOR_SMOKE` from `docs/SOFT_PRIOR_CLOSED_LOOP_LEARNER_PLAN.md`.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--min-entries", type=int, default=6)
    parser.add_argument("--min-source-files", type=int, default=2)
    parser.add_argument("--min-mean-vx", type=float, default=0.04)
    parser.add_argument("--max-vy-p95", type=float, default=0.12)
    parser.add_argument("--max-pitch-p95", type=float, default=0.35)
    parser.add_argument("--max-prior-velocity-p95", type=float, default=3.75)
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text())
    entries = manifest.get("entries") or []
    joint_names = list(PITCH_CHAIN_JOINTS)
    joint_indices = [PITCH_CHAIN_JOINTS[name] for name in joint_names]
    windows = [load_window(entry, joint_indices) for entry in entries]
    source_files = {window["source_name"] for window in windows}
    source_mode_pairs = {(window["source_name"], window["mode"]) for window in windows}
    prior = build_prior(windows, joint_names, args.dt_s)
    summary = {
        "entries": len(windows),
        "source_files": len(source_files),
        "source_mode_pairs": len(source_mode_pairs),
        "by_source": dict(sorted(Counter(window["source_name"] for window in windows).items())),
        "mean_vx_m_s": stats(float(np.mean(window["local_vx"])) for window in windows),
        "vy_abs_p95_m_s": stats(percentile(window["local_vy_abs"].tolist(), 95) for window in windows),
        "body_pitch_abs_p95_rad": stats(
            percentile(window["body_pitch_abs"].tolist(), 95) for window in windows
        ),
        "base_height_min_m": stats(float(np.min(window["base_height"])) for window in windows),
        "contact_dominance_pct": stats(
            max(Counter(pattern(item) for item in window["contacts"]).values())
            / len(window["contacts"])
            * 100.0
            for window in windows
        ),
    }
    digest_payload = {
        "manifest": str(manifest_path),
        "entries": [entry.get("entry_id") for entry in entries],
        "prior": prior,
    }
    dataset_id = hashlib.sha256(json.dumps(digest_payload, sort_keys=True).encode()).hexdigest()[:16]
    payload = {
        "status": "UNKNOWN",
        "manifest_path": str(manifest_path),
        "manifest_status": manifest.get("status"),
        "dataset_id": dataset_id,
        "source_dataset_id": manifest.get("dataset_id"),
        "summary": summary,
        "prior": prior,
        "next_required_gate": "PASS_SOFT_PRIOR_SMOKE",
    }
    payload["status"] = classify(payload, args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={payload['status']}")
    print(f"dataset_id={dataset_id}")
    print(f"entries={summary['entries']}")
    print(f"source_files={summary['source_files']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
