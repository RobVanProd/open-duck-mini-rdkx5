# CUDA Backend Training Runbook

Last updated: 2026-06-23

## Purpose

Use this runbook when the local `7900 XTX` ROCm/MJX path is blocked but a CUDA
machine is available, such as Colab L4/A100 or another NVIDIA host.

Current backend split:

```text
CUDA L4 closed-loop eval: PASS_CLOSED_LOOP_REPRODUCTION
CUDA L4 training smoke: PASS_SMOKE_RUN with jax/jaxlib==0.7.2
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
  branch: main

Playground fork:
  https://github.com/RobVanProd/Open_Duck_Playground
  branch: main
```

For headless/private-repo runs, prefer the Colab CLI tarball workflow:

```bash
python3 tools/run_colab_cli_cuda_workflow.py --workflow eval
```

Pass `--run` only when an authenticated `colab` CLI session is active. This
path uploads local RDK and Playground worktree tarballs and does not need a
GitHub token inside the notebook.

## Staged Curriculum Candidate

Current candidate evidence is stuck between unsafe motion and safe standstill.
The next preferred CUDA candidate shape is the staged curriculum:

```text
phase 1: locomotion bootstrap, no actuator bridge
phase 2: mild actuator bridge transition
phase 3: fitted actuator bridge consolidation
```

The workflow trains all three phases in one Colab job, restoring each phase from
the previous phase checkpoint, then runs the existing `x=0.0` and `x=0.08`
candidate gates.

The current staged recipe includes an explicit default-off Playground
`forward_shortfall` cost when launched through
`tools/plan_staged_curriculum_training.py`. The local plumbing smoke passed in:

```text
outputs/analysis/STAGED_CURRICULUM_SHORTFALL_SMOKE.md
```

Expect roughly 45-70 minutes for a full L4 run: the previous three-phase Colab
training took about 39 minutes, plus setup, packaging, and candidate gates.

A June 23 Colab A100 run of the staged shortfall recipe completed the three
training phases in about `26.8 minutes` of training time, but the final policy
was not robot-ready:

```text
outputs/analysis/STAGED_CURRICULUM_SHORTFALL_A100_SUMMARY.md
```

Gate results:

- `x=0.0`: `HOLD_CANDIDATE_TRACKING`, max pitch tracking p95 `0.0851 rad`
  against the `0.0800 rad` threshold
- `x=0.08`: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`, fitted-bridge forward
  tracking ratio `0.0211` against the `0.25` threshold

Use A100 for faster iteration when available, but do not treat the current
staged shortfall recipe as solved. It still lands in the actuator-safe
standstill optimum.

Candidate gate markdown now includes a `Forward Shortfall Diagnostic` section
that is independent of the environment reward config. Use that section to
distinguish these two cases:

```text
training manifest includes --forward_shortfall_scale
candidate gate reward-term table omits cost/forward_shortfall because eval uses default reward scales
candidate gate still reports measured progress_ratio and shortfall_cost
```

The gate decision should continue to be driven by measured local forward
velocity and command tracking ratio, not by whether a diagnostic reward term is
present in the default eval reward table.

Before launching another large run, review the combined reward-shape report:

```text
outputs/analysis/FORWARD_REWARD_LANDSCAPE_SHORTFALL_CURRENT.md
```

The failed A100 final phase still allowed zero velocity to retain about `42%`
of the shaped target reward at the low end of the command range
(`command_x=0.04`). Prefer a recipe that bootstraps movement at a higher command
floor or adds a stronger motion prior before reintroducing the full fitted
actuator bridge.

The staged Colab workflow now defaults to:

```text
movement_bootstrap_v4
```

This keeps `shortfall_v1`, `movement_bootstrap_v2`, and
`movement_bootstrap_v3` available for reproduction. V4 follows the A100 v3
result, which completed training but failed the fitted-bridge `x=0.0` gate. The
next run therefore starts with fitted-bridge zero-command stability before
reintroducing low positive commands. The corresponding planning artifact is:

```text
outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN.md
```

The command-window reward hooks are in the sibling Playground branch:

```text
RobVanProd/Open_Duck_Playground codex/forward-progress-reward @ 4c99d40
```

Plan-only:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow staged-curriculum \
  --session open-duck-l4j \
  --staged-recipe movement_bootstrap_v4 \
  --staged-timesteps-scale 1.0 \
  --timeout-s 14400
```

Run on an authenticated Colab CLI session:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow staged-curriculum \
  --session open-duck-l4j \
  --run \
  --staged-recipe movement_bootstrap_v4 \
  --staged-timesteps-scale 1.0 \
  --staged-phase-timeout-s 10800 \
  --timeout-s 14400
```

For a fast plumbing-only remote smoke, reduce phase lengths:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow staged-curriculum \
  --session open-duck-l4j \
  --run \
  --staged-recipe movement_bootstrap_v4 \
  --staged-timesteps-scale 0.001 \
  --staged-phase-timeout-s 1200 \
  --timeout-s 7200
```

Robot validation remains blocked even if the Colab run completes. A candidate
must pass both packaged sim gates before any suspended robot validation.

The generated notebook cell can still clone repos. If a repo is private, set
`GITHUB_TOKEN` or `GH_TOKEN` in the Colab environment before running it; the
cell uses `GIT_ASKPASS` and does not write the token into git remotes. It does
not try an interactive token prompt inside `%%bash`, because Colab bash cells
can fail on `getpass`/TTY input.

## One-Cell CUDA Smoke

Prefer generating the cell from the checked-in helper so branch names,
dependency pins, and candidate defaults stay in one place:

```bash
python3 tools/print_cuda_colab_cell.py
```

To generate a cell that also runs the first candidate-training shape:

```bash
python3 tools/print_cuda_colab_cell.py --run-candidate
```

To generate an uploadable one-code-cell notebook instead of copying a long
cell through the clipboard:

```bash
python3 tools/print_cuda_colab_cell.py \
  --run-candidate \
  --notebook-output /tmp/open_duck_cuda_candidate.ipynb
```

To generate the notebook, raw cell text, and a local handoff checklist together:

```bash
python3 tools/print_cuda_colab_cell.py \
  --run-candidate \
  --handoff-dir /home/lsd/robots/cuda_colab_handoff
```

The generated candidate cell also runs candidate-mode closed-loop sim gates at
`x=0.0` and `x=0.08` after training. It packages the candidate against both
gate reports, so a zero-command fall or a nonzero-command hold such as
`HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` is carried into the package metadata.
At the end, it creates a single `/content/open_duck_cuda_artifacts_<timestamp>.tar.gz`
bundle plus a matching `.sha256` sidecar with small analysis files, candidate
ONNX exports, manifests, and logs. In Colab, the generated cell also makes a
best-effort browser download request for the bundle and sidecar; if it prints
`CUDA_ARTIFACT_DOWNLOAD_SKIPPED` or `CUDA_ARTIFACT_DOWNLOAD_FAILED`, download
the printed bundle and sidecar paths manually.

If the repo sync or setup step fails before training, the `EXIT` trap still
builds a small evidence bundle. Its `CUDA_CELL_EXIT_STATUS.txt` should show a
nonzero `exit_status`; import that bundle locally if the failure needs review.

The default generated candidate recipe uses the Playground runner's opt-in
training-recipe overrides to test the next hypothesis from the CPU pilots:
stable standing was over-rewarded relative to nonzero forward command tracking.
It therefore tightens `tracking_sigma`, adds an explicit default-off
`forward_progress` reward term for nonzero commands, disables yaw tracking for
the straight-ahead command slice, adds an opt-in action-magnitude penalty to
discourage saturated constant actions, reduces alive and imitation scales,
samples straight-ahead positive `x` commands, and freezes head-command
randomization for the first candidate attempt.

See:

```text
docs/CUDA_COLAB_SINGLE_CELL.md
```

Run this as one Colab cell or one shell block on a CUDA host:

```bash
set -euo pipefail
cd /content
export PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3}"

nvidia-smi || true
"$PYTHON_BIN" - <<'PY'
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
git checkout main
git pull --ff-only

cd /content/Open_Duck_Playground
git fetch origin
git checkout main
git pull --ff-only

"$PYTHON_BIN" -m pip install -U pip
"$PYTHON_BIN" -m pip install -U "jax[cuda12]==0.7.2" "jaxlib==0.7.2" "playground==0.0.5" \
  "mujoco>=3.2.7,<3.10" "mujoco-mjx>=3.2.7" onnxruntime \
  ml-collections numpy matplotlib mediapy tensorflow tf2onnx
"$PYTHON_BIN" -m pip install --no-deps -e /content/Open_Duck_Playground

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

"$PYTHON_BIN" tools/check_training_env.py \
  --playground-root /content/Open_Duck_Playground

"$PYTHON_BIN" tools/audit_policy_sim_contract.py \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --playground-path /content/Open_Duck_Playground \
  --env-python "$PYTHON_BIN" \
  --instantiate-timeout-s 600 \
  --output-md outputs/analysis/POLICY_SIM_CONTRACT_AUDIT_CUDA.md \
  --output-json outputs/analysis/policy_sim_contract_audit_cuda.json

"$PYTHON_BIN" tools/eval_policy_with_actuator_bridge.py \
  --mode closed-loop-sim \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --playground-path /content/Open_Duck_Playground \
  --env-python "$PYTHON_BIN" \
  --command-x 0.08 \
  --duration 15 \
  --bridge-mode all \
  --jax-platform gpu \
  --sim-preflight-timeout-s 600 \
  --closed-loop-timeout-s 1800 \
  --output-dir outputs/analysis/cuda_eval

"$PYTHON_BIN" tools/run_actuator_bridge_training_smoke.py \
  --playground-path /content/Open_Duck_Playground \
  --env-python "$PYTHON_BIN" \
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
export PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3}"
"$PYTHON_BIN" tools/run_actuator_bridge_training_smoke.py \
  --playground-path /content/Open_Duck_Playground \
  --env-python "$PYTHON_BIN" \
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
  --target-rate-scale -0.001 \
  --actuator-tracking-scale 0.0 \
  --tracking-lin-vel-scale 12.0 \
  --tracking-ang-vel-scale 0.0 \
  --tracking-sigma 0.0025 \
  --forward-progress-scale 2.0 \
  --forward-progress-deadband 0.02 \
  --action-rate-scale -0.1 \
  --action-magnitude-scale -0.05 \
  --stand-still-scale -0.2 \
  --alive-scale 0.5 \
  --imitation-scale 0.25 \
  --lin-vel-x-min 0.04 \
  --lin-vel-x-max 0.12 \
  --lin-vel-y-min 0.0 \
  --lin-vel-y-max 0.0 \
  --ang-vel-yaw-min 0.0 \
  --ang-vel-yaw-max 0.0 \
  --command-resample-steps 500 \
  --zero-command-probability 0.1 \
  --head-range-factor 0.0 \
  --timeout-s 7200
```

This is a first candidate-training shape, not a guaranteed final config.
Review reward, target velocity, action saturation, and simulated actuator
tracking before increasing runtime.

If a candidate still holds at `x=0.08` with low forward progress, the next
offline-only escalation is to disable the historical zero-command curriculum for
that candidate run:

```bash
  --zero-command-probability 0.0 \
  --command-resample-steps 600
```

Those flags are training-curriculum controls only. They must not be confused
with robot runtime changes.

After candidate training, run the offline candidate gates before any packaging
or robot discussion:

```bash
"$PYTHON_BIN" tools/eval_policy_with_actuator_bridge.py \
  --mode closed-loop-sim \
  --eval-role candidate \
  --policy "$LATEST_ONNX" \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --playground-path /content/Open_Duck_Playground \
  --env-python "$PYTHON_BIN" \
  --command-x 0.0 \
  --duration 15 \
  --bridge-mode all \
  --jax-platform gpu \
  --sim-preflight-timeout-s 600 \
  --output-dir outputs/analysis/<candidate>_gate_x0

"$PYTHON_BIN" tools/eval_policy_with_actuator_bridge.py \
  --mode closed-loop-sim \
  --eval-role candidate \
  --policy "$LATEST_ONNX" \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --playground-path /content/Open_Duck_Playground \
  --env-python "$PYTHON_BIN" \
  --command-x 0.08 \
  --duration 15 \
  --bridge-mode all \
  --jax-platform gpu \
  --sim-preflight-timeout-s 600 \
  --output-dir outputs/analysis/<candidate>_gate_x008
```

The generated single cell performs these two gates automatically when
`--run-candidate` is used.

If a Colab run finishes training but disconnects during gate evaluation, use the
CLI eval-only workflow instead of rerunning training:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow candidate-eval-only \
  --candidate-existing-policy path/to/candidate.onnx \
  --candidate-training-manifest path/to/smoke_manifest.final.json \
  --candidate-name open_duck_mini_actuator_bridge_<run> \
  --run
```

The eval-only workflow uploads the selected ONNX and optional manifest, reruns
the `x=0.0` and `x=0.08` closed-loop candidate gates, and packages the results.
It does not train and does not touch the robot.

The generated cell now bundles artifacts from an `EXIT` trap. If a CUDA smoke,
candidate training, gate, or packaging command fails, still download the
printed `/content/open_duck_cuda_artifacts_<timestamp>.tar.gz` bundle. It
contains `CUDA_CELL_EXIT_STATUS.txt` plus whatever small summaries, ONNX files,
manifests, stdout, and stderr existed before the failure. The exit-status file
also records the RDK and Playground commits, dirty-file counts, Python/JAX/MuJoCo
package metadata when available, and the visible GPU name when `nvidia-smi` is
available. The bundle also includes `pip_freeze.txt` and `nvidia_smi.txt` when
those commands are available.

## Summarize And Package

After a CUDA run, copy or use the output directory path and run:

```bash
RUN_DIR=/content/open_duck_training_runs/<run_dir>
CANDIDATE=open_duck_mini_actuator_bridge_<date>_<shortsha>
export PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3}"

cd /content/open-duck-mini-rdkx5

"$PYTHON_BIN" tools/summarize_training_run.py "$RUN_DIR" \
  --output-md outputs/analysis/${CANDIDATE}_training_run_summary.md \
  --output-json outputs/analysis/${CANDIDATE}_training_run_summary.json

LATEST_ONNX="$(ls -1 "$RUN_DIR"/*.onnx | sort | tail -n 1)"

"$PYTHON_BIN" tools/package_candidate_policy.py "$LATEST_ONNX" \
  --candidate-name "$CANDIDATE" \
  --training-manifest "$RUN_DIR/smoke_manifest.final.json" \
  --contract-audit outputs/analysis/POLICY_SIM_CONTRACT_AUDIT_CUDA.md \
  --candidate-gate-x0 outputs/analysis/<candidate>_candidate_gate_x0.md \
  --candidate-gate-x008 outputs/analysis/<candidate>_candidate_gate_x008.md \
  --output-md outputs/analysis/${CANDIDATE}_policy_package.md \
  --output-json outputs/analysis/${CANDIDATE}_policy_metadata.json
```

If target-velocity analysis exists, add:

```text
--target-velocity-summary outputs/analysis/${CANDIDATE}_target_velocity.md
```

## Files To Send Back

Prefer sending the generated `.tar.gz` bundle and importing it locally first:

```bash
python3 tools/ingest_latest_cuda_artifact.py
```

The ingest helper searches common download locations for the newest
`open_duck_cuda_artifacts_*.tar.gz`, verifies the neighboring `.sha256` sidecar
when present, and skips bundles already imported by SHA256. If the download is
elsewhere, pass `--bundle /path/to/open_duck_cuda_artifacts_<timestamp>.tar.gz`.
For manual imports, `tools/import_cuda_artifact_bundle.py` still accepts
`--expected-sha256-file` or `--expected-sha256`.

Open the generated `CUDA_ARTIFACT_IMPORT_SUMMARY.md` first. It reports a
review gate such as `READY_FOR_SIM_GATE_REVIEW`,
`READY_FOR_STAGED_GATE_REVIEW`, `INFO_SMOKE_ONLY`,
`INFO_STAGED_RUN_NO_PHASE_GATE`, or the specific `HOLD_*` reason from the
staged phase gate, candidate package, sim gates, or notebook exit status.
`HOLD_CUDA_CELL_FAILED` means the bundle is partial; inspect logs before using
any candidate result. This is still an offline review gate, not approval for
robot testing.

If the bundle cannot be downloaded, send small summaries first:

```text
outputs/analysis/POLICY_SIM_CONTRACT_AUDIT_CUDA.md
outputs/analysis/cuda_eval/CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md
outputs/analysis/<candidate>_training_run_summary.md
outputs/analysis/<candidate>_candidate_gate_x0.md
outputs/analysis/<candidate>_candidate_gate_x008.md
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
