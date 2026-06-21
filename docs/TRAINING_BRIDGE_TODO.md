# Training Bridge TODO

Last updated: 2026-06-21

Purpose: convert the measured Open Duck Mini actuator evidence into small,
reviewable sim/training changes. Do not retrain blindly and do not change
robot runtime behavior as part of these items unless a later PR explicitly
requests a reviewed runtime experiment.

## P0: Inspect Current Training Contract

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

## P1: Add Actuator Model Controls

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

### Acceleration / Jerk Limit

- Add optional target acceleration and jerk clipping.
- Keep it configurable so experiments can isolate velocity limit vs lag vs
  jerk effects.

## P2: Reward And Curriculum

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

### Command Curriculum

Train/evaluate in stages:

```text
x = 0.00 -> 0.04 -> 0.08 -> higher
```

Do not export a robot candidate unless `x=0.08` passes sim-side actuator
robustness gates.

## P3: Evaluation And Export

### Target Velocity Evaluation Script

- Add a sim-side equivalent of `tools/analyze_policy_target_velocity.py`.
- Report target velocity, action deltas, rate-limit activation, and simulated
  actuator tracking error per joint.
- Include pitch-chain summary by default.

### Short Training Experiment

- Train with the actuator model enabled.
- Compare against a baseline with the current actuator assumptions.
- Save:
  - config
  - random seed
  - evaluation summaries
  - policy hash
  - target velocity metrics

### Candidate ONNX Export

- Export only after sim-side gates pass.
- Store policy metadata and hash.
- Do not overwrite `BEST_WALK_ONNX_2.onnx`.

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
