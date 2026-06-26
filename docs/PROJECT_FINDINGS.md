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

The command sweep then scoped that result:

```text
outputs/analysis/PUBLISHED_POLICY_COMMAND_SWEEP.md
status: WARN_COMMAND_SPECIFIC_PROPULSION_OVER_ENVELOPE
```

Results:

```text
upstream turning command x=0.074, y=-0.037, yaw=-0.074:
  moving seeds: 7 / 8
  mean local vx: 0.0540 m/s
  mean tracking ratio: 0.7294
  pitch-chain p95 target velocity mean: 3.0488 rad/s
  pitch-chain p95 target velocity max-joint mean: 4.6157 rad/s

straight x=0.04:
  moving seeds: 0 / 8
  mean local vx: 0.0019 m/s
  mean tracking ratio: 0.0468
  pitch-chain p95 target velocity max-joint mean: 1.2742 rad/s

straight x=0.08:
  moving seeds: 7 / 8
  mean local vx: 0.0640 m/s
  mean tracking ratio: 0.7998
  pitch-chain p95 target velocity mean: 3.2246 rad/s
  pitch-chain p95 target velocity max-joint mean: 5.1546 rad/s
```

This corrects the earlier shorthand. The published policy does prove
command-specific closed-loop propulsion in vanilla sim, but it does not yet
prove a real-envelope-safe gait. The moving cells exceed the measured
`3.75 rad/s` per-joint pitch-chain p95 envelope. The straight `x=0.04` cell is
inside the envelope but does not move, so it should not be treated as the easy
first gate or as an existence-proven training target.

The follow-up compact command-grid screen checked nearby straight and scaled
turning commands:

```text
outputs/analysis/PUBLISHED_POLICY_COMMAND_GRID.md
status: HOLD_MOVEMENT_REQUIRES_OVER_ENVELOPE
```

Results:

```text
straight x=0.05:
  moving seeds: 0 / 2
  mean tracking ratio: 0.0664
  max-seed pitch-chain p95 target velocity: 2.7422 rad/s

straight x=0.06:
  moving seeds: 0 / 2
  mean tracking ratio: 0.0935
  max-seed pitch-chain p95 target velocity: 3.8816 rad/s

straight x=0.07:
  moving seeds: 0 / 2
  mean tracking ratio: 0.2171
  max-seed pitch-chain p95 target velocity: 3.6654 rad/s

scaled turning 0.50 -> 0.90:
  moving seeds: 0 / 2 at every tested scale
  mean tracking ratio range: 0.0641 -> 0.0995
  max-seed pitch-chain p95 target velocity range: 1.1501 -> 3.1335 rad/s

scaled turning 1.00:
  moving seeds: 2 / 2
  mean tracking ratio: 0.7874
  max-seed pitch-chain p95 target velocity: 5.0147 rad/s
```

This tightens the activation read: in the nearby command cells tested so far,
the published policy either stays under the measured envelope and does not move,
or moves only after the per-joint pitch-chain target-rate exceeds the measured
envelope. The published policy is therefore useful as a closed-loop movement
teacher, but not as an envelope-safe target template.

The teacher-window extractor then checked whether the moving published-policy
rollouts contain usable low-rate subsets:

```text
outputs/analysis/CLOSED_LOOP_TEACHER_TEMPLATE.md
status: PASS_HAS_LOW_RATE_MOVING_TEACHER_WINDOWS
```

Results:

```text
straight x=0.08:
  moving ticks: 89.55%
  moving + in-envelope ticks: 70.55%
  moving + single-support + in-envelope ticks: 32.80%
  safe moving single-support 0.1s future vx delta: +0.0039 m/s
  full-trace pitch velocity p95: 5.1961 rad/s

upstream turning command:
  moving ticks: 82.15%
  moving + in-envelope ticks: 63.70%
  moving + single-support + in-envelope ticks: 28.90%
  safe moving single-support 0.1s future vx delta: +0.0034 m/s
  full-trace pitch velocity p95: 4.9472 rad/s

straight x=0.04:
  moving + single-support + in-envelope ticks: 1.25%
  safe moving single-support 0.1s future vx delta: -0.0483 m/s
```

So the whole moving command cell is not envelope-safe, but it does contain
substantial low-rate moving windows with positive single-support future velocity
delta. Those windows are the better teacher substrate than either the full
published policy trajectory or the open-loop reference targets.

The existing realized-window dataset flow was then run on those windows:

```text
outputs/analysis/CLOSED_LOOP_TEACHER_WINDOW_CURATION.md
status: PASS_CURATED_DATASET_SEED_READY
curated windows: 259 / 301

outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_MANIFEST.md
status: PASS_TARGET_DATASET_MANIFEST_READY
entries: 259
source rollout dirs: 16
samples if loaded for BC: 6475

outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_SANITY_CHECK.md
status: PASS_TARGET_DATASET_SANITY_CHECK
bc_readiness_status: PASS_TARGET_DATASET_BC_READY
```

A tiny offline kNN behavior-cloning smoke over that manifest then replayed in
closed-loop sim:

```text
outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_BC_SMOKE.md
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
model: kNN, k=5
command: straight x=0.08
duration: 3s
seeds: 0, 1

seed 0:
  mean vx: 0.0688 m/s
  track ratio: 0.8594
  sent target velocity p95: 2.4224 rad/s
  joint tracking p95: 0.1207 rad

seed 1:
  mean vx: 0.0673 m/s
  track ratio: 0.8417
  sent target velocity p95: 2.5628 rad/s
  joint tracking p95: 0.1193 rad
```

A longer 8-seed, 5-second kNN replay gate then held:

```text
outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_BC_GATE_X008.md
status: HOLD_BC_REPLAY_TERMINATED
command: straight x=0.08
duration: 5s
seeds: 0-7

completed forward-moving seeds: 5 / 8
duration-complete but near-standstill seeds: 2 / 8
fall/reverse seed: 1 / 8
```

Representative outcomes:

```text
seed 0:
  mean vx: 0.0700 m/s
  track ratio: 0.8753
  sent target velocity p95: 2.4505 rad/s

seed 3:
  samples: 79
  termination: fall_or_progress_failure
  mean vx: -0.2268 m/s
  pitch p95: 1.1177 rad

seed 4:
  duration complete
  mean vx: 0.0074 m/s
  sent target velocity p95: 0.3667 rad/s

seed 7:
  duration complete
  mean vx: 0.0027 m/s
  sent target velocity p95: 0.3373 rad/s
```

This is not a deployable policy and not PPO training. The 2-seed smoke proved
the dataset can drive a toy closed-loop imitation replay, but the 8-seed gate
shows that the kNN student is not robust enough by itself. The useful next step
is still reviewed imitation/pretraining from the curated low-rate windows, but
it must be graded on multi-seed forward-motion consistency, not on the short
smoke result.

A sequence-preservation diagnostic then checked whether an averaged low-rate
teacher-window action table could replace the memoryless kNN lookup:

```text
outputs/analysis/CLOSED_LOOP_TEACHER_SEQUENCE_REPLAY_X008.md
status: HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION
policy_set: aggregate
phase_adapter: fixed_time
periodic_seam_correction: true

outputs/analysis/CLOSED_LOOP_TEACHER_SEQUENCE_REPLAY_X008_NO_SEAM.md
status: HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION
policy_set: aggregate
phase_adapter: fixed_time
periodic_seam_correction: false
```

Both variants completed all eight seeds without falling, but stayed near
standstill:

```text
seam-corrected aggregate:
  mean vx range: -0.0108 to +0.0111 m/s
  sent target velocity p95: 0.2660 rad/s

raw aggregate:
  mean vx range: -0.0105 to +0.0113 m/s
  sent target velocity p95: 0.2853 rad/s
```

So preserving a single averaged action loop is not enough. The next student
needs state-conditioned imitation from the curated windows. The aggregate
sequence table is too muted to produce propulsion, while the kNN lookup has
motion but lacks robustness.

An 8-seed linear ridge baseline was also run:

```text
outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_LINEAR_BC_GATE_X008.md
status: HOLD_BC_REPLAY_TERMINATED
model: linear ridge
command: straight x=0.08
duration: 5s
seeds: 0-7
```

It is smoother than the MLP, but does not move:

```text
moving seeds with vx >= 0.02 m/s: 0 / 8
mean vx range: -0.3080 to +0.0077 m/s
sent target velocity p95 range: 0.7319 to 3.0866 rad/s
terminated seeds: 1 / 8
```

This fills the student-baseline table: linear/aggregate sequence are too weak,
kNN preserves some motion but is seed-fragile, and MLP variants become
high-rate and low-progress.

A blended kNN+linear student was then tested to combine local motion with
smoothness:

```text
outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_BLEND075_BC_GATE_X008.md
status: HOLD_BC_REPLAY_LOW_FORWARD_MOTION
moving seeds: 5 / 8
terminated seeds: 0 / 8

outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_BLEND080_BC_GATE_X008.md
status: HOLD_BC_REPLAY_LOW_FORWARD_MOTION
moving seeds: 5 / 8
terminated seeds: 0 / 8

outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_BLEND090_BC_GATE_X008.md
status: HOLD_BC_REPLAY_TERMINATED
moving seeds: 4 / 8
terminated seeds: 1 / 8
```

Blend `0.80` is the best cheap student baseline so far:

```text
moving seeds: 0, 2, 3, 5, 6
near-standstill seeds: 1, 4, 7
mean vx on moving seeds: about 0.0445-0.0648 m/s
sent target velocity p95 on moving seeds: about 2.42-2.47 rad/s
```

It improves over raw kNN by removing the seed-3 fall/reverse while preserving
five moving seeds, but it does not solve the seed-dependent freeze. kNN `k=3`
was also tested and was worse than the original kNN `k=5`, reintroducing the
seed-3 fall while leaving seeds 1/4/7 near standstill.

A traced blend `0.80` replay then characterized the freeze mechanism:

```text
outputs/analysis/BLEND080_SEED_MODE_ANALYSIS.md
status: HOLD_FREEZE_LOW_ACTION_DOUBLE_SUPPORT
moving seeds: 0, 2, 3, 5, 6
frozen seeds: 1, 4, 7

moving group:
  mean vx ≈ 0.0586 m/s
  single support ≈ 46.24%
  double support ≈ 53.52%
  pitch-chain sent target velocity p95 ≈ 3.19 rad/s

frozen group:
  mean vx ≈ 0.0031 m/s
  single support ≈ 2.67%
  double support ≈ 97.20%
  pitch-chain sent target velocity p95 ≈ 0.40 rad/s
```

So the remaining blend failure is not an instability hidden by fall-count. It
is a quiet double-support dwell: on seeds 1/4/7 the model produces too little
closed-loop target motion after startup, never creates alternating single
support, and therefore never propels forward.

The matching traced raw kNN `k=5` replay shows the tradeoff:

```text
outputs/analysis/KNN5_SEED_MODE_ANALYSIS.md
status: HOLD_FREEZE_DOUBLE_SUPPORT
moving seeds: 0, 1, 2, 5, 6
fall/reverse seed: 3
double-support freeze seeds: 4, 7
```

Compared with blend `0.80`, raw kNN recovers seed `1` but loses seed `3`.
Seeds `4` and `7` freeze in both. The next student therefore needs an adaptive
closed-loop selection rule, not a single global kNN/linear blend: it must retain
enough kNN-local motion to escape double support on seed `1`, smooth the seed
`3` lunge, and add a separate pressure to recover seeds `4` and `7`.

A narrow global-blend sweep confirmed there is no obvious scalar coefficient
between the useful-but-frozen blend and the raw-kNN fall:

```text
blend 0.75: moving 0/2/3/5/6, freeze 1/4/7, no terminations
blend 0.80: moving 0/2/3/5/6, freeze 1/4/7, no terminations
blend 0.82: moving 0/2/3/5/6, freeze 1/4/7, no terminations
blend 0.85: moving 0/2/3/5/6, freeze 1/4/7, no terminations
blend 0.88: moving 0/2/3/5/6, freeze 1/4/7, no terminations
blend 0.90: moving 0/2/5/6, freeze 1/4/7, seed 3 terminates
```

So the next attempt should not keep sweeping global blend alpha. It needs
state-conditioned or closed-loop-selected imitation that can apply different
motion/smoothing tradeoffs in different rollout states.

A first state-conditioned selector was tested as `dwell_blend`: base blend
`0.80`, switch to raw kNN (`1.00`) after double-support dwell. It did not solve
the split:

```text
trigger 5 ticks:
  moving seeds: 0, 2, 5, 6
  frozen seeds: 1, 4, 7
  terminated seeds: 3

trigger 10 ticks:
  moving seeds: 0, 2, 3, 5, 6
  frozen seeds: 1, 4, 7
  terminated seeds: none

trigger 20 ticks:
  moving seeds: 0, 2, 3, 5, 6
  frozen seeds: 1, 4, 7
  terminated seeds: none
```

So simply switching to raw kNN after double-support dwell is either too late to
help the frozen seeds or early enough to bring back the seed-3 lunge. The next
student must learn/select a genuinely better local action, not only choose
between linear, blend, and raw kNN.

A velocity-gated blend then produced the first clear improvement over blend
`0.80`:

```text
outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_VX_BLEND080_100_VXNEG002_BC_GATE_X008.md
base blend: 0.80
raw-kNN blend: 1.00
switch condition: local vx >= -0.02 m/s
status: HOLD_BC_REPLAY_LOW_FORWARD_MOTION
moving seeds: 0, 1, 2, 3, 5, 6
frozen seeds: 4, 7
terminated seeds: none

outputs/analysis/VX_BLEND080_100_VXNEG002_SEED_MODE_ANALYSIS.md
moving group:
  mean vx ≈ 0.0672 m/s
  single support ≈ 51.00%
  pitch-chain sent target velocity p95 ≈ 3.17 rad/s

frozen group:
  mean vx ≈ 0.0050 m/s
  double support ≈ 97.60%
  pitch-chain sent target velocity p95 ≈ 0.48 rad/s
```

This selector keeps seed `3` alive while recovering seed `1`, which neither raw
kNN nor any global blend did. It does not solve the full gate because seeds `4`
and `7` still settle into quiet double-support dwell, but it is now the best
cheap baseline to beat.

A source-filtered velocity selector then cleared the offline replay gate:

```text
outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_SOURCE_VX_BLEND080_100_SRCVX002_ALT_EXCLUDE_SEED4_BC_GATE_X008.md
primary model: full curated teacher dataset
alternate model: same dataset excluding source labels matching _seed4/
alternate switch: local vx >= +0.02 m/s
internal blend switch: local vx >= -0.02 m/s
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
duration: 5s
moving seeds: 0, 1, 2, 3, 4, 5, 6, 7
terminated seeds: none
sent-target velocity p95 range: 2.4474-2.5315 rad/s

outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_SOURCE_VX_BLEND080_100_SRCVX002_ALT_EXCLUDE_SEED4_BC_GATE_X008_10S.md
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
duration: 10s
moving seeds: 0, 1, 2, 3, 4, 5, 6, 7
terminated seeds: none
sent-target velocity p95 range: 2.4293-2.4851 rad/s

outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_SOURCE_VX_BLEND080_100_SRCVX002_ALT_EXCLUDE_SEED4_FITTED_BRIDGE_BC_GATE_X008_10S.md
actuator bridge: fitted
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
duration: 10s
moving seeds: 0, 1, 2, 3, 4, 5, 6, 7
terminated seeds: none
track ratio range: 0.5491-0.6172
sent-target velocity p95 range: 2.2569-2.3622 rad/s
joint tracking p95 range: 0.1809-0.1863 rad

outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_SOURCE_VX_BLEND080_100_SRCVX002_ALT_EXCLUDE_SEED4_STRESS_BRIDGE_BC_GATE_X008.md
actuator bridge: stress
status: HOLD_BC_REPLAY_TERMINATED
result: stress bridge collapses forward progress and terminates seed 5

outputs/analysis/SOURCE_VX_SELECTOR_FITTED_BRIDGE_TRACE_MANIFEST.md
status: PASS_BC_TRACE_MANIFEST_READY
entries: 8
samples: 4000
purpose: distill the fitted-bridge source selector into a normal obs->action student

outputs/analysis/SOURCE_VX_SELECTOR_TRACE_BLEND080_FITTED_BRIDGE_BC_GATE_X008_10S.md
student: blend 0.80 over selector-trace manifest
source switch: none
local-vx switch: none
actuator bridge: fitted
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
duration: 10s
moving seeds: 0, 1, 2, 3, 4, 5, 6, 7
terminated seeds: none
track ratio range: 0.5170-0.6279
sent-target velocity p95 range: 2.0779-2.2134 rad/s
joint tracking p95 range: 0.1803-0.1843 rad

outputs/analysis/SOURCE_VX_SELECTOR_TRACE_MLP128_FITTED_BRIDGE_BC_GATE_X008_10S.md
student: MLP 128x128 over selector-trace manifest
actuator bridge: fitted
status: HOLD_BC_REPLAY_TERMINATED
result: all seeds fall/progress-fail with reverse velocity and high target rate

outputs/analysis/SOURCE_VX_SELECTOR_TRACE_MLP128_RATE_REG_FITTED_BRIDGE_BC_GATE_X008_10S.md
student: MLP 128x128 + target-rate regularizer over selector-trace manifest
actuator bridge: fitted
status: HOLD_BC_REPLAY_TERMINATED
result: one seed completes near standstill, most seeds still reverse/fall
sent-target velocity p95 range: 3.6588-4.4620 rad/s
```

The paired failed filters explain why the selector matters:

```text
exclude seed4 sources directly:
  recovers seeds 4/7 but makes seed 3 terminate

exclude seed7 sources directly:
  same freeze split as before

dual-source selector:
  uses the seed4-excluded model only when local vx is already positive
  keeps seed 3 on the safer primary model during negative-vx states
```

This is the first offline imitation-selector result that gets all eight seeds
moving at straight `x=0.08` in vanilla CPU sim while staying low-rate. It is
still not robot-ready: it started as a diagnostic selector over teacher windows,
not a trained exported policy. A follow-up trace-distillation pass produced a
source-switch-free blend student that also passes the 10s fitted actuator bridge
gate, but the small neural MLP distillation still fails and no hardware test has
been run.

The focused student decision artifact is:

```text
outputs/analysis/STUDENT_IMITATION_BASELINE_DECISION.md
status: PASS_TRACE_BLEND_STUDENT_FITTED_BRIDGE_SMOKE
```

A first plain state-conditioned MLP BC smoke was then added to the same tool and
run locally on CPU:

```text
outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_MLP_BC_GATE_X008.md
status: HOLD_BC_REPLAY_LOW_FORWARD_MOTION
model: JAX/Optax MLP, 64x64, 1000 supervised steps
command: straight x=0.08
duration: 5s
seeds: 0-7
```

It completed all eight seeds, but did not produce robust forward motion and
hit the runtime target-rate limit:

```text
mean vx range: -0.0225 to +0.0296 m/s
moving seeds with vx >= 0.02 m/s: 1 / 8
sent target velocity p95: 5.2400 rad/s on every seed
action delta p95: about 39-49 /s
```

That rules out a naive one-step MLP clone as the missing student. It can fit the
dataset offline, but the closed-loop rollout becomes high-rate and low-progress.
Two first regularized variants were also tested:

```text
outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_MLP_RATE_REG_BC_GATE_X008.md
status: HOLD_BC_REPLAY_TERMINATED
regularization: predicted target-rate penalty over 3.75 rad/s

outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_MLP_CONSISTENCY_BC_GATE_X008.md
status: HOLD_BC_REPLAY_TERMINATED
regularization: observation-noise consistency
```

Both still hit `5.2400 rad/s` sent-target velocity p95 on every seed and added
fall/reverse terminations. The local regularizers did not keep the closed-loop
student on the low-rate teacher manifold. The next imitation design therefore
needs closed-loop target-rate/action-smoothness selection or training feedback,
not just lower supervised action error and not only offline pairwise/noise
regularization.

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
acceleration. The low-rate teacher-window dataset is a better substrate than
the full over-envelope trace, but the first kNN student still has seed-dependent
fall/freeze modes.

Current decision: do not continue with another stance-relative lateral-damping
teacher variant by default. The command-grid search did not find an
envelope-safe published-policy command cell in the nearby straight/turning
region, but the moving command traces contain meaningful low-rate moving
subsets. The next offline branch should mine those low-rate closed-loop windows
as the teacher. The manifest and kNN BC smoke show that this substrate can
preserve forward movement inside the envelope for a short closed-loop replay,
while the 8-seed gate shows that a simple kNN student is not sufficient and the
aggregate sequence smoke shows that a single averaged action loop is too weak.
The plain MLP BC smoke shows that one-step supervised accuracy alone can still
produce high-rate, low-progress closed-loop behavior, and the first offline
rate/consistency regularizers do not fix that. The next offline branch should
be a reviewed state-conditioned imitation/pretraining experiment from this
dataset with closed-loop target-rate/action-smoothness selection or training
feedback, graded on longer multi-seed closed-loop gates and max-joint
pitch-chain p95 target velocity. Robot validation remains blocked.

## 2026-06-25: DAgger Relabeling Produces First Exportable Neural Smoke Pass

The first source-switch-free blend student remained the best fitted-bridge
behavioral baseline, but it was not an exported policy. A DAgger-style offline
relabeling pass was added to turn student-visited states back into safer blend
teacher actions without running the robot:

```text
tools/relabel_bc_trace_actions.py
```

The first relabel pass took failed 128x128 MLP rollout states and relabeled
them with the blend teacher:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_MLP128_RELABEL_BLEND.md
status: PASS_BC_TRACE_RELABEL_READY
samples_out: 1166
```

Training a 128x128 MLP on the original selector trace plus those relabeled
states improved the failure from all-seed collapse to one remaining failure:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER1_MLP128_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: HOLD_BC_REPLAY_TERMINATED
result: 7 / 8 seeds completed; seed 5 fell/reversed
```

A second relabel pass added 3602 DAgger-1 student-visited states, producing a
24-entry / 8768-sample manifest:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER2_MANIFEST.md
status: PASS_BC_TRACE_MANIFEST_READY
dataset_id: 29210cfbb880ecb9
```

The DAgger-2 128x128 MLP is the first compact neural student to pass the
10-second fitted actuator bridge smoke:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER2_MLP128_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
moving seeds: 8 / 8
terminated seeds: 0 / 8
track ratio range: 0.5208-0.6182
sent-target velocity p95 range: 2.1174-2.1601 rad/s
joint tracking p95 range: 0.1770-0.1813 rad
```

The MLP was exported to ONNX and verified against the NumPy/JAX-side MLP:

```text
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_candidate/candidate.onnx
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_candidate/candidate_mlp.npz
onnx verify max_abs_error: 4.172325e-07
contract: obs[1,101] -> continuous_actions[1,14]
```

The standard closed-loop ONNX evaluator also completed with the fitted bridge
on CPU:

```text
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_onnx_eval/CLOSED_LOOP_ACTUATOR_BRIDGE_EVAL.md
status: PASS_CLOSED_LOOP_REPRODUCTION
duration: 10s / 500 samples
mean local vx: 0.0197 m/s
track ratio: 0.2457
sent-target p95 max pitch-chain joint: 3.8533 rad/s
terminated: no
```

This is an exportability milestone, not a robot milestone. The DAgger-2 ONNX
candidate is portable and survives the local fitted-bridge smoke, but the
standard evaluator shows low commanded-speed tracking and the right knee still
exceeds the fitted envelope. It remains offline-only. The next step is stricter
offline review of the exported ONNX behavior, especially multi-seed standard
ONNX evaluation and stress-bridge margin, before any robot-side discussion.

The first multi-seed standard ONNX fitted-bridge review confirms that caveat:

```text
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_onnx_multiseed_fitted/MULTISEED_FITTED_SUMMARY.md
status: HOLD_DAGGER2_ONNX_MULTI_SEED_LOW_FORWARD_PROGRESS
duration complete: 6 / 8
moving seeds with track ratio >= 0.5: 0 / 8
moving seeds with mean local vx >= 0.02 m/s: 4 / 8
mean track ratio: 0.2526
mean local vx: 0.0202 m/s
early terminations: seeds 1 and 7
```

That first standard review used the default `flat_terrain` task, while the
DAgger smoke gate used `flat_terrain_backlash`. A task-matched standard ONNX
review on `flat_terrain_backlash` shows the export is much closer to the smoke
gate, but still not promotion-ready:

```text
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_onnx_multiseed_fitted_backlash/MULTISEED_FITTED_BACKLASH_SUMMARY.md
status: HOLD_DAGGER2_ONNX_BACKLASH_LOW_FORWARD_PROGRESS
duration complete: 8 / 8
moving seeds with track ratio >= 0.5: 7 / 8
moving seeds with mean local vx >= 0.02 m/s: 8 / 8
mean track ratio: 0.5409
mean local vx: 0.0433 m/s
max pitch-chain sent-target p95 range: 4.5943-4.8522 rad/s
```

The task-matched run closes the earlier task-confound, but the exported MLP
still overdrives the right-knee pitch-chain target relative to the fitted
envelope and remains a hold. A scalar action-gain screen does not solve that:

```text
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_onnx_gain_screen_backlash/GAIN_SCREEN_SUMMARY.md
status: HOLD_GAIN_SCREEN_NO_ENVELOPE_SAFE_MOTION
screen: gains 0.9, 0.8, 0.7, 0.6 on seeds 0 and 3
result: no gain preserves track ratio >= 0.5 while keeping max pitch-chain p95 <= 3.75 rad/s
```

So the ONNX export path is working, but the exported DAgger-2 MLP is not a
promotion candidate. The source-switch-free blend student remains the stronger
offline behavior baseline; the ONNX student needs better closed-loop
distillation or a different portable policy class before any robot gate.

The existing pairwise target-rate regularizer was then tested on the DAgger-2
manifest at lighter and stronger scales:

```text
outputs/analysis/source_vx_selector_trace_dagger2_mlp128_rate_reg_scale_screen_backlash/RATE_REG_SCALE_SCREEN_SUMMARY.md
status: HOLD_RATE_REG_SCALE_SWEEP_NO_BALANCED_PASS
screen: target_rate_scale 0.03, 0.05, 0.10 on seeds 0 and 3
```

The regularizer forms the expected tradeoff but does not solve it:

```text
scale 0.03:
  mean track ratio 0.4583
  max pitch-chain sent-target p95 3.7688 rad/s

scale 0.05:
  mean track ratio 0.4571
  max pitch-chain sent-target p95 3.6952 rad/s

scale 0.10:
  mean track ratio 0.4104
  max pitch-chain sent-target p95 3.6419 rad/s
```

So increasing the current pairwise target-rate penalty is not the next best
branch. It can buy envelope compliance, but it does so by weakening forward
motion below the gate. The next portable student needs a different objective or
policy class that preserves the blend/selector closed-loop behavior while
reducing the right-knee target-rate peak.

An exact kNN+ridge blend ONNX export was then added for the source-switch-free
blend baseline. The exporter keeps the kNN training set inside the ONNX graph
and verifies against the Python blend to numerical precision:

```text
outputs/analysis/source_vx_selector_trace_blend080_exact_onnx_candidate/candidate.onnx
size: 1.8 MB
contract: obs[1,101] -> continuous_actions[1,14]
onnx verify max_abs_error: 1.192093e-07
```

The Python-side fitted-bridge smoke remains a pass:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_BLEND080_EXACT_ONNX_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
moving seeds: 8 / 8
terminated seeds: 0 / 8
track ratio range: 0.5170-0.6279
sent-target velocity p95 range: 2.0779-2.2134 rad/s
```

The stricter task-matched standard ONNX evaluator shows the export preserves
forward motion better than the DAgger-2 MLP, but it is still not
promotion-ready:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_BLEND080_EXACT_ONNX_MULTI_SEED_FITTED_BACKLASH_SUMMARY.md
status: HOLD_EXACT_BLEND_ONNX_RIGHT_KNEE_RATE_TRACKING
duration complete: 8 / 8
moving seeds with track ratio >= 0.5: 8 / 8
mean track ratio: 0.5768
mean local vx: 0.0461 m/s
max pitch-chain sent-target p95 range: 4.7355-5.1118 rad/s
max pitch-chain tracking p95 range: 0.2679-0.2800 rad
dominant failure joint: right_knee
```

This closes export fidelity as the issue for the blend baseline. The remaining
problem is not ONNX approximation loss; it is that the source-switch-free blend
itself carries a hidden max-joint pitch-chain rate/tracking violation in the
standard evaluator, dominated by the right knee. The next branch should target
that joint/rate mechanism directly instead of further proving exportability.

A focused seed-3 trace diagnostic characterizes that right-knee failure:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_BLEND080_EXACT_ONNX_RIGHT_KNEE_SPIKE_DIAGNOSTIC.md
status: HOLD_RIGHT_KNEE_CYCLIC_RATE_SPIKES
joint: right_knee
events over 3.75 rad/s: 62 / 499 target deltas (12.42%)
cluster count: 32
cluster length: 1-3 ticks
max sent velocity: 5.2400 rad/s
high-event contacts: 11=39, 10=21, 01=2
```

The high-rate events are short cyclic bursts, often clipped at the runtime
`5.24 rad/s` slew ceiling, and occur mostly during double support. That makes
the next offline target more specific: preserve the blend's forward motion but
remove the right-knee phase/target discontinuity. Another broad export or
global damping pass is unlikely to answer that mechanism.

The source trace manifest itself contains the same hidden discontinuity:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_MANIFEST_RIGHT_KNEE_RATE_DIAGNOSTIC.md
status: HOLD_TEACHER_TRACE_RIGHT_KNEE_RATE_DISCONTINUITIES
dataset_id: de4935ec7672ceea
right-knee deltas over 3.75 rad/s: 506 / 3992 (12.68%)
max implied target velocity: 8.3015 rad/s
high-event contacts: 11=297, 10=208, 00=1
```

This means the exact blend ONNX did not invent the right-knee spikes. It
faithfully exported a teacher-data problem that the earlier flattened
sent-target velocity metric hid. The next branch should re-curate or relabel
the selector trace dataset with max-joint/per-joint right-knee target-rate
constraints before exporting another portable student.

An offline right-knee action-rate curation helper was then added and screened
against the selector trace dataset:

```text
tools/rate_limit_bc_trace_actions.py
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_RIGHT_KNEE_RATE_LIMIT_SWEEP_SUMMARY.md
status: HOLD_RIGHT_KNEE_RATE_LIMIT_CURATION_NOT_ROBOT_READY
```

The sweep confirms the source-data mechanism but does not produce a
robot-ready candidate:

```text
right-knee cap 4.7 rad/s:
  changed ticks: 408
  smoke replay: PASS, 8 / 8 complete, 8 / 8 moving

right-knee cap 4.3 rad/s:
  changed ticks: 493
  smoke replay: PASS, 8 / 8 complete, 8 / 8 moving
  strict ONNX backlash gate: HOLD_STRICT_EVAL_TARGET_VELOCITY_GATE
  strict max pitch-chain sent-target p95: 4.2994 rad/s
  strict max pitch-chain tracking p95: 0.2773 rad
  worst / fastest joint: right_knee on all 8 seeds

right-knee caps 4.0 and 3.75 rad/s:
  smoke replay: HOLD, seed 5 terminates
```

Compared with the uncurated exact blend strict ONNX summary, the `4.3 rad/s`
curation reduces max pitch-chain sent-target p95 from about `5.1118` to
`4.2994 rad/s` while preserving all-seed forward replay. It still does not
reach the conservative `2.5 rad/s` gate or the fitted-envelope `3.75 rad/s`
check, and right-knee tracking remains near `0.27 rad` p95. This means simple
one-joint hard clipping is a useful diagnostic and a partial mitigation, but
not the next deployable path. The next curation pass should reject or relabel
bad right-knee phase/contact windows, or apply dynamics-aware multi-joint
smoothing, instead of just pushing the right-knee cap lower.

The published BEST_WALK policy was then compared across command cells using the
same upstream-main `flat_terrain_backlash` closed-loop propulsion audit:

```text
outputs/analysis/PUBLISHED_POLICY_COMMAND_PROPULSION_COMPARISON.md
status: PASS_POLICY_COMMAND_PROPULSION_COMPARISON
```

Result:

```text
straight x=0.04:
  duration complete: 8 / 8
  moving seeds: 0 / 8
  envelope-safe seeds: 8 / 8
  mean local vx: 0.0019 m/s
  single support: 3.65%

upstream nearest turning key x=0.074, y=-0.037, yaw=-0.074:
  duration complete: 8 / 8
  moving seeds: 7 / 8
  envelope-safe seeds: 1 / 8
  mean local vx: 0.0540 m/s
  max pitch-chain sent-target p95: 5.2400 rad/s

straight x=0.08:
  duration complete: 8 / 8
  moving seeds: 7 / 8
  envelope-safe seeds: 0 / 8
  mean local vx: 0.0640 m/s
  max pitch-chain sent-target p95: 5.2400 rad/s
```

This means the earlier straight `x=0.04` walking gate was not a proven-easy
cell; even the published policy mostly stands there while staying within the
measured pitch-chain envelope. The moving command cells confirm that
closed-loop walking exists in sim, but they also confirm the same right-knee
rate mechanism: walking uses target rates near the runtime slew ceiling. The
next training/eval re-entry should extract the single-support/CoM mechanism
from the moving command cells while reducing right-knee target rate, rather
than assuming BEST_WALK is already an in-envelope walking proof.

The closed-loop template extractor then split those traces into command cells:

```text
outputs/analysis/PUBLISHED_POLICY_COMMAND_CLOSED_LOOP_TEMPLATE.md
status: PASS_HAS_LOW_RATE_MOVING_TEACHER_WINDOWS
```

It shows why the command comparison is not just a binary pass/hold:

```text
straight x=0.04:
  moving in envelope: 4.65%
  moving single-support in envelope: 1.25%

upstream nearest turning key:
  moving in envelope: 63.70%
  moving single-support in envelope: 28.90%
  pitch p95: 4.9472 rad/s

straight x=0.08:
  moving in envelope: 70.55%
  moving single-support in envelope: 32.80%
  pitch p95: 5.1961 rad/s
```

So the moving BEST_WALK traces contain useful low-rate moving windows, but the
whole trace is not envelope-safe. The next data source should mine those
moving single-support in-envelope windows and reject or relabel the high
right-knee burst windows before BC/export.

A dedicated closed-loop teacher window miner then checked whether those
aggregate low-rate ticks form contiguous teacher snippets:

```text
tools/mine_closed_loop_teacher_windows.py

25-tick / 0.50s windows:
  outputs/analysis/CLOSED_LOOP_TEACHER_WINDOW_MINE.md
  status: HOLD_INSUFFICIENT_CLOSED_LOOP_WINDOWS
  pass windows: 0 / 1104

10-tick / 0.20s windows:
  outputs/analysis/CLOSED_LOOP_TEACHER_WINDOW_MINE_10T.md
  status: PASS_CURATED_CLOSED_LOOP_WINDOWS_FOUND
  pass windows: 142 / 2904
```

The 10-tick passing windows are mostly from the moving command cells:

```text
upstream nearest turning key: 76 passing windows
straight x=0.08: 63 passing windows
straight x=0.04: 3 passing windows
```

This tightens the next source-design rule:

```text
BEST_WALK contains brief envelope-safe moving single-support snippets.
It does not yet provide sustained 25-tick envelope-safe moving windows.
```

So the next candidate source should not copy full BEST_WALK traces. It should
mine short safe snippets as motion/phase evidence, then build a continuity
mechanism that bridges between those snippets without reintroducing the
right-knee high-rate bursts.

The first continuity check then tested whether the 10-tick passing snippets
can be merged into longer contiguous windows:

```text
tools/plan_closed_loop_snippet_stitching.py

outputs/analysis/CLOSED_LOOP_SNIPPET_STITCH_PLAN.md
status: HOLD_STITCH_RUNS_TOO_SHORT

short pass windows: 142
stitch runs: 86
passing stitch runs: 84
traces with >=25-tick pass runs: 0
traces with >=50-tick pass runs: 0
max passing stitch span: 18 ticks
```

By command cell:

```text
upstream nearest turning key:
  76 short pass windows
  max passing stitch span: 12 ticks

straight x=0.04:
  3 short pass windows
  max passing stitch span: 12 ticks

straight x=0.08:
  63 short pass windows
  max passing stitch span: 18 ticks
```

This rules out direct BC from stitched BEST_WALK snippets as the next clean
step. The safe closed-loop behavior is fragmented into local sub-step hints,
not sustained 25-50 tick teacher windows. The next source needs an explicit
continuity/generation mechanism, or a different closed-loop imitation route,
before export or training.

The next comparative stance-timing read checked the full-observation foot
position traces across straight `x=0.04`, straight `x=0.08`, and the upstream
turning command:

```text
tools/analyze_published_policy_stance_timing.py
outputs/analysis/PUBLISHED_POLICY_STANCE_TIMING_COMPARISON.md
status: PASS_STANCE_TIMING_COMPARISON_READY
```

Key command-cell averages:

| command cell | mean vx | single support | single alternations | single-support dvx @ 0.1s | pitch p95 |
|---|---:|---:|---:|---:|---:|
| straight `x=0.04` | 0.0019 m/s | 3.65% | 1.50 | -0.0155 m/s | 0.8647 rad/s |
| straight `x=0.08` | 0.0640 m/s | 49.40% | 17.63 | 0.0030 m/s | 3.2849 rad/s |
| upstream turning key | 0.0540 m/s | 44.80% | 16.25 | 0.0042 m/s | 3.2396 rad/s |

This makes the command-cell split explicit. Straight `x=0.04` is not a
walking existence proof for BEST_WALK: it stays in double support about 96% of
the time and its rare single-support ticks are followed by negative local
forward velocity change. The moving command cells enter alternating single
support and produce positive future forward velocity deltas, but they do so
with much higher pitch-chain target velocity. The next learning target should
start from the command cells where closed-loop stance transfer actually exists,
not from straight `x=0.04` as a walking gate.

The follow-up rule-candidate analysis compared short full-observation windows
that pass the movement/contact/envelope gate against windows that move but
exceed the pitch-chain target-rate envelope:

```text
tools/analyze_closed_loop_window_rule_candidates.py
outputs/analysis/CLOSED_LOOP_WINDOW_RULE_CANDIDATES.md
status: PASS_RULE_CONTRAST_READY
```

Bucket averages:

| bucket | windows | mean vx | single support | moving in envelope | pitch p95 | right knee p95 | action delta p95 |
|---|---:|---:|---:|---:|---:|---:|---:|
| pass safe moving single | 330 | 0.0721 m/s | 46.79% | 81.61% | 3.2896 rad/s | 2.1407 rad/s | 0.1678 |
| reject high-rate moving | 1233 | 0.0667 m/s | 53.10% | 64.13% | 4.7046 rad/s | 4.0445 rad/s | 0.2053 |
| reject low progress | 1214 | 0.0008 m/s | 5.88% | 2.65% | 0.8400 rad/s | 0.6684 rad/s | 0.0497 |

The important contrast is that passing and high-rate moving windows have
similar forward speed and single-support occupancy. The difference is not
"more contact" or "more forward motion"; it is target-rate management during
that stance transfer. Fastest-pitch-joint counts were dominated by knees:

```text
right_knee: 1360 windows
left_knee: 1048 windows
right_hip_pitch: 247 windows
```

So the next closed-loop source should explicitly manage knee target-rate while
preserving the moving command cells' alternating single-support pattern. A
selector that only keys on contact state will reproduce high-rate moving
windows as well as safe ones.

The first knee-rate-aware selector manifest then filtered for passing moving
windows with an explicit right-knee p95 cap:

```text
tools/build_knee_rate_selector_manifest.py
outputs/analysis/KNEE_RATE_SELECTOR_MANIFEST.md
status: HOLD_SELECTOR_MISSING_STANCE_SIDE

entries: 313
covered phase bins: 5 / 8
stance side coverage:
  double: 178
  right_stance: 135
  left_stance: 0
```

Relaxing the right-knee cap to the full `3.75 rad/s` envelope did not recover
left-stance coverage:

```text
pass all center contacts: 11 = 200, 01 = 129, 10 = 1
pass all majority contacts: 11 = 195, 01 = 135, 10 = 0
```

So the currently mined safe BEST_WALK source is one-sided: it contains
right-stance plus double-support safe windows, but essentially no left-stance
safe windows. It is not a balanced selector-training source. The next branch
must either recover the missing left-stance mechanism, mirror/symmetrize with
verification, or use a different closed-loop source. Do not train from this
manifest as-is.

The left-stance gap analysis then checked whether left stance is absent or
present-but-unsafe:

```text
tools/analyze_left_stance_gap.py
outputs/analysis/LEFT_STANCE_GAP_ANALYSIS.md
status: WARN_LEFT_STANCE_EXISTS_BUT_NOT_IN_SELECTOR

total windows: 2904
left-related windows: 553
```

Left stance exists, but it is almost always excluded by high pitch-chain target
rate:

| contact group | windows | pass | mean vx | pitch p95 | right knee p95 | left knee p95 | top reason |
|---|---:|---:|---:|---:|---:|---:|---|
| center left / majority left | 388 | 0 | 0.0600 | 5.1021 | 5.0757 | 2.6358 | high pitch velocity |
| center left / majority double | 94 | 1 | 0.0579 | 5.0024 | 4.9303 | 2.1449 | high pitch velocity |
| center right / majority right | 362 | 102 | 0.0693 | 3.6390 | 1.9382 | 3.6082 | mixed |
| center double / majority right | 64 | 33 | 0.0605 | 3.3411 | 2.6167 | 3.1245 | mixed |

This says the missing selector side is not a contact-absence problem. It is a
side-specific rate problem: when the policy is in left stance, the right knee
often hits the target-rate ceiling. When the policy is in right stance, the
right knee is much quieter and windows can pass. The next recovery branch
should target left-stance/right-knee burst suppression or verified symmetry,
not another generic contact selector.

An offline relabeling probe then tested whether capping only the right-knee
target rate can recover those unsafe left-stance windows:

```text
tools/analyze_left_stance_rate_recovery.py
outputs/analysis/LEFT_STANCE_RATE_RECOVERY.md
status: PASS_RIGHT_KNEE_RELABEL_RECOVERS_LEFT_STANCE

right_knee_cap: 3.61 rad/s
left-related windows: 553
original pass windows: 1
relabeled pass windows: 343
relabeled pass pct: 62.03%
```

By contact group:

| group | windows | original pass | relabeled pass | relabeled pass % |
|---|---:|---:|---:|---:|
| center left / majority left | 388 | 0 | 242 | 62.37% |
| center left / majority double | 94 | 1 | 70 | 74.47% |
| center double / majority left | 64 | 0 | 31 | 48.44% |

This says the left-stance gap is likely recoverable by target-rate relabeling,
at least as an offline selector source. The next artifact should build a
balanced relabeled selector manifest and then re-score 25-50 tick continuity.
Do not train yet; this has not been stepped through sim.

That balanced source now exists:

```text
tools/build_relabelled_balanced_selector_manifest.py
outputs/analysis/RELABELLED_BALANCED_SELECTOR_MANIFEST.md
status: PASS_BALANCED_SELECTOR_SOURCE_READY

entries: 672
phase bins: 8 / 8
left_stance: 273
right_stance: 135
double: 264
right_knee_rate_cap relabelled entries: 343
original entries: 329
```

This is the first selector source in the closed-loop teacher branch that has
both stance sides and full phase-bin coverage while respecting the measured
pitch-chain envelope in the scored windows. It is still not training-ready:
the entries are local windows, not a verified closed-loop sequence. The next
required artifact is a 25-50 tick continuity/replay score using this manifest.

The first continuity score over that manifest now passes the offline 50-tick
gate:

```text
tools/score_relabelled_selector_continuity.py
outputs/analysis/RELABELLED_SELECTOR_CONTINUITY_SCORE.md
status: PASS_SELECTOR_CONTINUITY_50_TICKS

runs: 101
pass runs: 98
max pass span: 96 ticks
pass runs >=25 ticks: 20
pass runs >=50 ticks: 11
pass runs using relabel: 92
```

Longest passing run:

```text
source: published_policy_command_straight_x008_seed1
ticks: 154-249
span: 96 ticks
mean vx: 0.0719 m/s
single support: 52.08%
moving in envelope: 92.71%
moving single-support in envelope: 48.96%
pitch p95: 3.61 rad/s
```

This is the first source in this branch that has balanced stance/phase coverage
and sustained 50+ tick offline continuity. It is still not training-ready: the
right-knee relabeling has not been stepped through sim. The next required gate
is a bounded sim replay of the relabeled selector spans before BC/export.

That bounded sim replay now exists and is a hold:

```text
tools/build_relabelled_selector_replay_manifest.py
tools/run_target_sequence_replay_smoke.py
outputs/analysis/RELABELLED_SELECTOR_REPLAY_MANIFEST.md
outputs/analysis/RELABELLED_SELECTOR_SEQUENCE_REPLAY_TOP3_5S.md
status: HOLD_SEQUENCE_REPLAY_TERMINATED
```

Top-three 5s CPU replay result:

```text
seed 0:
  all 3 top spans complete 250 samples
  mean vx: 0.0440-0.0475 m/s
  sent target velocity p95: 2.54-3.04 rad/s
  body pitch p95: 0.0466-0.1134 rad

seed 1:
  all 3 top spans terminate at 33-38 samples
  mean vx: -0.0913 to -0.0690 m/s
  vy p95: 1.0380-1.1032 m/s
  body pitch p95: 0.3202-0.3678 rad
```

Interpretation: the relabeled spans can step in sim and produce bounded
forward motion from at least one reset seed, but they are not seed-robust and
are not ready for BC/export. The failures happen before the selected window on
seed 1, so the next branch should focus on state alignment or a closed-loop
selector policy instead of treating the sequence table as a deployable teacher.

A source-vs-replay divergence audit confirms that the prefix replay is already
off the source trajectory before the selected window:

```text
tools/analyze_selector_replay_divergence.py
outputs/analysis/RELABELLED_SELECTOR_REPLAY_DIVERGENCE.md
status: HOLD_REPLAY_DIVERGES_BEFORE_SELECTOR_WINDOW
```

All six checked replay traces diverge before `prefix_end`; first divergence is
tick 0 for five of six traces and tick 5 for the remaining trace. Seed 1 has
large lateral velocity error (`vy` p95 about 1.11-1.24 m/s) and contact
mismatch 60.5-81.8% before it terminates. This means open-loop prefix replay
cannot recreate the source state reliably. The next useful branch is
state-aligned replay or a closed-loop selector, not a longer static sequence.

Exact state-aligned replay is blocked on trace contents:

```text
outputs/analysis/SELECTOR_STATE_ALIGNMENT_REQUIREMENTS.md
status: HOLD_STATE_ALIGNMENT_TRACE_CONTRACT_INCOMPLETE
```

Current traces have base position, pitch, local velocity, joint position,
targets, contacts, foot sites, and observations. They do not include full
`qpos`, `qvel`, base quaternion, control state, or motor-target/action-history
state. Do not approximate exact state alignment from partial state. Either
regenerate source traces with full state or build a closed-loop selector that
acts from the current observation/contact state.
