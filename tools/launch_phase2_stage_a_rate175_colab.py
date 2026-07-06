#!/usr/bin/env python3
"""Retry-launch the valid Phase 2 Stage A rate175 Colab job.

This helper is offline-only. It does not touch the robot, SSH, deploy, or run
grounded replay. It only manages a Colab session and, when requested, invokes
the already-pinned Stage A workflow from the true Phase 1 rate175 checkpoint.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "analysis" / "phase2_stage_a_rate175_colab_retry"


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def run_command(command: list[str], *, timeout_s: int | None = None) -> dict[str, object]:
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


def session_exists(status_result: dict[str, object]) -> bool:
    text = f"{status_result.get('stdout') or ''}\n{status_result.get('stderr') or ''}".lower()
    if status_result.get("returncode") not in {0, None}:
        return False
    return "not found" not in text and "session '" not in text


def parse_session_names(text: str) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if " | Hardware: " not in stripped:
            continue
        match = re.match(r"^\[([^\]]+)\]\s+", stripped)
        if not match:
            continue
        name = match.group(1).strip()
        if not name or name in {"?", "colab"} or name in seen:
            continue
        seen.add(name)
        names.append(name)
    return names


def find_unique_existing_session(timeout_s: int) -> dict[str, object]:
    result = run_command(["colab", "status"], timeout_s=timeout_s)
    combined = f"{result.get('stdout') or ''}\n{result.get('stderr') or ''}"
    names = parse_session_names(combined)
    status = "HOLD_NO_EXISTING_SESSION"
    selected = None
    if len(names) == 1:
        status = "PASS_UNIQUE_EXISTING_SESSION"
        selected = names[0]
    elif len(names) > 1:
        status = "HOLD_MULTIPLE_EXISTING_SESSIONS"
    return {
        "status": status,
        "selected_session": selected,
        "session_names": names,
        "result": result,
    }


def wait_for_unique_existing_session(
    *, timeout_s: float, interval_s: float, status_timeout_s: int
) -> dict[str, object]:
    started = time.monotonic()
    checks: list[dict[str, object]] = []
    selected = None
    final_status = "HOLD_WAIT_TIMEOUT"
    while True:
        check = find_unique_existing_session(status_timeout_s)
        checks.append(
            {
                "elapsed_s": round(time.monotonic() - started, 3),
                "status": check.get("status"),
                "selected_session": check.get("selected_session"),
                "session_names": check.get("session_names"),
            }
        )
        if check.get("status") == "PASS_UNIQUE_EXISTING_SESSION":
            selected = check.get("selected_session")
            final_status = "PASS_UNIQUE_EXISTING_SESSION"
            break
        if check.get("status") == "HOLD_MULTIPLE_EXISTING_SESSIONS":
            final_status = "HOLD_MULTIPLE_EXISTING_SESSIONS"
            break
        elapsed = time.monotonic() - started
        if elapsed >= timeout_s:
            break
        time.sleep(min(interval_s, max(0.0, timeout_s - elapsed)))
    return {
        "status": final_status,
        "selected_session": selected,
        "checks": checks,
        "elapsed_s": round(time.monotonic() - started, 3),
    }


def stage_a_workflow_command(args: argparse.Namespace) -> list[str]:
    command = [
        sys.executable,
        "tools/run_colab_cli_cuda_workflow.py",
        "--session",
        args.session,
        "--workflow",
        "phase2-stage-a-narrow",
        "--run",
        "--skip-audit",
        "--phase2-skip-post-training-gates",
        "--remote-artifact-interval-s",
        "0",
        "--timeout-s",
        str(args.workflow_timeout_s),
        "--candidate-behavior-prior-mlp-npz",
        "outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz",
        "--candidate-behavior-prior-scale",
        "-0.6",
        "--candidate-behavior-prior-huber-delta",
        "0.05",
        "--phase2-restore-policy-kl-scale",
        "4.0",
        "--output-root",
        str(args.workflow_output_root),
    ]
    if args.execution_mode == "exec":
        command.extend(["--exec-remote", "--exec-remote-timeout-s", str(args.exec_remote_timeout_s)])
    return command


def write_reports(payload: dict[str, object], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "phase2_stage_a_rate175_colab_retry.json"
    md_path = output_dir / "PHASE2_STAGE_A_RATE175_COLAB_RETRY.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    attempts = payload.get("allocation_attempts") or []
    rows = []
    if isinstance(attempts, list):
        for item in attempts:
            if not isinstance(item, dict):
                continue
            rows.append(
                "| `{}` | `{}` | `{}` | `{}` |".format(
                    item.get("attempt"),
                    item.get("command_label"),
                    item.get("status"),
                    str(item.get("detail") or "").replace("\n", " ")[:180],
                )
            )
    if not rows:
        rows.append("| NA | NA | NA | NA |")

    workflow = payload.get("workflow_result")
    workflow_lines = []
    if isinstance(workflow, dict):
        workflow_lines = [
            f"- workflow_started: `{payload.get('workflow_started')}`",
            f"- workflow_returncode: `{workflow.get('returncode')}`",
            f"- workflow_timed_out: `{workflow.get('timed_out')}`",
        ]
    else:
        workflow_lines = [f"- workflow_started: `{payload.get('workflow_started')}`"]

    md_path.write_text(
        "\n".join(
            [
                "# Phase 2 Stage A Rate175 Colab Retry",
                "",
                f"status: `{payload.get('status')}`",
                f"generated_at: `{payload.get('generated_at')}`",
                "",
                "Offline only. No robot, SSH, deploy, grounded replay, or runtime behavior change was performed.",
                "",
                "## Allocation Attempts",
                "",
                "| attempt | command | status | detail |",
                "|---:|---|---|---|",
                *rows,
                "",
                "## Workflow",
                "",
                *workflow_lines,
                "",
                "## Next",
                "",
                str(payload.get("decision") or ""),
                "",
            ]
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", default="open-duck-t4-stagea")
    parser.add_argument("--accelerator", default="T4")
    parser.add_argument("--attempts", type=int, default=6)
    parser.add_argument("--delay-s", type=float, default=300.0)
    parser.add_argument("--status-timeout-s", type=int, default=30)
    parser.add_argument("--new-timeout-s", type=int, default=60)
    parser.add_argument("--workflow-timeout-s", type=int, default=14400)
    parser.add_argument("--exec-remote-timeout-s", type=int, default=14400)
    parser.add_argument(
        "--execution-mode",
        choices=["detached", "exec"],
        default="detached",
        help=(
            "Use detached console polling by default. The exec mode blocks "
            "inside colab exec and can hang if the hosted runtime disappears."
        ),
    )
    parser.add_argument(
        "--run-workflow",
        action="store_true",
        help="Launch the valid Stage A workflow after a session is visible.",
    )
    parser.add_argument(
        "--adopt-existing-session",
        action="store_true",
        help=(
            "Before allocating, adopt the unique locally tracked active Colab "
            "session reported by `colab status`. This is intended for a "
            "browser-kept-alive CLI session."
        ),
    )
    parser.add_argument(
        "--wait-for-existing-session",
        action="store_true",
        help=(
            "When adopting an existing session, poll for a unique visible "
            "session before falling back to allocation/no-create behavior."
        ),
    )
    parser.add_argument(
        "--wait-timeout-s",
        type=float,
        default=0.0,
        help="Maximum seconds to wait for a unique existing session.",
    )
    parser.add_argument(
        "--wait-interval-s",
        type=float,
        default=30.0,
        help="Polling interval for --wait-for-existing-session.",
    )
    parser.add_argument(
        "--no-create",
        action="store_true",
        help=(
            "Do not call `colab new`. Use this with --adopt-existing-session "
            "for a preflight that only uses an already visible session."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for retry reports.",
    )
    parser.add_argument(
        "--workflow-output-root",
        type=Path,
        default=ROOT / "outputs" / "analysis" / "colab_cli_stage_a_rate175_prior",
    )
    args = parser.parse_args()

    payload: dict[str, object] = {
        "status": "HOLD_COLAB_GPU_ALLOCATION",
        "generated_at": timestamp(),
        "no_robot_ssh_deploy_grounded_replay": True,
        "session": args.session,
        "accelerator": args.accelerator,
        "attempts_requested": args.attempts,
        "adopt_existing_session": args.adopt_existing_session,
        "wait_for_existing_session": args.wait_for_existing_session,
        "wait_timeout_s": args.wait_timeout_s,
        "wait_interval_s": args.wait_interval_s,
        "no_create": args.no_create,
        "workflow_started": False,
        "allocation_attempts": [],
        "workflow_command": stage_a_workflow_command(args),
    }

    session_ready = False
    allocation_attempts: list[dict[str, object]] = []
    if args.adopt_existing_session:
        if args.wait_for_existing_session:
            adopt_result = wait_for_unique_existing_session(
                timeout_s=max(0.0, args.wait_timeout_s),
                interval_s=max(1.0, args.wait_interval_s),
                status_timeout_s=args.status_timeout_s,
            )
        else:
            adopt_result = find_unique_existing_session(args.status_timeout_s)
        payload["adopt_existing_session_result"] = adopt_result
        if adopt_result.get("status") == "PASS_UNIQUE_EXISTING_SESSION":
            args.session = str(adopt_result["selected_session"])
            payload["session"] = args.session
            payload["workflow_command"] = stage_a_workflow_command(args)
            allocation_attempts.append(
                {
                    "attempt": 0,
                    "command_label": "colab status",
                    "status": "PASS_ADOPTED_EXISTING_SESSION",
                    "detail": f"adopted unique session {args.session}",
                    "result": adopt_result.get("result"),
                }
            )
            session_ready = True

    for index in range(1, args.attempts + 1):
        if session_ready:
            break
        status_result = run_command(
            ["colab", "status", "-s", args.session],
            timeout_s=args.status_timeout_s,
        )
        if session_exists(status_result):
            allocation_attempts.append(
                {
                    "attempt": index,
                    "command_label": "colab status",
                    "status": "PASS_SESSION_VISIBLE",
                    "detail": (status_result.get("stdout") or "").strip(),
                    "result": status_result,
                }
            )
            session_ready = True
            break

        if args.no_create:
            allocation_attempts.append(
                {
                    "attempt": index,
                    "command_label": "colab new",
                    "status": "HOLD_NO_CREATE_SESSION_MISSING",
                    "detail": (
                        f"session {args.session!r} is not visible and "
                        "--no-create was requested"
                    ),
                    "result": status_result,
                }
            )
            break

        new_result = run_command(
            ["colab", "new", "-s", args.session, "--gpu", args.accelerator],
            timeout_s=args.new_timeout_s,
        )
        combined = f"{new_result.get('stdout') or ''}\n{new_result.get('stderr') or ''}"
        if new_result.get("returncode") == 0:
            attempt_status = "PASS_SESSION_CREATED"
            session_ready = True
        elif "Service Unavailable" in combined:
            attempt_status = "HOLD_SERVICE_UNAVAILABLE"
        elif "Backend rejected accelerator" in combined:
            attempt_status = "HOLD_ACCELERATOR_REJECTED"
        else:
            attempt_status = "HOLD_COLAB_NEW_FAILED"
        allocation_attempts.append(
            {
                "attempt": index,
                "command_label": "colab new",
                "status": attempt_status,
                "detail": combined.strip(),
                "result": new_result,
            }
        )
        if session_ready:
            break
        if index < args.attempts and args.delay_s > 0:
            time.sleep(args.delay_s)

    payload["allocation_attempts"] = allocation_attempts
    payload["session_ready"] = session_ready

    if session_ready:
        url_result = run_command(["colab", "url", "-s", args.session], timeout_s=args.status_timeout_s)
        payload["session_url_result"] = url_result
        if url_result.get("returncode") == 0:
            payload["session_url"] = (url_result.get("stdout") or "").strip()

    if session_ready and args.run_workflow:
        workflow_result = run_command(
            stage_a_workflow_command(args),
            timeout_s=args.exec_remote_timeout_s + 900,
        )
        payload["workflow_started"] = True
        payload["workflow_result"] = workflow_result
        payload["status"] = (
            "PASS_WORKFLOW_COMMAND_COMPLETED"
            if workflow_result.get("returncode") == 0
            else "HOLD_WORKFLOW_COMMAND_FAILED"
        )
        payload["decision"] = (
            "Inspect the downloaded Stage A artifacts and run checkpoint sweep."
            if workflow_result.get("returncode") == 0
            else "Workflow command failed; inspect stdout/stderr in the JSON report."
        )
    elif session_ready:
        payload["status"] = "PASS_SESSION_READY_WORKFLOW_NOT_STARTED"
        payload["decision"] = (
            "Run again with --run-workflow, or execute the recorded workflow_command."
        )
    else:
        payload["status"] = "HOLD_COLAB_GPU_ALLOCATION"
        payload["decision"] = (
            "No Colab GPU session became available. Retry later; do not substitute "
            "CPU smoke for a Phase 2 gate."
        )

    write_reports(payload, args.output_dir)
    print(json.dumps({"status": payload["status"], "output_dir": str(args.output_dir)}, sort_keys=True))
    return 0 if session_ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
