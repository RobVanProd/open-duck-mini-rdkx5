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
    if "outputs" in parts and "analysis" in parts and "colab_cli" in parts:
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


def write_console_script(path: Path, remote_script: str) -> None:
    path.write_text(remote_script.strip() + "\nexit\n")


def start_remote_job(args: argparse.Namespace, run_dir: Path, rdk_remote_tar: str, playground_remote_tar: str) -> None:
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

    driver = build_remote_driver(args, workflow_name, rdk_remote_tar, playground_remote_tar, remote_bundle)
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
    print(">>>", f"colab console -s {args.session} < {console_script}", flush=True)
    completed = subprocess.run(
        ["colab", "console", "-s", args.session],
        input=console_script.read_text(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=120,
        check=False,
    )
    (run_dir / "console_start.log").write_text(completed.stdout or "")
    print(completed.stdout[-2000:] if completed.stdout else "", flush=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)

    if args.no_poll:
        print(f"Remote job started. Bundle will be {remote_bundle}", flush=True)
        return
    poll_remote(args.session, run_dir, remote_log, remote_exit, remote_bundle, args.poll_interval_s, args.timeout_s)


def build_remote_driver(args: argparse.Namespace, workflow_name: str, rdk_tar: str, playground_tar: str, remote_bundle: str) -> str:
    run_smoke = args.workflow in {"smoke", "all", "candidate"}
    run_candidate = args.workflow in {"candidate", "candidate-only", "all"}
    run_eval = args.workflow in {"eval", "smoke", "candidate", "all"}
    install_deps = not args.skip_deps
    smoke_steps = args.smoke_num_timesteps
    candidate_steps = args.candidate_num_timesteps
    return textwrap.dedent(
        f"""
        import atexit
        import datetime as dt
        import json
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

        def copy_training_outputs(src, dest):
            src = Path(src)
            dest = Path(dest)
            if not src.exists():
                return
            dest.mkdir(parents=True, exist_ok=True)
            for run_dir in sorted(src.glob("smoke_*_gpu")):
                run_dest = dest / run_dir.name
                run_dest.mkdir(exist_ok=True)
                for pattern in ["*.onnx", "smoke_manifest*.json", "stdout.txt", "stderr.txt"]:
                    for item in sorted(run_dir.glob(pattern)):
                        try:
                            (run_dest / item.name).write_bytes(item.read_bytes())
                        except Exception as exc:
                            print("copy_training_outputs_warning", item, type(exc).__name__, exc, flush=True)

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

        def run(cmd, cwd=None, timeout=None, env=None):
            print("\\n>>>", " ".join(str(x) for x in cmd), flush=True)
            completed = subprocess.run(cmd, cwd=cwd, timeout=timeout, env=env, text=True)
            print("<<< returncode", completed.returncode, flush=True)
            if completed.returncode != 0:
                RUN_STATUS["exit_status"] = completed.returncode
                raise SystemExit(completed.returncode)

        run(["rm", "-rf", str(RDK), str(PLAYGROUND)])
        run(["tar", "-xzf", "{rdk_tar}", "-C", "/content"])
        run(["tar", "-xzf", "{playground_tar}", "-C", "/content"])

        if {install_deps!r}:
            run([PYTHON, "-m", "pip", "install", "-U", "pip"], timeout=600)
            run([
                PYTHON, "-m", "pip", "install", "-U",
                "jax[cuda12]=={PINNED_JAX_VERSION}",
                "jaxlib=={PINNED_JAX_VERSION}",
                "playground==0.0.5",
                "mujoco>=3.2.7,<3.10",
                "mujoco-mjx>=3.2.7",
                "onnxruntime",
                "ml-collections",
                "numpy",
                "matplotlib",
                "mediapy",
                "tensorflow",
                "tf2onnx",
            ], timeout=1800)
            run([PYTHON, "-m", "pip", "install", "--no-deps", "-e", str(PLAYGROUND)], timeout=600)

        print("=== Versions ===", flush=True)
        for name in ["jax", "jaxlib", "brax", "mujoco", "mujoco-mjx", "playground"]:
            try:
                print(name, metadata.version(name), flush=True)
            except Exception as exc:
                print(name, type(exc).__name__, exc, flush=True)
        run([PYTHON, "-c", "import jax; print('backend', jax.default_backend(), jax.devices()); print('has_device_put_replicated', hasattr(jax, 'device_put_replicated'))"])

        if {run_eval!r}:
            run([
                PYTHON, "tools/audit_policy_sim_contract.py",
                "--policy", "policy/BEST_WALK_ONNX_2.onnx",
                "--playground-path", str(PLAYGROUND),
                "--env-python", PYTHON,
                "--instantiate-timeout-s", "600",
                "--output-md", str(OUT / "POLICY_SIM_CONTRACT_AUDIT_CUDA.md"),
                "--output-json", str(OUT / "policy_sim_contract_audit_cuda.json"),
            ], cwd=RDK, timeout=900)
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

        if {run_candidate!r}:
            run([
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
                "--target-rate-scale", "-0.01",
                "--actuator-tracking-scale", "0.0",
                "--tracking-lin-vel-scale", "{args.candidate_tracking_lin_vel_scale}",
                "--alive-scale", "{args.candidate_alive_scale}",
                "--imitation-scale", "{args.candidate_imitation_scale}",
                "--lin-vel-x-min", "{args.candidate_lin_vel_x_min}",
                "--lin-vel-x-max", "{args.candidate_lin_vel_x_max}",
                "--lin-vel-y-min", "0.0",
                "--lin-vel-y-max", "0.0",
                "--ang-vel-yaw-min", "0.0",
                "--ang-vel-yaw-max", "0.0",
                "--head-range-factor", "0.0",
                "--timeout-s", "{args.candidate_timeout_s}",
            ], cwd=RDK, timeout={args.candidate_timeout_s + 300})
            run_dirs = sorted(Path("/content/open_duck_training_runs_cli").glob("smoke_*_gpu"))
            if not run_dirs:
                raise SystemExit("candidate training produced no smoke_*_gpu run directory")
            run_dir = run_dirs[-1]
            onnx_files = sorted(run_dir.glob("*.onnx"))
            if not onnx_files:
                raise SystemExit(f"candidate training produced no ONNX files in {{run_dir}}")
            latest_onnx = onnx_files[-1]
            candidate_name = "open_duck_mini_actuator_bridge_cli_" + dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
            run([
                PYTHON, "tools/summarize_training_run.py", str(run_dir),
                "--output-md", str(OUT / f"{{candidate_name}}_training_run_summary.md"),
                "--output-json", str(OUT / f"{{candidate_name}}_training_run_summary.json"),
            ], cwd=RDK, timeout=300)
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
            run([
                PYTHON, "tools/package_candidate_policy.py", str(latest_onnx),
                "--candidate-name", candidate_name,
                "--training-manifest", str(run_dir / "smoke_manifest.final.json"),
                "--contract-audit", str(OUT / "POLICY_SIM_CONTRACT_AUDIT_CUDA.md"),
                "--actuator-bridge-eval", str(OUT / f"{{candidate_name}}_candidate_gate_x008.md"),
                "--output-md", str(OUT / f"{{candidate_name}}_policy_package.md"),
                "--output-json", str(OUT / f"{{candidate_name}}_policy_metadata.json"),
            ], cwd=RDK, timeout=300)
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


def poll_remote(session: str, run_dir: Path, remote_log: str, remote_exit: str, remote_bundle: str, interval_s: int, timeout_s: int) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if colab_file_exists(session, remote_exit):
            break
        if colab_file_exists(session, remote_log):
            log_dest = run_dir / "remote_live.log"
            subprocess.run(
                ["colab", "download", "-s", session, remote_log, str(log_dest)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if log_dest.exists():
                lines = log_dest.read_text(errors="replace").splitlines()
                print("\n".join(lines[-12:]), flush=True)
        time.sleep(interval_s)
    else:
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
        choices=["eval", "smoke", "candidate", "candidate-only", "all"],
        default="eval",
    )
    parser.add_argument("--run", action="store_true", help="execute; default is plan-only")
    parser.add_argument("--skip-deps", action="store_true", help="reuse remote dependencies")
    parser.add_argument("--no-poll", action="store_true", help="start remote job and return")
    parser.add_argument("--poll-interval-s", type=int, default=60)
    parser.add_argument("--timeout-s", type=int, default=7200)
    parser.add_argument("--smoke-num-timesteps", type=int, default=64)
    parser.add_argument("--candidate-num-timesteps", type=int, default=200000)
    parser.add_argument("--candidate-ppo-num-envs", type=int, default=256)
    parser.add_argument("--candidate-ppo-num-evals", type=int, default=4)
    parser.add_argument("--candidate-episode-length", type=int, default=600)
    parser.add_argument("--candidate-unroll-length", type=int, default=10)
    parser.add_argument("--candidate-ppo-batch-size", type=int, default=256)
    parser.add_argument("--candidate-ppo-num-minibatches", type=int, default=4)
    parser.add_argument("--candidate-ppo-num-updates-per-batch", type=int, default=4)
    parser.add_argument("--candidate-timeout-s", type=int, default=10800)
    parser.add_argument("--candidate-tracking-lin-vel-scale", type=float, default=3.0)
    parser.add_argument("--candidate-alive-scale", type=float, default=1.0)
    parser.add_argument("--candidate-imitation-scale", type=float, default=1.0)
    parser.add_argument("--candidate-lin-vel-x-min", type=float, default=0.0)
    parser.add_argument("--candidate-lin-vel-x-max", type=float, default=0.12)
    args = parser.parse_args()

    rdk_root = Path(args.rdk_root).resolve()
    playground_root = Path(args.playground_root).resolve()
    if not rdk_root.exists():
        raise SystemExit(f"RDK repo missing: {rdk_root}")
    if not playground_root.exists():
        raise SystemExit(f"Playground repo missing: {playground_root}")

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
    make_tarball(rdk_root, rdk_tar, "open-duck-mini-rdkx5")
    make_tarball(playground_root, playground_tar, "Open_Duck_Playground")
    rdk_remote = "/content/open-duck-mini-rdkx5_cli.tar.gz"
    playground_remote = "/content/Open_Duck_Playground_cli.tar.gz"
    run(["colab", "upload", "-s", args.session, str(rdk_tar), rdk_remote])
    run(["colab", "upload", "-s", args.session, str(playground_tar), playground_remote])
    start_remote_job(args, run_dir, rdk_remote, playground_remote)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
