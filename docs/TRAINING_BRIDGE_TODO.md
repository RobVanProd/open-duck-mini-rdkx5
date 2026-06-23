# Training Bridge TODO

Last updated: 2026-06-23

Purpose: convert the measured Open Duck Mini actuator evidence into small,
reviewable sim/training changes. Do not retrain blindly and do not change
robot runtime behavior as part of these items unless a later PR explicitly
requests a reviewed runtime experiment.

## Training Environment Constraint

Future training runs should use the local `7900 XTX` / ROCm-capable setup.
Before starting training:

- verify the AMD/ROCm environment is active
- verify the MuJoCo render fix for this GPU
- run a short MuJoCo smoke test before launching long training
- keep driver packages, local envs, render screenshots, and cache files out of
  git

Local references observed on this workstation:

```text
../envs/open-duck-playground
../envs/rocm-baseline
../verify_scratch/render_mujoco_egl.py
../amdgpu-install_7.2.1.70201-1_all.deb
```

Use `../envs/open-duck-playground/bin/python` for Open Duck Playground eval and
future training. `../envs/rocm-baseline` sees the ROCm device, but currently
lacks project-specific packages such as `mujoco_playground`, `ml_collections`,
and `onnxruntime`.

Cross-backend correctness result:

```text
Google Colab NVIDIA L4: PASS_CLOSED_LOOP_REPRODUCTION
local RX 7900 XTX ROCm: HOLD_PLAYGROUND_GPU_STEP / ROCM_ERROR_ILLEGAL_ADDRESS
```

This means the actuator-bridge eval path is valid on CUDA and the local ROCm
failure should not block the next design step. The local `7900 XTX` remains the
preferred target for eventual training, but if ROCm/MJX remains unstable, use a
reviewed CUDA backend for correctness/training experiments while keeping the
same policy/sim contract and actuator model.

CUDA fallback/runbook:

```text
docs/CUDA_BACKEND_TRAINING_RUNBOOK.md
```

## P0: Inspect Current Training Contract

### Fit Real Actuator Response From Telemetry

- Use `tools/fit_actuator_response_model.py` on suspended `x=0.08` telemetry.
- Save the small markdown/JSON summary under `outputs/analysis/`.
- Extract per-joint:
  - delay ticks
  - first-order tau
  - effective velocity limit
  - model RMSE
  - p95 model error
  - amplitude ratio
  - asymmetry notes

### Extract Current Actuator Delay Model

- Find where action delay is implemented in the training environment.
- Confirm the current randomization range, believed to be `0-3` env steps.
- Document whether delay is applied to actions, targets, observations, or all
  of them.
- Add notes to `docs/ACTUATOR_SIM_BRIDGE_SPEC.md` if the implementation differs
  from the audit.

### Compare Train-Time And Runtime Target-Rate Behavior

- Trace training action scaling and target generation.
- Confirm whether training uses the same `action_scale = 0.25`.
- Confirm whether sim enforces the same `max_motor_velocity = 5.24 rad/s`.
- Report target velocity p50/p95/p99/max in sim rollouts.

### Add Evaluation For Existing Policy

- Run the current `BEST_WALK_ONNX_2` equivalent in sim with actuator logging.
- Compute target velocity and simulated tracking lag with the same metrics as
  `tools/analyze_policy_target_velocity.py`.
- Compare sim p95 target velocity and tracking error against real suspended
  `x=0.08`.

### Check Local Training Environment

- Run `../envs/open-duck-playground/bin/python tools/check_training_env.py`.
- Confirm the intended `7900 XTX` / ROCm environment is active.
- Confirm JAX sees a GPU/ROCm backend.
- Confirm MuJoCo imports and can load a small model.
- Run the optional offscreen render check before any render-dependent eval:

```bash
../envs/open-duck-playground/bin/python tools/check_training_env.py --render-check
```

Do not start training from an interpreter that reports `HOLD_ENV_NOT_READY`.

### Reconcile Policy / Sim Contract

- Run `tools/audit_policy_sim_contract.py`.
- Confirm `BEST_WALK_ONNX_2` contract:
  - `obs[1,101]`
  - `continuous_actions[1,14]`
- Confirm local Playground `Joystick(flat_terrain)` contract under
  `../envs/open-duck-playground/bin/python`:
  - state observation length `101`
  - action size `14`
  - actuator order matches runtime / policy
  - `JAX backend = gpu`, `device = rocm:0`
- Current status: `PASS_POLICY_SIM_CONTRACT`.

### Sim Actuator Bridge Eval Harness

- Run `tools/eval_policy_with_actuator_bridge.py` in preflight mode.
- Run telemetry replay mode against existing suspended `x=0.08` evidence.
- Current status:
  - `PASS_TELEMETRY_REPLAY_REPRODUCTION`
  - `PASS_POLICY_SIM_CONTRACT`
  - `PASS_CLOSED_LOOP_REPRODUCTION` on Colab NVIDIA L4 / CUDA
  - `HOLD_SIM_RUNTIME_ERROR` on local `7900 XTX` ROCm
- The closed-loop eval now has a target-stage bridge insertion point before
  `mjx_env.step(...)`, but the local ROCm/JAX/MJX worker currently fails with
  `ROCM_ERROR_ILLEGAL_ADDRESS`.
- ROCm/MJX isolation narrowed this to `HOLD_PLAYGROUND_GPU_STEP`: basic JAX
  GPU, JAX jit/scan, minimal MJX GPU, Playground contract construction, and
  Playground reset pass; Open Duck Playground one-step on GPU is the smallest
  failing operation.
- Follow-up execution-mode checks show that a JIT-wrapped Playground step and a
  `jax.lax.scan` Playground step both fail with `ROCM_ERROR_ILLEGAL_ADDRESS`.
- Debug nan/inf flags fail during MJX convex collision on both GPU and CPU
  because the collision path uses `-inf` sentinels internally; do not treat that
  debug failure alone as proof of a corrupted robot model state.
- Triton softmax and ROCm data-dir XLA flags suggested for testing are not
  accepted by the local JAX/XLA build. Strict IEEE ROCm compiler flags still hit
  `ROCM_ERROR_ILLEGAL_ADDRESS`.
- Reset-state finite checks show `qpos`, `qvel`, `qacc`, `ctrl`, and
  `qfrc_constraint` are finite after reset. Post-reset sanitation does not fix
  the GPU scan-step failure, while the CPU sanitized scan passes.
- MJCF contact audit found implicit `solref` / `solimp` values on foot/floor
  contact geoms. Treat explicit contact-parameter experiments as a separate
  offline sim-model PR, not as a training or robot-runtime change.
- CPU can run short correctness paths, including closed-loop vanilla short
  matrix, but CPU bridge/multi-step eval is slow under the current timeout.
- A post-reset one-step isolation rerun still reports
  `HOLD_PLAYGROUND_GPU_STEP`: GPU contract/reset/finite-state checks pass, but
  Playground one-step vanilla times out and JIT/scan variants fail with
  returncode `-6`. CPU one-step, JIT, scan, bridge, and closed-loop reduced
  checks pass.
- Next implementation task: implement the training-time actuator wrapper using
  the verified `101` observation / `14` action contract. Keep local ROCm/MJX
  debugging as a backend workstream, not as a blocker for the actuator bridge
  design.

## P1: Add Actuator Model Controls

### Candidate Search Status: Escape Safe Standstill

Current offline candidate gates show two local optima:

```text
aggressive policy:
  moves
  violates posture/tracking/fall gates

actuator-aware policy:
  stable at x=0.0
  remains near standstill at x=0.08
```

`tools/analyze_policy_command_sensitivity.py` now checks whether an ONNX policy
changes action under synthetic `command_x` changes. The June 23 report shows the
latest safe candidates are command-sensitive at the static ONNX level, so the
next training work should not assume command blindness. The likely missing
piece is a locomotion bootstrap/curriculum that produces gait structure before
the full actuator bridge and smoothness pressure make standing the easiest
solution.

Recommended next training work:

- add a staged curriculum runner that can continue from checkpoints across
  phases in one remote job
- phase 1: positive straight-ahead commands, no or weak bridge, strong
  forward-progress requirement
- phase 2: mild bridge and moderate target/action penalties
- phase 3: fitted bridge with the existing candidate gates
- keep `zero_command_probability` low or zero during movement bootstrap
- keep robot validation blocked until both `x=0.0` and `x=0.08` sim gates pass

Supporting evidence:

- `outputs/analysis/CANDIDATE_RECIPE_SEARCH_SUMMARY.md`
- `outputs/analysis/POLICY_COMMAND_SENSITIVITY.md`

June 23 staged-curriculum result:

- Colab L4 three-phase run completed and produced a final ONNX.
- The final policy passed the offline `x=0.0` candidate sim gate.
- The same policy failed `x=0.08` with
  `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`.
- `x=0.08` fitted-bridge track ratio was `0.0277` against the `0.25`
  threshold, with mean local forward velocity about `0.0022 m/s`.
- Interpretation: the staged recipe improved infrastructure and x0 stability,
  but still lands in the safe standstill optimum. It is not a robot candidate.

June 23 follow-up:

- Added a default-off `forward_shortfall` cost to the Playground reward stack.
- Updated the staged curriculum to enable `forward_shortfall` explicitly:
  - phase 1: scale `-2.0`, required ratio `0.4`
  - phase 2: scale `-3.0`, required ratio `0.45`
  - phase 3: scale `-4.0`, required ratio `0.5`
- A tiny CPU plumbing smoke passed and confirmed phase restore, bridge
  transition, and CLI propagation:
  `outputs/analysis/STAGED_CURRICULUM_SHORTFALL_SMOKE.md`
- This is not a policy result. The next result needed is a full CUDA/Colab
  staged run with the shortfall term, followed by the packaged `x=0.0` and
  `x=0.08` candidate gates.

June 23 A100 staged shortfall result:

- Colab A100 completed all three phases in about `1609 s` of training time.
- Final policy sha256:
  `5b7d67d2f3bc8f4fc27f7cda0f8cb5af651915deada70a68cf3031e6a8a148c6`.
- `x=0.0` gate: `HOLD_CANDIDATE_TRACKING`; max pitch tracking p95
  `0.0851 rad` versus the `0.0800 rad` threshold.
- `x=0.08` gate: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`; fitted-bridge mean
  local forward velocity about `0.0017 m/s`, command tracking ratio `0.0211`.
- Max sent target velocity p95 stayed low (`0.4080 rad/s` at `x=0.08`), and
  action saturation was `0%`, so the policy is actuator-safe but still does not
  walk.
- Summary: `outputs/analysis/STAGED_CURRICULUM_SHORTFALL_A100_SUMMARY.md`.
- Interpretation: increasing explicit shortfall pressure inside the current
  staged recipe is not enough. The next recipe needs a stronger locomotion
  bootstrap or motion prior, not robot validation.
- Reporting caveat: the A100 packaged candidate gates used the evaluator's
  default reward config, so their reward-term tables did not list
  `cost/forward_shortfall` even though the training manifests passed
  `--forward_shortfall_scale`. The gate decision is still valid because it is
  based on measured local forward velocity and command tracking ratio. Future
  gates now include a reward-config-independent forward-shortfall diagnostic.
- Reward landscape caveat:
  `outputs/analysis/FORWARD_REWARD_LANDSCAPE_SHORTFALL_CURRENT.md` shows that
  the current final phase still gives zero velocity about `42%` of the shaped
  target reward at `command_x=0.04` before alive/imitation terms. The next
  recipe should raise the bootstrap command floor and/or tighten early reward
  shaping instead of only increasing the same shortfall scale.

Next recipe now staged:

- `tools/plan_staged_curriculum_training.py --recipe movement_bootstrap_v3`
  is the current offline plan.
- `shortfall_v1` remains available to reproduce the June 23 A100 run.
- `movement_bootstrap_v2` remains available to reproduce the failed A100
  movement-bootstrap run.
- `movement_bootstrap_v2` raised the command floor, tightened
  `tracking_sigma`, reduces alive dominance, and keeps a stronger
  imitation/motion prior before reintroducing the fitted actuator bridge.
- Planning artifacts:
  - `outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN.md`
  - `outputs/analysis/FORWARD_REWARD_LANDSCAPE_MOVEMENT_BOOTSTRAP_V2.md`
- A100 result:
  - `outputs/analysis/MOVEMENT_BOOTSTRAP_V2_A100_SUMMARY.md`
  - `x=0.0`: `HOLD_CANDIDATE_TRACKING`, max pitch tracking p95
    `0.1388 rad` vs `0.0800 rad`
  - `x=0.08`: `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`, fitted-bridge mean local
    forward velocity `0.0023 m/s`, tracking ratio `0.0286`
  - Decision: not a robot candidate.

Do not repeat `movement_bootstrap_v2` unchanged. `movement_bootstrap_v3` adds
default-off command-window cumulative progress and shortfall terms to the
Playground training env, then uses those terms in a new three-phase staged
recipe. This requires the sibling Playground branch:

```text
RobVanProd/Open_Duck_Playground codex/forward-progress-reward @ 4c99d40
```

If using Colab CLI again, run v3 explicitly:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow staged-curriculum \
  --staged-recipe movement_bootstrap_v3 \
  --session <colab-session> \
  --run \
  --timeout-s 14400
```

Robot validation remains blocked until the resulting candidate passes both
offline gates.

### Configurable Target Delay Wrapper

- Add per-episode random delay:
  - baseline: `3-8` ticks
  - stress range: `2-10` ticks
- Support per-joint jitter.
- Log sampled delay values.

### First-Order Actuator Lag Wrapper

- Implement:

```text
y[t] = y[t-1] + alpha * (target[t] - y[t-1])
alpha = 1 - exp(-dt / tau)
```

- Baseline tau range: `0.06-0.14 s`.
- Randomize tau per episode and optionally per joint.
- Log sampled tau and alpha values.

### Velocity Limit Randomizer

- Train with effective max velocity lower than the current optimistic runtime
  limit:

```text
2.5-4.7 rad/s
```

- Allow knees and ankles to sample lower limits than hips.
- Log clipping percentage per joint.

### Current Policy Lagged-Sim Replay

- Run the current `BEST_WALK_ONNX_2` behavior through the lagged actuator
  wrapper in sim.
- Check whether it degrades in sim under measured delay/lag/velocity limits in
  the same way it degraded on the real suspended Duck.
- Treat this as the key validation that the sim bridge captures the gap.
- Required sequence:
  - run `../envs/open-duck-playground/bin/python tools/check_training_env.py`
  - run `tools/audit_policy_sim_contract.py`
  - run `tools/isolate_rocm_mjx_failure.py`
  - run `tools/eval_policy_with_actuator_bridge.py` in closed-loop mode
  - use the CUDA L4 `PASS_CLOSED_LOOP_REPRODUCTION` result as the current
    correctness evidence if local ROCm remains blocked
  - compare fitted-bridge metrics to real suspended `x=0.08`
  - proceed to JAX/MJX training wrapper only if sim reproduction is plausible

### Acceleration / Jerk Limit

- Add optional target acceleration and jerk clipping.
- Keep it configurable so experiments can isolate velocity limit vs lag vs
  jerk effects.

## P2: Reward And Curriculum

### Current Candidate Lesson

June 22, 2026 CUDA/Colab candidate gates found a consistent failure mode:

- 50k actuator-bridge candidate: `x=0.0` passed, `x=0.08` held for low forward
  progress.
- 300k strengthened candidate: actuator-safe and stable, but `x=0.08`
  fitted/stress mean forward velocity stayed approximately zero.
- archived `verify_scratch/odm_phase_b` sweep: five selected compatible ONNX
  checkpoints all held at `x=0.08` for low forward progress.

Small summary:

```text
outputs/analysis/PHASE_B_CHECKPOINT_SWEEP_SUMMARY.md
outputs/analysis/FORWARD_REWARD_LANDSCAPE.md
```

Interpretation: the current actuator bridge and smoothness penalties can
produce policies that are easy for the real actuators to track, but the reward
landscape still allows near-standing behavior to score well enough under a
nonzero forward command. Do not spend more GPU time on the same recipe.

Current reward-shape calculation:

```bash
python3 tools/analyze_forward_reward_landscape.py \
  --output-md outputs/analysis/FORWARD_REWARD_LANDSCAPE.md \
  --output-json outputs/analysis/forward_reward_landscape.json
```

With `tracking_sigma=0.01`, `tracking_lin_vel_scale=12`, and `x=0.08`, zero
forward velocity keeps `52.7%` of the raw velocity-tracking reward. That is too
permissive for the next candidate recipe.

Next training PR should make the nonzero-command locomotion objective stricter
before launching another candidate:

- inspect the `tracking_lin_vel` reward formula and command tracking sigma
- verify whether near-zero velocity at `x=0.08` still receives a large reward
- tighten forward-velocity reward or add an explicit minimum-progress term for
  nonzero commands
- review command sampling so training cannot spend most useful updates near
  standing
- use the default-off `zero_command_probability` and
  `command_resample_steps` runner overrides for candidate-only experiments if
  zero-command curriculum still pulls the learned behavior toward standing
- keep the actuator bridge active, but reduce smoothness pressure if it turns
  standing into the easiest optimum
- keep `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` as a hard offline block for robot
  validation
- review the closed-loop eval `reward_terms` table/JSON for each candidate so
  total reward cannot hide a weak forward-tracking term behind `alive` or other
  stabilizing rewards
- next candidate recipe should use the default-off Playground
  `forward_progress` reward term plus a stricter velocity-tracking shape:
  `tracking_sigma=0.0025`, `forward_progress_scale=2.0`,
  `forward_progress_deadband=0.02`, `tracking_lin_vel_scale=12.0`,
  `tracking_ang_vel_scale=0.0`,
  `alive_scale=0.5`, `imitation_scale=0.25`, and reduced smoothness pressure
  such as `target_rate_scale=-0.001`, `action_rate_scale=-0.1`, and
  `action_magnitude_scale=-0.05`

### Action-Magnitude Penalty

The June 22 CUDA candidates showed saturated sample actions after the first
training checkpoint. `action_rate` alone is insufficient because a constant
saturated action can have low rate cost. Add and use a default-off
`action_magnitude` cost for candidate recipes before launching another GPU run.

### Action-Rate Penalty

- Penalize large action deltas.
- Report action delta p95/p99/max during evaluation.
- Compare against the current suspended `x=0.08` target waveform.

### Target-Velocity Penalty

- Penalize target velocity directly after action scaling.
- Track per-joint target velocity distribution in training logs.

### Tracking-Friendly Smoothness Term

- Reward policies whose commanded targets remain trackable under the sampled
  actuator model.
- Avoid rewarding artificially frozen gaits; pair with forward progress and
  stability metrics.
- Treat near-zero mean forward velocity under nonzero `x` commands as a
  candidate hold, even when target velocity and tracking metrics look good.

### Command Curriculum

Train/evaluate in stages:

```text
x = 0.00 -> 0.04 -> 0.08 -> higher
```

Do not export a robot candidate unless `x=0.08` passes sim-side actuator
robustness gates and forward command tracking gates.

## P3: Evaluation And Export

### Target Velocity Evaluation Script

- Add a sim-side equivalent of `tools/analyze_policy_target_velocity.py`.
- Report target velocity, action deltas, rate-limit activation, and simulated
  actuator tracking error per joint.
- Include pitch-chain summary by default.
- Include explicit target velocity p95/p99/max gates.
- Include simulated tracking p95/p99/max gates.
- Include base forward progress, mean forward velocity, and command tracking
  ratio for nonzero command evaluations.

### Short Training Experiment

- Only start after the sim actuator bridge eval reaches a reviewed
  `PASS_SIM_REPRODUCTION` or equivalent.
- First run a short ROCm smoke training job on the `7900 XTX` setup.
- If ROCm/MJX remains blocked, use the CUDA-backed correctness result for
  design decisions and run only small CPU smoke jobs locally.
- The local ROCm host-loop eval mode
  (`--mjx-step-loop-mode python` or `python_block_each`) is only for tiny
  correctness probes. It passed 10 closed-loop ticks but took about 105 seconds,
  so it is not a training-throughput path.
- Use `tools/run_actuator_bridge_training_smoke.py` to print and optionally
  execute the tiny smoke command. This records the exact command and output
  manifest under `/tmp` and does not create a deployable policy.
- Train with the actuator model enabled.
- Compare against a baseline with the current actuator assumptions.
- Save:
  - config
  - random seed
  - evaluation summaries
  - policy hash
  - target velocity metrics

### Next Candidate Recipe

`movement_bootstrap_v3` completed all three A100 phases but failed the
fitted-bridge `x=0.0` candidate gate with
`HOLD_CANDIDATE_FALL_OR_TERMINATION`. The next candidate should not simply push
harder on forward progress. It should separate stability and motion:

- Stage A: fitted-bridge `x=0.0` stability recovery.
- Stage B: introduce low positive commands only after Stage A passes.
- Stage C: add command-window progress while preserving fitted-bridge stability.
- Keep the no-robot rule until both `x=0.0` and `x=0.08` candidate gates pass.

Current v3 evidence:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V3_A100_SUMMARY.md
```

### Candidate ONNX Export

- Export only after sim-side gates pass.
- Store policy metadata and hash.
- Do not overwrite `BEST_WALK_ONNX_2.onnx`.
- Follow `docs/CANDIDATE_POLICY_VALIDATION_GATES.md` before requesting any
  robot-side suspended validation.

## P4: Robot Validation

### Suspended-Only Validation

Run only after review:

1. suspended `x=0.0`
2. suspended `x=0.08`

Required pass gates:

- pitch-chain p95 tracking error preferably `<0.05 rad`
- pitch-chain p95 tracking error acceptable `<0.08 rad`
- no sustained post-startup pitch tracking error above `0.10 rad`
- no action saturation bursts
- no write errors
- CRC read errors only warning unless correlated with control damage

### Grounded Replay

Only after suspended dynamic tracking passes.

Required evidence:

- telemetry JSONL
- terminal log
- side-view video
- final 3-5 seconds before failure if it fails

## Non-Goals For This TODO

- No physical gain tuning.
- No offset/remap changes.
- No phase timing changes.
- No action-scale changes.
- No TPU/friction claims until suspended dynamic tracking is acceptable.
