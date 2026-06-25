#!/usr/bin/env python3
"""Decide the next offline weight-transfer branch from compact evidence.

This is a planning/evidence tool. It does not run simulation, training, robot
SSH, deployment, or hardware tests. It reads the current target-gate artifacts
and emits one explicit next branch so the project does not reopen already
failed local teacher variants by accident.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GATE_JSON = ROOT / "outputs" / "analysis" / "weight_transfer_target_gate_check.json"
DEFAULT_FAILURE_JSON = (
    ROOT / "outputs" / "analysis" / "weight_transfer_gate_failure_analysis.json"
)
DEFAULT_LEG_EXTENSION_100_JSON = (
    ROOT / "outputs" / "analysis" / "closed_loop_weight_transfer_teacher_leg_extension_score_100.json"
)
DEFAULT_LEG_EXTENSION_150_JSON = (
    ROOT / "outputs" / "analysis" / "closed_loop_weight_transfer_teacher_leg_extension_score_150.json"
)
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "NEXT_WEIGHT_TRANSFER_BRANCH.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "next_weight_transfer_branch.json"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"missing": True, "path": str(path)}
    return json.loads(path.read_text())


def status_of(payload: dict[str, Any]) -> str:
    if payload.get("missing"):
        return "MISSING"
    return str(payload.get("status") or "UNKNOWN")


def robust_count(payload: dict[str, Any]) -> int | None:
    value = payload.get("robust_mode_count")
    return int(value) if isinstance(value, int | float) else None


def decide(
    gate: dict[str, Any],
    failure: dict[str, Any],
    leg100: dict[str, Any],
    leg150: dict[str, Any],
) -> dict[str, Any]:
    gate_status = status_of(gate)
    failure_status = status_of(failure)
    class_summary = failure.get("class_summary") or {}
    leg100_status = status_of(leg100)
    leg150_status = status_of(leg150)

    if gate_status == "PASS_WEIGHT_TRANSFER_TARGET":
        decision = "PROCEED_TARGET_DATASET_SMOKE"
        next_branch = "Build a compact target manifest and run CPU replay before any training."
        rationale = [
            "A target source has cleared the documented 100-150 tick gate.",
            "This still does not authorize robot validation.",
        ]
        stop_rules = [
            "Do not train until the exact passing source and seeds are reviewed.",
            "Do not run robot validation from this artifact alone.",
        ]
    elif (
        failure_status == "HOLD_FORWARD_IMPULSE_PRIMARY"
        and int(class_summary.get("all_three_rows", 0) or 0) == 0
        and leg100_status == "HOLD_NO_SEED_ROBUST_TARGETS"
        and leg150_status == "HOLD_NO_SEED_ROBUST_TARGETS"
    ):
        decision = "PLAN_FOOT_PLACEMENT_MPC_TEACHER"
        next_branch = (
            "Design a finite-horizon state-feedback teacher/optimizer that chooses "
            "stance side, lateral body placement, swing-foot placement, and forward "
            "push timing together."
        )
        rationale = [
            "No checked target source passes PASS_WEIGHT_TRANSFER_TARGET.",
            "Forward-ready rows are rare, and no row satisfies stability, support, and forward progress together.",
            "The default-off stance knee/ankle push-off probe also held, so the missing mechanism is not a local distal push term inside the existing support-state teacher.",
            "Existing rows show support/contact can improve, but usable forward impulse remains coupled to lateral velocity or pitch margin.",
        ]
        stop_rules = [
            "Do not launch PPO/BC from current target sources.",
            "Do not run robot validation, grounded replay, or x=0.08.",
            "Do not widen the same local teacher grid unless a new state variable or objective is added.",
            "Require PASS_WEIGHT_TRANSFER_TARGET before training re-entry.",
        ]
    elif failure_status == "HOLD_FORWARD_IMPULSE_PRIMARY":
        decision = "REVIEW_LOCAL_TEACHER_EVIDENCE"
        next_branch = (
            "Review missing or stale local teacher evidence before picking the next branch."
        )
        rationale = [
            "The failure analysis points at forward impulse, but supporting local probe evidence is incomplete or stale.",
        ]
        stop_rules = [
            "Do not train or run robot tests while the branch decision is under-evidenced.",
        ]
    else:
        decision = "HOLD_INSUFFICIENT_DECISION_EVIDENCE"
        next_branch = "Regenerate the target gate and failure analysis artifacts."
        rationale = [
            "The current artifact statuses do not match a known branch decision.",
        ]
        stop_rules = [
            "Do not train or run robot tests until the gate artifacts are regenerated.",
        ]

    return {
        "status": decision,
        "next_branch": next_branch,
        "inputs": {
            "gate_status": gate_status,
            "gate_artifacts": len(gate.get("files") or []),
            "failure_status": failure_status,
            "seed_rows_scanned": class_summary.get("rows"),
            "stable_actuator_rows": class_summary.get("stable_actuator_rows"),
            "support_ready_rows": class_summary.get("support_ready_rows"),
            "forward_ready_rows": class_summary.get("forward_ready_rows"),
            "stable_and_support_rows": class_summary.get("stable_and_support_rows"),
            "stable_and_forward_rows": class_summary.get("stable_and_forward_rows"),
            "support_and_forward_rows": class_summary.get("support_and_forward_rows"),
            "all_three_rows": class_summary.get("all_three_rows"),
            "leg_extension_100_status": leg100_status,
            "leg_extension_100_robust_modes": robust_count(leg100),
            "leg_extension_150_status": leg150_status,
            "leg_extension_150_robust_modes": robust_count(leg150),
        },
        "rationale": rationale,
        "required_next_design": [
            "stateful stance-side selection",
            "explicit lateral body placement over the stance foot",
            "swing-foot placement and clearance objective",
            "forward push timed after support loading",
            "lateral velocity and base-y drift penalties",
            "pitch and base-height guards",
            "measured actuator-envelope scoring",
            "100-150 tick seed-robust PASS_WEIGHT_TRANSFER_TARGET gate",
        ],
        "stop_rules": stop_rules,
        "non_goals": [
            "robot tests",
            "SSH or deployment",
            "grounded replay",
            "policy/runtime changes",
            "PPO/BC before target gate pass",
            "another nearby scalar teacher-grid expansion",
        ],
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    inputs = payload["inputs"]
    lines = [
        "# Next Weight-Transfer Branch Decision",
        "",
        f"status: `{payload['status']}`",
        "",
        "This is an offline planning artifact. It does not run simulation,",
        "training, robot SSH, deployment, or hardware tests.",
        "",
        "## Input Evidence",
        "",
        "| field | value |",
        "|---|---:|",
    ]
    for key, value in inputs.items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            payload["next_branch"],
            "",
            "## Rationale",
            "",
        ]
    )
    for item in payload["rationale"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Required Next Design", ""])
    for item in payload["required_next_design"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Stop Rules", ""])
    for item in payload["stop_rules"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Non-Goals", ""])
    for item in payload["non_goals"]:
        lines.append(f"- {item}")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate-json", default=str(DEFAULT_GATE_JSON))
    parser.add_argument("--failure-json", default=str(DEFAULT_FAILURE_JSON))
    parser.add_argument("--leg-extension-100-json", default=str(DEFAULT_LEG_EXTENSION_100_JSON))
    parser.add_argument("--leg-extension-150-json", default=str(DEFAULT_LEG_EXTENSION_150_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    payload = decide(
        load_json(Path(args.gate_json)),
        load_json(Path(args.failure_json)),
        load_json(Path(args.leg_extension_100_json)),
        load_json(Path(args.leg_extension_150_json)),
    )
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(f"status={payload['status']}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
