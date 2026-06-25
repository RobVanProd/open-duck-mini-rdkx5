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
checked score artifacts: 39
passing target sources: 0
```

Treat missing required metrics as a hold. Older score artifacts that do not
record local forward displacement do not prove this gate.

The current failure-mode scan is:

```text
tool: tools/analyze_weight_transfer_gate_failures.py
artifact: outputs/analysis/WEIGHT_TRANSFER_GATE_FAILURE_ANALYSIS.md
status: HOLD_FORWARD_IMPULSE_PRIMARY
seed rows scanned: 1956
```

Key split:

```text
stable + actuator-safe rows: 964
support-ready rows: 492
forward-ready rows: 15
stable + support rows: 7
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
status: PLAN_FOOT_PLACEMENT_MPC_TEACHER
```

The required next design is:

```text
finite-horizon state-feedback teacher/optimizer
stateful stance-side selection
explicit lateral body placement over the stance foot
swing-foot placement and clearance objective
forward push timed after support loading
lateral velocity and base-y drift penalties
pitch and base-height guards
measured actuator-envelope scoring
100-150 tick seed-robust PASS_WEIGHT_TRANSFER_TARGET gate
```

This is intentionally stronger than "try Branch A." It rules out another nearby
scalar teacher-grid expansion and points at a foot-placement/body-state
optimizer as the next reviewed implementation target.

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
