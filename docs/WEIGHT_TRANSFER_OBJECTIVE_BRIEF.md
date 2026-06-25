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

## First Support-State Probe

The first default-off support-state controller hook was added to:

```text
tools/probe_closed_loop_weight_transfer_teacher.py
flag: --support-state-modes
```

Mode `0` preserves the historical phase-scheduled stance/swing behavior. Mode
`1` uses actual single-foot contact as the stance side when the sim has already
entered single support, and falls back to phase only during double/no support.

Bounded CPU probe:

```text
artifact: outputs/analysis/SUPPORT_STATE_WEIGHT_TRANSFER_PROBE.md
score_100: outputs/analysis/SUPPORT_STATE_WEIGHT_TRANSFER_PROBE_SCORE_100.md
score_150: outputs/analysis/SUPPORT_STATE_WEIGHT_TRANSFER_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Result:

```text
100-tick top seed0 / seed2:
  vx: 0.0137 / 0.0115 m/s
  local dx: 0.0273 / 0.0230 m
  vy95: 0.1479 / 0.1483 m/s
  single support: 10.0% / 11.0%
  contact transitions: 16 / 20

150-tick top seed0 / seed2:
  vx: 0.0102 / 0.0103 m/s
  local dx: 0.0306 / 0.0309 m
  vy95: 0.1548 / 0.1635 m/s
  single support: 10.0% / 15.3%
  contact transitions: 19 / 25
```

Interpretation: using actual support state increased useful contact transitions
and single-support time, but did not create enough forward displacement and
still failed lateral velocity. The next controller must not merely follow
actual contact state; it must decide when and how to move the center of mass,
load the stance foot, and push forward without side impulse.

## First Support-Loaded Push Probe

The next default-off hook was added to test stance-foot loading:

```text
flag: --single-support-push-scales
```

Scale `0` preserves the existing stance-push behavior. Scale `1` only applies
stance push while the sim is in actual single support. A bounded CPU probe
tested scales `0`, `0.5`, and `1.0`:

```text
artifact: outputs/analysis/SUPPORT_LOADED_WEIGHT_TRANSFER_PROBE.md
score_100: outputs/analysis/SUPPORT_LOADED_WEIGHT_TRANSFER_PROBE_SCORE_100.md
score_150: outputs/analysis/SUPPORT_LOADED_WEIGHT_TRANSFER_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Result:

```text
100-tick best scale: 0.5
  vx: 0.0115 / 0.0129 m/s
  local dx: 0.0230 / 0.0258 m
  vy95: 0.1424 / 0.1543 m/s
  single support: 11.0% / 10.0%

150-tick best scale: 0.5
  vx: 0.0103 / 0.0121 m/s
  local dx: 0.0309 / 0.0362 m
  vy95: 0.1586 / 0.1635 m/s
  single support: 14.0% / 17.3%
```

Interpretation: requiring confirmed single-support loading improves support
dwell/transition metrics, but it still leaves the same forward/lateral failure.
It is not enough to wait for single support; the controller must actively place
and regulate the body over the stance foot.

The next concrete implementation plan is:

```text
docs/COM_WEIGHT_TRANSFER_CONTROLLER_PLAN.md
```

The first CoM controller implementation has now been tested:

```text
tool: tools/probe_com_weight_transfer_controller.py
strict artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_PROBE.md
relaxed artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_RELAXED_PROBE.md
stance artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STANCE_PROBE.md
aggressive stance artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STANCE_AGGRESSIVE_PROBE.md
reverse-push stance artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STANCE_REVERSE_PUSH_PROBE.md
sagittal push-off artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SAGITTAL_PROBE.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Strict gates rarely allowed push. Relaxed gates allowed more push but still held
with low displacement:

```text
strict top 100-tick local dx: 0.0074 / 0.0132 m
relaxed top 100-tick local dx: 0.0088 / 0.0121 m
stance-relative top 100-tick local dx: 0.0145 / 0.0129 m
aggressive stance-relative top 100-tick local dx: 0.0254 / 0.0209 m
reverse-push stance-relative top 100-tick local dx: 0.0209 / 0.0218 m
sagittal push-off top 100-tick local dx: 0.0209 / 0.0208 m
sagittal push-off top 150-tick local dx: 0.0012 / 0.0134 m
```

This points to `HOLD_FORWARD_IMPULSE_STILL_LOW`: stance-foot-relative lateral
control improves contact and lateral behavior, and aggressive push can roughly
double short-window forward displacement, but no variant reaches seed-robust
forward displacement or sustained 150-tick progress. The tested sagittal
body-over-stance-foot and ankle push-off terms did not beat the aggressive
stance-relative baseline, so the next step should be a different
higher-level controller/reference design, not another nearby scalar gate or
push-sign expansion.

## Next Structural Branch

The next branch is specified in:

```text
docs/CONTACT_TIMED_REFERENCE_SNIPPETS_PLAN.md
```

Decision:

```text
try contact-timed reference snippets before any new scalar CoM/controller sweep
```

Reason:

```text
dynamic-roll lateral-fix fragments contain the best known 50-tick contact/motion
timing, while CoM controller probes contain the best known lateral/contact
discipline. The next target source should preserve useful contact timing from
the curated fragments but regenerate longer envelope-aware targets that can be
scored over 100-150 ticks.
```

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

## Contact-Timed Fragment Audit

The first-pass audit of robust dynamic-roll 50-tick fragments showed that the
source fragments themselves are double-support dominated:

```text
tool: tools/build_contact_timed_reference_snippets.py
artifact: outputs/analysis/CONTACT_TIMED_REFERENCE_SNIPPETS.md
status: HOLD_SOURCE_FRAGMENTS_DOUBLE_SUPPORT
entries: 9
pass_entries: 0
single_support_pct_mean: 7.33%
double_support_pct_mean: 92.67%
```

Closed-loop aggregate replay and objective scoring also held:

```text
replay: outputs/analysis/CONTACT_TIMED_REFERENCE_SEQUENCE_REPLAY.md
score_100: outputs/analysis/CONTACT_TIMED_REFERENCE_SEQUENCE_SCORE_100.md
score_150: outputs/analysis/CONTACT_TIMED_REFERENCE_SEQUENCE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Decision:

```text
do not train from the current 50-tick dynamic-roll fragments; the next source
must explicitly generate useful single-support / weight-transfer timing.
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
