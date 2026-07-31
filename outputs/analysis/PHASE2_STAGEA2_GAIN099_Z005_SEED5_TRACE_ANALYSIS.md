# Phase 2 Stage-A2 Gain-0.99 z=0.005 Seed-5 Trace Analysis

status: `HOLD_TERRAIN_Z005_SEED5_BACKWARD_PITCH_COLLAPSE`

## Scope

This is an offline CPU sim trace analysis only. No robot tests, SSH, deploy,
grounded replay, runtime behavior changes, or policy overwrite were performed.

## Candidate

```text
candidate:
  policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx

candidate_sha256:
  209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b
```

## Trace

```text
source:
  outputs/analysis/phase2_stagea2_gain099_z005_seed5_trace_cpu/gain099/seed_005/trace.jsonl

configuration:
  task: rough_terrain_backlash
  terrain_hfield_z_scale: 0.005
  command_x: 0.08
  bridge: fitted corrected knee bridge
  seed: 5
  duration: 15 s
  pushes: disabled
  policy_action_gain: 1.0
  JAX platform: cpu
```

The rollout reproduced the z=0.005 boundary hold:

```text
samples:       56
last tick:     55
termination:   fall_or_nan
```

## Failure Shape

The failure is a backward pitch/support collapse, not an actuator-envelope
violation.

```text
base height min:       0.0677 m at tick 55
body pitch min:       -1.4489 rad at tick 54
body pitch last:      -1.4184 rad
mean local vx:        -0.2654 m/s
last local vx:        -1.4738 m/s
mean local vy:        -0.0109 m/s
last local vy:        -0.2010 m/s
```

Contact state before termination:

```text
double support:       91.1%
single support:        7.1%
no contact:            1.8%

contact counts:
  11: 51
  10: 3
  01: 1
  00: 1
```

The first 10 ticks include forward motion, then the rollout reverses:

| window | ticks | mean vx | min vx | max vx | mean pitch | max abs pitch | contact shape |
|---|---:|---:|---:|---:|---:|---:|---|
| first10 | 0-9 | 0.1165 | -0.0194 | 0.2222 | -0.1292 | 0.2283 | mixed |
| 10-30 | 10-29 | -0.0473 | -0.0742 | -0.0285 | -0.2245 | 0.2760 | all double support |
| 30-end | 30-55 | -0.5802 | -1.4738 | -0.0960 | -0.6907 | 1.4489 | mostly double support |
| last10 | 46-55 | -1.0483 | -1.4738 | -0.6142 | -1.1138 | 1.4489 | mostly double support |

## Actuator Check

The corrected actuator gate stayed clean during the failing trace:

```text
max pitch-chain sent velocity p95:     1.9284 rad/s
max pitch-chain applied velocity p95:  1.6040 rad/s
max pitch-chain tracking p95:          0.1533 rad
corrected envelope excess:             0.0000 rad/s
```

Per pitch-chain p95 tracking stayed below the `0.20 rad` gate:

| joint | tracking p95 | sent vel p95 | applied vel p95 |
|---|---:|---:|---:|
| left_hip_pitch | 0.0653 | 1.4375 | 1.4285 |
| left_knee | 0.1410 | 1.9284 | 1.6040 |
| left_ankle | 0.0887 | 1.0511 | 0.9232 |
| right_hip_pitch | 0.1418 | 1.1811 | 0.9347 |
| right_knee | 0.1533 | 1.8312 | 1.3775 |
| right_ankle | 0.0985 | 1.6012 | 1.3027 |

## Decision

Do not widen the actuator envelope or increase global action gain as the next
response. The z=0.005 seed-5 hold is a rough-terrain contact/support timing
boundary:

- the policy stays mostly in double support,
- the body reverses after the first few ticks,
- backward pitch grows rapidly after tick 30,
- collapse happens while target velocity and p95 tracking remain inside the
  corrected bridge gate.

Next Phase 2 work should target seed-5 rough-terrain step/support margin between
`z=0.002` and `z=0.005`, with emphasis on escaping double support and preventing
backward pitch reversal. The current packaged gain-0.99 candidate remains the
best reviewed `z=0.002` rough-terrain gentle-push offline candidate.
