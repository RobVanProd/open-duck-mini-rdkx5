#!/usr/bin/env python3
"""Summarize the Phase 2 z=0.0075 post-push A100 training result.

This report is offline-only. It reads the downloaded Colab training summary and
local compact checkpoint sweep, then records whether any exported checkpoint is
worth promoting to the full corrected-bridge gates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_DIR = ROOT / "outputs/analysis/phase2_z0075_post_push_stability_a100_20260704"
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_Z0075_POST_PUSH_STABILITY_A100_RESULT.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_z0075_post_push_stability_a100_result.json"


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def build_payload(run_dir: Path) -> dict[str, Any]:
    training_json = run_dir / "phase2_z0075_post_push_stability_cuda_training_run_summary.json"
    sweep_json = run_dir / "checkpoint_sweep/candidate_checkpoint_sweep.json"
    exit_status = run_dir / "COLAB_CLI_EXIT_STATUS.txt"
    bundle = (
        ROOT
        / "outputs/analysis/colab_cli/open-duck-phase2-a100-phase2-b0g-20260704T042437Z/final_download/open_duck_colab_cli_phase2-b0g_20260704T042553Z_artifacts.tar.gz"
    )

    training = load_json(training_json)
    sweep = load_json(sweep_json)
    decisions = sweep.get("promotion_decisions", [])
    promoted = [d for d in decisions if d.get("promote")]

    latest_onnx = training.get("latest_onnx", {})
    checkpoint_files = sorted((run_dir / "checkpoints").glob("*.onnx"))

    best_by_ratio = None
    for decision in decisions:
        ratio = decision.get("positive_command_tracking_ratio_mean")
        if ratio is None:
            continue
        if best_by_ratio is None or ratio > best_by_ratio.get("positive_command_tracking_ratio_mean", -1):
            best_by_ratio = decision

    payload = {
        "status": "HOLD_NO_PROMOTABLE_CHECKPOINT" if not promoted else "PASS_PROMOTABLE_CHECKPOINT_FOUND",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "offline_phase2_a100_training_result",
        "robot_touched": False,
        "ssh_performed": False,
        "deploy_performed": False,
        "grounded_replay_performed": False,
        "run_dir": rel(run_dir),
        "training_summary": {
            "path": rel(training_json),
            "sha256": sha256(training_json),
            "status": training.get("status"),
            "returncode": training.get("manifest", {}).get("returncode"),
            "elapsed_s": training.get("manifest", {}).get("elapsed_s"),
            "latest_onnx": latest_onnx,
            "reward_steps": training.get("reward_steps", []),
        },
        "colab_exit_status": {
            "path": rel(exit_status),
            "sha256": sha256(exit_status),
            "text": exit_status.read_text().strip() if exit_status.exists() else None,
        },
        "downloaded_bundle": {
            "path": rel(bundle),
            "sha256": sha256(bundle),
            "size_bytes": bundle.stat().st_size if bundle.exists() else None,
        },
        "checkpoint_files": [
            {
                "path": rel(path),
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
            for path in checkpoint_files
        ],
        "checkpoint_sweep": {
            "path": rel(sweep_json),
            "sha256": sha256(sweep_json),
            "commands": [0.0, 0.08],
            "duration_s": 1.0,
            "bridge_mode": "fitted",
            "fit_json": "outputs/analysis/actuator_response_fit_corrected_knee.json",
            "result_count": len(sweep.get("results", [])),
            "promotion_decisions": decisions,
            "promoted": promoted,
            "best_by_positive_command_ratio": best_by_ratio,
        },
        "decision": {
            "promote_to_full_gates": bool(promoted),
            "full_gates_run": False,
            "full_gates_skipped_reason": None
            if promoted
            else "compact sweep found no checkpoint with meaningful in-envelope forward progress",
            "next_recommendation": "do not promote this b0g PPO result; return to teacher-action or trust-region continuity rather than another scalar reward tweak"
            if not promoted
            else "run full corrected-bridge multi-seed gates before any packaging or robot work",
        },
    }
    return payload


def render_md(payload: dict[str, Any]) -> str:
    training = payload["training_summary"]
    sweep = payload["checkpoint_sweep"]
    latest = training.get("latest_onnx") or {}
    lines = [
        "# Phase 2 z=0.0075 Post-Push Stability A100 Result",
        "",
        f"status: `{payload['status']}`",
        f"generated_at: `{payload['generated_at']}`",
        "",
        "## Scope",
        "",
        "- Offline sim/training analysis only.",
        "- No robot tests, SSH, deploy, grounded replay, or runtime behavior changes were performed.",
        "- This report summarizes the A100 `phase2-b0g` run and the local compact corrected-bridge checkpoint sweep.",
        "",
        "## Training",
        "",
        f"- run_dir: `{payload['run_dir']}`",
        f"- colab_exit_status: `{payload['colab_exit_status']['text']}`",
        f"- training_status: `{training.get('status')}`",
        f"- returncode: `{training.get('returncode')}`",
        f"- elapsed_s: `{training.get('elapsed_s')}`",
        f"- latest_onnx: `{latest.get('path')}`",
        f"- latest_onnx_sha256: `{latest.get('sha256')}`",
        f"- downloaded_bundle_sha256: `{payload['downloaded_bundle']['sha256']}`",
        "",
        "### Exported Checkpoints",
        "",
        "| checkpoint | sha256 | size_bytes |",
        "|---|---|---:|",
    ]
    for item in payload["checkpoint_files"]:
        lines.append(f"| `{item['path']}` | `{item['sha256']}` | {item['size_bytes']} |")

    lines += [
        "",
        "## Compact Corrected-Bridge Sweep",
        "",
        f"- sweep_json: `{sweep['path']}`",
        f"- commands: `{sweep['commands']}`",
        f"- duration_s: `{sweep['duration_s']}`",
        f"- bridge_mode: `{sweep['bridge_mode']}`",
        f"- corrected_bridge: `{sweep['fit_json']}`",
        "",
        "| policy | decision | pass_count | max_vel_p95 | max_tracking_p95 | x=0.08 ratio |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for decision in sweep["promotion_decisions"]:
        lines.append(
            "| `{policy}` | `{status}` | {pass_count}/{required} | {vel:.4f} | {tracking:.4f} | {ratio:.4f} |".format(
                policy=decision.get("policy_label"),
                status=decision.get("status"),
                pass_count=decision.get("pass_count"),
                required=decision.get("required_command_count"),
                vel=decision.get("max_pitch_sent_target_velocity_p95_rad_s") or 0.0,
                tracking=decision.get("max_pitch_tracking_p95_rad") or 0.0,
                ratio=decision.get("positive_command_tracking_ratio_mean") or 0.0,
            )
        )

    best = sweep.get("best_by_positive_command_ratio") or {}
    lines += [
        "",
        "## Decision",
        "",
        f"- promote_to_full_gates: `{payload['decision']['promote_to_full_gates']}`",
        f"- full_gates_run: `{payload['decision']['full_gates_run']}`",
        f"- full_gates_skipped_reason: `{payload['decision']['full_gates_skipped_reason']}`",
        f"- best_compact_screen_policy: `{best.get('policy_label')}`",
        f"- best_compact_screen_x008_ratio: `{best.get('positive_command_tracking_ratio_mean')}`",
        "",
        "The A100 training run completed and exported valid ONNX checkpoints, but all",
        "three checkpoints failed the compact corrected-bridge screen. The failure is",
        "not over-envelope velocity or action saturation; it is insufficient forward",
        "progress while tracking remains around the prior plateau. No checkpoint from",
        "this run is promoted to full gates or robot work.",
        "",
        f"next_recommendation: `{payload['decision']['next_recommendation']}`",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON)
    args = parser.parse_args()

    payload = build_payload(args.run_dir)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2) + "\n")
    args.output_md.write_text(render_md(payload))
    print(args.output_md)
    print(args.output_json)
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
