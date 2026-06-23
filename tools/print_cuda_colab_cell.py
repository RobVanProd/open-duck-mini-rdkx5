#!/usr/bin/env python3
"""Print a single CUDA/Colab cell for actuator-bridge training checks."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import textwrap


DEFAULT_RDK_REPO = "https://github.com/RobVanProd/open-duck-mini-rdkx5.git"
DEFAULT_PLAYGROUND_REPO = "https://github.com/RobVanProd/Open_Duck_Playground.git"
DEFAULT_RDK_BRANCH = "main"
DEFAULT_PLAYGROUND_BRANCH = "main"
DEFAULT_CUDA_JAX_VERSION = "0.7.2"


def bash_bool(value: bool) -> str:
    return "1" if value else "0"


def build_cell(args: argparse.Namespace) -> str:
    candidate_flag = bash_bool(args.run_candidate)
    auto_download_flag = bash_bool(not args.no_auto_download)
    smoke_steps = args.smoke_num_timesteps
    candidate_steps = args.candidate_num_timesteps
    candidate_disable_bridge_line = (
        "    --disable-actuator-bridge \\\n"
        if args.candidate_disable_actuator_bridge
        else ""
    )
    cell = f"""%%bash
set -euo pipefail

# Open Duck Mini CUDA actuator-bridge workflow.
# This is offline-only: no robot SSH, deploy, runtime changes, or policy overwrite.
cd /content

export RDK_REPO={args.rdk_repo!r}
export PLAYGROUND_REPO={args.playground_repo!r}
export RDK_BRANCH={args.rdk_branch!r}
export PLAYGROUND_BRANCH={args.playground_branch!r}
export RUN_CANDIDATE={candidate_flag}
export CANDIDATE_NUM_TIMESTEPS={candidate_steps}
export CANDIDATE_RESTORE_CHECKPOINT_PATH={args.candidate_restore_checkpoint_path!r}
export CUDA_AUTO_DOWNLOAD={auto_download_flag}
export ARTIFACT_ROOT="/content/open_duck_cuda_artifacts"
BUNDLE="/content/open_duck_cuda_artifacts_$(date -u +%Y%m%dT%H%M%SZ).tar.gz"
export BUNDLE
if [ -z "${{PYTHON_BIN:-}}" ]; then
  if [ -x /usr/bin/python3 ]; then
    PYTHON_BIN=/usr/bin/python3
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
  else
    PYTHON_BIN="$(command -v python)"
  fi
  export PYTHON_BIN
fi
echo "PYTHON_BIN=$PYTHON_BIN"
if [ -n "$CANDIDATE_RESTORE_CHECKPOINT_PATH" ]; then
  CANDIDATE_RESTORE_ARGS=(--restore-checkpoint-path "$CANDIDATE_RESTORE_CHECKPOINT_PATH")
else
  CANDIDATE_RESTORE_ARGS=()
fi

prompt_for_github_token() {{
  if [ -n "${{GITHUB_TOKEN:-}}" ]; then
    echo "GitHub token: provided by environment"
    return 0
  fi
  if [ -n "${{GH_TOKEN:-}}" ]; then
    GITHUB_TOKEN="$GH_TOKEN"
    export GITHUB_TOKEN
    echo "GitHub token: provided by GH_TOKEN"
    return 0
  fi
  echo "GitHub token: not provided; attempting public repo access only"
  echo "For private repos, set GITHUB_TOKEN or GH_TOKEN before running this cell."
}}

setup_git_auth() {{
  export GIT_TERMINAL_PROMPT=0
  if [ -z "${{GITHUB_TOKEN:-}}" ]; then
    unset GIT_ASKPASS
    return 0
  fi
  GIT_ASKPASS=/tmp/open_duck_git_askpass.sh
  cat > "$GIT_ASKPASS" <<'SH'
#!/bin/sh
case "$1" in
  *Username*) printf '%s\n' "x-access-token" ;;
  *Password*) printf '%s\n' "$GITHUB_TOKEN" ;;
  *) printf '\n' ;;
esac
SH
  chmod 700 "$GIT_ASKPASS"
  export GIT_ASKPASS
}}

clone_or_update_repo() {{
  local repo="$1"
  local path="$2"
  local branch="$3"
  local name="$4"
  echo "=== Sync $name ==="
  if [ ! -d "$path/.git" ]; then
    rm -rf "$path"
    git clone "$repo" "$path"
  fi
  git -C "$path" fetch origin
  git -C "$path" checkout "$branch"
  git -C "$path" pull --ff-only
}}

bundle_cuda_artifacts() {{
  local exit_status="${{1:-0}}"
  set +e
  echo "=== Build CUDA artifact bundle (exit_status=$exit_status) ==="
  rm -rf "$ARTIFACT_ROOT"
  mkdir -p "$ARTIFACT_ROOT"
  {{
    echo "exit_status=$exit_status"
    echo "timestamp_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "rdk_repo=$RDK_REPO"
    echo "rdk_branch=$RDK_BRANCH"
    if [ -n "${{GITHUB_TOKEN:-}}" ]; then
      echo "github_token_present=yes"
    else
      echo "github_token_present=no"
    fi
    if [ -d /content/open-duck-mini-rdkx5/.git ]; then
      echo "rdk_commit=$(git -C /content/open-duck-mini-rdkx5 rev-parse HEAD 2>/dev/null || echo UNKNOWN)"
      echo "rdk_dirty_files=$(git -C /content/open-duck-mini-rdkx5 status --short 2>/dev/null | wc -l | tr -d ' ')"
    else
      echo "rdk_commit=UNKNOWN"
      echo "rdk_dirty_files=UNKNOWN"
    fi
    echo "playground_repo=$PLAYGROUND_REPO"
    echo "playground_branch=$PLAYGROUND_BRANCH"
    if [ -d /content/Open_Duck_Playground/.git ]; then
      echo "playground_commit=$(git -C /content/Open_Duck_Playground rev-parse HEAD 2>/dev/null || echo UNKNOWN)"
      echo "playground_dirty_files=$(git -C /content/Open_Duck_Playground status --short 2>/dev/null | wc -l | tr -d ' ')"
    else
      echo "playground_commit=UNKNOWN"
      echo "playground_dirty_files=UNKNOWN"
    fi
    echo "run_candidate=$RUN_CANDIDATE"
  }} > "$ARTIFACT_ROOT/CUDA_CELL_EXIT_STATUS.txt"
  {{
    echo "python_executable=${{PYTHON_BIN:-UNKNOWN}}"
    "$PYTHON_BIN" - <<'PY' 2>/dev/null || true
import sys
from importlib import metadata

print("python_version=" + sys.version.replace("\\n", " "))
for package in [
    "jax",
    "jaxlib",
    "mujoco",
    "mujoco-mjx",
    "playground",
    "mujoco-playground",
    "onnxruntime",
    "tensorflow",
]:
    key = package.replace("-", "_") + "_version"
    try:
        value = metadata.version(package)
    except metadata.PackageNotFoundError:
        value = "NOT_INSTALLED"
    except Exception as exc:
        value = type(exc).__name__ + ":" + str(exc)
    print(key + "=" + value)
PY
    if command -v nvidia-smi >/dev/null 2>&1; then
      nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -n 1 | sed 's/^/gpu_name=/'
    else
      echo "gpu_name=UNKNOWN"
    fi
  }} >> "$ARTIFACT_ROOT/CUDA_CELL_EXIT_STATUS.txt"
  "$PYTHON_BIN" -m pip freeze > "$ARTIFACT_ROOT/pip_freeze.txt" 2>&1 || true
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi > "$ARTIFACT_ROOT/nvidia_smi.txt" 2>&1 || true
  else
    echo "nvidia-smi not found" > "$ARTIFACT_ROOT/nvidia_smi.txt"
  fi

  if [ -d /content/open-duck-mini-rdkx5/outputs/analysis/cuda_manual ]; then
    cp -a /content/open-duck-mini-rdkx5/outputs/analysis/cuda_manual "$ARTIFACT_ROOT/"
  else
    echo "missing /content/open-duck-mini-rdkx5/outputs/analysis/cuda_manual" >> "$ARTIFACT_ROOT/CUDA_CELL_EXIT_STATUS.txt"
  fi

  for TRAINING_ROOT in /content/open_duck_training_smokes /content/open_duck_training_runs; do
    if [ -d "$TRAINING_ROOT" ]; then
      DEST_ROOT="$ARTIFACT_ROOT/$(basename "$TRAINING_ROOT")"
      mkdir -p "$DEST_ROOT"
      for RUN in "$TRAINING_ROOT"/smoke_*_gpu; do
        [ -d "$RUN" ] || continue
        DEST="$DEST_ROOT/$(basename "$RUN")"
        mkdir -p "$DEST"
        cp "$RUN"/*.onnx "$DEST/" 2>/dev/null || true
        cp "$RUN"/smoke_manifest*.json "$DEST/" 2>/dev/null || true
        cp "$RUN"/stdout.txt "$DEST/" 2>/dev/null || true
        cp "$RUN"/stderr.txt "$DEST/" 2>/dev/null || true
      done
    fi
  done

  if tar -czf "$BUNDLE" -C /content "$(basename "$ARTIFACT_ROOT")"; then
    "$PYTHON_BIN" - <<PY
import hashlib
from pathlib import Path
bundle = Path("$BUNDLE")
sha256 = hashlib.sha256(bundle.read_bytes()).hexdigest()
sidecar = Path(str(bundle) + ".sha256")
sidecar.write_text(f"{{sha256}}  {{bundle.name}}\\n")
print("CUDA_ARTIFACT_BUNDLE", bundle)
print("CUDA_ARTIFACT_BUNDLE_SIZE_BYTES", bundle.stat().st_size)
print("CUDA_ARTIFACT_BUNDLE_SHA256", sha256)
print("CUDA_ARTIFACT_BUNDLE_SHA256_FILE", sidecar)
PY
    if [ "${{CUDA_AUTO_DOWNLOAD:-1}}" = "1" ]; then
      "$PYTHON_BIN" - <<PY
from pathlib import Path

bundle = Path("$BUNDLE")
sidecar = Path(str(bundle) + ".sha256")
try:
    from google.colab import files
except Exception as exc:
    print("CUDA_ARTIFACT_DOWNLOAD_SKIPPED", type(exc).__name__, exc)
else:
    try:
        files.download(str(bundle))
        print("CUDA_ARTIFACT_DOWNLOAD_TRIGGERED", bundle)
        if sidecar.exists():
            files.download(str(sidecar))
            print("CUDA_ARTIFACT_SHA256_DOWNLOAD_TRIGGERED", sidecar)
    except Exception as exc:
        print("CUDA_ARTIFACT_DOWNLOAD_FAILED", type(exc).__name__, exc)
PY
    fi
  else
    echo "CUDA_ARTIFACT_BUNDLE_FAILED $BUNDLE"
  fi
}}

on_cuda_cell_exit() {{
  local rc="$?"
  bundle_cuda_artifacts "$rc"
  exit "$rc"
}}
trap on_cuda_cell_exit EXIT

echo "=== GPU ==="
nvidia-smi || true

echo "=== Python/JAX before setup ==="
"$PYTHON_BIN" - <<'PY'
try:
    import jax
    print("jax", jax.__version__)
    print("backend", jax.default_backend())
    print("devices", jax.devices())
except Exception as exc:
    print("jax_pre_setup_error", type(exc).__name__, exc)
PY

echo "=== Clone / update repos ==="
prompt_for_github_token
setup_git_auth
clone_or_update_repo "$RDK_REPO" /content/open-duck-mini-rdkx5 "$RDK_BRANCH" "RDK repo"
clone_or_update_repo "$PLAYGROUND_REPO" /content/Open_Duck_Playground "$PLAYGROUND_BRANCH" "Playground repo"

echo "=== Install CUDA eval/training deps ==="
"$PYTHON_BIN" -m pip install -U pip
"$PYTHON_BIN" -m pip install \\
  "jax[cuda12]=={DEFAULT_CUDA_JAX_VERSION}" \\
  "jaxlib=={DEFAULT_CUDA_JAX_VERSION}" \\
  "playground==0.0.5" \\
  "mujoco==3.9.0" \\
  "mujoco-mjx==3.9.0" \\
  "onnxruntime==1.27.0" \\
  "ml-collections==1.1.0" \\
  "numpy==2.0.2" \\
  "matplotlib==3.10.0" \\
  "mediapy==1.2.6" \\
  "tensorflow==2.20.0" \\
  "protobuf==5.29.6" \\
  "onnx==1.22.0"
"$PYTHON_BIN" -m pip install --no-deps "tf2onnx==1.17.0"
"$PYTHON_BIN" -m pip install --no-deps -e /content/Open_Duck_Playground

echo "=== Verify key imports ==="
"$PYTHON_BIN" - <<'PY'
import jax
import mujoco
import mujoco_playground
import mujoco_playground._src.collision as collision
print("jax", jax.__version__, jax.default_backend(), jax.devices())
print("mujoco", mujoco.__version__)
print("mujoco_playground", mujoco_playground.__file__)
print("collision", collision.__file__)
PY

cd /content/open-duck-mini-rdkx5
mkdir -p outputs/analysis/cuda_manual

echo "=== Environment check ==="
"$PYTHON_BIN" tools/check_training_env.py \\
  --playground-root /content/Open_Duck_Playground

echo "=== Policy/sim contract audit ==="
"$PYTHON_BIN" tools/audit_policy_sim_contract.py \\
  --policy policy/BEST_WALK_ONNX_2.onnx \\
  --playground-path /content/Open_Duck_Playground \\
  --env-python "$PYTHON_BIN" \\
  --instantiate-timeout-s 600 \\
  --output-md outputs/analysis/cuda_manual/POLICY_SIM_CONTRACT_AUDIT_CUDA.md \\
  --output-json outputs/analysis/cuda_manual/policy_sim_contract_audit_cuda.json

echo "=== Closed-loop baseline bridge reproduction ==="
"$PYTHON_BIN" tools/eval_policy_with_actuator_bridge.py \\
  --mode closed-loop-sim \\
  --policy policy/BEST_WALK_ONNX_2.onnx \\
  --fit-json outputs/analysis/actuator_response_fit.json \\
  --playground-path /content/Open_Duck_Playground \\
  --env-python "$PYTHON_BIN" \\
  --command-x 0.08 \\
  --duration 15 \\
  --bridge-mode all \\
  --jax-platform gpu \\
  --sim-preflight-timeout-s 600 \\
  --closed-loop-timeout-s 1800 \\
  --output-dir outputs/analysis/cuda_manual

echo "=== CUDA smoke training ==="
"$PYTHON_BIN" tools/run_actuator_bridge_training_smoke.py \\
  --playground-path /content/Open_Duck_Playground \\
  --env-python "$PYTHON_BIN" \\
  --platform gpu \\
  --run \\
  --output-root /content/open_duck_training_smokes \\
  --num-timesteps {smoke_steps} \\
  --ppo-num-envs {args.smoke_ppo_num_envs} \\
  --ppo-num-evals 1 \\
  --ppo-episode-length {args.smoke_episode_length} \\
  --ppo-unroll-length 5 \\
  --ppo-batch-size {args.smoke_ppo_batch_size} \\
  --ppo-num-minibatches 1 \\
  --ppo-num-updates-per-batch 1 \\
  --target-rate-scale -0.01 \\
  --actuator-tracking-scale 0.0 \\
  --timeout-s 1200

if [ "$RUN_CANDIDATE" = "1" ]; then
  echo "=== CUDA candidate training ==="
  "$PYTHON_BIN" tools/run_actuator_bridge_training_smoke.py \\
    --playground-path /content/Open_Duck_Playground \\
    --env-python "$PYTHON_BIN" \\
    --platform gpu \\
    --run \\
    --output-root /content/open_duck_training_runs \\
    --num-timesteps "$CANDIDATE_NUM_TIMESTEPS" \\
    --ppo-num-envs {args.candidate_ppo_num_envs} \\
    --ppo-num-evals {args.candidate_ppo_num_evals} \\
    --ppo-episode-length {args.candidate_episode_length} \\
    --ppo-unroll-length {args.candidate_unroll_length} \\
    --ppo-batch-size {args.candidate_ppo_batch_size} \\
    --ppo-num-minibatches {args.candidate_ppo_num_minibatches} \\
    --ppo-num-updates-per-batch {args.candidate_ppo_num_updates_per_batch} \\
    --target-rate-scale {args.candidate_target_rate_scale} \\
    --actuator-tracking-scale {args.candidate_actuator_tracking_scale} \\
    --tracking-lin-vel-scale {args.candidate_tracking_lin_vel_scale} \\
    --tracking-ang-vel-scale {args.candidate_tracking_ang_vel_scale} \\
    --tracking-sigma {args.candidate_tracking_sigma} \\
    --forward-progress-scale {args.candidate_forward_progress_scale} \\
    --forward-progress-deadband {args.candidate_forward_progress_deadband} \\
    --action-rate-scale {args.candidate_action_rate_scale} \\
    --action-magnitude-scale {args.candidate_action_magnitude_scale} \\
    --stand-still-scale {args.candidate_stand_still_scale} \\
    --alive-scale {args.candidate_alive_scale} \\
    --imitation-scale {args.candidate_imitation_scale} \\
    --lin-vel-x-min {args.candidate_lin_vel_x_min} \\
    --lin-vel-x-max {args.candidate_lin_vel_x_max} \\
    --lin-vel-y-min 0.0 \\
    --lin-vel-y-max 0.0 \\
    --ang-vel-yaw-min 0.0 \\
    --ang-vel-yaw-max 0.0 \\
    --command-resample-steps {args.candidate_command_resample_steps} \\
    --zero-command-probability {args.candidate_zero_command_probability} \\
    --head-range-factor 0.0 \\
{candidate_disable_bridge_line.rstrip()}
    --actuator-bridge-delay-min-ticks {args.candidate_actuator_bridge_delay_min_ticks} \\
    --actuator-bridge-delay-max-ticks {args.candidate_actuator_bridge_delay_max_ticks} \\
    --actuator-bridge-tau-min-s {args.candidate_actuator_bridge_tau_min_s} \\
    --actuator-bridge-tau-max-s {args.candidate_actuator_bridge_tau_max_s} \\
    --actuator-bridge-velocity-limit-min-rad-s {args.candidate_actuator_bridge_velocity_limit_min_rad_s} \\
    --actuator-bridge-velocity-limit-max-rad-s {args.candidate_actuator_bridge_velocity_limit_max_rad_s} \\
    --actuator-bridge-per-joint-variation {args.candidate_actuator_bridge_per_joint_variation} \\
    "${{CANDIDATE_RESTORE_ARGS[@]}}" \\
    --timeout-s {args.candidate_timeout_s}

  RUN_DIR="$(find /content/open_duck_training_runs -maxdepth 1 -type d -name 'smoke_*_gpu' | sort | tail -n 1)"
  CANDIDATE="open_duck_mini_actuator_bridge_$(date -u +%Y%m%dT%H%M%SZ)"
  LATEST_ONNX="$(find "$RUN_DIR" -maxdepth 1 -type f -name '*.onnx' -print | sort | tail -n 1)"

  "$PYTHON_BIN" tools/summarize_training_run.py "$RUN_DIR" \\
    --output-md "outputs/analysis/cuda_manual/${{CANDIDATE}}_training_run_summary.md" \\
    --output-json "outputs/analysis/cuda_manual/${{CANDIDATE}}_training_run_summary.json" || true

  echo "=== Candidate closed-loop sim gate: x=0.0 ==="
  "$PYTHON_BIN" tools/eval_policy_with_actuator_bridge.py \\
    --mode closed-loop-sim \\
    --eval-role candidate \\
    --policy "$LATEST_ONNX" \\
    --fit-json outputs/analysis/actuator_response_fit.json \\
    --playground-path /content/Open_Duck_Playground \\
    --env-python "$PYTHON_BIN" \\
    --command-x 0.0 \\
    --duration 15 \\
    --bridge-mode all \\
    --jax-platform gpu \\
    --sim-preflight-timeout-s 600 \\
    --closed-loop-timeout-s 1800 \\
    --output-dir "outputs/analysis/cuda_manual/${{CANDIDATE}}_gate_x0"
  cp "outputs/analysis/cuda_manual/${{CANDIDATE}}_gate_x0/CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md" \\
    "outputs/analysis/cuda_manual/${{CANDIDATE}}_candidate_gate_x0.md"
  cp "outputs/analysis/cuda_manual/${{CANDIDATE}}_gate_x0/closed_loop_actuator_bridge_eval.json" \\
    "outputs/analysis/cuda_manual/${{CANDIDATE}}_candidate_gate_x0.json"

  echo "=== Candidate closed-loop sim gate: x=0.08 ==="
  "$PYTHON_BIN" tools/eval_policy_with_actuator_bridge.py \\
    --mode closed-loop-sim \\
    --eval-role candidate \\
    --policy "$LATEST_ONNX" \\
    --fit-json outputs/analysis/actuator_response_fit.json \\
    --playground-path /content/Open_Duck_Playground \\
    --env-python "$PYTHON_BIN" \\
    --command-x 0.08 \\
    --duration 15 \\
    --bridge-mode all \\
    --jax-platform gpu \\
    --sim-preflight-timeout-s 600 \\
    --closed-loop-timeout-s 1800 \\
    --output-dir "outputs/analysis/cuda_manual/${{CANDIDATE}}_gate_x008"
  cp "outputs/analysis/cuda_manual/${{CANDIDATE}}_gate_x008/CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md" \\
    "outputs/analysis/cuda_manual/${{CANDIDATE}}_candidate_gate_x008.md"
  cp "outputs/analysis/cuda_manual/${{CANDIDATE}}_gate_x008/closed_loop_actuator_bridge_eval.json" \\
    "outputs/analysis/cuda_manual/${{CANDIDATE}}_candidate_gate_x008.json"

  TRAINING_MANIFEST="$RUN_DIR/smoke_manifest.final.json"
  if [ ! -f "$TRAINING_MANIFEST" ]; then
    TRAINING_MANIFEST="$RUN_DIR/smoke_manifest.start.json"
  fi

  "$PYTHON_BIN" tools/package_candidate_policy.py "$LATEST_ONNX" \\
    --candidate-name "$CANDIDATE" \\
    --training-manifest "$TRAINING_MANIFEST" \\
    --contract-audit outputs/analysis/cuda_manual/POLICY_SIM_CONTRACT_AUDIT_CUDA.md \\
    --candidate-gate-x0 "outputs/analysis/cuda_manual/${{CANDIDATE}}_candidate_gate_x0.md" \\
    --candidate-gate-x008 "outputs/analysis/cuda_manual/${{CANDIDATE}}_candidate_gate_x008.md" \\
    --output-md "outputs/analysis/cuda_manual/${{CANDIDATE}}_policy_package.md" \\
    --output-json "outputs/analysis/cuda_manual/${{CANDIDATE}}_policy_metadata.json" || true

  echo "=== Candidate small outputs ==="
  find outputs/analysis/cuda_manual -maxdepth 1 -type f -name "${{CANDIDATE}}_*" -print | sort || true
else
  echo "RUN_CANDIDATE=0, so candidate training was skipped."
  echo "After smoke passes, rerun this cell with --run-candidate generated or set RUN_CANDIDATE=1 near the top."
fi

echo "=== Small output files ==="
find outputs/analysis/cuda_manual -maxdepth 1 -type f -printf '%p\\n' | sort

echo "=== Final safety note ==="
echo "This cell does not approve robot testing. Package and sim gates must be reviewed before any suspended validation."
"""
    return textwrap.dedent(cell).strip() + "\n"


def write_notebook(path: Path, cell: str) -> None:
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": cell.splitlines(keepends=True),
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
            "open_duck": {
                "purpose": "offline CUDA/Colab actuator-bridge candidate workflow",
                "robot_tests": "not approved",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    path.write_text(json.dumps(notebook, indent=2) + "\n")


def write_handoff_dir(path: Path, cell: str, run_candidate: bool) -> None:
    path.mkdir(parents=True, exist_ok=True)
    stem = "open_duck_cuda_candidate" if run_candidate else "open_duck_cuda_smoke"
    cell_path = path / f"{stem}_cell.txt"
    notebook_path = path / f"{stem}.ipynb"
    manifest_path = path / "CUDA_COLAB_HANDOFF.md"

    cell_path.write_text(cell)
    write_notebook(notebook_path, cell)

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    mode = "candidate" if run_candidate else "smoke"
    manifest_path.write_text(
        textwrap.dedent(
            f"""\
            # CUDA / Colab Handoff

            generated_at: `{generated_at}`
            mode: `{mode}`

            ## Files

            - notebook: `{notebook_path.name}`
            - raw cell text: `{cell_path.name}`

            ## Run

            Upload/open `{notebook_path.name}` in a trusted, manually
            authenticated CUDA/Colab session and run its single code cell.
            If either repo is private, set `GITHUB_TOKEN` or `GH_TOKEN` in the
            Colab environment before running the `%%bash` cell. The cell does
            not use an interactive hidden token prompt.

            The cell is offline-only for the robot project:

            - no robot SSH
            - no robot deploy
            - no robot tests
            - no policy overwrite on the robot

            ## Expected Bundle Lines

            At the end of the cell, copy these printed values:

            ```text
            CUDA_ARTIFACT_BUNDLE /content/open_duck_cuda_artifacts_<timestamp>.tar.gz
            CUDA_ARTIFACT_BUNDLE_SHA256 <hash>
            CUDA_ARTIFACT_BUNDLE_SHA256_FILE /content/open_duck_cuda_artifacts_<timestamp>.tar.gz.sha256
            CUDA_ARTIFACT_DOWNLOAD_TRIGGERED /content/open_duck_cuda_artifacts_<timestamp>.tar.gz
            CUDA_ARTIFACT_SHA256_DOWNLOAD_TRIGGERED /content/open_duck_cuda_artifacts_<timestamp>.tar.gz.sha256
            ```

            If browser download is skipped or fails, download the printed
            `CUDA_ARTIFACT_BUNDLE` and `CUDA_ARTIFACT_BUNDLE_SHA256_FILE`
            paths manually.

            ## Import Locally

            After downloading the bundle to this machine:

            ```bash
            cd /home/lsd/robots/open-duck-mini-rdkx5
            python3 tools/ingest_latest_cuda_artifact.py
            ```

            Start review from the generated:

            ```text
            outputs/analysis/cuda_imports/<timestamp>_<bundle>/CUDA_ARTIFACT_IMPORT_SUMMARY.md
            ```

            ## Safety

            This handoff does not approve robot testing. Robot-side validation
            remains blocked until a candidate passes reviewed sim gates and Rob
            explicitly approves a specific suspended validation run.
            """
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print a copy-paste CUDA/Colab cell for Open Duck actuator bridge work."
    )
    parser.add_argument("--rdk-repo", default=DEFAULT_RDK_REPO)
    parser.add_argument("--playground-repo", default=DEFAULT_PLAYGROUND_REPO)
    parser.add_argument("--rdk-branch", default=DEFAULT_RDK_BRANCH)
    parser.add_argument("--playground-branch", default=DEFAULT_PLAYGROUND_BRANCH)
    parser.add_argument("--run-candidate", action="store_true")
    parser.add_argument("--smoke-num-timesteps", type=int, default=64)
    parser.add_argument("--smoke-ppo-num-envs", type=int, default=8)
    parser.add_argument("--smoke-ppo-batch-size", type=int, default=8)
    parser.add_argument("--smoke-episode-length", type=int, default=50)
    parser.add_argument("--candidate-num-timesteps", type=int, default=200_000)
    parser.add_argument("--candidate-ppo-num-envs", type=int, default=512)
    parser.add_argument("--candidate-ppo-num-evals", type=int, default=5)
    parser.add_argument("--candidate-episode-length", type=int, default=500)
    parser.add_argument("--candidate-unroll-length", type=int, default=10)
    parser.add_argument("--candidate-ppo-batch-size", type=int, default=512)
    parser.add_argument("--candidate-ppo-num-minibatches", type=int, default=16)
    parser.add_argument("--candidate-ppo-num-updates-per-batch", type=int, default=4)
    parser.add_argument(
        "--candidate-restore-checkpoint-path",
        default="",
        help=(
            "Optional checkpoint path visible inside the Colab runtime for "
            "offline fine-tuning."
        ),
    )
    parser.add_argument("--candidate-target-rate-scale", type=float, default=-0.001)
    parser.add_argument("--candidate-actuator-tracking-scale", type=float, default=0.0)
    parser.add_argument("--candidate-tracking-lin-vel-scale", type=float, default=12.0)
    parser.add_argument("--candidate-tracking-ang-vel-scale", type=float, default=0.0)
    parser.add_argument("--candidate-tracking-sigma", type=float, default=0.0025)
    parser.add_argument("--candidate-forward-progress-scale", type=float, default=2.0)
    parser.add_argument("--candidate-forward-progress-deadband", type=float, default=0.02)
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
            "bootstrap run. Sim gates still evaluate fitted/stress bridge modes."
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
    parser.add_argument("--candidate-timeout-s", type=int, default=7200)
    parser.add_argument(
        "--no-auto-download",
        action="store_true",
        help=(
            "Do not include the best-effort google.colab.files.download call "
            "after building the artifact bundle."
        ),
    )
    parser.add_argument("--output", help="Write the cell to this file instead of stdout.")
    parser.add_argument(
        "--notebook-output",
        help=(
            "Write a one-code-cell .ipynb containing the generated CUDA/Colab "
            "cell. This is useful when uploading a notebook is easier than "
            "copying a large cell into Colab."
        ),
    )
    parser.add_argument(
        "--handoff-dir",
        help=(
            "Write an uploadable notebook, raw cell text, and "
            "CUDA_COLAB_HANDOFF.md into this directory."
        ),
    )
    args = parser.parse_args()

    cell = build_cell(args)
    if args.output:
        Path(args.output).write_text(cell)
    if args.notebook_output:
        write_notebook(Path(args.notebook_output), cell)
    if args.handoff_dir:
        write_handoff_dir(Path(args.handoff_dir), cell, args.run_candidate)
    if not args.output and not args.notebook_output and not args.handoff_dir:
        print(cell, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
