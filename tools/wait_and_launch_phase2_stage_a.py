#!/usr/bin/env python3
"""Wait for an adoptable Colab runtime, then launch Phase 2 Stage A.

This helper exists for unattended handoff. It polls the runtime availability
guard and only starts the Stage A launcher when a named Colab session is already
visible. It does not allocate a runtime, use local ROCm, SSH, deploy, touch the
robot, run grounded replay, or promote a training result.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "analysis" / "phase2_stage_a_wait_and_launch"


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(command: list[str], *, timeout_s: int | None = None) -> dict[str, object]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
        return {
            "command": command,
            "elapsed_s": round(time.monotonic() - started, 3),
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "elapsed_s": round(time.monotonic() - started, 3),
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timed_out": True,
        }


def load_json(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def report_command(output_dir: Path) -> list[str]:
    return [
        sys.executable,
        "tools/report_phase2_runtime_availability.py",
        "--output-md",
        str(output_dir / "PHASE2_RUNTIME_AVAILABILITY.md"),
        "--output-json",
        str(output_dir / "phase2_runtime_availability.json"),
    ]


def launch_command(output_dir: Path, workflow_output_root: Path) -> list[str]:
    return [
        sys.executable,
        "tools/launch_phase2_stage_a_rate175_colab.py",
        "--adopt-existing-session",
        "--no-create",
        "--run-workflow",
        "--output-dir",
        str(output_dir / "stage_a_launcher"),
        "--workflow-output-root",
        str(workflow_output_root),
    ]


def postrun_scan_command(output_dir: Path, workflow_output_root: Path) -> list[str]:
    return [
        sys.executable,
        "tools/report_phase2_stage_a_postrun_status.py",
        "--artifact-root",
        str(workflow_output_root),
        "--output-md",
        str(output_dir / "PHASE2_STAGE_A_POSTRUN_STATUS.md"),
        "--output-json",
        str(output_dir / "phase2_stage_a_postrun_status.json"),
    ]


def write_reports(payload: dict[str, object], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "phase2_stage_a_wait_and_launch.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )

    checks = payload.get("checks")
    rows: list[str] = []
    if isinstance(checks, list):
        for check in checks:
            if not isinstance(check, dict):
                continue
            rows.append(
                "| `{}` | `{}` | `{}` | `{}` |".format(
                    check.get("elapsed_s"),
                    check.get("status"),
                    check.get("colab_sessions"),
                    check.get("local_gpu_blocker_count"),
                )
            )
    if not rows:
        rows.append("| NA | NA | NA | NA |")

    launch_result = payload.get("launch_result")
    launch_lines = [f"- launch_started: `{payload.get('launch_started')}`"]
    if isinstance(launch_result, dict):
        launch_lines.extend(
            [
                f"- launch_returncode: `{launch_result.get('returncode')}`",
                f"- launch_timed_out: `{launch_result.get('timed_out')}`",
            ]
        )

    postrun_status = payload.get("postrun_status")
    postrun_lines = [
        f"- postrun_scan_started: `{payload.get('postrun_scan_started')}`",
        f"- postrun_status: `{postrun_status}`",
    ]

    (output_dir / "PHASE2_STAGE_A_WAIT_AND_LAUNCH.md").write_text(
        "\n".join(
            [
                "# Phase 2 Stage A Wait And Launch",
                "",
                f"status: `{payload.get('status')}`",
                f"generated_at: `{payload.get('generated_at')}`",
                "",
                "Offline only. No robot, SSH, deploy, grounded replay, training-result",
                "promotion, runtime behavior change, or local ROCm training was performed",
                "by this wrapper.",
                "",
                "## Poll Checks",
                "",
                "| elapsed_s | status | colab_sessions | local_gpu_blockers |",
                "|---:|---|---|---:|",
                *rows,
                "",
                "## Launch",
                "",
                *launch_lines,
                "",
                "## Post-Run",
                "",
                *postrun_lines,
                "",
                "## Decision",
                "",
                str(payload.get("decision") or ""),
                "",
            ]
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--workflow-output-root",
        type=Path,
        default=ROOT / "outputs" / "analysis" / "colab_cli_stage_a_rate175_prior",
    )
    parser.add_argument("--timeout-s", type=float, default=3600.0)
    parser.add_argument("--interval-s", type=float, default=30.0)
    parser.add_argument("--launch-timeout-s", type=int, default=15300)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Poll once and report the decision without launching Stage A.",
    )
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    payload: dict[str, object] = {
        "status": "HOLD_GPU_RUNTIME_UNAVAILABLE",
        "generated_at": timestamp(),
        "offline_only": True,
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "grounded_replay_performed": False,
        "local_rocm_training_started": False,
        "launch_started": False,
        "postrun_scan_started": False,
        "dry_run": args.dry_run,
        "checks": [],
    }

    started = time.monotonic()
    selected = False
    while True:
        availability_result = run(report_command(output_dir), timeout_s=90)
        availability = load_json(output_dir / "phase2_runtime_availability.json") or {}
        status = availability.get("status")
        blockers = availability.get("local_gpu_blockers")
        sessions = availability.get("colab_sessions")
        payload["checks"].append(
            {
                "elapsed_s": round(time.monotonic() - started, 3),
                "status": status,
                "colab_sessions": sessions,
                "local_gpu_blocker_count": len(blockers) if isinstance(blockers, list) else None,
                "availability_returncode": availability_result.get("returncode"),
            }
        )
        if status == "PASS_COLAB_SESSION_AVAILABLE":
            selected = True
            payload["status"] = "PASS_COLAB_SESSION_AVAILABLE"
            payload["decision"] = "Colab session is visible; Stage A launch is authorized."
            break
        if args.dry_run:
            payload["status"] = str(status or "HOLD_RUNTIME_STATUS_UNKNOWN")
            payload["decision"] = (
                "Dry run only. No Stage A launch was attempted."
            )
            break
        if time.monotonic() - started >= args.timeout_s:
            payload["status"] = "HOLD_WAIT_TIMEOUT"
            payload["decision"] = (
                "No adoptable Colab session appeared before timeout. No launch attempted."
            )
            break
        time.sleep(min(max(1.0, args.interval_s), max(0.0, args.timeout_s - (time.monotonic() - started))))

    if selected and not args.dry_run:
        launch_result = run(
            launch_command(output_dir, args.workflow_output_root),
            timeout_s=args.launch_timeout_s,
        )
        payload["launch_started"] = True
        payload["launch_result"] = launch_result

        postrun_result = run(
            postrun_scan_command(output_dir, args.workflow_output_root),
            timeout_s=300,
        )
        payload["postrun_scan_started"] = True
        payload["postrun_result"] = postrun_result
        postrun_payload = load_json(output_dir / "phase2_stage_a_postrun_status.json") or {}
        payload["postrun_status"] = postrun_payload.get("status")
        payload["stage_a_checkpoint_count"] = postrun_payload.get("checkpoint_count")

        if payload["postrun_status"] == "PASS_STAGE_A_CHECKPOINTS_READY":
            payload["status"] = "PASS_STAGE_A_CHECKPOINTS_READY"
            payload["decision"] = (
                "Run the sweep_command_shell recorded in the post-run status JSON."
            )
        elif launch_result.get("returncode") == 0:
            payload["status"] = str(payload["postrun_status"] or "HOLD_POSTRUN_STATUS_UNKNOWN")
            payload["decision"] = (
                "Stage A launcher returned, but no usable checkpoint was found."
            )
        else:
            payload["status"] = "HOLD_STAGE_A_LAUNCH_FAILED"
            payload["decision"] = (
                "Stage A launcher failed. Inspect launch stdout/stderr in the JSON report."
            )

    write_reports(payload, output_dir)
    print(json.dumps({"status": payload["status"], "output_dir": str(output_dir)}, sort_keys=True))
    return 0 if str(payload["status"]).startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
