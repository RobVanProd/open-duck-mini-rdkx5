#!/usr/bin/env python3
"""Summarize an Open Duck Playground training output directory.

This offline tool reads manifests, stdout/stderr, checkpoint directories, ONNX
exports, and basic reward lines. It does not train, deploy, SSH, or run robot
tests.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
from typing import Any


STEP_RE = re.compile(
    r"^STEP:\s+(?P<step>\d+)\s+reward:\s+(?P<reward>[-+0-9.eE]+)"
    r"\s+reward_std:\s+(?P<reward_std>[-+0-9.eE]+)"
)
CHECKPOINT_RE = re.compile(r"Saving checkpoint \(step:\s*(?P<step>\d+)\):\s*(?P<path>.+)")
EXPORT_RE = re.compile(r"Model exported to:\s*(?P<path>.+)")


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {exc}"}


def parse_stdout(text: str) -> dict[str, Any]:
    steps = []
    checkpoints = []
    exports = []
    observation_size = None
    ppo_params = None
    for line in text.splitlines():
        step_match = STEP_RE.match(line.strip())
        if step_match:
            steps.append(
                {
                    "step": int(step_match.group("step")),
                    "reward": float(step_match.group("reward")),
                    "reward_std": float(step_match.group("reward_std")),
                }
            )
            continue
        checkpoint_match = CHECKPOINT_RE.search(line)
        if checkpoint_match:
            checkpoints.append(
                {
                    "step": int(checkpoint_match.group("step")),
                    "path": checkpoint_match.group("path").strip(),
                }
            )
            continue
        export_match = EXPORT_RE.search(line)
        if export_match:
            exports.append(export_match.group("path").strip())
            continue
        if line.startswith("Observation size:"):
            try:
                observation_size = int(line.split(":", 1)[1].strip())
            except ValueError:
                observation_size = line.split(":", 1)[1].strip()
        if line.startswith("PPO params:"):
            ppo_params = line.split(":", 1)[1].strip()
    return {
        "step_metrics": steps,
        "checkpoints": checkpoints,
        "exports_from_stdout": exports,
        "observation_size": observation_size,
        "ppo_params_raw": ppo_params,
    }


def collect_onnx(run_dir: Path) -> list[dict[str, Any]]:
    items = []
    for path in sorted(run_dir.glob("*.onnx")):
        step = None
        suffix = path.stem.rsplit("_", 1)[-1]
        if suffix.isdigit():
            step = int(suffix)
        items.append(
            {
                "path": str(path),
                "name": path.name,
                "step": step,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return items


def collect_files(run_dir: Path) -> dict[str, Any]:
    manifests = sorted(run_dir.glob("*manifest*.json"))
    stdout = run_dir / "stdout.txt"
    stderr = run_dir / "stderr.txt"
    event_files = sorted(run_dir.glob("events.out.tfevents.*"))
    checkpoint_dirs = [
        path
        for path in sorted(run_dir.iterdir())
        if path.is_dir() and (path / "_CHECKPOINT_METADATA").exists()
    ]
    return {
        "manifests": [str(path) for path in manifests],
        "stdout": str(stdout) if stdout.exists() else None,
        "stderr": str(stderr) if stderr.exists() else None,
        "event_files": [str(path) for path in event_files],
        "checkpoint_dirs": [str(path) for path in checkpoint_dirs],
    }


def warning_summary(path: Path | None, max_lines: int = 50, max_chars: int = 240) -> dict[str, Any]:
    if path is None or not path.exists():
        return {"count": 0, "lines": []}
    needles = ("warning", "error", "traceback", "exception", "illegal", "nan", "inf")
    lines = []
    count = 0
    for line in path.read_text(errors="replace").splitlines():
        low = line.lower()
        if any(needle in low for needle in needles):
            count += 1
            if len(lines) < max_lines:
                lines.append(line[:max_chars] + ("..." if len(line) > max_chars else ""))
    return {"count": count, "lines": lines}


def latest_onnx(onnx_files: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not onnx_files:
        return None
    return sorted(onnx_files, key=lambda item: (-1 if item["step"] is None else item["step"]))[-1]


def decide_status(payload: dict[str, Any]) -> str:
    if not payload["onnx_files"]:
        return "HOLD_NO_ONNX_EXPORT"
    if not payload["stdout_parse"]["step_metrics"]:
        return "HOLD_NO_REWARD_STEP"
    if payload["manifest"].get("returncode") not in (0, None):
        return "HOLD_RUN_RETURNED_NONZERO"
    if payload["non_deployable"]:
        return "INFO_NON_DEPLOYABLE_TRAINING_RUN"
    return "READY_FOR_CANDIDATE_REVIEW"


def markdown(payload: dict[str, Any]) -> str:
    latest = payload.get("latest_onnx")
    lines = [
        "# Training Run Summary",
        "",
        f"status: `{payload['status']}`",
        f"generated_at: `{payload['generated_at']}`",
        f"run_dir: `{payload['run_dir']}`",
        "",
        "## Run",
        "",
        f"- platform: `{payload['manifest'].get('platform')}`",
        f"- returncode: `{payload['manifest'].get('returncode')}`",
        f"- actuator_bridge_enabled: `{payload['manifest'].get('actuator_bridge_enabled')}`",
        f"- target_rate_scale: `{payload['manifest'].get('target_rate_scale')}`",
        f"- actuator_tracking_scale: `{payload['manifest'].get('actuator_tracking_scale')}`",
        f"- non_deployable: `{payload['non_deployable']}`",
    ]
    if latest:
        lines.extend(
            [
                "",
                "## Latest ONNX",
                "",
                f"- path: `{latest['path']}`",
                f"- step: `{latest['step']}`",
                f"- sha256: `{latest['sha256']}`",
                f"- size_bytes: `{latest['size_bytes']}`",
            ]
        )

    lines.extend(["", "## Reward Steps", "", "| step | reward | reward_std |", "|---:|---:|---:|"])
    for item in payload["stdout_parse"]["step_metrics"]:
        lines.append(
            f"| {item['step']} | {item['reward']:.6f} | {item['reward_std']:.6f} |"
        )

    lines.extend(["", "## ONNX Exports", "", "| step | file | sha256 |", "|---:|---|---|"])
    for item in payload["onnx_files"]:
        lines.append(f"| {item['step']} | `{item['name']}` | `{item['sha256']}` |")

    warnings = payload["stderr_warnings"]
    lines.extend(["", "## Warning Lines", ""])
    if warnings["lines"]:
        lines.append(f"Warning/error-like stderr lines found: `{warnings['count']}`")
        lines.append("")
        lines.append("First lines, truncated:")
        lines.append("")
        lines.append("```text")
        lines.extend(warnings["lines"][:20])
        lines.append("```")
    else:
        lines.append("No warning/error-like stderr lines found.")

    lines.extend(
        [
            "",
            "## Next Gate",
            "",
            "Use `tools/package_candidate_policy.py` on the latest ONNX only after",
            "the run is intended as a candidate and the required sim-gate evidence",
            "exists. This summary does not approve robot testing.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize a Playground training/smoke output directory."
    )
    parser.add_argument("run_dir")
    parser.add_argument("--output-md")
    parser.add_argument("--output-json")
    parser.add_argument(
        "--non-deployable",
        action="store_true",
        help="Force non-deployable status for smoke/debug runs.",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    if not run_dir.exists():
        print(f"Missing run directory: {run_dir}", file=sys.stderr)
        return 2

    files = collect_files(run_dir)
    manifest_path = run_dir / "smoke_manifest.final.json"
    if not manifest_path.exists():
        manifest_path = run_dir / "smoke_manifest.start.json"
    manifest = load_json(manifest_path) if manifest_path.exists() else {}
    stdout_path = Path(files["stdout"]) if files["stdout"] else None
    stderr_path = Path(files["stderr"]) if files["stderr"] else None
    stdout_text = stdout_path.read_text(errors="replace") if stdout_path else ""
    stdout_parse = parse_stdout(stdout_text)
    onnx_files = collect_onnx(run_dir)
    non_deployable = bool(
        args.non_deployable
        or "smoke" in str(run_dir)
        or "not a deployable policy" in json.dumps(manifest).lower()
    )

    payload = {
        "generated_at": timestamp(),
        "run_dir": str(run_dir),
        "files": files,
        "manifest_path": str(manifest_path) if manifest_path.exists() else None,
        "manifest": manifest,
        "stdout_parse": stdout_parse,
        "onnx_files": onnx_files,
        "latest_onnx": latest_onnx(onnx_files),
        "stderr_warnings": warning_summary(stderr_path),
        "non_deployable": non_deployable,
    }
    payload["status"] = decide_status(payload)

    text = markdown(payload)
    if args.output_json:
        output_json = Path(args.output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(text)
    else:
        print(text)

    return 1 if payload["status"].startswith("HOLD") else 0


if __name__ == "__main__":
    raise SystemExit(main())
