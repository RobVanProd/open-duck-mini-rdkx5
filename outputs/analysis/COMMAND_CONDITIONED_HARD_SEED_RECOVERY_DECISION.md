# Command-Conditioned Hard-Seed Recovery Decision

status: `HOLD_X0_SEED5_STILL_FAILS`

Purpose: test whether adding the warm-start baseline's hard-seed x=0.08
recovery traces to the existing command-conditioned standstill/moving dataset
produces a portable PPO-compatible student that both stands at x=0.0 and moves
at x=0.08.

This is offline analysis only. It did not train PPO, deploy, SSH, run robot
tests, or change robot runtime behavior.

## Dataset

Manifest:

```text
outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_MANIFEST.md
```

Inputs:

```text
stable x=0.0 labels:
  outputs/analysis/scale0p75_x0_full_obs_traces/scale0p75/seed_*/trace.jsonl

rate-limited x=0.08 moving labels:
  outputs/analysis/source_vx_pitch_chain_rate_limited_2p25_traces/seed_*.jsonl

baseline hard-seed x=0.08 recovery labels:
  outputs/analysis/behavior_preserving_recovery_finetune/seed1_seed7_trace_compare/baseline/seed_*/trace.jsonl
  outputs/analysis/behavior_preserving_recovery_finetune/seed3_trace_compare/baseline/seed_*/trace.jsonl
```

Manifest summary:

```text
status: PASS_BC_TRACE_MANIFEST_READY
entries: 19
samples: 10250
bc_ready_entries: 19
```

## Supervised Fit

Artifact:

```text
outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_BC_STUDENT.md
```

Result:

```text
status: PASS_PPO_LOC_BC_FIT_SMOKE
p95 action error: 0.024773
target-rate p95: 1.736061 rad/s
target-rate max: 2.759758 rad/s
```

## Closed-Loop Gates

x=0.0, canonical backlash, fitted bridge, 10 seconds:

```text
artifact: outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_X0_FITTED_10S.md
duration complete: 7 / 8
falls: 1
failing seed: 5 at 73 samples
mean vx: -0.0275 m/s
```

x=0.08, canonical backlash, fitted bridge, 10 seconds:

```text
artifact: outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_X008_FITTED_10S.md
duration complete: 8 / 8
falls: 0
mean vx: 0.0346 m/s
mean track ratio: 0.4329
max pitch-chain target velocity p95: about 2.03-2.09 rad/s
hold reason: tracking
```

## Interpretation

The hard-seed recovery labels improve the previous command-conditioned BC line:

```text
- x=0.08 remains stable across all eight seeds
- x=0.08 target rates stay under the fitted velocity envelope
- prior x=0 hard seed 3 now completes
```

But the candidate is still not deployable:

```text
- x=0.0 seed 5 falls at 73 samples
- the failure is command-specific, because the same seed completes at x=0.08
- x=0.08 still holds on tracking rather than passing
```

## Seed-5 Trace Comparison

Artifact:

```text
outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_SEED5_X0_VS_X008_TRACE_COMPARE.md
```

The same candidate and seed were traced at `x=0.0` and `x=0.08` with full
observations. The `x=0.0` rollout falls after 73 samples, while the `x=0.08`
rollout completes 10 seconds.

Key differences:

```text
x=0.0 seed 5:
  duration: 1.46 s
  vx_mean: -0.2176 m/s
  vx_p05: -1.2001 m/s
  abs_pitch_p95: 1.2413 rad
  base_height_min: 0.0464 m
  double_support: 79.45%

x=0.08 seed 5:
  duration: 10.00 s
  vx_mean: 0.0371 m/s
  vx_p05: -0.0187 m/s
  abs_pitch_p95: 0.1283 rad
  base_height_min: 0.1462 m
  double_support: 69.80%
```

The first measurable divergence is early:

```text
local_vx:   tick 7  / 0.14 s
local_vy:   tick 16 / 0.32 s
body_pitch: tick 20 / 0.40 s
base_y:     tick 29 / 0.58 s
base_x:     tick 43 / 0.86 s
height:     tick 67 / 1.34 s
```

This makes the current blocker narrower than generic hard-seed instability:
`x=0.0` seed 5 selects an early reverse/pitch-collapse behavior, while the
same seed under `x=0.08` selects a survivable forward-moving behavior. The next
offline fix should add targeted `x=0.0` seed-5 corrective labels or relabeling
without weakening the `x=0.08` recovery behavior.

## Seed-5 Failure Mode Analysis

Artifacts:

```text
outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_SEED5_X0_FAILURE_ANALYSIS.md
outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_X0_PASS_TRACE_GATE.md
outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_SEED5_X0_VS_SEED0_X0_TRACE_COMPARE.md
outputs/analysis/COMMAND_CONDITIONED_HARD_SEED_RECOVERY_SEED5_X0_VS_SEED3_X0_TRACE_COMPARE.md
```

The seed-5 failure was analyzed against the current manifest and BC model:

```text
status: HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY
nearest manifest distance p95: 1.8015
nearest action L1 p95: 0.0820
target velocity p95: 0.7501 rad/s
joint tracking p95: 0.0803 rad
```

This is not a simple out-of-distribution trace or large supervised action-fit
miss. The trace has nearby manifest support and modest nearest-action gap, but
the closed-loop rollout still enters reverse motion and pitch collapse.

Passing x=0 comparison traces:

```text
seed 0: PASS, 10 s, vx_mean 0.0003, body_pitch_p95 0.0239, tracking_p95 0.0754
seed 3: PASS, 10 s, vx_mean -0.0056, body_pitch_p95 0.0331, tracking_p95 0.0724
```

Compared with passing x=0 seeds, failing seed 5:

```text
uses less quiet double support:
  seed 5 fail: 79.45%
  seed 0 pass: 98.40%
  seed 3 pass: 98.80%

has much larger pitch and reverse velocity:
  seed 5 vx_mean: -0.2176
  seed 5 abs_pitch_p95: 1.2413
  seed 5 base_height_min: 0.0464
```

The divergence from passing seeds appears at or near the initial samples in
velocity, lateral motion, and pitch. That makes the next corrective branch a
zero-command hard-seed stabilization problem: keep seed 5 in quiet support at
`x=0.0` without globally scaling down the action path that preserves `x=0.08`
motion.

## Decision

Do not promote this ONNX to robot validation or longer gates.

The next offline step should target the x=0.0 seed-5 failure specifically while
preserving the x=0.08 recovery behavior. Useful options:

```text
1. add or relabel seed-5 x=0.0 recovery/standstill data
2. compare x=0 seed-5 trace against the passing x=0 seeds and the x=0.08 seed-5 trace
3. build a smaller corrective dataset around x=0 hard-seed stability instead of adding more generic x=0.08 motion
```

Robot validation remains blocked.
