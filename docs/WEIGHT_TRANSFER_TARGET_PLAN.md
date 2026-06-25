# Weight Transfer Target Plan

This is an offline planning note. It does not authorize robot tests, SSH,
deployment, runtime changes, policy deployment, or training by itself.

## Current Finding

The contact-transfer audit says:

```text
artifact: outputs/analysis/CONTACT_TRANSFER_BLOCKER_AUDIT.md
status: HOLD_TARGET_SOURCE_DOUBLE_SUPPORT
```

The current dynamic-roll/lateral-fix target snippets are not valid stepping
demonstrations yet:

```text
50-tick robust-mode curated snippets:
  double support mean/p95: 92.67% / 94.00%
  single support mean/p95: 7.33% / 11.20%
  weight-transfer-pass windows: 0

100-tick curation:
  curated windows: 0

150-tick curation:
  curated windows: 0
```

The fragments can produce small forward displacement, but they mostly do it
while staying in double support. Training BC/PPO from those snippets would teach
a double-support shuffle, not a transferable stepping gait.

## Decision

Do not launch another PPO run from:

```text
current V24 recipe
current dynamic-roll/lateral-fix fragments
current 50-tick target dataset manifest
another scalar contact reward tweak
```

The next offline target is:

```text
PASS_WEIGHT_TRANSFER_TARGET
```

before BC, imitation, or PPO.

The executable gate check is:

```bash
python3 tools/check_weight_transfer_target_gate.py
```

Current result:

```text
artifact: outputs/analysis/WEIGHT_TRANSFER_TARGET_GATE_CHECK.md
status: HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET
checked score artifacts: 62
passing target sources: 0
```

Treat missing required metrics as a hold. Older score artifacts that do not
record local forward displacement do not prove this gate.

The current failure-mode scan is:

```text
tool: tools/analyze_weight_transfer_gate_failures.py
artifact: outputs/analysis/WEIGHT_TRANSFER_GATE_FAILURE_ANALYSIS.md
status: HOLD_FORWARD_IMPULSE_PRIMARY
seed rows scanned: 3384
```

Key split:

```text
stable + actuator-safe rows: 1250
support-ready rows: 789
forward-ready rows: 15
stable + support rows: 9
stable + forward rows: 0
support + forward rows: 1
all three: 0
```

So the next generator should not only create more single-support time. The
closest rows show that once support/stability/actuator gates are satisfied,
forward impulse is still missing. Rows with forward motion tend to buy it by
leaving lateral or pitch gates.

## Minimum Target Gate

A target source must pass this gate before training:

```text
seeds: 0 and 2 minimum
window length: 100-150 ticks
mean vx >= 0.04 m/s
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

If this target gate fails, do not start policy training from that source.

## Next Implementation Branch

Use a richer closed-loop teacher/optimizer, not another reward-only learner.

The first bounded finite-horizon sequence smoke did not clear the gate:

```text
tool: tools/optimize_contact_weight_transfer_sequence.py
artifact: outputs/analysis/CONTACT_WEIGHT_TRANSFER_SEQUENCE_OPTIMIZER_SMOKE.md
status: HOLD_HORIZON_SEQUENCE_NO_ROBUST_TARGET
seeds: 0,2
candidates: 4
window: 100 ticks
```

Best candidate summary:

```text
seed_000:
  mean vx: -0.0035 m/s
  double support: 93%
  single support: 7%

seed_002:
  mean vx: 0.0038 m/s
  double support: 90%
  single support: 10%
```

So a plain smooth horizon action-table random shoot still lands in the same
double-support/low-progress basin. The next generator needs more structure than
unconditioned finite-horizon action tables.

The target generator should explicitly control:

```text
stance side
body lateral placement over stance foot
swing-foot clearance
swing-foot placement
stance push timing
support transition timing
pitch and base-height guards
actuator-envelope limits
```

The objective should score support transfer directly:

```text
double support dwell is a cost during commanded motion
left-only and right-only support must both occur
single-support intervals must last long enough to be useful
forward progress must occur during/after stance push
no-support and lateral collapse remain hard failures
```

## Latest Ruled-Out Local Mechanism

The closed-loop teacher now exposes default-off stance leg-extension push-off
terms:

```text
tool: tools/probe_closed_loop_weight_transfer_teacher.py
flags:
  --stance-knee-pushes
  --stance-ankle-pushes
```

A bounded CPU-only probe tested support-state mode with coordinated stance
knee/ankle push-off:

```text
artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_LEG_EXTENSION_PROBE.md
score_100: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_LEG_EXTENSION_SCORE_100.md
score_150: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_LEG_EXTENSION_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Result:

```text
100-tick robust modes: 0 / 18
150-tick robust modes: 0 / 18

dominant failures:
  low_forward_velocity
  high_lateral_velocity

best 150-tick windows:
  support/contact gates can improve to roughly 64-70% double support and
  30-36% single support, but vx remains around 0.001-0.014 m/s and vy95
  remains around 0.21-0.26 m/s.
```

Interpretation: adding knee/ankle push-off to the same support-state teacher
does not produce the missing mechanism. The next branch should not widen this
nearby teacher grid again. It needs a different body-state/contact/propulsion
controller or optimizer.

## Executable Next-Branch Decision

The next branch is selected by:

```bash
python3 tools/decide_next_weight_transfer_branch.py
```

Current decision artifact:

```text
outputs/analysis/NEXT_WEIGHT_TRANSFER_BRANCH.md
status: PLAN_LATERAL_CONTAINED_STANCE_PROPULSION
```

The required next design is:

```text
finite-horizon state-feedback teacher/optimizer
stateful stance-side selection
explicit lateral body placement over the stance foot
swing-foot placement and clearance objective
active lateral containment while stance propulsion remains enabled
stance-support propulsion that is not only a direct push-amplitude increase
lateral velocity and base-y drift penalties
pitch and base-height guards
measured actuator-envelope scoring
100-150 tick seed-robust PASS_WEIGHT_TRANSFER_TARGET gate
```

This is intentionally stronger than "try Branch A." It rules out another nearby
scalar teacher-grid expansion and, after the push-effectiveness trace read,
points at lateral-contained stance propulsion as the next reviewed
implementation target.

Implementation spec:

```text
docs/FOOT_PLACEMENT_MPC_TEACHER_SPEC.md
```

First implementation smoke:

```text
tool: tools/probe_foot_placement_mpc_teacher.py
artifacts:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_SMOKE_V3_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_SMOKE_V3_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
stance-interleaved modes: 8
stance-interleaved robust modes: 0
```

The probe now interleaves left-start/right-start variants before candidate
truncation, but the first candidate set still misses forward impulse across
seeds. Treat this as an instrumented negative smoke, not permission to train.

Sagittal stance-feedback propulsion diagnostic:

```text
artifacts:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_SAGITTAL_PROPULSION_PROBE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_SAGITTAL_PROPULSION_PROBE_SCORE_150.md
  outputs/analysis/FOOT_PLACEMENT_SAGITTAL_PROPULSION_EFFECTIVENESS_ANALYSIS.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 64
```

This added a default-off stance-foot-relative sagittal drive:

```text
stance_base_x_offset_m
sagittal_gain
vx_gain
propulsion_limit_rad
propulsion_pattern
```

It was a better diagnostic than the old fixed pitch-chain push because it tied
stance propulsion to base position and local forward-velocity error. It did
move the aggregate push-effectiveness metric in the right direction:

```text
relative-yaw push diagnostic mean future vx delta: -0.0003 m/s
sagittal propulsion mean future vx delta: +0.0056 m/s
PASS_PUSH_EFFECTIVE traces: 1 / 128
```

But it still failed the target gate. The best robust-ranked windows stayed far
below `0.04 m/s`, and the remaining failures were low forward velocity,
lateral velocity, and target-velocity violations on seed 2. This is a useful
partial mechanism, not a target source.

Sagittal softgate follow-up:

```text
artifacts:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_SAGITTAL_SOFTGATE_PROBE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_SAGITTAL_SOFTGATE_PROBE_SCORE_150.md
  outputs/analysis/FOOT_PLACEMENT_SAGITTAL_SOFTGATE_EFFECTIVENESS_ANALYSIS.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 64
```

Reintroducing lateral/yaw soft gates around the sagittal drive reduced some
lateral stress but starved forward impulse:

```text
sagittal propulsion mean future vx delta: +0.0056 m/s
softgated sagittal mean future vx delta: +0.0007 m/s
PASS_PUSH_EFFECTIVE traces: 1 / 128
```

Interpretation: the replacement stance propulsion direction is not enough by
itself. The next useful branch needs a controller that actively preserves
lateral support while pushing, instead of throttling push whenever lateral
motion appears or pushing through a laterally uncontained stance.

Stronger-push diagnostic:

```text
artifacts:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_PUSH_PROBE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_PUSH_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 16
```

Relaxing readiness and increasing stance push improved seed 2 but made lateral
velocity worse and did not move seed 0 forward. The next revision should improve
coupled lateral balance and foot placement, not simply increase push amplitude.

Orientation diagnostic:

```text
artifact: outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ORIENTATION_SMOKE_SCORE_100.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 2
```

The trace/scorer now reports roll p95, yaw-change p95, and world-x displacement
next to local-forward displacement. Use these fields to distinguish real
forward progress from heading/lateral drift in future teacher revisions.

Swing-foot advance diagnostic:

```text
artifacts:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ADVANCE_PROBE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ADVANCE_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 16
```

Preventing backward swing-foot placement improved seed 0 from near-zero/backward
to small positive local vx in the best 100-tick window, but it remained below
the forward gate and exposed lateral/yaw tradeoffs. Use it as a parameter in the
next controller, not as a complete fix.

Wide swing-advance diagnostic:

```text
artifacts:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ADVANCE_WIDE_PROBE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ADVANCE_WIDE_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 16
```

Larger swing advance improved the worst-seed score but did not produce enough
forward velocity. The next controller should stabilize lateral/yaw behavior
while using swing advance, not keep increasing advance alone.

Lateral/yaw push-stability diagnostic:

```text
artifacts:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_STABILITY_PROBE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_STABILITY_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 64
```

This added default-off push attenuation based on lateral velocity and yaw. It
made the best windows more conservative:

```text
100-tick top windows:
  seed 0 vx: about 0.0045 m/s
  seed 2 vx: about 0.0053-0.0081 m/s
  sent target velocity p95: about 0.66-0.71 rad/s
  lateral p95: near or under the 0.12 m/s gate

150-tick top windows:
  vx: about 0.0037 m/s on both seeds
  sent target velocity p95: about 0.76-1.07 rad/s
```

Interpretation: push attenuation can reduce lateral/actuator stress, but it
solves the wrong side of the tradeoff by starving forward impulse. The next
controller needs active lateral/heading support stabilization that enables
propulsion, not only a push throttle that turns propulsion down.

Higher swing-clearance diagnostic:

```text
artifacts:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_CLEARANCE_PROBE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_CLEARANCE_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 16
```

This was prompted by a trace read of the best wide-advance mode:

```text
load_ready: 92-93%
swing_ready: 6-12%
dominant contact: double support
foot clearance p95: below the 0.008 m clearance gate
```

Increasing swing knee lift to `0.18 rad` improved support transfer on some
windows:

```text
seed 2 examples:
  single support: about 31-42%
  double support: about 58-69%
  contact transitions: about 22-29
```

But it did not clear the gate:

```text
forward velocity: still below 0.04 m/s
lateral p95: often 0.20-0.32 m/s
some target velocity rows near or above the scoring threshold
seed 0 still weak or mostly double-support
```

Interpretation: swing clearance is a useful mechanism, but by itself it shifts
the failure from "cannot enter single support" toward "enters support while
losing lateral/heading margin and not producing enough forward impulse."

Hip-yaw heading-support diagnostic:

```text
artifacts:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_YAW_SUPPORT_PROBE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_YAW_SUPPORT_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 72
```

This added default-off hip-yaw correction terms:

```text
yaw_gain
yaw_vy_gain
yaw_limit
```

The best 100-tick windows showed the same tradeoff:

```text
conservative heading-correction modes:
  lateral velocity can stay near the gate
  target velocities are low
  but forward velocity is near zero and double-support dominates

support-transfer modes:
  seed 2 can reach about 23-35% single support in some windows
  but lateral p95 remains about 0.24-0.28 m/s
  yaw change can grow above 0.2 rad
  forward velocity remains below the 0.04 m/s gate
```

Interpretation: simple hip-yaw feedback does not decouple heading/lateral drift
from support transfer. The next revision needs a more stateful stance controller
or optimization objective that explicitly keeps base-y/yaw bounded while
choosing foot placement and stance push, rather than adding a single yaw target
overlay.

Relative-yaw recovery-gate diagnostic:

```text
artifacts:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_RELATIVE_YAW_RECOVERY_PROBE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_RELATIVE_YAW_RECOVERY_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 16
```

This run fixed an instrumentation issue in the first recovery-gate attempt:
transition readiness must use wrapped yaw error relative to the rollout's
initial heading. The corrected probe shows high switch readiness in the leading
candidates, roughly `75-97%`, so the recovery gate is no longer blocked by a
spurious absolute-yaw condition. It still does not clear the target gate:

```text
100-tick dominant failures:
  seed 0: low_forward_velocity across all modes
  seed 2: low_forward_velocity and high_lateral_velocity across all modes

best 100-tick windows:
  seed0 vx: about -0.0001 to 0.0084 m/s
  seed2 vx: about 0.0046 to 0.0213 m/s
  seed2 vy95: about 0.1266 to 0.3395 m/s
```

Interpretation: the corrected yaw gate removes one false blocker but does not
create propulsion. The next branch still needs a stance/foot-placement
controller that generates forward impulse while preserving lateral support,
not another yaw recovery or scalar push grid.

Push-effectiveness trace read:

```text
tool: tools/analyze_foot_placement_push_effectiveness.py
artifact: outputs/analysis/FOOT_PLACEMENT_PUSH_EFFECTIVENESS_ANALYSIS.md
status: HOLD_PUSH_INEFFECTIVE
traces: 32
mean push_allowed_pct: 27.5362
mean push_future_vx_delta_m_s: -0.0003
```

This analyzed the corrected relative-yaw traces only. It found push was present
often enough to evaluate, but the current push primitive does not produce
reliable forward acceleration:

```text
push_does_not_accelerate: 19 / 32 traces
push_lateral_velocity_high: 32 / 32 traces
push_target_velocity_high: 18 / 32 traces
```

Interpretation: the missing forward impulse is now localized to the push
primitive itself. The next branch should change how propulsion is generated
under stance support, not simply alter transition timing or make the existing
pitch-chain push more frequent.

## Stop Conditions

Stop target generation and do not train if:

```text
100-150 tick candidates remain dominated by double support
only one seed passes
one single-support side is missing
forward motion only appears in short 50-tick fragments
target velocity leaves the measured actuator envelope
base height or body pitch fails before the target window ends
```

## Training Re-entry Rule

Training can resume only after a reviewed target source clears:

```text
PASS_WEIGHT_TRANSFER_TARGET
```

Then the next training path should be small and staged:

```text
1. supervised/imitation smoke from the verified target source
2. seed sweep at x=0.04 vanilla
3. mild bridge only after coherent low-command motion exists
4. fitted bridge only after mild bridge passes
5. x=0.08 only after x=0.04 is seed-robust
```

Robot validation remains blocked until the offline low-command multi-seed gates
pass.
