# Target-Source Exit Decision

This note is an offline research handoff. It does not authorize training,
robot tests, SSH, deployment, grounded replay, or runtime changes.

## Decision

The current target-source branch should stop expanding nearby scalar variants.

Status:

```text
HOLD_TARGET_SOURCE_BRANCH_EXHAUSTED
```

Reason:

```text
The tested target families can improve one part of the gait problem at a time,
but none produces seed-robust 100-150 tick forward motion with useful
single-support, low lateral velocity, stable pitch/height, and actuator-safe
targets.
```

The next branch must be structurally different. It should not be another
prior-scale change, phase-state wrapper, open-loop lift pulse, stance-push sign
check, or small CoM gate sweep around the same target primitive.

## Evidence Summary

The durable target-source evidence now says:

```text
dynamic-roll 50-tick fragments:
  short seed-robust snippets exist
  but source snippets are mostly double support
  not valid stepping references

open-loop single-support primitives:
  stronger lift / roll / stance-push pulses still stay double-support dominated

closed-loop CoM / stance-relative controller:
  improves lateral/contact discipline
  but forward displacement collapses

support-readiness gate:
  increases single-support time
  but freezes forward motion

stateful support phase:
  confirms timer flipping is not the main blocker
  phase transitions alone do not create propulsion

horizon random-shoot sequences:
  first bounded pass is a structural tool, not another scalar gate
  still produces low forward velocity and double-support dominance
```

Key artifacts:

```text
outputs/analysis/CONTACT_TIMED_REFERENCE_SNIPPETS.md
outputs/analysis/CONTACT_TIMED_REFERENCE_SEQUENCE_SCORE_100.md
outputs/analysis/CONTACT_TIMED_REFERENCE_SEQUENCE_SCORE_150.md
outputs/analysis/TARGET_GENERATOR_SINGLE_SUPPORT_PROBE.md
outputs/analysis/TARGET_GENERATOR_SINGLE_SUPPORT_PROBE_SCORE_100.md
outputs/analysis/TARGET_GENERATOR_SINGLE_SUPPORT_PROBE_SCORE_150.md
outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SUPPORT_GATED_PROBE.md
outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SUPPORT_GATED_SCORE_100.md
outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SUPPORT_GATED_SCORE_150.md
outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_STRICT_PROBE.md
outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_TIMEOUT_PROBE.md
outputs/analysis/CONTACT_WEIGHT_TRANSFER_SEQUENCE_OPTIMIZER.md
outputs/analysis/contact_weight_transfer_sequence_optimizer.json
```

## Ruled Out

Do not spend the next run on:

```text
more dynamic-roll 50-tick fragment stitching
more open-loop lift-pulse / roll-assist / stance-push grids
more stance-push sign checks
more prior-scale-only PPO runs
more contact-bit adapters around the same short reference table
more phase-state plumbing around the same pitch-chain stance push
more passive "wait until ready" swing gates
```

These are not banned forever, but they are not the highest-information next
step. Each has already failed the current seed-robust target gate or failed to
produce forward motion without lateral/contact compromise.

## Still Live

The live hypothesis is:

```text
the Duck needs an explicit weight-transfer / foot-placement / propulsion
strategy that makes single support physically available before it asks the
policy to imitate or optimize forward steps.
```

This is stronger than "the reward needs another weight." The current holds
occur before PPO can use a good walking target: the target generators
themselves are not producing sustained, actuator-safe single-support forward
motion across seeds.

## First Horizon Sequence Optimizer Result

The first structural follow-up tool is:

```text
tools/optimize_contact_weight_transfer_sequence.py
```

It generates smooth finite-horizon action tables, replays them through the
closed-loop sim sequence path, and scores the realized traces with the same
seed-robust contact/forward objective. It is not training.

First bounded CPU pass:

```text
artifact: outputs/analysis/CONTACT_WEIGHT_TRANSFER_SEQUENCE_OPTIMIZER.md
status: HOLD_HORIZON_SEQUENCE_NO_ROBUST_TARGET
candidates: 6
seeds: 0,2
window: 100 ticks
```

Result:

```text
robust_mode_count: 0
best seed0 vx: 0.0020 m/s
best seed2 vx: 0.0036 m/s
dominant failures:
  low_forward_velocity
  double_support_dominates
  too_little_single_support
  single_support_not_balanced
```

Interpretation:

```text
The new instrument is working, but the first direct horizon search did not find
a useful target source. The blocker remains contact/weight-transfer plus
propulsion, not merely the lack of a sequence replay mechanism.
```

## Next Structural Branch

The next useful branch should test one of these, in this order:

1. A horizon-based teacher or optimizer that chooses stance side, body lateral
   placement, swing-foot placement, and forward push together, then scores the
   realized contact sequence over 100-150 ticks.
2. A contact/weight-transfer objective inside the learning environment that
   explicitly rewards useful left/right single-support alternation and penalizes
   double-support dwell during commanded motion, before reintroducing actuator
   bridge curriculum.
3. A closed-loop reference generator that reacts to base pitch, base height,
   lateral velocity, and foot contacts, instead of replaying fixed snippets.

The first default-off learning-objective hook for option 2 is in the companion
Playground branch:

```text
repo: RobVanProd/Open_Duck_Playground
branch: codex/forward-progress-reward
commit: b4a96ca training: add forward support contact rewards
```

It adds:

```text
forward_single_support:
  positive scale rewards exactly one support foot during forward commands

forward_double_support:
  negative scale penalizes double-support dwell during forward commands
```

Both scales default to `0.0`, so existing training behavior is unchanged unless
the runner flags enable them explicitly.

The RDK training planner now exposes those default-off hooks through:

```text
tools/run_actuator_bridge_training_smoke.py
tools/plan_staged_curriculum_training.py
```

The first planned probe is:

```text
recipe: movement_bootstrap_v23
artifact: outputs/analysis/MOVEMENT_BOOTSTRAP_V23_SUPPORT_OBJECTIVE_PLAN.md
status: plan-only / not trained
```

V23 is not another target-source variant. It removes the soft-prior target
branch and tests whether explicit single-support reward plus double-support
dwell cost can teach low-command weight transfer at x=0.04 under vanilla
dynamics. It must be graded by contact alternation and coherent forward motion
across seeds, not by fall-count alone.

First V23 evidence:

```text
artifact: outputs/analysis/V23_L4_PARTIAL_RUN_SUMMARY.md
status: HOLD_V23_SUPPORT_OBJECTIVE_FAILED_GATE
training: completed and exported the 184320-step ONNX
gate: seeds 0-5 all held with fall/termination
remote: Colab disappeared during seed 6
```

The full 0-7 seed distribution is incomplete, but the gate failure is already
proven because the configured pass condition allowed no failed seeds. This means
the first explicit support-contact reward probe also failed to clear the
weight-transfer blocker. Do not rerun V23 unchanged.

Any branch must report:

```text
mean_vx
local forward displacement
track ratio
vy_abs_p95
body_pitch_abs_p95
base_height_min
double_support_pct
single_support_pct
left/right single-support pct
contact transitions
sent_target_velocity_p95
joint_tracking_p95
termination tick / done margin
```

## Required Gate

Before another BC/PPO run from target-source data, require:

```text
PASS_WEIGHT_TRANSFER_TARGET:
  seeds 0 and 2 both have a 100-tick window with:
    mean_vx >= 0.04 m/s
    local forward displacement >= 0.004 m
    vy_abs_p95 <= 0.12 m/s
    body_pitch_abs_p95 <= 0.35 rad
    base_height_min >= 0.145 m
    double_support_pct <= 75%
    single_support_pct >= 20%
    min_each_single_support_pct >= 5%
    contact_transitions >= 2
    sent_target_velocity_p95 <= 3.75 rad/s
    joint_tracking_p95 <= 0.12 rad
```

Preferred before training:

```text
same gate over 150 ticks
local forward displacement >= 0.006 m
```

Passing this gate does not authorize robot validation. It only authorizes a
reviewed imitation or target-dataset smoke branch.

## Stop Conditions

Stop a candidate branch immediately if:

```text
forward motion appears only by increasing lateral velocity above gate
forward motion appears only with double-support dominance
forward motion appears only for one seed
target velocity exceeds the measured actuator envelope
the candidate improves fall count by freezing
```

If those holds repeat, move away from target-source generation and test the
contact/weight-transfer learning objective directly in sim.
