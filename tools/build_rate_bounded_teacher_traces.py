#!/usr/bin/env python3
"""Build temporally rate-bounded teacher labels on student-visited traces.

The bounded projection uses alternating forward/backward passes. Unlike a
one-sided clamp, it spreads a required correction across neighboring ticks so
the transition target is not replaced by a single held value. This is offline
dataset analysis only; it does not train, deploy, SSH, or touch the robot.
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np

from compare_policy_to_behavior_prior import JOINT_NAMES, abs_stats, predict_mlp_npz


PITCH_INDICES = [2, 3, 4, 11, 12, 13]


def contact_code(row: dict) -> str:
    contacts = row.get("foot_contacts") or []
    return "".join(str(int(bool(value))) for value in contacts[:2]) if len(contacts) >= 2 else "NA"


def project_rate(sequence: np.ndarray, max_delta: float, passes: int) -> np.ndarray:
    bounded = sequence.copy()
    for _ in range(passes):
        for tick in range(1, bounded.shape[0]):
            bounded[tick] = np.clip(
                bounded[tick], bounded[tick - 1] - max_delta, bounded[tick - 1] + max_delta
            )
        for tick in range(bounded.shape[0] - 2, -1, -1):
            bounded[tick] = np.clip(
                bounded[tick], bounded[tick + 1] - max_delta, bounded[tick + 1] + max_delta
            )
    return bounded


def transition_mask(codes: list[str], radius: int) -> np.ndarray:
    mask = np.zeros(len(codes), dtype=bool)
    changes = [tick for tick in range(1, len(codes)) if codes[tick] != codes[tick - 1]]
    for tick in changes:
        mask[max(0, tick - radius) : min(len(codes), tick + radius + 1)] = True
    return mask


def main() -> int:
    args = parse_args()
    paths = sorted({Path(item) for pattern in args.trace_glob for item in glob.glob(pattern)})
    max_delta = args.max_target_rate_rad_s * args.dt_s / args.action_scale
    output_root = Path(args.output_trace_dir)
    trace_reports = []
    all_distortion, all_original_rates, all_bounded_rates = [], [], []
    for path in paths:
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        observations = np.asarray([row["obs_state"] for row in rows], dtype=np.float64)
        teacher = predict_mlp_npz(Path(args.teacher_npz), observations)
        bounded = teacher.copy()
        bounded[:, PITCH_INDICES] = project_rate(
            teacher[:, PITCH_INDICES], max_delta, args.projection_passes
        )
        original_rate = np.abs(np.diff(teacher[:, PITCH_INDICES], axis=0)) * args.action_scale / args.dt_s
        bounded_rate = np.abs(np.diff(bounded[:, PITCH_INDICES], axis=0)) * args.action_scale / args.dt_s
        distortion = bounded - teacher
        codes = [contact_code(row) for row in rows]
        near_transition = transition_mask(codes, args.transition_radius_ticks)
        transition_distortion = distortion[near_transition][:, PITCH_INDICES]
        ordinary_distortion = distortion[~near_transition][:, PITCH_INDICES]
        seed_dir = path.parent.name
        output_path = output_root / seed_dir / path.name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            for tick, row in enumerate(rows):
                new_row = dict(row)
                new_row["student_action"] = row.get("action")
                new_row["unbounded_teacher_action"] = teacher[tick].tolist()
                new_row["action"] = bounded[tick].tolist()
                new_row["rate_bounded_teacher"] = True
                new_row["rate_bound_rad_s"] = args.max_target_rate_rad_s
                new_row["rate_projection_passes"] = args.projection_passes
                new_row["near_contact_transition"] = bool(near_transition[tick])
                new_row["mode"] = args.output_mode
                handle.write(json.dumps(new_row, sort_keys=True) + "\n")
        report = {
            "source_trace": str(path),
            "output_trace": str(output_path),
            "samples": len(rows),
            "contact_transition_count": sum(codes[tick] != codes[tick - 1] for tick in range(1, len(codes))),
            "transition_window_samples": int(np.sum(near_transition)),
            "original_teacher_rate_abs_rad_s": abs_stats(original_rate),
            "bounded_teacher_rate_abs_rad_s": abs_stats(bounded_rate),
            "bounded_vs_teacher_abs": abs_stats(distortion),
            "pitch_distortion_near_transition_abs": abs_stats(transition_distortion),
            "pitch_distortion_away_transition_abs": abs_stats(ordinary_distortion),
            "changed_pitch_values": int(np.sum(np.abs(distortion[:, PITCH_INDICES]) > 1.0e-12)),
        }
        trace_reports.append(report)
        all_distortion.append(distortion)
        all_original_rates.append(original_rate)
        all_bounded_rates.append(bounded_rate)
    distortion = np.concatenate(all_distortion) if all_distortion else np.empty((0, 14))
    original_rates = np.concatenate(all_original_rates) if all_original_rates else np.empty((0, 6))
    bounded_rates = np.concatenate(all_bounded_rates) if all_bounded_rates else np.empty((0, 6))
    payload = {
        "status": "PASS_RATE_BOUNDED_TEACHER_TRACES_READY" if trace_reports else "HOLD_NO_TRACES",
        "trace_globs": args.trace_glob,
        "teacher_npz": args.teacher_npz,
        "output_trace_dir": args.output_trace_dir,
        "settings": {
            "pitch_joints": [JOINT_NAMES[index] for index in PITCH_INDICES],
            "max_target_rate_rad_s": args.max_target_rate_rad_s,
            "max_action_delta": max_delta,
            "projection_passes": args.projection_passes,
            "transition_radius_ticks": args.transition_radius_ticks,
        },
        "summary": {
            "traces": len(trace_reports),
            "samples": int(sum(item["samples"] for item in trace_reports)),
            "original_teacher_rate_abs_rad_s": abs_stats(original_rates),
            "bounded_teacher_rate_abs_rad_s": abs_stats(bounded_rates),
            "bounded_vs_teacher_abs": abs_stats(distortion),
            "changed_pitch_values": int(sum(item["changed_pitch_values"] for item in trace_reports)),
        },
        "traces": trace_reports,
        "offline_only": True,
    }
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(Path(args.output_md), payload)
    print(payload["status"])
    return 0 if trace_reports else 2


def write_markdown(path: Path, payload: dict) -> None:
    summary = payload["summary"]
    original = summary["original_teacher_rate_abs_rad_s"]
    bounded = summary["bounded_teacher_rate_abs_rad_s"]
    distortion = summary["bounded_vs_teacher_abs"]
    lines = [
        "# Phase 2 Rate-Bounded On-Policy Teacher Traces",
        "",
        f"status: `{payload['status']}`",
        "",
        "Offline target-manifold analysis only. No training, deployment, SSH, local GPU, or robot operation was performed.",
        "",
        "## Summary",
        "",
        f"- traces/samples: `{summary['traces']}` / `{summary['samples']}`",
        f"- original teacher target-rate p95/max: `{original['p95']:.4f}` / `{original['max']:.4f}` rad/s",
        f"- bounded teacher target-rate p95/max: `{bounded['p95']:.4f}` / `{bounded['max']:.4f}` rad/s",
        f"- bounded-vs-teacher action mean/p95/max: `{distortion['mean']:.4f}` / `{distortion['p95']:.4f}` / `{distortion['max']:.4f}`",
        f"- changed pitch-chain values: `{summary['changed_pitch_values']}`",
        "",
        "## Per Trace",
        "",
        "| trace | transitions | changed | original max | bounded max | distortion p95 | transition distortion p95 | ordinary distortion p95 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in payload["traces"]:
        lines.append(
            f"| `{Path(item['source_trace']).parent.name}` | {item['contact_transition_count']} | "
            f"{item['changed_pitch_values']} | {item['original_teacher_rate_abs_rad_s']['max']:.4f} | "
            f"{item['bounded_teacher_rate_abs_rad_s']['max']:.4f} | {item['bounded_vs_teacher_abs']['p95']:.4f} | "
            f"{(item['pitch_distortion_near_transition_abs']['p95'] or 0.0):.4f} | "
            f"{(item['pitch_distortion_away_transition_abs']['p95'] or 0.0):.4f} |"
        )
    path.write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-glob", action="append", required=True)
    parser.add_argument("--teacher-npz", required=True)
    parser.add_argument("--output-trace-dir", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--max-target-rate-rad-s", type=float, default=2.0)
    parser.add_argument("--action-scale", type=float, default=0.25)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--projection-passes", type=int, default=4)
    parser.add_argument("--transition-radius-ticks", type=int, default=4)
    parser.add_argument("--output-mode", default="rate_bounded_onpolicy_teacher")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
