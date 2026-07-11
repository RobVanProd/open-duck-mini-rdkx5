#!/usr/bin/env python3
"""Measure frozen-teacher corrections on student-visited full-observation traces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from compare_policy_to_behavior_prior import JOINT_NAMES, abs_stats, predict_mlp_npz


PITCH_CHAIN = {2, 3, 4, 11, 12, 13}


def load_trace(path: Path) -> tuple[np.ndarray, np.ndarray]:
    observations, actions = [], []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        obs = row.get("obs_state") or row.get("observation")
        action = row.get("action")
        if isinstance(obs, list) and len(obs) == 101 and isinstance(action, list) and len(action) == 14:
            observations.append(obs)
            actions.append(action)
    if not observations:
        raise ValueError(f"no obs[101]/action[14] rows in {path}")
    return np.asarray(observations, dtype=np.float64), np.asarray(actions, dtype=np.float64)


def main() -> int:
    args = parse_args()
    manifest = json.loads(Path(args.manifest).read_text())
    rows = []
    all_corrections = []
    all_teacher_rates = []
    pitch_dominant = 0
    for entry in manifest.get("entries", []):
        path = Path(entry["source_path"])
        observations, student = load_trace(path)
        teacher = predict_mlp_npz(Path(args.teacher_npz), observations)
        correction = teacher - student
        teacher_rate = np.abs(np.diff(teacher, axis=0)) * args.action_scale / args.dt_s
        joint_stats = {
            name: abs_stats(correction[:, index])
            for index, name in enumerate(JOINT_NAMES)
        }
        top_index = int(np.argmax([float(joint_stats[name]["p95"] or 0.0) for name in JOINT_NAMES]))
        is_pitch = top_index in PITCH_CHAIN
        pitch_dominant += int(is_pitch)
        rows.append(
            {
                "source_name": entry.get("source_name"),
                "samples": int(observations.shape[0]),
                "correction_abs": abs_stats(correction),
                "correction_abs_by_joint": joint_stats,
                "top_correction_joint": JOINT_NAMES[top_index],
                "top_correction_is_pitch_chain": is_pitch,
                "teacher_target_rate_abs": abs_stats(teacher_rate),
                "teacher_target_rate_max_by_joint_rad_s": {
                    name: float(np.max(teacher_rate[:, index])) if teacher_rate.size else 0.0
                    for index, name in enumerate(JOINT_NAMES)
                },
            }
        )
        all_corrections.append(correction)
        if teacher_rate.size:
            all_teacher_rates.append(teacher_rate)
    corrections = np.concatenate(all_corrections, axis=0)
    rates = np.concatenate(all_teacher_rates, axis=0)
    payload = {
        "status": "PASS_ONPOLICY_TEACHER_CORRECTION_ANALYSIS_READY",
        "manifest": args.manifest,
        "teacher_npz": args.teacher_npz,
        "trace_count": len(rows),
        "samples": int(corrections.shape[0]),
        "pitch_chain_dominant_trace_count": pitch_dominant,
        "pitch_chain_dominant_fraction": pitch_dominant / len(rows) if rows else None,
        "correction_abs": abs_stats(corrections),
        "teacher_target_rate_abs_rad_s": abs_stats(rates),
        "thresholds": {
            "required_pitch_chain_dominant_traces": args.required_pitch_chain_dominant_traces,
            "teacher_target_rate_p95_max_rad_s": args.teacher_target_rate_p95_max,
            "teacher_target_rate_max_rad_s": args.teacher_target_rate_max,
            "correction_max_normalized_action": args.correction_max,
        },
        "data_gate_pass": bool(
            pitch_dominant >= args.required_pitch_chain_dominant_traces
            and float(abs_stats(rates)["p95"] or float("inf")) <= args.teacher_target_rate_p95_max
            and float(abs_stats(rates)["max"] or float("inf")) <= args.teacher_target_rate_max
            and float(abs_stats(corrections)["max"] or float("inf")) <= args.correction_max
        ),
        "traces": rows,
        "offline_only": True,
    }
    if payload["data_gate_pass"]:
        payload["status"] = "PASS_ONPOLICY_CONTINUITY_DATA_GATE"
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(Path(args.output_md), payload)
    print(payload["status"])
    return 0 if payload["data_gate_pass"] else 2


def write_markdown(path: Path, payload: dict) -> None:
    correction = payload["correction_abs"]
    rate = payload["teacher_target_rate_abs_rad_s"]
    lines = [
        "# Phase 2 Stage A On-Policy Teacher Corrections",
        "",
        f"status: `{payload['status']}`",
        f"data_gate_pass: `{payload['data_gate_pass']}`",
        "",
        "Offline analysis only. No training, deployment, SSH, local GPU, or robot operation was performed.",
        "",
        "## Aggregate",
        "",
        f"- traces: `{payload['trace_count']}`",
        f"- samples: `{payload['samples']}`",
        f"- pitch-chain-dominant traces: `{payload['pitch_chain_dominant_trace_count']}/{payload['trace_count']}`",
        f"- teacher correction mean/p95/max: `{correction['mean']:.4f}` / `{correction['p95']:.4f}` / `{correction['max']:.4f}` normalized action",
        f"- teacher target-rate p95/max: `{rate['p95']:.4f}` / `{rate['max']:.4f}` rad/s",
        "",
        "## Per Trace",
        "",
        "| source | top correction joint | pitch chain | correction p95 | correction max | teacher rate p95 | teacher rate max |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in payload["traces"]:
        correction = row["correction_abs"]
        rate = row["teacher_target_rate_abs"]
        lines.append(
            f"| `{row['source_name']}` | `{row['top_correction_joint']}` | "
            f"`{row['top_correction_is_pitch_chain']}` | {correction['p95']:.4f} | "
            f"{correction['max']:.4f} | {rate['p95']:.4f} | {rate['max']:.4f} |"
        )
    lines += ["", "## Decision", ""]
    lines.append(
        "The pre-registered data gate passed; a default-off/uniform-weight parity check remains required before any GPU smoke."
        if payload["data_gate_pass"]
        else "The pre-registered data gate did not pass. Do not allocate a GPU or train this branch."
    )
    path.write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--teacher-npz", required=True)
    parser.add_argument("--action-scale", type=float, default=0.25)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--required-pitch-chain-dominant-traces", type=int, default=6)
    parser.add_argument("--teacher-target-rate-p95-max", type=float, default=1.75)
    parser.add_argument("--teacher-target-rate-max", type=float, default=2.0)
    parser.add_argument("--correction-max", type=float, default=0.25)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
