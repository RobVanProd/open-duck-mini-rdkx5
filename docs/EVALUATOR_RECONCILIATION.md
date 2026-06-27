# Evaluator Reconciliation

Status: `PASS_EVALUATOR_CANONICAL`

This is the blocking Step 0 artifact for
`LIVE_ORACLE_DAGGER_PHASE_STUDENT`. It resolves the reported mismatch where
the BC smoke path showed `sent_vel95 ~= 2.2 rad/s` while the standard
task-matched evaluator showed `max_pitch_vel_p95 ~= 3.8 rad/s` for related
students.

## Finding

The discrepancy is primarily a metric-definition mismatch, not evidence that
the fitted bridge or sim stepping path is inconsistent.

Concrete comparison artifact:

```text
outputs/analysis/EVALUATOR_RECONCILIATION_METRIC_COMPARE.md
```

Representative historical pair:

```text
BC smoke max flattened sent_vel95:       2.2237 rad/s
canonical max pitch-joint sent_vel95:   4.2879 rad/s
canonical max pitch tracking p95:       0.2794 rad
```

This reproduces the observed "pass smoke / hold standard" split without
requiring a different simulator, policy contract, bridge insertion point, or
frame timing. The BC smoke metric masked pitch-joint envelope violations by
flattening all joints and all ticks into one percentile.

The BC smoke path reports:

```text
sent_target_velocity_p95_rad_s = p95(flatten(abs(diff(sent_target)) / dt))
```

over all joints and all ticks in the rollout.

The strict candidate path reports:

```text
max_pitch_vel_p95 = max(per-joint p95(abs(diff(sent_target)) / dt))
```

over the pitch-chain joints only:

```text
left_hip_pitch
left_knee
left_ankle
right_hip_pitch
right_knee
right_ankle
```

A single pitch joint can therefore exceed the actuator envelope while the
flattened all-joint p95 remains much lower. For the hardware gate, the
per-joint pitch-chain maximum is the correct statistic because one overloaded
pitch joint is enough to recreate the real tracking failure.

## Path Audit

### BC Smoke Path

Entry point:

```text
tools/run_target_dataset_bc_smoke.py
```

Metric source:

```text
summarize_rollout(...)
sent_target_velocity_p95_rad_s:
  percentile(sent_velocity.reshape(-1), 95)
```

Properties:

- useful as a quick behavior-cloning replay smoke
- can run short windows and curated target datasets
- reports one flattened velocity percentile across all joints
- does not implement the promotion gate
- not canonical for deployability

### Standard Candidate Path

Entry point:

```text
tools/run_candidate_seed_sweep.py
```

Worker:

```text
tools/eval_policy_with_actuator_bridge.py --mode closed-loop-sim --eval-role candidate
```

Core sim implementation:

```text
tools/closed_loop_sim_eval.py
```

Metric source:

```text
classify_candidate_gate(...)
max_sent_target_velocity_p95_rad_s =
  max(p95(abs(diff(sent_target_j)) / dt) for j in pitch_chain)
```

Properties:

- instantiates the verified `101` observation / `14` action Playground env
- uses `flat_terrain_backlash` for the strict deployment-style gate
- inserts the actuator bridge at `target_stage_direct`
- records `sent_target_rad`, `applied_target_rad`, and
  `actual_position_rad`
- computes pitch-chain per-joint target velocity and tracking p95
- reports fall/termination and command tracking across explicit seeds
- canonical for branch gates and promotion decisions

## Obs Construction

The canonical evaluator uses the Playground environment observation directly:

```text
state.obs["state"]
```

Expected shape:

```text
obs[101]
```

The ONNX contract check rejects mismatched observation or action dimensions.
No padding or truncation is allowed.

## Bridge Insertion Point

The canonical evaluator inserts the fitted actuator bridge after runtime-style
target preparation and before MuJoCo stepping:

```text
action -> action delay -> home + action * action_scale
       -> runtime max_motor_velocity slew limit
       -> sent_target
       -> fitted bridge
       -> applied_target
       -> mjx_env.step(..., applied_target)
```

Recorded insertion point:

```text
target_stage_direct
```

This is the correct comparison point for the real robot evidence because the
real telemetry also distinguished sent target from achieved/actual position.

## Slew / Clip Application

The canonical path preserves the Playground runtime-style preparation:

```text
pre_rate_limit = default_actuator + delayed_action * action_scale
sent_target = clip(pre_rate_limit,
                   previous_motor_targets - max_motor_velocity * dt,
                   previous_motor_targets + max_motor_velocity * dt)
```

Then the fitted bridge transforms `sent_target` into `applied_target`.

Important distinction:

- `sent_target` velocity is the command burden placed on the actuator chain.
- `applied_target` velocity is the bridge-limited target sent into MJX.
- The strict envelope gate must constrain `sent_target` per pitch joint,
  because that is what exposed the real x=0.08 actuator lag.

## Frame Timing

The canonical evaluator uses the Playground control timestep:

```text
ctrl_dt = 0.02 s
sim_dt = 0.002 s
n_substeps = 10
```

Target velocity metrics use:

```text
abs(diff(sent_target)) / ctrl_dt
```

## Canonical Strict Evaluator

All `LIVE_ORACLE_DAGGER_PHASE_STUDENT` gates must use this command family:

```bash
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py \
  --policies label=path/to/candidate.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --command-x 0.08 \
  --duration 15 \
  --seeds 0-7 \
  --bridge-mode fitted \
  --task flat_terrain_backlash \
  --jax-platform cpu \
  --run
```

For zero-command semantics:

```bash
../envs/open-duck-playground/bin/python tools/run_candidate_seed_sweep.py \
  --policies label=path/to/candidate.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --command-x 0.0 \
  --duration 15 \
  --seeds 0-7 \
  --bridge-mode fitted \
  --task flat_terrain_backlash \
  --jax-platform cpu \
  --run
```

## Acceptance Metrics

Use the canonical evaluator output fields:

```text
duration_complete_count
fall_count
track_ratio.mean
max_pitch_vel_p95_rad_s.max
max_tracking_p95_rad.max
mean_local_vx_m_s.mean
```

For promotion, the strict x=0.08 branch gate is:

```text
duration_complete: 8/8
falls: 0/8
mean track ratio: >= 0.50
max pitch-chain sent velocity p95: <= 3.75 rad/s
max pitch-chain tracking p95: <= 0.20 rad
```

The x=0.0 semantic gate is:

```text
duration_complete: 8/8
falls: 0/8
mean |vx|: <= 0.005 m/s
```

## Decision

Use the standard candidate path as canonical:

```text
tools/run_candidate_seed_sweep.py
  -> tools/eval_policy_with_actuator_bridge.py
  -> tools/closed_loop_sim_eval.py
```

Do not promote, reject, or compare branch candidates using BC-smoke
`sent_vel95` alone. BC smoke remains useful for cheap fitting/debugging, but it
must be treated as a non-canonical replay diagnostic.

Gate result:

```text
PASS_EVALUATOR_CANONICAL
```
