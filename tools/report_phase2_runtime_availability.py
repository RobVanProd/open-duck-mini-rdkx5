#!/usr/bin/env python3
"""Report whether Phase 2 Stage A has a safe GPU runtime available.

This is an offline guard. It does not start training, SSH, deploy, touch the
robot, or run grounded replay. It only records whether a Colab session can be
adopted or whether local ROCm appears free enough for an explicit local run.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_MD = ROOT / "outputs" / "analysis" / "PHASE2_RUNTIME_AVAILABILITY.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs" / "analysis" / "phase2_runtime_availability.json"


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(command: list[str], *, timeout_s: int = 30) -> dict[str, object]:
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
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timed_out": True,
        }


def parse_colab_sessions(text: str) -> list[str]:
    sessions: list[str] = []
    seen: set[str] = set()
    for line in text.splitlines():
        if " | Hardware: " not in line:
            continue
        match = re.match(r"^\[([^\]]+)\]\s+", line.strip())
        if not match:
            continue
        name = match.group(1).strip()
        if not name or name in {"?", "colab"} or name in seen:
            continue
        seen.add(name)
        sessions.append(name)
    return sessions


def parse_rocm_pids(text: str) -> list[int]:
    pids: list[int] = []
    for match in re.finditer(r"PID\s+(\d+)\s+is using", text):
        pids.append(int(match.group(1)))
    return sorted(set(pids))


def process_info(pid: int) -> dict[str, object]:
    result = run(["ps", "-p", str(pid), "-o", "pid=,ppid=,stat=,etime=,pcpu=,pmem=,cmd="])
    text = (result.get("stdout") or "").strip()
    return {
        "pid": pid,
        "exists": result.get("returncode") == 0 and bool(text),
        "ps": text,
        "result": result,
    }


def local_gpu_blockers(processes: list[dict[str, object]]) -> list[dict[str, object]]:
    blockers: list[dict[str, object]] = []
    for process in processes:
        text = str(process.get("ps") or "")
        if not text:
            continue
        # Treat any long-running non-trivial GPU owner as a blocker. The tool is
        # intentionally conservative; an operator can stop or bless the process.
        if "rocm-smi" in text:
            continue
        blockers.append(process)
    return blockers


def read_stage_a_status() -> dict[str, object] | None:
    path = ROOT / "outputs" / "analysis" / "phase2_stage_a_postrun_status.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {"status": "HOLD_STAGE_A_STATUS_JSON_INVALID", "path": str(path)}


def build_payload() -> dict[str, object]:
    colab_sessions_result = run(["colab", "sessions"])
    colab_status_result = run(["colab", "status"])
    colab_text = "\n".join(
        [
            str(colab_sessions_result.get("stdout") or ""),
            str(colab_sessions_result.get("stderr") or ""),
            str(colab_status_result.get("stdout") or ""),
            str(colab_status_result.get("stderr") or ""),
        ]
    )
    sessions = parse_colab_sessions(colab_text)

    rocm_result = run(["rocm-smi", "--showuse", "--showmemuse", "--showpidgpus"])
    rocm_text = f"{rocm_result.get('stdout') or ''}\n{rocm_result.get('stderr') or ''}"
    pids = parse_rocm_pids(rocm_text)
    processes = [process_info(pid) for pid in pids]
    blockers = local_gpu_blockers(processes)

    stage_a_status = read_stage_a_status()
    checkpoint_count = None
    if isinstance(stage_a_status, dict):
        checkpoint_count = stage_a_status.get("checkpoint_count")

    if sessions:
        status = "PASS_COLAB_SESSION_AVAILABLE"
        decision = (
            "Run the Stage A launcher with --adopt-existing-session --no-create "
            "--run-workflow."
        )
    elif rocm_result.get("returncode") == 0 and not blockers:
        status = "PASS_LOCAL_ROCM_APPEARS_AVAILABLE"
        decision = (
            "Local ROCm appears free. A local Stage A smoke may be run only as "
            "debug/fallback evidence unless it clears the canonical gates."
        )
    else:
        status = "HOLD_GPU_RUNTIME_UNAVAILABLE"
        decision = (
            "No adoptable Colab session is visible and local ROCm has active "
            "GPU owner processes. Do not start Stage A until one runtime is free."
        )

    return {
        "status": status,
        "generated_at": timestamp(),
        "offline_only": True,
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "grounded_replay_performed": False,
        "colab_sessions": sessions,
        "colab_sessions_result": colab_sessions_result,
        "colab_status_result": colab_status_result,
        "rocm_result": rocm_result,
        "rocm_pids": pids,
        "rocm_processes": processes,
        "local_gpu_blockers": blockers,
        "stage_a_postrun_status": stage_a_status,
        "stage_a_checkpoint_count": checkpoint_count,
        "decision": decision,
        "adopt_colab_command": (
            "python3 tools/launch_phase2_stage_a_rate175_colab.py "
            "--adopt-existing-session --no-create --run-workflow "
            "--output-dir outputs/analysis/phase2_stage_a_rate175_colab_adopt_existing"
        ),
        "wait_adopt_colab_command": (
            "python3 tools/launch_phase2_stage_a_rate175_colab.py "
            "--adopt-existing-session --wait-for-existing-session "
            "--wait-timeout-s 3600 --wait-interval-s 30 --no-create "
            "--run-workflow "
            "--output-dir outputs/analysis/phase2_stage_a_rate175_colab_wait_adopt"
        ),
    }


def write_reports(payload: dict[str, object], md_path: Path, json_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    blockers = payload.get("local_gpu_blockers")
    blocker_lines: list[str] = []
    if isinstance(blockers, list) and blockers:
        for blocker in blockers:
            if isinstance(blocker, dict):
                blocker_lines.append(f"- `{blocker.get('ps')}`")
    else:
        blocker_lines.append("- None detected.")

    sessions = payload.get("colab_sessions")
    session_lines: list[str] = []
    if isinstance(sessions, list) and sessions:
        session_lines = [f"- `{session}`" for session in sessions]
    else:
        session_lines = ["- None detected."]

    md_path.write_text(
        "\n".join(
            [
                "# Phase 2 Runtime Availability",
                "",
                f"status: `{payload.get('status')}`",
                f"generated_at: `{payload.get('generated_at')}`",
                "",
                "Offline only. No robot, SSH, deploy, grounded replay, training-result",
                "promotion, or runtime behavior change was performed.",
                "",
                "## Colab Sessions",
                "",
                *session_lines,
                "",
                "## Local ROCm GPU Owners",
                "",
                *blocker_lines,
                "",
                "## Stage A Checkpoint State",
                "",
                f"- checkpoint_count: `{payload.get('stage_a_checkpoint_count')}`",
                "",
                "## Decision",
                "",
                str(payload.get("decision") or ""),
                "",
                "## Commands",
                "",
                "Adopt visible Colab session:",
                "",
                "```bash",
                str(payload.get("adopt_colab_command") or ""),
                "```",
                "",
                "Wait for a visible Colab session:",
                "",
                "```bash",
                str(payload.get("wait_adopt_colab_command") or ""),
                "```",
                "",
            ]
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    args = parser.parse_args()

    payload = build_payload()
    write_reports(payload, args.output_md, args.output_json)
    print(json.dumps({"status": payload["status"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
