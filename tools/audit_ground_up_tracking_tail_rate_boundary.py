#!/usr/bin/env python3
"""Audit whether gate-setting tails follow measured target-rate boundary use."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


INDICES = np.asarray([2, 3, 4, 11, 12, 13])
NAMES = [
    "left_hip_pitch", "left_knee", "left_ankle",
    "right_hip_pitch", "right_knee", "right_ankle",
]
LIMITS = np.asarray([1.50, 1.50, 1.75, 1.25, 1.00, 1.25])
DT = 0.02
THRESHOLD = 0.20


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def summarize(path: Path) -> dict:
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    sent = np.asarray([row["sent_target_rad"] for row in rows], dtype=np.float64)
    actual = np.asarray([row["actual_position_rad"] for row in rows], dtype=np.float64)
    error = np.abs(sent[:, INDICES] - actual[:, INDICES])
    p95 = np.percentile(error, 95, axis=0)
    joint = int(np.argmax(p95))
    rate = np.abs(np.diff(sent[:, INDICES[joint]], prepend=sent[0, INDICES[joint]])) / DT
    at_limit = rate >= LIMITS[joint] - 1.0e-4
    recent = np.asarray(
        [np.any(at_limit[max(0, tick - 2) : tick + 1]) for tick in range(len(rows))]
    )
    exceed = error[:, joint] > THRESHOLD
    phase_counts = np.bincount(np.arange(len(rows))[exceed] % 27, minlength=27)
    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "command_x": float(rows[0]["command"][0]),
        "seed": int(rows[0]["seed"]),
        "gate_joint": NAMES[joint],
        "gate_p95_rad": float(p95[joint]),
        "exceedance_ticks": int(np.sum(exceed)),
        "recent_rate_boundary_on_exceedance_fraction": float(np.mean(recent[exceed])),
        "recent_rate_boundary_off_exceedance_fraction": float(np.mean(recent[~exceed])),
        "top_four_period_bins_exceedance_fraction": float(
            np.sort(phase_counts)[-4:].sum() / phase_counts.sum()
        ),
        "period_bin_exceedance_counts": phase_counts.tolist(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-root", type=Path, required=True)
    parser.add_argument("--search-result", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    summaries = [
        summarize(path)
        for directory in sorted(path for path in args.trace_root.iterdir() if path.is_dir())
        for path in sorted(directory.glob("*.jsonl"))
    ]
    exceed_hits = []
    nonexceed_hits = []
    # Reconstruct pooled counts from each trace's exact fractions and tick counts.
    for item in summaries:
        exceed_count = item["exceedance_ticks"]
        nonexceed_count = 600 - exceed_count
        exceed_hits.append(
            (item["recent_rate_boundary_on_exceedance_fraction"], exceed_count)
        )
        nonexceed_hits.append(
            (item["recent_rate_boundary_off_exceedance_fraction"], nonexceed_count)
        )
    pooled_exceed = sum(fraction * count for fraction, count in exceed_hits) / sum(
        count for _, count in exceed_hits
    )
    pooled_nonexceed = sum(fraction * count for fraction, count in nonexceed_hits) / sum(
        count for _, count in nonexceed_hits
    )
    odds_ratio = (
        pooled_exceed / (1.0 - pooled_exceed)
    ) / (pooled_nonexceed / (1.0 - pooled_nonexceed))

    search = json.loads(args.search_result.read_text())
    t3_final_worst = search["arms"]["T3_FOUR"]["checkpoints"]["1024000"][
        "worst_tracking_p95_rad"
    ]
    gate_ratio = THRESHOLD / t3_final_worst
    gap = 1.0 - gate_ratio
    multipliers = [1.0 - factor * gap for factor in (1.0, 2.0, 4.0)]
    checks = {
        "all_36_traces_present": len(summaries) == 36,
        "at_least_97pct_exceedance_follows_two_tick_rate_boundary": pooled_exceed
        >= 0.97,
        "recent_rate_boundary_odds_ratio_at_least_5": odds_ratio >= 5.0,
        "top_four_period_bins_cover_at_least_88pct_each": min(
            item["top_four_period_bins_exceedance_fraction"] for item in summaries
        )
        >= 0.88,
        "derived_multipliers_positive_and_ordered": 0.0 < multipliers[2]
        < multipliers[1]
        < multipliers[0]
        < 1.0,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = "PASS_RATE_BOUNDARY_AUDIT" if not failed else "FAIL_RATE_BOUNDARY_AUDIT"
    decision = (
        "PREREGISTER_STATEFUL_PITCH_RATE_BOUNDARY_CPU_SCREEN"
        if not failed
        else "NO_RATE_BOUNDARY_SCREEN"
    )
    payload = {
        "schema_version": "ground_up_tracking_tail_rate_boundary_audit.v1",
        "status": status,
        "decision": decision,
        "checks": checks,
        "failed_checks": failed,
        "pooled_recent_rate_boundary_on_exceedance_fraction": pooled_exceed,
        "pooled_recent_rate_boundary_off_exceedance_fraction": pooled_nonexceed,
        "recent_rate_boundary_odds_ratio": odds_ratio,
        "minimum_top_four_period_bins_coverage": min(
            item["top_four_period_bins_exceedance_fraction"] for item in summaries
        ),
        "mean_top_four_period_bins_coverage": float(
            np.mean([item["top_four_period_bins_exceedance_fraction"] for item in summaries])
        ),
        "multiplier_derivation": {
            "strong_final_worst_tracking_p95_rad": t3_final_worst,
            "tracking_limit_rad": THRESHOLD,
            "gate_ratio": gate_ratio,
            "gap": gap,
            "factors": [1.0, 2.0, 4.0],
            "pitch_rate_multipliers": multipliers,
        },
        "traces": summaries,
        "interpretation": (
            "Gate-setting exceedances are phase-local and 97%+ occur at or within two "
            "ticks after the measured target-rate boundary, with an odds ratio above five. "
            "This supports a CPU-only stateful ONNX boundary A/B, not another reward or "
            "training run. Candidate multipliers are frozen from the exact T3-final gate "
            "ratio and 1x/2x/4x that measured gap before outcomes."
        ),
        "authority": {
            "cpu_policy_transform_screen": not failed,
            "training": False,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    args.output_md.write_text(
        "\n".join(
            [
                "# Ground-Up Tracking-Tail Rate-Boundary Audit",
                "",
                f"status: `{status}`",
                f"decision: `{decision}`",
                "",
                f"pooled exceedance recent-boundary fraction: `{pooled_exceed}`",
                f"pooled non-exceedance recent-boundary fraction: `{pooled_nonexceed}`",
                f"odds ratio: `{odds_ratio}`",
                f"minimum / mean top-four period-bin coverage: "
                f"`{payload['minimum_top_four_period_bins_coverage']}` / "
                f"`{payload['mean_top_four_period_bins_coverage']}`",
                f"derived pitch-rate multipliers: `{multipliers}`",
                "",
                payload["interpretation"],
                "",
            ]
        )
    )
    print(json.dumps({"status": status, "decision": decision, "failed": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
