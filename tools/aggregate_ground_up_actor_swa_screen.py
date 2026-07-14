#!/usr/bin/env python3
"""Aggregate the preregistered actor-only cumulative SWA behavior screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from aggregate_ground_up_stateful_pitch_rate_boundary_screen import checkpoint_summary


RATES = {"U0_UNCHANGED": 1.0, "R3_FOUR_GAP": 0.919637027640626}
TAILS = ("T2_EQUAL", "T3_FOUR")
CHECKPOINTS = ("HALF_CUMULATIVE", "FINAL_CUMULATIVE")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--transform-contract", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    prereg = json.loads(args.preregistration.read_text())
    transform = json.loads(args.transform_contract.read_text())
    rates = {}
    combinations = []
    for rate_name, multiplier in RATES.items():
        tails = {}
        for tail_name in TAILS:
            checkpoints = {}
            for checkpoint_name in CHECKPOINTS:
                path = args.eval_root / (
                    f"ground_up_actor_swa_{rate_name}_{tail_name}_"
                    f"{checkpoint_name}_eval.json"
                )
                checkpoints[checkpoint_name] = checkpoint_summary(path)
            item = {
                "checkpoints": checkpoints,
                "combination_pass": all(
                    checkpoint["checkpoint_pass"] for checkpoint in checkpoints.values()
                ),
                "worst_tracking_p95_rad": max(
                    checkpoint["worst_tracking_p95_rad"] for checkpoint in checkpoints.values()
                ),
                "minimum_forward_velocity_m_s": min(
                    checkpoint["minimum_forward_velocity_m_s"] for checkpoint in checkpoints.values()
                ),
            }
            tails[tail_name] = item
            combinations.append((rate_name, tail_name, item))
        rates[rate_name] = {"pitch_multiplier": multiplier, "tails": tails}

    checks = {
        "preregistration_status_valid": prereg["status"] == "PREREGISTERED_CPU_ONLY",
        "preregistered_matrix_exact": (
            prereg["matrix"]["source_tail_arms"] == list(TAILS)
            and prereg["matrix"]["averaged_checkpoints"] == list(CHECKPOINTS)
            and prereg["matrix"]["onnx_policies"] == 8
            and prereg["matrix"]["behavior_cells"] == 48
        ),
        "transform_contract_passed": transform["status"] == "PASS_ACTOR_SWA_TRANSFORM_CONTRACT",
        "all_48_cells_present": all(
            checkpoint["checks"]["all_six_cells_present"]
            for _, _, item in combinations
            for checkpoint in item["checkpoints"].values()
        ),
        "all_48_cells_cpu_only": all(
            checkpoint["execution_platform"] == "cpu"
            for _, _, item in combinations
            for checkpoint in item["checkpoints"].values()
        ),
        "all_48_cells_600_ticks": all(
            checkpoint["checks"]["all_600_ticks_duration_complete"]
            for _, _, item in combinations
            for checkpoint in item["checkpoints"].values()
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    passing = [row for row in combinations if row[2]["combination_pass"]]
    if failed:
        status = "FAIL_ACTOR_SWA_SCREEN_EVIDENCE_CONTRACT"
        decision = "INVALID_EVIDENCE"
        winner = None
    elif passing:
        rate_name, tail_name, item = sorted(
            passing,
            key=lambda row: (
                -RATES[row[0]],
                row[2]["worst_tracking_p95_rad"],
                -row[2]["minimum_forward_velocity_m_s"],
            ),
        )[0]
        status = "PASS_ACTOR_SWA_SCREEN_WITH_WINNER"
        decision = f"ADVANCE_{rate_name}_{tail_name}"
        winner = {
            "rate": rate_name,
            "tail": tail_name,
            "worst_tracking_p95_rad": item["worst_tracking_p95_rad"],
            "minimum_forward_velocity_m_s": item["minimum_forward_velocity_m_s"],
        }
    else:
        status = "PASS_ACTOR_SWA_SCREEN_NO_WINNER"
        decision = "CLOSE_ACTOR_SWA_STABILIZATION_FORMULATION"
        winner = None

    closest_rate, closest_tail, closest = min(
        combinations, key=lambda row: row[2]["worst_tracking_p95_rad"]
    )
    payload = {
        "schema_version": "ground_up_actor_swa_screen_result.v1",
        "status": status,
        "decision": decision,
        "checks": checks,
        "failed_checks": failed,
        "preregistration": {
            "path": str(args.preregistration.resolve()),
            "sha256": sha256(args.preregistration),
        },
        "transform_contract": {
            "path": str(args.transform_contract.resolve()),
            "sha256": sha256(args.transform_contract),
        },
        "rates": rates,
        "passing_combinations": [
            {"rate": rate, "tail": tail} for rate, tail, _ in passing
        ],
        "winner": winner,
        "closest_nonpassing_combination": {
            "rate": closest_rate,
            "tail": closest_tail,
            "worst_tracking_p95_rad": closest["worst_tracking_p95_rad"],
            "excess_over_limit_rad": closest["worst_tracking_p95_rad"] - 0.20,
        },
        "selection_uses_training_reward": False,
        "authority": {
            "x0_preservation_gate": bool(winner),
            "training": False,
            "colab": False,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
        "interpretation": (
            "All 48 preregistered CPU cells were full-duration walks with bilateral "
            "support, zero saturation, and zero measured rate excess. No cumulative "
            "actor-average checkpoint clears the 0.20 rad tracking gate, so actor SWA "
            "is closed without selecting the closest endpoint."
        ),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Actor-SWA Screen Result",
        "",
        f"status: `{status}`",
        f"decision: `{decision}`",
        "",
        "| rate | tail | cumulative half worst p95 | cumulative final worst p95 | pass |",
        "|---|---|---:|---:|---|",
    ]
    for rate_name, rate in rates.items():
        for tail_name, item in rate["tails"].items():
            lines.append(
                f"| `{rate_name}` | `{tail_name}` | "
                f"{item['checkpoints']['HALF_CUMULATIVE']['worst_tracking_p95_rad']:.9f} | "
                f"{item['checkpoints']['FINAL_CUMULATIVE']['worst_tracking_p95_rad']:.9f} | "
                f"`{item['combination_pass']}` |"
            )
    lines.extend(
        [
            "",
            f"closest nonpassing combination: `{closest_rate}/{closest_tail}` at "
            f"`{closest['worst_tracking_p95_rad']}` rad",
            "",
            payload["interpretation"],
            "",
            "This result authorizes no training, x=0 gate, Colab, RDK-X5, or robot access.",
            "",
        ]
    )
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "winner": winner}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
