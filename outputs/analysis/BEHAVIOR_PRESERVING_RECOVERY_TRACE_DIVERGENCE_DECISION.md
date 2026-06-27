# Behavior-Preserving Recovery Trace Divergence Decision

status: `HOLD_SMALL_PPO_REWARD_PRIOR_LOOP`

Purpose: explain why the support-transition and behavior-prior PPO smoke
branches should not continue as nearby scalar tweaks.

This is offline analysis only. It did not SSH, deploy, touch the robot, change
runtime behavior, or overwrite any policy.

## Compared Policies

Baseline warm start:

```text
outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0.onnx
```

Behavior-prior smoke export:

```text
/tmp/open_duck_behavior_preserving_recovery/smoke_20260627T035024Z_cpu/2026_06_26_235105_1040.onnx
```

Gate:

```text
task: flat_terrain_backlash
bridge: fitted actuator bridge
command_x: 0.08
duration: 15 s
```

## Trace Artifacts

Seed trace sweeps:

```text
outputs/analysis/BEHAVIOR_PRESERVING_RECOVERY_SEED3_TRACE_COMPARE.md
outputs/analysis/BEHAVIOR_PRESERVING_RECOVERY_SEED1_SEED7_TRACE_COMPARE.md
```

Per-seed divergence summaries:

```text
outputs/analysis/BEHAVIOR_PRESERVING_RECOVERY_SEED1_TRACE_DIVERGENCE.md
outputs/analysis/BEHAVIOR_PRESERVING_RECOVERY_SEED3_TRACE_DIVERGENCE.md
outputs/analysis/BEHAVIOR_PRESERVING_RECOVERY_SEED7_TRACE_DIVERGENCE.md
```

Raw trace JSONL files are intentionally left out of git.

## Findings

Seed 3 is the early-collapse split:

```text
baseline:        duration complete, vx 0.0293 m/s, track ratio 0.3661
behavior smoke:  fall at 74 samples, vx -0.2708 m/s, track ratio -3.3845
```

The behavior-smoke trace diverges from baseline before the fall:

```text
local_vx divergence:   tick 15 / 0.30 s
body_pitch divergence: tick 23 / 0.46 s
base_y divergence:     tick 37 / 0.74 s
base_height collapse:  tick 69 / 1.38 s
```

So the fall is not a late actuator-rate or tracking-envelope event. It is an
early closed-loop state/action divergence that becomes a reverse/pitch collapse.

Seeds 1 and 7 are the motion-suppression split:

```text
baseline seeds 1/7:
  mean vx: 0.0335 / 0.0374 m/s
  double support: 66.7% / 65.2%
  single support: about 33%

behavior-smoke seeds 1/7:
  mean vx: -0.0014 / 0.0001 m/s
  double support: 98.4% / 98.8%
  single support: about 1-2%
```

The behavior-smoke policy keeps height and posture by staying in double support
and almost entirely suppressing the gait. This also increases mean reward
relative to the baseline on these seeds, which confirms that the local reward
landscape still permits a stable no-step solution.

## Decision

Do not continue with nearby scalar edits to:

```text
support/contact reward weights
small behavior-prior weights
small target-rate/tracking weights
```

Both tiny PPO branches found the same easier basin:

```text
reduce motion -> reduce pitch/tracking stress -> lose forward gait
```

The next useful branch must change the supervision/data structure, not just the
scalar weights.

## Recommended Next Branch

Prefer a targeted closed-loop recovery dataset or trainer update:

```text
1. Generate short on-policy traces from the baseline warm start for seeds 1, 3, and 7.
2. Preserve the baseline's single-support/motion pattern as positive behavior.
3. Add recovery labels or rollouts only around the early divergence windows:
   - seed 3: ticks 10-75, reverse/pitch-collapse recovery
   - seeds 1/7: ticks 10-120, avoid double-support freeze
4. Train/evaluate against the matched baseline, not just absolute pass/fail.
5. Reject any candidate that improves tracking by reducing x=0.08 vx or
   single-support time.
```

If that branch is too large, the smaller next step is to build an offline
dataset manifest from the traced windows and score whether candidate labels
preserve:

```text
local_vx > 0
single-support fraction
base height
pitch-chain target-rate envelope
```

Robot validation remains blocked.
