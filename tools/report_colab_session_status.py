#!/usr/bin/env python3
"""Report google-colab-cli session readiness for offline training handoff.

This tool is read-only. It does not start training, create sessions, SSH, deploy,
or touch the robot. Its purpose is to make the next CUDA/A100 handoff explicit:
which Colab sessions are visible, which common session names are missing, and
the exact Phase 2 B0E command to run once a session is available.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/COLAB_SESSION_STATUS.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/colab_session_status.json"
DEFAULT_SESSIONS = ["open-duck-l4", "open-duck-a100", "open-duck-a100a"]


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def run(command: list[str], timeout_s: int = 30) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_s,
        )
        return {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "ok": completed.returncode == 0,
        }
    except FileNotFoundError as exc:
        return {
            "command": command,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "ok": False,
            "missing_executable": command[0],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "ok": False,
            "timeout": True,
        }


def combined_text(result: dict[str, Any]) -> str:
    return ((result.get("stdout") or "") + (result.get("stderr") or "")).strip()


def phase2_b0e_command(session: str) -> list[str]:
    return [
        "python3",
        "tools/run_colab_cli_cuda_workflow.py",
        "--workflow",
        "phase2-b0e",
        "--session",
        session,
        "--candidate-name",
        "phase2_b0e_motion_preserving_tracking_cuda",
        "--candidate-timeout-s",
        "10800",
        "--candidate-checkpoint-sweep",
        "--candidate-checkpoint-sweep-commands",
        "0.0,0.08",
        "--candidate-checkpoint-sweep-duration",
        "1.0",
        "--candidate-checkpoint-sweep-jax-platform",
        "cpu",
        "--candidate-checkpoint-sweep-timeout-s",
        "7200",
        "--run",
    ]


def shell_join(command: list[str]) -> str:
    import shlex

    return " ".join(shlex.quote(part) for part in command)


def collect(args: argparse.Namespace) -> dict[str, Any]:
    colab_path = shutil.which("colab")
    payload: dict[str, Any] = {
        "timestamp": timestamp(),
        "robot_touched": False,
        "training_started": False,
        "deploy_performed": False,
        "colab_executable": colab_path,
        "sessions_command": None,
        "session_status": {},
        "recommended_session": None,
        "recommended_phase2_b0e_command": None,
    }

    if colab_path is None:
        payload["status"] = "HOLD_COLAB_CLI_MISSING"
        return payload

    sessions = run(["colab", "sessions"], timeout_s=args.timeout_s)
    payload["sessions_command"] = sessions

    visible_text = combined_text(sessions)
    for session in args.sessions:
        status = run(["colab", "status", "-s", session], timeout_s=args.timeout_s)
        text = combined_text(status)
        exists = status["ok"] and "not found" not in text.lower()
        payload["session_status"][session] = {
            "exists": exists,
            "status_command": status,
            "text": text,
        }
        if exists and payload["recommended_session"] is None:
            payload["recommended_session"] = session

    if payload["recommended_session"]:
        command = phase2_b0e_command(payload["recommended_session"])
        payload["recommended_phase2_b0e_command"] = command
        payload["status"] = "PASS_COLAB_SESSION_VISIBLE"
    elif sessions["ok"] and "no active sessions" in visible_text.lower():
        payload["status"] = "HOLD_NO_ACTIVE_COLAB_SESSION"
    else:
        payload["status"] = "HOLD_COLAB_SESSION_NOT_MATCHED"

    return payload


def write_md(payload: dict[str, Any], output_md: Path) -> None:
    lines = [
        "# Colab Session Status",
        "",
        f"status: `{payload['status']}`",
        f"timestamp: `{payload['timestamp']}`",
        "",
        "- robot_touched: `false`",
        "- training_started: `false`",
        "- deploy_performed: `false`",
        f"- colab_executable: `{payload.get('colab_executable')}`",
        "",
        "## Visible Sessions",
        "",
        "```text",
        combined_text(payload.get("sessions_command") or {}) or "NO_OUTPUT",
        "```",
        "",
        "## Probed Session Names",
        "",
        "| session | exists | status |",
        "|---|---:|---|",
    ]
    for session, info in payload.get("session_status", {}).items():
        text = (info.get("text") or "").replace("\n", " ") or "NO_OUTPUT"
        lines.append(f"| `{session}` | `{info.get('exists')}` | `{text}` |")

    lines.extend(["", "## Next Command", ""])
    command = payload.get("recommended_phase2_b0e_command")
    if command:
        lines.extend(
            [
                "Run this only after confirming the session is the desired CUDA/A100 runtime:",
                "",
                "```bash",
                shell_join(command),
                "```",
            ]
        )
    else:
        lines.extend(
            [
                "No matching active session is visible. Do not launch B0E yet.",
                "",
                "Create or reconnect a Colab session, then rerun:",
                "",
                "```bash",
                "python3 tools/report_colab_session_status.py",
                "```",
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This report is infrastructure-only evidence. It does not approve robot",
            "validation and does not change the Phase 2 gate. A B0E artifact is useful",
            "only after the corrected-bridge rough-terrain gentle-push gates are run",
            "and reviewed locally.",
        ]
    )
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sessions", nargs="+", default=DEFAULT_SESSIONS)
    parser.add_argument("--timeout-s", type=int, default=30)
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    payload = collect(args)
    output_md = Path(args.output_md)
    output_json = Path(args.output_json)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_md(payload, output_md)
    print(payload["status"])
    if payload.get("recommended_session"):
        print("recommended_session", payload["recommended_session"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
