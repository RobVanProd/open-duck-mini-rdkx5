#!/usr/bin/env python3
"""Report the allowed next actions for the current Phase 2 stage.

This is a read-only guardrail artifact. It does not train, SSH, deploy, touch
the robot, or modify Playground. It combines the current curriculum ledger,
next-run plan, z=0.005 support recipe, and artifact manifest into one explicit
"allowed vs forbidden" decision so the campaign cannot silently advance past a
held gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from run_colab_cli_cuda_workflow import required_rdk_package_paths, would_package_path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEDGER = ROOT / "outputs/analysis/phase2_curriculum_gate_ledger.json"
DEFAULT_NEXT_PLAN = ROOT / "outputs/analysis/phase2_next_run_plan.json"
DEFAULT_RECIPE = ROOT / "outputs/analysis/phase2_z005_support_next_recipe.json"
DEFAULT_MANIFEST = ROOT / "outputs/analysis/phase2_artifact_manifest.json"
DEFAULT_PACKAGE_MANIFEST = ROOT / "outputs/analysis/phase2_colab_package_manifest.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_STAGE_GUARD.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_stage_guard.json"


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        return {
            "_read_error": str(exc),
            "_path": rel(path),
        }


def nested(payload: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return default if current is None else current


def package_preflight(workflow: str) -> dict[str, Any]:
    items = []
    for relative_path in required_rdk_package_paths(workflow):
        local_path = ROOT / relative_path
        items.append(
            {
                "path": relative_path,
                "exists": local_path.exists(),
                "included_by_tar_filter": would_package_path(relative_path),
            }
        )
    missing = [item["path"] for item in items if not item["exists"]]
    excluded = [item["path"] for item in items if item["exists"] and not item["included_by_tar_filter"]]
    status = "PASS_PACKAGE_PREFLIGHT" if not missing and not excluded else "HOLD_PACKAGE_PREFLIGHT"
    return {
        "status": status,
        "workflow": workflow,
        "missing": missing,
        "excluded_by_tar_filter": excluded,
        "items": items,
    }


def collect(args: argparse.Namespace) -> dict[str, Any]:
    ledger_path = Path(args.ledger)
    next_plan_path = Path(args.next_plan)
    recipe_path = Path(args.recipe)
    manifest_path = Path(args.manifest)
    package_manifest_path = Path(args.package_manifest)

    ledger = read_json(ledger_path)
    next_plan = read_json(next_plan_path)
    recipe = read_json(recipe_path)
    manifest = read_json(manifest_path)
    package_manifest = read_json(package_manifest_path)

    current_stage = ledger.get("current_stage")
    current_gate_status = ledger.get("status")
    next_recipe_status = recipe.get("status")
    launch_status = nested(next_plan, "readiness", "launch_status")
    colab_status = nested(next_plan, "readiness", "colab", "status")
    colab_hardware = nested(next_plan, "readiness", "colab", "hardware")
    git_status = nested(next_plan, "readiness", "git", "status")
    colab_active = bool(nested(next_plan, "readiness", "colab", "active", default=False))
    preferred_command = nested(next_plan, "commands", "colab", "shell") or nested(recipe, "commands", "colab", "shell")
    package = package_preflight("phase2-z005-support")

    gates = ledger.get("gates") if isinstance(ledger.get("gates"), dict) else {}
    held_gates = [
        name
        for name, item in gates.items()
        if isinstance(item, dict) and item.get("status") not in {"PASS_GATE", None}
    ]
    missing_gates = [
        name
        for name, item in gates.items()
        if isinstance(item, dict) and item.get("status") in {"MISSING_GATE_ARTIFACT", "INVALID_GATE_JSON"}
    ]

    allowed_actions = [
        "Review committed Phase 2 analysis artifacts and guard reports.",
        "Run read-only report tools: report_phase2_curriculum_gate.py, report_phase2_artifact_manifest.py, and report_phase2_stage_guard.py.",
        "Run the phase2-z005-support Colab workflow in plan-only mode to verify the package preflight and generated remote driver.",
        "Run the phase2-z005-support Colab workflow with --package-only to build and hash local upload archives without contacting Colab.",
        "Prepare or reconnect a Colab GPU session named open-duck-l4; A100/L4 is preferred, T4 is acceptable but slower.",
        "Run the phase2-z005-support recipe only after the Colab session is active and still using the corrected bridge.",
        "Run report_phase2_z005_post_training_gates.py on post-training seed-gate output.",
    ]
    if colab_active:
        allowed_actions.append("Launch the preferred phase2-z005-support Colab workflow.")
    else:
        allowed_actions.append("Do not launch training yet from this host; Colab session open-duck-l4 is not active.")

    forbidden_actions = [
        "No robot validation.",
        "No SSH.",
        "No deploy.",
        "No grounded replay.",
        "No direct BEST_WALK deployment.",
        "No training from scratch; continue only from the Phase 2 warm-start checkpoint.",
        "No old/asymmetric actuator bridge.",
        "No z=0.005 push stage until both z=0.005 no-push gates pass.",
        "No stronger terrain until z=0.005 support passes and z=0.002 regression stays clear.",
        "No promotion without PASS_PHASE2_Z005_POST_TRAINING_GATES.",
    ]

    advance_requirements = [
        "z=0.005 x=0.08 no-push: 8/8 duration complete, zero falls, no velocity excess, tracking p95 <= 0.20, track ratio >= 0.40.",
        "z=0.005 x=0.0 no-push: 8/8 duration complete, zero falls, no velocity excess, |mean vx| <= 0.005.",
        "z=0.002 x=0.08/x=0.0 no-push regression gates remain passing.",
        "z=0.002 x=0.08/x=0.0 gentle-push regression gates remain passing.",
        "Post-training decision artifact reports PASS_PHASE2_Z005_POST_TRAINING_GATES.",
    ]

    if launch_status and launch_status != "PASS_PHASE2_NEXT_RUN_READY":
        status = launch_status
    elif package["status"] != "PASS_PACKAGE_PREFLIGHT":
        status = package["status"]
    elif current_gate_status and str(current_gate_status).startswith("HOLD"):
        status = "PASS_PHASE2_STAGE_GUARD_READY_TO_RUN_Z005_SUPPORT"
    else:
        status = "PASS_PHASE2_STAGE_GUARD_READY"

    return {
        "status": status,
        "current_stage": current_stage,
        "current_gate_status": current_gate_status,
        "next_recipe_status": next_recipe_status,
        "launch_status": launch_status,
        "colab_status": colab_status,
        "colab_hardware": colab_hardware,
        "git_status": git_status,
        "held_gates": held_gates,
        "missing_gates": missing_gates,
        "candidate": manifest.get("core_artifacts", {}).get("candidate", {}),
        "corrected_bridge": manifest.get("core_artifacts", {}).get("corrected_bridge", {}),
        "restore_checkpoint": manifest.get("core_artifacts", {}).get("restore_checkpoint", {}),
        "package_preflight": package,
        "package_manifest_status": package_manifest.get("status"),
        "input_artifacts": {
            "ledger": rel(ledger_path),
            "next_plan": rel(next_plan_path),
            "recipe": rel(recipe_path),
            "manifest": rel(manifest_path),
            "package_manifest": rel(package_manifest_path),
        },
        "allowed_actions": allowed_actions,
        "forbidden_actions": forbidden_actions,
        "advance_requirements": advance_requirements,
        "preferred_command": preferred_command,
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 Stage Guard",
        "",
        f"status: `{payload['status']}`",
        f"current_stage: `{payload.get('current_stage')}`",
        f"current_gate_status: `{payload.get('current_gate_status')}`",
        f"next_recipe_status: `{payload.get('next_recipe_status')}`",
        f"launch_status: `{payload.get('launch_status')}`",
        "",
        "This is a read-only guard. It did not train, SSH, deploy, or touch the robot.",
        "",
        "## Readiness",
        "",
        f"- colab_status: `{payload.get('colab_status')}`",
        f"- colab_hardware: `{payload.get('colab_hardware')}`",
        f"- git_status: `{payload.get('git_status')}`",
        f"- package_preflight: `{payload.get('package_preflight', {}).get('status')}`",
        f"- package_manifest_status: `{payload.get('package_manifest_status')}`",
        f"- held_gates: `{', '.join(payload.get('held_gates') or []) or 'none'}`",
        f"- missing_gates: `{', '.join(payload.get('missing_gates') or []) or 'none'}`",
        "",
        "## Allowed Now",
        "",
    ]
    for item in payload["allowed_actions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Forbidden", ""])
    for item in payload["forbidden_actions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Required Evidence To Advance", ""])
    for item in payload["advance_requirements"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Package Preflight",
            "",
            "| path | exists | included by tar filter |",
            "|---|---|---|",
        ]
    )
    for item in payload.get("package_preflight", {}).get("items", []):
        lines.append(
            f"| `{item['path']}` | `{item['exists']}` | `{item['included_by_tar_filter']}` |"
        )
    lines.extend(
        [
            "",
            "## Preferred Command",
            "",
            "```bash",
            payload.get("preferred_command") or "NA",
            "```",
            "",
            "## Input Artifacts",
            "",
        ]
    )
    for key, value in payload["input_artifacts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    parser.add_argument("--next-plan", default=str(DEFAULT_NEXT_PLAN))
    parser.add_argument("--recipe", default=str(DEFAULT_RECIPE))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--package-manifest", default=str(DEFAULT_PACKAGE_MANIFEST))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()
    payload = collect(args)
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, output_md)
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
