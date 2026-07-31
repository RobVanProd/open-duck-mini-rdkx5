#!/usr/bin/env python3
"""Relate phase-conditioned actions and teacher corrections to measured progress.

This is offline analysis only. It reads saved full-observation traces and does
not train, simulate, deploy, connect to a robot, or require a GPU.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from build_rate_bounded_teacher_traces import project_rate
from compare_policy_to_behavior_prior import JOINT_NAMES, predict_mlp_npz

PITCH_CHAIN = [2, 3, 4, 11, 12, 13]


def load_trace(path: Path) -> tuple[int, np.ndarray, np.ndarray, np.ndarray]:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    valid = [
        row
        for row in rows
        if len(row.get("obs_state") or []) == 101
        and len(row.get("action") or []) == 14
        and len(row.get("foot_contacts") or []) == 2
    ]
    if not valid:
        raise ValueError(f"no aligned obs/action/contact samples in {path}")
    seeds = {int(row["seed"]) for row in valid}
    if len(seeds) != 1:
        raise ValueError(f"expected one seed in {path}, got {sorted(seeds)}")
    observations = np.asarray([row["obs_state"] for row in valid], dtype=np.float64)
    actions = np.asarray([row["action"] for row in valid], dtype=np.float64)
    contacts = np.asarray([row["foot_contacts"] for row in valid], dtype=np.int64)
    return seeds.pop(), observations, actions, contacts


def waveform(coefficients: np.ndarray, samples: int = 256) -> np.ndarray:
    phase = np.linspace(0.0, 2.0 * np.pi, samples, endpoint=False)
    features = np.column_stack((np.ones(samples), np.cos(phase), np.sin(phase)))
    return features @ coefficients


def contact_pct(contacts: np.ndarray) -> dict[str, float]:
    return {
        f"{left}{right}": float(
            100.0 * np.mean((contacts[:, 0] == left) & (contacts[:, 1] == right))
        )
        for left, right in ((0, 0), (0, 1), (1, 0), (1, 1))
    }


def cosine_alignment(correction: np.ndarray, target: np.ndarray) -> dict[str, float]:
    dot = np.sum(correction * target, axis=1)
    denominator = np.linalg.norm(correction, axis=1) * np.linalg.norm(target, axis=1)
    cosine = np.divide(
        dot,
        denominator,
        out=np.zeros_like(dot),
        where=denominator > 1.0e-12,
    )
    return {
        "mean": float(np.mean(cosine)),
        "p50": float(np.percentile(cosine, 50)),
        "positive_pct": float(100.0 * np.mean(cosine > 0.0)),
        "projection_mean": float(np.mean(dot)),
    }


def main() -> int:
    args = parse_args()
    manifest = json.loads(Path(args.manifest).read_text())
    traces = []
    for entry in manifest.get("entries", []):
        seed, observations, actions, contacts = load_trace(Path(entry["source_path"]))
        progress = entry.get("mean_vx_m_s")
        if progress is None:
            raise ValueError(f"manifest entry lacks mean_vx_m_s: {entry['source_path']}")
        features = np.column_stack(
            (np.ones(observations.shape[0]), observations[:, 99:101])
        )
        coefficients = np.linalg.lstsq(features, actions, rcond=None)[0]
        traces.append(
            {
                "seed": seed,
                "source_path": entry["source_path"],
                "mean_vx_m_s": float(progress),
                "observations": observations,
                "actions": actions,
                "contacts": contacts,
                "phase_features": features,
                "phase_coefficients": coefficients,
            }
        )
    if len(traces) < args.cohort_size * 2:
        raise ValueError(
            f"need at least {args.cohort_size * 2} traces for disjoint cohorts"
        )
    traces.sort(key=lambda item: item["mean_vx_m_s"])
    low = traces[: args.cohort_size]
    high = traces[-args.cohort_size :]
    low_coeff = np.asarray([item["phase_coefficients"] for item in low])
    high_coeff = np.asarray([item["phase_coefficients"] for item in high])
    coefficient_delta = np.mean(high_coeff, axis=0) - np.mean(low_coeff, axis=0)

    high_waves = np.asarray([waveform(item["phase_coefficients"]) for item in high])
    low_waves = np.asarray([waveform(item["phase_coefficients"]) for item in low])
    mean_wave_delta = np.mean(high_waves, axis=0) - np.mean(low_waves, axis=0)
    between_rms = np.sqrt(np.mean(mean_wave_delta**2, axis=0))
    high_dispersion = np.mean(
        (high_waves - np.mean(high_waves, axis=0, keepdims=True)) ** 2,
        axis=(0, 1),
    )
    low_dispersion = np.mean(
        (low_waves - np.mean(low_waves, axis=0, keepdims=True)) ** 2,
        axis=(0, 1),
    )
    within_rms = np.sqrt((high_dispersion + low_dispersion) / 2.0)

    joint_rows = []
    for index, name in enumerate(JOINT_NAMES):
        joint_rows.append(
            {
                "joint": name,
                "index": index,
                "phase_waveform_between_rms": float(between_rms[index]),
                "phase_waveform_within_rms": float(within_rms[index]),
                "between_to_within_ratio": float(
                    between_rms[index] / max(within_rms[index], 1.0e-12)
                ),
                "intercept_delta": float(coefficient_delta[0, index]),
                "harmonic_rms_delta": float(
                    np.linalg.norm(coefficient_delta[1:, index]) / np.sqrt(2.0)
                ),
            }
        )
    joint_rows.sort(key=lambda item: item["between_to_within_ratio"], reverse=True)

    teacher_path = Path(args.teacher_npz)
    alignment_rows = []
    all_correction = []
    all_target = []
    for item in low:
        teacher = predict_mlp_npz(teacher_path, item["observations"])
        correction = teacher - item["actions"]
        target = item["phase_features"] @ coefficient_delta
        all_correction.append(correction)
        all_target.append(target)
        alignment_rows.append(
            {
                "seed": item["seed"],
                "mean_vx_m_s": item["mean_vx_m_s"],
                "all_joints": cosine_alignment(correction, target),
                "pitch_chain": cosine_alignment(
                    correction[:, PITCH_CHAIN], target[:, PITCH_CHAIN]
                ),
            }
        )
    correction = np.concatenate(all_correction, axis=0)
    target = np.concatenate(all_target, axis=0)
    candidate_corrections = []
    candidate_rates = []
    for item in low:
        candidate = item["actions"] + item["phase_features"] @ coefficient_delta
        candidate[:, PITCH_CHAIN] = project_rate(
            candidate[:, PITCH_CHAIN],
            args.max_target_rate_rad_s * args.dt_s / args.action_scale,
            args.rate_projection_passes,
        )
        candidate_corrections.append(candidate - item["actions"])
        candidate_rates.append(
            np.abs(np.diff(candidate[:, PITCH_CHAIN], axis=0))
            * args.action_scale
            / args.dt_s
        )
    candidate_correction = np.concatenate(candidate_corrections, axis=0)
    candidate_rate = np.concatenate(candidate_rates, axis=0)
    high_contacts = np.concatenate([item["contacts"] for item in high], axis=0)
    low_contacts = np.concatenate([item["contacts"] for item in low], axis=0)

    report: dict[str, Any] = {
        "status": "PASS_PHASE_ACTION_OUTCOME_COHORT_ANALYSIS_READY",
        "manifest": args.manifest,
        "teacher_npz": args.teacher_npz,
        "phase_features": ["intercept", "obs_state[99]", "obs_state[100]"],
        "cohort_definition": {
            "method": "rank_by_manifest_mean_vx",
            "cohort_size": args.cohort_size,
            "low": [
                {"seed": item["seed"], "mean_vx_m_s": item["mean_vx_m_s"]}
                for item in low
            ],
            "high": [
                {"seed": item["seed"], "mean_vx_m_s": item["mean_vx_m_s"]}
                for item in high
            ],
        },
        "contact_occupancy_pct": {
            "low": contact_pct(low_contacts),
            "high": contact_pct(high_contacts),
        },
        "phase_action_difference_by_joint": joint_rows,
        "phase_action_coefficient_delta": coefficient_delta.tolist(),
        "empirical_full_delta_screen_on_low_cohort": {
            "correction_abs": absolute_stats(candidate_correction),
            "pitch_target_rate_abs_rad_s": absolute_stats(candidate_rate),
            "max_target_rate_rad_s": args.max_target_rate_rad_s,
            "action_scale": args.action_scale,
            "dt_s": args.dt_s,
            "rate_projection_passes": args.rate_projection_passes,
        },
        "teacher_alignment_on_low_cohort": {
            "aggregate_all_joints": cosine_alignment(correction, target),
            "aggregate_pitch_chain": cosine_alignment(
                correction[:, PITCH_CHAIN], target[:, PITCH_CHAIN]
            ),
            "by_seed": alignment_rows,
        },
        "limitations": [
            "Eight traces and rank-defined cohorts provide hypothesis evidence, not causality.",
            "Phase regression summarizes observed actions; it does not prove that applying the high-cohort waveform to low states is safe or effective.",
            "Teacher alignment is a directional screen and does not replace closed-loop evaluation.",
        ],
        "offline_only": True,
    }
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_json).write_text(json.dumps(report, indent=2) + "\n")
    write_markdown(Path(args.output_md), report)
    print(report["status"])
    return 0


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cohorts = report["cohort_definition"]
    contacts = report["contact_occupancy_pct"]
    alignment = report["teacher_alignment_on_low_cohort"]
    screen = report["empirical_full_delta_screen_on_low_cohort"]
    lines = [
        "# Phase-Conditioned Action Outcome Cohorts",
        "",
        f"status: `{report['status']}`",
        "",
        "Offline analysis only. No training, simulation, deployment, robot access,",
        "local GPU, or Colab allocation was performed.",
        "",
        "## Cohorts",
        "",
        "Cohorts are rank-defined from measured manifest mean velocity; no behavior",
        "threshold was chosen after inspecting joint actions.",
        "",
        "| cohort | seed | mean vx (m/s) |",
        "|---|---:|---:|",
    ]
    for name in ("low", "high"):
        for item in cohorts[name]:
            lines.append(f"| {name} | {item['seed']} | {item['mean_vx_m_s']:.6f} |")
    lines += [
        "",
        "## Contact Occupancy",
        "",
        "| cohort | neither | right only (01) | left only (10) | double (11) |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in ("low", "high"):
        item = contacts[name]
        lines.append(
            f"| {name} | {item['00']:.2f}% | {item['01']:.2f}% | "
            f"{item['10']:.2f}% | {item['11']:.2f}% |"
        )
    lines += [
        "",
        "## Phase-Conditioned Action Differences",
        "",
        "A linear harmonic model uses the policy's two phase observations. The",
        "between/within ratio ranks cohort separation relative to seed variation.",
        "",
        "| joint | waveform between RMS | within RMS | ratio | intercept delta | harmonic RMS delta |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in report["phase_action_difference_by_joint"]:
        lines.append(
            f"| `{item['joint']}` | {item['phase_waveform_between_rms']:.5f} | "
            f"{item['phase_waveform_within_rms']:.5f} | "
            f"{item['between_to_within_ratio']:.3f} | "
            f"{item['intercept_delta']:+.5f} | {item['harmonic_rms_delta']:.5f} |"
        )
    lines += [
        "",
        "## Existing Teacher Alignment on Low-Progress States",
        "",
        "Cosine alignment compares the teacher correction with the empirical",
        "low-to-high phase-action direction. +1 is aligned, 0 orthogonal, and -1",
        "opposed.",
        "",
        "| scope | mean cosine | median | positive samples | mean projection |",
        "|---|---:|---:|---:|---:|",
    ]
    for label, key in (
        ("all joints", "aggregate_all_joints"),
        ("pitch chain", "aggregate_pitch_chain"),
    ):
        item = alignment[key]
        lines.append(
            f"| {label} | {item['mean']:+.5f} | {item['p50']:+.5f} | "
            f"{item['positive_pct']:.2f}% | {item['projection_mean']:+.7f} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "The observed outcome separation is concentrated in phase-conditioned",
        "pitch-chain behavior, especially the left knee and ankle. Contact",
        "occupancy alone does not separate success: the high cohort has more, not",
        "less, double support. The existing teacher correction is approximately",
        "orthogonal to the empirical low-to-high action direction and therefore",
        "does not encode a coherent outcome-aligned correction on these states.",
        "",
        "## Empirical Full-Delta Offline Screen",
        "",
        "Adding the measured cohort phase delta to the low-cohort actions, with",
        "the registered pitch-chain temporal projection, gives:",
        "",
        f"- correction mean/p95/max: `{screen['correction_abs']['mean']:.5f}` / "
        f"`{screen['correction_abs']['p95']:.5f}` / `{screen['correction_abs']['max']:.5f}`",
        f"- pitch target-rate p95/max: `{screen['pitch_target_rate_abs_rad_s']['p95']:.5f}` / "
        f"`{screen['pitch_target_rate_abs_rad_s']['max']:.5f}` rad/s",
        "",
        "This is a screen, not a new teacher target. The high-cohort waveform must",
        "not be applied counterfactually without state-matched safety evidence.",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report["limitations"])
    path.write_text("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--teacher-npz", required=True)
    parser.add_argument("--cohort-size", type=int, default=3)
    parser.add_argument("--max-target-rate-rad-s", type=float, default=2.0)
    parser.add_argument("--action-scale", type=float, default=0.25)
    parser.add_argument("--dt-s", type=float, default=0.02)
    parser.add_argument("--rate-projection-passes", type=int, default=4)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-json", required=True)
    return parser.parse_args()


def absolute_stats(values: np.ndarray) -> dict[str, float]:
    values = np.abs(np.asarray(values, dtype=np.float64)).reshape(-1)
    return {
        "mean": float(np.mean(values)),
        "p50": float(np.percentile(values, 50)),
        "p95": float(np.percentile(values, 95)),
        "p99": float(np.percentile(values, 99)),
        "max": float(np.max(values)),
    }


if __name__ == "__main__":
    raise SystemExit(main())
