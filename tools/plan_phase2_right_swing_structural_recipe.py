#!/usr/bin/env python3
"""Plan the Phase 2 right-swing structural envelope branch.

This is a read-only planning/preflight tool. It consumes the phase-primary
swing-clearance diagnostic and records the next offline recipe after the
right leg was classified as STRUCTURAL/envelope-pressed while the left leg
remained mostly latency-limited.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIAGNOSTIC = (
    ROOT / "outputs/analysis/phase2_swing_clearance_diagnostic_z0024.json"
)
DEFAULT_OUTPUT_MD = (
    ROOT / "outputs/analysis/PHASE2_RIGHT_SWING_STRUCTURAL_NEXT_RECIPE.md"
)
DEFAULT_OUTPUT_JSON = (
    ROOT / "outputs/analysis/phase2_right_swing_structural_next_recipe.json"
)
PLAYGROUND_ROOT = ROOT.parent / "Open_Duck_Playground"
JOYSTICK_PATH = PLAYGROUND_ROOT / "playground/open_duck_mini_v2/joystick.py"
RUNNER_PATH = PLAYGROUND_ROOT / "playground/open_duck_mini_v2/runner.py"
REWARDS_PATH = PLAYGROUND_ROOT / "playground/common/rewards.py"
SMOKE_WRAPPER = ROOT / "tools/run_actuator_bridge_training_smoke.py"

RIGHT_PITCH_CHAIN_INDICES = "11,12,13"
RIGHT_PITCH_CHAIN_LIMITS = "2.25,2.75,2.00"


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def text_has(path: Path, needles: list[str]) -> dict[str, bool]:
    if not path.exists():
        return {needle: False for needle in needles}
    text = path.read_text(errors="replace")
    return {needle: needle in text for needle in needles}


def audit_target_rate_hook() -> dict[str, Any]:
    needles = [
        "forward_swing_target_rate_limit",
        "--forward_swing_target_rate_limit_scale",
        "--forward-swing-target-rate-limit-scale",
    ]
    files = {
        "joystick": JOYSTICK_PATH,
        "runner": RUNNER_PATH,
        "rewards": REWARDS_PATH,
        "smoke_wrapper": SMOKE_WRAPPER,
    }
    evidence = {name: text_has(path, needles) for name, path in files.items()}
    required = {
        "joystick": "forward_swing_target_rate_limit",
        "runner": "--forward_swing_target_rate_limit_scale",
        "rewards": "forward_swing_target_rate_limit",
        "smoke_wrapper": "--forward-swing-target-rate-limit-scale",
    }
    missing = [
        name
        for name, needle in required.items()
        if not evidence.get(name, {}).get(needle)
    ]
    return {
        "status": (
            "PASS_TARGET_RATE_HOOK_PRESENT"
            if not missing
            else "HOLD_TARGET_RATE_HOOK_MISSING"
        ),
        "hook_present": not missing,
        "missing": missing,
        "files": {name: rel(path) for name, path in files.items()},
        "evidence": evidence,
    }


def summarize_diagnostic(diagnostic: dict[str, Any]) -> dict[str, Any]:
    aggregate = diagnostic.get("aggregate_verdict") or {}
    right_rows = []
    left_rows = []
    for seed in diagnostic.get("seed_results") or []:
        side_results = seed.get("side_results") or {}
        for side, rows in (("left", left_rows), ("right", right_rows)):
            item = side_results.get(side) or {}
            rows.append(
                {
                    "seed": seed.get("seed"),
                    "classification": item.get("classification"),
                    "rate_utilization_peak": item.get("rate_utilization_peak"),
                    "achieved_to_ceiling_ratio_peak": item.get(
                        "achieved_to_ceiling_ratio_peak"
                    ),
                    "planted_pct_during_phase_swing": item.get(
                        "planted_pct_during_phase_swing"
                    ),
                    "rate_driver_joint": item.get("rate_driver_joint"),
                    "rate_utilization_by_joint_peak": item.get(
                        "rate_utilization_by_joint_peak"
                    ),
                }
            )
    return {
        "status": diagnostic.get("status"),
        "verdict": aggregate.get("verdict"),
        "side_verdicts": aggregate.get("side_verdicts"),
        "side_classification_counts": aggregate.get("side_classification_counts"),
        "rate_driver_joint_counts": aggregate.get("rate_driver_joint_counts"),
        "selected_fix_branch": aggregate.get("selected_fix_branch"),
        "candidate": diagnostic.get("inputs", {}).get("candidate"),
        "candidate_sha256": diagnostic.get("inputs", {}).get("candidate_sha256"),
        "corrected_bridge": diagnostic.get("inputs", {}).get("corrected_bridge")
        or diagnostic.get("inputs", {}).get("fit_json"),
        "corrected_bridge_sha256": diagnostic.get("inputs", {}).get(
            "corrected_bridge_sha256"
        )
        or diagnostic.get("inputs", {}).get("fit_json_sha256"),
        "command_x": diagnostic.get("inputs", {}).get("command_x"),
        "terrain_hfield_z_scale": diagnostic.get("inputs", {}).get(
            "terrain_hfield_z_scale"
        ),
        "right_rows": right_rows,
        "left_rows": left_rows,
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    diagnostic_path = Path(args.diagnostic)
    diagnostic = read_json(diagnostic_path)
    summary = summarize_diagnostic(diagnostic)
    hook = audit_target_rate_hook()
    right_structural = summary["side_verdicts"].get("right") == "STRUCTURAL"
    left_latency = summary["side_verdicts"].get("left") == "LATENCY_LIMITED"
    if right_structural and hook["hook_present"]:
        status = "PASS_RIGHT_SWING_STRUCTURAL_RECIPE_READY"
    elif right_structural:
        status = "HOLD_TARGET_RATE_HOOK_MISSING"
    else:
        status = "HOLD_DIAGNOSTIC_NOT_RIGHT_STRUCTURAL"
    train_command = [
        "python3",
        "tools/run_actuator_bridge_training_smoke.py",
        "--platform",
        "gpu",
        "--run",
        "--task",
        "rough_terrain_backlash",
        "--restore-checkpoint-path",
        "outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520",
        "--terrain-hfield-z-scale",
        "0.0024",
        "--forward-swing-target-rate-limit-scale",
        "-0.0025",
        "--forward-swing-target-rate-limit-joint-indices",
        RIGHT_PITCH_CHAIN_INDICES,
        "--forward-swing-target-rate-limit-values",
        RIGHT_PITCH_CHAIN_LIMITS,
        "--forward-swing-target-rate-limit-huber-delta",
        "0.05",
        "--forward-swing-clearance-scale",
        "-0.00025",
        "--forward-swing-clearance-target-m",
        "0.016",
        "--forward-swing-advance-scale",
        "-0.001",
        "--forward-swing-advance-target-m",
        "0.004",
    ]
    colab_command = [
        "python3",
        "tools/run_colab_cli_cuda_workflow.py",
        "--workflow",
        "phase2-right-swing-structural",
        "--run",
        "--timeout-s",
        "14400",
    ]
    return {
        "status": status,
        "stage": "phase2_right_swing_structural",
        "diagnostic": {
            "path": rel(diagnostic_path),
            "sha256": sha256_file(diagnostic_path),
            **summary,
        },
        "hook_audit": hook,
        "right_leg_structural": right_structural,
        "left_leg_latency_limited": left_latency,
        "recipe_intent": [
            "Do not run global smoothing or global phase advance.",
            "Target only the right pitch chain because the diagnostic shows right R > 1 on all seeds.",
            "Use the corrected per-joint right pitch-chain limits as the training cost reference.",
            "Treat the new cost as a small, default-off structural guard, not as a relaxed gate.",
            "After any training, gate with corrected p95 and max per-joint velocity checks.",
            "Rerun the swing-clearance diagnostic before promoting any candidate.",
        ],
        "train_command": train_command,
        "colab_workflow_command": colab_command,
        "acceptance": [
            "x=0.08 z=0.0024 corrected-bridge gate remains 8/8.",
            "x=0.0 corrected-bridge gate remains 8/8 with command semantics preserved.",
            "No per-joint corrected envelope excess in p95 or max target velocity.",
            "Right-leg swing diagnostic no longer reports STRUCTURAL from R > 1.",
            "Left latency is not made worse; defer left-specific phase advance until right structural excess is gone.",
        ],
        "falsifiers": [
            "If right R stays > 1, stop right-swing label weighting and change gait duration or geometry.",
            "If target-rate cost removes forward motion, reject the recipe as another smoothing trap.",
            "If only p95 passes while max per-joint spikes remain, reject the candidate.",
        ],
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    diagnostic = payload["diagnostic"]
    hook = payload["hook_audit"]
    lines = [
        "# Phase 2 Right-Swing Structural Next Recipe",
        "",
        f"status: `{payload['status']}`",
        f"stage: `{payload['stage']}`",
        "",
        "This is an offline planning artifact. It did not train, SSH, deploy, or touch the robot.",
        "",
        "## Diagnostic Input",
        "",
        f"- diagnostic: `{diagnostic['path']}`",
        f"- diagnostic_sha256: `{diagnostic['sha256']}`",
        f"- verdict: `{diagnostic['verdict']}`",
        f"- side_verdicts: `{diagnostic['side_verdicts']}`",
        f"- side_classification_counts: `{diagnostic['side_classification_counts']}`",
        f"- rate_driver_joint_counts: `{diagnostic['rate_driver_joint_counts']}`",
        f"- selected_fix_branch: `{diagnostic['selected_fix_branch']}`",
        f"- candidate: `{diagnostic['candidate']}`",
        f"- candidate_sha256: `{diagnostic['candidate_sha256']}`",
        f"- corrected_bridge: `{diagnostic['corrected_bridge']}`",
        f"- corrected_bridge_sha256: `{diagnostic['corrected_bridge_sha256']}`",
        f"- command_x: `{diagnostic['command_x']}`",
        f"- terrain_hfield_z_scale: `{diagnostic['terrain_hfield_z_scale']}`",
        "",
        "## Hook Audit",
        "",
        f"- status: `{hook['status']}`",
        f"- hook_present: `{hook['hook_present']}`",
        f"- missing: `{hook['missing']}`",
        f"- files: `{hook['files']}`",
        "",
        "## Recipe Intent",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["recipe_intent"])
    lines.extend(["", "## Proposed Training Command", "", "```bash"])
    lines.append(" \\\n  ".join(payload["train_command"]))
    lines.extend(["```", "", "## Proposed Colab Workflow Command", "", "```bash"])
    lines.append(" \\\n  ".join(payload["colab_workflow_command"]))
    lines.extend(["```", "", "## Acceptance", ""])
    lines.extend(f"- {item}" for item in payload["acceptance"])
    lines.extend(["", "## Falsifiers", ""])
    lines.extend(f"- {item}" for item in payload["falsifiers"])
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diagnostic", default=str(DEFAULT_DIAGNOSTIC))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
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
