# CUDA Backend Training Runbook

Last updated: 2026-06-22

## Purpose

Use this runbook when the local `7900 XTX` ROCm/MJX path is blocked but a CUDA
machine is available, such as Colab L4/A100 or another NVIDIA host.

Current backend split:

```text
CUDA L4 closed-loop eval: PASS_CLOSED_LOOP_REPRODUCTION
local RX 7900 XTX ROCm/MJX: HOLD_PLAYGROUND_GPU_STEP
CPU: usable for reduced-horizon correctness checks only
```

This runbook is still offline-only:

- no robot tests
- no SSH
- no deployment
- no overwrite of `BEST_WALK_ONNX_2.onnx`
- no candidate is robot-ready until sim gates and package checks pass

## Inputs

Repositories:

```text
RDK repo:
  https://github.com/RobVanProd/open-duck-mini-rdkx5
  branch: codex/training-actuator-wrapper-workflow

Playground fork:
  https://github.com/RobVanProd/Open_Duck_Playground
  branch: codex/training-actuator-bridge
```

If a repo is private, authenticate in the notebook/session using your normal
GitHub flow. Do not paste tokens into committed files.

## One-Cell CUDA Smoke

Run this as one Colab cell or one shell block on a CUDA host:

```bash
set -euo pipefail
cd /content

nvidia-smi || true
python - <<'PY'
import jax
print("jax", jax.__version__)
print("backend", jax.default_backend())
print("devices", jax.devices())
PY

if [ ! -d open-duck-mini-rdkx5 ]; then
  git clone https://github.com/RobVanProd/open-duck-mini-rdkx5.git
fi
if [ ! -d Open_Duck_Playground ]; then
  git clone https://github.com/RobVanProd/Open_Duck_Playground.git
fi

cd /content/open-duck-mini-rdkx5
git fetch origin
git checkout codex/training-actuator-wrapper-workflow
git pull --ff-only

cd /content/Open_Duck_Playground
git fetch origin
git checkout codex/training-actuator-bridge
git pull --ff-only

python -m pip install -U pip
python -m pip install -U "jax[cuda12]" mujoco mujoco-mjx onnxruntime \
  ml-collections numpy matplotlib mediapy
python -m pip install --no-deps -e /content/Open_Duck_Playground

cd /content/open-duck-mini-rdkx5

python tools/check_training_env.py \
  --playground-root /content/Open_Duck_Playground

python tools/audit_policy_sim_contract.py \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --playground-path /content/Open_Duck_Playground \
  --env-python "$(command -v python)" \
  --instantiate-timeout-s 600 \
  --output-md outputs/analysis/POLICY_SIM_CONTRACT_AUDIT_CUDA.md \
  --output-json outputs/analysis/policy_sim_contract_audit_cuda.json

python tools/eval_policy_with_actuator_bridge.py \
  --mode closed-loop-sim \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --playground-path /content/Open_Duck_Playground \
  --env-python "$(command -v python)" \
  --command-x 0.08 \
  --duration 15 \
  --bridge-mode all \
  --closed-loop-timeout-s 1800 \
  --output-dir outputs/analysis/cuda_eval

python tools/run_actuator_bridge_training_smoke.py \
  --playground-path /content/Open_Duck_Playground \
  --env-python "$(command -v python)" \
  --platform gpu \
  --run \
  --num-timesteps 64 \
  --ppo-num-envs 8 \
  --ppo-batch-size 8 \
  --ppo-episode-length 50 \
  --ppo-unroll-length 5 \
  --timeout-s 900
```

Expected smoke result:

```text
PASS_SMOKE_RUN
```

## First Candidate Training Shape

Only run candidate training after the smoke command passes and the Playground
PR is reviewed. Start modestly; do not jump straight to a long unattended run.

Example shape:

```bash
cd /content/open-duck-mini-rdkx5
python tools/run_actuator_bridge_training_smoke.py \
  --playground-path /content/Open_Duck_Playground \
  --env-python "$(command -v python)" \
  --platform gpu \
  --run \
  --output-root /content/open_duck_training_runs \
  --num-timesteps 200000 \
  --ppo-num-envs 512 \
  --ppo-num-evals 5 \
  --ppo-episode-length 500 \
  --ppo-unroll-length 10 \
  --ppo-batch-size 512 \
  --ppo-num-minibatches 16 \
  --ppo-num-updates-per-batch 4 \
  --target-rate-scale 0.01 \
  --actuator-tracking-scale 0.0 \
  --timeout-s 7200
```

This is a first candidate-training shape, not a guaranteed final config.
Review reward, target velocity, action saturation, and simulated actuator
tracking before increasing runtime.

## Summarize And Package

After a CUDA run, copy or use the output directory path and run:

```bash
RUN_DIR=/content/open_duck_training_runs/<run_dir>
CANDIDATE=open_duck_mini_actuator_bridge_<date>_<shortsha>

cd /content/open-duck-mini-rdkx5

python tools/summarize_training_run.py "$RUN_DIR" \
  --output-md outputs/analysis/${CANDIDATE}_training_run_summary.md \
  --output-json outputs/analysis/${CANDIDATE}_training_run_summary.json

LATEST_ONNX="$(ls -1 "$RUN_DIR"/*.onnx | sort | tail -n 1)"

python tools/package_candidate_policy.py "$LATEST_ONNX" \
  --candidate-name "$CANDIDATE" \
  --training-manifest "$RUN_DIR/smoke_manifest.final.json" \
  --contract-audit outputs/analysis/POLICY_SIM_CONTRACT_AUDIT_CUDA.md \
  --actuator-bridge-eval outputs/analysis/cuda_eval/CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md \
  --output-md outputs/analysis/${CANDIDATE}_policy_package.md \
  --output-json outputs/analysis/${CANDIDATE}_policy_metadata.json
```

If target-velocity analysis exists, add:

```text
--target-velocity-summary outputs/analysis/${CANDIDATE}_target_velocity.md
```

## Files To Send Back

Send small summaries first:

```text
outputs/analysis/POLICY_SIM_CONTRACT_AUDIT_CUDA.md
outputs/analysis/cuda_eval/CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md
outputs/analysis/<candidate>_training_run_summary.md
outputs/analysis/<candidate>_policy_package.md
outputs/analysis/<candidate>_policy_metadata.json
```

Do not send giant checkpoint directories unless explicitly requested.

## Robot Gate

This runbook does not approve robot testing. A candidate must pass the gates in:

```text
docs/CANDIDATE_POLICY_VALIDATION_GATES.md
```

Only after review should Rob be asked for suspended `x=0.0` validation.
