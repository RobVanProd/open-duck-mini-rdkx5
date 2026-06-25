# Project Findings

This document extracts the main sim-to-real findings from the evidence branch.
It is intentionally short; detailed artifacts remain in `outputs/analysis/` and
`SIM2REAL_RESULTS_SUMMARY.md`.

## 1. BEST_WALK_ONNX_2 Is Actuator-Hostile At x=0.08

The original deployed policy is coherent enough to move, but its dynamic target
waveform is too aggressive for the measured ST3215 actuator chain.

Evidence:

```text
suspended x=0.0:
  mostly healthy, no gross mapping or IMU failure

suspended x=0.08:
  coherent air-walking visually
  pitch-chain p95 tracking around 0.12-0.17 rad
  effective lag around 3-4 ticks
  target velocity around 3.09-5.22 rad/s

slow sine sweeps:
  0.25/0.5 Hz at 0.03 rad passed
  max sine target velocity about 0.094 rad/s at 0.5 Hz
```

The actuator model fit converted that into training ranges:

```text
best pitch-chain delay fit: about 3 ticks
effective velocity limits: about 2.25-3.75 rad/s
combined model p95 fit error: about 0.019-0.035 rad
```

Decision:

```text
do not fix the old policy with runtime smoothing as the main solution
train/evaluate against a measured actuator bridge instead
```

## 2. The Policy/Sim Contract Is 101 Observations / 14 Actions

The local Open Duck Playground path initially looked mismatched from static
inspection, but instantiated through the correct environment it matches the
deployed policy contract:

```text
observation: 101
action: 14
actuator order: runtime/policy order including neck/head
MJCF nu/nq/nv: 14/21/20
home ctrl length: 14
```

Decision:

```text
do not train a 10-actuator no-head policy as a BEST_WALK_ONNX_2 replacement
```

## 3. Closed-Loop Actuator Bridge Reproduction Passed

The closed-loop sim eval with the fitted actuator bridge reproduced the real
x=0.08 degradation closely enough to justify actuator-aware training work.

Evidence:

```text
gate: PASS_CLOSED_LOOP_REPRODUCTION
platform used for that successful run: CUDA/L4 Colab
insertion point: target_stage_direct
double rate limit: false
```

Decision:

```text
the measured actuator bridge is useful
robot validation remains blocked until offline candidate gates pass
```

## 4. Reward/Curriculum Runs Found A Standstill Basin

Multiple PPO recipes after the actuator bridge either:

```text
move but over-drive and fall
freeze/stand still
reverse
collapse under contact timing
```

The important lesson from V7-V10 was that fall count alone is not a valid
success metric. Policies can reduce fall count by freezing.

Decision:

```text
grade candidates on coherent forward motion across seeds, not just fewer falls
```

## 5. Reference Motion Seeding Had A Command-Mismatch Gotcha

The initial reference-imitation seed test did not test the intended low-command
straight gait because the selected reference key was mismatched:

```text
requested gate: x=0.04 straight
selected reference: faster, lateral/yaw-biased gait
```

A command-matched reference override fixed the experimental design, but the
reference-derived target was still not directly usable as an action target.

Evidence:

```text
reference target velocity and action envelope exceeded the runtime budget
reference contact mismatch stayed around 66-69%
```

Decision:

```text
reference motion is a gait hint, not a deployable controller target as-is
```

## 6. Current Blocker Is Weight Transfer / Single Support

The latest contact-transfer audit sharpened the blocker:

```text
artifact: outputs/analysis/CONTACT_TRANSFER_BLOCKER_AUDIT.md
status: HOLD_TARGET_SOURCE_DOUBLE_SUPPORT
```

The best current dynamic-roll/lateral-fix fragments mostly move forward while
remaining in double support:

```text
50-tick robust snippets:
  double support mean/p95: 92.67% / 94.00%
  single support mean/p95: 7.33% / 11.20%
  weight-transfer-pass windows: 0

100-tick curation:
  curated windows: 0

150-tick curation:
  curated windows: 0
```

A tiny finite-horizon sequence optimizer smoke landed in the same basin:

```text
artifact: outputs/analysis/CONTACT_WEIGHT_TRANSFER_SEQUENCE_OPTIMIZER_SMOKE.md
status: HOLD_HORIZON_SEQUENCE_NO_ROBUST_TARGET

best seed_000:
  mean vx -0.0035 m/s
  double support 93%
  single support 7%

best seed_002:
  mean vx 0.0038 m/s
  double support 90%
  single support 10%
```

Decision:

```text
do not train BC/PPO from the current fragments
first build a target/demo source that actually produces sustained left/right
single-support alternation
```

## Current Next Step

The next valid offline branch is captured in:

```text
docs/WEIGHT_TRANSFER_TARGET_PLAN.md
```

The target source must pass:

```text
PASS_WEIGHT_TRANSFER_TARGET
```

before supervised imitation, PPO, robot validation, or grounded replay.

The executable gate checker is:

```bash
python3 tools/check_weight_transfer_target_gate.py
```

Current gate artifact:

```text
outputs/analysis/WEIGHT_TRANSFER_TARGET_GATE_CHECK.md
status: HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET
checked score artifacts: 66
passing target sources: 0
```

The failure-mode analysis scans the same compact score family:

```text
outputs/analysis/WEIGHT_TRANSFER_GATE_FAILURE_ANALYSIS.md
status: HOLD_FORWARD_IMPULSE_PRIMARY
seed rows scanned: 3896
```

It found:

```text
stable + actuator-safe rows: 1380
support-ready rows: 1464
forward-ready rows: 23
stable + support rows: 9
stable + forward rows: 0
support + forward rows: 9
all three: 0
```

This means the next target generator needs an explicit propulsion mechanism
after support loading. More contact alternation alone is not enough, and the
rows that move forward tend to spend lateral/pitch margin to do it.

The latest default-off stance knee/ankle push-off probe was also a hold:

```text
outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_LEG_EXTENSION_SCORE_100.md
outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_LEG_EXTENSION_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 18
dominant failures: low_forward_velocity and high_lateral_velocity
```

So "add knee/ankle push-off to the existing support-state teacher" is not the
missing mechanism either.

The latest foot-placement MPC diagnostics also ruled out two nearby fixes:

```text
wide swing-foot advance:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ADVANCE_WIDE_PROBE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ADVANCE_WIDE_PROBE_SCORE_150.md
  robust modes: 0 / 16

lateral/yaw push attenuation:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_STABILITY_PROBE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_STABILITY_PROBE_SCORE_150.md
  robust modes: 0 / 64

higher swing clearance:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_CLEARANCE_PROBE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_CLEARANCE_PROBE_SCORE_150.md
  robust modes: 0 / 16

hip-yaw heading support:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_YAW_SUPPORT_PROBE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_YAW_SUPPORT_PROBE_SCORE_150.md
  robust modes: 0 / 72
```

Wide swing advance made seed 0 move slightly forward but still far below the
gate. Lateral/yaw push attenuation made the traces more conservative and
actuator-safe, but starved propulsion; the best windows stayed around
`0.003-0.008 m/s`, not `0.04 m/s`.

So the next teacher cannot be just "more advance" or "less push when unstable."
Higher swing clearance confirms a useful submechanism: it can create more
single-support time, especially on seed 2. It still fails because that support
comes with lateral velocity and low forward speed. The next teacher needs an
active lateral/heading support controller that enables push, plus a propulsion
model that moves the body while preserving the support state. A first hip-yaw
heading-support probe did not solve that coupling: the conservative modes
reduced lateral velocity by returning to double-support/low-speed behavior,
while the modes that created more support transfer still failed lateral/yaw and
forward-speed gates.

Relative-yaw recovery-gate diagnostic:

```text
artifact: outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_RELATIVE_YAW_RECOVERY_PROBE_SCORE_100.md
artifact: outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_RELATIVE_YAW_RECOVERY_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 16
```

This corrected a diagnostic flaw in the first recovery-gate attempt: switch
readiness must use yaw error relative to the rollout's initial heading, not
absolute world yaw. With the corrected relative-yaw gate, top candidates show
high switch readiness, roughly `75-97%`, so the prior all-zero switch-ready
result was overconstrained. The corrected run still holds because forward
velocity remains far below `0.04 m/s` and seed 2 often fails lateral velocity.
This keeps the blocker at forward impulse under support/lateral constraints,
not at yaw-gate measurement.

Push-effectiveness trace read:

```text
artifact: outputs/analysis/FOOT_PLACEMENT_PUSH_EFFECTIVENESS_ANALYSIS.md
status: HOLD_PUSH_INEFFECTIVE
traces analyzed: 32
mean push_allowed_pct: 27.5362
mean 0.1s future vx delta during push: -0.0003 m/s
```

This shows the current foot-placement push primitive is not just under-used.
Push phases occur, but they do not create reliable forward acceleration. Every
trace also fails the push lateral-velocity check, and 18/32 traces exceed the
pitch-chain target-velocity check during push. The next branch should redesign
the propulsion primitive around stance support and lateral containment, not
only schedule the existing push more often.

The next branch decision is now explicit:

```text
tool: tools/decide_next_weight_transfer_branch.py
artifact: outputs/analysis/NEXT_WEIGHT_TRANSFER_BRANCH.md
status: PLAN_STANCE_RELATIVE_LATERAL_DAMPING
```

That means the next offline implementation should be a finite-horizon
state-feedback teacher/optimizer that chooses stance side, lateral body
placement, swing-foot placement, capped stance-relative propulsion, and
stronger lateral damping together.
Do not launch PPO/BC or robot validation from current target sources.

Implementation spec:

```text
docs/FOOT_PLACEMENT_MPC_TEACHER_SPEC.md
```

First implementation smoke:

```text
tool: tools/probe_foot_placement_mpc_teacher.py
status: HOLD_NO_SEED_ROBUST_TARGETS
stance-interleaved robust modes: 0 / 8
dominant failure: low_forward_velocity on seeds 0 and 2
```

The probe is useful as an offline target-source instrument, but the initial
candidate set is still not a supervised target source. The aggregate target
gate now includes 50 compact score artifacts and remains held.

Stronger-push diagnostic:

```text
artifact: outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_PUSH_PROBE_SCORE_100.md
artifact: outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_PUSH_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 16
```

It improved seed 2 partial motion but left seed 0 near-zero/backward and raised
lateral velocity. The current blocker is not just push amplitude.

Orientation diagnostic:

```text
artifact: outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ORIENTATION_SMOKE_SCORE_100.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 2
```

The traces now include roll/pitch/yaw, and the scorer reports roll p95,
yaw-change p95, and world-x displacement. This matters because local-forward
progress can diverge from world-frame x motion when heading/lateral drift is
present.

Swing-foot advance diagnostic:

```text
artifact: outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ADVANCE_PROBE_SCORE_100.md
artifact: outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ADVANCE_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 16
```

Preventing backward swing-foot placement improved seed 0 slightly but did not
clear the forward gate and introduced lateral/yaw tradeoffs. The blocker is now
sharper: foot placement helps, but it needs lateral/heading stabilization.

Wide swing-advance diagnostic:

```text
artifact: outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ADVANCE_WIDE_PROBE_SCORE_100.md
artifact: outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ADVANCE_WIDE_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 16
```

Larger swing advance improved the worst-seed score but still failed the forward
gate. The next teacher should not keep increasing advance alone.

Robot validation remains blocked.

The first replacement stance-propulsion branch has now been tested offline:

```text
outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_SAGITTAL_PROPULSION_PROBE_SCORE_100.md
outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_SAGITTAL_PROPULSION_PROBE_SCORE_150.md
outputs/analysis/FOOT_PLACEMENT_SAGITTAL_PROPULSION_EFFECTIVENESS_ANALYSIS.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 64
mean future vx delta during push: +0.0056 m/s
```

A softgated follow-up also held:

```text
outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_SAGITTAL_SOFTGATE_PROBE_SCORE_100.md
outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_SAGITTAL_SOFTGATE_PROBE_SCORE_150.md
outputs/analysis/FOOT_PLACEMENT_SAGITTAL_SOFTGATE_EFFECTIVENESS_ANALYSIS.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 64
mean future vx delta during push: +0.0007 m/s
```

This sharpens the blocker: a stance-foot-relative sagittal drive can create a
small impulse locally, but it is not seed-robust and safety gating largely
removes the effect. The next offline target-source work needs lateral support
containment that enables propulsion, not another direct increase in push
amplitude.

The latest stance-relative lateral follow-up is the best direction so far, but
still a hold:

```text
outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_STANCE_RELATIVE_LATERAL_PROBE_SCORE_100.md
outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_STANCE_RELATIVE_LATERAL_PROBE_SCORE_150.md
outputs/analysis/FOOT_PLACEMENT_STANCE_RELATIVE_LATERAL_EFFECTIVENESS_ANALYSIS.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 64
top raw rollout mean vx: 0.0312 m/s
mean future vx delta during push: +0.0099 m/s
```

It increased forward impulse and raw rollout speed, but the target scores fail
on lateral velocity and sent target velocity. Current interpretation: keep the
stance-foot-relative controller idea, but shape target velocity and lateral
dynamics before any training re-entry.

The follow-up teacher-side target-velocity cap tightened that conclusion:

```text
outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_STANCE_RELATIVE_VELOCITY_CAP_PROBE_SCORE_100.md
outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_STANCE_RELATIVE_VELOCITY_CAP_PROBE_SCORE_150.md
outputs/analysis/FOOT_PLACEMENT_STANCE_RELATIVE_VELOCITY_CAP_EFFECTIVENESS_ANALYSIS.md
status: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0 / 64
top raw rollout mean vx: 0.0257 m/s
mean future vx delta during push: +0.0083 m/s
```

The cap reduced actuator-envelope pressure, but every push trace still failed
the lateral-velocity check and seed 0 stayed weak. Current decision:

```text
outputs/analysis/NEXT_WEIGHT_TRANSFER_BRANCH.md
status: PLAN_STANCE_RELATIVE_LATERAL_DAMPING
```

That plan is now superseded by the reference push-effectiveness comparison:

```text
docs/REFERENCE_PUSH_EFFECTIVENESS_DECISION.md
outputs/analysis/REFERENCE_PUSH_EFFECTIVENESS_V20_MATCHED.md
outputs/analysis/REFERENCE_PUSH_EFFECTIVENESS_UPSTREAM_NEAREST.md
```

The matched x=0.04 reference had one positive forward-impulse variant, but only
while violating lateral stability and the measured actuator envelope:

```text
status: HOLD_REFERENCE_PROPULSION_UNSTABLE
best reference-single future vx delta: +0.0161 m/s
reference-single vy p95: 0.2688 m/s
reference-single pitch velocity p95: 5.1133 rad/s
```

The original upstream Playground reference key also failed the same physical
question in this local sim and in a detached `origin/main` Playground worktree:

```text
command: x=0.074, y=-0.037, yaw=-0.074
status: HOLD_REFERENCE_CONTACT_MISMATCH
local branch best reference-single future vx delta: -0.0099 m/s
origin/main best reference-single future vx delta: -0.0158 m/s
```

The upstream README's current-win command uses `flat_terrain_backlash`, so the
same reference key was also tested on that task:

```text
outputs/analysis/REFERENCE_PUSH_EFFECTIVENESS_UPSTREAM_MAIN_BACKLASH_NEAREST.md
status: HOLD_REFERENCE_CONTACT_MISMATCH
best reference-single future vx delta: -0.0051 m/s
```

The upstream morphology audit adds one important constraint:

```text
outputs/analysis/UPSTREAM_SIM_MORPHOLOGY_AUDIT.md
status: PASS_MORPHOLOGY_MATCHES_UPSTREAM_CODE_DRIFT_ONLY
morphology/reference mismatches: 0
code drift: joystick.py, runner.py
```

The first targeted contact-physics substitution has also been tested:

```text
docs/CONTACT_PHYSICS_AUDIT.md
outputs/analysis/CONTACT_PHYSICS_AUDIT.md
status: HOLD_CONTACT_FRICTION_SOLVER_NOT_SUFFICIENT
```

The probe copied upstream-main Playground to `/tmp`, changed floor friction
from `0.6` to `1.5 0.01 0.0006`, and changed solver iterations from `1/5` to
`100/50`, matching the older Open_Duck_Mini scene's stronger contact settings.
It improved contact matching in the synchronized mode but did not create
forward impulse:

```text
baseline best reference-single future vx delta:      -0.0051 m/s
contact-probe best reference-single future vx delta: -0.0182 m/s
```

So low floor friction / low solver iterations alone are not the missing
mechanism.

The published-policy audit has now answered that gate:

```text
outputs/analysis/PUBLISHED_POLICY_PROPULSION_AUDIT.md
status: PASS_POLICY_CLOSED_LOOP_FORWARD_MOTION
task: upstream-main flat_terrain_backlash
command: x=0.074, y=-0.037, yaw=-0.074
seeds: 8
duration complete: 8 / 8
moving seeds with track ratio >= 0.5: 7 / 8
mean local vx: 0.0540 m/s
mean command-tracking ratio: 0.7294
mean single-support fraction: 44.8%
mean single-support 0.1s future vx delta: +0.0042 m/s
```

The follow-up mechanism comparison makes the split sharper:

```text
outputs/analysis/POLICY_REFERENCE_MECHANISM_COMPARISON.md
status: PASS_POLICY_REFERENCE_MECHANISM_SPLIT
policy actual single-support fraction: 44.8%
reference contact-synchronized actual single-support fraction: 19.25%
policy single-support 0.1s future vx delta: +0.0042 m/s
reference requested-single 0.1s future vx delta: -0.0051 m/s
policy pitch-chain target velocity p95 mean: 3.0488 rad/s
reference contact-synchronized pitch-chain target velocity p95 mean: 4.9811 rad/s
```

This is the current pivot. The upstream-main sim/morphology can produce stable
closed-loop forward locomotion under the published `BEST_WALK_ONNX_2` policy.
The reference-target/open-loop path still fails the same contact/propulsion
question, and the first contact-friction/solver substitution did not rescue it.
So the blocker is no longer "sim cannot propel forward" in general. It is the
mismatch between the published policy's closed-loop contact/CoM strategy and
the controller/reference-target pathways used by the local teacher campaign.
The closed-loop policy gets more actual single support and keeps the pitch-chain
target-rate closer to the measured actuator envelope; the reference-target path
asks for single support but does not convert those windows into forward
acceleration.

Current decision: do not continue with another stance-relative lateral-damping
teacher variant by default. The next offline gate is to mine the published
policy's state-action/contact timing as a teacher or constraint source instead
of generating another nearby open-loop target variant. Robot validation remains
blocked.
