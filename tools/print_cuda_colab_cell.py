#!/usr/bin/env python3
"""Print a single CUDA/Colab cell for actuator-bridge training checks."""

from __future__ import annotations

import argparse
from pathlib import Path
import textwrap


DEFAULT_RDK_REPO = "https://github.com/RobVanProd/open-duck-mini-rdkx5.git"
DEFAULT_PLAYGROUND_REPO = "https://github.com/RobVanProd/Open_Duck_Playground.git"
DEFAULT_RDK_BRANCH = "main"
DEFAULT_PLAYGROUND_BRANCH = "main"


def bash_bool(value: bool) -> str:
    return "1" if value else "0"


def build_cell(args: argparse.Namespace) -> str:
    candidate_flag = bash_bool(args.run_candidate)
    auto_download_flag = bash_bool(not args.no_auto_download)
    smoke_steps = args.smoke_num_timesteps
    candidate_steps = args.candidate_num_timesteps
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
export CUDA_AUTO_DOWNLOAD={auto_download_flag}
export ARTIFACT_ROOT="/content/open_duck_cuda_artifacts"
export BUNDLE="/content/open_duck_cuda_artifacts_$(date -u +%Y%m%dT%H%M%SZ).tar.gz"

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
    echo "python_executable=$(command -v python || echo UNKNOWN)"
    python - <<'PY' 2>/dev/null || true
import sys
print("python_version=" + sys.version.replace("\\n", " "))
try:
    import jax
    print("jax_version=" + getattr(jax, "__version__", "UNKNOWN"))
    try:
        print("jax_backend=" + str(jax.default_backend()))
        print("jax_devices=" + ",".join(str(device) for device in jax.devices()))
    except Exception as exc:
        print("jax_device_error=" + type(exc).__name__ + ":" + str(exc))
except Exception as exc:
    print("jax_import_error=" + type(exc).__name__ + ":" + str(exc))
try:
    import mujoco
    print("mujoco_version=" + getattr(mujoco, "__version__", "UNKNOWN"))
except Exception as exc:
    print("mujoco_import_error=" + type(exc).__name__ + ":" + str(exc))
PY
    if command -v nvidia-smi >/dev/null 2>&1; then
      nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -n 1 | sed 's/^/gpu_name=/'
    else
      echo "gpu_name=UNKNOWN"
    fi
  }} >> "$ARTIFACT_ROOT/CUDA_CELL_EXIT_STATUS.txt"

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
    python - <<PY
import hashlib
from pathlib import Path
bundle = Path("$BUNDLE")
print("CUDA_ARTIFACT_BUNDLE", bundle)
print("CUDA_ARTIFACT_BUNDLE_SIZE_BYTES", bundle.stat().st_size)
print("CUDA_ARTIFACT_BUNDLE_SHA256", hashlib.sha256(bundle.read_bytes()).hexdigest())
PY
    if [ "${{CUDA_AUTO_DOWNLOAD:-1}}" = "1" ]; then
      python - <<PY
from pathlib import Path

bundle = Path("$BUNDLE")
try:
    from google.colab import files
except Exception as exc:
    print("CUDA_ARTIFACT_DOWNLOAD_SKIPPED", type(exc).__name__, exc)
else:
    try:
        files.download(str(bundle))
        print("CUDA_ARTIFACT_DOWNLOAD_TRIGGERED", bundle)
    except Exception as exc:
        print("CUDA_ARTIFACT_DOWNLOAD_FAILED", type(exc).__name__, exc)
PY
    fi
  else
    echo "CUDA_ARTIFACT_BUNDLE_FAILED $BUNDLE"
  fi
}}

trap 'rc=$?; bundle_cuda_artifacts "$rc"; exit "$rc"' EXIT

echo "=== GPU ==="
nvidia-smi || true

echo "=== Python/JAX before setup ==="
python - <<'PY'
try:
    import jax
    print("jax", jax.__version__)
    print("backend", jax.default_backend())
    print("devices", jax.devices())
except Exception as exc:
    print("jax_pre_setup_error", type(exc).__name__, exc)
PY

echo "=== Clone / update repos ==="
if [ ! -d /content/open-duck-mini-rdkx5 ]; then
  git clone "$RDK_REPO" /content/open-duck-mini-rdkx5
fi
if [ ! -d /content/Open_Duck_Playground ]; then
  git clone "$PLAYGROUND_REPO" /content/Open_Duck_Playground
fi

cd /content/open-duck-mini-rdkx5
git fetch origin
git checkout "$RDK_BRANCH"
git pull --ff-only

cd /content/Open_Duck_Playground
git fetch origin
git checkout "$PLAYGROUND_BRANCH"
git pull --ff-only

echo "=== Install CUDA eval/training deps ==="
python -m pip install -U pip
python -m pip install -U \\
  "jax[cuda12]" \\
  "playground==0.0.5" \\
  "mujoco>=3.2.7,<3.10" \\
  "mujoco-mjx>=3.2.7" \\
  onnxruntime \\
  ml-collections \\
  numpy \\
  matplotlib \\
  mediapy \\
  tensorflow \\
  tf2onnx
python -m pip install --no-deps -e /content/Open_Duck_Playground

echo "=== Verify key imports ==="
python - <<'PY'
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
python tools/check_training_env.py \\
  --playground-root /content/Open_Duck_Playground

echo "=== Policy/sim contract audit ==="
python tools/audit_policy_sim_contract.py \\
  --policy policy/BEST_WALK_ONNX_2.onnx \\
  --playground-path /content/Open_Duck_Playground \\
  --env-python "$(command -v python)" \\
  --instantiate-timeout-s 600 \\
  --output-md outputs/analysis/cuda_manual/POLICY_SIM_CONTRACT_AUDIT_CUDA.md \\
  --output-json outputs/analysis/cuda_manual/policy_sim_contract_audit_cuda.json

echo "=== Closed-loop baseline bridge reproduction ==="
python tools/eval_policy_with_actuator_bridge.py \\
  --mode closed-loop-sim \\
  --policy policy/BEST_WALK_ONNX_2.onnx \\
  --fit-json outputs/analysis/actuator_response_fit.json \\
  --playground-path /content/Open_Duck_Playground \\
  --env-python "$(command -v python)" \\
  --command-x 0.08 \\
  --duration 15 \\
  --bridge-mode all \\
  --jax-platform gpu \\
  --sim-preflight-timeout-s 600 \\
  --closed-loop-timeout-s 1800 \\
  --output-dir outputs/analysis/cuda_manual

echo "=== CUDA smoke training ==="
python tools/run_actuator_bridge_training_smoke.py \\
  --playground-path /content/Open_Duck_Playground \\
  --env-python "$(command -v python)" \\
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
  python tools/run_actuator_bridge_training_smoke.py \\
    --playground-path /content/Open_Duck_Playground \\
    --env-python "$(command -v python)" \\
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
    --target-rate-scale -0.01 \\
    --actuator-tracking-scale 0.0 \\
    --tracking-lin-vel-scale {args.candidate_tracking_lin_vel_scale} \\
    --alive-scale {args.candidate_alive_scale} \\
    --imitation-scale {args.candidate_imitation_scale} \\
    --lin-vel-x-min {args.candidate_lin_vel_x_min} \\
    --lin-vel-x-max {args.candidate_lin_vel_x_max} \\
    --lin-vel-y-min 0.0 \\
    --lin-vel-y-max 0.0 \\
    --ang-vel-yaw-min 0.0 \\
    --ang-vel-yaw-max 0.0 \\
    --head-range-factor 0.0 \\
    --timeout-s {args.candidate_timeout_s}

  RUN_DIR="$(find /content/open_duck_training_runs -maxdepth 1 -type d -name 'smoke_*_gpu' | sort | tail -n 1)"
  CANDIDATE="open_duck_mini_actuator_bridge_$(date -u +%Y%m%dT%H%M%SZ)"
  LATEST_ONNX="$(ls -1 "$RUN_DIR"/*.onnx | sort | tail -n 1)"

  python tools/summarize_training_run.py "$RUN_DIR" \\
    --output-md "outputs/analysis/cuda_manual/${{CANDIDATE}}_training_run_summary.md" \\
    --output-json "outputs/analysis/cuda_manual/${{CANDIDATE}}_training_run_summary.json"

  echo "=== Candidate closed-loop sim gate: x=0.0 ==="
  python tools/eval_policy_with_actuator_bridge.py \\
    --mode closed-loop-sim \\
    --eval-role candidate \\
    --policy "$LATEST_ONNX" \\
    --fit-json outputs/analysis/actuator_response_fit.json \\
    --playground-path /content/Open_Duck_Playground \\
    --env-python "$(command -v python)" \\
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
  python tools/eval_policy_with_actuator_bridge.py \\
    --mode closed-loop-sim \\
    --eval-role candidate \\
    --policy "$LATEST_ONNX" \\
    --fit-json outputs/analysis/actuator_response_fit.json \\
    --playground-path /content/Open_Duck_Playground \\
    --env-python "$(command -v python)" \\
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

  python tools/package_candidate_policy.py "$LATEST_ONNX" \\
    --candidate-name "$CANDIDATE" \\
    --training-manifest "$RUN_DIR/smoke_manifest.final.json" \\
    --contract-audit outputs/analysis/cuda_manual/POLICY_SIM_CONTRACT_AUDIT_CUDA.md \\
    --actuator-bridge-eval "outputs/analysis/cuda_manual/${{CANDIDATE}}_candidate_gate_x008.md" \\
    --output-md "outputs/analysis/cuda_manual/${{CANDIDATE}}_policy_package.md" \\
    --output-json "outputs/analysis/cuda_manual/${{CANDIDATE}}_policy_metadata.json" || true

  echo "=== Candidate small outputs ==="
  ls -1 outputs/analysis/cuda_manual/${{CANDIDATE}}_* || true
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
    parser.add_argument("--candidate-tracking-lin-vel-scale", type=float, default=6.0)
    parser.add_argument("--candidate-alive-scale", type=float, default=5.0)
    parser.add_argument("--candidate-imitation-scale", type=float, default=0.5)
    parser.add_argument("--candidate-lin-vel-x-min", type=float, default=0.04)
    parser.add_argument("--candidate-lin-vel-x-max", type=float, default=0.12)
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
    args = parser.parse_args()

    cell = build_cell(args)
    if args.output:
        Path(args.output).write_text(cell)
    else:
        print(cell, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
