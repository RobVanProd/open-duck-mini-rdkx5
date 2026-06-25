# Weight-Transfer Objective Brief

This brief defines the next offline experiment after the current target-source
campaign. It is a design gate, not permission to train or touch the robot.

## Problem

The latest evidence has narrowed the low-command walking blocker to contact and
weight transfer:

```text
forward displacement can be forced,
but current target families do it through lateral momentum;
when lateral/contact gates are controlled,
forward displacement collapses or double-support dominates.
```

The next experiment should stop re-presenting the same kinematic targets and
instead make weight transfer itself the object being optimized.

Current aggregate evidence:

```text
artifact: outputs/analysis/WEIGHT_TRANSFER_TARGET_CAMPAIGN_SUMMARY.md
status: HOLD_FORWARD_LATERAL_SUPPORT_TRADEOFF
```

That summary aggregates the compact target-source score artifacts and should be
checked before launching another target-source or training branch.

## Required Gate

The next target source must pass:

```text
PASS_WEIGHT_TRANSFER_TARGET:
  seeds 0 and 2 both have a 100-150 tick window with:
    mean_vx >= 0.04 m/s
    local forward displacement >= 0.04 m over 100 ticks
    local forward displacement >= 0.06 m over 150 ticks
    vy_abs_p95 <= 0.12 m/s
    body_pitch_abs_p95 <= 0.35 rad
    base_height_min >= 0.145 m
    double_support_pct <= 90%
    single_support_pct >= 8%
    min_each_single_support_pct >= 2%
    contact_transitions >= 3
    sent_target_velocity_p95 <= 2.5 rad/s
    joint_tracking_p95 <= 0.12 rad
```

This is a target-source gate. Passing it does not authorize robot validation.

## Objective Terms

The next controller/generator should score these directly:

```text
positive:
  local forward displacement
  useful left/right single-support alternation
  contact transitions after stable support dwell
  base height inside safe band

negative:
  lateral velocity p95
  base-y drift
  double-support dwell during commanded motion
  no-support dwell
  body pitch and pitch rate
  sent target velocity above envelope
  action saturation
  joint tracking error
```

## Controller Direction

Prefer a state-feedback controller or optimizer over another periodic grid.
The controller should reason over:

```text
local_vx
local_vy
base_y
body_pitch
body_pitch_rate
base_height
left/right foot contacts
left/right foot site height
time in current support state
stance side
swing side
```

It should explicitly couple:

```text
1. lateral load shift,
2. stance-foot support,
3. swing-foot clearance,
4. forward stance push,
5. pitch/base-height recovery,
6. side transition timing.
```

## Branch Decisions

Use these decisions before spending more GPU time:

```text
PASS:
  Build a compact target manifest and run CPU closed-loop replay.

HOLD_FORWARD_STILL_LOW:
  Objective/controller is too conservative; inspect whether double support or
  pitch limits are suppressing push.

HOLD_LATERAL_UNSTABLE:
  Forward impulse exists but is still side-coupled; add lateral momentum/base-y
  state to the controller before training.

HOLD_SUPPORT_TRANSFER_FAILED:
  The controller is still not entering useful single support; change the support
  state machine or foot-clearance/contact-transition objective.

HOLD_ACTUATOR_ENVELOPE:
  The only successful target violates actuator limits; do not train from it.
```

## Non-Goals

```text
do not run robot tests
do not SSH or deploy
do not run grounded replay
do not change BEST_WALK_ONNX_2
do not relax the actuator envelope to force a pass
do not treat binary contact matching alone as success
do not launch another prior-scale-only PPO run
do not train from short fragments that fail the 100-150 tick gate
```
