# V11 Reward Mechanics Audit

status: `HOLD_REWARD_MECHANICS_BEFORE_V12`
robot_touched: `false`
training_started: `false`

## Executive Summary

V11 trained successfully on the pinned A100 stack, but the final policy solved
`x=0.08` by standing almost still:

```text
mean local vx:       ~0.0009 m/s
track ratio:         ~0.011
samples:             750 / 750
action saturation:   0%
target velocity p95: <= 0.275 rad/s
```

This is not an actuator-envelope failure. It is a training/task objective
failure: positive-command no-motion remains a viable local optimum.

## Evidence

Primary artifacts:

```text
outputs/analysis/MOVEMENT_BOOTSTRAP_V11_A100_SUMMARY.md
outputs/analysis/V11_FORWARD_REWARD_LANDSCAPE.md
outputs/analysis/v11_forward_reward_landscape.json
```

V11 candidate:

```text
name: movement_bootstrap_v11_hard_progress_a100_20260624
onnx_sha256: a3f30d64f21334a5263df15d0b8c11576a04c4fe280c2a082cecb4e2038a13c7
x=0.0:  PASS_CANDIDATE_SIM_GATE
x=0.08: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
```

At `x=0.08`, the candidate completed the full 15 s closed-loop gate in vanilla,
fitted, and stress modes, but forward motion was near zero.

## Reward Path Findings

The Playground step path computes scaled terms, then clips the final reward:

```text
reward = clip(sum(scaled_reward_terms) * dt, 0.0, 10000.0)
```

Reference:

```text
../Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py:677
../Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py:681
```

Command-window progress is tracked separately:

```text
command_progress_distance += signed_vx * dt
command_progress_ratio = progress_distance / target_distance
command_progress_shortfall_cost = shortfall / target_distance shaped by pseudo-Huber
```

Reference:

```text
../Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py:495
../Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py:520
../Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py:523
```

V11 set hard progress terms in the staged plan:

```text
positive x commands only
forward_shortfall_huber_delta = 0
command_progress_shortfall_huber_delta = 0
forward_shortfall_scale = -36, -34, -30
command_progress_shortfall_scale = -50, -48, -42
alive_scale = 0.02
```

The scalar reward-landscape check confirms that, with those intended V11 scales,
zero velocity should be worse than moving at the target speed in the simple
per-tick formula. That means another blind increase to shortfall weights is not
the clean next move.

## Important Caveat

The closed-loop candidate gate reward-term table appears to use the default eval
reward configuration, not the V11 training override configuration. For example,
the gate reports:

```text
reward/alive mean: 20.0
reward/tracking_lin_vel mean: ~1.33
cost/stand_still mean: 0.0
```

Those numbers are useful for understanding the gate environment, but they should
not be treated as the exact V11 training reward decomposition. The behavior
metric is still decisive: V11 did not move at positive command.

## Interpretation

V11 shows that the current staged PPO setup can converge to no-motion even when
the scalar velocity reward terms prefer forward progress. The likely blockers
are task/optimization mechanics rather than a single small coefficient:

```text
1. Low progress does not terminate positive-command episodes.
2. Final reward clipping at zero may flatten bad low-progress regions.
3. Stable posture with tiny actions remains easy to discover.
4. The candidate gate does not replay the exact training reward config, so
   reward-term diagnostics can be misleading unless explicitly overridden.
5. The current training loop lacks a cheap per-phase freeze detector before
   committing later A100 phases.
```

## Recommendation

Do not launch V12 as another scale-only recipe. First add or specify mechanics
that make no-motion under positive command non-viable:

```text
1. Add a command-progress failure condition after a warmup window.
2. End or truncate episodes when progress ratio stays below the required floor.
3. Report low-progress term values under the same reward config used for
   training, not only the default gate config.
4. Add a per-phase closed-loop gate so frozen phase-1/phase-2 policies stop the
   curriculum early.
5. Keep the fitted actuator bridge and target-velocity envelope active.
```

Only after those mechanics are explicit should a new training recipe be started.
