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

### V7/V8/V9 Candidate Lessons

The latest movement-bootstrap sequence narrowed the remaining problem:

```text
V7: in-envelope forward motion, but lunge/fall at x=0.08
V8: lunge suppressed, but collapsed into safe standstill
V9: short-horizon speed looked balanced, but full-duration recheck still fell
```

The V9 full-duration recheck is preserved in:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V9_FULL_DURATION_RECHECK.md
```

Key result:

```text
seed 0: fall at 73 samples, track ratio 2.7707, body pitch p95 1.2604 rad
seed 1: fall at 32 samples, track ratio 0.2314, base height min 0.0672 m
target velocity p95 stayed under threshold in both runs
action saturation was 0%
```

The eight-seed V7/V9 baseline is now preserved in:

```text
outputs/analysis/V7_V9_MULTI_SEED_STABILITY_BASELINE.md
```

Baseline to beat:

```text
V7: 5/8 falls, 3/8 standstill completions, mean samples 311.75
V9: 5/8 falls, 3/8 standstill completions, mean samples 312.00
```

Observed failure surfaces:

```text
seeds 0 and 6: lunge / pitch-over
seed 5: reverse or negative local velocity failure
seeds 1 and 7: early base-height/contact collapse
seeds 2, 3, and 4: low-forward-progress standstill
```

Four-surface onset comparison:

```text
outputs/analysis/v9_four_surface_trace_recheck_x008_fitted/V9_FOUR_SURFACE_ONSET_COMPARISON.md
```

This shows the regimes branch within the first few ticks. V10 is not merely a
"reduce overshoot" run; it must produce the same forward-moving behavior family
across reset seeds.

Interpretation:

- the one-second checkpoint sweep is useful for triage but not sufficient,
- V9 is not a stable robot candidate,
- the remaining failure is not target-velocity budget or saturation,
- the next recipe must stabilize the `60-100` sample fall window without
  erasing forward motion,
- V10 should be graded by multi-seed distribution shift: fewer falls, later
  falls, fewer standstill completions, and useful forward tracking across more
  seeds.

Immediate tooling work:

- keep `--seed` available in `tools/eval_policy_with_actuator_bridge.py`,
- add or use a multi-seed wrapper for candidate gates,
- require candidate promotion to include full-duration `x=0.0` and `x=0.08`
  gates across more than one seed,
- record seed values in every gate summary.

Next recipe direction:

- start from the best moving checkpoint, not from a final standstill policy,
- add an explicit teacher-action / trust-region term to preserve early gait
  structure,
- penalize forward-speed overshoot, pitch growth, pitch-rate growth, and
  base-height collapse during the first `60-100` samples,
- include contact/support timing or stance-support terms because seed 1 and
  seed 7 fail by base-height/contact collapse rather than pure speed overshoot,
- keep the fitted actuator bridge and velocity envelope active,
- reject both failure modes: above-command lunge and near-zero standstill.

V10 plan and exit rule:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V10_PLAN.md
```

If V10 still lands near the V7/V9 distribution (`5/8` falls, `3/8` standstill
completions, mean lifetime around `312` samples, same four surfaces), stop
iterating this phase-1/V7/V9 anchor lineage. Switch to a structurally different
bootstrap rather than launching V11 with another small scalar adjustment.

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

The command-feasibility curve should be checked before spending another large
training run:

```bash
python3 tools/analyze_command_feasibility_curve.py \
  --policy policy/BEST_WALK_ONNX_2.onnx \
  --commands 0,0.02,0.04,0.06,0.08,0.10,0.12 \
  --duration 5 \
  --bridge-mode fitted \
  --jax-platform cpu \
  --run
```

The curve should identify where pitch-chain p95 target velocity crosses the
robust fitted actuator envelope (`~2.25-3.75 rad/s`) and whether `x=0.08` is
inside or above that envelope.

Current BEST_WALK result:

```text
outputs/analysis/best_walk_command_feasibility_curve_cpu/COMMAND_FEASIBILITY_CURVE.md
```

`x=0.08` is the first swept command above the fitted actuator envelope. Commands
through `x=0.06` stay below the envelope but do not produce meaningful forward
progress. The next training objective should target stable low-command motion
below the envelope before trying to recover `x=0.08`.

The next planned recipe is `movement_bootstrap_v5` in
`tools/plan_staged_curriculum_training.py`. It replaces the v4 `x=0.0`-first
stage with low-command movement in the measured feasible range:

```text
phase 1: x=0.04-0.06, mild bridge, Huber-shaped smoothness costs
phase 2: x=0.04-0.06, robust fitted velocity envelope
phase 3: x=0.04-0.08, expand only after low-command motion exists
```

The Huber controls are opt-in. With all deltas left at `0.0`, the Playground
reward costs remain the existing squared penalties. V5 enables deltas for
action-rate, target-rate, actuator-tracking, and shortfall terms so a few large
residuals do not dominate the reward gradient while still discouraging sharp
actuator-hostile commands.

After v5 or any later candidate completes, run its command feasibility curve and
apply [CANDIDATE_FEASIBILITY_STOP_RULE.md](CANDIDATE_FEASIBILITY_STOP_RULE.md).
Do not keep adding curriculum variants indefinitely. If three
feasibility-curve-targeted recipes only move above the measured actuator
envelope, treat the forward-gait target as actuator-envelope limited rather
than continuing to escalate training recipes.

V5 result:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V5_A100_SUMMARY.md
```

The run completed, but it did not find an in-envelope forward gait. Nonzero
commands remained below the target-velocity envelope but produced near-zero
forward velocity. Zero and tiny command cases fell with above-envelope target
spikes. This candidate is not deployable and counts as feasibility-targeted
attempt `1 / 3`.

The phase-checkpoint audit matters:

```text
phase 1 x=0.08: below envelope, mean local vx 0.1892 m/s, falls after 80 samples
phase 2 x=0.08: above envelope, mean local vx 0.2628 m/s, falls after 61 samples
final x=0.08: below envelope, mean local vx 0.0031 m/s, stable standstill
```

So the next recipe should not simply increase progress scales. It should try to
preserve the phase-1 in-envelope motion and add stability around it, or use
phase-1 as the checkpoint for a smaller stabilizing transition.

The phase-1 checkpoint has been preserved:

```text
policy/candidates/movement_bootstrap_v5_phase1_in_envelope_unstable_20260623/candidate.onnx
```

The traced failure is summarized in:

```text
docs/PHASE1_IN_ENVELOPE_MOTION_LEAD.md
outputs/analysis/PHASE1_X008_FAILURE_TRACE.md
```

Next staged recipe:

```text
movement_bootstrap_v6
```

V6 constraints:

```text
- keep fitted velocity envelope active in every phase: 2.5-3.75 rad/s
- train only in x=0.06-0.08 rather than expanding the command window
- add orientation/base-height costs gradually
- lower PPO learning rate and clipping in consolidation phases
- do not count stable standstill as success
```

Important limitation:

V6 does not implement a true teacher-policy action anchor against the preserved
phase-1 policy. It approximates continuity through checkpoint continuation and
smaller PPO updates. If V6 again loses the moving gait, the next task should be
to implement an action-level behavior-cloning/trust-region mechanism using the
phase-1 policy as teacher, rather than adding v7 reward terms.

V6 result:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V6_A100_SUMMARY.md
```

The A100 run completed all three phases but is not deployable:

```text
final x=0.0:  HOLD_CANDIDATE_FALL_OR_TERMINATION, 78 samples
final x=0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS, stable standstill
phase 1 x=0.08: stable standstill, mean local vx 0.0009 m/s
phase 2 x=0.08: stable standstill, mean local vx 0.0010 m/s
```

The stricter fitted-envelope phase 1 did not recover the v5 phase-1 motion
lead. This makes the next task more specific:

```text
1. Preserve staged training checkpoint directories in Colab artifacts.
2. Reproduce or recover the moving v5 phase-1 checkpoint with its trainable
   checkpoint state, not only ONNX export.
3. Add an action-level teacher/trust-region continuity mechanism around that
   checkpoint before adding more stability pressure.
```

The Colab wrapper now supports this recovery path:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-a100-v5-phase1-recovery \
  --workflow staged-curriculum \
  --staged-recipe movement_bootstrap_v5 \
  --staged-stop-after-phase 1 \
  --artifact-checkpoint-mode latest \
  --run
```

That command should produce the v5 phase-1 ONNX plus the latest matching
trainable checkpoint directory in the artifact bundle. Use it before any new
continuity/stabilization experiment that needs to resume from the moving
phase-1 behavior.

This recovery has now been completed and preserved:

```text
policy/candidates/movement_bootstrap_v5_phase1_trainable_recovery_20260623/
```

The recovered checkpoint is not deployable, but it is the correct trainable
anchor for a continuity/trust-region stabilization run:

```text
x=0.08 fitted bridge: 52 samples, mean local vx 0.2989 m/s, max pitch p95 target velocity 1.7912 rad/s
```

Next checkpoint-anchored recipe:

```text
movement_bootstrap_v7
```

Run it with the recovered checkpoint as the initial restore point:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-a100-v7-anchor \
  --workflow staged-curriculum \
  --staged-recipe movement_bootstrap_v7 \
  --staged-initial-restore-checkpoint /content/open-duck-mini-rdkx5/policy/candidates/movement_bootstrap_v5_phase1_trainable_recovery_20260623/checkpoint_2026_06_23_205634_368640 \
  --artifact-checkpoint-mode latest \
  --run
```

This is still not a full teacher-action behavior-cloning loss. It is a
checkpoint-anchored trust-region-style continuation experiment: small PPO
updates, low clip, low learning rate, and stability pressure added around the
recovered moving policy. If v7 also destroys motion, implement an actual
teacher-action regularizer rather than adding more reward terms.

V7 result:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V7_A100_SUMMARY.md
policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/
```

The run completed, but it is still not deployable:

```text
x=0.0:  HOLD_CANDIDATE_TRACKING, duration complete, max pitch tracking p95 0.0860 rad
x=0.08: HOLD_CANDIDATE_FALL_OR_TERMINATION, fitted bridge fall after 60 samples
```

The useful signal is that v7 preserved in-envelope forward motion:

```text
x=0.08 fitted mean local vx: 0.2640 m/s
x=0.08 fitted max pitch p95 target velocity: 2.2663 rad/s
action saturation: 0%
```

Next offline target:

```text
stabilize the x=0.08 velocity-overshoot/pitch-over failure under fitted bridge
```

The compact trace analysis is preserved in:

```text
outputs/analysis/V7_X008_ONSET_ANALYSIS.md
```

The onset sequence shows forward velocity exceeding the command at tick `3` /
`0.06s`, while body pitch does not cross `0.25 rad` until tick `15` /
`0.30s`. That makes the next recipe a velocity-overshoot and pitch/pitch-rate
stabilization problem first, with contact-timing terms added only after the
overshoot is controlled.

Do not request robot validation for v6 or v7.

### Movement Bootstrap V8

V8 targets the specific failure shown by the v7 onset trace:

```text
forward velocity overshoots the x=0.08 command before the pitch collapse
```

Planned recipe:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V8_PLAN.md
```

It starts from the v7 anchored checkpoint, keeps the fitted actuator bridge
active, and adds opt-in costs for:

```text
forward_overshoot
forward_pitch
forward_pitch_rate
```

V8 should be judged by whether it reduces `track_ratio`, body-pitch growth, and
fall/termination at `x=0.08` without returning to standstill. It should not
relax the fitted target-velocity envelope to buy motion.

V8 result:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V8_A100_SUMMARY.md
policy/candidates/movement_bootstrap_v8_overshoot_stabilized_standstill_20260623/
```

The run completed, but it is still not deployable:

```text
x=0.0:  HOLD_CANDIDATE_TRACKING, duration complete, max pitch tracking p95 0.0863 rad
x=0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS, duration complete, fitted mean local vx 0.0015 m/s
```

The useful signal is that V8 removed the v7 lunge/fall under `x=0.08`, with
body pitch and base height inside the candidate limits and `0%` action
saturation. The failure moved from "overdriven lunge" to "stable near
standstill." Next recipe work should keep the fitted bridge and velocity
envelope active while rebalancing progress and overshoot:

```text
1. anneal or reduce forward_overshoot / forward_pitch / forward_pitch_rate
2. increase command-window progress or shortfall pressure after stabilization
3. stage x commands from 0.04-0.06 before expanding to 0.08
4. preserve V8's no-lunge behavior but require measurable nonzero vx
```

Do not request robot validation for v8.

### Movement Bootstrap V9

V9 is planned here:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V9_PLAN.md
```

It starts from the V7 anchored checkpoint again instead of the V8 standstill.
The recipe keeps the fitted actuator bridge and `2.5-3.75 rad/s` velocity
envelope active, but reduces V8's overshoot/pitch damping and increases
command-window progress pressure.

V9 should be judged by whether it can land between the two recent failure
shapes:

```text
V7: moves in-envelope, but lunges/falls
V8: does not lunge/fall, but returns to standstill
V9 target: measurable x=0.08 progress, no lunge, no envelope relaxation
```

Robot validation remains blocked unless both candidate gates pass.

V9 result:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V9_A100_SUMMARY.md
policy/candidates/movement_bootstrap_v9_progress_balanced_standstill_20260623/
```

The run completed, but it is still not deployable:

```text
x=0.0:  HOLD_CANDIDATE_TRACKING, duration complete, max pitch tracking p95 0.0932 rad
x=0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS, duration complete, fitted mean local vx 0.0017 m/s
```

V9 did not land between V7 and V8. It behaved like V8: stable, low target
velocity, and nearly stationary. This is evidence that another small
overshoot/progress weight tweak is unlikely to be the next best move.

Next offline work should prioritize:

```text
1. checkpoint sweep/selection across V7/V8/V9 phase checkpoints
2. explicit teacher-action or trust-region regularization from a moving policy
3. separate stabilization from motion preservation instead of blending them only through reward weights
```

Use the checkpoint-sweep helper for the first item:

```bash
python3 tools/sweep_candidate_checkpoints.py \
  --policies policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/candidate.onnx \
             policy/candidates/movement_bootstrap_v8_overshoot_stabilized_standstill_20260623/candidate.onnx \
             policy/candidates/movement_bootstrap_v9_progress_balanced_standstill_20260623/candidate.onnx \
  --commands 0.08 \
  --duration 5 \
  --bridge-mode fitted \
  --output-dir outputs/analysis/candidate_checkpoint_sweep
```

Run it with `--run` only on a known-good CUDA session or CPU fallback. The local
ROCm/MJX path remains a backend issue.

Short CPU fallback sweep result:

```text
outputs/analysis/candidate_checkpoint_sweep_cpu_short/CANDIDATE_CHECKPOINT_SWEEP.md
```

At `x=0.08`, fitted bridge, one-second horizon:

```text
V7: vx 0.1469 m/s, track ratio 1.8356, pitch vel p95 1.9357 rad/s, tracking p95 0.2449 rad
V8: vx 0.0203 m/s, track ratio 0.2539, pitch vel p95 2.1929 rad/s, tracking p95 0.2391 rad
V9: vx 0.0730 m/s, track ratio 0.9129, pitch vel p95 2.1496 rad/s, tracking p95 0.2369 rad
```

This is not a candidate pass. It is a checkpoint-selection signal: V7 still
has the strongest motion, V8 is nearly standstill, and V9 may be the more
balanced moving anchor to inspect next. All three remain tracking holds over
the short horizon, so the next recipe should still use teacher/trust-region
continuity rather than another small reward-weight tweak.

Detailed short-horizon gate metrics sharpen that read:

```text
V7 body pitch p95: 0.723 rad, forward ratio: 1.836
V8 body pitch p95: 0.293 rad, forward ratio: 0.254
V9 body pitch p95: 0.448 rad, forward ratio: 0.913
```

V9 is not stable enough, but it is closer to commanded-speed behavior than V7
without falling all the way back to V8's standstill. Treat it as a candidate
teacher/anchor source for the next continuity experiment, not as a deployable
policy.

Do not request robot validation for v9.

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

## V10 Seed-Consistency Recipe

Status:

```text
V10 recipe implemented: movement_bootstrap_v10
dry-run plan: outputs/analysis/MOVEMENT_BOOTSTRAP_V10_TRAINING_PLAN.md
smoke status: PASS_SMOKE_RUN for new reward hooks on CPU
robot touched: no
```

V10 adds two default-off Playground reward terms:

```text
forward_wrong_direction
forward_contact_support
Playground dependency: RobVanProd/Open_Duck_Playground
                       codex/forward-progress-reward @ f7b817d
```

Use them only for recipes that explicitly need the V7/V9 failure-surface
pressure. Existing recipes remain behavior-compatible unless these scales are
nonzero.

Next execution step:

```bash
python3 tools/plan_staged_curriculum_training.py \
  --recipe movement_bootstrap_v10 \
  --platform gpu \
  --initial-restore-checkpoint \
    policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/checkpoint_2026_06_23_213846_184320 \
  --output-root /tmp/open_duck_movement_bootstrap_v10 \
  --run
```

After training, run the same seed-sweep gate used for V7/V9:

```bash
python3 tools/run_candidate_seed_sweep.py \
  --policies path/to/v10_candidate.onnx \
  --seeds 0,1,2,3,4,5,6,7 \
  --command-x 0.08 \
  --duration 15 \
  --bridge-mode fitted \
  --output-dir outputs/analysis/movement_bootstrap_v10_seed_sweep_x008_fitted
```

Promotion condition:

```text
Material distribution shift versus V7/V9:
- fewer than 5/8 falls, or
- fewer than 3/8 standstill completions, or
- mean lifetime materially above ~312 samples with useful forward tracking
```

Exit condition:

```text
If V10 is statistically similar to V7/V9, stop iterating on this anchor lineage.
```

### V10 Result

V10 was trained on A100 and evaluated with the same eight-seed `x=0.08`
fitted-bridge gate used for the V7/V9 baseline:

```text
summary: outputs/analysis/MOVEMENT_BOOTSTRAP_V10_SEED_SWEEP_SUMMARY.md
candidate: 2026_06_24_024457_153600
onnx_sha256: 54f5619c0a50f8064aa4b11e02b5a66125f0a27526ad83416e8d3e049e92254e
```

Result:

```text
V10: 3/8 falls, 5/8 duration-complete low-progress holds
mean samples: 482.75
mean track ratio: -0.4610
```

V10 is not a useful candidate. It improved lifetime mostly by freezing, and one
seed still failed by moving strongly backward. Do not request robot validation
for this policy.

Next training work should not continue simple V7/V9 anchor consolidation as the
main path. Switch to a structurally different bootstrap/objective that first
creates one coherent forward behavior across seeds, then adds stability margin.

## V11 Fresh Hard-Progress Bootstrap

V11 is prepared as the next structurally different experiment:

```text
recipe: movement_bootstrap_v11
plan: outputs/analysis/MOVEMENT_BOOTSTRAP_V11_TRAINING_PLAN.md
json: outputs/analysis/movement_bootstrap_v11_training_plan.json
initial restore checkpoint: none by default
```

Design intent:

```text
- do not continue the V7/V9/V10 anchor lineage
- keep fitted actuator limits active from phase 1
- train only positive x commands
- remove Huber smoothing from the forward shortfall and command-window
  shortfall floors
- strongly penalize reverse motion
- add stability only after forward motion is made expensive to abandon
```

Evaluation rule:

```text
Run the same eight-seed x=0.08 fitted-bridge seed sweep.
V11 is only useful if it produces more coherent forward tracking across seeds,
not merely longer standstill survival.
```

### V11 Result

V11 completed all three A100 phases and produced a valid `101 -> 14` ONNX, but
it is not a deployable candidate:

```text
summary: outputs/analysis/MOVEMENT_BOOTSTRAP_V11_A100_SUMMARY.md
candidate: movement_bootstrap_v11_hard_progress_a100_20260624
onnx_sha256: a3f30d64f21334a5263df15d0b8c11576a04c4fe280c2a082cecb4e2038a13c7
x=0.0 gate: PASS_CANDIDATE_SIM_GATE
x=0.08 gate: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
```

At `x=0.08`, the policy stayed upright for the full gate but only reached a
track ratio of about `0.011` with mean local velocity around `0.0009 m/s`.
Action saturation stayed at `0%` and target-velocity p95 stayed below
`0.275 rad/s`, so the hold is a freeze/no-motion failure rather than an
actuator-envelope or saturation failure.

Next work:

```text
1. Audit V11 reward-term magnitudes and PPO logs.
2. Identify why low-progress positive-command episodes remain viable.
3. Change the training mechanics so command-progress failure cannot be solved
   by standing still.
4. Add cheap per-phase freeze detection before spending full A100 phases.
5. Only after that, design another training run.
```

Do not request robot validation for V11.

### V11 Reward Mechanics Follow-Up

Initial audit:

```text
outputs/analysis/V11_REWARD_MECHANICS_AUDIT.md
outputs/analysis/V11_FORWARD_REWARD_LANDSCAPE.md
```

The scalar reward-landscape check indicates the intended V11 phase scales should
make zero velocity worse than target-speed motion. Treat V11 as a mechanics
failure before treating it as another coefficient-search failure.

Before V12:

```text
1. Use the default-off command-progress failure/truncation path after a warmup
   window.
2. Add eval support for replaying the same reward override config used during
   training.
3. Add per-phase freeze detection so the staged curriculum stops if a phase
   produces low progress at positive command.
4. Keep fitted actuator limits active.
5. Do not start another A100 recipe until those mechanics are explicit.
```
