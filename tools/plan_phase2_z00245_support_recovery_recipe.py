#!/usr/bin/env python3
"""Plan the Phase 2 z=0.00245 support-recovery continuation.

This is a read-only planning tool. It records the next allowed step after the
z=0.00245 one-shot BC/relabel branch closed: a bounded on-policy terrain
support run with the corrected envelope active, followed by seed-5-first gates.

It does not train, SSH, deploy, or touch the robot.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECISION_JSON = (
    ROOT / "outputs/analysis/phase2_z00245_support_recovery_next_decision_20260702.json"
)
DEFAULT_BRIDGE_JSON = ROOT / "outputs/analysis/actuator_response_fit_corrected_knee.json"
DEFAULT_SOURCE_MANIFEST = ROOT / "outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_Z00245_ON_POLICY_SUPPORT_RECIPE.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_z00245_on_policy_support_recipe.json"
DEFAULT_RESTORE_CHECKPOINT = (
    ROOT
    / "outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu"
    / "smoke_20260628T031553Z_gpu/2026_06_27_232221_491520"
)


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json_optional(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        return {"_read_error": str(exc), "_path": rel(path)}


def file_sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checkpoint_digest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": rel(path), "present": False}
    if path.is_file():
        return {"path": rel(path), "present": True, "sha256": file_sha256(path)}
    files = sorted(item for item in path.rglob("*") if item.is_file())
    digest = hashlib.sha256()
    for item in files:
        relative = item.relative_to(path).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_sha256(item).encode("ascii"))
        digest.update(b"\0")
    return {
        "path": rel(path),
        "present": True,
        "file_count": len(files),
        "tree_sha256": digest.hexdigest(),
    }


def multiline_shell(parts: list[str]) -> str:
    return (" " + "\\\n" + "    ").join(shlex.quote(part) for part in parts)


def terrain_label(value: str) -> str:
    text = str(value).strip()
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text.startswith("0."):
        return "z" + text[2:]
    return "z" + text.replace(".", "p")


def colab_command(
    *,
    session: str,
    candidate_name: str,
    terrain_z: str,
    timesteps: int,
    package_only: bool,
) -> list[str]:
    parts = [
        "python3",
        "tools/run_colab_cli_cuda_workflow.py",
        "--workflow",
        "phase2-z0025-boundary",
        "--session",
        session,
        "--candidate-name",
        candidate_name,
        "--phase2-terrain-hfield-z-scale",
        terrain_z,
        "--phase2-num-timesteps",
        str(timesteps),
        "--phase2-ppo-num-envs",
        "64",
        "--phase2-ppo-batch-size",
        "512",
        "--phase2-ppo-num-minibatches",
        "4",
        "--phase2-ppo-num-updates-per-batch",
        "2",
        "--phase2-target-rate-scale",
        "-0.01",
        "--phase2-actuator-tracking-scale",
        "-0.005",
        "--phase2-command-progress-required-ratio",
        "0.45",
        "--candidate-checkpoint-sweep",
        "--candidate-checkpoint-sweep-commands",
        "0.0,0.08",
        "--candidate-checkpoint-sweep-duration",
        "1.0",
        "--candidate-checkpoint-sweep-jax-platform",
        "cpu",
        "--candidate-timeout-s",
        "10800",
    ]
    if package_only:
        parts.append("--package-only")
    else:
        parts.append("--run")
    return parts


def short_gate_command(policy: str, command_x: str, terrain_z: str, output_dir: str) -> list[str]:
    return [
        "python3",
        "tools/run_candidate_seed_sweep.py",
        "--policy",
        policy,
        "--fit-json",
        "outputs/analysis/actuator_response_fit_corrected_knee.json",
        "--playground-path",
        "../Open_Duck_Playground",
        "--env-python",
        "../envs/open-duck-playground/bin/python",
        "--task",
        "rough_terrain_backlash",
        "--command-x",
        command_x,
        "--duration",
        "2",
        "--seeds",
        "5",
        "--bridge-mode",
        "fitted",
        "--terrain-hfield-z-scale",
        terrain_z,
        "--output-dir",
        output_dir,
    ]


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    decision_path = Path(args.decision_json)
    bridge_path = Path(args.bridge_json)
    source_path = Path(args.source_manifest)
    restore_path = Path(args.restore_checkpoint)
    decision = read_json_optional(decision_path)
    package_cmd = colab_command(
        session=args.session,
        candidate_name=args.candidate_name,
        terrain_z=args.terrain_z,
        timesteps=args.timesteps,
        package_only=True,
    )
    run_cmd = colab_command(
        session=args.session,
        candidate_name=args.candidate_name,
        terrain_z=args.terrain_z,
        timesteps=args.timesteps,
        package_only=False,
    )
    return {
        "status": "PASS_Z00245_ON_POLICY_SUPPORT_RECIPE_READY",
        "stage": "stage_z00245_on_policy_support_recovery",
        "supersedes": [
            "one-shot z=0.00245 recovery BC from z=0.0024 source labels",
            "z=0.0025 boundary recipe as immediate next step",
        ],
        "terrain_hfield_z_scale": float(args.terrain_z),
        "decision_basis": {
            "decision_json": rel(decision_path),
            "decision_status": decision.get("decision"),
            "closed_branch": decision.get("closed_branch"),
        },
        "canonical_inputs": {
            "corrected_bridge": {
                "path": rel(bridge_path),
                "present": bridge_path.exists(),
                "sha256": file_sha256(bridge_path),
            },
            "z0024_source_manifest": {
                "path": rel(source_path),
                "present": source_path.exists(),
                "sha256": file_sha256(source_path),
                "role": "anchor_only_not_direct_failed_state_labels",
            },
            "restore_checkpoint": checkpoint_digest(restore_path),
        },
        "recipe_intent": [
            "Use the existing on-policy phase2-z0025-boundary workflow, but pin terrain to z=0.00245.",
            "Warm-start from the Phase A2 checkpoint; do not train from scratch.",
            "Keep corrected actuator tracking and target-rate costs active during optimization.",
            "Use the z=0.0024 source manifest only as an anchor/behavior prior if explicitly configured, not as copied labels for failed z=0.00245 states.",
            "Gate seed 5 at x=0.0 before x=0.08, then expand to 8-seed and z=0.0024 regression gates only if the short gates pass.",
        ],
        "key_settings": {
            "workflow": "phase2-z0025-boundary",
            "terrain_hfield_z_scale": float(args.terrain_z),
            "num_timesteps": args.timesteps,
            "ppo_num_envs": 64,
            "target_rate_scale": -0.01,
            "actuator_tracking_scale": -0.005,
            "command_progress_required_ratio": 0.45,
            "corrected_bridge_velocity_limit_range_rad_s": [2.0, 3.25],
            "push_enable": False,
            "post_training_primary_gate": f"{terrain_label(args.terrain_z)}_x000/x008_no_push",
        },
        "commands": {
            "package_only": {
                "argv": package_cmd,
                "shell": multiline_shell(package_cmd),
            },
            "preferred_colab_gpu": {
                "argv": run_cmd,
                "shell": multiline_shell(run_cmd),
            },
            "short_gate_order": [
                {
                    "name": "seed5_x000_short",
                    "argv": short_gate_command(
                        "<candidate.onnx>",
                        "0.0",
                        args.terrain_z,
                        "outputs/analysis/phase2_z00245_on_policy_seed5_short_x000",
                    ),
                },
                {
                    "name": "seed5_x008_short",
                    "argv": short_gate_command(
                        "<candidate.onnx>",
                        "0.08",
                        args.terrain_z,
                        "outputs/analysis/phase2_z00245_on_policy_seed5_short_x008",
                    ),
                },
            ],
        },
        "acceptance": [
            "seed 5 z=0.00245 x=0.0 short gate passes first: no fall, no action saturation, no corrected-envelope velocity excess, |vx| near zero",
            "seed 5 z=0.00245 x=0.08 short gate passes second: positive forward motion, no fall, no action saturation, no corrected-envelope velocity excess",
            "z=0.00245 8-seed x=0.0 and x=0.08 gates pass before any promotion",
            "known z=0.0024 regression gates remain clear",
        ],
        "falsifiers": [
            "If seed 5 x=0.0 fails by over-envelope target rate or saturation, stop and do not soften/reweight the same labels again.",
            "If seed 5 x=0.0 fails by base-height/support collapse without velocity excess, generate a structurally different intermediate support target before more BC.",
            "If x=0.0 passes but x=0.08 fails by reverse/low progress, adjust on-policy progress/support balance before scaling to 8 seeds.",
        ],
        "robot_touched": False,
        "ssh_used": False,
        "deploy_performed": False,
        "training_started": False,
    }


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Phase 2 z=0.00245 On-Policy Support Recovery Recipe",
        "",
        f"status: `{payload['status']}`",
        f"stage: `{payload['stage']}`",
        f"terrain_hfield_z_scale: `{payload['terrain_hfield_z_scale']}`",
        "",
        "This is an offline planning artifact. It did not train, SSH, deploy, or touch the robot.",
        "",
        "## Decision Basis",
        "",
        f"- decision_json: `{payload['decision_basis']['decision_json']}`",
        f"- decision_status: `{payload['decision_basis']['decision_status']}`",
        f"- closed_branch: `{payload['decision_basis']['closed_branch']}`",
        "",
        "## Canonical Inputs",
        "",
    ]
    for name, item in payload["canonical_inputs"].items():
        lines.append(f"- `{name}`: `{item}`")
    lines.extend(["", "## Recipe Intent", ""])
    lines.extend(f"- {item}" for item in payload["recipe_intent"])
    lines.extend(["", "## Key Settings", ""])
    for key, value in payload["key_settings"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Package-Only Check", "", "```bash"])
    lines.append(payload["commands"]["package_only"]["shell"])
    lines.extend(["```", "", "## Preferred Colab GPU Command", "", "```bash"])
    lines.append(payload["commands"]["preferred_colab_gpu"]["shell"])
    lines.extend(["```", "", "## Short Gate Order", ""])
    for item in payload["commands"]["short_gate_order"]:
        lines.extend([f"### {item['name']}", "", "```bash", multiline_shell(item["argv"]), "```", ""])
    lines.extend(["## Acceptance", ""])
    lines.extend(f"- {item}" for item in payload["acceptance"])
    lines.extend(["", "## Falsifiers", ""])
    lines.extend(f"- {item}" for item in payload["falsifiers"])
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", default="open-duck-a100-phase2-z00245")
    parser.add_argument("--candidate-name", default="phase2_z00245_on_policy_support_cuda")
    parser.add_argument("--terrain-z", default="0.00245")
    parser.add_argument("--timesteps", type=int, default=81920)
    parser.add_argument("--decision-json", default=str(DEFAULT_DECISION_JSON))
    parser.add_argument("--bridge-json", default=str(DEFAULT_BRIDGE_JSON))
    parser.add_argument("--source-manifest", default=str(DEFAULT_SOURCE_MANIFEST))
    parser.add_argument("--restore-checkpoint", default=str(DEFAULT_RESTORE_CHECKPOINT))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    args = parser.parse_args()

    payload = build_payload(args)
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    write_markdown(payload, output_md)
    print(payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
