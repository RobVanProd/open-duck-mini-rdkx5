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
outputs/analysis/WEIGHT_TRANSFER_TARGET_GATE_CHECK.md
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

Executable checker:

```bash
python3 tools/check_weight_transfer_target_gate.py
```

Current result:

```text
artifact: outputs/analysis/WEIGHT_TRANSFER_TARGET_GATE_CHECK.md
status: HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET
checked score artifacts: 37
passing target sources: 0
```

Missing required metrics are treated as a hold. Older score artifacts that do
not record local forward displacement cannot prove the full gate.

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

## First Support-Objective Result

The first direct support-objective probe also held:

```text
artifact: outputs/analysis/V23_L4_ARTIFACT_RECOVERY_SUMMARY.md
status: HOLD_V23_ARTIFACT_RECOVERED_GATE_FAILED
x=0.0: all modes fall by 55-71 samples
x=0.08: all modes fall by 98-140 samples and move backward in local frame
max x=0.08 sent target velocity p95: 0.6026 rad/s
action saturation: 0%
```

The recovered V23 candidate is not actuator-envelope limited and is not a
candidate for robot validation. The next branch must add a structural
support/propulsion mechanism or inspect the V23 fall trace before designing a
new objective.

The first V23 trace confirms why:

```text
artifact: outputs/analysis/V23_SEED0_X004_TRACE_SUMMARY.md
status: HOLD_DOUBLE_SUPPORT_STANDSTILL
command: x=0.04
seed: 0
samples: 750 / duration_complete
double support: 99.33%
single support: 0.67%
mean local vx: -0.0002 m/s
track ratio: -0.0051
```

The direct support objective did not create support transfer. It produced a
stable double-support standstill. Future branches should require support-state
transition and forward displacement together; single-support occupancy alone is
not enough.

The next planned support-objective branch is:

```text
artifact: outputs/analysis/MOVEMENT_BOOTSTRAP_V24_TRANSITION_PROPULSION_PLAN.md
recipe: movement_bootstrap_v24
status: DRY_RUN / not trained
```

This branch is explicitly different from V23: contact-transition reward is
conditioned on forward progress, and double-support penalty grows with dwell
time. It should be graded on support transitions and forward displacement
together, not on single-support occupancy alone.

First V24 evidence:

```text
artifact: outputs/analysis/V24_L4_PARTIAL_RUN_SUMMARY.md
status: HOLD_V24_TRANSITION_PROPULSION_FAILED_GATE
training: completed and exported the 184320-step ONNX
gate: seeds 0-5 all held with fall/termination
remote: Colab disappeared before seeds 6-7 completed
```

The full 0-7 seed distribution is incomplete, but the gate failure is already
proven because the configured pass condition allowed no failed seeds. V24 did
not create coherent forward support transfer:

```text
recovered seeds: 6
failed recovered seeds: 6
mean local vx: near-zero or negative for every recovered seed
action saturation: 0%
pitch-chain target velocity: far below the measured actuator envelope
```

Reward-term activation audit:

```text
artifact: outputs/analysis/V24_REWARD_TERM_ACTIVATION_AUDIT.md
status: HOLD_REWARD_TERMS_MISSING
missing configured terms:
  forward_contact_transition
  forward_double_support
  forward_double_support_dwell
  forward_single_support
```

This means the recovered V24 gate is behaviorally failed, but the recovered
reward-term trace did not prove that the configured transition/dwell terms were
observed. Before treating another support-objective run as definitive, require
the new contact terms to be visible in gate artifacts.

The missing-term cause is now identified and patched:

```text
artifact: outputs/analysis/V24_REWARD_OVERRIDE_ALLOWLIST_FIX.md
status: PASS_LOCAL_REWARD_TERMS_OBSERVED_AFTER_ALLOWLIST_FIX
```

The issue was stale closed-loop eval reward override allow-listing, not missing
Playground reward definitions. This makes reward activation smoke a required
preflight for any next support-contact PPO branch.

Runbook:

```text
docs/SUPPORT_REWARD_PREFLIGHT.md
```

Next offline branch handoff:

```text
docs/NEXT_OFFLINE_BRANCH_AFTER_V24.md
```

Corrected seed-0 V24 evidence:

```text
artifact: outputs/analysis/V24_CORRECTED_SEED0_TRACE.md
reward audit: outputs/analysis/V24_CORRECTED_SEED0_REWARD_AUDIT.md
status: LOW_PROGRESS_TERMINATION
double support: 65 / 70 ticks
mean local vx: -0.0008 m/s
```

After the allow-list fix, the support-contact reward terms are visible, but the
candidate still fails by staying mostly in double support and making no useful
forward progress.

This closes the nearby "add transition reward / dwell penalty and hope" branch.
The next target-source or learning-objective branch should be structurally
different, not another scalar reward tweak around V23/V24.
