# Training Bridge TODO

Last updated: 2026-06-24

Purpose: convert the measured Open Duck Mini actuator evidence into small,
reviewable sim/training changes. Do not retrain blindly and do not change
robot runtime behavior as part of these items unless a later PR explicitly
requests a reviewed runtime experiment.

Current low-command target-source decision:

```text
docs/TARGET_SOURCE_DECISION.md
```

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

Cloud GPU smoke/debug notes:

```text
docs/CLOUD_GPU_TRAINING_DEBUG.md
```

Closed-loop weight-transfer teacher plan:

```text
docs/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_PLAN.md
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

### Build Closed-Loop Weight-Transfer Teacher Probe

Current target-source probes show that the open-loop primitive family is
exhausted for this question:

```text
roll/lift support-biased primitive:
  no seed-robust 100/150 tick target

stance-push primitive:
  no seed-robust 100/150 tick target

velocity-feedback stance-push primitive:
  no seed-robust 100/150 tick target
```

Next implementation should follow:

```text
docs/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_PLAN.md
```

Do not add another scalar term to `tools/search_low_command_target_primitives.py`
unless it is part of a state-feedback teacher design. The next useful probe
should couple support phase, body pitch/height, stance loading, swing
clearance, and forward displacement in closed loop.

Block PPO/BC/A100 runs until there is a compact offline result for:

```text
PASS_WEIGHT_TRANSFER_TEACHER_PROBE
```

or a specific teacher-probe hold such as `HOLD_SUPPORT_TRANSFER_FAILED`,
`HOLD_FORWARD_STILL_LOW`, `HOLD_PITCH_OR_HEIGHT_UNSTABLE`, or
`HOLD_ACTUATOR_ENVELOPE`.

First teacher-probe result:

```text
tool: tools/probe_closed_loop_weight_transfer_teacher.py
artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_PROBE.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

The first state-feedback teacher improved raw rollout forward velocity versus
the open-loop probes, but the scored windows still failed both seeds:

```text
top aggregate rollout mean vx: 0.0232 m/s
100-tick robust modes: 0
150-tick robust modes: 0
dominant failures: low_forward_velocity and high_lateral_velocity
```

Next teacher work should reduce lateral impulse while keeping contact
transitions: stronger local-vy damping, push gating when lateral velocity is
high, and body-y / CoM centering feedback.

Second teacher-probe result:

```text
artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V2_PROBE.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

V2 added body-y centering and lateral-speed push gating. It improved the top
raw rollout mean velocity to `0.0305 m/s`, but robust 100/150 tick scoring
still found zero passing modes. Objective-ranked candidates control lateral
velocity only by losing forward displacement. The next teacher design needs
forward step geometry or foot-placement/CoM planning, not another roll/push
feedback term.

Third teacher-probe result:

```text
artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V3_PROBE.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

V3 added swing-hip reach, stance retract, and pitch target terms. It improved
top raw rollout mean velocity to `0.0337 m/s`, but still produced zero robust
100/150 tick modes. The best scored windows retained support transitions and
low target velocities, but failed both forward velocity and lateral velocity.
The next branch should be a staged or optimized planner, not a larger random
grid over these same terms.

Staged planner probe:

```text
tool: tools/probe_staged_weight_transfer_planner.py
artifact: outputs/analysis/STAGED_WEIGHT_TRANSFER_PLANNER_PROBE.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

The staged planner used lateral/base-y/height/pitch gates before enabling
forward step targets. It met the lateral gate in the best windows, but forward
velocity fell to near zero (`0.0015 / 0.0034 m/s` over the best 100-tick
seed0/seed2 windows). This means balance gating alone is not enough. The next
target-source task should be a short-horizon optimizer or model-predictive
planner, not a wider random search.

Next target-source branch:

```text
doc: docs/WEIGHT_TRANSFER_OPTIMIZER_PLAN.md
```

Implement a short-horizon optimizer that searches compact target-sequence
parameters against the same seed-robust objective. This is the correct next
step because prior probes have bracketed the tradeoff but not solved it.

First optimizer slice:

```text
tool: tools/optimize_weight_transfer_target_sequence.py
artifact: outputs/analysis/WEIGHT_TRANSFER_OPTIMIZER.md
status: HOLD_OPTIMIZER_NO_ROBUST_TARGET
```

The wrapper works and produces scored traces, but the first small run stayed in
the conservative basin: lateral velocity near gate, target velocity low, and
forward velocity near zero. Do not train from these traces.

Gate-mode optimizer extension:

```text
artifact: outputs/analysis/WEIGHT_TRANSFER_OPTIMIZER_GATE_MODE.md
status: HOLD_OPTIMIZER_NO_ROBUST_TARGET
```

Sampling soft and ungated step phases did not restore forward displacement. The
next optimizer change should add an explicit terminal forward-displacement
objective or a richer target-sequence parameterization, not just more gate-mode
sampling.

Displacement-weighted scorer/optimizer result:

```text
artifact: outputs/analysis/WEIGHT_TRANSFER_OPTIMIZER_DISPLACEMENT.md
status: HOLD_OPTIMIZER_NO_ROBUST_TARGET
```

Every sampled candidate failed the new displacement gate. This confirms that
the current compact planner parameterization is not sufficient as a target
source. The next branch should change the target representation or move to a
closed-loop state-feedback teacher.

Forward-intent teacher result:

```text
tool flags:
  --min-forward-scales
  --feedforward-pushes
artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_FORWARD_INTENT.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

This branch restored local-frame forward displacement but failed lateral
velocity. The top scored 100-tick windows reached `0.0518 / 0.0420 m` local
forward displacement on seeds `0 / 2`, while `vy95` remained around
`0.19 m/s`. Do not train from these traces; they prove the tradeoff, not a
usable target source.

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

### V12 Mechanics-Test Plan

V12 is now planned but not trained:

```text
recipe: movement_bootstrap_v12
plan: outputs/analysis/MOVEMENT_BOOTSTRAP_V12_TRAINING_PLAN.md
json: outputs/analysis/movement_bootstrap_v12_training_plan.json
```

Intent:

```text
- keep the V11 fresh hard-progress bootstrap
- enable command-progress failure in every phase
- keep fitted actuator limits active
- run per-phase freeze checks so a frozen phase stops the staged run early
- do not request robot validation until x=0.0 and x=0.08 candidate gates pass
```

### V12 A100 Phase-1 Gate Result

V12 was launched on an A100 from PR #74 head `79c0e21` with the corrected
per-phase gate. Phase 1 completed and exported an ONNX, but the gate stopped the
staged run before phase 2:

```text
status: HOLD_PHASE_FREEZE_OR_LOW_PROGRESS
candidate_gate_status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
termination: duration_complete
forward_tracking_ratio: 0.04537
max_action_saturation_pct: 0.0
max_pitch_tracking_p95_rad: 0.07263
max_sent_target_velocity_p95_rad_s: 0.17286
```

Interpretation: V12 did not escape the stable low-motion basin. The policy stayed
upright and inside the actuator envelope, but it barely moved at `x=0.08`. The
corrected gate did its job by stopping the staged curriculum before later phases
consolidated the no-motion behavior. Robot validation remains blocked.

Summary artifact: `outputs/analysis/MOVEMENT_BOOTSTRAP_V12_A100_PHASE1_SUMMARY.md`.

### V13 Signed-Failure Mechanics Plan

The V12 result exposed a narrower mechanics failure: low-progress episodes were
terminated, but standing until termination still did not carry enough negative
consequence to defeat the no-motion basin. Source inspection showed that the
environment clipped scalar reward at zero by default, so a terminal low-progress
event could still be flattened instead of becoming an explicit signed penalty.

V13 is prepared as a dry-run plan:

```text
recipe: movement_bootstrap_v13
plan: outputs/analysis/MOVEMENT_BOOTSTRAP_V13_TRAINING_PLAN.md
json: outputs/analysis/movement_bootstrap_v13_training_plan.json
training_started: false
robot_touched: false
```

Intent:

```text
- keep the V12 fitted-bridge low-command curriculum
- keep command-progress failure enabled in every phase
- add signed command-progress failure penalties: -120, -140, -160
- lower reward_clip_min to -10.0 so failure can be negative
- keep the per-phase candidate gate so frozen phases stop early
- do not request robot validation until x=0.0 and x=0.08 gates pass
```

V13 remains an offline mechanics test. It should answer whether explicit
negative low-progress failure can make forward motion cheaper than standing
still inside the measured actuator envelope.

### V13 A100 Phase-1 Gate Result

V13 was launched on an A100 from PR #74 head `dff8d69`. Phase 1 completed and
exported an ONNX, but the per-phase gate stopped the staged run before phase 2:

```text
status: HOLD_PHASE_FREEZE_OR_LOW_PROGRESS
candidate_gate_status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
termination: duration_complete
forward_tracking_ratio: 0.01601
mean local vx: 0.0013 m/s
max_action_saturation_pct: 0.0
max_pitch_tracking_p95_rad: 0.07430
max_sent_target_velocity_p95_rad_s: 0.14604
max_abs_body_pitch_p95_rad: 0.05504
min_base_height_m: 0.15368
```

Training rewards were negative throughout phase 1, which confirms the signed
failure / negative reward path was active. The resulting policy still chose
near-standstill at `x=0.08`, so V13 does not solve the no-motion basin.

Next offline task: inspect whether the command-progress failure signal actually
appears frequently enough during training and whether alive/tracking/imitation
terms still make low-motion behavior locally preferable despite the signed
failure penalty.

Summary artifact: `outputs/analysis/MOVEMENT_BOOTSTRAP_V13_A100_PHASE1_SUMMARY.md`.

### V13 Training-Reward Replay

The closed-loop evaluator and staged-plan manifest were updated after V13
because the original candidate gate replayed default reward settings and did not
execute the command-progress failure path while manually inserting the actuator
bridge. The first replay also exposed that the staged-plan JSON omitted several
core phase fields, including `tracking_lin_vel_scale`, `alive_scale`, and
`target_rate_scale`, and it did not record the hardcoded
`tracking_ang_vel_scale=0.0` training flag. The planner now writes the full
phase dataclass payload plus the reward-relevant hardcoded command settings.

With the complete V13 phase-1 reward overrides applied, the same candidate now
terminates exactly at the configured command-progress failure boundary:

```text
status: HOLD_CANDIDATE_FALL_OR_TERMINATION
samples: 80
termination: fall_or_nan
forward_tracking_ratio: 0.04657
mean local vx: 0.0037 m/s
diagnostic/command_progress_failure max: 1.0
cost/command_progress_failure max: 120.0
reward_mean: -0.38404
reward_min: -2.76543
```

Interpretation: V13's failure mechanic is active and visible in
training-equivalent eval, and the full reward scale set is now replayed. The
remaining failure is a short-lived low-motion local optimum: the policy survives
until the low-progress boundary rather than learning forward motion.

Summary artifact: `outputs/analysis/V13_TRAINING_REWARD_REPLAY_SUMMARY.md`.

### V14 Motion-Discovery Ladder

Next planned offline recipe: `movement_bootstrap_v14`.

Why this is different from V13:

- V13 proved the signed command-progress failure path works.
- V13 still learned low motion until the 80-step failure boundary.
- Starting directly under the fitted actuator bridge appears too hard for fresh
  PPO discovery.
- V14 starts with a milder actuator bridge to discover low-command forward
  motion, then transfers to the fitted envelope only if phase gates preserve
  progress.

Planned phases:

```text
phase1_mild_bridge_motion_discovery:
  x = 0.04-0.06
  delay = 1-3 ticks
  velocity limit = 3.8-5.24 rad/s

phase2_fitted_bridge_motion_transfer:
  x = 0.04-0.06
  delay = 2-5 ticks
  velocity limit = 2.5-3.75 rad/s

phase3_expand_command_with_fitted_bridge:
  x = 0.04-0.08
  delay = 3-6 ticks
  velocity limit = 2.5-3.75 rad/s
```

Do not run robot validation. Do not launch a follow-on phase if the phase gate
freezes, falls, reverses, or fails the forward-progress gate.

Plan artifact: `outputs/analysis/MOVEMENT_BOOTSTRAP_V14_TRAINING_PLAN.md`.

### V14 A100 Phase-1 Partial

V14 phase 1 was launched on an A100 as a phase-1-only offline run. The remote
job reached step `102400`, exported an ONNX, then disappeared without writing
the workflow exit sentinel or final artifact bundle. The partial ONNX and
stdout/stderr were recovered manually.

Recovered checkpoint:

```text
outputs/analysis/movement_bootstrap_v14_a100_phase1_partial/2026_06_24_064318_102400.onnx
sha256: fe265e85d0d2e6f8b3d4c2f4b85550adcca6fd56232778be34c1a4634f273161
```

CPU gate on `x=0.08`, fitted bridge, V14 phase-1 reward overrides:

```text
status: HOLD_CANDIDATE_FALL_OR_TERMINATION
samples: 120
termination: fall_or_nan
mean local vx: 0.0014 m/s
forward_tracking_ratio: 0.0181
reward_mean: -0.1850
max_sent_target_velocity_p95_rad_s: 0.2466
diagnostic/command_progress_failure max: 1.0
```

Interpretation: this is not a complete V14 verdict, but the recovered partial
checkpoint is still low-motion and should not be used as a restore anchor. Before
another A100 run, either fix the Colab no-sentinel failure handling or make a
more structural discovery change.

Summary artifact:
`outputs/analysis/MOVEMENT_BOOTSTRAP_V14_A100_PHASE1_PARTIAL_SUMMARY.md`.

### V15 No-Bridge Gait-Discovery Plan

Next planned offline recipe: `movement_bootstrap_v15`.

V14's recovered step-102400 checkpoint was already low-motion, so repeating the
same mild-bridge discovery recipe is not the best next use of A100 time. V15
separates the search into an explicit gait-discovery phase and actuator-transfer
phases:

```text
phase1_no_bridge_high_entropy_gait_discovery:
  bridge = disabled
  x = 0.06-0.10
  alive = 0
  imitation = 0
  entropy = 0.02
  gate bridge = vanilla

phase2_mild_bridge_gait_transfer:
  bridge = mild
  x = 0.05-0.08
  velocity limit = 3.6-5.24 rad/s
  gate bridge = fitted

phase3_fitted_bridge_gait_consolidation:
  bridge = fitted
  x = 0.04-0.08
  velocity limit = 2.5-3.75 rad/s
  gate bridge = fitted
```

The staged planner now records a per-phase `phase_gate_bridge_mode`, so phase 1
can be evaluated as a vanilla motion-discovery gate without prematurely
rejecting a useful gait before actuator transfer. Later phases still gate under
the fitted bridge.

Robot validation remains blocked. A V15 policy only becomes interesting if it
first survives the phase gates and then passes the standard offline `x=0.0` and
`x=0.08` candidate gates.

Plan artifact: `outputs/analysis/MOVEMENT_BOOTSTRAP_V15_TRAINING_PLAN.md`.

### V15 A100 No-Sentinel Export Handoff

The first V15 phase-1 A100 launch did not complete. It reached `STEP: 0`,
saved/exported a step-0 ONNX, then the detached Colab process disappeared
without writing the workflow exit sentinel or final artifact bundle.

This should be treated as an export-handoff infrastructure hold, not a V15
policy result:

```text
status: HOLD_REMOTE_NO_SENTINEL_EXPORT_HANDOFF
step: 0 only
later checkpoints: none
usable candidate: no
```

Follow-up training hygiene:

- keep TensorFlow ONNX export CPU-only by default in `Open_Duck_Playground`
- pass `--export-min-step 1` from staged training so step-0 checkpoint/ONNX
  export is skipped
- preserve later checkpoint/ONNX exports for candidate packaging and gates

Summary artifact:
`outputs/analysis/MOVEMENT_BOOTSTRAP_V15_A100_NO_SENTINEL_SUMMARY.md`.

### V15B A100 Post-Step0 Hold

The fixed V15 relaunch used `--export-min-step 1` and proved the step-0 export
guard is active:

```text
STEP: 0 reward: -191.49404907226562 reward_std: 169.26931762695312
Skipping checkpoint/export at step 0; export_min_step=1
```

The process still disappeared after step 0 without a workflow exit sentinel,
artifact bundle, Python traceback, checkpoint, or ONNX.

Interpretation: the first failure was not solely step-0 export. The current
offline hold is the A100/JAX training path immediately after initial eval.

Next debugging step:

- run a smaller A100 V15 phase-1 smoke with reduced PPO envs/batch size
- only promote back to full phase if the smaller run reaches at least one
  nonzero PPO progress/export step
- keep the robot parked

Summary artifact:
`outputs/analysis/MOVEMENT_BOOTSTRAP_V15B_A100_NO_SENTINEL_SUMMARY.md`.

### V15C A100 Reduced PPO Hold

The next V15 check used a smaller A100 phase-1 smoke:

```text
timesteps_scale: 0.25
ppo_num_envs: 64
ppo_batch_size: 64
ppo_num_minibatches: 2
ppo_num_updates_per_batch: 2
export_min_step: 1
```

The Colab session again became idle without a workflow exit sentinel, artifact
bundle, final manifest, ONNX, or checkpoint. The captured log reached the runner
command but not a visible `STEP: 0` reward line.

Interpretation: the A100 hold is broader than the step-0 export handoff and
broader than the original larger PPO configuration. Before any more full A100
recipe launches, isolate the cloud training path with a tiny known-good PPO
smoke that must write a normal sentinel/final manifest.

Next debugging steps:

- run a minimal A100 runner smoke that is smaller than V15C and verifies normal
  sentinel/final-manifest behavior:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-a100-smoke \
  --workflow training-smoke \
  --run \
  --timeout-s 1800 \
  --smoke-num-timesteps 64 \
  --smoke-export-min-step 1
```

- use the hardened poller behavior for remote-idle/no-sentinel cases instead
  of waiting for the full timeout
- use a different backend for recipe iteration if the minimal A100 smoke still
  disappears
- keep the robot parked

Summary artifact:
`outputs/analysis/MOVEMENT_BOOTSTRAP_V15C_A100_REDUCED_NO_SENTINEL_SUMMARY.md`.

### Minimal A100 Training Smoke Hold

The `training-smoke` workflow was run on a fresh A100 session with the pinned
JAX stack and the smallest current PPO smoke:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-a100-smoke \
  --workflow training-smoke \
  --run \
  --timeout-s 1800 \
  --smoke-num-timesteps 64 \
  --smoke-export-min-step 1
```

The pinned stack initialized:

```text
jax 0.7.2
jaxlib 0.7.2
backend gpu [CudaDevice(id=0)]
has_device_put_replicated True
```

The remote session still disappeared while running the tiny PPO smoke and the
hardened poller recorded `HOLD_REMOTE_NO_SENTINEL`.

Interpretation: this is not a V15 recipe result. The A100 hold is now isolated
to the minimal GPU PPO training path or Colab runtime around it.

Next debugging options:

- run the same `training-smoke` on L4 or CPU to separate A100-specific failure
  from generic Colab/Brax runner failure
- if L4/CPU passes, keep recipe iteration off A100 until the A100 PPO smoke is
  fixed
- if all Colab backends fail, reproduce the tiny smoke locally and inspect
  stdout/stderr directly
- keep the robot parked

Summary artifact:
`outputs/analysis/A100_TRAINING_SMOKE_NO_SENTINEL_SUMMARY.md`.

### Minimal L4 Training Smoke Hold

The same `training-smoke` check was run on L4 and reproduced the no-sentinel
failure after the pinned stack initialized successfully.

Interpretation: the minimal smoke failure is not A100-specific. The current
debug target is the Colab remote execution/capture path or a generic GPU PPO
smoke failure.

Next debugging steps:

- add a foreground remote execution mode for tiny smokes so Colab console
  captures the driver exit status directly
- rerun `training-smoke` in foreground mode before launching any more staged
  recipes:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-l4-smoke-foreground \
  --workflow training-smoke \
  --run \
  --foreground-remote \
  --foreground-remote-timeout-s 1800 \
  --timeout-s 1800 \
  --smoke-num-timesteps 64 \
  --smoke-export-min-step 1
```

- keep the robot parked

Summary artifact:
`outputs/analysis/L4_TRAINING_SMOKE_NO_SENTINEL_SUMMARY.md`.

### L4 Foreground Training Smoke Hold

Foreground remote execution was tested on L4:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-l4-smoke-foreground \
  --workflow training-smoke \
  --run \
  --foreground-remote \
  --foreground-remote-timeout-s 1800 \
  --timeout-s 1800 \
  --smoke-num-timesteps 64 \
  --smoke-export-min-step 1
```

It still disappeared without a foreground exit sentinel after reaching the tiny
PPO smoke command.

Interpretation: the detached `setsid` wrapper is not the sole cause. The next
split is local CPU smoke versus Colab GPU smoke.

Next debugging steps:

- run the same tiny smoke locally on CPU
- if local CPU passes, use it to keep recipe/debug work moving while Colab GPU
  smoke observability is fixed separately
- if local CPU fails, inspect local stdout/stderr directly before any further
  cloud runs
- keep the robot parked

Summary artifact:
`outputs/analysis/L4_FOREGROUND_TRAINING_SMOKE_NO_SENTINEL_SUMMARY.md`.

### Local CPU Training Smoke Pass

The tiny smoke was rerun locally on CPU after fixing the launcher to set both
JAX platform environment variables:

```text
JAX_PLATFORM_NAME=cpu
JAX_PLATFORMS=cpu
```

Result:

```text
status: PASS_SMOKE_RUN
returncode: 0
elapsed_s: 54.36
STEP: 80 reward: 11.251152038574219 reward_std: 4.502880573272705
```

Interpretation: the runner is valid. The first local CPU failure was an
environment selection issue from JAX trying to initialize the installed ROCm
plugin. The next cloud check should rerun `training-smoke` after this
`JAX_PLATFORMS` fix is present in the uploaded repo.

Summary artifact:
`outputs/analysis/LOCAL_CPU_TRAINING_SMOKE_SUMMARY.md`.

### L4 Platform Mapping Hold

The first cloud rerun after the local CPU platform fix used:

```text
JAX_PLATFORM_NAME=gpu
JAX_PLATFORMS=gpu
```

That is invalid for CUDA JAX. The recovered stderr showed:

```text
Backend 'rocm' is not in the list of known backends: ['cpu', 'tpu', 'cuda'].
```

Fix now in the tools:

- `run_actuator_bridge_training_smoke.py --jax-platforms`
- CPU defaults to `JAX_PLATFORMS=cpu`
- Colab CUDA workflow passes `--jax-platforms cuda`
- staged curriculum passes `--jax-platforms` through to each phase
- remote artifact bundling recreates `OUT` after repo extraction

Next command:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-l4-smoke-cuda-platform \
  --workflow training-smoke \
  --run \
  --foreground-remote \
  --foreground-remote-timeout-s 1800 \
  --timeout-s 1800 \
  --smoke-num-timesteps 64 \
  --smoke-export-min-step 1
```

Summary artifact:
`outputs/analysis/L4_PLATFORMFIX_TRAINING_SMOKE_SUMMARY.md`.

### L4 CUDA Training Smoke Hold

The foreground L4 smoke was rerun with `JAX_PLATFORMS=cuda`. It still
disappeared during or immediately before the tiny PPO smoke; the expected smoke
output directory was never created.

Current backend matrix:

```text
local CPU training-smoke: PASS
Colab A100 training-smoke: HOLD_REMOTE_NO_SENTINEL
Colab L4 training-smoke: HOLD_REMOTE_NO_SENTINEL
Colab L4 foreground + cuda selector: HOLD_REMOTE_NO_SENTINEL
```

Interpretation: this is now a cloud GPU training-runtime hold, not a recipe
result. Continue recipe/debug iteration on a stable backend such as local CPU,
and treat Colab GPU as a separate infrastructure issue.

Summary artifact:
`outputs/analysis/L4_CUDA_TRAINING_SMOKE_NO_SENTINEL_SUMMARY.md`.

### Local CPU Candidate Gate Fix

The closed-loop candidate evaluator now maps `--jax-platform cpu` to both:

```text
JAX_PLATFORM_NAME=cpu
JAX_PLATFORMS=cpu
```

This prevents local CPU candidate gates from probing the blocked ROCm backend.
The staged planner also accepts `--phase-gate-jax-platforms` for explicit gate
overrides when needed.

Rerunning the V15 local CPU smoke checkpoint gate now reaches the real policy
verdict:

```text
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
jax: cpu ['TFRT_CPU_0']
mean_local_vx: -0.0083 m/s
track_ratio: -0.1033
```

Next training task: use this fixed local gate path for short recipe debugging
or full CPU checks while Colab GPU remains a separate runtime issue.

Summary artifact:
`outputs/analysis/LOCAL_V15_CPU_GATE_AFTER_JAX_PLATFORMS_FIX_SUMMARY.md`.

### Colab GPU Startup Diagnostic

Added a narrower diagnostic path for the Colab GPU smoke hold:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session <colab-session> \
  --workflow training-smoke-diagnostic \
  --run \
  --foreground-remote \
  --foreground-remote-timeout-s 1800 \
  --timeout-s 1800 \
  --smoke-num-timesteps 64 \
  --smoke-export-min-step 1
```

This workflow runs `tools/diagnose_training_smoke_startup.py`, which creates
its output directory first and writes one artifact per stage:

```text
00_python_jax_device
01_import_training_stack
02_smoke_dry_run
03_smoke_run
```

Use this before another full recipe launch. The goal is to determine whether
Colab disappears during CUDA/JAX device computation, Playground imports, smoke
runner dry-run startup, or the tiny PPO loop itself.

Local validation:

```text
00_python_jax_device: PASS
01_import_training_stack: PASS
02_smoke_dry_run: PASS
03_smoke_run: PASS
```

The Colab poller also now attempts to download the remote workflow output
directory into `partial_remote_output` before declaring
`HOLD_REMOTE_NO_SENTINEL` or `HOLD_REMOTE_TIMEOUT`.

Summary artifact:
`outputs/analysis/LOCAL_TRAINING_SMOKE_STARTUP_DIAGNOSTIC_SUMMARY.md`.

### Multi-Seed Phase Gates

Substantial staged A100 runs should no longer trust a single phase-gate rollout.
The staged planner can now run a seed-sweep gate after each phase:

```bash
python3 tools/plan_staged_curriculum_training.py \
  --run \
  --phase-gate-freeze-check \
  --phase-gate-seeds 0-3 \
  --phase-gate-max-fall-fraction 0.0 \
  --phase-gate-min-track-ratio-mean 0.25 \
  --phase-gate-min-vx-mean 0.02
```

The Colab staged workflow passes `--staged-phase-gate-seeds 0-3` by default and
bundles the seed-gate markdown/JSON artifacts on both pass and hold exits.

Use this gate before promoting any future V16+ staged phase. The phase must
show consistent forward motion across seeds, not merely avoid falling by
freezing or drifting backward.

### V16 Anchored Continuation

The next recipe is `movement_bootstrap_v16`. It deliberately returns to the
recovered V5 moving checkpoint instead of continuing V15's standstill lineage.
Run it only with an explicit restore checkpoint:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --session open-duck-a100 \
  --workflow staged-curriculum \
  --staged-recipe movement_bootstrap_v16 \
  --staged-initial-restore-checkpoint \
    policy/candidates/movement_bootstrap_v5_phase1_trainable_recovery_20260623/checkpoint_2026_06_23_205634_368640 \
  --staged-phase-gate-seeds 0-3
```

Do not treat a fall-count improvement as sufficient. V16 must improve the
multi-seed distribution while preserving positive mean forward velocity and
command tracking.

The first V16 A100 phase-1 attempt reached step 0 but produced no exit sentinel
or artifact bundle. Treat it as `HOLD_A100_V16_PHASE1_NO_SENTINEL`, not as a
policy result. Before relaunching, improve the Colab workflow so it detects an
alive remote process without a sentinel and does not start a second job in the
same session.

A tiny restored V16 A100 smoke also reached step 0 without a final sentinel, but
the same restored V16 path passed locally on CPU after resolving the restore
checkpoint to an absolute path before invoking the Playground runner. Current
interpretation:

```text
V16 restore/training path: locally validated
A100/Colab/CUDA path: still needs one tiny restored smoke rerun
```

Next A100 action should be a tiny restored V16 smoke with the PID-aware poller
and timeout-safe PID probe, not a full phase-1 launch. If that tiny A100 smoke
passes, relaunch full V16 phase 1 with the multi-seed phase gate enabled.

The tiny A100 restored smoke now passes the workflow gate: it restores the V5
checkpoint, runs V16 phase-1 training on GPU for 120 timesteps, exports ONNX,
runs x=0 and x=0.08 sim gates, and downloads artifacts. The toy 120-step policy
correctly holds both gates and is not a robot candidate.

Next:

```text
Run full V16 phase 1 on A100.
Keep multi-seed phase gates enabled.
Do not deploy or test on the robot.
```

The first full V16 phase-1 A100 run reached the multi-seed phase gate with a
phase-1 ONNX, but the Colab session was lost before seed-gate artifacts were
downloaded. Treat this as `HOLD_A100_V16_PHASE1_SEED_GATE_STALL`, not as a V16
policy verdict.

Seed-gate tooling has been patched to emit per-seed start/done markers, kill
subprocess groups on timeout, and write partial seed-sweep JSON after each seed.
Rerun full V16 phase 1 with the patched gate before changing the recipe.

The patched rerun completed phase-1 training and produced the full multi-seed
gate. V16 phase 1 held:

```text
falls: 1/4
track_ratio_mean: -0.1269
mean_local_vx_mean: -0.0102 m/s
```

Before designing V17, sweep the V16 intermediate ONNX exports from steps 40960
and 81920. If an intermediate checkpoint has better forward-progress
distribution than the final 122880 checkpoint, branch from it. If all V16
checkpoints are low/reverse progress, stop extending the V5-anchor continuation.

The intermediate sweep found no better V16 branch point:

```text
40960:  falls 1/4, track_ratio_mean -0.0508, vx_mean -0.0041 m/s
81920:  falls 1/4, track_ratio_mean -0.1072, vx_mean -0.0086 m/s
122880: falls 1/4, track_ratio_mean -0.1269, vx_mean -0.0102 m/s
```

Next recipe should not be another V5-anchor continuation. V17 should be a
structural break that makes signed positive progress non-negotiable from the
start while keeping enough pitch/base-height/contact pressure to avoid the old
lunge and collapse modes.

### V17 Structural Break

V17 is the next offline recipe:

```text
phase 1: no bridge, x=0.04-0.06, hard signed positive progress
phase 2: mild bridge transfer only if phase 1 passes
phase 3: fitted bridge low-command transfer only if phase 2 passes
```

It intentionally does not restore from the V5 checkpoint. The goal is to escape
the V5/V16 low-reverse-progress basin rather than regularize toward it.

The A100 V17 phase-1 run completed but held the multi-seed gate:

```text
status: HOLD_PHASE_MULTI_SEED_FALLS
falls: 1/4
track_ratio_mean: -0.2876
mean_local_vx_mean: -0.0230 m/s
```

Per-seed outcome:

```text
seed 0: low progress, track_ratio  0.0358
seed 1: fall at 33 samples, reverse vx, track_ratio -1.2270
seed 2: low progress, track_ratio  0.0560
seed 3: low/reverse progress, track_ratio -0.0152
```

Conclusion: removing the V5 restore and making phase-1 progress pressure much
harder was still insufficient. Do not proceed to V17 phase 2; phase 1 failed
the discovery gate.

Next offline task before another large A100 run:

- replay V17 phase-1 rollouts with reward-component logging for seeds `0-3`
- verify the local forward-velocity sign convention used by training reward and
  candidate evaluator
- compare command-progress failure penalties against posture, base-height, and
  contact-support terms
- inspect whether the policy is rewarded for crouched support / low motion more
  than stepping
- design the next recipe only after that reward audit

Summary artifact:
`outputs/analysis/A100_V17_PHASE1_MULTI_SEED_HOLD_SUMMARY.md`.

### V17 Reward Override Audit

V17 phase 1 was replayed with the actual phase-1 reward override config. This
removed a possible evaluation mismatch:

```text
x=0.08, vanilla bridge, seeds 0-3, 5 seconds
falls_or_terminations: 4/4
track_ratio_mean: -0.2367
mean_local_vx_mean: -0.0189 m/s
```

Seeds `0`, `2`, and `3` terminate at sample `60`, which is the
command-progress failure warmup boundary. Seed `1` reverses and collapses at
sample `32`, before that failure term activates.

Conclusion:

- the reward overrides are active
- V17 is failing the intended progress objective
- the failure is still low/reverse progress, not an actuator envelope violation
- do not run V17 phase 2

Next offline tasks before another A100 run:

- audit the reward source for the local-forward-velocity sign convention
- compare the dense signed-progress terms with posture/contact survival terms
- decide whether delayed terminal command-progress failure is too sparse for PPO
- design the next recipe only after the reward/sign audit

Summary artifact:
`outputs/analysis/V17_PHASE1_REWARD_OVERRIDE_AUDIT_SUMMARY.md`.

### V17 Sign And Low-Command Audit

The reward/evaluator sign convention was audited after the V17 reward-overridden
replay. The local-forward sign is consistent:

```text
command-progress window: local_vx * sign(command_x)
dense forward progress: local_vel[0] * sign(command_x)
dense shortfall/wrong-direction costs: local_vel[0] * sign(command_x)
candidate evaluator: local_forward_velocity / command_x
```

The same V17 phase-1 checkpoint was then replayed at `x=0.04`, the low end of
the command range it trained on. It still failed all four seeds:

```text
runs: 4
falls_or_terminations: 4
duration_complete: 0
track_ratio_mean: -0.6911
mean_local_vx_mean: -0.0276 m/s
```

Conclusion: V17 did not fail because of a sign bug or because the `x=0.08` gate
was too aggressive. It failed to learn coherent forward motion at the easiest
trained command under the intended reward config.

Next recipe should be designed as a minimal low-command discovery experiment:

- train and gate on the same low command first, such as `x=0.04`
- keep bridge disabled until low-command motion exists
- remove or minimize any survival reward that can make standing competitive
- make wrong-direction motion immediately expensive
- prefer dense per-step signed progress over delayed terminal progress failure
- only return to `x=0.08` after low-command motion passes across seeds

Summary artifact:
`outputs/analysis/V17_REWARD_SIGN_AND_LOW_COMMAND_AUDIT.md`.

### V18 Minimal Low-Command Discovery

The next staged recipe is `movement_bootstrap_v18`.

Purpose:

```text
Answer the smallest remaining discovery question:
can the policy learn coherent forward motion at x=0.04 at all?
```

Phase-1 constraints:

```text
restore: none
bridge: disabled
training command range: x=0.035-0.045
phase gate command: x=0.04
phase gate bridge: vanilla
zero command probability: 0
alive/imitation rewards: 0
```

Reward intent:

```text
dense per-step signed progress
immediate wrong-direction pressure
reduced posture/contact shaping compared with V17
delayed command-progress failure retained only as a backstop
```

Stop rule:

```text
If V18 phase 1 fails x=0.04 across seeds, do not run phase 2.
Do not test x=0.08 until x=0.04 passes.
Do not add actuator bridge until low-command motion exists.
```

Plan artifact:
`outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN_V18.md`.

### V18 A100 Result

V18 phase 1 was run on A100 and gated at `x=0.04`, the same low-command region
used for phase-1 training.

Result:

```text
HOLD_PHASE_MULTI_SEED_FALLS
```

Per-seed result:

```text
seed 0: low forward progress, duration complete, track ratio 0.0165
seed 1: fall/termination at 33 samples, track ratio -2.4426
seed 2: low forward progress, duration complete, track ratio 0.0575
seed 3: low/reverse progress, duration complete, track ratio -0.1171
```

Distribution:

```text
runs: 4
falls: 1
duration_complete: 3
track_ratio_mean: -0.6214
vx_mean: -0.0249 m/s
```

Stop rule outcome:

```text
Do not run V18 phase 2.
Do not test V18 at x=0.08.
Do not send V18 to the robot.
```

Tooling caveat:

```text
The V18 A100 seed gate did not pass phase reward overrides into the evaluator.
The hold is still valid because the failure is from motion/fall metrics, but
raw reward-term diagnostics from that gate are not the V18 training reward.
Future phase gates should pass phase-local reward overrides before reward-term
diagnostics are interpreted.
```

Corrected replay:

```text
V18 phase-1 final ONNX was replayed with the intended V18 reward overrides for
seeds 0-1 at x=0.04. Both seeds terminated:
  seed 0: command-progress failure at 50 samples
  seed 1: reverse/collapse at 33 samples
```

The corrected replay confirms the reward machinery is active. V18 still fails
the low-command discovery task under its intended reward config.

Low-command reward signal:

```text
At x=0.04, the analytic V18 reward signal prefers forward local velocity over
standing:
  standstill reward: -1.3686
  required-speed reward at vx=0.026: 1.6494
  command-speed reward at vx=0.040: 2.2800
```

Stop tuning the V18-style reward weights as the main strategy. The immediate
signal is not the blocker; cold-start locomotion discovery is.

Next offline tasks:

- locate and audit the upstream Open Duck reference-motion / imitation path
- build an imitation/reference-gait seed experiment at `x=0.04`, vanilla dynamics
- gate the seeded candidate across seeds on coherent forward motion, not fall-count
- if the seed refines, reintroduce the fitted actuator bridge later
- if the seed degrades, debug the reward/task landscape against the reference behavior

### V19 Reference-Imitation Discovery Split

The upstream reference-motion artifact is present at:

```text
../Open_Duck_Playground/playground/open_duck_mini_v2/data/polynomial_coefficients.pkl
```

The audit found the nearest reference entry for the `x=0.04` low-command test:

```text
nearest_reference_key: 0.074_-0.037_-0.074
period: 0.54 s
steps_per_period: 27 at 50 Hz
sampled mean linvel_x: 0.0772 m/s
sampled mean linvel_y: -0.0417 m/s
sampled p95_abs linvel_y: 0.2804 m/s
```

Important interpretation:

```text
V19 is a reference-imitation reward seed, not a robot test and not a runtime
behavior change. The reference contains the 14 runtime action joints plus
antenna dimensions, while the active imitation reward compares leg joint
pose/velocity, base motion, and foot contacts.
```

The nearest reference is not a perfect command match for straight low-speed
walking. It is faster than `x=0.04` and side-biased. Treat V19 as a test of a
nearby reference reward seed, not as proof that a perfectly matched reference
trajectory would also fail.

V19 phase 1:

```text
recipe: movement_bootstrap_v19
phase: phase1_reference_imitation_seed_x004
dynamics: vanilla
actuator bridge: disabled
command_x training range: 0.035-0.045
phase gate command_x: 0.04
phase gate seeds: 0-7
imitation_scale: 4.0
alive_scale: 0.0
zero_command_probability: 0.0
```

Decision rule:

```text
If V19 refines into coherent multi-seed forward motion:
  cold-start discovery was the blocker. Reintroduce the fitted actuator bridge
  only after the low-command vanilla gait passes.

If V19 degrades into standstill, reverse, collapse, or command-progress failure:
  the reward/task landscape is hostile even to the reference gait. Stop
  cold-start/reward-weight variants and debug against the reference path.
```

Summary artifact:
`outputs/analysis/A100_V18_PHASE1_LOW_COMMAND_HOLD_SUMMARY.md`.
Corrected reward replay:
`outputs/analysis/V18_PHASE1_REWARD_OVERRIDE_REPLAY_SUMMARY.md`.
Decision brief:
`docs/LOW_COMMAND_DISCOVERY_DECISION.md`.
Reference audit:
`outputs/analysis/REFERENCE_MOTION_SEED_AUDIT.md`.
V19 plan:
`outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN_V19.md`.

### V19 A100 Partial Result

V19 phase 1 trained on A100 and reached the x=0.04 multi-seed gate. The Colab
session was lost before final artifact download, but six completed seeds were
captured from the remote monitor:

```text
seed 0: fall/termination, track ratio -0.0239
seed 1: reverse/collapse, track ratio -2.2442
seed 2: low progress/fall, track ratio 0.1931
seed 3: reverse/fall, track ratio -0.4032
seed 4: low progress/fall, track ratio 0.1999
seed 5: hard reverse/collapse, track ratio -8.1420
```

Decision:

```text
V19 is a partial hold. The reference-imitation reward did not refine into
coherent low-command forward motion in the observed seed distribution.
```

Do not rerun x=0.08, fitted bridge, or robot validation from V19.

Next training-bridge task:

```text
debug the reference/reward path directly:
  - score the upstream reference trajectory under the current task rewards
  - quantify the command mismatch from using the nearest reference grid point
  - decide whether to add/interpolate a straight x=0.04 reference
  - confirm whether following the reference is rewarded above standing/reverse
  - identify whether termination/contact/base-height terms destroy it
  - only then decide whether to modify the task or use behavior cloning
```

V19 artifact:
`outputs/analysis/A100_V19_REFERENCE_SEED_PARTIAL_HOLD_SUMMARY.md`.

### Reference Grid Interpolation

The nearest raw reference key was not a clean `x=0.04,y=0,yaw=0` gait. A grid
interpolation audit shows a better candidate can be synthesized from symmetric
lateral references and the `dx=0.0` / `dx=0.074` rows:

```text
source keys:
  0.0_-0.037_-0.074
  0.0_0.037_-0.074
  0.074_-0.037_-0.074
  0.074_0.037_-0.074
composite mean linvel_x: 0.0426 m/s
composite mean linvel_y: -0.0021 m/s
```

Next implementation work:

```text
1. create a synthesized reference artifact for straight x=0.04, or add a
   reference interpolation path to the training environment
2. score the synthesized reference under the current task rewards before
   training
3. only then launch a V20 reference-imitation run
```

Artifact:
`outputs/analysis/REFERENCE_GRID_INTERPOLATION.md`.

### Reference Override Artifact

A training-only override pickle now exists:

```text
outputs/analysis/reference_motion_x004_override.pkl
sha256: see outputs/analysis/REFERENCE_MOTION_OVERRIDE.md
replaced key: 0.074_-0.037_-0.074
validated PolyReferenceMotion command lookup:
  command x=0.04, y=0.0, yaw=0.0
  mean linvel_x = 0.0426 m/s
  mean linvel_y = -0.0021 m/s
```

This preserves the original grid shape by replacing the key that
`PolyReferenceMotion` already selects for the straight x=0.04 command. V20
should use this override only as a training/reference artifact; it is not a
runtime or robot file.

Implemented workflow support:

```text
V20 recipe: movement_bootstrap_v20
override: outputs/analysis/reference_motion_x004_override.pkl
wrapper flag: --reference-motion-override
behavior:
  - back up Playground polynomial_coefficients.pkl
  - copy the override only for the training subprocess
  - record source/destination/backup sha256 in the run manifest
  - restore the original reference file after the subprocess exits
```

V20 has now run. It is a hold, not a deployable candidate.

```text
V20 A100 training: completed
matched reference override: applied, hash-recorded, restored
gate: x=0.04, vanilla, seeds 0-7
result: 8/8 early terminations
mean vx: -0.0539 m/s
mean track ratio: -1.3468
mean lateral p95_abs velocity: 0.3793 m/s
```

Interpretation:

```text
The V19 raw-reference command mismatch was a real confound, but correcting it
did not produce coherent low-command forward motion. The next work is not
another reward-weight variant. Debug the reference/imitation mechanism itself.
```

Next tasks:

```text
1. verify policy/reference phase alignment
2. score forced reference-following rollouts under current task rewards
3. test whether command-progress termination prevents early reference lock
4. add behavior-cloning or supervised pretraining if PPO cannot stay near the
   matched reference
5. only return to fitted actuator bridge after x=0.04 vanilla motion passes
```

Do not run robot validation, x=0.08, or the fitted actuator bridge until the
x=0.04 vanilla multi-seed gate passes with coherent forward motion.

Artifact:
`outputs/analysis/REFERENCE_MOTION_OVERRIDE.md`.

V20 plan:
`outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN_V20.md`.

V20 result:
`outputs/analysis/V20_MATCHED_REFERENCE_TRACE_SUMMARY.md`.

Reference-lock signal:

```text
status: PASS_REFERENCE_SIGNAL_COHERENT
progress_ratio: 1.0512
ideal_imitation_scaled: 24.0
pre_terminal_unclipped_sum_mean: 50.8050
lateral p95_abs velocity: 0.2350 m/s
```

This says the matched reference kinematics are coherent as a low-command
progress/reward signal. PPO did not acquire or preserve that reference, but the
next direct playback diagnostic shows there is also a reference/action-contract
problem to resolve before behavior cloning.

Artifact:
`outputs/analysis/REFERENCE_LOCK_SIGNAL_V20.md`.

Reference-target rollout:

```text
tool: tools/eval_reference_motion_rollout.py
status: HOLD_REFERENCE_TARGET_TERMINATES
command: x=0.04
dynamics: vanilla
seeds: 0-7
runs: 8
early terminations: 8
duration_complete: 0
mean vx: -0.0105 m/s
mean track ratio: -0.2614
mean lateral p95_abs velocity: 0.3918 m/s
mean action saturation: 6.4967%
mean target clip p95: 0.0314 rad
mean joint tracking p95: 0.1876 rad
mean reference contact mismatch: 69.50%
```

Pitch-chain stress from direct reference playback:

```text
left_hip_pitch: 23.1496% action saturation, 3.9927 rad/s sent velocity p95
left_knee: 15.2756% action saturation, 5.2400 rad/s sent velocity p95
left_ankle: 12.1260% action saturation, 3.9546 rad/s sent velocity p95
right_hip_pitch: 18.7402% action saturation, 5.1082 rad/s sent velocity p95
right_knee: 15.7480% action saturation, 5.2400 rad/s sent velocity p95
right_ankle: 5.9843% action saturation, 5.1066 rad/s sent velocity p95
```

Interpretation:

```text
Direct reference-derived actions still fail when passed through the current
action_scale and max_motor_velocity contract. Do not launch another PPO or BC
run yet. First inspect:
  - whether the 16-dof reference-to-14-action mapping is correct
  - whether the reference phase/reset index aligns with env reset
  - whether the reference target velocities exceed the intended low-command
    budget even though the mean reference velocity is x=0.04
  - whether lateral sway/contact timing causes the early collapses
  - whether the reference should be converted into a supervised action dataset
    from realized stable targets rather than raw reference joint positions
```

Artifact:
`outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20.md`.

Reference action-envelope audit:

```text
tool: tools/analyze_reference_action_envelope.py
status: HOLD_REFERENCE_EXCEEDS_ACTION_ENVELOPE
closest low-distance phases have 0 saturated joints
left_knee target velocity p95/max: 8.0846 / 8.6417 rad/s
right_knee target velocity p95/max: 9.8963 / 13.2122 rad/s
right_hip_pitch target velocity p95/max: 5.4889 / 6.0116 rad/s
right_ankle target velocity p95/max: 4.8676 / 7.6140 rad/s
right_knee max_abs_action: 2.2704
right_hip_pitch max_abs_action: 1.9062
```

Interpretation:

```text
The reference phase can be chosen near home, but the reference waveform still
exceeds the policy action envelope and target-rate budget over the cycle. A BC
or reference-lock phase must not train directly against raw polynomial joint
positions. First build an envelope-aware reference projection/filter, or derive
targets from realized stable rollouts.
```

Artifact:
`outputs/analysis/REFERENCE_ACTION_ENVELOPE_V20.md`.

Projected reference rollout:

```text
tool: tools/eval_reference_motion_rollout.py --reference-target-mode cycle_projected
status: HOLD_REFERENCE_TARGET_TERMINATES
runs: 8
early terminations: 8
duration_complete: 0
mean vx: -0.0100 m/s
mean track ratio: -0.2495
mean lateral p95_abs velocity: 0.4017 m/s
mean action saturation: 1.1454%
mean target clip p95: 0.0000 rad
mean joint tracking p95: 0.1440 rad
mean reference contact mismatch: 68.85%
```

Interpretation:

```text
Projection fixed most of the raw action/rate envelope violation, but the
rollout still fails. Do not launch BC/PPO yet. The next diagnostic target is
reference/task alignment: phase offset, reset state, contact timing, lateral
sway, and whether this polynomial reference is dynamically compatible with the
current flat-terrain Joystick initialization.
```

Artifact:
`outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20_PROJECTED.md`.

Projected phase-offset check:

```text
phase 1:  HOLD, samples mean 83.0000, track ratio -0.2495, contact mismatch 68.85%
phase 5:  HOLD, samples mean 81.6250, track ratio -0.4917, contact mismatch 68.15%
phase 19: HOLD, samples mean 69.3750, track ratio -1.2155, contact mismatch 68.54%
```

Interpretation:

```text
Starting from a home-near reference phase does not fix the projected reference.
The reference/actual contact pattern mismatch stays near 68-70% across raw,
projected, and phase-offset variants. The next reference-path work should target
contact/lateral/reference compatibility, or build a realized stable-target
dataset instead of replaying polynomial joint positions.
```

Artifacts:

```text
outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20_PROJECTED_PHASE5.md
outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20_PROJECTED_PHASE19.md
```

Reference contact compatibility:

```text
tool: tools/analyze_reference_contact_compatibility.py
raw reference: 68.03% mismatch, actual double support 73.86%, reference double support 35.43%
projected phase 1: 67.77% mismatch, actual double support 75.90%, reference double support 35.54%
projected phase 5: 67.23% mismatch, actual double support 74.89%, reference double support 37.52%
projected phase 19: 67.57% mismatch, actual double support 74.41%, reference double support 38.38%
```

Interpretation:

```text
The reference expects alternating single support much more often than the
simulated body realizes. Current reference targets keep the sim in double
support. A left/right swap only reduces mismatch to about 65-66%, and polarity
inversion is much worse, so this is not a simple contact-bit encoding bug. Raw
or reference-projected BC is not the next training step. First either adapt the
reference contact schedule to the Joystick task or generate realized stable
targets from the actual sim dynamics.
```

Artifact:
`outputs/analysis/REFERENCE_CONTACT_COMPATIBILITY_V20.md`.

### Realized Motion Window Mining

The reference path now has a safer alternative to raw polynomial target BC:
mine short realized-motion snippets from existing sim traces that already pass
basic height, pitch, saturation, and forward-motion filters.

```text
tool: tools/mine_realized_target_windows.py
status: PASS_REALIZED_WINDOWS_AVAILABLE
candidate windows: 17
window length: 25 samples
best mean vx: 0.1071 m/s
best min base height: 0.1500 m
best pitch p95: 0.3954 rad
best action saturation: 0.0%
```

Use these windows only as curated motion hints or seed material. They are not a
complete walking dataset:

```text
some windows are pre-fall snippets
most windows are very short
contact state is mostly double support
post-window outcome must stay attached to each snippet
```

Next dataset tasks:

```text
1. add stricter filters for post-window survival and contact diversity
2. export a compact candidate manifest, not raw trace dumps
3. build a supervised pretraining experiment only from curated windows
4. keep V20 raw polynomial targets out of BC until contact compatibility is fixed
5. gate any supervised seed by x=0.04 multi-seed forward-motion distribution
```

Artifacts:

```text
outputs/analysis/REALIZED_TARGET_WINDOW_MINE.md
outputs/analysis/realized_target_window_mine.json
```

### Realized Motion Window Curation Gate

A stricter curation pass has been added so mined snippets cannot silently become
a weak BC dataset:

```text
tool: tools/curate_realized_target_windows.py
status: HOLD_INSUFFICIENT_CURATED_WINDOWS
min_curated_windows: 8
curated_seed_windows: 1
review_motion_hints: 15
rejected_dataset_seeds: 1
```

This is a hold for supervised pretraining:

```text
do not train BC/PPO from the current realized-window manifest
do not treat review-only motion hints as target labels
generate or mine more stable low-command windows first
```

Next curation tasks:

```text
1. collect more low-command realized sim traces with explicit per-seed outcomes
2. prefer windows with no later termination, low lateral velocity, and low pitch
3. require contact-pattern diversity instead of mostly double-support snippets
4. keep all snippets linked to the source trace, seed, mode, and future outcome
5. only start supervised pretraining when the curated pool passes the count/diversity gate
```

Artifacts:

```text
outputs/analysis/REALIZED_TARGET_WINDOW_CURATION.md
outputs/analysis/realized_target_window_curation.json
```

### Broad Realized-Window Archive Sweep

The same curation gate was applied to a broader trace manifest built from all
compatible JSONL traces currently available under `outputs/analysis`:

```text
status: HOLD_INSUFFICIENT_CURATED_WINDOWS
compatible candidate windows: 94
curated_seed_windows: 1
review_motion_hints: 37
rejected_dataset_seeds: 56
```

This rules out the easy path where enough clean seed data was already present
in previous candidate/reference traces. The current archive is useful for
understanding failure surfaces, not for direct supervised pretraining.

Next target-data tasks:

```text
1. generate new low-command rollouts specifically for target-window collection
2. stop each generation run with the same curation gate, not subjective review
3. require enough curated windows across seeds/modes before BC
4. keep broad trace mining as an audit, not as an automatic label exporter
```

Artifacts:

```text
outputs/analysis/REALIZED_TARGET_WINDOW_MINE_BROAD.md
outputs/analysis/realized_target_window_mine_broad.json
outputs/analysis/REALIZED_TARGET_WINDOW_CURATION_BROAD.md
outputs/analysis/realized_target_window_curation_broad.json
```

### Contact-Gated Reference Projection

`tools/eval_reference_motion_rollout.py` now has an explicit
`contact_gated_projected` diagnostic mode. It starts from the cycle-projected
reference and damps a leg's target delta when the reference expects that foot to
swing but the sim still reports it in contact.

```text
mode: contact_gated_projected
contact_gate_swing_scale: 0.35
command_x: 0.04
seeds: 0-7
status: HOLD_REFERENCE_TARGET_TERMINATES
falls: 7/8
mean vx: 0.0012 m/s
mean contact mismatch: 69.4217%
curated seed windows: 0
```

Compared with the previous reference-target contact runs:

```text
raw:                    68.03% mismatch
cycle_projected:        67.77% mismatch
projected phase 5:      67.23% mismatch
projected phase 19:     67.57% mismatch
contact_gated_projected:66.35% mismatch
```

The small mismatch reduction is not enough to recover the gait, and actual
double support rises to `84.95%`. Do not continue this exact damping rule as a
training path. Use it as evidence that the reference needs a stronger stateful
target-generation/adaptation method.

Artifacts:

```text
outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20_CONTACT_GATED_PROJECTED.md
outputs/analysis/reference_motion_rollout_v20_contact_gated_projected.json
outputs/analysis/REFERENCE_CONTACT_COMPATIBILITY_V20_WITH_CONTACT_GATED.md
outputs/analysis/reference_contact_compatibility_v20_with_contact_gated.json
outputs/analysis/REALIZED_WINDOW_CONTACT_GATED_REFERENCE_CURATION.md
outputs/analysis/realized_window_contact_gated_reference_curation.json
```

### Contact-Synchronized Reference Projection

`tools/eval_reference_motion_rollout.py` also has a
`contact_synchronized_projected` mode. It retimes the projected reference phase
to match the current simulated contact pattern as closely as possible.

```text
mode: contact_synchronized_projected
command_x: 0.04
seeds: 0-7
status: HOLD_REFERENCE_TARGET_TERMINATES
falls: 7/8
mean vx: -0.0152 m/s
mean track ratio: -0.3788
mean contact mismatch: 7.7531% per-seed mean / 4.36% aggregate
curated seed windows: 0
```

This is a useful negative result. It shows that matching the reference contact
schedule is achievable by retiming, but it does not preserve forward motion.
Do not build the next target generator around contact matching alone.

Next target-generation requirements:

```text
1. preserve positive forward velocity
2. maintain low lateral velocity
3. keep body pitch and base height inside curation bounds
4. realize contact transitions instead of freezing into double support
5. pass the realized-window curation gate before BC/PPO
```

Artifacts:

```text
outputs/analysis/REFERENCE_MOTION_ROLLOUT_V20_CONTACT_SYNCHRONIZED_PROJECTED.md
outputs/analysis/reference_motion_rollout_v20_contact_synchronized_projected.json
outputs/analysis/REFERENCE_CONTACT_COMPATIBILITY_V20_WITH_CONTACT_ADAPTATIONS.md
outputs/analysis/reference_contact_compatibility_v20_with_contact_adaptations.json
outputs/analysis/REALIZED_WINDOW_CONTACT_SYNCHRONIZED_REFERENCE_CURATION.md
outputs/analysis/realized_window_contact_synchronized_reference_curation.json
```

### Target Generation Plan

The next canonical offline path is now documented in:

```text
docs/TARGET_GENERATION_PLAN.md
```

Do not launch another reward-only PPO run or BC run from the current mined
windows. The next implementation should generate short low-command target
windows deliberately, then stop at the curation gate:

```text
PASS_CURATED_DATASET_SEED_READY
```

The plan ranks the next generator options:

```text
1. short-horizon target search around projected reference
2. contact-transition constrained search
3. low-dimensional gait primitive search
4. reference adaptation with an explicit forward objective
```

### First Primitive Target Search

The first generator implementation is:

```text
tool: tools/search_low_command_target_primitives.py
command_x: 0.04
duration: 3 s
seeds: 0
candidates: 12
```

Result:

```text
search status: PASS_TARGET_SEARCH_RAN
best mean vx: 0.0018 m/s
window mine: HOLD_NO_REALIZED_WINDOWS
curated seed windows: 0
```

Interpretation:

```text
The initial symmetric pitch-chain primitive grid is stable but produces
standstill. Do not expand this exact grid blindly. The next target-search
iteration needs a forward-displacement mechanism such as stance asymmetry,
body-pitch bias, foot placement bias, or an optimizer that scores realized
forward progress directly.
```

Artifacts:

```text
outputs/analysis/TARGET_GENERATOR_SEARCH.md
outputs/analysis/target_generator_search.json
outputs/analysis/TARGET_GENERATOR_WINDOW_MINE.md
outputs/analysis/target_generator_window_mine.json
outputs/analysis/TARGET_GENERATOR_WINDOW_CURATION.md
outputs/analysis/target_generator_window_curation.json
```

### Biased Primitive Target Search

The generator was extended with common hip/knee/ankle pitch biases and a small
opposite hip-roll bias probe.

Key result:

```text
best useful family:
  hip_pitch_bias: +0.06 rad
  hip_pitch_amp: 0.05 rad
  knee_amp: 0.08 rad
  ankle_bias: +0.04 rad
  ankle_amp: -0.025 rad

roll-bias probe:
  hip_roll_bias: -0.04, 0.0, +0.04 rad
  seeds: 0,2
  curated seed windows: 12
  curated source/mode pairs: 12
  curated source files: 1
  status: HOLD_INSUFFICIENT_CURATED_DIVERSITY
```

Important caveat:

```text
The roll-bias probe is source/mode-diverse but not seed-diverse. All curated
windows are from seed_000. Seed_002 produced review-only motion hints, mostly
due to lateral velocity or contact-pattern dominance.
```

Do next:

```text
1. preserve the roll-bias probe artifacts as target-generator evidence
2. add seed-diversity or lateral/contact scoring before BC
3. build a deliberate compact target dataset only after the next generator
   pass produces windows that are not all from seed_000
```

### Seed-2 Rescue Search

A targeted seed-2 rescue grid swept stronger opposite hip-roll bias and finer
phase offsets around the best biased primitive family.

Result:

```text
seed: 2
candidates: 50
curated windows: 0
review hints: 80
rejected windows: 11
status: HOLD_INSUFFICIENT_CURATED_WINDOWS
```

Conclusion:

```text
Do not keep expanding hand grids. The seed-2 failure splits between high lateral
velocity in early windows and single-contact dominance in later windows. The
next generator should optimize a score that includes forward velocity, lateral
velocity, contact diversity, base height, and actuator envelope terms.
```

### Shuffled Broad Primitive Search

The primitive tool now supports deterministic candidate shuffling so broad grids
can be sampled without nested-loop ordering bias.

Result:

```text
seeds: 0,2
sampled candidates: 40
grid_seed: 20260625
curated windows: 11
curated source files: 2
curated source/mode pairs: 11
status: PASS_CURATED_DATASET_SEED_READY
seed distribution: seed_000=10, seed_002=1
```

Do next:

```text
1. build a compact target-dataset manifest from the 11 curated windows
2. verify the manifest keeps source/mode/seed metadata and does not copy raw
   trace slices into git
3. run a no-training dataset sanity check
4. only then consider a small supervised/imitation seed experiment
```

### Target Dataset Manifest

A compact manifest was generated from the shuffled broad curated windows:

```text
tool: tools/build_target_dataset_manifest.py
dataset_id: e84d27e27fd73419
status: PASS_TARGET_DATASET_MANIFEST_READY
entries: 11
source files: 2
source/mode pairs: 11
source distribution: seed_000=10, seed_002=1
```

Do next:

```text
1. run a no-training manifest sanity check
2. review whether the 10:1 source skew is acceptable for a tiny smoke seed
3. if accepted, run only a tiny supervised/imitation smoke experiment
4. do not launch a larger PPO run directly from this manifest
```

### Target Dataset Sanity Check

The compact manifest was checked against the local ignored traces:

```text
tool: tools/check_target_dataset_manifest.py
status: WARN_TARGET_DATASET_SANITY_SOURCE_SKEW
entries checked: 11
entries with errors: 0
bc readiness: HOLD_TARGET_DATASET_BC_OBSERVATIONS_MISSING
bc ready entries: 0
source files: 2
max source fraction: 0.9091
```

Do next:

```text
1. treat the manifest as valid target evidence, not BC-ready data
2. extend the target generator/traces to record policy obs[101]
3. rebuild the manifest and sanity check until bc_readiness_status passes
4. only then run a tiny supervised/imitation smoke experiment
```

### Observation-Ready Target Dataset

The primitive generator now records `observation[101]`, and the shuffled broad
search was rerun into an observation-bearing trace set.

Result:

```text
dataset_id: 6c43c18e8f2b72ec
curation status: PASS_CURATED_DATASET_SEED_READY
manifest status: PASS_TARGET_DATASET_MANIFEST_READY
sanity status: WARN_TARGET_DATASET_SANITY_SOURCE_SKEW
bc readiness: PASS_TARGET_DATASET_BC_READY
entries: 11
source files: 2
source distribution: seed_000=10, seed_002=1
```

Do next:

```text
1. run only a tiny supervised/imitation smoke experiment
2. keep source skew visible in the smoke report
3. evaluate whether the resulting policy reproduces low-command forward motion
4. stop if the policy freezes, reverses, or only reduces supervised loss
```

### V5/V7 Low-Command Trace Collection

The old moving-lineage policies were replayed at `x=0.04` with vanilla dynamics
to see whether they can produce more realized low-command target snippets
without new training:

```text
tool: tools/run_candidate_seed_sweep.py
policies: v5_phase1, v7_anchor
seeds: 0-3
trace_seeds: 0-3
command_x: 0.04
bridge_mode: vanilla
duration: 5 s
```

Result:

```text
v5_phase1: HOLD, no coherent low-command forward motion
v7_anchor: HOLD, no coherent low-command forward motion
window mine: HOLD_NO_REALIZED_WINDOWS
curated seed windows: 0
```

This collection attempt did not add target seed data. Future target-data work
should not keep replaying these old policies at low command; it should change
the generation mechanism.

Artifacts:

```text
outputs/analysis/REALIZED_WINDOW_COLLECTION_X004_V5_V7_CPU.md
outputs/analysis/realized_window_collection_x004_v5_v7_cpu.json
outputs/analysis/REALIZED_WINDOW_COLLECTION_X004_V5_V7_MINE.md
outputs/analysis/realized_window_collection_x004_v5_v7_mine.json
outputs/analysis/REALIZED_WINDOW_COLLECTION_X004_V5_V7_CURATION.md
outputs/analysis/realized_window_collection_x004_v5_v7_curation.json
```

### Longer Target Window Remine

The observation-ready shuffled broad traces were remined for 50-sample windows
to check whether the current trace set already has longer BC material:

```text
tool: tools/mine_realized_target_windows.py
window_samples: 50
mine status: PASS_REALIZED_WINDOWS_AVAILABLE
curation status: HOLD_INSUFFICIENT_CURATED_WINDOWS
mined windows: 5
curated seed windows: 0
review motion hints: 5
```

The longer hints are all review-only because they fail lateral/contact criteria:

```text
failure reasons: high_lateral_velocity, single_contact_pattern_dominates
```

Do next:

```text
1. do not train from the current longer-window hints
2. make the next target generator score lateral velocity and contact alternation
3. require longer curated windows before sequence-aware imitation/pretraining
```

### Targeted Lateral/Contact Search

A targeted primitive search around lower hip-roll bias and lower lateral motion
produced the first 50-sample curated windows by count:

```text
tool: tools/search_low_command_target_primitives.py
command_x: 0.04
duration: 4 s
seeds: 0,2
candidates: 48
25-sample curated windows: 25
50-sample curated windows: 8
status: HOLD_INSUFFICIENT_CURATED_DIVERSITY
curated source files: 1
```

Do next:

```text
1. keep this as target-generation progress, not training permission
2. preserve the seed_000 50-sample families
3. make seed_002 pass by reducing lateral velocity and single-contact dominance
4. only build a longer-window target manifest after source diversity passes
```

### Seed 2 Balance Search

A larger but still bounded CPU search targeted the seed_2 review hints with
finer phase offsets and smaller hip-roll bias:

```text
tool: tools/search_low_command_target_primitives.py
command_x: 0.04
duration: 4 s
seeds: 0,2
candidates: 80
25-sample curated windows: 45
50-sample curated windows: 23
status: HOLD_INSUFFICIENT_CURATED_DIVERSITY
curated source files: 1
```

Do next:

```text
1. stop treating broader random primitive grids as the main path
2. add seed-robust candidate scoring for worst-seed lateral velocity
3. add contact alternation/contact-dominance terms to the target objective
4. require seed_002 to contribute curated windows before any supervised seed
```

### Target Seed Robustness Audit

The latest 50-sample curation outputs were audited by primitive mode and seed:

```text
tool: tools/analyze_target_seed_robustness.py
status: HOLD_SEED2_LATERAL_CONTACT
robust modes across seed_000 and seed_002: 0
seed0-curated / seed2-review near misses: 12
seed2 single_contact_pattern_dominates count: 64
seed2 high_lateral_velocity count: 40
```

Do next:

```text
1. make the next generator objective-driven, not just broader
2. target seed2 lateral p95 <= 0.12 m/s
3. target seed2 contact dominance <= 95%
4. keep all supervised/imitation training blocked until robust modes exist
```

Next target-generator spec:

```text
docs/TARGET_OBJECTIVE_GENERATOR_SPEC.md
```

### Target Objective Score

The worst-seed objective scorer was run on the latest target trace sets:

```text
tool: tools/score_target_candidates_objective.py
seed2-balance 50-sample status: HOLD_NO_SEED_ROBUST_TARGETS
lateral/contact 50-sample status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0
```

Best current near pass:

```text
mode: primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927
seed0: pass
seed2: vx=0.0515 m/s, vy95=0.0507 m/s, contact_dominance=98%
remaining failure: single_contact_pattern_dominates
```

Do next:

```text
1. tune contact alternation around the best near-pass candidate
2. target seed2 contact dominance <= 95%
3. preserve seed2 vx and vy95, which already pass on this candidate
4. preserve seed0 curation pass
```

### Contact-Break Target Search

A focused micro-grid around the best near-pass family tested whether small
contact-break perturbations could move seed2 from 98% contact dominance to the
<=95% gate:

```text
tool: tools/search_low_command_target_primitives.py
command_x: 0.04
duration: 4 s
seeds: 0,2
candidates: 96
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust 50-sample modes: 0
```

Best contact-break near pass:

```text
seed0: pass, vx=0.0531 m/s
seed2: vx=0.0453 m/s, vy95=0.1028 m/s
seed2 contact_dominance: 98%
failure: single_contact_pattern_dominates
```

Curation improved seed0 coverage but not seed diversity:

```text
50-sample curated windows: 70
50-sample curated modes: 38
curated source files: 1
curated source: seed_000
```

Do next:

```text
1. do not train from the contact-break windows; they are still single-seed
2. stop local micro-grid searches around the same sine primitive family
3. add a contact-lift/contact-transition primitive or objective
4. continue ranking by worst-seed score across seed_000 and seed_002
5. require seed2 contact dominance <=95% before rebuilding a target manifest
```

### Lift-Pulse Target Search

The primitive generator now has default-off lift-pulse parameters:

```text
--lift-duties
--lift-scales
```

The default `--lift-scales=0.0` preserves the old primitive. A bounded CPU
search tested narrow lift pulses across seed0 and seed2:

```text
candidates: 96
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust 50-sample modes: 0
```

Best lift-pulse near pass:

```text
seed0: pass, vx=0.0508 m/s
seed2: vx=0.0519 m/s, vy95=0.0937 m/s
seed2 contact_dominance: 98%
seed2 contact pattern: 98% double contact, 2% single contact
failure: single_contact_pattern_dominates
```

Curation remained single-seed:

```text
50-sample curated windows: 59
50-sample curated modes: 46
curated source files: 1
curated source: seed_000
```

Do next:

```text
1. keep supervised/BC/PPO training blocked
2. treat lift-pulse as a useful generator capability, not a solved target set
3. add a contact-state objective that rewards actual contact transitions
4. consider a foot-clearance/site-height metric, not just joint-space lift
5. require seed2 contact dominance <=95% before target-manifest rebuild
```

### Foot-Clearance Probe

The generator now writes `foot_site_z_m` for future target traces. A smaller
probe used stronger lift pulses and scored contact transitions explicitly:

```text
candidates: 48
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust 50-sample modes: 0
min_contact_transitions: 3
```

Best probe near pass:

```text
seed0: pass, vx=0.0475 m/s
seed2: vx=0.0565 m/s, vy95=0.1166 m/s
seed2 contact_dominance: 98%
seed2 contact_transitions: 2
seed2 foot_site_z_p95: 0.0159 m
```

Curation remained single-seed:

```text
50-sample curated windows: 23
50-sample curated modes: 19
curated source files: 1
curated source: seed_000
```

Do next:

```text
1. stop increasing knee-lift amplitude inside this primitive family
2. use foot-site clearance and contact transitions as first-class objectives
3. consider an IK/reference primitive that places swing feet, not only joint sinusoids
4. keep all training blocked until seed2 contributes curated windows
```

### Target Dataset BC Smoke

The observation-ready target manifest was tested with tiny linear and KNN
behavior-cloning smokes:

```text
tool: tools/run_target_dataset_bc_smoke.py
dataset_id: 6c43c18e8f2b72ec
samples: 275
source files: 2
source skew: seed_000=10 windows, seed_002=1 window
fit: near-exact train reconstruction
linear closed-loop replay: HOLD_BC_REPLAY_LOW_FORWARD_MOTION
knn closed-loop replay: HOLD_BC_REPLAY_LOW_FORWARD_MOTION
```

The linear closed-loop CPU replay completed without falling but produced
essentially zero actions:

```text
seed_000: vx=-0.0023 m/s, action_abs_mean=0.0001
seed_002: vx=+0.0014 m/s, action_abs_mean=0.0001
```

KNN avoided the zero-action collapse but still stayed well below the command:

```text
seed_000: vx=+0.0139 m/s, ratio=0.3463, action_abs_mean=0.1209
seed_002: vx=+0.0072 m/s, ratio=0.1798, action_abs_mean=0.0904
```

Do next:

```text
1. treat this as a hold for one-shot linear BC from the tiny target manifest
2. treat KNN as evidence that the dataset has weak motion hints but poor coverage
3. improve temporal/source diversity before scaling supervised pretraining
4. consider sequence-aware imitation or explicit rollout-preserving objectives
5. do not launch larger PPO from this dataset just because supervised loss is low
```

### Dynamic Hip-Roll Target Source

The latest target-source search added default-off dynamic hip-roll controls to
the primitive generator:

```text
--hip-roll-amps
--hip-roll-phase-offsets
```

Current evidence:

```text
broad dynamic-roll curation: PASS_CURATED_DATASET_SEED_READY
50-sample curated windows: 42
curated source files: 2
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust same-mode modes: 0
best same-mode near-pass:
  seed0: vx=0.0413 m/s, vy95=0.1234 m/s, contact_dominance=92%, transitions=3
  seed2: vx=0.0417 m/s, vy95=0.1110 m/s, contact_dominance=94%, transitions=4
```

Focused refinement around that near-pass did not clear the 50-sample gate:

```text
refine 50-sample curated windows: 3
refine 25-sample curated windows: 207
remaining blocker moved from seed0 lateral to seed0 low forward velocity
```

Training status:

```text
BC/PPO remains blocked under the strict same-mode seed-robust target-source gate.
Do not train from the dynamic-roll windows unless a reviewed experiment
explicitly relaxes the gate to source-diverse, non-same-mode windows.
```

Do next:

```text
1. keep the broad dynamic-roll family
2. reduce seed0 lateral p95 from 0.1234 to <=0.12 m/s
3. preserve seed0 vx >=0.04 m/s
4. preserve seed2 contact dominance <=95% and transitions >=3
5. prefer 50-sample robustness over 25-sample window count
6. rerun the target-source audit before any supervised or PPO launch
```

### Dynamic Hip-Roll Lateral-Fix Pass

The broad lateral-fix search cleared the strict target-source gate:

```text
objective score: PASS_SEED_ROBUST_TARGETS
robust objective modes: 2
50-sample curation: PASS_CURATED_DATASET_SEED_READY
50-sample curated windows: 70
curated source files: 2
curated modes: 63
seed robustness audit: PASS_SEED_ROBUST_TARGETS
robust curated modes: 3
```

Best robust target mode:

```text
mode: primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55
seed0: vx=0.0416 m/s, vy95=0.0716 m/s, contact_dominance=90%, contact_transitions=3
seed2: vx=0.0437 m/s, vy95=0.0736 m/s, contact_dominance=94%, contact_transitions=4
```

Training status:

```text
Target-source discovery is unblocked.
Robot validation remains blocked.
Full PPO remains blocked until a small offline imitation/BC smoke proves the
target windows produce a closed-loop policy that still moves forward.
```

Do next:

```text
1. build a target manifest from dynamic-roll lateral-fix 50-sample curation
2. run the smallest supervised/BC smoke
3. replay the BC policy in closed-loop vanilla x=0.04 over seed0 and seed2
4. grade on forward motion, lateral velocity, contact transitions, posture,
   target velocity, and tracking
5. only if the smoke passes, consider a larger offline imitation or PPO run
6. do not run robot validation
```

### Dynamic-Roll Lateral-Fix BC Smoke

Two compact manifests were tested:

```text
full lateral-fix manifest:
  dataset_id: 0ff1f1c3750dbfb1
  entries: 70
  samples: 3500
  source skew: seed_000=60 windows, seed_002=10 windows

robust-mode-only manifest:
  dataset_id: 47153f26ab48ef14
  entries: 9
  samples: 450
  robust modes: 3
  source skew warning: false
```

Closed-loop smoke results:

```text
full manifest linear: HOLD_BC_REPLAY_LOW_FORWARD_MOTION
  seed0 vx=0.0009 m/s
  seed2 vx=0.0037 m/s

full manifest KNN: HOLD_BC_REPLAY_LOW_FORWARD_MOTION
  seed0 vx=0.0064 m/s
  seed2 vx=0.0084 m/s

robust-mode KNN: HOLD_BC_REPLAY_LOW_FORWARD_MOTION
  seed0 vx=0.0070 m/s
  seed2 vx=0.0097 m/s

robust-mode linear: HOLD_BC_REPLAY_TERMINATED
  seed0 terminated at 73 samples with reverse velocity
```

Interpretation:

```text
The target windows are valid, but one-step obs[101] -> action[14] cloning does
not preserve the generated gait in closed-loop replay. The next imitation step
should be sequence-aware and rollout-preserving, not another one-step BC fit.
```

Do next:

```text
1. test whether preserving target sequence timing is sufficient
2. preserve primitive phase or time index through any future learner
3. train/evaluate against rollout metrics, not supervised loss
4. keep PPO blocked until sequence-aware imitation passes x=0.04 replay
5. keep robot validation blocked
```

### Dynamic-Roll Lateral-Fix Sequence Replay Smoke

The sequence-preserving smoke was run from the robust-mode-only manifest. It
replays each trace's startup prefix and then loops the curated 50-tick window in
closed-loop CPU sim.

Artifacts:

```text
tools/run_target_sequence_replay_smoke.py
outputs/analysis/TARGET_SEQUENCE_REPLAY_SMOKE_1P2S.md
outputs/analysis/target_sequence_replay_smoke_1p2s.json
outputs/analysis/TARGET_SEQUENCE_REPLAY_SMOKE.md
outputs/analysis/target_sequence_replay_smoke.json
```

Results:

```text
1.2 s replay:
  status: HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE
  aggregate seed0/seed2 vx: 0.0309 / 0.0363 m/s
  aggregate seed0/seed2 vy95: 0.1183 / 0.1466 m/s
  aggregate seed0/seed2 pitch95: 0.2967 / 0.2521 rad
  aggregate sent target velocity p95: 0.3668 rad/s

3.0 s replay:
  status: HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION
  aggregate seed0/seed2 vx: 0.0117 / 0.0138 m/s
  aggregate seed0/seed2 vy95: 0.0645 / 0.0499 m/s
  aggregate sent target velocity p95: 0.3658 rad/s

3.0 s aggregate replay with periodic seam correction:
  status: HOLD_SEQUENCE_REPLAY_TERMINATED
  seed0: terminated at 85 ticks, vx=0.1812 m/s, pitch95=1.1645 rad
  seed2: completed, vx=0.0194 m/s, pitch95=0.3589 rad
```

Interpretation:

```text
Timing preservation improves over memoryless one-step BC on the short horizon,
but the current target tables are not stable reusable gait labels. They miss
lateral/pitch gates over 1.2 s and lose forward progress when looped to 3 s.
Linear seam correction makes the aggregate replay worse, causing a seed0
lunge/fall, so the loop seam is not the only blocker.
```

Do next:

```text
1. do not launch PPO or robot validation from these target tables as-is
2. follow docs/PHASE_CONTINUATION_ADAPTER_PLAN.md
3. add a phase-continuation/contact-timing adapter before any learner
4. grade the adapter by the same closed-loop x=0.04 replay metrics
5. only after sequence replay passes, consider a compact supervised/imitation
   learner that preserves phase/time continuity
6. keep full training and robot validation blocked
```

### Phase Continuation Adapter Smoke

Default-off `contact_hold`, `contact_match`, and `state_match` adapters were
added to `tools/run_target_sequence_replay_smoke.py` and tested on the aggregate
robust target table.

Result:

```text
contact_hold: HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION
  seed0/seed2 vx: 0.0119 / 0.0138 m/s
  contact mismatch: 2.76% / 0.00%

contact_match: HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION
  seed0/seed2 vx: 0.0117 / 0.0138 m/s
  contact mismatch: 2.76% / 0.00%

state_match: HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION
  seed0/seed2 vx: 0.0117 / 0.0138 m/s
  contact mismatch: 2.76% / 0.00%
```

Interpretation:

```text
Contact/phase selection is not the primary blocker for the aggregate table.
Contact mismatch is already low, and the adapters do not recover forward
progress. Do not spend more runs trying to rescue the aggregate table with
contact matching alone.
```

Do next:

```text
1. generate a longer self-consistent low-command target trajectory directly, or
2. use the short target fragment only as a soft motion prior inside a
   closed-loop objective that rewards forward progress and posture, and
3. keep robot validation blocked
```

### Sustained Target Generation Probe

The existing dynamic-roll lateral-fix trace set was rescored at 100 and 150
samples, then a bounded sustained primitive search was run.

Result:

```text
existing lateral-fix 100-sample objective: HOLD_NO_SEED_ROBUST_TARGETS
existing lateral-fix 100-sample curation: curated_seed_windows=0
existing lateral-fix 150-sample objective: HOLD_NO_SEED_ROBUST_TARGETS
existing lateral-fix 150-sample curation: curated_seed_windows=0

sustained probe candidates: 180
sustained probe 100-sample objective: HOLD_NO_SEED_ROBUST_TARGETS
sustained probe 100-sample curation: curated_seed_windows=0
sustained probe 150-sample objective: HOLD_NO_SEED_ROBUST_TARGETS
sustained probe 150-sample curation: curated_seed_windows=0
```

Interpretation:

```text
The current primitive target generator family is exhausted as a direct
supervised-label source. It finds short fragments but not a robust sustained
low-command gait. Do not run BC/PPO from these target tables.
```

Do next:

```text
1. change the target generator structure, or
2. use the short fragments as a soft prior in a closed-loop learner/objective,
   not as hard action labels, and
3. keep robot validation blocked
```

### Soft-Prior Closed-Loop Learner Gate

The next branch is specified in:

```text
docs/SOFT_PRIOR_CLOSED_LOOP_LEARNER_PLAN.md
```

Current rule:

```text
do not launch BC/PPO directly from target tables
do not launch an A100 run from the primitive fragments
do not treat a 50-tick fragment as a loopable gait
```

Required next result:

```text
PASS_SOFT_PRIOR_SMOKE
```

before any small learner is authorized. The smoke must show that a default-off
prior based on the short fragments can preserve forward motion in closed-loop
sim without freezing, lunging, lateral instability, contact lock, or envelope
violation.

The first compact prior config is ready:

```text
tool: tools/build_soft_prior_fragment_config.py
status: PASS_SOFT_PRIOR_CONFIG_READY
entries: 9
source_files: 2
max pitch-chain target velocity p95: 2.4428 rad/s
```

Artifacts:

```text
outputs/analysis/SOFT_PRIOR_FRAGMENT_CONFIG.md
outputs/analysis/soft_prior_fragment_config.json
```

Next implementation target:

```text
default-off soft-prior smoke evaluator
```

Soft-prior smoke result:

```text
1.2 s: HOLD_SOFT_PRIOR_LATERAL_UNSTABLE
  seed0 vx=0.0325, seed2 vx=0.0414

3.0 s: HOLD_SOFT_PRIOR_FREEZE
  seed0 vx=0.0115, seed2 vx=0.0143
```

Interpretation:

```text
The prior is not a controller or label source. It should only become a weak
auxiliary term in a closed-loop learner that still rewards real progress,
posture, and survival.
```

Patch spec for the next cross-repo change:

```text
docs/SOFT_PRIOR_TRAINING_PATCH_SPEC.md
```

Patch helper:

```text
tools/prepare_training_soft_prior_patch.py
```

Review artifact:

```text
outputs/analysis/SOFT_PRIOR_TRAINING_PATCH.diff
```

Read-only validation result:

```text
PASS_PATCH_PREPARED
```

Applied Playground patch:

```text
repo: RobVanProd/Open_Duck_Playground
branch: codex/forward-progress-reward
pr: https://github.com/RobVanProd/Open_Duck_Playground/pull/4
commit: 11ebae1 training: add default-off soft prior reward
```

Verification artifact:

```text
outputs/analysis/SOFT_PRIOR_PLAYGROUND_PATCH_VERIFY.md
```

Next offline gate is a small learner run that explicitly enables the weak
soft-prior term and grades multi-seed forward motion. Robot validation remains
blocked.

### V21 Weak Soft-Prior Learner

The next offline recipe is now prepared but not launched:

```text
recipe: movement_bootstrap_v21
doc: docs/SOFT_PRIOR_LEARNER_V21_PLAN.md
plan_md: outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN_V21.md
plan_json: outputs/analysis/staged_curriculum_training_plan_v21.json
```

V21 is explicit-only. It was added to the staged planner and Colab workflow
without changing the default recipe from V20.

Run only after reviewing the plan:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow staged-curriculum \
  --staged-recipe movement_bootstrap_v21 \
  --staged-phase-gate-seeds 0-3 \
  --staged-phase-gate-command-x 0.04 \
  --staged-phase-gate-bridge-mode vanilla \
  --staged-phase-gate-freeze-check \
  --run
```

Do not run robot validation from V21. The only acceptable next result is a
multi-seed x=0.04 sim gate verdict.

Local CPU smoke:

```text
outputs/analysis/SOFT_PRIOR_CPU_SMOKE.md
status: PASS_SOFT_PRIOR_CPU_SMOKE
```

This confirms the patched Playground runner accepts the soft-prior config in an
actual tiny training invocation. It is not a candidate run.

V21 launch readiness:

```text
tool: tools/check_v21_launch_readiness.py
artifact: outputs/analysis/V21_LAUNCH_READINESS.md
json: outputs/analysis/v21_launch_readiness.json
status: HOLD_COLAB_SESSION_MISSING
```

The readiness check confirms:

```text
soft-prior config: PASS
V21 plan: PASS
Playground soft-prior patch: PASS
RDK PR checks: PASS
Playground PR checks: PASS
Colab session open-duck-l4: MISSING
```

Once a Colab session is active again, rerun the readiness check before launch.

Planner-level CPU smoke:

```text
artifact: outputs/analysis/V21_PLANNER_CPU_SMOKE.md
status: PASS_V21_PLANNER_CPU_SMOKE
```

This verifies the full staged planner path invokes the V21 phase-1 recipe with
the soft-prior flags and that the wrapper resolves the compact prior config to
an absolute path before calling the sibling Playground runner. It was a
22-timestep CPU smoke only; the generated `/tmp` checkpoint and ONNX are not
candidate artifacts.

Next step remains a real CUDA/Colab V21 run and an `x=0.04` multi-seed sim
gate after `tools/check_v21_launch_readiness.py` reports an active session.

If `google-colab-cli` still cannot see the session but a browser Colab notebook
is connected, use the single-cell fallback:

```bash
python3 tools/print_cuda_colab_cell.py \
  --staged-curriculum-v21 \
  --rdk-branch codex/colab-cli-cuda-workflow \
  --playground-branch codex/forward-progress-reward \
  --handoff-dir /home/lsd/robots/cuda_colab_handoff_v21
```

The generated notebook runs only the explicit V21 staged curriculum and bundles
small staged artifacts for local import. It is not robot approval.

The artifact importer now understands V21 staged-curriculum outputs. After
downloading a V21 browser-Colab bundle, run:

```bash
python3 tools/ingest_latest_cuda_artifact.py
```

Then start from `CUDA_ARTIFACT_IMPORT_SUMMARY.md`. Expected staged review
statuses are `READY_FOR_STAGED_GATE_REVIEW`, the specific phase-gate `HOLD_*`
reason, `INFO_STAGED_RUN_NO_PHASE_GATE`, or `HOLD_STAGED_NO_ONNX`.

Local ROCm status after the firmware/BIOS update:

```text
artifact: outputs/analysis/LOCAL_ROCM_STATUS_20260625.md
json: outputs/analysis/local_rocm_status_20260625.json
tool: tools/check_local_rocm_status.py
status: HOLD_LOCAL_ROCM_KFD
```

`rocminfo` currently fails on `/dev/kfd` with `Invalid argument`, and JAX cannot
see a ROCm device. Treat this as a workstation backend issue below JAX/MJX.
Do not run V21 on local ROCm until `rocminfo` and a minimal JAX device probe
both pass.

### V22 Strong Step-Prior Lock Diagnostic

V21 trained, but CPU trace replay showed the exported policy was still far from
the curated pitch-chain prior:

```text
artifact: outputs/analysis/V21_TRACE_SET_SUMMARY.md
soft_prior_abs_error_mean: 0.2609
failure_surfaces:
  LOW_PROGRESS_TERMINATION: 3
  REVERSE_HEIGHT_COLLAPSE: 1
```

The next explicit recipe is:

```text
recipe: movement_bootstrap_v22
doc: docs/SOFT_PRIOR_LOCKING_V22_PLAN.md
plan_md: outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN_V22.md
plan_json: outputs/analysis/staged_curriculum_training_plan_v22.json
```

V22 is a diagnostic, not a candidate for robot validation. It uses vanilla
dynamics, `x=0.035-0.045`, a strong step-phased soft prior, and the same x=0.04
multi-seed gate. It must not progress to fitted bridge, `x=0.08`, deployment,
or robot validation unless both the behavior gate and prior-lock trace gate
pass.

Expected launch shape after review:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow staged-curriculum \
  --staged-recipe movement_bootstrap_v22 \
  --staged-phase-gate-seeds 0-3 \
  --staged-phase-gate-command-x 0.04 \
  --staged-phase-gate-bridge-mode vanilla \
  --staged-phase-gate-freeze-check \
  --run
```

After importing artifacts, replay the exported V22 ONNX with trace capture and
run `tools/analyze_candidate_trace.py --soft-prior-config
outputs/analysis/soft_prior_fragment_config.json` for seeds 0-3. Compare
`soft_prior_abs_error_mean` against V21's `0.2609`; `<0.12` is the preferred
prior-lock target, and `<0.18` is useful but still a hold for robot work.

If V22 does not materially reduce prior distance, stop treating soft reward
shaping as sufficient imitation. The next branch should be explicit supervised
pretraining, behavior cloning, or a stronger reference-locking mechanism before
any actuator bridge or robot validation work resumes.

### Contact / Weight-Transfer Branch

The contact discriminator result is now recorded:

```text
artifact: outputs/analysis/CONTACT_WEIGHT_TRANSFER_DISCRIMINATOR.md
status: HOLD_CONTACT_NOT_BINARY_MISMATCH_ONLY
```

Use this distinction in the next branch:

```text
raw polynomial reference path:
  contact mismatch around 67-68%, actual double support around 74-76%;
  do not use as direct BC/controller labels.

dynamic-roll lateral-fix fragment path:
  binary contact mismatch is already low in closed-loop replay
  (2.76% / 0.00% on seed_000 / seed_002), but forward progress is still low.
```

Do not spend the next run on stronger pitch-chain prior scale or another
contact-bit adapter around the same short table. The next useful offline gate is:

```text
PASS_WEIGHT_TRANSFER_TARGET:
  100-150 tick target or rollout has meaningful forward progress, low lateral
  drift, stable pitch/height, in-envelope target velocities, and multiple
  useful support transitions.
```

If this gate fails, improve the generator/objective before launching another
CUDA PPO run. If it passes, use that target as the source for the next reviewed
BC/PPO experiment.

The first gate read over existing artifacts failed:

```text
artifact: outputs/analysis/WEIGHT_TRANSFER_TARGET_GATE.md
status: HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET
```

Existing 100/150-tick dynamic-roll lateral-fix objective-score artifacts have
`robust_mode_count: 0`. The dominant failures are low forward velocity and
single-contact-pattern dominance. Next implementation work should target the
generator/objective directly:

```text
1. score useful single-support dwell and left/right support alternation,
2. keep forward progress above the low-command gate for 100-150 ticks,
3. reject mostly double-support sustained windows,
4. keep lateral drift, pitch, height, action saturation, and target velocity
   inside the existing gates,
5. only then create a new manifest for BC/PPO.
```

`tools/score_target_candidates_objective.py` now supports explicit
weight-transfer criteria:

```text
--max-double-support-pct
--max-no-support-pct
--min-single-support-pct
--min-each-single-support-pct
```

The first explicit rescore also failed:

```text
100 ticks:
  double_support_dominates: 310
  too_little_single_support: 294

150 ticks:
  double_support_dominates: 312
  too_little_single_support: 312
```

A bounded CPU-only weight-transfer probe tested the obvious next primitive
change: stronger hip-roll/lift pulses. It also failed:

```text
artifact: outputs/analysis/TARGET_GENERATOR_WEIGHT_TRANSFER_PROBE.md
score_100: outputs/analysis/TARGET_OBJECTIVE_SCORE_WEIGHT_TRANSFER_PROBE_100.md
score_150: outputs/analysis/TARGET_OBJECTIVE_SCORE_WEIGHT_TRANSFER_PROBE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

The top candidates had more single-support time than the previous sustained
dynamic-roll gate, but still almost no forward progress:

```text
100 ticks:
  top seed vx: 0.0045 / 0.0043 m/s

150 ticks:
  top seed vx: 0.0018 / 0.0035 m/s
```

Do not repeat this exact primitive-family probe. The next generator change
should explicitly couple support transfer to forward displacement, for example
by searching over stance push-off timing, pelvis/body lean timing, or a
closed-loop teacher that adjusts targets based on body velocity/contact state.

The first stance-push extension was implemented and tested:

```text
tool flags:
  --stance-push-amps
  --stance-ankle-scales

artifact: outputs/analysis/TARGET_GENERATOR_STANCE_PUSH_PROBE.md
score_100: outputs/analysis/TARGET_OBJECTIVE_SCORE_STANCE_PUSH_PROBE_100.md
score_150: outputs/analysis/TARGET_OBJECTIVE_SCORE_STANCE_PUSH_PROBE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

This still failed:

```text
100 ticks:
  top seed vx: 0.0089 / 0.0108 m/s

150 ticks:
  top seed vx: 0.0028 / 0.0061 m/s
```

Do not repeat open-loop sinusoid variants as the main strategy. The next
generator should be closed-loop/phase-aware and should use body velocity,
pitch, and foot contact state to decide stance push-off rather than applying a
fixed stance offset.

A first velocity-feedback stance-push hook was also tested:

```text
tool flags:
  --velocity-push-gains
  --velocity-push-limit

artifact: outputs/analysis/TARGET_GENERATOR_VELOCITY_FEEDBACK_PROBE.md
score_100: outputs/analysis/TARGET_OBJECTIVE_SCORE_VELOCITY_FEEDBACK_PROBE_100.md
score_150: outputs/analysis/TARGET_OBJECTIVE_SCORE_VELOCITY_FEEDBACK_PROBE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

It still failed:

```text
100 ticks:
  top seed vx: 0.0070 / 0.0061 m/s

150 ticks:
  top seed vx: 0.0031 / 0.0058 m/s
```

Do not keep adding scalar terms to this sinusoid primitive as the main path.
The next implementation should be a structurally different target generator or
teacher that plans contact phase, body lean/pitch, and stance push together.

The later closed-loop teacher/optimizer sequence refined the same decision:

```text
optimizer displacement probe:
  HOLD_OPTIMIZER_NO_ROBUST_TARGET
  best local dx: -0.0070 / 0.0030 m

forward-intent teacher:
  HOLD_NO_SEED_ROBUST_TARGETS
  top 100-tick local dx: 0.0518 / 0.0420 m
  top 100-tick vy95: 0.1917 / 0.1859 m/s

lateral-refined forward-intent teacher:
  HOLD_NO_SEED_ROBUST_TARGETS
  top scored 100-tick local dx: 0.0261 / 0.0371 m
  top scored 150-tick local dx: 0.0411 / 0.0372 m

CoM / stance-relative controller:
  HOLD_NO_SEED_ROBUST_TARGETS
  best controlled 100-tick local dx: 0.0254 / 0.0209 m
  sagittal/ankle push-off did not improve the result
```

The current target-source conclusion is:

```text
forward displacement can be forced, but current target families do it through
lateral momentum; when lateral motion is controlled, forward displacement
collapses.
```

The next target-source branch is specified in:

```text
docs/CONTACT_TIMED_REFERENCE_SNIPPETS_PLAN.md
```

It should preserve useful 50-tick dynamic-roll contact timing, regenerate
longer envelope-aware snippets, and score them over 100-150 ticks before any
new PPO/BC run.

Before another CUDA PPO/BC run, require a structurally different
contact/weight-transfer objective or controller that can pass the 100-150 tick
target gate. Do not run another nearby teacher-grid expansion as training
preparation.

The first-pass contact-timed audit closed the current dynamic-roll fragment
path:

```text
tool: tools/build_contact_timed_reference_snippets.py
artifact: outputs/analysis/CONTACT_TIMED_REFERENCE_SNIPPETS.md
status: HOLD_SOURCE_FRAGMENTS_DOUBLE_SUPPORT
single_support_pct_mean: 7.33%
double_support_pct_mean: 92.67%
```

The aggregate replay with exported traces also held:

```text
replay: outputs/analysis/CONTACT_TIMED_REFERENCE_SEQUENCE_REPLAY.md
score_100: outputs/analysis/CONTACT_TIMED_REFERENCE_SEQUENCE_SCORE_100.md
score_150: outputs/analysis/CONTACT_TIMED_REFERENCE_SEQUENCE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Next training prerequisite:

```text
build a target source that explicitly creates single-support / weight-transfer
timing; do not train from the existing 50-tick dynamic-roll fragments.
```

A bounded single-support-biased open-loop primitive probe also failed:

```text
artifact: outputs/analysis/TARGET_GENERATOR_SINGLE_SUPPORT_PROBE.md
score_100: outputs/analysis/TARGET_GENERATOR_SINGLE_SUPPORT_PROBE_SCORE_100.md
score_150: outputs/analysis/TARGET_GENERATOR_SINGLE_SUPPORT_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

The best scored windows still had roughly 95-98% double support and low forward
velocity. Do not launch another BC/PPO run from nearby open-loop lift-pulse /
roll-assist / stance-push grids. The next source must be state-aware and must
make support transfer a gate, not an incidental byproduct.

The first support-readiness-gated controller also held:

```text
tool flag: --gate-swing-on-ready
artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SUPPORT_GATED_PROBE.md
score_100: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SUPPORT_GATED_SCORE_100.md
score_150: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SUPPORT_GATED_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

It created more single-support time but froze forward motion. The next target
source must actively drive load shift/readiness and then push; do not treat a
passive readiness gate as a training-ready reference.

Stateful phase variants also held:

```text
strict:
  artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_STRICT_PROBE.md
  score_100: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_STRICT_SCORE_100.md
  score_150: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_STRICT_SCORE_150.md
  status: HOLD_NO_SEED_ROBUST_TARGETS

timeout:
  artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_TIMEOUT_PROBE.md
  score_100: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_TIMEOUT_SCORE_100.md
  score_150: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_TIMEOUT_SCORE_150.md
  status: HOLD_NO_SEED_ROBUST_TARGETS
```

Do not spend the next GPU run on phase-state plumbing around the same stance
push primitive. The missing target source now appears to be the propulsion /
foot-placement model itself.

A first finite-horizon random-shoot sequence optimizer is now available:

```text
tool: tools/optimize_contact_weight_transfer_sequence.py
artifact: outputs/analysis/CONTACT_WEIGHT_TRANSFER_SEQUENCE_OPTIMIZER.md
status: HOLD_HORIZON_SEQUENCE_NO_ROBUST_TARGET
```

The initial bounded CPU pass confirmed the instrument works but found no
seed-robust target. It should be used for reviewed structural target-source
experiments only. Do not treat it as permission to launch BC/PPO unless a
100-150 tick target gate passes.

The current compact handoff docs are:

```text
docs/SIM2REAL_FINDINGS_DIGEST.md
docs/WEIGHT_TRANSFER_OBJECTIVE_BRIEF.md
docs/COM_WEIGHT_TRANSFER_CONTROLLER_PLAN.md
docs/CONTACT_TIMED_REFERENCE_SNIPPETS_PLAN.md
docs/TARGET_SOURCE_EXIT_DECISION.md
```

The first learning-objective probe after the target-source exit is:

```text
recipe: movement_bootstrap_v23
planner: tools/plan_staged_curriculum_training.py
new hooks:
  --forward-single-support-scale
  --forward-double-support-scale
status: plan-only / not trained
```

V23 uses the companion Playground support-contact reward hooks to test explicit
single-support weight transfer at x=0.04. Keep this branch offline until the
plan is reviewed. Do not reintroduce x=0.08, fitted bridge, or robot validation
unless the x=0.04 multi-seed gate shows coherent forward motion and useful
left/right single-support alternation.

First V23 run:

```text
artifact: outputs/analysis/V23_L4_PARTIAL_RUN_SUMMARY.md
status: HOLD_V23_SUPPORT_OBJECTIVE_FAILED_GATE
training: completed and exported 184320-step ONNX
gate: seeds 0-5 all held with fall/termination
remote: Colab disappeared during seed 6, so the full 0-7 distribution is incomplete
```

The gate failure is still decisive because the configured pass condition allowed
no failed seeds. Do not rerun V23 unchanged. Before another long cloud run,
analyze at least one V23 fall trace for contact sequence, base height, pitch,
local velocity, support dwell, and termination reason.

Recovered V23 package:

```text
artifact: outputs/analysis/V23_L4_ARTIFACT_RECOVERY_SUMMARY.md
status: HOLD_V23_ARTIFACT_RECOVERED_GATE_FAILED
final ONNX sha256: d8a92162cfee07cb4c6f2643c5206a182882fd46c0098f93a1c65c03e99c86c7
```

The recovered candidate fails seed-0 `x=0.0` and `x=0.08` gates. At `x=0.08`
it stays far below the measured actuator velocity envelope and has 0% action
saturation, but local-frame forward velocity is negative and all bridge modes
terminate with `fall_or_nan`. Treat this as evidence that the first explicit
support-contact reward is insufficient, not as a reason to rerun V23 unchanged.

Targeted V23 trace:

```text
artifact: outputs/analysis/V23_SEED0_X004_TRACE_SUMMARY.md
status: HOLD_DOUBLE_SUPPORT_STANDSTILL
command: x=0.04
seed: 0
bridge: vanilla
samples: 750
contact pattern: 99.33% double support
mean local vx: -0.0002 m/s
```

This confirms the failure mode: V23 learned a stable double-support standstill,
not alternating support transfer. The next recipe should not be an unchanged V23
rerun or a nearby scalar-weight tweak. It needs support transition plus forward
propulsion as a coupled objective or a closed-loop teacher that enforces stance
side, foot placement, and body placement.

V24 plan:

```text
artifact: outputs/analysis/MOVEMENT_BOOTSTRAP_V24_TRANSITION_PROPULSION_PLAN.md
status: DRY_RUN / not trained
recipe: movement_bootstrap_v24
```

V24 adds default-off Playground terms for transition-coupled support:

```text
forward_contact_transition:
  rewards landing transitions only when local forward velocity reaches a
  command-normalized minimum progress ratio

forward_double_support_dwell:
  penalizes prolonged double-support dwell during forward commands after a
  short grace window
```

Do not run V24 unless the plan is reviewed. It is still a sim-only x=0.04 probe;
robot validation remains blocked.

First V24 run:

```text
artifact: outputs/analysis/V24_L4_PARTIAL_RUN_SUMMARY.md
status: HOLD_V24_TRANSITION_PROPULSION_FAILED_GATE
training: PASS_SMOKE_RUN
final ONNX sha256: 84bc62cffb5972711769dc4be73c7bcfc1986795d8482cc6c0b2a976d27cbf58
gate: x=0.04, vanilla bridge
recovered seeds:
  seeds 0-5: HOLD_CANDIDATE_FALL_OR_TERMINATION
  seeds 6-7: not recovered before Colab runtime disappeared
remote: HOLD_REMOTE_NO_SENTINEL
```

The recovered V24 seeds still failed with near-zero or reverse local forward
velocity, low pitch-chain target velocities, and 0% action saturation. This is
not an actuator-envelope hold.

Reward-term activation audit:

```text
tool: tools/audit_reward_term_activation.py
artifact: outputs/analysis/V24_REWARD_TERM_ACTIVATION_AUDIT.md
status: HOLD_REWARD_TERMS_MISSING
missing configured terms:
  forward_contact_transition
  forward_double_support
  forward_double_support_dwell
  forward_single_support
```

This means the recovered eval artifacts prove the candidate failed behaviorally,
but they do not prove the newly configured transition/dwell terms were observed
in the reward-term trace.

Do not rerun V24 unchanged. The next branch should be structurally different:
either a stronger closed-loop teacher / optimizer with explicit stance side,
body placement, foot placement, and push timing, or an imitation/demonstration
path that can hold a coherent single-support stepping behavior before PPO
tries to refine it. Also require reward-term activation/observability for any
new contact objective before trusting another long cloud run.
