#!/usr/bin/env python3
"""Plan the Phase 2 swing phase-advance branch.

This is a read-only planning/preflight tool. It consumes the swing-clearance
diagnostic and records whether the training stack has the default-off hook
needed to act on a LATENCY_LIMITED verdict. It does not train, SSH, deploy, or
touch the robot.
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
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_SWING_PHASE_ADVANCE_NEXT_RECIPE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_swing_phase_advance_next_recipe.json"
PLAYGROUND_ROOT = ROOT.parent / "Open_Duck_Playground"
JOYSTICK_PATH = PLAYGROUND_ROOT / "playground/open_duck_mini_v2/joystick.py"
RUNNER_PATH = PLAYGROUND_ROOT / "playground/open_duck_mini_v2/runner.py"
REWARDS_PATH = PLAYGROUND_ROOT / "playground/common/rewards.py"


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


def text_contains(path: Path, needles: list[str]) -> dict[str, bool]:
    if not path.exists():
        return {needle: False for needle in needles}
    text = path.read_text(errors="replace")
    return {needle: needle in text for needle in needles}


def audit_phase_advance_hook() -> dict[str, Any]:
    """Return evidence for whether a real phase-advance hook exists."""

    joystick_needles = [
        "forward_swing_phase_advance",
        "swing_phase_advance",
        "phase_advance_ticks",
        "phase_advance_steps",
    ]
    runner_needles = [
        "--forward_swing_phase_advance_ticks",
        "--swing-phase-advance",
        "phase_advance_ticks",
    ]
    rewards_needles = [
        "advance_phase",
        "phase_advance_ticks",
        "forward_swing_phase",
    ]
    joystick = text_contains(JOYSTICK_PATH, joystick_needles)
    runner = text_contains(RUNNER_PATH, runner_needles)
    rewards = text_contains(REWARDS_PATH, rewards_needles)
    hook_present = any(joystick.values()) and any(runner.values())
    return {
        "status": (
            "PASS_PHASE_ADVANCE_HOOK_PRESENT"
            if hook_present
            else "HOLD_PHASE_ADVANCE_HOOK_MISSING"
        ),
        "hook_present": hook_present,
        "files": {
            "joystick": rel(JOYSTICK_PATH),
            "runner": rel(RUNNER_PATH),
            "rewards": rel(REWARDS_PATH),
        },
        "evidence": {
            "joystick": joystick,
            "runner": runner,
            "rewards": rewards,
        },
        "existing_hooks": [
            "forward_swing_clearance fires on first_contact using swing_peak_lift.",
            "forward_swing_advance fires on first_contact using swing_peak_forward_advance.",
            "forward_swing_balance penalizes one-sided swing usage.",
        ],
        "missing_hook": (
            "A default-off phase-advanced swing objective that evaluates lift/advance "
            "against phase + advance_ticks before the measured 3-tick actuator delay."
        ),
    }


def summarize_diagnostic(diagnostic: dict[str, Any]) -> dict[str, Any]:
    aggregate = diagnostic.get("aggregate_verdict") or {}
    seed_results = diagnostic.get("seed_results") or []
    side_rows: list[dict[str, Any]] = []
    for seed in seed_results:
        for side, side_data in (seed.get("side_results") or {}).items():
            side_rows.append(
                {
                    "seed": seed.get("seed"),
                    "side": side,
                    "classification": side_data.get("classification"),
                    "rate_utilization_peak": side_data.get("rate_utilization_peak"),
                    "planted_pct_during_phase_swing": side_data.get(
                        "planted_pct_during_phase_swing"
                    ),
                    "achieved_to_ceiling_ratio_peak": side_data.get(
                        "achieved_to_ceiling_ratio_peak"
                    ),
                    "latency_limited_segment_count": side_data.get(
                        "latency_limited_segment_count"
                    ),
                    "phase_swing_segments": side_data.get("phase_swing_segments"),
                }
            )
    rate_peaks = [
        float(row["rate_utilization_peak"])
        for row in side_rows
        if row.get("rate_utilization_peak") is not None
    ]
    planted = [
        float(row["planted_pct_during_phase_swing"])
        for row in side_rows
        if row.get("planted_pct_during_phase_swing") is not None
    ]
    return {
        "status": diagnostic.get("status"),
        "verdict": aggregate.get("verdict"),
        "classification_counts": aggregate.get("classification_counts"),
        "selected_fix_branch": aggregate.get("selected_fix_branch"),
        "candidate": diagnostic.get("inputs", {}).get("candidate"),
        "candidate_sha256": diagnostic.get("inputs", {}).get("candidate_sha256"),
        "corrected_bridge": diagnostic.get("inputs", {}).get("corrected_bridge")
        or diagnostic.get("inputs", {}).get("fit_json"),
        "corrected_bridge_sha256": diagnostic.get("inputs", {}).get(
            "corrected_bridge_sha256"
        )
        or diagnostic.get("inputs", {}).get("fit_json_sha256"),
        "task": diagnostic.get("inputs", {}).get("task"),
        "terrain_hfield_z_scale": diagnostic.get("inputs", {}).get(
            "terrain_hfield_z_scale"
        ),
        "command_x": diagnostic.get("inputs", {}).get("command_x"),
        "phase_convention": diagnostic.get("audit", {}).get("phase_convention"),
        "side_rows": side_rows,
        "max_rate_utilization_peak": max(rate_peaks) if rate_peaks else None,
        "mean_planted_pct_during_phase_swing": (
            sum(planted) / len(planted) if planted else None
        ),
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    diagnostic_path = Path(args.diagnostic)
    diagnostic = read_json(diagnostic_path)
    summary = summarize_diagnostic(diagnostic)
    hook_audit = audit_phase_advance_hook()
    status = (
        "PASS_SWING_PHASE_ADVANCE_RECIPE_READY"
        if summary["verdict"] == "LATENCY_LIMITED" and hook_audit["hook_present"]
        else "HOLD_PHASE_ADVANCE_HOOK_MISSING"
        if summary["verdict"] == "LATENCY_LIMITED"
        else "HOLD_DIAGNOSTIC_NOT_LATENCY_LIMITED"
    )
    return {
        "status": status,
        "stage": "phase2_swing_phase_advance",
        "diagnostic": {
            "path": rel(diagnostic_path),
            "sha256": sha256_file(diagnostic_path),
            **summary,
        },
        "hook_audit": hook_audit,
        "recipe_intent": [
            "Act on the LATENCY_LIMITED swing-clearance verdict, not on generic terrain or support failure.",
            "Advance the swing lift/advance objective by roughly the corrected 3-tick actuator delay.",
            "Keep bridge limits canonical; do not increase global target-rate allowance.",
            "Warm-start from the Phase 2 gain099 candidate/trainable checkpoint; do not train from scratch.",
            "Gate x=0.08 and x=0.0 on the corrected bridge after any implementation.",
        ],
        "required_default_off_hook": {
            "config": "reward_config.forward_swing_phase_advance_ticks, default 0",
            "runner_cli": "--forward_swing_phase_advance_ticks",
            "semantics": [
                "Use phase-primary swing segmentation.",
                "Compute the rewarded swing side from phase advanced by N control ticks.",
                "Reward/penalize lift and forward advance before touchdown so lift starts before the measured actuator lag.",
                "Report the configured advance ticks in training manifests and gate artifacts.",
            ],
            "initial_values_to_test": [1, 2, 3],
            "canonical_first_try": 3,
        },
        "acceptance_after_hook": [
            "Training manifests show forward_swing_phase_advance_ticks explicitly.",
            "No corrected per-joint velocity-limit excess at x=0.08.",
            "z=0.0024 x=0.08 and x=0.0 corrected-bridge gates remain 8/8.",
            "Gentle-push z=0.0024 regressions remain 8/8.",
            "Swing diagnostic rerun shows lower planted percentage during phase-commanded swing without higher rate utilization.",
        ],
        "falsifiers": [
            "If phase advance reduces planted swing but breaks x=0.0 command semantics, reject the candidate.",
            "If phase advance only improves clearance by exceeding corrected pitch-chain limits, reject the recipe.",
            "If ticks 1-3 all preserve latency-limited planted swing, return to structural gait-duration/knee-bend branch.",
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
        "# Phase 2 Swing Phase-Advance Next Recipe",
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
        f"- classification_counts: `{diagnostic['classification_counts']}`",
        f"- selected_fix_branch: `{diagnostic['selected_fix_branch']}`",
        f"- candidate: `{diagnostic['candidate']}`",
        f"- candidate_sha256: `{diagnostic['candidate_sha256']}`",
        f"- corrected_bridge: `{diagnostic['corrected_bridge']}`",
        f"- corrected_bridge_sha256: `{diagnostic['corrected_bridge_sha256']}`",
        f"- task: `{diagnostic['task']}`",
        f"- terrain_hfield_z_scale: `{diagnostic['terrain_hfield_z_scale']}`",
        f"- command_x: `{diagnostic['command_x']}`",
        f"- max_rate_utilization_peak: `{diagnostic['max_rate_utilization_peak']}`",
        f"- mean_planted_pct_during_phase_swing: `{diagnostic['mean_planted_pct_during_phase_swing']}`",
        "",
        "## Hook Audit",
        "",
        f"- status: `{hook['status']}`",
        f"- hook_present: `{hook['hook_present']}`",
        f"- joystick: `{hook['files']['joystick']}`",
        f"- runner: `{hook['files']['runner']}`",
        f"- rewards: `{hook['files']['rewards']}`",
        "",
        "Existing hooks:",
        "",
    ]
    lines.extend(f"- {item}" for item in hook["existing_hooks"])
    lines.extend(
        [
            "",
            "Missing hook:",
            "",
            f"- {hook['missing_hook']}",
            "",
            "## Recipe Intent",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["recipe_intent"])
    lines.extend(["", "## Required Default-Off Hook", ""])
    for key, value in payload["required_default_off_hook"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Acceptance After Hook", ""])
    lines.extend(f"- {item}" for item in payload["acceptance_after_hook"])
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
