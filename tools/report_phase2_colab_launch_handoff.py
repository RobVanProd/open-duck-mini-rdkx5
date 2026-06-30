#!/usr/bin/env python3
"""Write the Phase 2 Colab launch handoff.

This report is intentionally read-only. It ties the current package-only
tarballs, source SHAs, archive verification, and z=0.002 launch audit to one
operator-facing handoff so the next Colab GPU session can run the exact staged
workflow without reconstructing commands from several artifacts. It does not
upload, train, SSH, deploy, or touch the robot.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_MANIFEST = (
    ROOT
    / "outputs/analysis/colab_cli/open-duck-l4-phase2-z002-tracking-margin-20260630T012421Z"
    / "PACKAGE_ONLY_MANIFEST.json"
)
DEFAULT_ARCHIVE_VERIFICATION = ROOT / "outputs/analysis/phase2_package_only_archive_verification.json"
DEFAULT_LAUNCH_AUDIT = ROOT / "outputs/analysis/phase2_z002_tracking_margin_launch_audit.json"
DEFAULT_STAGE_GUARD = ROOT / "outputs/analysis/phase2_stage_guard.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_Z002_COLAB_LAUNCH_HANDOFF.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_z002_colab_launch_handoff.json"


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


def git_value(args: list[str], cwd: Path = ROOT) -> str | None:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def shell_join(argv: list[str]) -> str:
    return " ".join(argv)


def multiline_command(argv: list[str]) -> str:
    if not argv:
        return ""
    separator = " \\" + "\n  "
    return separator.join(argv)


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    package_manifest_path = Path(args.package_manifest)
    archive_verification_path = Path(args.archive_verification_json)
    launch_audit_path = Path(args.launch_audit_json)
    stage_guard_path = Path(args.stage_guard_json)

    package = read_json(package_manifest_path)
    archive = read_json(archive_verification_path)
    launch = read_json(launch_audit_path)
    stage_guard = read_json(stage_guard_path)

    launch_command = launch.get("launch_command") or []
    package_rdk_source = ((package.get("source") or {}).get("rdk") or {})
    current_rdk_head = git_value(["rev-parse", "HEAD"])
    current_rdk_branch = git_value(["branch", "--show-current"])
    package_rdk_head = package_rdk_source.get("head")
    package_source_matches_current_head = (
        package_rdk_head is not None and package_rdk_head == current_rdk_head
    )
    checks = {
        "package_manifest_ready": package.get("status") == "PASS_COLAB_PACKAGE_ONLY_READY",
        "archive_verification_pass": archive.get("status")
        == "PASS_PHASE2_PACKAGE_ONLY_ARCHIVE_VERIFICATION",
        "archive_verification_matches_package": archive.get("package_manifest")
        == rel(package_manifest_path),
        "launch_audit_internal_checks_pass": all((launch.get("checks") or {}).values()),
        "launch_command_present": bool(launch_command),
        "stage_guard_workflow_matches": stage_guard.get("preferred_workflow") == package.get("workflow"),
        "robot_scope_clean": all(
            not bool(source.get(key))
            for source in [package, archive, launch, stage_guard]
            for key in ["robot_touched", "ssh_used", "deploy_performed", "training_started"]
        ),
    }
    notes = []
    if not package_source_matches_current_head:
        notes.append(
            "The package-only tarballs are a verified immutable snapshot, but their RDK source head "
            "differs from the current branch head. The normal --run command rebuilds and uploads a "
            "fresh tarball from the current worktree."
        )
    external_blockers = []
    if launch.get("colab_status") != "PASS_COLAB_SESSION_VISIBLE":
        external_blockers.append(launch.get("colab_status") or "COLAB_STATUS_UNKNOWN")
    if launch.get("git_status") not in {"PASS_GIT_REMOTE_READ_AUTH", "PASS_GIT_REMOTE_PUSH_AUTH"}:
        external_blockers.append(launch.get("git_status") or "GIT_STATUS_UNKNOWN")

    if all(checks.values()) and not external_blockers:
        status = "PASS_PHASE2_Z002_COLAB_HANDOFF_READY_TO_RUN"
    elif all(checks.values()):
        status = "HOLD_PHASE2_Z002_COLAB_SESSION_NOT_READY"
    else:
        status = "HOLD_PHASE2_Z002_COLAB_HANDOFF_INCOMPLETE"

    return {
        "status": status,
        "workflow": package.get("workflow"),
        "session": package.get("session"),
        "package_manifest": rel(package_manifest_path),
        "archive_verification_json": rel(archive_verification_path),
        "launch_audit_json": rel(launch_audit_path),
        "stage_guard_json": rel(stage_guard_path),
        "checks": checks,
        "notes": notes,
        "external_blockers": external_blockers,
        "current_source": {
            "rdk_branch": current_rdk_branch,
            "rdk_head": current_rdk_head,
            "package_rdk_head": package_rdk_head,
            "package_source_matches_current_head": package_source_matches_current_head,
        },
        "launch_status": launch.get("launch_status"),
        "colab_status": launch.get("colab_status"),
        "git_status": launch.get("git_status"),
        "stage_strategy": stage_guard.get("stage_strategy"),
        "launch_command": launch_command,
        "launch_command_shell": shell_join(launch_command),
        "launch_command_multiline": multiline_command(launch_command),
        "preflight_commands": [
            "colab sessions",
            f"colab status -s {package.get('session')}",
            "python3 tools/report_phase2_package_only_archive_verification.py "
            f"--package-manifest {rel(package_manifest_path)}",
            "python3 tools/report_phase2_z002_launch_audit.py "
            f"--package-manifest {rel(package_manifest_path)}",
        ],
        "package_archives": package.get("archives", {}),
        "source": package.get("source", {}),
        "required_rdk_package_paths": package.get("required_rdk_package_paths", []),
        "post_training_gate_command": [
            "python3",
            "tools/report_phase2_z002_tracking_margin_post_training_gates.py",
            "--help",
        ],
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 z=0.002 Colab Launch Handoff",
        "",
        f"status: `{payload['status']}`",
        f"workflow: `{payload['workflow']}`",
        f"session: `{payload['session']}`",
        "",
        "This is a read-only handoff. It did not upload, train, SSH, deploy, or touch the robot.",
        "",
        "## Current Gate",
        "",
        f"- launch_status: `{payload['launch_status']}`",
        f"- colab_status: `{payload['colab_status']}`",
        f"- git_status: `{payload['git_status']}`",
        f"- external_blockers: `{', '.join(payload['external_blockers']) if payload['external_blockers'] else 'none'}`",
        "",
        "## Stage Strategy",
        "",
        payload.get("stage_strategy") or "NA",
        "",
        "## Preflight",
        "",
    ]
    lines.extend(f"- `{key}`: `{value}`" for key, value in payload["checks"].items())
    lines.extend(["", "## Source Snapshot", ""])
    current = payload["current_source"]
    lines.extend(
        [
            f"- current_rdk_branch: `{current['rdk_branch']}`",
            f"- current_rdk_head: `{current['rdk_head']}`",
            f"- package_rdk_head: `{current['package_rdk_head']}`",
            f"- package_source_matches_current_head: `{current['package_source_matches_current_head']}`",
        ]
    )
    if payload["notes"]:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {item}" for item in payload["notes"])
    lines.extend(["", "## Package Archives", "", "| archive | size bytes | sha256 | path |", "|---|---:|---|---|"])
    for name, item in payload["package_archives"].items():
        lines.append(
            f"| `{name}` | {item.get('size_bytes')} | `{item.get('sha256')}` | `{item.get('path')}` |"
        )
    lines.extend(["", "## Source", ""])
    for name in ["rdk", "playground"]:
        item = (payload.get("source") or {}).get(name) or {}
        lines.append(
            f"- `{name}`: branch `{item.get('branch')}`, head `{item.get('head')}`, "
            f"tracked_dirty `{item.get('tracked_dirty')}`, untracked_count `{item.get('untracked_count')}`"
        )
    lines.append(f"- `jax_pin`: `{(payload.get('source') or {}).get('jax_pin')}`")
    lines.extend(["", "## Commands To Run When Colab Is Visible", ""])
    lines.append("Preflight:")
    lines.extend(["", "```bash", *payload["preflight_commands"], "```", ""])
    lines.append("Launch:")
    lines.extend(["", "```bash", payload["launch_command_multiline"], "```", ""])
    lines.extend(
        [
            "## Required RDK Package Paths",
            "",
        ]
    )
    lines.extend(f"- `{item}`" for item in payload["required_rdk_package_paths"])
    lines.extend(
        [
            "",
            "## Scope",
            "",
            "- No robot validation.",
            "- No SSH.",
            "- No deploy.",
            "- No grounded replay.",
            "- No training from scratch.",
            "- Use the corrected actuator bridge only.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-manifest", default=str(DEFAULT_PACKAGE_MANIFEST))
    parser.add_argument("--archive-verification-json", default=str(DEFAULT_ARCHIVE_VERIFICATION))
    parser.add_argument("--launch-audit-json", default=str(DEFAULT_LAUNCH_AUDIT))
    parser.add_argument("--stage-guard-json", default=str(DEFAULT_STAGE_GUARD))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    payload = build_payload(args)
    output_json = Path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, Path(args.output_md))
    print(payload["status"])
    return 1 if payload["status"] == "HOLD_PHASE2_Z002_COLAB_HANDOFF_INCOMPLETE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
