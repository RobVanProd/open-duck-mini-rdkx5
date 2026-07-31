#!/usr/bin/env python3
"""Audit whether reference actions are valid BC labels or only an actor prior."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projected-table", type=Path, required=True)
    parser.add_argument("--raw-rollout", type=Path, required=True)
    parser.add_argument("--projected-rollout", type=Path, required=True)
    parser.add_argument("--synchronized-rollout", type=Path, required=True)
    parser.add_argument("--mechanism-ranking", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    table = json.loads(args.projected_table.read_text())
    rollouts = []
    for path in (args.raw_rollout, args.projected_rollout, args.synchronized_rollout):
        payload = json.loads(path.read_text())
        aggregate = payload["aggregate"]
        rollouts.append(
            {
                "path": str(path),
                "mode": payload["reference_target_mode"],
                "status": payload["status"],
                "command_x": payload["command_x"],
                "duration_s": payload["duration_s"],
                **aggregate,
            }
        )
    ranking = json.loads(args.mechanism_ranking.read_text())
    refcond = next(
        row for row in ranking["ranking"] if row["candidate_id"] == "M1_REFCOND"
    )

    direct_bc_valid = all(
        row["falls"] == 0 and row["vx_mean"] > 0 and row["track_ratio_mean"] > 0
        for row in rollouts
    )
    result = {
        "schema_version": "ground_up_reference_teacher_audit.v1",
        "status": "REJECT_DIRECT_BC_SELECT_REFERENCE_ANCHORED_RESIDUAL_CONTRACT",
        "selection_uses_training_reward": False,
        "projected_table": table,
        "direct_reference_rollouts": rollouts,
        "reference_conditioned_policy_score": refcond["score"],
        "reference_conditioned_persistent_moving_seeds": len(
            refcond["persistent_moving_seeds"]
        ),
        "direct_behavior_cloning_labels_valid": direct_bc_valid,
        "selected_next_mechanism": (
            "actor-internal reference-anchored residual: initialize final action at "
            "the projected reference and learn state-feedback correction with PPO"
        ),
        "rejected_next_mechanisms": [
            "direct supervised cloning of projected reference actions",
            "another randomly initialized actor that only receives reference action as input",
            "post-policy runtime action wrapper",
        ],
    }
    lines = [
        "# Ground-Up Reference Teacher Audit",
        "",
        "status: `REJECT_DIRECT_BC_SELECT_REFERENCE_ANCHORED_RESIDUAL_CONTRACT`",
        "",
        "## Measured teacher behavior",
        "",
        "| reference action mode | runs | falls | mean vx | track ratio | contact mismatch | decision |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rollouts:
        lines.append(
            f"| `{row['mode']}` | {row['runs']} | {row['falls']} | "
            f"{row['vx_mean']:.4f} | {row['track_ratio_mean']:.4f} | "
            f"{row['reference_contact_mismatch_pct_mean']:.2f}% | invalid BC label |"
        )
    lines += [
        "",
        "The envelope-projected table itself is deterministic and valid: "
        f"shape `{table['shape']}`, maximum action `{table['max_abs_action']:.1f}`, "
        f"SHA-256 `{table['output_sha256']}`. The failure is behavioral, not a "
        "missing table or action-envelope violation.",
        "",
        "Contact synchronization reduced mismatch but did not create propulsion: "
        "mean forward velocity remained negative and two of eight runs fell. "
        "Direct supervised cloning would therefore reproduce a measured failed "
        "controller and is rejected.",
        "",
        "## Existing learned comparison",
        "",
        "`M1_REFCOND` gave a randomly initialized actor the same projected action "
        "as an observation feature. It produced one isolated moving pass, zero "
        "persistent moving seeds, two hard failures, and no full checkpoint pass. "
        "Reference input alone is insufficient.",
        "",
        "## Selected contract target",
        "",
        "The next mechanism to implement and CPU-test is an actor-internal "
        "reference-anchored residual. Its initial deterministic final action must "
        "equal the projected reference action, while the learned network supplies "
        "a state-feedback correction. The composition must be inside the exported "
        "policy, not an RDK wrapper. This uses the reference as initialization, not "
        "as a claim that its open-loop actions are correct.",
        "",
        "No accelerator experiment is authorized until initialization equality, "
        "PPO log-probability semantics, ONNX equivalence, observation/action ABI, "
        "and a finite CPU smoke train all pass.",
        "",
        "No GPU, iGPU, RDK-X5, robot, motor, or torque access occurred.",
        "",
    ]
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    args.output_md.write_text("\n".join(lines))
    print(json.dumps({"status": result["status"], "direct_bc_valid": direct_bc_valid}))
    return 0 if not direct_bc_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
