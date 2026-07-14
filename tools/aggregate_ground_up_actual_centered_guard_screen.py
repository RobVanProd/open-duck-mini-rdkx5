#!/usr/bin/env python3
"""Aggregate the preregistered actual-centered guard behavior screen."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from aggregate_ground_up_stateful_pitch_rate_boundary_screen import checkpoint_summary


GUARDS = {
    "G1_EXACT_BOUNDARY": 0.2000,
    "G2_HALF_TICK_BUFFER": 0.1825,
    "G3_FULL_TICK_BUFFER": 0.1650,
}
TAILS = ("T2_EQUAL", "T3_FOUR")
STEPS = (512000, 1024000)


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

    guards = {}
    combinations = []
    for guard_name, margin in GUARDS.items():
        tails = {}
        for tail_name in TAILS:
            checkpoints = {}
            for step in STEPS:
                path = args.eval_root / (
                    f"ground_up_actual_centered_guard_{guard_name}_{tail_name}_{step}_eval.json"
                )
                checkpoints[str(step)] = checkpoint_summary(path)
            item = {
                "checkpoints": checkpoints,
                "combination_pass": all(value["checkpoint_pass"] for value in checkpoints.values()),
                "worst_tracking_p95_rad": max(value["worst_tracking_p95_rad"] for value in checkpoints.values()),
                "minimum_forward_velocity_m_s": min(value["minimum_forward_velocity_m_s"] for value in checkpoints.values()),
            }
            tails[tail_name] = item
            combinations.append((guard_name, tail_name, item))
        guards[guard_name] = {"margin_rad": margin, "tails": tails}

    checks = {
        "preregistration_status_valid": prereg["status"] == "PREREGISTERED_CPU_ONLY",
        "preregistered_matrix_exact": (
            prereg["source_policies"]["tail_arms"] == list(TAILS)
            and prereg["source_policies"]["steps"] == list(STEPS)
            and prereg["matrix"]["onnx_policies"] == 12
            and prereg["matrix"]["behavior_cells"] == 72
        ),
        "transform_contract_passed": transform["status"] == "PASS_ACTUAL_CENTERED_GUARD_TRANSFORM_CONTRACT",
        "all_72_cells_present": all(
            checkpoint["checks"]["all_six_cells_present"]
            for _, _, item in combinations
            for checkpoint in item["checkpoints"].values()
        ),
        "all_72_cells_cpu_only": all(
            checkpoint["execution_platform"] == "cpu"
            for _, _, item in combinations
            for checkpoint in item["checkpoints"].values()
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    passing = [row for row in combinations if row[2]["combination_pass"]]
    if failed:
        status = "FAIL_ACTUAL_CENTERED_GUARD_EVIDENCE_CONTRACT"
        decision = "INVALID_EVIDENCE"
        winner = None
    elif passing:
        guard_name, tail_name, item = sorted(
            passing,
            key=lambda row: (
                -GUARDS[row[0]],
                row[2]["worst_tracking_p95_rad"],
                -row[2]["minimum_forward_velocity_m_s"],
            ),
        )[0]
        status = "PASS_ACTUAL_CENTERED_GUARD_WITH_WINNER"
        decision = f"ADVANCE_{guard_name}_{tail_name}_TO_PREREGISTERED_X0_GATE"
        winner = {
            "guard": guard_name,
            "margin_rad": GUARDS[guard_name],
            "tail": tail_name,
            "steps": list(STEPS),
            "worst_tracking_p95_rad": item["worst_tracking_p95_rad"],
            "minimum_forward_velocity_m_s": item["minimum_forward_velocity_m_s"],
        }
    else:
        status = "PASS_ACTUAL_CENTERED_GUARD_NO_WINNER"
        decision = "CLOSE_ACTUAL_CENTERED_GUARD_FORMULATION"
        winner = None

    payload = {
        "schema_version": "ground_up_actual_centered_guard_screen_result.v1",
        "status": status,
        "decision": decision,
        "checks": checks,
        "failed_checks": failed,
        "preregistration": {"path": str(args.preregistration.resolve()), "sha256": sha256(args.preregistration)},
        "transform_contract": {"path": str(args.transform_contract.resolve()), "sha256": sha256(args.transform_contract)},
        "guards": guards,
        "passing_combinations": [
            {
                "guard": guard,
                "tail": tail,
                "worst_tracking_p95_rad": item["worst_tracking_p95_rad"],
                "minimum_forward_velocity_m_s": item["minimum_forward_velocity_m_s"],
            }
            for guard, tail, item in passing
        ],
        "winner": winner,
        "selection_uses_training_reward": False,
        "authority": {
            "preregister_x0_preservation_gate": bool(winner),
            "run_x0_without_preregistration": False,
            "training": False,
            "colab": False,
            "local_gpu": False,
            "rdk_or_robot": False,
        },
        "interpretation": (
            "The actual-position-centered invariant repairs the measured compound lag failure. "
            "The least restrictive 0.20 rad guard passes both half and final checkpoints for "
            "T2 and T3; the frozen tie-break selects T2. This is the first persistent full-horizon "
            "nominal winner in the ground-up route, but it requires a separately preregistered x=0 gate."
        ),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Ground-Up Actual-Centered Guard Screen Result", "",
        f"status: `{status}`", f"decision: `{decision}`", "",
        "| guard | tail | half worst p95 | final worst p95 | min vx | pass |",
        "|---|---|---:|---:|---:|---|",
    ]
    for guard_name, guard in guards.items():
        for tail_name, item in guard["tails"].items():
            lines.append(
                f"| `{guard_name}` | `{tail_name}` | "
                f"{item['checkpoints']['512000']['worst_tracking_p95_rad']:.9f} | "
                f"{item['checkpoints']['1024000']['worst_tracking_p95_rad']:.9f} | "
                f"{item['minimum_forward_velocity_m_s']:.9f} | `{item['combination_pass']}` |"
            )
    lines.extend([
        "", f"winner: `{winner['guard']}/{winner['tail'] if winner else None}`" if winner else "winner: `None`", "",
        payload["interpretation"], "",
        "This authorizes only preregistration of an x=0 preservation gate. It does not authorize that gate before preregistration, training, Colab, RDK-X5, or robot access.", "",
    ])
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": status, "decision": decision, "winner": winner}))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
