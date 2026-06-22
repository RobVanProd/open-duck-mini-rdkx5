# Candidate Policy Validation Gates

Last updated: 2026-06-22

## Purpose

This document defines the gates a newly trained Open Duck Mini policy must pass
before it is considered for robot-side suspended validation.

The current project target is not "make any policy that walks in sim." The
target is a policy compatible with the RDK-X5 runtime contract:

```text
observation: state[101]
action: 14 joints
action order: left leg, neck/head, right leg
runtime target: home + action * action_scale
```

## Current Baseline Finding

`BEST_WALK_ONNX_2` is no longer suspected of having a gross joint-map or IMU
contract failure. The leading failure is dynamic actuator mismatch:

```text
suspended x=0.08 real robot:
  pitch-chain target waveform too fast
  sustained 3-4 tick lag
  p95 pitch tracking roughly 0.12-0.17 rad

closed-loop sim with fitted actuator bridge:
  PASS_CLOSED_LOOP_REPRODUCTION on CUDA L4
```

Local `7900 XTX` ROCm/MJX remains a backend workstream:

```text
tracking issue: https://github.com/RobVanProd/open-duck-mini-rdkx5/issues/19
```

## Training Preconditions

Before any candidate training run:

- Playground contract audit must report `state[101]` and `action_size=14`.
- Actuator order must match `BEST_WALK_ONNX_2`.
- The actuator bridge must be disabled by default.
- Training must explicitly enable the actuator bridge.
- Training config must record delay, tau, velocity-limit, and reward scales.
- `BEST_WALK_ONNX_2.onnx` must not be overwritten.
- Raw training logs/checkpoints must not be committed by default.

## Sim-Side Candidate Gates

A candidate can move to robot-side suspended validation only if it passes all
reviewed sim-side gates:

| gate | required result |
|---|---|
| contract | `state[101] -> action[14]` |
| actuator bridge | enabled with reviewed ranges |
| action saturation | no sustained bursts |
| target velocity | p95/p99 reduced versus `BEST_WALK_ONNX_2` x=0.08 baseline |
| simulated pitch tracking | p95 preferably `<0.05 rad`, acceptable `<0.08 rad` |
| post-startup tracking | no sustained pitch-chain error `>0.10 rad` |
| gait stability | stable at `x=0.00`, `x=0.04`, and `x=0.08` in sim |
| reward | no obvious frozen or collapsed gait exploit |
| metadata | ONNX hash, config, seed, and eval summary saved |

## Required Offline Artifacts

For each candidate, save small summaries:

```text
outputs/analysis/<candidate>_contract.md
outputs/analysis/<candidate>_target_velocity.md
outputs/analysis/<candidate>_actuator_bridge_eval.md
outputs/analysis/<candidate>_policy_metadata.json
```

Large training checkpoints, raw TensorBoard logs, and videos should stay outside
git unless explicitly approved.

## Candidate Naming

Do not overwrite the baseline policy.

Use a new name such as:

```text
policy/candidates/open_duck_mini_actuator_bridge_<YYYYMMDD>_<shortsha>.onnx
```

Record:

- source Playground commit
- source RDK tools commit
- training command
- config overrides
- seed
- ONNX SHA256

## Robot-Side Validation Order

Robot tests require Rob physically present and explicit approval.

Run only after the sim-side candidate gates are reviewed:

1. suspended replay, `x=0.0`
2. suspended replay, `x=0.08`
3. grounded replay only if suspended dynamic tracking passes

Robot-side pass gates:

- pitch-chain p95 tracking preferably `<0.05 rad`
- pitch-chain p95 tracking acceptable `<0.08 rad`
- no sustained post-startup pitch tracking error `>0.10 rad`
- no action saturation bursts
- no repeated write errors
- CRC read retries are warning-only unless correlated with control damage
- visually coherent and symmetric suspended gait

Grounded replay remains blocked until suspended validation passes.

## Non-Goals

- Do not tune hardware gains as the primary fix.
- Do not change joint offsets or IMU remaps for a candidate policy.
- Do not change action scale or phase timing as part of candidate export.
- Do not claim TPU/friction is fixed until suspended dynamic tracking is clean.
