#!/usr/bin/env python3
"""Plan or run a staged locomotion curriculum for actuator-bridge training.

The current candidate search is stuck between unsafe motion and safe
standstill. This helper defines a staged offline training recipe that first
bootstraps forward locomotion, then gradually reintroduces the measured actuator
bridge. It does not touch the robot, SSH, deploy, or modify runtime behavior.

By default this writes a plan only. Pass ``--run`` to execute the phases through
``tools/run_actuator_bridge_training_smoke.py`` in the selected Python/env.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import datetime as dt
import json
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_ENV_PYTHON = ROOT.parent / "envs/open-duck-playground/bin/python"
DEFAULT_OUTPUT_ROOT = Path("/tmp/open_duck_staged_curriculum")
DEFAULT_PLAN_MD = ROOT / "outputs" / "analysis" / "STAGED_CURRICULUM_TRAINING_PLAN.md"
DEFAULT_PLAN_JSON = ROOT / "outputs" / "analysis" / "staged_curriculum_training_plan.json"


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def cli_value(value: Any) -> str:
    if isinstance(value, float):
        text = f"{value:.12f}".rstrip("0").rstrip(".")
        return text if text not in {"", "-0"} else "0"
    return str(value)


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


@dataclass(frozen=True)
class Phase:
    name: str
    purpose: str
    num_timesteps: int
    bridge: bool
    delay: tuple[int, int]
    tau_s: tuple[float, float]
    velocity_limit_rad_s: tuple[float, float]
    target_rate_scale: float
    actuator_tracking_scale: float
    tracking_lin_vel_scale: float
    tracking_sigma: float
    forward_progress_scale: float
    forward_shortfall_scale: float
    forward_shortfall_required_ratio: float
    action_rate_scale: float
    action_magnitude_scale: float
    stand_still_scale: float
    alive_scale: float
    imitation_scale: float
    lin_vel_x: tuple[float, float]
    zero_command_probability: float


PHASES = [
    Phase(
        name="phase1_locomotion_bootstrap_no_bridge",
        purpose="force forward intent before actuator constraints make standing easy",
        num_timesteps=300_000,
        bridge=False,
        delay=(0, 0),
        tau_s=(0.0, 0.0),
        velocity_limit_rad_s=(5.24, 5.24),
        target_rate_scale=0.0,
        actuator_tracking_scale=0.0,
        tracking_lin_vel_scale=35.0,
        tracking_sigma=0.0025,
        forward_progress_scale=6.0,
        forward_shortfall_scale=-2.0,
        forward_shortfall_required_ratio=0.4,
        action_rate_scale=-0.02,
        action_magnitude_scale=-0.005,
        stand_still_scale=-0.6,
        alive_scale=0.2,
        imitation_scale=0.1,
        lin_vel_x=(0.06, 0.14),
        zero_command_probability=0.0,
    ),
    Phase(
        name="phase2_mild_bridge_transition",
        purpose="keep forward motion while introducing mild delay/lag/velocity limits",
        num_timesteps=250_000,
        bridge=True,
        delay=(1, 3),
        tau_s=(0.02, 0.06),
        velocity_limit_rad_s=(4.0, 5.24),
        target_rate_scale=-0.004,
        actuator_tracking_scale=-0.25,
        tracking_lin_vel_scale=30.0,
        tracking_sigma=0.0025,
        forward_progress_scale=5.0,
        forward_shortfall_scale=-3.0,
        forward_shortfall_required_ratio=0.45,
        action_rate_scale=-0.04,
        action_magnitude_scale=-0.01,
        stand_still_scale=-0.5,
        alive_scale=0.25,
        imitation_scale=0.15,
        lin_vel_x=(0.05, 0.13),
        zero_command_probability=0.0,
    ),
    Phase(
        name="phase3_fitted_bridge_consolidation",
        purpose="train under the fitted actuator envelope used by the candidate gates",
        num_timesteps=300_000,
        bridge=True,
        delay=(3, 8),
        tau_s=(0.06, 0.14),
        velocity_limit_rad_s=(2.5, 4.7),
        target_rate_scale=-0.01,
        actuator_tracking_scale=-0.75,
        tracking_lin_vel_scale=25.0,
        tracking_sigma=0.0025,
        forward_progress_scale=4.0,
        forward_shortfall_scale=-4.0,
        forward_shortfall_required_ratio=0.5,
        action_rate_scale=-0.08,
        action_magnitude_scale=-0.02,
        stand_still_scale=-0.4,
        alive_scale=0.3,
        imitation_scale=0.2,
        lin_vel_x=(0.04, 0.12),
        zero_command_probability=0.05,
    ),
]


def phase_command(
    args: argparse.Namespace,
    phase: Phase,
    output_root: Path,
    restore_checkpoint: Path | None,
) -> list[str]:
    command = [
        str(Path(args.env_python)),
        str(ROOT / "tools" / "run_actuator_bridge_training_smoke.py"),
        "--run",
        "--playground-path",
        str(Path(args.playground_path)),
        "--env-python",
        str(Path(args.env_python)),
        "--output-root",
        str(output_root),
        "--platform",
        args.platform,
        "--timeout-s",
        str(args.phase_timeout_s),
        "--num-timesteps",
        str(int(phase.num_timesteps * args.timesteps_scale)),
        "--ppo-num-envs",
        str(args.ppo_num_envs),
        "--ppo-num-evals",
        str(args.ppo_num_evals),
        "--ppo-episode-length",
        str(args.ppo_episode_length),
        "--ppo-unroll-length",
        str(args.ppo_unroll_length),
        "--ppo-batch-size",
        str(args.ppo_batch_size),
        "--ppo-num-minibatches",
        str(args.ppo_num_minibatches),
        "--ppo-num-updates-per-batch",
        str(args.ppo_num_updates_per_batch),
        "--target-rate-scale",
        cli_value(phase.target_rate_scale),
        "--actuator-tracking-scale",
        cli_value(phase.actuator_tracking_scale),
        "--tracking-lin-vel-scale",
        cli_value(phase.tracking_lin_vel_scale),
        "--tracking-ang-vel-scale",
        "0.0",
        "--tracking-sigma",
        cli_value(phase.tracking_sigma),
        "--forward-progress-scale",
        cli_value(phase.forward_progress_scale),
        "--forward-shortfall-scale",
        cli_value(phase.forward_shortfall_scale),
        "--forward-progress-deadband",
        "0.02",
        "--forward-shortfall-required-ratio",
        cli_value(phase.forward_shortfall_required_ratio),
        "--action-rate-scale",
        cli_value(phase.action_rate_scale),
        "--action-magnitude-scale",
        cli_value(phase.action_magnitude_scale),
        "--stand-still-scale",
        cli_value(phase.stand_still_scale),
        "--alive-scale",
        cli_value(phase.alive_scale),
        "--imitation-scale",
        cli_value(phase.imitation_scale),
        "--lin-vel-x-min",
        cli_value(phase.lin_vel_x[0]),
        "--lin-vel-x-max",
        cli_value(phase.lin_vel_x[1]),
        "--lin-vel-y-min",
        "0.0",
        "--lin-vel-y-max",
        "0.0",
        "--ang-vel-yaw-min",
        "0.0",
        "--ang-vel-yaw-max",
        "0.0",
        "--command-resample-steps",
        "600",
        "--zero-command-probability",
        cli_value(phase.zero_command_probability),
        "--head-range-factor",
        "0.25",
    ]
    if not phase.bridge:
        command.append("--disable-actuator-bridge")
    else:
        command.extend(
            [
                "--actuator-bridge-delay-min-ticks",
                str(phase.delay[0]),
                "--actuator-bridge-delay-max-ticks",
                str(phase.delay[1]),
                "--actuator-bridge-tau-min-s",
                cli_value(phase.tau_s[0]),
                "--actuator-bridge-tau-max-s",
                cli_value(phase.tau_s[1]),
                "--actuator-bridge-velocity-limit-min-rad-s",
                cli_value(phase.velocity_limit_rad_s[0]),
                "--actuator-bridge-velocity-limit-max-rad-s",
                cli_value(phase.velocity_limit_rad_s[1]),
                "--actuator-bridge-per-joint-variation",
                "0.15",
            ]
        )
    if restore_checkpoint is not None:
        command.extend(["--restore-checkpoint-path", str(restore_checkpoint)])
    return command


def find_latest_checkpoint(root: Path) -> Path | None:
    candidates: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        if path.name.endswith(("_x0", "_x008")) or "gate" in path.name:
            continue
        if any(path.with_suffix(suffix).exists() for suffix in (".onnx", ".pkl")):
            candidates.append(path)
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def find_latest_onnx(root: Path) -> Path | None:
    candidates = list(root.rglob("*.onnx"))
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def phase_payload(phase: Phase, command: list[str], output_root: Path) -> dict[str, Any]:
    return {
        "name": phase.name,
        "purpose": phase.purpose,
        "output_root": str(output_root),
        "bridge_enabled": phase.bridge,
        "delay_ticks": list(phase.delay),
        "tau_s": list(phase.tau_s),
        "velocity_limit_rad_s": list(phase.velocity_limit_rad_s),
        "lin_vel_x": list(phase.lin_vel_x),
        "zero_command_probability": phase.zero_command_probability,
        "forward_shortfall_scale": phase.forward_shortfall_scale,
        "forward_shortfall_required_ratio": phase.forward_shortfall_required_ratio,
        "num_timesteps": phase.num_timesteps,
        "restore_checkpoint": (
            command[command.index("--restore-checkpoint-path") + 1]
            if "--restore-checkpoint-path" in command
            else None
        ),
        "command": command,
        "command_shell": shell_join(command),
    }


def write_plan(payload: dict[str, Any], output_md: Path, output_json: Path) -> None:
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# Staged Curriculum Training Plan",
        "",
        "Offline-only plan. This does not touch the robot, SSH, deploy, or modify",
        "runtime behavior. Training only runs when the planner is invoked with",
        "`--run`.",
        "",
        f"status: `{payload['status']}`",
        f"platform: `{payload['platform']}`",
        f"output_root: `{payload['output_root']}`",
        "",
        "## Why",
        "",
        "Current candidates are either aggressive and unsafe, or stable and nearly",
        "stationary at `x=0.08`. The staged recipe bootstraps forward motion before",
        "tightening actuator realism.",
        "",
        "## Phases",
        "",
        "| phase | bridge | timesteps | x command range | shortfall | delay | tau | velocity limit | purpose |",
        "|---|---|---:|---|---|---|---|---|---|",
    ]
    for phase in payload["phases"]:
        lines.append(
            "| `{name}` | {bridge} | {steps} | `{x}` | `{shortfall}` | `{delay}` | `{tau}` | `{vel}` | {purpose} |".format(
                name=phase["name"],
                bridge="yes" if phase["bridge_enabled"] else "no",
                steps=phase["num_timesteps"],
                x=phase["lin_vel_x"],
                shortfall={
                    "scale": phase["forward_shortfall_scale"],
                    "required_ratio": phase["forward_shortfall_required_ratio"],
                },
                delay=phase["delay_ticks"],
                tau=phase["tau_s"],
                vel=phase["velocity_limit_rad_s"],
                purpose=phase["purpose"],
            )
        )
    lines.extend(["", "## Commands", ""])
    for phase in payload["phases"]:
        lines.extend(
            [
                f"### {phase['name']}",
                "",
                f"- restore_checkpoint: `{phase.get('restore_checkpoint') or 'None'}`",
                "",
                "```bash",
                phase["command_shell"],
                "```",
                "",
            ]
        )
    if payload.get("final_candidate_onnx"):
        lines.extend(
            [
                "## Result",
                "",
                f"- final_candidate_onnx: `{payload['final_candidate_onnx']}`",
                f"- final_checkpoint: `{payload.get('final_checkpoint', 'NA')}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Next Gate",
            "",
            "After a staged run, evaluate the final ONNX with:",
            "",
            "```bash",
            "JAX_PLATFORMS=cpu ../envs/open-duck-playground/bin/python tools/eval_policy_with_actuator_bridge.py \\",
            "  --mode closed-loop-sim --eval-role candidate \\",
            "  --policy <final_candidate.onnx> \\",
            "  --fit-json outputs/analysis/actuator_response_fit.json \\",
            "  --playground-path ../Open_Duck_Playground \\",
            "  --env-python ../envs/open-duck-playground/bin/python \\",
            "  --command-x 0.0 --duration 15 --bridge-mode all --jax-platform cpu \\",
            "  --output-dir outputs/analysis/<candidate>_gate_x0",
            "```",
            "",
            "Then repeat with `--command-x 0.08`. Robot validation remains blocked until",
            "both gates pass.",
            "",
        ]
    )
    output_md.write_text("\n".join(lines))


def run_phase(command: list[str], cwd: Path, timeout_s: int) -> None:
    print(">>>", shell_join(command), flush=True)
    completed = subprocess.run(command, cwd=cwd, text=True, timeout=timeout_s, check=False)
    print("<<<", completed.returncode, flush=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-path", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--env-python", default=str(DEFAULT_ENV_PYTHON))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--output-md", type=Path, default=DEFAULT_PLAN_MD)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_PLAN_JSON)
    parser.add_argument("--platform", choices=["cpu", "gpu"], default="gpu")
    parser.add_argument("--timesteps-scale", type=float, default=1.0)
    parser.add_argument("--phase-timeout-s", type=int, default=3600)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--ppo-num-envs", type=int, default=256)
    parser.add_argument("--ppo-num-evals", type=int, default=4)
    parser.add_argument("--ppo-episode-length", type=int, default=600)
    parser.add_argument("--ppo-unroll-length", type=int, default=10)
    parser.add_argument("--ppo-batch-size", type=int, default=256)
    parser.add_argument("--ppo-num-minibatches", type=int, default=4)
    parser.add_argument("--ppo-num-updates-per-batch", type=int, default=4)
    args = parser.parse_args()

    output_root = Path(args.output_root).expanduser().resolve()
    payload: dict[str, Any] = {
        "status": "RUN_REQUESTED" if args.run else "DRY_RUN",
        "timestamp": timestamp(),
        "robot_touched": False,
        "deploy_performed": False,
        "platform": args.platform,
        "output_root": str(output_root),
        "phases": [],
    }

    restore_checkpoint: Path | None = None
    for index, phase in enumerate(PHASES, 1):
        phase_root = output_root / f"{index:02d}_{phase.name}"
        restore_for_command = restore_checkpoint
        if restore_for_command is None and not args.run and index > 1:
            restore_for_command = Path(f"<latest_checkpoint_from_phase_{index - 1}>")
        command = phase_command(args, phase, phase_root, restore_for_command)
        payload["phases"].append(phase_payload(phase, command, phase_root))
        if args.run:
            run_phase(command, ROOT, args.phase_timeout_s + 300)
            restore_checkpoint = find_latest_checkpoint(phase_root)
            if restore_checkpoint is None:
                raise SystemExit(f"{phase.name} produced no checkpoint under {phase_root}")

    if args.run:
        payload["status"] = "PASS_STAGED_CURRICULUM_RUN"
        payload["final_checkpoint"] = str(restore_checkpoint) if restore_checkpoint else None
        final_onnx = find_latest_onnx(output_root)
        payload["final_candidate_onnx"] = str(final_onnx) if final_onnx else None
    write_plan(payload, args.output_md, args.output_json)
    print(f"Wrote {args.output_md}")
    print(f"Wrote {args.output_json}")
    if not args.run:
        print("Dry-run only. Pass --run to execute staged training.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.TimeoutExpired as exc:
        print(f"HOLD_STAGED_CURRICULUM_TIMEOUT: timed out after {exc.timeout}s", file=sys.stderr)
        raise SystemExit(124) from exc
