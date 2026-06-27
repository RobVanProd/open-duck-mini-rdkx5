# Command-Conditioned x=0.08 Relabel Weight-3 Decision

status: `HOLD_X008_RELABEL_WEIGHT3_REGRESSES_FORWARD_PROGRESS`

## Purpose

Test whether a small DAgger correction on the current best command-conditioned
candidate can improve the remaining x=0.08 fitted-bridge tracking hold without
touching the robot.

This was offline only. It did not SSH, deploy, run robot tests, train PPO, or
change runtime behavior.

## Trace Collection

Current best candidate:

```text
outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate/candidate.onnx
```

Traced x=0.08 fitted-bridge seeds 0 and 5 with full observations:

```text
artifact: outputs/analysis/COMMAND_CONDITIONED_SEED5_X0_X008_TRACE_FOR_DAGGER.md
status seed 0: HOLD_CANDIDATE_TRACKING
status seed 5: HOLD_CANDIDATE_TRACKING
```

Both rollouts completed 10 seconds without falling, reproduced the known
tracking-limited behavior, and produced 1000 BC-ready samples.

## Relabel

The traces were relabeled with the existing command-conditioned DAgger seed-5
blend teacher:

```text
artifact: outputs/analysis/COMMAND_CONDITIONED_X008_RELABEL_SEED0_SEED5.md
status: PASS_BC_TRACE_RELABEL_READY
samples_out: 1000
```

Action deltas were modest:

```text
seed 0 action_delta_p95: 0.0394
seed 5 action_delta_p95: 0.0542
```

This indicates the existing teacher mostly agrees with the current student on
these x=0.08 tracking-limited states. That makes this a weak correction signal.

## Fit

The original command-conditioned manifest was merged with the relabeled x=0.08
traces and the relabeled traces were upweighted 3x:

```text
artifact: outputs/analysis/COMMAND_CONDITIONED_X008_RELABEL_WEIGHTED_MANIFEST.md
weighted_samples: 13250
```

A 512/256/128 swish MLP was fit with the same target-rate regularizer:

```text
artifact: outputs/analysis/COMMAND_CONDITIONED_X008_RELABEL_WEIGHT3_BC_STUDENT.md
candidate: outputs/analysis/command_conditioned_x008_relabel_weight3_candidate/candidate.onnx
train_p95_abs_error: 0.0364
pred_action_saturation_pct: 0
```

The supervised fit is worse than the current best command-conditioned student
(`0.0364` p95 action error vs `0.0242`).

## Compact Gate Sweep

The compact fitted-bridge checkpoint sweep compared the current best candidate
against the relabel-weighted candidate:

```text
artifact: outputs/analysis/COMMAND_CONDITIONED_X008_RELABEL_WEIGHT3_CHECKPOINT_SWEEP.md
status: no promoted checkpoint
```

Result:

```text
best x=0.08:
  mean vx: 0.0223
  track ratio: 0.2793
  max tracking p95: 0.2219

relabel_weight3 x=0.08:
  mean vx: -0.0172
  track ratio: -0.2154
  max tracking p95: 0.2175
```

The relabel-weighted candidate slightly reduced the compact tracking metric but
regressed into backward motion. It is not a candidate and should not receive a
full gate or PPO warm start.

## Decision

Do not continue this exact x=0.08 relabel/upweight branch.

The correction signal is too close to the existing student action on the
visited states, and upweighting it damages forward progress. The remaining
tracking hold is unlikely to be solved by another small static DAgger relabel
against the same teacher.

Next offline work should use a mechanism that changes closed-loop dynamics
rather than reweighting nearly identical labels:

```text
- gate-selected PPO checkpoints, now wired in the Colab workflow
- explicit tracking/actuator-state feedback during training
- a stronger teacher that actually differs on tracking-limited states
- or revisit physical raw-home offset audit once the robot is reachable
```

Robot validation remains blocked.
