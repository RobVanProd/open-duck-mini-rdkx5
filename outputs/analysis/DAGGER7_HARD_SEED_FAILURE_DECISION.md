# DAgger-7 Hard-Seed Failure Decision

status: `PLAN_SPLIT_SEED_RECOVERY_AND_STABILITY`

This is offline analysis only. No robot tests, SSH, deployment, runtime edits,
or PPO updates were performed.

## Context

DAgger-7 upweighted the seed-1 and seed-7 early-collapse recovery labels by
`50x`, but the resulting deployable MLP still failed both hard seeds around
tick `32`.

The failure is now split into two different mechanisms rather than one generic
BC failure.

## Evidence

Seed 1 against the DAgger-7 manifest:

```text
artifact: outputs/analysis/DAGGER6_SEED1_VS_DAGGER7_MANIFEST_FAILURE_ANALYSIS.md
status: HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY
samples: 32
termination tick: 31
base height min: 0.0775 m
target velocity p95: 2.1766 rad/s
joint tracking p95: 0.1751 rad
nearest action L1 p95: 0.0736
dominant contact: 10, 84.38%
last-10 vy grows to +1.3568 m/s
```

Interpretation: seed 1 has nearby manifest support and modest action mismatch.
The failure is not primarily "more labels needed"; it is a closed-loop
lateral/height instability under left single support.

Seed 7 against the DAgger-7 manifest:

```text
artifact: outputs/analysis/DAGGER6_SEED7_VS_DAGGER7_MANIFEST_FAILURE_ANALYSIS.md
status: HOLD_SEED_FAILURE_ACTION_MISMATCH
samples: 33
termination tick: 32
base height min: 0.0730 m
target velocity p95: 2.0073 rad/s
joint tracking p95: 0.1681 rad
nearest action L1 p95: 0.1290
dominant contact: 01, 84.85%
last-10 vy grows to -1.3233 m/s
```

Interpretation: seed 7 has nearby states but the local action fit is still too
far from the teacher. This is still a BC/local-fit problem around right single
support.

## Decision

Do not run another uniform-label-weight DAgger pass. The hard seeds require
different treatment:

```text
seed 1:
  closed-loop stabilization/contact objective
  reduce lateral velocity growth and height collapse during left support

seed 7:
  improve local teacher-action fit before PPO
  collect or fit a more precise right-support recovery mapping
```

Joint-level follow-up:

```text
artifact: outputs/analysis/DAGGER7_HARD_SEED_JOINT_ACTION_GAPS.md
seed 1 largest gap: right_knee p95 0.2234
seed 7 largest gaps: right_hip_pitch p95 0.1987, right_knee p95 0.1899
```

The next deployable-policy attempt should either:

1. add an explicit lateral-stability / base-height recovery term during
   closed-loop fine-tuning while preserving the DAgger-6/7 walking manifold, or
2. build a split hard-seed recovery dataset/model that treats seed 1 and seed 7
   separately instead of upweighting them with the same static BC rule.

## Stop Rule

Do not treat fall-count reduction as success if mean forward progress collapses.
The standard fitted-bridge x=0.08 gate remains:

```text
- duration complete across seeds
- meaningful positive vx / track ratio
- target velocity p95 inside measured envelope
- no hard-seed lateral/height collapse
```
