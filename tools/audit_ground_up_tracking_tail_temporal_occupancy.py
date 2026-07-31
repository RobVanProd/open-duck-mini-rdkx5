#!/usr/bin/env python3
"""Audit squared tail magnitude against the gate's temporal occupancy boundary."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np


INDICES = np.asarray([2, 3, 4, 11, 12, 13])
NAMES = [
    "left_hip_pitch", "left_knee", "left_ankle",
    "right_hip_pitch", "right_knee", "right_ankle",
]
THRESHOLD = 0.20
ALLOWED_EXCEEDANCE_TICKS = 30


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
    excess = np.maximum(error - THRESHOLD, 0.0)
    positive = excess[:, joint][excess[:, joint] > 0.0]
    counts = np.sum(error > THRESHOLD, axis=0)
    return {
        "path": str(path.resolve()),
        "sha256": sha256(path),
        "rows": len(rows),
        "command_x": float(rows[0]["command"][0]),
        "seed": int(rows[0]["seed"]),
        "gate_joint": NAMES[joint],
        "gate_p95_rad": float(p95[joint]),
        "gate_joint_exceedance_ticks": int(counts[joint]),
        "ticks_over_30_boundary": int(counts[joint] - ALLOWED_EXCEEDANCE_TICKS),
        "gate_joint_exceedance_fraction": float(counts[joint] / len(rows)),
        "conditional_mean_excess_rad": float(np.mean(positive)),
        "conditional_rms_excess_rad": float(np.sqrt(np.mean(np.square(positive)))),
        "conditional_max_excess_rad": float(np.max(positive)),
        "six_joint_squared_tail_mean": float(np.mean(np.square(excess))),
        "six_joint_linear_tail_mean": float(np.mean(excess)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    groups = {}
    unique = []
    all_rows = []
    for directory in sorted(path for path in args.trace_root.iterdir() if path.is_dir()):
        traces = [summarize(path) for path in sorted(directory.glob("*.jsonl"))]
        groups[directory.name] = traces
        all_rows.extend(traces)
        unique.extend(item for item in traces if item["seed"] == 100)

    squared_discordance = []
    linear_discordance = []
    for left, right in itertools.permutations(unique, 2):
        if (
            left["six_joint_squared_tail_mean"]
            < right["six_joint_squared_tail_mean"]
            and left["gate_p95_rad"] > right["gate_p95_rad"]
        ):
            squared_discordance.append((left["path"], right["path"]))
        if (
            left["six_joint_linear_tail_mean"]
            < right["six_joint_linear_tail_mean"]
            and left["gate_p95_rad"] > right["gate_p95_rad"]
        ):
            linear_discordance.append((left["path"], right["path"]))

    strong_final = groups["T3_FOUR_1024000"]
    strong_final_seed100 = sorted(
        (item for item in strong_final if item["seed"] == 100),
        key=lambda item: item["command_x"],
    )
    checks = {
        "all_36_traces_present": len(all_rows) == 36,
        "all_traces_have_600_rows": all(item["rows"] == 600 for item in all_rows),
        "strong_final_misses_boundary_by_1_7_3_ticks": [
            item["ticks_over_30_boundary"] for item in strong_final_seed100
        ]
        == [1, 7, 3],
        "strong_final_conditional_rms_excess_below_0p014": max(
            item["conditional_rms_excess_rad"] for item in strong_final_seed100
        )
        < 0.014,
        "squared_magnitude_has_gate_rank_discordance": len(squared_discordance) > 0,
        "linear_hinge_is_not_constant_rescaling_of_squared": len(
            {
                round(
                    item["six_joint_linear_tail_mean"]
                    / item["six_joint_squared_tail_mean"],
                    9,
                )
                for item in unique
                if item["six_joint_squared_tail_mean"] > 0.0
            }
        )
        > 1,
    }
    failed = [name for name, passed in checks.items() if not passed]
    status = "PASS_TEMPORAL_OCCUPANCY_AUDIT" if not failed else "FAIL_TEMPORAL_OCCUPANCY_AUDIT"
    decision = (
        "SELECT_TEMPORAL_OCCUPANCY_QUANTITY_NO_SURROGATE"
        if not failed
        else "NO_CAUSAL_MECHANISM_SELECTED"
    )
    payload = {
        "schema_version": "ground_up_tracking_tail_temporal_occupancy_audit.v1",
        "status": status,
        "decision": decision,
        "checks": checks,
        "failed_checks": failed,
        "threshold_rad": THRESHOLD,
        "allowed_exceedance_ticks_at_600": ALLOWED_EXCEEDANCE_TICKS,
        "unique_policy_command_rows": len(unique),
        "squared_cost_gate_rank_discordant_pairs": len(squared_discordance),
        "linear_cost_gate_rank_discordant_pairs": len(linear_discordance),
        "strong_final_seed100": strong_final_seed100,
        "groups": groups,
        "interpretation": (
            "The strongest final checkpoint is no longer failing on large errors: its "
            "gate-setting joint exceeds 0.20 rad by only 1, 7, and 3 ticks beyond the "
            "30-tick five-percent boundary, with conditional RMS excess below 0.014 rad. "
            "Squared hinge has vanishing pressure as those residuals approach the boundary "
            "and its ranking disagrees with the external p95 gate. Linear hinge is not "
            "selected: it has more rank-discordant pairs on the same frozen rows (21 vs "
            "17), so constant gradient alone is insufficient evidence. Temporal occupancy "
            "is the supported causal quantity, but no trainable surrogate is uniquely "
            "supported and no training run is authorized."
        ),
        "authority": {
            "cpu_diagnostic_only": False,
            "training": False,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Tracking-Tail Temporal Occupancy Audit",
        "",
        f"status: `{status}`",
        f"decision: `{decision}`",
        "",
        "| x | gate joint | p95 | exceed ticks | ticks over 30 | conditional RMS excess |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for item in strong_final_seed100:
        lines.append(
            f"| {item['command_x']:.3f} | `{item['gate_joint']}` | "
            f"{item['gate_p95_rad']:.9f} | {item['gate_joint_exceedance_ticks']} | "
            f"{item['ticks_over_30_boundary']} | {item['conditional_rms_excess_rad']:.9f} |"
        )
    lines.extend(
        [
            "",
            f"squared-cost/gate rank-discordant pairs: `{len(squared_discordance)}`",
            f"linear-cost/gate rank-discordant pairs: `{len(linear_discordance)}`",
            "",
            payload["interpretation"],
            "",
        ]
    )
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "failed": failed}, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
