#!/usr/bin/env python3
"""Pre-register the on-policy teacher-continuity branch after Stage A.

This planner records measured inputs, the default-off mechanism, data gates,
acceptance gates, and falsifiers.  It does not train, deploy, SSH, or touch the
robot.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULT = ROOT / "outputs/analysis/PHASE2_STAGE_A_RATE175_20260711_RESULT.md"
DEFAULT_COMPARISON = (
    ROOT / "outputs/analysis/phase2_stage_a_rate175_step163840_onpolicy_prior_comparison.json"
)
DEFAULT_POLICY = (
    ROOT
    / "outputs/analysis/colab_cli_stage_a_rate175_prior"
    / "open-duck-t4-stagea-phase2-stage-a-narrow-20260711T020114Z"
    / "artifact/open_duck_colab_cli_phase2-stage-a-narrow_20260711T020137Z"
    / "open_duck_training_phase2_stage_a_narrow_cli/smoke_20260711T020210Z_gpu"
    / "2026_07_11_021603_163840.onnx"
)
DEFAULT_TEACHER = (
    ROOT
    / "outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate"
    / "candidate_mlp.npz"
)
JOINT_WEIGHTS = [0.25, 0.5, 1.0, 2.0, 2.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.5, 1.0, 2.0, 2.0]


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.is_file() else {}


def build_payload(args: argparse.Namespace) -> dict:
    comparison_path = Path(args.comparison)
    comparison = load_json(comparison_path)
    stage_policy = next(
        (
            item
            for item in comparison.get("policies", [])
            if item.get("policy_name") == "2026_07_11_021603_163840"
        ),
        {},
    )
    by_joint = stage_policy.get("teacher_delta_abs_by_joint") or {}
    ranked = sorted(
        (
            {"joint": joint, "mean": stats.get("mean"), "p95": stats.get("p95")}
            for joint, stats in by_joint.items()
        ),
        key=lambda item: float(item.get("p95") or 0.0),
        reverse=True,
    )
    policy = Path(args.policy)
    teacher = Path(args.teacher)
    return {
        "status": "PASS_ONPOLICY_CONTINUITY_RECIPE_PRE_REGISTERED_DATA_GATE_OPEN",
        "training_authorized": False,
        "robot_authorized": False,
        "diagnosis": {
            "stage_a_status": "HOLD_STAGE_A_TRACKING_GATE",
            "best_checkpoint_step": 163840,
            "compact_x008_mean_vx_m_s": 0.0298,
            "compact_x008_track_ratio": 0.3724,
            "compact_x008_tracking_p95_rad": 0.2177,
            "seed0_fullobs_tracking_p95_rad": 0.2384,
            "onpolicy_teacher_delta_mean": (stage_policy.get("teacher_delta_abs") or {}).get("mean"),
            "onpolicy_teacher_delta_p95": (stage_policy.get("teacher_delta_abs") or {}).get("p95"),
            "ranked_joint_teacher_delta": ranked,
            "interpretation": (
                "The global policy remains close to the teacher, but small on-policy "
                "pitch-chain deviations coincide with the tracking hold. Constrain "
                "those joints on visited states instead of increasing a uniform scalar."
            ),
        },
        "inputs": {
            "stage_a_result": relative(Path(args.stage_a_result)),
            "stage_a_policy": {"path": relative(policy), "sha256": sha256(policy)},
            "teacher_mlp": {"path": relative(teacher), "sha256": sha256(teacher)},
            "onpolicy_comparison": relative(comparison_path),
        },
        "mechanism": {
            "name": "joint_weighted_onpolicy_teacher_continuity",
            "default_off": True,
            "joint_weights_action_order": JOINT_WEIGHTS,
            "joint_weight_csv": ",".join(str(value) for value in JOINT_WEIGHTS),
            "teacher_source": "frozen rate175 command-conditioned MLP queried on PPO-visited observations",
            "scope": "behavior-prior auxiliary cost only; no runtime or robot change",
        },
        "data_gate_before_training": [
            "Collect full-observation x=0.08 corrected-bridge traces for seeds 0-7 from step 163840.",
            "Confirm knee/ankle or hip-pitch teacher deltas dominate tracking-damage windows across at least 6/8 seeds.",
            "Confirm teacher relabel target-rate p95 stays <= 1.75 rad/s and max <= 2.0 rad/s.",
            "Confirm no required teacher correction exceeds 0.25 normalized action on any pitch-chain joint.",
            "Run a default-off and uniform-weight CPU wiring parity check before any GPU allocation.",
        ],
        "first_training_smoke_if_data_gate_passes": {
            "restore": "Stage A step 163840 checkpoint directory is unavailable; use the original rate175 restore checkpoint and pre-register equivalent initialization evidence before launch.",
            "timesteps": 40960,
            "restore_policy_kl_scale": 4.0,
            "behavior_prior_scale": -0.6,
            "behavior_prior_huber_delta": 0.05,
            "behavior_prior_joint_weights": JOINT_WEIGHTS,
            "all_other_stage_a_settings": "frozen",
            "note": "Only the joint weighting may change in the first causal smoke.",
        },
        "acceptance": [
            "Compact x=0.0 remains PASS_CANDIDATE_SIM_GATE.",
            "Compact x=0.08 tracking p95 <= 0.20 rad.",
            "Compact x=0.08 mean vx >= 0.0298 m/s and tracking ratio >= 0.3724.",
            "Pitch-chain sent-target velocity p95 remains within [2.0, 3.25] rad/s envelope and action saturation remains zero.",
            "Only after compact acceptance: full 15 s x=0.0 and x=0.08 corrected-bridge seeds 0-7, with no falls and no regression from the teacher full-gate mean vx 0.0339 m/s / ratio 0.4238.",
        ],
        "falsifier": (
            "If the weighted smoke remains above 0.20 rad tracking p95 or loses the "
            "Stage A forward-progress floor, stop behavior-prior/KL tuning. The next "
            "branch must change the teacher target manifold or actuator objective, not "
            "the scalar or joint weights."
        ),
    }


def write_markdown(payload: dict, path: Path) -> None:
    diagnosis = payload["diagnosis"]
    lines = [
        "# Phase 2 Stage A On-Policy Continuity Recipe",
        "",
        f"status: `{payload['status']}`",
        f"training_authorized: `{payload['training_authorized']}`",
        f"robot_authorized: `{payload['robot_authorized']}`",
        "",
        "This is an offline pre-registration artifact. It did not train, deploy, SSH, use a local GPU, or touch the robot.",
        "",
        "## Diagnosis",
        "",
        f"- Stage A best step: `{diagnosis['best_checkpoint_step']}`",
        f"- compact x=0.08: vx `{diagnosis['compact_x008_mean_vx_m_s']}` m/s, ratio `{diagnosis['compact_x008_track_ratio']}`, tracking p95 `{diagnosis['compact_x008_tracking_p95_rad']}` rad",
        f"- seed-0 full-observation tracking p95: `{diagnosis['seed0_fullobs_tracking_p95_rad']}` rad",
        f"- on-policy teacher delta mean/p95: `{diagnosis['onpolicy_teacher_delta_mean']}` / `{diagnosis['onpolicy_teacher_delta_p95']}` normalized action",
        f"- interpretation: {diagnosis['interpretation']}",
        "",
        "### Largest On-Policy Teacher Deltas",
        "",
        "| joint | mean | p95 |",
        "|---|---:|---:|",
    ]
    for item in diagnosis["ranked_joint_teacher_delta"][:8]:
        lines.append(f"| `{item['joint']}` | {item['mean']:.4f} | {item['p95']:.4f} |")
    lines += ["", "## Mechanism", ""]
    lines += [f"- `{key}`: `{value}`" for key, value in payload["mechanism"].items()]
    lines += ["", "## Data Gate Before Training", ""]
    lines += [f"- {item}" for item in payload["data_gate_before_training"]]
    lines += ["", "## First Causal Smoke If Data Gate Passes", ""]
    lines += [f"- `{key}`: `{value}`" for key, value in payload["first_training_smoke_if_data_gate_passes"].items()]
    lines += ["", "## Acceptance", ""]
    lines += [f"- {item}" for item in payload["acceptance"]]
    lines += ["", "## Falsifier", "", payload["falsifier"], ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage-a-result", default=str(DEFAULT_RESULT))
    parser.add_argument("--comparison", default=str(DEFAULT_COMPARISON))
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--teacher", default=str(DEFAULT_TEACHER))
    parser.add_argument(
        "--output-md",
        default=str(ROOT / "outputs/analysis/PHASE2_STAGE_A_ONPOLICY_CONTINUITY_RECIPE.md"),
    )
    parser.add_argument(
        "--output-json",
        default=str(ROOT / "outputs/analysis/phase2_stage_a_onpolicy_continuity_recipe.json"),
    )
    args = parser.parse_args()
    payload = build_payload(args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
