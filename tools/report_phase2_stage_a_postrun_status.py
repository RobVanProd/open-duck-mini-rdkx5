#!/usr/bin/env python3
"""Report Phase 2 Stage A post-run checkpoint readiness.

This helper is offline-only. It does not train, SSH, deploy, touch the robot,
or run grounded replay. It scans a Stage A artifact root for exported ONNX
checkpoints, records hashes, and prints the corrected-bridge checkpoint sweep
command that must run before any checkpoint can be promoted.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import shlex


ROOT = Path(__file__).resolve().parents[1]


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def discover_onnx(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        path
        for path in root.rglob("*.onnx")
        if path.is_file() and "__MACOSX" not in path.parts
    )


def discover_selected_checkpoint(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*selected_checkpoint*.json") if path.is_file())


def build_sweep_command(args: argparse.Namespace, policies: list[Path]) -> list[str]:
    return [
        args.env_python,
        "tools/sweep_candidate_checkpoints.py",
        "--policies",
        *[str(path) for path in policies],
        "--fit-json",
        args.fit_json,
        "--playground-path",
        args.playground_path,
        "--env-python",
        args.env_python,
        "--commands",
        args.commands,
        "--duration",
        str(args.duration),
        "--bridge-mode",
        "fitted",
        "--mode-name",
        "corrected_fitted",
        "--jax-platform",
        args.jax_platform,
        "--velocity-envelope",
        args.velocity_envelope,
        "--output-dir",
        str(args.sweep_output_dir),
        "--output-md",
        str(args.sweep_output_dir / "CANDIDATE_CHECKPOINT_SWEEP.md"),
        "--output-json",
        str(args.sweep_output_dir / "candidate_checkpoint_sweep.json"),
        "--run",
    ]


def build_report(payload: dict[str, object]) -> str:
    checkpoints = payload["checkpoints"]
    selected = payload["selected_checkpoint_files"]
    lines = [
        "# Phase 2 Stage A Post-Run Status",
        "",
        f"status: `{payload['status']}`",
        f"generated_at: `{payload['generated_at']}`",
        "",
        "Offline only. No robot, SSH, deploy, grounded replay, training-result",
        "promotion, or runtime behavior change was performed.",
        "",
        "## Artifact Root",
        "",
        f"- root: `{payload['artifact_root']}`",
        f"- exists: `{payload['artifact_root_exists']}`",
        "",
        "## Exported ONNX Checkpoints",
        "",
    ]
    if checkpoints:
        lines.extend(["| path | sha256 |", "|---|---|"])
        for item in checkpoints:
            lines.append(f"| `{item['path']}` | `{item['sha256']}` |")
    else:
        lines.append("- None found.")

    lines.extend(["", "## Selected Checkpoint Metadata", ""])
    if selected:
        for item in selected:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None found.")

    lines.extend(["", "## Next", ""])
    if payload.get("sweep_command_shell"):
        lines.extend(
            [
                "Run the corrected-bridge checkpoint sweep:",
                "",
                "```bash",
                str(payload["sweep_command_shell"]),
                "```",
            ]
        )
    else:
        lines.append(
            "No exported ONNX checkpoints are available. Re-run Stage A on a "
            "GPU session; do not substitute CPU smoke for a Phase 2 gate."
        )
    return "\n".join(lines).rstrip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=ROOT / "outputs" / "analysis" / "colab_cli_stage_a_rate175_prior",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=ROOT / "outputs" / "analysis" / "PHASE2_STAGE_A_POSTRUN_STATUS.md",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=ROOT / "outputs" / "analysis" / "phase2_stage_a_postrun_status.json",
    )
    parser.add_argument("--fit-json", default="outputs/analysis/actuator_response_fit_corrected_knee.json")
    parser.add_argument("--playground-path", default="../Open_Duck_Playground")
    parser.add_argument("--env-python", default="../envs/open-duck-playground/bin/python")
    parser.add_argument("--commands", default="0.0,0.08")
    parser.add_argument("--duration", type=float, default=1.0)
    parser.add_argument("--jax-platform", default="cpu")
    parser.add_argument("--velocity-envelope", default="2.0,3.25")
    parser.add_argument(
        "--sweep-output-dir",
        type=Path,
        default=ROOT / "outputs" / "analysis" / "phase2_stage_a_rate175_checkpoint_sweep",
    )
    args = parser.parse_args()

    artifact_root = args.artifact_root
    policies = discover_onnx(artifact_root)
    selected_files = discover_selected_checkpoint(artifact_root)
    checkpoints = [
        {
            "path": str(path),
            "sha256": sha256_file(path),
        }
        for path in policies
    ]
    sweep_command = build_sweep_command(args, policies) if policies else []
    payload: dict[str, object] = {
        "status": "PASS_STAGE_A_CHECKPOINTS_READY" if policies else "HOLD_STAGE_A_CHECKPOINTS_MISSING",
        "generated_at": timestamp(),
        "offline_only": True,
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "grounded_replay_performed": False,
        "training_result_promoted": False,
        "artifact_root": str(artifact_root),
        "artifact_root_exists": artifact_root.exists(),
        "checkpoint_count": len(policies),
        "checkpoints": checkpoints,
        "selected_checkpoint_files": [str(path) for path in selected_files],
        "sweep_command": sweep_command,
        "sweep_command_shell": shell_join(sweep_command) if sweep_command else None,
    }

    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(build_report(payload) + "\n")
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": payload["status"], "checkpoint_count": len(policies)}, sort_keys=True))
    return 0 if policies else 2


if __name__ == "__main__":
    raise SystemExit(main())
