#!/usr/bin/env python3
"""Write a launch audit for the Phase 2 z=0.002 tracking-margin run.

This is a read-only bookkeeping tool. It records the selected workflow, the
required local inputs, the package-only archive hashes, readiness state, and
the exact launch command. It does not train, SSH, deploy, or touch the robot.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECIPE_JSON = ROOT / "outputs/analysis/phase2_z002_tracking_margin_next_recipe.json"
DEFAULT_NEXT_RUN_JSON = ROOT / "outputs/analysis/phase2_next_run_plan.json"
DEFAULT_READINESS_JSON = ROOT / "outputs/analysis/phase2_local_fallback_readiness.json"
DEFAULT_STAGE_GUARD_JSON = ROOT / "outputs/analysis/phase2_stage_guard.json"
DEFAULT_ARTIFACT_MANIFEST_JSON = ROOT / "outputs/analysis/phase2_artifact_manifest.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_Z002_TRACKING_MARGIN_LAUNCH_AUDIT.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_z002_tracking_margin_launch_audit.json"
DEFAULT_PACKAGE_ROOT = ROOT / "outputs/analysis/colab_cli"


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
    except FileNotFoundError:
        return {"_missing": True, "_path": str(path)}


def latest_package_manifest(root: Path, workflow: str) -> Path | None:
    candidates = sorted(
        root.glob(f"*-{workflow}-*/PACKAGE_ONLY_MANIFEST.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def shell_command(argv: list[str]) -> str:
    return " ".join(argv)


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    recipe = read_json(Path(args.recipe_json))
    next_run = read_json(Path(args.next_run_json))
    readiness = read_json(Path(args.readiness_json))
    stage_guard = read_json(Path(args.stage_guard_json))
    artifact_manifest = read_json(Path(args.artifact_manifest_json))
    package_manifest_path = (
        Path(args.package_manifest)
        if args.package_manifest
        else latest_package_manifest(Path(args.package_root), args.workflow)
    )
    package_manifest = read_json(package_manifest_path) if package_manifest_path else {}

    required_inputs: dict[str, dict[str, Any]] = {}
    for name, item in (readiness.get("core_artifacts") or {}).items():
        path = ROOT / item.get("path", "")
        required_inputs[name] = {
            "path": item.get("path"),
            "exists": path.exists(),
            "kind": "directory" if path.is_dir() else "file",
        }

    recipe_settings = recipe.get("key_recipe_settings") or {}
    launch_command = (next_run.get("commands") or {}).get("colab", {}).get("argv", [])
    launch_status = (next_run.get("readiness") or {}).get("launch_status")
    colab_status = ((next_run.get("readiness") or {}).get("colab") or {}).get("status")
    git_status = ((next_run.get("readiness") or {}).get("git") or {}).get("status")
    archive_status = package_manifest.get("status")
    package_workflow = package_manifest.get("workflow")

    checks = {
        "recipe_workflow_matches": recipe_settings.get("workflow") == args.workflow,
        "next_run_workflow_matches": (
            (next_run.get("commands") or {}).get("colab", {}).get("workflow") == args.workflow
        ),
        "readiness_workflow_matches": readiness.get("workflow") == args.workflow,
        "stage_guard_workflow_matches": stage_guard.get("preferred_workflow") == args.workflow,
        "stage_guard_post_training_status_matches": (
            stage_guard.get("post_training_status")
            == "PASS_PHASE2_Z002_TRACKING_MARGIN_POST_TRAINING_GATES"
        ),
        "artifact_manifest_stage_matches": artifact_manifest.get("stage") == "stage_z002_tracking_margin",
        "artifact_manifest_promotion_gate_matches": (
            (artifact_manifest.get("promotion_gate") or {}).get("required_post_training_status")
            == "PASS_PHASE2_Z002_TRACKING_MARGIN_POST_TRAINING_GATES"
        ),
        "package_workflow_matches": package_workflow == args.workflow,
        "required_inputs_exist": all(item["exists"] for item in required_inputs.values()),
        "package_only_ready": archive_status == "PASS_COLAB_PACKAGE_ONLY_READY",
        "robot_scope_clean": all(
            not bool(source.get(key))
            for source in [recipe, package_manifest, readiness]
            for key in ["robot_touched", "ssh_used", "deploy_performed", "training_started"]
        ),
    }

    if all(checks.values()) and launch_status == "PASS_PHASE2_COLAB_GPU_SESSION_READY":
        status = "PASS_Z002_TRACKING_MARGIN_READY_TO_LAUNCH"
    elif all(checks.values()):
        status = "HOLD_EXTERNAL_LAUNCH_BLOCKERS"
    else:
        status = "HOLD_Z002_TRACKING_MARGIN_AUDIT_FAILED"

    return {
        "status": status,
        "workflow": args.workflow,
        "recipe_json": rel(Path(args.recipe_json)),
        "next_run_json": rel(Path(args.next_run_json)),
        "readiness_json": rel(Path(args.readiness_json)),
        "stage_guard_json": rel(Path(args.stage_guard_json)),
        "artifact_manifest_json": rel(Path(args.artifact_manifest_json)),
        "package_manifest": rel(package_manifest_path) if package_manifest_path else None,
        "launch_status": launch_status,
        "colab_status": colab_status,
        "git_status": git_status,
        "checks": checks,
        "required_inputs": required_inputs,
        "recipe_settings": recipe_settings,
        "launch_command": launch_command,
        "launch_command_shell": shell_command(launch_command),
        "package_archives": package_manifest.get("archives", {}),
        "package_required_paths": package_manifest.get("required_rdk_package_paths", []),
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 z=0.002 Tracking-Margin Launch Audit",
        "",
        f"status: `{payload['status']}`",
        f"workflow: `{payload['workflow']}`",
        "",
        "This is a read-only launch audit. It did not train, SSH, deploy, or touch the robot.",
        "",
        "## Launch State",
        "",
        f"- launch_status: `{payload['launch_status']}`",
        f"- colab_status: `{payload['colab_status']}`",
        f"- git_status: `{payload['git_status']}`",
        f"- package_manifest: `{payload['package_manifest']}`",
        f"- stage_guard_json: `{payload['stage_guard_json']}`",
        f"- artifact_manifest_json: `{payload['artifact_manifest_json']}`",
        "",
        "## Checks",
        "",
    ]
    lines.extend(f"- `{key}`: `{value}`" for key, value in payload["checks"].items())
    lines.extend(["", "## Required Inputs", "", "| input | exists | kind | path |", "|---|---:|---|---|"])
    for name, item in payload["required_inputs"].items():
        lines.append(f"| `{name}` | `{item['exists']}` | `{item['kind']}` | `{item['path']}` |")
    lines.extend(["", "## Recipe Settings", ""])
    for key in [
        "workflow",
        "terrain_hfield_z_scale",
        "num_timesteps",
        "restore_policy_kl_scale",
        "ppo_learning_rate",
        "target_rate_scale",
        "command_progress_required_ratio",
        "push_enable",
        "actuator_bridge_velocity_limit_range_rad_s",
    ]:
        if key in payload["recipe_settings"]:
            lines.append(f"- `{key}`: `{payload['recipe_settings'][key]}`")
    lines.extend(["", "## Package Archives", "", "| archive | size bytes | sha256 | path |", "|---|---:|---|---|"])
    for name, item in payload["package_archives"].items():
        lines.append(f"| `{name}` | {item.get('size_bytes')} | `{item.get('sha256')}` | `{item.get('path')}` |")
    lines.extend(["", "## Launch Command", "", "```bash", payload["launch_command_shell"], "```", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", default="phase2-z002-tracking-margin")
    parser.add_argument("--recipe-json", default=str(DEFAULT_RECIPE_JSON))
    parser.add_argument("--next-run-json", default=str(DEFAULT_NEXT_RUN_JSON))
    parser.add_argument("--readiness-json", default=str(DEFAULT_READINESS_JSON))
    parser.add_argument("--stage-guard-json", default=str(DEFAULT_STAGE_GUARD_JSON))
    parser.add_argument("--artifact-manifest-json", default=str(DEFAULT_ARTIFACT_MANIFEST_JSON))
    parser.add_argument("--package-root", default=str(DEFAULT_PACKAGE_ROOT))
    parser.add_argument("--package-manifest")
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
