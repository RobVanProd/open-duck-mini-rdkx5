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
DEFAULT_PUSH_EFFECTIVENESS_JSON = (
    ROOT / "outputs" / "analysis" / "foot_placement_push_effectiveness_analysis.json"
)
DEFAULT_SAGITTAL_PROPULSION_EFFECTIVENESS_JSON = (
    ROOT
    / "outputs"
    / "analysis"
    / "foot_placement_sagittal_propulsion_effectiveness_analysis.json"
)
DEFAULT_SAGITTAL_SOFTGATE_EFFECTIVENESS_JSON = (
    ROOT
    / "outputs"
    / "analysis"
    / "foot_placement_sagittal_softgate_effectiveness_analysis.json"
)
DEFAULT_STANCE_RELATIVE_EFFECTIVENESS_JSON = (
    ROOT
    / "outputs"
    / "analysis"
    / "foot_placement_stance_relative_lateral_effectiveness_analysis.json"
)
DEFAULT_STANCE_RELATIVE_VELOCITY_CAP_EFFECTIVENESS_JSON = (
    ROOT
    / "outputs"
    / "analysis"
    / "foot_placement_stance_relative_velocity_cap_effectiveness_analysis.json"
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
    push_effectiveness: dict[str, Any],
    sagittal_propulsion_effectiveness: dict[str, Any],
    sagittal_softgate_effectiveness: dict[str, Any],
    stance_relative_effectiveness: dict[str, Any],
    stance_relative_velocity_cap_effectiveness: dict[str, Any],
) -> dict[str, Any]:
    gate_status = status_of(gate)
    failure_status = status_of(failure)
    class_summary = failure.get("class_summary") or {}
    leg100_status = status_of(leg100)
    leg150_status = status_of(leg150)
    push_effectiveness_status = status_of(push_effectiveness)
    push_summary = push_effectiveness.get("aggregate") or {}
    sagittal_propulsion_status = status_of(sagittal_propulsion_effectiveness)
    sagittal_propulsion_summary = sagittal_propulsion_effectiveness.get("aggregate") or {}
    sagittal_softgate_status = status_of(sagittal_softgate_effectiveness)
    sagittal_softgate_summary = sagittal_softgate_effectiveness.get("aggregate") or {}
    stance_relative_status = status_of(stance_relative_effectiveness)
    stance_relative_summary = stance_relative_effectiveness.get("aggregate") or {}
    stance_relative_velocity_cap_status = status_of(
        stance_relative_velocity_cap_effectiveness
    )
    stance_relative_velocity_cap_summary = (
        stance_relative_velocity_cap_effectiveness.get("aggregate") or {}
    )

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
        and sagittal_propulsion_status == "HOLD_PUSH_INEFFECTIVE"
        and sagittal_softgate_status == "HOLD_PUSH_INEFFECTIVE"
        and stance_relative_status == "MISSING"
    ):
        decision = "PLAN_LATERAL_CONTAINED_STANCE_PROPULSION"
        next_branch = (
            "Design a stance propulsion controller with active lateral support "
            "containment. The sagittal stance-feedback primitive creates small "
            "local impulse, but it is not seed robust, and soft gating mostly "
            "removes the impulse."
        )
        rationale = [
            "No checked target source passes PASS_WEIGHT_TRANSFER_TARGET.",
            "The aggregate failure remains HOLD_FORWARD_IMPULSE_PRIMARY with zero rows satisfying stability, support, and forward progress together.",
            "The original foot-placement push measured as ineffective.",
            "The sagittal stance-feedback replacement improved mean future vx delta slightly, but still produced zero seed-robust 100/150 tick modes.",
            "The softgated sagittal follow-up kept the hold and reduced the already-small forward impulse.",
            "This means the missing mechanism is lateral containment that permits propulsion to stay active, not another direct push-amplitude or push-throttle sweep.",
        ]
        stop_rules = [
            "Do not launch PPO/BC from current target sources.",
            "Do not run robot validation, grounded replay, or x=0.08.",
            "Do not widen the same sagittal/softgate grid without adding an active lateral support mechanism.",
            "Require PASS_WEIGHT_TRANSFER_TARGET before training re-entry.",
        ]
    elif (
        failure_status == "HOLD_FORWARD_IMPULSE_PRIMARY"
        and int(class_summary.get("all_three_rows", 0) or 0) == 0
        and stance_relative_velocity_cap_status == "HOLD_PUSH_INEFFECTIVE"
    ):
        decision = "PLAN_STANCE_RELATIVE_LATERAL_DAMPING"
        next_branch = (
            "Keep stance-foot-relative lateral targeting and teacher-side "
            "target-velocity limiting, but add stronger lateral containment "
            "and seed-symmetry shaping. The velocity cap removed the main "
            "actuator-envelope failure from the push-effectiveness read, but "
            "the target gate still fails through lateral velocity and weak "
            "seed-robust forward motion."
        )
        rationale = [
            "No checked target source passes PASS_WEIGHT_TRANSFER_TARGET.",
            "The aggregate failure remains HOLD_FORWARD_IMPULSE_PRIMARY with zero rows satisfying stability, support, and forward progress together.",
            "The stance-relative lateral probe remains the best local direction for forward impulse, but it exceeded lateral and target-velocity gates.",
            "The teacher-side velocity-cap follow-up reduced actuator-envelope pressure while keeping a positive mean future-vx delta.",
            "That capped follow-up still produced zero robust 100/150 tick modes, and every push-effectiveness trace still failed the lateral-velocity check.",
            "The next branch should keep the cap near the measured envelope and attack lateral containment/seed asymmetry; it should not relax the actuator limit or simply increase propulsion.",
        ]
        stop_rules = [
            "Do not launch PPO/BC from current target sources.",
            "Do not run robot validation, grounded replay, or x=0.08.",
            "Do not relax teacher target velocity above the measured envelope to buy forward speed.",
            "Do not widen the same stance-relative grid without adding lateral containment or seed-symmetry mechanisms.",
            "Require PASS_WEIGHT_TRANSFER_TARGET before training re-entry.",
        ]
    elif (
        failure_status == "HOLD_FORWARD_IMPULSE_PRIMARY"
        and int(class_summary.get("all_three_rows", 0) or 0) == 0
        and stance_relative_status == "HOLD_PUSH_INEFFECTIVE"
        and float(
            stance_relative_summary.get("mean_push_future_vx_delta_m_s") or 0.0
        )
        > float(sagittal_propulsion_summary.get("mean_push_future_vx_delta_m_s") or 0.0)
    ):
        decision = "PLAN_STANCE_RELATIVE_PROPULSION_SHAPING"
        next_branch = (
            "Keep the stance-foot-relative lateral target as the promising "
            "direction, but shape it to satisfy lateral and actuator gates. "
            "It increased forward impulse and raw rollout speed, but still "
            "fails the target gate through lateral velocity and target-velocity "
            "violations."
        )
        rationale = [
            "No checked target source passes PASS_WEIGHT_TRANSFER_TARGET.",
            "The aggregate failure remains HOLD_FORWARD_IMPULSE_PRIMARY with zero rows satisfying stability, support, and forward progress together.",
            "Stance-foot-relative lateral targeting increased push scheduling and mean future vx delta beyond the sagittal-only variant.",
            "The 100/150 tick scores still found zero robust modes, with high lateral velocity and high sent target velocity dominating.",
            "This is evidence for a usable direction, not training permission: the next branch should shape the stance-relative controller inside lateral and actuator limits.",
        ]
        stop_rules = [
            "Do not launch PPO/BC from current target sources.",
            "Do not run robot validation, grounded replay, or x=0.08.",
            "Do not increase stance-relative propulsion before target velocity and lateral velocity are bounded.",
            "Require PASS_WEIGHT_TRANSFER_TARGET before training re-entry.",
        ]
    elif (
        failure_status == "HOLD_FORWARD_IMPULSE_PRIMARY"
        and int(class_summary.get("all_three_rows", 0) or 0) == 0
        and push_effectiveness_status == "HOLD_PUSH_INEFFECTIVE"
    ):
        decision = "PLAN_REPLACE_STANCE_PROPULSION_PRIMITIVE"
        next_branch = (
            "Design a new stance-support propulsion primitive. The existing "
            "foot-placement push is present often enough to evaluate, but it "
            "does not create reliable forward acceleration and couples into "
            "lateral velocity."
        )
        rationale = [
            "No checked target source passes PASS_WEIGHT_TRANSFER_TARGET.",
            "The aggregate failure remains HOLD_FORWARD_IMPULSE_PRIMARY with zero rows satisfying stability, support, and forward progress together.",
            "The corrected relative-yaw recovery probe showed high switch readiness, so yaw-gate measurement is not the primary blocker.",
            "The push-effectiveness analyzer measured the current push primitive as HOLD_PUSH_INEFFECTIVE.",
            "This means the next branch should change the propulsion mechanism under stance support, not make the same pitch-chain push earlier, later, or more frequent.",
        ]
        stop_rules = [
            "Do not launch PPO/BC from current target sources.",
            "Do not run robot validation, grounded replay, or x=0.08.",
            "Do not widen the same push/advance/clearance/yaw/recovery grid.",
            "Require PASS_WEIGHT_TRANSFER_TARGET before training re-entry.",
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
            "push_effectiveness_status": push_effectiveness_status,
            "push_mean_allowed_pct": push_summary.get("mean_push_allowed_pct"),
            "push_mean_future_vx_delta_m_s": push_summary.get(
                "mean_push_future_vx_delta_m_s"
            ),
            "sagittal_propulsion_status": sagittal_propulsion_status,
            "sagittal_propulsion_mean_future_vx_delta_m_s": (
                sagittal_propulsion_summary.get("mean_push_future_vx_delta_m_s")
            ),
            "sagittal_propulsion_pass_count": (
                sagittal_propulsion_summary.get("status_counts", {}).get(
                    "PASS_PUSH_EFFECTIVE"
                )
            ),
            "sagittal_softgate_status": sagittal_softgate_status,
            "sagittal_softgate_mean_future_vx_delta_m_s": (
                sagittal_softgate_summary.get("mean_push_future_vx_delta_m_s")
            ),
            "sagittal_softgate_pass_count": (
                sagittal_softgate_summary.get("status_counts", {}).get(
                    "PASS_PUSH_EFFECTIVE"
                )
            ),
            "stance_relative_status": stance_relative_status,
            "stance_relative_mean_future_vx_delta_m_s": (
                stance_relative_summary.get("mean_push_future_vx_delta_m_s")
            ),
            "stance_relative_pass_count": (
                stance_relative_summary.get("status_counts", {}).get(
                    "PASS_PUSH_EFFECTIVE"
                )
            ),
            "stance_relative_velocity_cap_status": stance_relative_velocity_cap_status,
            "stance_relative_velocity_cap_mean_future_vx_delta_m_s": (
                stance_relative_velocity_cap_summary.get(
                    "mean_push_future_vx_delta_m_s"
                )
            ),
            "stance_relative_velocity_cap_pass_count": (
                stance_relative_velocity_cap_summary.get("status_counts", {}).get(
                    "PASS_PUSH_EFFECTIVE"
                )
            ),
        },
        "rationale": rationale,
        "required_next_design": [
            "stateful stance-side selection",
            "explicit lateral body placement over the stance foot",
            "swing-foot placement and clearance objective",
            "active lateral containment while stance propulsion remains enabled",
            "stance-support propulsion that is not only a direct push-amplitude increase",
            "teacher-side target-velocity limiting near the measured actuator envelope",
            "stronger lateral velocity, roll, and base-y drift penalties",
            "seed-symmetry shaping so seed 0 does not stay weak while seed 2 moves",
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
    parser.add_argument("--push-effectiveness-json", default=str(DEFAULT_PUSH_EFFECTIVENESS_JSON))
    parser.add_argument(
        "--sagittal-propulsion-effectiveness-json",
        default=str(DEFAULT_SAGITTAL_PROPULSION_EFFECTIVENESS_JSON),
    )
    parser.add_argument(
        "--sagittal-softgate-effectiveness-json",
        default=str(DEFAULT_SAGITTAL_SOFTGATE_EFFECTIVENESS_JSON),
    )
    parser.add_argument(
        "--stance-relative-effectiveness-json",
        default=str(DEFAULT_STANCE_RELATIVE_EFFECTIVENESS_JSON),
    )
    parser.add_argument(
        "--stance-relative-velocity-cap-effectiveness-json",
        default=str(DEFAULT_STANCE_RELATIVE_VELOCITY_CAP_EFFECTIVENESS_JSON),
    )
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    payload = decide(
        load_json(Path(args.gate_json)),
        load_json(Path(args.failure_json)),
        load_json(Path(args.leg_extension_100_json)),
        load_json(Path(args.leg_extension_150_json)),
        load_json(Path(args.push_effectiveness_json)),
        load_json(Path(args.sagittal_propulsion_effectiveness_json)),
        load_json(Path(args.sagittal_softgate_effectiveness_json)),
        load_json(Path(args.stance_relative_effectiveness_json)),
        load_json(Path(args.stance_relative_velocity_cap_effectiveness_json)),
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
