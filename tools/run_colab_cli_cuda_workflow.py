#!/usr/bin/env python3
"""Run the Open Duck CUDA workflow through google-colab-cli.

This helper is offline-only. It uploads local repo tarballs to an existing Colab
session, starts a detached remote shell job through ``colab console``, polls for
an artifact bundle, and downloads the results. It does not use GitHub tokens and
does not touch the robot.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tarfile
import textwrap
import time


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAYGROUND = ROOT.parent / "Open_Duck_Playground"
DEFAULT_OUTPUT_ROOT = ROOT / "outputs" / "analysis" / "colab_cli"
DEFAULT_UPLOAD_ROOT = ROOT.parent / "outputs" / "colab_cli_uploads"
DEFAULT_SESSION = "open-duck-l4"
PINNED_JAX_VERSION = "0.7.2"


def timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def cli_value(value: object) -> str:
    """Return a command-line-safe scalar string for generated remote scripts."""

    if isinstance(value, float):
        # argparse can treat scientific negative strings such as "-5e-05" as
        # option-like tokens. Use fixed decimal form for small negative scales.
        text = f"{value:.12f}".rstrip("0").rstrip(".")
        return text if text not in {"", "-0"} else "0"
    return str(value)


def run(command: list[str], *, check: bool = True, timeout: int | None = None) -> subprocess.CompletedProcess:
    print(">>>", shell_join(command), flush=True)
    completed = subprocess.run(command, text=True, timeout=timeout, check=False)
    print("<<<", completed.returncode, flush=True)
    if check and completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return completed


def tar_filter(member: tarfile.TarInfo) -> tarfile.TarInfo | None:
    parts = Path(member.name).parts
    blocked = {
        ".git",
        ".tmp",
        "__pycache__",
        ".pytest_cache",
        "cuda_imports",
        "wandb",
    }
    if any(part in blocked for part in parts):
        return None
    if "outputs" in parts and "analysis" in parts:
        allowed_analysis = {
            ("outputs", "analysis", "actuator_response_fit.json"),
            ("outputs", "analysis", "ACTUATOR_RESPONSE_FIT.md"),
        }
        rel_parts = tuple(parts[1:]) if len(parts) > 1 else tuple(parts)
        is_allowed_path = rel_parts in allowed_analysis
        is_allowed_parent = any(path[: len(rel_parts)] == rel_parts for path in allowed_analysis)
        if not is_allowed_path and not is_allowed_parent:
            return None
    if member.name.endswith((".pyc", ".pyo")):
        return None
    return member


def make_tarball(src: Path, dest: Path, arcname: str) -> None:
    src = src.resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(dest, "w:gz") as tf:
        tf.add(src, arcname=arcname, filter=tar_filter)
    print(f"TARBALL {dest} size={dest.stat().st_size}", flush=True)


def colab_file_exists(session: str, remote_path: str) -> bool:
    completed = subprocess.run(
        ["colab", "ls", "-s", session, remote_path],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.returncode == 0


def colab_status_text(session: str) -> str:
    completed = subprocess.run(
        ["colab", "status", "-s", session],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.stdout or ""


def colab_status_is_idle(status_text: str) -> bool:
    return "idle" in status_text.lower()


def write_console_script(path: Path, remote_script: str) -> None:
    path.write_text(remote_script.strip() + "\nexit\n")


def run_console_script(
    session: str,
    console_script: Path,
    log_path: Path,
    *,
    timeout_s: int = 120,
) -> subprocess.CompletedProcess:
    print(">>>", f"colab console -s {session} < {console_script}", flush=True)
    completed = subprocess.run(
        ["colab", "console", "-s", session],
        input=console_script.read_text(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout_s,
        check=False,
    )
    log_path.write_text(completed.stdout or "")
    print(completed.stdout[-2000:] if completed.stdout else "", flush=True)
    return completed


def initialize_content_api(session: str, run_dir: Path) -> None:
    """Touch /content once so google-colab-cli file upload/download can see it."""

    console_script = run_dir / "initialize_content_api_console.sh"
    write_console_script(
        console_script,
        """
        set -euo pipefail
        mkdir -p /content
        printf 'ready\\n' > /content/open_duck_colab_cli_content_ready.txt
        ls -l /content/open_duck_colab_cli_content_ready.txt
        """,
    )
    completed = run_console_script(
        session,
        console_script,
        run_dir / "console_initialize_content_api.log",
        timeout_s=120,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def start_remote_job(
    args: argparse.Namespace,
    run_dir: Path,
    rdk_remote_tar: str,
    playground_remote_tar: str,
    candidate_remote_policy: str | None = None,
    candidate_remote_manifest: str | None = None,
) -> None:
    workflow_name = f"open_duck_colab_cli_{args.workflow}_{timestamp()}"
    remote_driver = f"/content/{workflow_name}_driver.py"
    remote_log = f"/content/{workflow_name}.log"
    remote_exit = f"/content/{workflow_name}.exit"
    remote_pid = f"/content/{workflow_name}.pid"
    remote_bundle = f"/content/{workflow_name}_artifacts.tar.gz"
    run_dir.joinpath("REMOTE_PATHS.txt").write_text(
        "\n".join(
            [
                f"workflow_name={workflow_name}",
                f"remote_driver={remote_driver}",
                f"remote_log={remote_log}",
                f"remote_exit={remote_exit}",
                f"remote_pid={remote_pid}",
                f"remote_bundle={remote_bundle}",
            ]
        )
        + "\n"
    )

    driver = build_remote_driver(
        args,
        workflow_name,
        rdk_remote_tar,
        playground_remote_tar,
        remote_bundle,
        candidate_remote_policy=candidate_remote_policy,
        candidate_remote_manifest=candidate_remote_manifest,
    )
    driver_local = run_dir / f"{workflow_name}_driver.py"
    driver_local.write_text(driver)
    run(["colab", "upload", "-s", args.session, str(driver_local), remote_driver])

    console_script = run_dir / f"{workflow_name}_start_console.sh"
    write_console_script(
        console_script,
        f"""
        set -euo pipefail
        setsid bash -lc {shlex.quote(f'/usr/bin/python3 {remote_driver} > {remote_log} 2>&1; echo $? > {remote_exit}')} >/dev/null 2>&1 &
        echo $! > {remote_pid}
        echo COLAB_CLI_WORKFLOW_STARTED $(cat {remote_pid})
        """,
    )
    # colab console reads from stdin, so feed the small start script directly.
    completed = run_console_script(
        args.session,
        console_script,
        run_dir / "console_start.log",
        timeout_s=120,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)

    if args.no_poll:
        print(f"Remote job started. Bundle will be {remote_bundle}", flush=True)
        return
    poll_remote(
        args.session,
        run_dir,
        remote_log,
        remote_exit,
        remote_bundle,
        remote_pid,
        args.poll_interval_s,
        args.timeout_s,
    )


def build_remote_driver(
    args: argparse.Namespace,
    workflow_name: str,
    rdk_tar: str,
    playground_tar: str,
    remote_bundle: str,
    *,
    candidate_remote_policy: str | None = None,
    candidate_remote_manifest: str | None = None,
) -> str:
    run_smoke = args.workflow in {"smoke", "training-smoke", "all", "candidate"}
    run_candidate_training = args.workflow in {"candidate", "candidate-only", "all"}
    run_staged_curriculum = args.workflow == "staged-curriculum"
    run_candidate_eval_only = args.workflow == "candidate-eval-only"
    run_checkpoint_sweep = args.workflow == "checkpoint-sweep"
    run_candidate_gates = (
        run_candidate_training or run_staged_curriculum or run_candidate_eval_only
    )
    run_audit = (
        args.workflow
        in {
            "eval",
            "smoke",
            "candidate",
            "candidate-only",
            "candidate-eval-only",
            "checkpoint-sweep",
            "all",
        }
        and not args.skip_audit
    )
    run_baseline_eval = args.workflow in {"eval", "smoke", "candidate", "all"}
    install_deps = not args.skip_deps
    smoke_steps = args.smoke_num_timesteps
    candidate_steps = args.candidate_num_timesteps
    candidate_target_rate_scale = cli_value(args.candidate_target_rate_scale)
    candidate_actuator_tracking_scale = cli_value(args.candidate_actuator_tracking_scale)
    candidate_tracking_lin_vel_scale = cli_value(args.candidate_tracking_lin_vel_scale)
    candidate_tracking_ang_vel_scale = cli_value(args.candidate_tracking_ang_vel_scale)
    candidate_tracking_sigma = cli_value(args.candidate_tracking_sigma)
    candidate_forward_progress_scale = cli_value(args.candidate_forward_progress_scale)
    candidate_forward_progress_deadband = cli_value(args.candidate_forward_progress_deadband)
    candidate_forward_shortfall_scale = cli_value(args.candidate_forward_shortfall_scale)
    candidate_forward_shortfall_required_ratio = cli_value(
        args.candidate_forward_shortfall_required_ratio
    )
    candidate_action_rate_scale = cli_value(args.candidate_action_rate_scale)
    candidate_action_magnitude_scale = cli_value(args.candidate_action_magnitude_scale)
    candidate_stand_still_scale = cli_value(args.candidate_stand_still_scale)
    candidate_alive_scale = cli_value(args.candidate_alive_scale)
    candidate_imitation_scale = cli_value(args.candidate_imitation_scale)
    candidate_lin_vel_x_min = cli_value(args.candidate_lin_vel_x_min)
    candidate_lin_vel_x_max = cli_value(args.candidate_lin_vel_x_max)
    candidate_zero_command_probability = cli_value(args.candidate_zero_command_probability)
    candidate_actuator_bridge_tau_min_s = cli_value(
        args.candidate_actuator_bridge_tau_min_s
    )
    candidate_actuator_bridge_tau_max_s = cli_value(
        args.candidate_actuator_bridge_tau_max_s
    )
    candidate_actuator_bridge_velocity_limit_min_rad_s = cli_value(
        args.candidate_actuator_bridge_velocity_limit_min_rad_s
    )
    candidate_actuator_bridge_velocity_limit_max_rad_s = cli_value(
        args.candidate_actuator_bridge_velocity_limit_max_rad_s
    )
    candidate_actuator_bridge_per_joint_variation = cli_value(
        args.candidate_actuator_bridge_per_joint_variation
    )
    artifact_checkpoint_mode = args.artifact_checkpoint_mode
    staged_initial_restore_checkpoint = args.staged_initial_restore_checkpoint
    if staged_initial_restore_checkpoint and not Path(
        staged_initial_restore_checkpoint
    ).is_absolute():
        staged_initial_restore_checkpoint = (
            f"/content/open-duck-mini-rdkx5/{staged_initial_restore_checkpoint}"
        )
    candidate_restore_checkpoint_path = args.candidate_restore_checkpoint_path
    if candidate_restore_checkpoint_path and not Path(
        candidate_restore_checkpoint_path
    ).is_absolute():
        candidate_restore_checkpoint_path = (
            f"/content/open-duck-mini-rdkx5/{candidate_restore_checkpoint_path}"
        )
    staged_stop_after_phase_arg = (
        f'"--stop-after-phase", "{args.staged_stop_after_phase}",'
        if args.staged_stop_after_phase is not None
        else ""
    )
    staged_initial_restore_arg = (
        f'"--initial-restore-checkpoint", "{staged_initial_restore_checkpoint}",'
        if staged_initial_restore_checkpoint
        else ""
    )
    staged_phase_gate_arg = (
        '"--phase-gate-freeze-check",'
        f'"--phase-gate-command-x", "{cli_value(args.staged_phase_gate_command_x)}",'
        f'"--phase-gate-duration-s", "{cli_value(args.staged_phase_gate_duration_s)}",'
        f'"--phase-gate-bridge-mode", "{args.staged_phase_gate_bridge_mode}",'
        f'"--phase-gate-platform", "{args.staged_phase_gate_platform}",'
        f'"--phase-gate-timeout-s", "{args.staged_phase_gate_timeout_s}",'
        if args.staged_phase_gate_freeze_check
        else ""
    )
    staged_timeout_multiplier = args.staged_stop_after_phase or 3
    staged_phase_gate_timeout_total = (
        args.staged_phase_gate_timeout_s * staged_timeout_multiplier
        if args.staged_phase_gate_freeze_check
        else 0
    )
    checkpoint_sweep_policies = json.dumps(args.checkpoint_sweep_policies)
    checkpoint_sweep_commands = cli_value(args.checkpoint_sweep_commands)
    checkpoint_sweep_duration = cli_value(args.checkpoint_sweep_duration)
    checkpoint_sweep_bridge_mode = args.checkpoint_sweep_bridge_mode
    candidate_disable_bridge_arg = (
        '"--disable-actuator-bridge",' if args.candidate_disable_actuator_bridge else ""
    )
    return textwrap.dedent(
        f"""
        import atexit
        import datetime as dt
        import json
        import shutil
        import subprocess
        import sys
        from pathlib import Path
        from importlib import metadata

        PYTHON = "/usr/bin/python3"
        RDK = Path("/content/open-duck-mini-rdkx5")
        PLAYGROUND = Path("/content/Open_Duck_Playground")
        OUT = RDK / "outputs/analysis/{workflow_name}"
        OUT.mkdir(parents=True, exist_ok=True)
        REMOTE_BUNDLE = Path("{remote_bundle}")
        RUN_STATUS = {{"exit_status": 0}}
        ARTIFACT_CHECKPOINT_MODE = {artifact_checkpoint_mode!r}

        def checkpoint_dirs_for_run(run_dir):
            onnx_stems = {{path.stem for path in run_dir.glob("*.onnx")}}
            candidates = []
            for child in run_dir.iterdir():
                if child.is_dir() and child.name in onnx_stems:
                    candidates.append(child)
            return sorted(candidates, key=lambda path: path.stat().st_mtime)

        def copy_checkpoint_dirs(run_dir, run_dest):
            manifest = {{
                "mode": ARTIFACT_CHECKPOINT_MODE,
                "copied": [],
                "available": [],
            }}
            candidates = checkpoint_dirs_for_run(run_dir)
            manifest["available"] = [path.name for path in candidates]
            if ARTIFACT_CHECKPOINT_MODE == "none":
                selected = []
            elif ARTIFACT_CHECKPOINT_MODE == "all":
                selected = candidates
            else:
                selected = candidates[-1:]
            for item in selected:
                try:
                    dest = run_dest / item.name
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                    manifest["copied"].append(item.name)
                except Exception as exc:
                    print("copy_checkpoint_warning", item, type(exc).__name__, exc, flush=True)
            try:
                (run_dest / "checkpoint_artifact_manifest.json").write_text(
                    json.dumps(manifest, indent=2) + "\\n"
                )
            except Exception as exc:
                print("checkpoint_manifest_warning", type(exc).__name__, exc, flush=True)

        def copy_training_outputs(src, dest):
            src = Path(src)
            dest = Path(dest)
            if not src.exists():
                return
            dest.mkdir(parents=True, exist_ok=True)
            for run_dir in sorted(src.glob("**/smoke_*_gpu")):
                rel_parent = run_dir.parent.relative_to(src)
                run_dest = dest / rel_parent / run_dir.name
                run_dest.mkdir(parents=True, exist_ok=True)
                for pattern in ["*.onnx", "smoke_manifest*.json", "stdout.txt", "stderr.txt"]:
                    for item in sorted(run_dir.glob(pattern)):
                        try:
                            (run_dest / item.name).write_bytes(item.read_bytes())
                        except Exception as exc:
                            print("copy_training_outputs_warning", item, type(exc).__name__, exc, flush=True)
                copy_checkpoint_dirs(run_dir, run_dest)

        def bundle_artifacts():
            try:
                (OUT / "COLAB_CLI_EXIT_STATUS.txt").write_text(
                    "exit_status=" + str(RUN_STATUS.get("exit_status", 0)) + "\\n"
                )
                copy_training_outputs(
                    "/content/open_duck_training_smokes_cli",
                    OUT / "open_duck_training_smokes_cli",
                )
                copy_training_outputs(
                    "/content/open_duck_training_runs_cli",
                    OUT / "open_duck_training_runs_cli",
                )
                subprocess.run(
                    ["tar", "-czf", str(REMOTE_BUNDLE), "-C", str(OUT.parent), OUT.name],
                    check=False,
                    text=True,
                )
                print("COLAB_CLI_ARTIFACT", REMOTE_BUNDLE, flush=True)
            except Exception as exc:
                print("bundle_artifacts_warning", type(exc).__name__, exc, flush=True)

        atexit.register(bundle_artifacts)

        def run(cmd, cwd=None, timeout=None, env=None, check=True):
            print("\\n>>>", " ".join(str(x) for x in cmd), flush=True)
            completed = subprocess.run(cmd, cwd=cwd, timeout=timeout, env=env, text=True)
            print("<<< returncode", completed.returncode, flush=True)
            if completed.returncode != 0:
                RUN_STATUS["exit_status"] = completed.returncode
                if check:
                    raise SystemExit(completed.returncode)
            return completed

        run(["rm", "-rf", str(RDK), str(PLAYGROUND)])
        run(["tar", "-xzf", "{rdk_tar}", "-C", "/content"])
        run(["tar", "-xzf", "{playground_tar}", "-C", "/content"])

        if {install_deps!r}:
            run([PYTHON, "-m", "pip", "install", "-U", "pip"], timeout=600)
            run([
                PYTHON, "-m", "pip", "install",
                "jax[cuda12]=={PINNED_JAX_VERSION}",
                "jaxlib=={PINNED_JAX_VERSION}",
                "playground==0.0.5",
                "mujoco==3.9.0",
                "mujoco-mjx==3.9.0",
                "onnxruntime==1.27.0",
                "ml-collections==1.1.0",
                "numpy==2.0.2",
                "matplotlib==3.10.0",
                "mediapy==1.2.6",
                "tensorflow==2.20.0",
                "protobuf==5.29.6",
                "onnx==1.22.0",
            ], timeout=1800)
            run([PYTHON, "-m", "pip", "install", "--no-deps", "tf2onnx==1.17.0"], timeout=600)
            run([PYTHON, "-m", "pip", "install", "--no-deps", "-e", str(PLAYGROUND)], timeout=600)

        print("=== Versions ===", flush=True)
        for name in ["jax", "jaxlib", "brax", "mujoco", "mujoco-mjx", "playground"]:
            try:
                print(name, metadata.version(name), flush=True)
            except Exception as exc:
                print(name, type(exc).__name__, exc, flush=True)
        run([PYTHON, "-c", "import jax; print('backend', jax.default_backend(), jax.devices()); print('has_device_put_replicated', hasattr(jax, 'device_put_replicated'))"])

        if {run_audit!r}:
            run([
                PYTHON, "tools/audit_policy_sim_contract.py",
                "--policy", "policy/BEST_WALK_ONNX_2.onnx",
                "--playground-path", str(PLAYGROUND),
                "--env-python", PYTHON,
                "--instantiate-timeout-s", "600",
                "--output-md", str(OUT / "POLICY_SIM_CONTRACT_AUDIT_CUDA.md"),
                "--output-json", str(OUT / "policy_sim_contract_audit_cuda.json"),
            ], cwd=RDK, timeout=900)

        if {run_checkpoint_sweep!r}:
            sweep_policies = {checkpoint_sweep_policies}
            sweep_cmd = [
                PYTHON, "tools/sweep_candidate_checkpoints.py",
                "--policies", *sweep_policies,
                "--fit-json", "outputs/analysis/actuator_response_fit.json",
                "--playground-path", str(PLAYGROUND),
                "--env-python", PYTHON,
                "--commands", "{checkpoint_sweep_commands}",
                "--duration", "{checkpoint_sweep_duration}",
                "--bridge-mode", "{checkpoint_sweep_bridge_mode}",
                "--mode-name", "{checkpoint_sweep_bridge_mode}",
                "--jax-platform", "gpu",
                "--sim-preflight-timeout-s", "600",
                "--closed-loop-timeout-s", "1800",
                "--output-dir", str(OUT / "candidate_checkpoint_sweep"),
                "--run",
            ]
            run(sweep_cmd, cwd=RDK, timeout={args.checkpoint_sweep_timeout_s})
            bundle_artifacts()

        if {run_baseline_eval!r}:
            run([
                PYTHON, "tools/eval_policy_with_actuator_bridge.py",
                "--mode", "closed-loop-sim",
                "--policy", "policy/BEST_WALK_ONNX_2.onnx",
                "--fit-json", "outputs/analysis/actuator_response_fit.json",
                "--playground-path", str(PLAYGROUND),
                "--env-python", PYTHON,
                "--command-x", "0.08",
                "--duration", "15",
                "--bridge-mode", "all",
                "--jax-platform", "gpu",
                "--sim-preflight-timeout-s", "600",
                "--closed-loop-timeout-s", "1800",
                "--output-dir", str(OUT / "baseline_x008"),
            ], cwd=RDK, timeout=2400)

        if {run_smoke!r}:
            run([
                PYTHON, "tools/run_actuator_bridge_training_smoke.py",
                "--playground-path", str(PLAYGROUND),
                "--env-python", PYTHON,
                "--platform", "gpu",
                "--run",
                "--output-root", "/content/open_duck_training_smokes_cli",
                "--num-timesteps", "{smoke_steps}",
                "--export-min-step", "{args.smoke_export_min_step}",
                "--ppo-num-envs", "8",
                "--ppo-num-evals", "1",
                "--ppo-episode-length", "50",
                "--ppo-unroll-length", "5",
                "--ppo-batch-size", "8",
                "--ppo-num-minibatches", "1",
                "--ppo-num-updates-per-batch", "1",
                "--target-rate-scale", "-0.01",
                "--actuator-tracking-scale", "0.0",
                "--timeout-s", "1200",
            ], cwd=RDK, timeout=1500)
            copy_training_outputs(
                "/content/open_duck_training_smokes_cli",
                OUT / "open_duck_training_smokes_cli",
            )

        latest_onnx = None
        candidate_name = None
        training_manifest = None

        if {run_candidate_training!r}:
            candidate_training_cmd = [
                PYTHON, "tools/run_actuator_bridge_training_smoke.py",
                "--playground-path", str(PLAYGROUND),
                "--env-python", PYTHON,
                "--platform", "gpu",
                "--run",
                "--output-root", "/content/open_duck_training_runs_cli",
                "--num-timesteps", "{candidate_steps}",
                "--ppo-num-envs", "{args.candidate_ppo_num_envs}",
                "--ppo-num-evals", "{args.candidate_ppo_num_evals}",
                "--ppo-episode-length", "{args.candidate_episode_length}",
                "--ppo-unroll-length", "{args.candidate_unroll_length}",
                "--ppo-batch-size", "{args.candidate_ppo_batch_size}",
                "--ppo-num-minibatches", "{args.candidate_ppo_num_minibatches}",
                "--ppo-num-updates-per-batch", "{args.candidate_ppo_num_updates_per_batch}",
                "--target-rate-scale", "{candidate_target_rate_scale}",
                "--actuator-tracking-scale", "{candidate_actuator_tracking_scale}",
                "--tracking-lin-vel-scale", "{candidate_tracking_lin_vel_scale}",
                "--tracking-ang-vel-scale", "{candidate_tracking_ang_vel_scale}",
                "--tracking-sigma", "{candidate_tracking_sigma}",
                "--forward-progress-scale", "{candidate_forward_progress_scale}",
                "--forward-progress-deadband", "{candidate_forward_progress_deadband}",
                "--forward-shortfall-scale", "{candidate_forward_shortfall_scale}",
                "--forward-shortfall-required-ratio", "{candidate_forward_shortfall_required_ratio}",
                "--action-rate-scale", "{candidate_action_rate_scale}",
                "--action-magnitude-scale", "{candidate_action_magnitude_scale}",
                "--stand-still-scale", "{candidate_stand_still_scale}",
                "--alive-scale", "{candidate_alive_scale}",
                "--imitation-scale", "{candidate_imitation_scale}",
                "--lin-vel-x-min", "{candidate_lin_vel_x_min}",
                "--lin-vel-x-max", "{candidate_lin_vel_x_max}",
                "--lin-vel-y-min", "0.0",
                "--lin-vel-y-max", "0.0",
                "--ang-vel-yaw-min", "0.0",
                "--ang-vel-yaw-max", "0.0",
                "--command-resample-steps", "{args.candidate_command_resample_steps}",
                "--zero-command-probability", "{candidate_zero_command_probability}",
                "--head-range-factor", "0.0",
                {candidate_disable_bridge_arg}
                "--actuator-bridge-delay-min-ticks", "{args.candidate_actuator_bridge_delay_min_ticks}",
                "--actuator-bridge-delay-max-ticks", "{args.candidate_actuator_bridge_delay_max_ticks}",
                "--actuator-bridge-tau-min-s", "{candidate_actuator_bridge_tau_min_s}",
                "--actuator-bridge-tau-max-s", "{candidate_actuator_bridge_tau_max_s}",
                "--actuator-bridge-velocity-limit-min-rad-s", "{candidate_actuator_bridge_velocity_limit_min_rad_s}",
                "--actuator-bridge-velocity-limit-max-rad-s", "{candidate_actuator_bridge_velocity_limit_max_rad_s}",
                "--actuator-bridge-per-joint-variation", "{candidate_actuator_bridge_per_joint_variation}",
                "--timeout-s", "{args.candidate_timeout_s}",
            ]
            if {candidate_restore_checkpoint_path!r}:
                candidate_training_cmd.extend([
                    "--restore-checkpoint-path",
                    {candidate_restore_checkpoint_path!r},
                ])
            run(candidate_training_cmd, cwd=RDK, timeout={args.candidate_timeout_s + 300})
            run_dirs = sorted(Path("/content/open_duck_training_runs_cli").glob("smoke_*_gpu"))
            if not run_dirs:
                raise SystemExit("candidate training produced no smoke_*_gpu run directory")
            run_dir = run_dirs[-1]
            onnx_files = sorted(run_dir.glob("*.onnx"))
            if not onnx_files:
                raise SystemExit(f"candidate training produced no ONNX files in {{run_dir}}")
            latest_onnx = onnx_files[-1]
            candidate_name = {args.candidate_name!r} or (
                "open_duck_mini_actuator_bridge_cli_"
                + dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
            )
            training_manifest = run_dir / "smoke_manifest.final.json"
            if not training_manifest.exists():
                training_manifest = run_dir / "smoke_manifest.start.json"
            run([
                PYTHON, "tools/summarize_training_run.py", str(run_dir),
                "--output-md", str(OUT / f"{{candidate_name}}_training_run_summary.md"),
                "--output-json", str(OUT / f"{{candidate_name}}_training_run_summary.json"),
            ], cwd=RDK, timeout=300, check=False)
            copy_training_outputs(
                "/content/open_duck_training_runs_cli",
                OUT / "open_duck_training_runs_cli",
            )
            bundle_artifacts()

        elif {run_staged_curriculum!r}:
            candidate_name = {args.candidate_name!r} or (
                "open_duck_mini_staged_curriculum_cli_"
                + dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
            )
            staged_root = Path("/content/open_duck_staged_curriculum_cli")
            run([
                PYTHON, "tools/plan_staged_curriculum_training.py",
                "--run",
                "--recipe", "{args.staged_recipe}",
                "--playground-path", str(PLAYGROUND),
                "--env-python", PYTHON,
                "--platform", "gpu",
                "--timesteps-scale", "{args.staged_timesteps_scale}",
                {staged_initial_restore_arg}
                {staged_stop_after_phase_arg}
                {staged_phase_gate_arg}
                "--phase-timeout-s", "{args.staged_phase_timeout_s}",
                "--output-root", str(staged_root),
                "--output-md", str(OUT / f"{{candidate_name}}_staged_curriculum_plan.md"),
                "--output-json", str(OUT / f"{{candidate_name}}_staged_curriculum_plan.json"),
                "--ppo-num-envs", "{args.candidate_ppo_num_envs}",
                "--ppo-num-evals", "{args.candidate_ppo_num_evals}",
                "--ppo-episode-length", "{args.candidate_episode_length}",
                "--ppo-unroll-length", "{args.candidate_unroll_length}",
                "--ppo-batch-size", "{args.candidate_ppo_batch_size}",
                "--ppo-num-minibatches", "{args.candidate_ppo_num_minibatches}",
                "--ppo-num-updates-per-batch", "{args.candidate_ppo_num_updates_per_batch}",
            ], cwd=RDK, timeout={args.staged_phase_timeout_s * staged_timeout_multiplier + staged_phase_gate_timeout_total + 900})
            staged_plan = OUT / f"{{candidate_name}}_staged_curriculum_plan.json"
            payload = json.loads(staged_plan.read_text())
            latest_onnx = Path(payload.get("final_candidate_onnx") or "")
            if not latest_onnx.exists():
                raise SystemExit(
                    f"staged curriculum produced no final ONNX: {{latest_onnx}}"
                )
            training_manifest = latest_onnx.parent / "smoke_manifest.final.json"
            if not training_manifest.exists():
                training_manifest = latest_onnx.parent / "smoke_manifest.start.json"
            if not training_manifest.exists():
                training_manifest = None
            copy_training_outputs(
                str(staged_root),
                OUT / "open_duck_staged_curriculum_cli",
            )
            bundle_artifacts()

        elif {run_candidate_eval_only!r}:
            latest_onnx = Path({candidate_remote_policy!r}) if {candidate_remote_policy!r} else None
            if latest_onnx is None or not latest_onnx.exists():
                raise SystemExit(
                    "candidate-eval-only requires --candidate-existing-policy "
                    "and the uploaded ONNX must exist in the Colab runtime"
                )
            candidate_name = {args.candidate_name!r} or (
                "open_duck_mini_actuator_bridge_eval_"
                + latest_onnx.stem
                + "_"
                + dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
            )
            if {candidate_remote_manifest!r}:
                training_manifest = Path({candidate_remote_manifest!r})
                if not training_manifest.exists():
                    print("candidate_eval_only_manifest_missing", training_manifest, flush=True)
                    training_manifest = None
            (OUT / f"{{candidate_name}}_existing_policy_path.txt").write_text(
                str(latest_onnx) + "\\n"
            )
            bundle_artifacts()

        if {run_candidate_gates!r}:
            for command_x, suffix in [("0.0", "x0"), ("0.08", "x008")]:
                gate_dir = OUT / f"{{candidate_name}}_gate_{{suffix}}"
                run([
                    PYTHON, "tools/eval_policy_with_actuator_bridge.py",
                    "--mode", "closed-loop-sim",
                    "--eval-role", "candidate",
                    "--policy", str(latest_onnx),
                    "--fit-json", "outputs/analysis/actuator_response_fit.json",
                    "--playground-path", str(PLAYGROUND),
                    "--env-python", PYTHON,
                    "--command-x", command_x,
                    "--duration", "15",
                    "--bridge-mode", "all",
                    "--jax-platform", "gpu",
                    "--sim-preflight-timeout-s", "600",
                    "--closed-loop-timeout-s", "1800",
                    "--output-dir", str(gate_dir),
                ], cwd=RDK, timeout=2400)
                run(["cp", str(gate_dir / "CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md"), str(OUT / f"{{candidate_name}}_candidate_gate_{{suffix}}.md")])
                run(["cp", str(gate_dir / "closed_loop_actuator_bridge_eval.json"), str(OUT / f"{{candidate_name}}_candidate_gate_{{suffix}}.json")])
                bundle_artifacts()
            package_cmd = [
                PYTHON, "tools/package_candidate_policy.py", str(latest_onnx),
                "--candidate-name", candidate_name,
                "--contract-audit", str(OUT / "POLICY_SIM_CONTRACT_AUDIT_CUDA.md"),
                "--candidate-gate-x0", str(OUT / f"{{candidate_name}}_candidate_gate_x0.md"),
                "--candidate-gate-x008", str(OUT / f"{{candidate_name}}_candidate_gate_x008.md"),
                "--output-md", str(OUT / f"{{candidate_name}}_policy_package.md"),
                "--output-json", str(OUT / f"{{candidate_name}}_policy_metadata.json"),
            ]
            if training_manifest is not None and training_manifest.exists():
                package_cmd.extend(["--training-manifest", str(training_manifest)])
            else:
                package_cmd.extend([
                    "--allow-missing-evidence",
                    "--non-deployable-reason",
                    (
                        "Eval-only package: training manifest was not provided "
                        "in this Colab run. Sim gates must be reviewed before "
                        "any robot validation."
                    ),
                ])
            run(package_cmd, cwd=RDK, timeout=300, check=False)
            if {run_candidate_training!r}:
                copy_training_outputs(
                    "/content/open_duck_training_runs_cli",
                    OUT / "open_duck_training_runs_cli",
                )

        run([PYTHON, "-m", "pip", "freeze"], cwd=RDK)
        run(["bash", "-lc", f"nvidia-smi > {{OUT / 'nvidia_smi.txt'}} 2>&1 || true"], cwd=RDK)
        run(["bash", "-lc", f"{{PYTHON}} -m pip freeze > {{OUT / 'pip_freeze.txt'}}"], cwd=RDK)
        bundle_artifacts()
        atexit.unregister(bundle_artifacts)
        """
    ).strip() + "\n"


def poll_remote(
    session: str,
    run_dir: Path,
    remote_log: str,
    remote_exit: str,
    remote_bundle: str,
    remote_pid: str,
    interval_s: int,
    timeout_s: int,
) -> None:
    deadline = time.time() + timeout_s
    last_log_size: int | None = None
    unchanged_log_polls = 0
    idle_no_exit_polls = 0
    last_status = ""
    log_dest = run_dir / "remote_live.log"
    while time.time() < deadline:
        if colab_file_exists(session, remote_exit):
            break
        if colab_file_exists(session, remote_log):
            subprocess.run(
                ["colab", "download", "-s", session, remote_log, str(log_dest)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if log_dest.exists():
                log_size = log_dest.stat().st_size
                if last_log_size == log_size:
                    unchanged_log_polls += 1
                else:
                    unchanged_log_polls = 0
                    last_log_size = log_size
                lines = log_dest.read_text(errors="replace").splitlines()
                print("\n".join(lines[-12:]), flush=True)
        if colab_file_exists(session, remote_bundle):
            partial_dest = run_dir / (Path(remote_bundle).name + ".partial")
            subprocess.run(
                ["colab", "download", "-s", session, remote_bundle, str(partial_dest)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if partial_dest.exists():
                print(f"PARTIAL_ARTIFACT {partial_dest} size={partial_dest.stat().st_size}", flush=True)
        last_status = colab_status_text(session)
        remote_is_idle = colab_status_is_idle(last_status)
        if remote_is_idle and not colab_file_exists(session, remote_exit):
            idle_no_exit_polls += 1
        else:
            idle_no_exit_polls = 0
        if (
            remote_is_idle
            and not colab_file_exists(session, remote_exit)
            and (
                unchanged_log_polls >= 2
                or (idle_no_exit_polls >= 2 and not colab_file_exists(session, remote_bundle))
            )
        ):
            evidence = {
                "status": "HOLD_REMOTE_NO_SENTINEL",
                "session": session,
                "remote_log": remote_log,
                "remote_exit": remote_exit,
                "remote_pid": remote_pid,
                "remote_bundle": remote_bundle,
                "unchanged_log_polls": unchanged_log_polls,
                "idle_no_exit_polls": idle_no_exit_polls,
                "poll_interval_s": interval_s,
                "local_live_log": str(log_dest),
                "colab_status": last_status,
                "interpretation": (
                    "The Colab session reported idle while the workflow exit "
                    "sentinel was missing and the remote log stopped growing. "
                    "Treat the run as incomplete and inspect/download any "
                    "partial artifacts manually before reusing checkpoints."
                ),
            }
            (run_dir / "REMOTE_NO_SENTINEL.json").write_text(
                json.dumps(evidence, indent=2, sort_keys=True) + "\n"
            )
            (run_dir / "REMOTE_NO_SENTINEL.md").write_text(
                "\n".join(
                    [
                        "# Remote Colab Workflow Lost Sentinel",
                        "",
                        "status: `HOLD_REMOTE_NO_SENTINEL`",
                        "",
                        f"- session: `{session}`",
                        f"- remote_log: `{remote_log}`",
                        f"- remote_exit: `{remote_exit}`",
                        f"- remote_pid: `{remote_pid}`",
                        f"- remote_bundle: `{remote_bundle}`",
                        f"- unchanged_log_polls: `{unchanged_log_polls}`",
                        f"- idle_no_exit_polls: `{idle_no_exit_polls}`",
                        f"- poll_interval_s: `{interval_s}`",
                        "",
                        "The Colab session reported idle while the workflow "
                        "exit sentinel was missing and the downloaded remote "
                        "log stopped growing. This means the remote job should "
                        "be treated as incomplete, even if partial checkpoints "
                        "or logs exist.",
                        "",
                        "Do not promote partial checkpoints without an "
                        "explicit local gate and evidence summary.",
                        "",
                    ]
                )
            )
            raise SystemExit("HOLD_REMOTE_NO_SENTINEL: Colab workflow disappeared without exit sentinel")
        time.sleep(interval_s)
    else:
        timeout_evidence = {
            "status": "HOLD_REMOTE_TIMEOUT",
            "session": session,
            "remote_log": remote_log,
            "remote_exit": remote_exit,
            "remote_pid": remote_pid,
            "remote_bundle": remote_bundle,
            "timeout_s": timeout_s,
            "last_colab_status": last_status,
        }
        (run_dir / "REMOTE_TIMEOUT.json").write_text(
            json.dumps(timeout_evidence, indent=2, sort_keys=True) + "\n"
        )
        raise SystemExit(f"Timed out waiting for {remote_exit}")

    run(["colab", "download", "-s", session, remote_exit, str(run_dir / Path(remote_exit).name)])
    if colab_file_exists(session, remote_log):
        run(["colab", "download", "-s", session, remote_log, str(run_dir / Path(remote_log).name)])
    if colab_file_exists(session, remote_bundle):
        bundle_dest = run_dir / Path(remote_bundle).name
        run(["colab", "download", "-s", session, remote_bundle, str(bundle_dest)])
        extract_dir = run_dir / "artifact"
        extract_dir.mkdir(exist_ok=True)
        with tarfile.open(bundle_dest) as tf:
            tf.extractall(extract_dir)
        print(f"DOWNLOADED_ARTIFACT {bundle_dest}", flush=True)
    else:
        print(f"REMOTE_BUNDLE_MISSING {remote_bundle}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Open Duck CUDA workflow through google-colab-cli.")
    parser.add_argument("--session", default=DEFAULT_SESSION)
    parser.add_argument("--rdk-root", default=str(ROOT))
    parser.add_argument("--playground-root", default=str(DEFAULT_PLAYGROUND))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--upload-root", default=str(DEFAULT_UPLOAD_ROOT))
    parser.add_argument(
        "--workflow",
        choices=[
            "eval",
            "smoke",
            "training-smoke",
            "candidate",
            "candidate-only",
            "candidate-eval-only",
            "checkpoint-sweep",
            "staged-curriculum",
            "all",
        ],
        default="eval",
    )
    parser.add_argument("--run", action="store_true", help="execute; default is plan-only")
    parser.add_argument("--skip-deps", action="store_true", help="reuse remote dependencies")
    parser.add_argument(
        "--skip-audit",
        action="store_true",
        help=(
            "Skip the repeated policy/sim contract audit in the remote workflow. "
            "Use only after the 101/14 contract has already been verified."
        ),
    )
    parser.add_argument("--no-poll", action="store_true", help="start remote job and return")
    parser.add_argument("--poll-interval-s", type=int, default=60)
    parser.add_argument("--timeout-s", type=int, default=7200)
    parser.add_argument("--smoke-num-timesteps", type=int, default=64)
    parser.add_argument(
        "--smoke-export-min-step",
        type=int,
        default=1,
        help=(
            "Pass --export-min-step to the tiny training-smoke run. The "
            "default skips step-0 ONNX export so the smoke isolates PPO "
            "execution and final-manifest behavior."
        ),
    )
    parser.add_argument("--candidate-num-timesteps", type=int, default=200000)
    parser.add_argument(
        "--checkpoint-sweep-policies",
        nargs="+",
        default=[
            "policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/candidate.onnx",
            "policy/candidates/movement_bootstrap_v8_overshoot_stabilized_standstill_20260623/candidate.onnx",
            "policy/candidates/movement_bootstrap_v9_progress_balanced_standstill_20260623/candidate.onnx",
        ],
        help=(
            "Policy ONNX paths, relative to the uploaded RDK repo unless "
            "absolute, for --workflow checkpoint-sweep."
        ),
    )
    parser.add_argument("--checkpoint-sweep-commands", default="0.08")
    parser.add_argument("--checkpoint-sweep-duration", type=float, default=5.0)
    parser.add_argument("--checkpoint-sweep-bridge-mode", default="fitted")
    parser.add_argument("--checkpoint-sweep-timeout-s", type=int, default=3600)
    parser.add_argument(
        "--staged-timesteps-scale",
        type=float,
        default=1.0,
        help=(
            "Scale the three staged-curriculum phase lengths. The base phases "
            "depend on --staged-recipe."
        ),
    )
    parser.add_argument(
        "--staged-recipe",
        choices=[
            "movement_bootstrap_v15",
            "movement_bootstrap_v14",
            "movement_bootstrap_v13",
            "movement_bootstrap_v12",
            "movement_bootstrap_v11",
            "movement_bootstrap_v10",
            "movement_bootstrap_v9",
            "movement_bootstrap_v8",
            "movement_bootstrap_v7",
            "movement_bootstrap_v6",
            "movement_bootstrap_v5",
            "movement_bootstrap_v4",
            "movement_bootstrap_v3",
            "movement_bootstrap_v2",
            "shortfall_v1",
        ],
        default="movement_bootstrap_v15",
        help=(
            "Recipe passed to tools/plan_staged_curriculum_training.py for "
            "--workflow staged-curriculum. The current default is "
            "movement_bootstrap_v15, which separates no-bridge gait discovery "
            "from mild/fitted actuator transfer after the V14 partial "
            "checkpoint remained low-motion. movement_bootstrap_v14 starts "
            "with a mild bridge for motion discovery before transferring to "
            "the fitted actuator envelope. "
            "movement_bootstrap_v6 explicitly "
            "targets continuity from the in-envelope phase-1 lead. "
            "movement_bootstrap_v7 is intended to be run with "
            "--staged-initial-restore-checkpoint pointing at the recovered "
            "v5 phase-1 checkpoint; movement_bootstrap_v8 is intended to start "
            "from the v7 anchored checkpoint and target the x=0.08 lunge; "
            "movement_bootstrap_v9 starts from v7 again with lighter damping "
            "after v8 stabilized into standstill; movement_bootstrap_v10 "
            "targets the multi-seed V7/V9 failure surfaces; "
            "movement_bootstrap_v11 starts a fresh hard-progress lineage after "
            "V10 failed mostly by freezing; movement_bootstrap_v12 adds "
            "command-progress failure to invalidate V11-style no-motion; "
            "movement_bootstrap_v13 makes that failure carry signed negative "
            "reward."
        ),
    )
    parser.add_argument(
        "--staged-phase-timeout-s",
        type=int,
        default=10800,
        help="Per-phase timeout for --workflow staged-curriculum.",
    )
    parser.add_argument(
        "--staged-stop-after-phase",
        type=int,
        default=None,
        help=(
            "Pass through to the staged planner to stop after this 1-based "
            "phase. Useful for recovering a trainable intermediate checkpoint."
        ),
    )
    parser.add_argument(
        "--staged-initial-restore-checkpoint",
        default=None,
        help=(
            "Checkpoint path visible inside the Colab runtime to use as the "
            "starting point for phase 1 of a staged-curriculum workflow."
        ),
    )
    parser.add_argument(
        "--staged-phase-gate-freeze-check",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Run a short candidate gate after each staged phase and stop on "
            "low forward progress. Enabled by default for staged workflows."
        ),
    )
    parser.add_argument("--staged-phase-gate-command-x", type=float, default=0.08)
    parser.add_argument("--staged-phase-gate-duration-s", type=float, default=5.0)
    parser.add_argument(
        "--staged-phase-gate-bridge-mode",
        choices=["vanilla", "fitted", "stress", "all"],
        default="fitted",
    )
    parser.add_argument(
        "--staged-phase-gate-platform",
        choices=["cpu", "gpu"],
        default="gpu",
    )
    parser.add_argument("--staged-phase-gate-timeout-s", type=int, default=900)
    parser.add_argument("--candidate-ppo-num-envs", type=int, default=256)
    parser.add_argument("--candidate-ppo-num-evals", type=int, default=4)
    parser.add_argument("--candidate-episode-length", type=int, default=600)
    parser.add_argument("--candidate-unroll-length", type=int, default=10)
    parser.add_argument("--candidate-ppo-batch-size", type=int, default=256)
    parser.add_argument("--candidate-ppo-num-minibatches", type=int, default=4)
    parser.add_argument("--candidate-ppo-num-updates-per-batch", type=int, default=4)
    parser.add_argument(
        "--candidate-restore-checkpoint-path",
        default=None,
        help=(
            "Optional checkpoint path visible inside the Colab runtime. Use "
            "this only after uploading or packaging the checkpoint separately."
        ),
    )
    parser.add_argument(
        "--candidate-existing-policy",
        help=(
            "Local ONNX path to upload and evaluate with --workflow "
            "candidate-eval-only. This avoids rerunning training when a prior "
            "Colab job disconnected during gate evaluation."
        ),
    )
    parser.add_argument(
        "--candidate-training-manifest",
        help=(
            "Optional local smoke_manifest JSON to upload with "
            "--workflow candidate-eval-only for candidate packaging."
        ),
    )
    parser.add_argument(
        "--candidate-name",
        help="Optional stable candidate name for training or eval-only packages.",
    )
    parser.add_argument(
        "--artifact-checkpoint-mode",
        choices=["none", "latest", "all"],
        default="latest",
        help=(
            "Checkpoint directories to include in downloaded Colab artifacts. "
            "latest preserves one continuation point per training run without "
            "copying every intermediate checkpoint."
        ),
    )
    parser.add_argument("--candidate-timeout-s", type=int, default=10800)
    parser.add_argument("--candidate-target-rate-scale", type=float, default=-0.001)
    parser.add_argument("--candidate-actuator-tracking-scale", type=float, default=0.0)
    parser.add_argument("--candidate-tracking-lin-vel-scale", type=float, default=12.0)
    parser.add_argument("--candidate-tracking-ang-vel-scale", type=float, default=0.0)
    parser.add_argument("--candidate-tracking-sigma", type=float, default=0.0025)
    parser.add_argument("--candidate-forward-progress-scale", type=float, default=2.0)
    parser.add_argument("--candidate-forward-progress-deadband", type=float, default=0.02)
    parser.add_argument("--candidate-forward-shortfall-scale", type=float, default=0.0)
    parser.add_argument(
        "--candidate-forward-shortfall-required-ratio",
        type=float,
        default=0.5,
    )
    parser.add_argument("--candidate-action-rate-scale", type=float, default=-0.1)
    parser.add_argument("--candidate-action-magnitude-scale", type=float, default=-0.05)
    parser.add_argument("--candidate-stand-still-scale", type=float, default=-0.2)
    parser.add_argument("--candidate-alive-scale", type=float, default=0.5)
    parser.add_argument("--candidate-imitation-scale", type=float, default=0.25)
    parser.add_argument("--candidate-lin-vel-x-min", type=float, default=0.04)
    parser.add_argument("--candidate-lin-vel-x-max", type=float, default=0.12)
    parser.add_argument("--candidate-command-resample-steps", type=int, default=500)
    parser.add_argument("--candidate-zero-command-probability", type=float, default=0.1)
    parser.add_argument(
        "--candidate-disable-actuator-bridge",
        action="store_true",
        help=(
            "Disable the default candidate actuator bridge for a locomotion "
            "bootstrap run. This is offline training only; sim gates still "
            "evaluate the exported policy against fitted/stress bridge modes."
        ),
    )
    parser.add_argument("--candidate-actuator-bridge-delay-min-ticks", type=int, default=3)
    parser.add_argument("--candidate-actuator-bridge-delay-max-ticks", type=int, default=8)
    parser.add_argument("--candidate-actuator-bridge-tau-min-s", type=float, default=0.06)
    parser.add_argument("--candidate-actuator-bridge-tau-max-s", type=float, default=0.14)
    parser.add_argument(
        "--candidate-actuator-bridge-velocity-limit-min-rad-s",
        type=float,
        default=2.5,
    )
    parser.add_argument(
        "--candidate-actuator-bridge-velocity-limit-max-rad-s",
        type=float,
        default=4.7,
    )
    parser.add_argument(
        "--candidate-actuator-bridge-per-joint-variation",
        type=float,
        default=0.15,
    )
    args = parser.parse_args()

    rdk_root = Path(args.rdk_root).resolve()
    playground_root = Path(args.playground_root).resolve()
    if not rdk_root.exists():
        raise SystemExit(f"RDK repo missing: {rdk_root}")
    if not playground_root.exists():
        raise SystemExit(f"Playground repo missing: {playground_root}")
    candidate_existing_policy = (
        Path(args.candidate_existing_policy).expanduser().resolve()
        if args.candidate_existing_policy
        else None
    )
    candidate_training_manifest = (
        Path(args.candidate_training_manifest).expanduser().resolve()
        if args.candidate_training_manifest
        else None
    )
    if args.workflow == "candidate-eval-only" and candidate_existing_policy is None:
        raise SystemExit("--workflow candidate-eval-only requires --candidate-existing-policy")
    if candidate_existing_policy is not None and not candidate_existing_policy.exists():
        raise SystemExit(f"Candidate ONNX missing: {candidate_existing_policy}")
    if (
        candidate_training_manifest is not None
        and not candidate_training_manifest.exists()
    ):
        raise SystemExit(f"Candidate training manifest missing: {candidate_training_manifest}")

    ts = timestamp()
    run_dir = Path(args.output_root).resolve() / f"{args.session}-{args.workflow}-{ts}"
    upload_root = Path(args.upload_root).resolve()
    rdk_tar = upload_root / f"open-duck-mini-rdkx5_cli_{ts}.tar.gz"
    playground_tar = upload_root / f"Open_Duck_Playground_cli_{ts}.tar.gz"

    print(f"COLAB_SESSION {args.session}")
    print(f"WORKFLOW {args.workflow}")
    print(f"RUN_DIR {run_dir}")
    print(f"JAX_PIN {PINNED_JAX_VERSION}")
    if not args.run:
        print("PLAN_ONLY pass --run to upload/start remote work")
        return 0

    run_dir.mkdir(parents=True, exist_ok=True)
    initialize_content_api(args.session, run_dir)
    make_tarball(rdk_root, rdk_tar, "open-duck-mini-rdkx5")
    make_tarball(playground_root, playground_tar, "Open_Duck_Playground")
    rdk_remote = "/content/open-duck-mini-rdkx5_cli.tar.gz"
    playground_remote = "/content/Open_Duck_Playground_cli.tar.gz"
    run(["colab", "upload", "-s", args.session, str(rdk_tar), rdk_remote])
    run(["colab", "upload", "-s", args.session, str(playground_tar), playground_remote])
    candidate_remote_policy = None
    candidate_remote_manifest = None
    if candidate_existing_policy is not None:
        candidate_remote_policy = "/content/open_duck_candidate_existing_policy.onnx"
        run([
            "colab",
            "upload",
            "-s",
            args.session,
            str(candidate_existing_policy),
            candidate_remote_policy,
        ])
    if candidate_training_manifest is not None:
        candidate_remote_manifest = "/content/open_duck_candidate_training_manifest.json"
        run([
            "colab",
            "upload",
            "-s",
            args.session,
            str(candidate_training_manifest),
            candidate_remote_manifest,
        ])
    start_remote_job(
        args,
        run_dir,
        rdk_remote,
        playground_remote,
        candidate_remote_policy=candidate_remote_policy,
        candidate_remote_manifest=candidate_remote_manifest,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
