#!/usr/bin/env python3
"""Plan the next Phase 2 gate-aware trainable-parent branch.

This is an offline planning/report tool. It does not train, SSH, deploy, run
robot tests, or change runtime behavior. It consumes the latest compact
corrected-bridge evidence and emits the next authorized branch after BC-only
compression failed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shlex
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STEP0_FIDELITY = (
    ROOT
    / "outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_step0_fidelity.json"
)
DEFAULT_STEP0_X008_GATE = (
    ROOT
    / "outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_step0_x008_gate.json"
)
DEFAULT_STEP0_X000_GATE = (
    ROOT
    / "outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_step0_x000_gate.json"
)
DEFAULT_PHASE_CONTACT_DECISION = (
    ROOT
    / "outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_phase_contact_modulated_decision.json"
)
DEFAULT_RECURRENT_DECISION = (
    ROOT
    / "outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_recurrent_h64_s32_decision.json"
)
DEFAULT_RESTORE_CHECKPOINT = (
    ROOT / "outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_step0_checkpoint"
)
DEFAULT_RESTORE_ONNX = (
    ROOT / "outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_step0.onnx"
)
DEFAULT_BRIDGE = ROOT / "outputs/analysis/actuator_response_fit_corrected_knee.json"
DEFAULT_OUTPUT_MD = ROOT / "outputs/analysis/PHASE2_GATE_AWARE_PARENT_NEXT_BRANCH.md"
DEFAULT_OUTPUT_JSON = ROOT / "outputs/analysis/phase2_gate_aware_parent_next_branch.json"


def now_utc() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path | str | None) -> str | None:
    if path is None:
        return None
    p = Path(path)
    try:
        return str(p.resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact(path: Path) -> dict[str, Any]:
    return {
        "path": rel(path),
        "exists": path.exists(),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
    }


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text())


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in parts)


def multiline_shell(parts: list[str]) -> str:
    return (" " + "\\\n" + "    ").join(shlex.quote(str(part)) for part in parts)


def first_aggregate(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not payload:
        return {}
    aggregate = payload.get("aggregate")
    if not isinstance(aggregate, dict) or not aggregate:
        return {}
    first = next(iter(aggregate.values()))
    return first if isinstance(first, dict) else {}


def agg_stat(agg: dict[str, Any], name: str, key: str = "mean") -> Any:
    value = agg.get(name)
    if isinstance(value, dict):
        return value.get(key)
    return value


def seed_rows(payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not payload:
        return []
    rows = []
    for item in payload.get("results", []):
        if not isinstance(item, dict):
            continue
        summary = item.get("summary") if isinstance(item.get("summary"), dict) else {}
        rows.append(
            {
                "seed": item.get("seed"),
                "status": item.get("status"),
                "samples": summary.get("samples"),
                "termination": summary.get("termination_reason"),
                "mean_local_vx_m_s": summary.get("mean_local_vx_m_s"),
                "track_ratio": summary.get("track_ratio"),
                "body_pitch_p95_rad": summary.get("body_pitch_p95_rad"),
                "base_height_min_m": summary.get("base_height_min_m"),
                "max_pitch_vel_p95_rad_s": summary.get("max_pitch_vel_p95_rad_s"),
                "p95_velocity_excess_rad_s": summary.get("max_pitch_vel_limit_excess_rad_s"),
                "max_velocity_excess_rad_s": summary.get(
                    "max_pitch_vel_max_limit_excess_rad_s"
                ),
                "max_tracking_p95_rad": summary.get("max_tracking_p95_rad"),
            }
        )
    return rows


def gate_summary(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    agg = first_aggregate(payload)
    rows = seed_rows(payload)
    pass_count = sum(1 for row in rows if row["status"] == "PASS_CANDIDATE_SIM_GATE")
    return {
        "artifact": artifact(path),
        "runs": len(rows) or agg.get("runs"),
        "pass_count": pass_count if rows else agg.get("duration_complete_count"),
        "fall_count": sum(
            1 for row in rows if row["status"] == "HOLD_CANDIDATE_FALL_OR_TERMINATION"
        )
        if rows
        else agg.get("fall_count"),
        "rows": rows,
        "aggregate": {
            "duration_complete_count": agg.get("duration_complete_count"),
            "fall_count": agg.get("fall_count"),
            "track_ratio_mean": agg_stat(agg, "track_ratio"),
            "mean_local_vx_m_s": agg_stat(agg, "mean_local_vx_m_s"),
            "body_pitch_p95_mean_rad": agg_stat(agg, "body_pitch_p95_rad"),
            "base_height_min_mean_m": agg_stat(agg, "base_height_min_m"),
            "max_p95_velocity_excess_rad_s": agg_stat(
                agg, "max_pitch_vel_limit_excess_rad_s", "max"
            ),
            "max_velocity_excess_rad_s": agg_stat(
                agg, "max_pitch_vel_max_limit_excess_rad_s", "max"
            ),
            "max_tracking_p95_rad": agg_stat(agg, "max_tracking_p95_rad", "max"),
        },
    }


def build_local_smoke_command(args: argparse.Namespace) -> list[str]:
    return [
        "../envs/open-duck-playground/bin/python",
        "tools/run_actuator_bridge_training_smoke.py",
        "--playground-path",
        "../Open_Duck_Playground",
        "--env-python",
        "../envs/open-duck-playground/bin/python",
        "--output-root",
        "outputs/phase2_domain_randomization/gate_aware_parent_iter0_local_smoke",
        "--platform",
        "gpu",
        "--local-rocm-safe-env",
        "--timeout-s",
        "7200",
        "--task",
        "rough_terrain_backlash",
        "--restore-checkpoint-path",
        rel(Path(args.restore_checkpoint)) or args.restore_checkpoint,
        "--restore-policy-kl-scale",
        "8.0",
        "--num-timesteps",
        "40960",
        "--export-min-step",
        "1",
        "--ppo-num-envs",
        "16",
        "--ppo-num-evals",
        "4",
        "--ppo-episode-length",
        "750",
        "--ppo-unroll-length",
        "20",
        "--ppo-batch-size",
        "128",
        "--ppo-num-minibatches",
        "1",
        "--ppo-num-updates-per-batch",
        "2",
        "--lin-vel-x-min",
        "0.06",
        "--lin-vel-x-max",
        "0.10",
        "--lin-vel-y-min",
        "0.0",
        "--lin-vel-y-max",
        "0.0",
        "--ang-vel-yaw-min",
        "0.0",
        "--ang-vel-yaw-max",
        "0.0",
        "--zero-command-probability",
        "0.15",
        "--command-resample-steps",
        "600",
        "--terrain-hfield-z-scale",
        "0.0075",
        "--push-enable",
        "--push-interval-min-s",
        "1.0",
        "--push-interval-max-s",
        "1.5",
        "--push-magnitude-min",
        "0.075",
        "--push-magnitude-max",
        "0.125",
        "--tracking-lin-vel-scale",
        "2.5",
        "--tracking-sigma",
        "0.015",
        "--forward-progress-scale",
        "2.0",
        "--command-progress-scale",
        "1.2",
        "--command-progress-shortfall-scale",
        "-2.0",
        "--command-progress-required-ratio",
        "0.35",
        "--command-progress-warmup-steps",
        "30",
        "--command-progress-failure-enable",
        "--command-progress-failure-min-ratio",
        "0.12",
        "--command-progress-failure-warmup-steps",
        "80",
        "--target-rate-scale",
        "-0.015",
        "--target-rate-huber-delta",
        "0.08",
        "--actuator-tracking-scale",
        "-0.015",
        "--actuator-tracking-huber-delta",
        "0.04",
        "--action-rate-scale",
        "-0.07",
        "--action-magnitude-scale",
        "-0.004",
        "--forward-pitch-scale",
        "-0.5",
        "--forward-pitch-rate-scale",
        "-0.10",
        "--base-height-scale",
        "-0.6",
        "--imitation-scale",
        "0.0",
        "--run",
    ]


def build_colab_command(args: argparse.Namespace) -> list[str]:
    final_args = build_local_smoke_command(args)
    # Drop wrapper-specific and already-forwarded fields from the training arg tail.
    first_training_flag = final_args.index("--restore-checkpoint-path")
    final_training_args = final_args[first_training_flag + 2 :]
    if "--run" in final_training_args:
        final_training_args.remove("--run")
    return [
        "python3",
        "tools/run_colab_cli_cuda_workflow.py",
        "--workflow",
        "phase2-b0g",
        "--session",
        "open-duck-a100-gate-aware-parent",
        "--candidate-name",
        "phase2_gate_aware_parent_iter0",
        "--phase2-restore-checkpoint-path",
        rel(Path(args.restore_checkpoint)) or args.restore_checkpoint,
        "--phase2-terrain-hfield-z-scale",
        "0.0075",
        "--phase2-num-timesteps",
        "122880",
        "--phase2-ppo-num-envs",
        "64",
        "--phase2-ppo-batch-size",
        "512",
        "--candidate-checkpoint-sweep",
        "--candidate-checkpoint-sweep-commands",
        "0.0,0.08",
        "--candidate-checkpoint-sweep-duration",
        "1.0",
        "--candidate-checkpoint-sweep-jax-platform",
        "cpu",
        "--staged-phase-gate-freeze-check",
        "--staged-phase-gate-command-x",
        "0.08",
        "--staged-phase-gate-duration-s",
        "5.0",
        "--staged-phase-gate-bridge-mode",
        "fitted",
        "--staged-phase-gate-platform",
        "cpu",
        "--staged-phase-gate-seeds",
        "0,1,2,6,7",
        "--staged-phase-gate-max-fall-fraction",
        "0.0",
        "--staged-phase-gate-min-track-ratio-mean",
        "0.25",
        "--staged-phase-gate-min-vx-mean",
        "0.02",
        "--phase2-final-training-args-json",
        json.dumps(final_training_args),
        "--run",
    ]


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    step0_fidelity = read_json(Path(args.step0_fidelity)) or {}
    x008 = gate_summary(Path(args.step0_x008_gate))
    x000 = gate_summary(Path(args.step0_x000_gate))
    phase_contact = read_json(Path(args.phase_contact_decision)) or {}
    recurrent = read_json(Path(args.recurrent_decision)) or {}

    x008_pass = x008["pass_count"]
    x008_runs = x008["runs"]
    x000_pass = x000["pass_count"]
    x000_runs = x000["runs"]
    status = (
        "PLAN_GATE_AWARE_ON_POLICY_PARENT"
        if step0_fidelity.get("status") == "PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY"
        and x008_pass is not None
        and x000_pass == x000_runs
        else "HOLD_GATE_AWARE_PARENT_INPUTS_INCOMPLETE"
    )

    report = {
        "status": status,
        "created_utc": now_utc(),
        "scope": "offline planning only; no robot, SSH, deploy, grounded replay, or training",
        "restore_checkpoint": artifact(Path(args.restore_checkpoint)),
        "restore_onnx": artifact(Path(args.restore_onnx)),
        "corrected_bridge": artifact(Path(args.corrected_bridge)),
        "step0_fidelity": {
            "artifact": artifact(Path(args.step0_fidelity)),
            "status": step0_fidelity.get("status"),
            "fidelity": step0_fidelity.get("fidelity"),
        },
        "compact_gates": {
            "x008": x008,
            "x000": x000,
        },
        "closed_bc_branches": {
            "ppo_loc_live_oracle_iter2": {
                "status": "HOLD_PPO_LOC_STEP0_MOVING_GATE",
                "reason": "best trainable restore point so far, but compact x=0.08 is not pass-all",
            },
            "phase_contact_modulated": {
                "artifact": artifact(Path(args.phase_contact_decision)),
                "status": phase_contact.get("status"),
            },
            "recurrent_h64_s32": {
                "artifact": artifact(Path(args.recurrent_decision)),
                "status": recurrent.get("status"),
            },
        },
        "decision": {
            "recommended_next": "Run a bounded gate-aware/on-policy parent iteration from the live-oracle iter2 PPO-loc step-0 checkpoint. Do not train from scratch and do not repeat one-shot BC compression on this aggregate.",
            "why": [
                "The restore checkpoint preserves x=0.0 command semantics 5/5 under the compact rough+push gate.",
                "The same checkpoint is close but not promotable at x=0.08: it passes 3/5, has one fall, and one target-velocity hold.",
                "Phase/contact modulation regressed to 2/5 and recurrent BC regressed to 0/5 with over-envelope collapse.",
            ],
            "success_gate": {
                "x008": "5/5 PASS_CANDIDATE_SIM_GATE, zero p95 and max corrected velocity excess",
                "x000": "5/5 PASS_CANDIDATE_SIM_GATE, mean |vx| <= 0.005 m/s, zero corrected velocity excess",
            },
            "stop_conditions": [
                "Any checkpoint with x=0.0 command-semantics regression is rejected.",
                "Any checkpoint with corrected velocity-envelope excess is rejected.",
                "If the first bounded on-policy iteration lowers x=0.08 pass count below the step-0 3/5 baseline, stop and change objective structure.",
                "Do not launch long DR until a step-0 or short on-policy parent clears the compact x=0.08 and x=0.0 gates.",
            ],
        },
        "commands": {
            "local_rocm_smoke": build_local_smoke_command(args),
            "local_rocm_smoke_shell": shell_join(build_local_smoke_command(args)),
            "colab_a100": build_colab_command(args),
            "colab_a100_shell": multiline_shell(build_colab_command(args)),
        },
    }
    return report


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    x008 = report["compact_gates"]["x008"]
    x000 = report["compact_gates"]["x000"]
    lines = [
        "# Phase 2 Gate-Aware Parent Next Branch",
        "",
        f"status: `{report['status']}`",
        "",
        "This is an offline planning artifact. It did not train, SSH, deploy,",
        "run robot tests, run grounded replay, or change robot runtime behavior.",
        "",
        "## Executive Summary",
        "",
        "BC-only compression is closed for the current live-oracle iter2 aggregate.",
        "The next authorized branch is a bounded gate-aware/on-policy parent",
        "iteration from the live-oracle iter2 PPO-loc step-0 checkpoint.",
        "",
        "Do not train from scratch. Do not launch long domain randomization until",
        "the compact corrected-bridge behavior-preservation gates pass.",
        "",
        "## Restore Point",
        "",
        f"- checkpoint: `{report['restore_checkpoint']['path']}`",
        f"- checkpoint exists: `{report['restore_checkpoint']['exists']}`",
        f"- ONNX: `{report['restore_onnx']['path']}`",
        f"- ONNX sha256: `{report['restore_onnx']['sha256']}`",
        f"- fidelity status: `{report['step0_fidelity']['status']}`",
        "",
        "## Compact Gate Evidence",
        "",
        "### x=0.08 moving gate",
        "",
        f"- pass count: `{x008['pass_count']}/{x008['runs']}`",
        f"- fall count: `{x008['fall_count']}`",
        f"- mean vx: `{x008['aggregate']['mean_local_vx_m_s']}`",
        f"- mean track ratio: `{x008['aggregate']['track_ratio_mean']}`",
        f"- max p95 velocity excess: `{x008['aggregate']['max_p95_velocity_excess_rad_s']}`",
        f"- max instantaneous velocity excess: `{x008['aggregate']['max_velocity_excess_rad_s']}`",
        "",
        "| seed | status | samples | mean vx | track ratio | max vel excess |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for row in x008["rows"]:
        lines.append(
            "| "
            f"`{row['seed']}` | `{row['status']}` | {row['samples']} | "
            f"{row['mean_local_vx_m_s']:.4f} | "
            f"{row['track_ratio'] if row['track_ratio'] is not None else 'NA'} | "
            f"{row['max_velocity_excess_rad_s']:.4f} |"
        )
    lines.extend(
        [
            "",
            "### x=0.0 command-semantics gate",
            "",
            f"- pass count: `{x000['pass_count']}/{x000['runs']}`",
            f"- fall count: `{x000['fall_count']}`",
            f"- mean vx: `{x000['aggregate']['mean_local_vx_m_s']}`",
            f"- max p95 velocity excess: `{x000['aggregate']['max_p95_velocity_excess_rad_s']}`",
            f"- max instantaneous velocity excess: `{x000['aggregate']['max_velocity_excess_rad_s']}`",
            "",
            "## Closed Branches",
            "",
        ]
    )
    for name, row in report["closed_bc_branches"].items():
        lines.append(f"- `{name}`: `{row.get('status')}`")
    lines.extend(
        [
            "",
            "## Next Branch",
            "",
            report["decision"]["recommended_next"],
            "",
            "Success gate:",
            "",
            f"- x=0.08: {report['decision']['success_gate']['x008']}",
            f"- x=0.0: {report['decision']['success_gate']['x000']}",
            "",
            "Stop conditions:",
            "",
        ]
    )
    for item in report["decision"]["stop_conditions"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Local Smoke Command",
            "",
            "```bash",
            report["commands"]["local_rocm_smoke_shell"],
            "```",
            "",
            "## Colab A100 Command",
            "",
            "```bash",
            report["commands"]["colab_a100_shell"],
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step0-fidelity", default=str(DEFAULT_STEP0_FIDELITY))
    parser.add_argument("--step0-x008-gate", default=str(DEFAULT_STEP0_X008_GATE))
    parser.add_argument("--step0-x000-gate", default=str(DEFAULT_STEP0_X000_GATE))
    parser.add_argument("--phase-contact-decision", default=str(DEFAULT_PHASE_CONTACT_DECISION))
    parser.add_argument("--recurrent-decision", default=str(DEFAULT_RECURRENT_DECISION))
    parser.add_argument("--restore-checkpoint", default=str(DEFAULT_RESTORE_CHECKPOINT))
    parser.add_argument("--restore-onnx", default=str(DEFAULT_RESTORE_ONNX))
    parser.add_argument("--corrected-bridge", default=str(DEFAULT_BRIDGE))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args)
    out_json = Path(args.output_json)
    out_md = Path(args.output_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2))
    write_markdown(out_md, report)
    print(report["status"])
    print(f"wrote {rel(out_md)}")
    print(f"wrote {rel(out_json)}")
    return 0 if report["status"].startswith("PLAN_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
