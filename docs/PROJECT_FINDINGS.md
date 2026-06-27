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

## 2026-06-26: Source-VX Selector Proves Feasibility; Pivot to Deployable Policy Validation

The source-VX selector result is the strongest positive feasibility result in
the campaign:

```text
outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_SOURCE_VX_BLEND080_100_SRCVX002_ALT_EXCLUDE_SEED4_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
command: straight x=0.08
duration: 10s
moving seeds: 8 / 8
terminated seeds: 0 / 8
track ratio range: 0.5491-0.6172
sent-target velocity p95 range: 2.2569-2.3622 rad/s
```

This proves that in-envelope forward motion exists in the fitted-bridge sim
proxy across all eight seeds. The morphology-wall hypothesis is no longer the
right default explanation.

The source-VX selector itself is still not a deployable policy. It is a
diagnostic kNN/blend selector over teacher windows. It has done its job by
proving feasibility, and further selector knob tuning should not be the default
path.

The deployable-policy evidence is now more nuanced than the earlier "MLP
distillation failed" result. The first plain 128x128 MLP did fail:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_MLP128_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: HOLD_BC_REPLAY_TERMINATED
```

But DAgger relabeling later produced exportable neural smoke passes:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER2_MLP128_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
ONNX: outputs/analysis/source_vx_selector_trace_dagger2_mlp128_candidate/candidate.onnx
moving seeds: 8 / 8
terminated seeds: 0 / 8
sent-target velocity p95 range: 2.1174-2.1601 rad/s

outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER2_MLP128_RATE_REG_ONNX_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
ONNX: outputs/analysis/source_vx_selector_trace_dagger2_mlp128_rate_reg_candidate/candidate.onnx
moving seeds: 8 / 8
terminated seeds: 0 / 8
sent-target velocity p95 range: 2.1256-2.1971 rad/s
```

Those are not robot-ready gates. They are the first deployable-policy-shaped
objects worth validating. The next branch should therefore be:

```text
PLAN_DEPLOYABLE_POLICY_VALIDATION_AND_WARMSTART
```

Required next artifact:

```text
outputs/analysis/SOURCE_VX_SELECTOR_POLICY_PIVOT.md
status: PLAN_DEPLOYABLE_POLICY_VALIDATION_AND_WARMSTART
```

Compare the DAgger-2 and DAgger-2 rate-reg ONNX candidates under stricter
offline fitted/stress bridge gates before any PPO or robot discussion. If a
candidate survives that review, the next training move is PPO fine-tuning from
the BC/DAgger policy with the fitted actuator bridge active. If not, expand the
selector-rollout dataset and repeat DAgger/BC. Do not resume selector refinement
as the primary path unless candidate validation identifies a concrete missing
teacher state.

That stricter fitted-bridge validation now exists:

```text
outputs/analysis/DEPLOYABLE_SOURCE_VX_POLICY_VALIDATION.md
status: HOLD_DEPLOYABLE_POLICY_TRACKING_RATE_TRADEOFF
```

Default `flat_terrain` was a hold for both candidates, with falls and low
progress. The task-matched `flat_terrain_backlash` gate is more informative:

```text
dagger2:
  duration complete: 8 / 8
  mean track ratio: 0.5409
  max sent-target velocity p95: 4.8522 rad/s
  tracking p95: 0.2626-0.2650 rad
  result: HOLD_CANDIDATE_TRACKING

dagger2_rate_reg:
  duration complete: 8 / 8
  mean track ratio: 0.4550
  max sent-target velocity p95: 3.6824 rad/s
  tracking p95: 0.2419-0.2472 rad
  result: HOLD_CANDIDATE_TRACKING
```

Neither ONNX candidate is robot-ready. The plain DAgger-2 student preserves
more forward progress but overdrives target rate. The rate-regularized student
brings target rate near the fitted envelope but still tracks poorly and loses
progress. The next branch should target this neural student tracking/rate
tradeoff directly with expanded on-policy DAgger relabeling and/or PPO
fine-tuning from the BC policy with the fitted bridge active. Do not run stress
or robot gates until the fitted tracking gate improves.

One more on-policy DAgger relabel pass was tested from the DAgger-2 rate-reg
student-visited states:

```text
outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER2_RATE_REG_STANDARD_RELABEL_BLEND.md
status: PASS_BC_TRACE_RELABEL_READY
samples_out: 4000

outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER3_MANIFEST.md
status: PASS_BC_TRACE_MANIFEST_READY
dataset_id: 80ea809b021b6b9a
entries: 25
samples: 9268
```

The DAgger-3 rate-reg MLP passes the BC smoke but still holds under the
standard task-matched fitted gate:

```text
outputs/analysis/DAGGER3_RATE_REG_POLICY_VALIDATION.md
status: HOLD_DAGGER3_TRACKING_RATE_REGRESSION

mean track ratio: 0.5255
sent-target velocity p95 range: 3.7121-3.8488 rad/s
tracking p95 range: 0.2623-0.2767 rad
```

Compared with DAgger-2 rate-reg, DAgger-3 improves forward progress but
regresses target-rate and tracking margin. That suggests another pure BC relabel
pass is unlikely to solve the core gate by itself. The next branch should add
tracking/target-rate feedback to the student objective or PPO fine-tune from
the BC warm start with the fitted actuator bridge active.

A PPO-shape BC student was then trained from the same DAgger-3 manifest using
the local Playground PPO policy hidden sizes `(512, 256, 128)`:

```text
outputs/analysis/PPO_SHAPE_BC_WARMSTART_CANDIDATE.md
status: HOLD_PPO_SHAPE_TRACKING_GATE

ONNX: outputs/analysis/source_vx_selector_trace_dagger3_mlp512_256_128_rate_reg_candidate/candidate.onnx
NPZ:  outputs/analysis/source_vx_selector_trace_dagger3_mlp512_256_128_rate_reg_candidate/candidate_mlp.npz

task-matched fitted gate:
  duration complete: 8 / 8
  falls: 0 / 8
  mean track ratio: 0.4953
  sent-target velocity p95 range: 3.7842-3.8409 rad/s
  tracking p95 range: 0.2570-0.2684 rad
```

This is not an improved policy candidate. It is slightly lower-progress than
the 128x128 DAgger-3 student and still holds on fitted tracking. Its value is
architectural: the saved BC weights now match the PPO policy hidden-layer shape,
so the next branch can build a PPO warm-start converter or runner init path
without also changing the network architecture.

One discrepancy must be resolved before trusting any step-0 PPO fidelity result:
the BC smoke replay reports sent-target p95 around `2.19-2.24 rad/s`, while the
standard candidate gate reports `3.78-3.84 rad/s` for the same exported ONNX.
The step-0 fidelity gate must use the standard evaluator path or explain the
smoke-vs-standard difference.

The PPO actor schema has now been inspected directly:

```text
outputs/analysis/PPO_POLICY_PARAM_SCHEMA.md
status: PASS_PPO_BC_SCHEMA_COMPATIBLE
```

The PPO policy network uses the same hidden shapes as the PPO-shape BC student
and outputs 28 tanh-normal distribution parameters. The first 14 outputs are
the action-location branch exported as `tanh(loc)`; the second 14 are scale
logits for PPO exploration. This makes a direct warm-start mapping feasible:

```text
BC hidden layers -> PPO policy hidden_0..hidden_2
BC action output -> PPO policy hidden_3 columns 0:14
PPO scale logits -> fresh or explicit low-variance initialization
value network    -> fresh PPO initialization
```

The next gate is not training. It is step-0 fidelity: initialize a PPO actor
from the BC NPZ and prove deterministic PPO actions match the BC ONNX/NPZ on
held-out observations and in the standard task-matched fitted evaluator.

The first action-level step-0 fidelity check exposed a head-contract mismatch:

```text
outputs/analysis/PPO_BC_WARMSTART_STEP0_FIDELITY.md
status: HOLD_PPO_BC_STEP0_ACTION_FIDELITY

direct BC final-head copy:
  p95 abs action error: 0.1254
  max abs action error: 0.2117

final loc-head refit to atanh(BC action):
  p95 abs action error: 0.0122
  max abs action error: 0.1656
```

The issue is structural: the BC student was trained to output clipped actions
directly, while PPO exports `tanh(loc)` from a tanh-normal actor. Forcing an
action-space BC head into the PPO loc branch is only approximate. The next
warm-start branch should train or fit a PPO-loc student directly, or otherwise
prove actual step-0 closed-loop fidelity before launching PPO.

That PPO-loc student was trained and validated:

```text
outputs/analysis/PPO_LOC_BC_POLICY_VALIDATION.md
status: HOLD_PPO_LOC_BC_TRACKING

fit artifact: outputs/analysis/PPO_LOC_BC_STUDENT.md
fit status: PASS_PPO_LOC_BC_FIT_SMOKE
ONNX: outputs/analysis/ppo_loc_bc_student_candidate/candidate.onnx
NPZ:  outputs/analysis/ppo_loc_bc_student_candidate/candidate_mlp.npz
```

The exported ONNX matches the PPO deterministic `tanh(loc)` contract, but the
standard task-matched fitted gate still holds:

```text
duration complete: 8 / 8
falls: 0 / 8
mean track ratio: 0.4761
sent-target velocity p95 range: 3.8384-3.9250 rad/s
tracking p95 range: 0.2641-0.2703 rad
```

So the remaining issue is not actor shape or ONNX export. Supervised imitation
of the source-VX selector still does not reduce fitted actuator tracking enough
in closed loop. The next step should build actual PPO params from the PPO-loc
NPZ, verify step-0 closed-loop fidelity, and only then run a short PPO
fine-tune with the fitted actuator bridge active.

The actual PPO-param construction was then tested with a swish PPO-loc student,
matching the real Playground PPO activation:

```text
outputs/analysis/PPO_BC_SWISH_WARMSTART_VALIDATION.md
status: HOLD_STEP0_CLOSED_LOOP_STABILITY

export fidelity:
  status: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
  action p95 error: 0.00000012
  action max error: 0.00000036
```

This closes the warm-start plumbing problem: BC weights can now be mapped into a
real PPO checkpoint and exported through the Playground PPO exporter with
essentially exact action fidelity.

The closed-loop step-0 gate still holds:

```text
runs: 8
falls: 1
duration complete: 7
mean track ratio: 0.1441
seed 5: reverse/fall at 74 samples, mean vx -0.1976 m/s
```

So PPO should not start from this checkpoint yet. The remaining warm-start
problem is behavioral: the swish PPO-compatible student has a seed-5
reverse/fall mode and the other seeds still hold on fitted tracking. Next branch
should collect a seed-5 trace, compare it with successful seeds, and improve the
swish warm-start dataset or loss before PPO updates.

The seed-5 trace analysis is now available:

```text
outputs/analysis/PPO_BC_SWISH_WARMSTART_SEED5_FAILURE_ANALYSIS.md
status: HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY
```

Key numbers:

```text
samples: 74
first negative vx tick: 10
base height below 10 cm tick: 72
mean vx: -0.1976 m/s
final pitch: -1.4801 rad
double support: 75.68%
target velocity p95: 1.7630 rad/s
joint tracking p95: 0.1760 rad
nearest manifest distance p95: 1.0276
nearest action L1 p95: 0.0783
```

This does not look like a simple target-rate violation or missing-manifest
state. The failing seed has nearby source coverage and modest action mismatch,
but the closed-loop rollout still backs up and pitches down into a fall. The
next fix should target closed-loop stability/contact support for seed 5 rather
than only increasing dataset size.

Successful seed comparison sharpened that result:

```text
outputs/analysis/PPO_BC_SWISH_WARMSTART_SEED_COMPARISON.md
status: HOLD_SEED5_WEAK_COVERAGE_AND_CLOSED_LOOP_COLLAPSE
```

Compared with successful seeds 0 and 2, seed 5 has:

```text
target velocity p95 lower, not higher:
  seed 5: 1.7630 rad/s
  seeds 0/2: 2.1786-2.1970 rad/s

tracking p95 comparable, not worse:
  seed 5: 0.1760 rad
  seeds 0/2: 0.1813-0.1842 rad

weaker manifest proximity:
  seed 5 nearest distance p95: 1.0276
  seeds 0/2 nearest distance p95: 0.4155-0.4358

more double support and collapse:
  seed 5 double support: 75.7%
  seeds 0/2 double support: about 61%
  seed 5 no-contact events: 6.8%
```

The seed-5 fix should therefore target the weak-coverage recovery basin and
closed-loop contact/stability behavior, not target-rate reduction.

## PPO Swish Seed-5 Recovery Relabel

A narrow recovery branch relabeled the failing swish PPO step-0 seed-5 trace
with the blend teacher and retrained the same swish PPO-loc BC architecture:

```text
relabel artifact: outputs/analysis/PPO_SWISH_SEED5_RELABEL_BLEND.md
manifest: outputs/analysis/PPO_SWISH_SEED5_RECOVERY_MANIFEST.md
BC fit: outputs/analysis/PPO_LOC_SWISH_SEED5_RECOVERY_BC_STUDENT.md
PPO export: outputs/analysis/PPO_BC_SWISH_SEED5_RECOVERY_STEP0_EXPORT_FIDELITY.md
gate: outputs/analysis/PPO_BC_SWISH_SEED5_RECOVERY_STEP0_VALIDATION_FITTED_BACKLASH.md
decision: outputs/analysis/PPO_BC_SWISH_SEED5_RECOVERY_DECISION.md
status: HOLD_SEED5_RECOVERY_TRACE_RELABEL_INSUFFICIENT
```

The manifest added only the failing seed-5 rollout:

```text
entries: 26
samples: 9342
added relabeled seed-5 samples: 74
```

The supervised fit improved slightly:

```text
MAE: 0.011601
p95 action error: 0.035147
max action error: 0.266879
target-rate p95: 2.2326 rad/s
```

The PPO-shaped export again passed action fidelity, so the plumbing remains
sound. The closed-loop gate did not improve enough:

```text
prior swish step0:
  falls: 1 / 8
  duration complete: 7 / 8
  mean vx: 0.0115 m/s
  mean track ratio: 0.1441
  max pitch velocity p95 mean: 3.7281 rad/s
  max tracking p95 mean: 0.2659 rad

seed-5 recovery step0:
  falls: 1 / 8
  duration complete: 7 / 8
  mean vx: 0.0120 m/s
  mean track ratio: 0.1496
  max pitch velocity p95 mean: 3.9029 rad/s
  max tracking p95 mean: 0.2733 rad
```

Seed 5 still fails in the same reverse/collapse basin:

```text
before:
  samples: 74
  mean vx: -0.1976 m/s
  base height min: 0.0717 m
  final pitch: -1.4801 rad
  double support: 75.68%
  nearest distance p95: 1.0276
  nearest action L1 p95: 0.0783

after:
  samples: 75
  mean vx: -0.1893 m/s
  base height min: 0.0777 m
  final pitch: -1.4773 rad
  double support: 80.00%
  nearest distance p95: 0.6022
  nearest action L1 p95: 0.0409
```

This is a useful negative result. The relabel improved local dataset proximity,
but it did not remove the closed-loop failure. The seed-5 problem is therefore
not just one missing teacher label. It needs stronger recovery coverage or a
loss branch that explicitly handles reverse velocity, backward pitch collapse,
and double-support dwell around seed-5-like states.

Do not start PPO from this checkpoint.

## PPO Swish Seed-5 Source-VX Recovery Relabel

The plain blend relabel was then replaced by the stronger source-VX selector
teacher that originally cleared the fitted-bridge selector gate:

```text
tool update: tools/relabel_bc_trace_actions.py supports source_vx_blend
relabel artifact: outputs/analysis/PPO_SWISH_SEED5_RELABEL_SOURCE_VX.md
manifest: outputs/analysis/PPO_SWISH_SEED5_SOURCE_VX_RECOVERY_MANIFEST.md
BC fit: outputs/analysis/PPO_LOC_SWISH_SEED5_SOURCE_VX_RECOVERY_BC_STUDENT.md
PPO export: outputs/analysis/PPO_BC_SWISH_SEED5_SOURCE_VX_RECOVERY_STEP0_EXPORT_FIDELITY.md
x=0.08 gate: outputs/analysis/PPO_BC_SWISH_SEED5_SOURCE_VX_RECOVERY_STEP0_VALIDATION_FITTED_BACKLASH.md
x=0.0 gate: outputs/analysis/PPO_BC_SWISH_SEED5_SOURCE_VX_RECOVERY_STEP0_VALIDATION_FITTED_BACKLASH_X0.md
decision: outputs/analysis/PPO_BC_SWISH_SEED5_SOURCE_VX_RECOVERY_DECISION.md
status: HOLD_COMMAND_CONDITIONING_REQUIRED
```

This is a real improvement over the plain blend relabel:

```text
weak seed-5 relabel x=0.08:
  falls: 1 / 8
  duration complete: 7 / 8
  mean vx: 0.0120 m/s
  mean track ratio: 0.1496
  min samples: 75

source-VX seed-5 relabel x=0.08:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0416 m/s
  mean track ratio: 0.5201
  min samples: 500
```

The seed-5 reverse/fall basin is removed in the deployable-shape warm start.
However, the same policy also walks forward at zero command:

```text
source-VX seed-5 relabel x=0.0:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0415 m/s
  min samples: 500
```

So the current warm-start is stable and moves, but it is not yet
command-conditioned. It learned the forward gait from an x=0.08-only source and
replays that gait even when `command_x = 0.0`.

This changes the next blocker:

```text
solved:
  seed-5 immediate reverse/fall basin

still blocked:
  zero-command semantic gate
  fitted tracking gate
  deployability / robot validation
```

Do not deploy this candidate and do not run robot validation. Before PPO, add
command-conditioned standstill/no-motion data or an explicit zero-command
correction phase, then rerun both x=0.0 and x=0.08 fitted step-0 gates.

## PPO Swish Command-Conditioned Warm Start

To correct the zero-command forward drift, a constant-zero ONNX policy was used
to collect x=0.0 standstill traces. The source was only partially stable:

```text
artifact: outputs/analysis/ZERO_ACTION_STANDSTILL_X0_TRACE_GATE.md
zero action x=0.0:
  falls: 2 / 8
  duration complete: 6 / 8
  passing seeds: 0,1,2,4,6,7
  failing seeds: 3,5
```

The six passing standstill traces were added to the source-VX recovery manifest:

```text
manifest: outputs/analysis/PPO_SWISH_COMMAND_CONDITIONED_MANIFEST.md
entries: 32
samples: 12342
BC fit: outputs/analysis/PPO_LOC_SWISH_COMMAND_CONDITIONED_BC_STUDENT.md
PPO export: outputs/analysis/PPO_BC_SWISH_COMMAND_CONDITIONED_STEP0_EXPORT_FIDELITY.md
decision: outputs/analysis/PPO_BC_SWISH_COMMAND_CONDITIONED_DECISION.md
status: HOLD_X0_HARD_SEED_STANDSTILL_STABILITY
```

The mixed-command fit improved supervised metrics and reduced target-rate p95:

```text
MAE: 0.010749
p95 action error: 0.032331
target-rate p95: 1.9567 rad/s
```

The x=0.08 fitted gate preserved the moving behavior:

```text
x=0.08:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0413 m/s
  mean track ratio: 0.5160
```

The x=0.0 fitted gate improved command semantics on easy seeds but still fails
on the same hard standstill seeds:

```text
x=0.0:
  falls: 2 / 8
  duration complete: 6 / 8
  mean vx: -0.0783 m/s
  failing seeds: 3,5
```

This narrows the next blocker again. The source-VX recovery solved the
x=0.08 seed-5 moving collapse; command-conditioned BC preserved that moving
behavior. The remaining deployable warm-start blocker is stable x=0.0
standstill/recovery behavior for seeds 3 and 5.

Do not start PPO, deploy, or run robot validation from this checkpoint.

## PPO Swish Source-VX Scale Diagnostic

The source-VX recovery policy was globally scaled to test whether a partial
moving-policy action could stabilize the hard zero-command seeds without
building a new teacher:

```text
decision: outputs/analysis/PPO_BC_SWISH_SOURCE_VX_SCALE_0P75_DECISION.md
status: HOLD_X008_FORWARD_PROGRESS_REGRESSION
base: outputs/analysis/ppo_bc_swish_seed5_source_vx_recovery_step0.onnx
scaled: outputs/analysis/ppo_bc_swish_seed5_source_vx_recovery_step0_scale_0p75.onnx
```

Hard-seed x=0.0 screen on seeds 3 and 5:

```text
scale 0.25: 1 / 2 duration complete, seed 5 falls backward
scale 0.50: 1 / 2 duration complete, seed 5 falls backward
scale 0.75: 2 / 2 duration complete, mean vx -0.0002 m/s
```

The full x=0.0 fitted-bridge gate then passed:

```text
x=0.0:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0003 m/s
  mean body_pitch_p95: 0.0232 rad
  mean max pitch target velocity p95: 0.4107 rad/s
```

But the paired x=0.08 fitted-bridge gate regressed to standstill:

```text
x=0.08:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0004 m/s
  mean track ratio: 0.0046
  all seeds: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
```

This is useful evidence, but not a candidate. The 0.75 global scale fixes the
hard x=0.0 standstill seeds by retaining enough source-VX feedback action, but
it also collapses command sensitivity and removes the x=0.08 gait. The next
deployable-policy step should not rely on a global scale. It needs a
command-conditioned zero-command branch or teacher that preserves the full
source-VX x=0.08 walking behavior.

## PPO Swish Command-Scale Wrapper

A command-conditioned ONNX wrapper was added to test the simplest deployable
branch:

```text
tool: tools/wrap_policy_command_scale.py
decision: outputs/analysis/PPO_BC_SWISH_COMMAND_SCALE_DECISION.md
status: HOLD_COMMAND_SCALE_TRACKING_LIMIT
formula: scale = 0.75 + (high_scale - 0.75) * clip(abs(obs[6]) / 0.08, 0, 1)
```

The primary wrapper used `high_scale=1.0`, so it exactly matches the
standstill-stabilizing 0.75 policy at x=0 and the full source-VX recovery
policy at x=0.08:

```text
x=0.0:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0003 m/s
  mean max tracking p95: 0.0710 rad

x=0.08:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0416 m/s
  mean track ratio: 0.5201
  mean max pitch target velocity p95: 3.8218 rad/s
  mean max tracking p95: 0.2662 rad
  status: HOLD_CANDIDATE_TRACKING
```

This proves the zero-command and moving-command behaviors can coexist in one
deployable ONNX graph. It does not pass the candidate gate because the x=0.08
tracking error remains too high.

A high-scale boundary screen showed why scalar amplitude alone is not enough:

```text
high_scale 0.90: seed 5 falls
high_scale 0.93-0.94: stable on seeds 0 and 5, but tracking p95 stays near 0.25 rad
high_scale 0.95-0.975: stable and more progress, but still tracking hold
```

One-tick target smoothing against `obs[83:97]` was also screened:

```text
alpha 0.90: 2 / 2 duration-complete, mean vx 0.0388 m/s, tracking p95 0.2653 rad
alpha 0.80: 2 / 2 duration-complete, mean vx 0.0318 m/s, tracking p95 0.2592 rad
```

This reduces target velocity and progress but does not clear the fitted tracking
gate.

The remaining blocker is action shape/timing at x=0.08, not zero-command
conditioning, not low progress, and not falls. The next deployable-policy work
should keep the command-conditioned x=0 branch but reduce x=0.08 tracking via a
better teacher or PPO fine-tuning from this warm start with the fitted bridge
active. A scalar scale or one-tick target blend is not enough.

## Command-Conditioned Pitch-Rate-Limited BC

A follow-up deployable-shape BC run replaced the weak zero-command source and
smoothed the walking labels:

```text
decision: outputs/analysis/CMD_PITCH_RL_2P25_DECISION.md
status: HOLD_FITTED_TRACKING_AFTER_TARGET_RATE_FIX
manifest: outputs/analysis/ppo_swish_cmd_conditioned_pitch_ratelimit_2p25_manifest.json
candidate: outputs/analysis/ppo_loc_swish_cmd_pitch_rl_2p25_candidate/candidate.onnx
```

The new x=0.0 source used full-observation traces from the already-passing
scale-0.75 stabilizing policy instead of zero-action traces:

```text
scale0p75 x=0.0 trace gate:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0003 m/s
  mean max tracking p95: 0.0710 rad
```

The x=0.08 source-VX walking traces were rate-limited across the full pitch
chain at `2.25 rad/s`, changing `3577` ticks across the eight walking traces.
The resulting swish PPO-loc BC fit had:

```text
samples: 8000
p95 action error: 0.024947
predicted target-rate p95: 1.7847 rad/s
predicted target-rate max: 2.4971 rad/s
```

Closed-loop fitted-bridge gates:

```text
x=0.0:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0004 m/s
  mean max pitch target velocity p95: 0.4448 rad/s
  mean max tracking p95: 0.0730 rad
  worst max tracking p95: 0.0837 rad

x=0.08:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0341 m/s
  mean track ratio: 0.4267
  mean max pitch target velocity p95: 2.1371 rad/s
  max pitch target velocity p95 range: 2.1112-2.1734 rad/s
  mean max tracking p95: 0.1963 rad
  worst max tracking p95: 0.2008 rad
```

This result is useful because it separates three mechanisms:

```text
mostly solved:
  x=0.0 hard-seed stability in a deployable ONNX shape

solved:
  x=0.08 target-rate envelope margin

not solved:
  x=0.08 fitted actuator tracking
```

The candidate is stable and in-envelope at x=0.08, but the fitted bridge still
tracks with about `0.19-0.20 rad` p95 error. That means the current blocker is
not scalar command gain, one-tick target smoothing, or target-rate clipping. It
is the closed-loop action timing/state feedback needed to make the fitted
actuator model follow the walking targets. The next high-value step is PPO
fine-tuning or another closed-loop training pass from this warm start with the
fitted bridge active and tracking/target-rate feedback in the objective, not
another one-step BC smoothing pass.

The BC fit was then promoted into a real Brax/PPO step-0 checkpoint:

```text
export: outputs/analysis/PPO_BC_SWISH_CMD_PITCH_RL_2P25_STEP0_EXPORT_FIDELITY.md
status: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
checkpoint: outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0_checkpoint
onnx: outputs/analysis/ppo_bc_swish_cmd_pitch_rl_2p25_step0.onnx
```

The step-0 ONNX preserves the same behavior:

```text
x=0.0:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0005 m/s
  mean max tracking p95: 0.0740 rad
  worst max tracking p95: 0.0861 rad

x=0.08:
  falls: 0 / 8
  duration complete: 8 / 8
  mean vx: 0.0347 m/s
  mean track ratio: 0.4343
  mean max pitch target velocity p95: 2.1196 rad/s
  mean max tracking p95: 0.1958 rad
```

This is now a valid PPO warm-start artifact, not a deployable robot candidate.
The next training branch should fine-tune from this checkpoint with the fitted
bridge active and target the remaining tracking gap.

The first A100 PPO fine-tune from that checkpoint completed, but regressed the
walking behavior:

```text
artifact: outputs/analysis/CMD_PITCH_RL_2P25_FINETUNE_V1_RESULT.md
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
training: PASS_SMOKE_RUN, 215040 PPO timesteps, A100/CUDA/JAX 0.7.2

x=0.0:
  status: PASS_CANDIDATE_SIM_GATE
  max pitch tracking p95: 0.0701 rad
  max sent target velocity p95: 0.1561 rad/s

x=0.08:
  status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
  mean fitted local vx: 0.0010 m/s
  command tracking ratio: 0.0118
  max sent target velocity p95: 0.2737 rad/s
  max pitch tracking p95: 0.0859 rad
  action saturation: 0.0%
```

This is a real negative result: the fine-tuned policy became actuator-safe but
nearly stationary at x=0.08. It regressed from the step-0 warm start, which
still moved at about `0.0347 m/s`. More steps with this exact PPO recipe are
unlikely to help. The next fine-tune needs an explicit early forward-motion
preservation term or teacher-action regularizer so PPO cannot improve reward by
collapsing the walking behavior into standstill.

A second A100 PPO fine-tune used a more conservative preservation recipe:

```text
artifact: outputs/analysis/CMD_PITCH_RL_2P25_FINETUNE_PRESERVE_V1_RESULT.md
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
training: PASS_SMOKE_RUN, 92160 exported PPO timesteps, A100/CUDA/JAX 0.7.2
learning_rate: 3e-5
clipping_epsilon: 0.05
max_grad_norm: 0.2
ppo_num_updates_per_batch: 1
target_rate_scale: -0.0005
actuator_tracking_scale: -0.005
```

It also held:

```text
x=0.0:
  status: PASS_CANDIDATE_SIM_GATE
  max pitch tracking p95: 0.0613 rad
  max sent target velocity p95: 0.2732 rad/s

x=0.08:
  status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
  mean fitted local vx: 0.0004 m/s
  fitted command tracking ratio: 0.0045
  stress command tracking ratio: 0.0018
  max sent target velocity p95: 0.4493 rad/s
  max pitch tracking p95: 0.0763 rad
  action saturation: 0.0%
```

This rules out the simplest "PPO updates were just too large" explanation. The
conservative run also improved reward while collapsing the x=0.08 gait into
low-rate standstill. The next training implementation should add a
state-conditioned teacher-action or behavior-prior regularizer during early PPO
fine-tuning. Another scalar PPO-parameter sweep is unlikely to be the right
next move.

A third A100 PPO fine-tune added a default-off behavior-prior hook in the
Playground runner and trained with a state-conditioned teacher-action prior:

```text
artifact: outputs/analysis/CMD_PITCH_RL_2P25_FINETUNE_BEHAVIOR_PRIOR_V1_RESULT.md
status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
training: PASS_SMOKE_RUN, 92160 exported PPO timesteps
behavior prior: ppo_loc_swish_cmd_pitch_rl_2p25_candidate/candidate_mlp.npz
behavior prior scale: -0.2
```

The Colab worker disappeared during the post-training gate before writing an
exit sentinel, but the final ONNX and training summary were recovered from the
partial artifact and both gates were rerun locally on CPU.

Result:

```text
x=0.0:
  status: PASS_CANDIDATE_SIM_GATE
  max pitch tracking p95: 0.0618 rad
  max sent target velocity p95: 0.2775 rad/s

x=0.08:
  status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
  fitted mean local vx: 0.0001 m/s
  fitted command tracking ratio: 0.0015
  stress command tracking ratio: 0.0029
  max sent target velocity p95: 0.4586 rad/s
  max pitch tracking p95: 0.0772 rad
  action saturation: 0.0%
```

This is another clear standstill regression. The behavior prior made the policy
stable and actuator-safe, but did not preserve the warm-start gait. It is now
unlikely that another scalar PPO sweep or weak MLP teacher prior is the right
next step. The selector/teacher result should be treated as a data source for a
larger on-distribution BC plus PPO warm-start, or the behavior objective must
anchor the actual walking manifold more directly.

The deployable source-VX DAgger candidates were then checked with a stricter
15-second, eight-seed fitted-bridge validation:

```text
artifact: outputs/analysis/DEPLOYABLE_SOURCE_VX_POLICY_VALIDATION_X008_FITTED_15S.md
status: HOLD_DEPLOYABLE_SOURCE_VX_POLICY_VALIDATION
command: x=0.08
bridge: fitted
duration: 15 s
```

Results:

```text
dagger2:
  pass: 0 / 8
  falls: 2 / 8
  duration complete: 6 / 8
  mean vx: 0.0199 m/s
  mean track ratio: 0.2487

dagger2_rate:
  pass: 0 / 8
  falls: 2 / 8
  duration complete: 6 / 8
  mean vx: 0.0148 m/s
  mean track ratio: 0.1847
```

This resolves the apparent contradiction in the selector/MLP work. The
DAgger-2 MLPs are not useless; they can move in the right direction and passed a
shorter 10-second smoke. But they are not yet deployable warm starts under the
stricter 15-second candidate gate. The current blocker is therefore still
learnability/coverage: the walking behavior exists in the selector, and the MLPs
partially distill it, but the current dataset/model does not preserve it robustly
enough over the full validation horizon.

The later DAgger-3 deployable candidates were also run through the same strict
gate:

```text
artifact: outputs/analysis/DEPLOYABLE_SOURCE_VX_POLICY_VALIDATION_DAGGER3_X008_FITTED_15S.md
status: HOLD_DEPLOYABLE_SOURCE_VX_POLICY_VALIDATION
command: x=0.08
bridge: fitted
duration: 15 s
```

Results:

```text
dagger3_128:
  pass: 0 / 8
  falls: 2 / 8
  duration complete: 6 / 8
  mean vx: 0.0218 m/s
  mean track ratio: 0.2729

dagger3_512:
  pass: 0 / 8
  falls: 3 / 8
  duration complete: 5 / 8
  mean vx: -0.0070 m/s
  mean track ratio: -0.0873
```

The DAgger-3 128-wide policy is slightly better than DAgger-2 on mean track
ratio, but still fails the strict gate. The larger 512/256/128 model is worse
and includes a strong reverse/fall seed. This makes the next branch sharper:
the project needs either a broader/higher-quality selector rollout dataset or a
different stabilization objective before PPO warm-start, not just a larger MLP.

A bounded source-VX selector expansion test then checked fresh seeds 8-15:

```text
artifact: outputs/analysis/SOURCE_VX_SELECTOR_EXPANSION_SEEDS8_15_FITTED_10S.md
status: HOLD_BC_REPLAY_TERMINATED
command: x=0.08
bridge: fitted
duration: 10 s
```

Only three of eight new seeds completed:

```text
complete moving traces: seeds 8, 10, 11
terminated/reverse/collapse traces: seeds 9, 12, 13, 14, 15

complete-trace vx range: 0.0315-0.0336 m/s
complete-trace track ratio range: 0.3941-0.4204
complete-trace sent_vel95 range: 2.2668-2.2931 rad/s
complete-trace tracking p95 range: 0.1820-0.1830 rad
```

This is the current sharpest learnability result. The selector proves
in-envelope walking exists, but it is not broadly seed-robust. Dataset expansion
must be curated around complete forward-moving traces; blindly adding selector
rollouts from new seeds would poison the BC labels with reverse/fall behavior.

To enforce that curation, `tools/filter_bc_manifest.py` was added and run over
the DAgger-3 manifest plus the seeds 8-15 expansion manifest:

```text
artifact: outputs/analysis/FILTERED_SOURCE_VX_SELECTOR_DAGGER4_MANIFEST.md
status: PASS_FILTERED_BC_MANIFEST_READY
input entries: 33
kept entries: 19
rejected entries: 14
samples: 9500
```

A filtered DAgger-4 128x128 rate-regularized MLP was then fit from the curated
manifest:

```text
artifact: outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER4_FILTERED_MLP128_RATE_REG_ONNX_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: HOLD_BC_REPLAY_TERMINATED
```

The result did not pass the 10-second smoke:

```text
duration complete: 6 / 8
terminated: seeds 1 and 7
seed 0: near standstill, vx 0.0009 m/s
moving complete seeds: 2, 3, 4, 5, 6
best seed: seed 2, vx 0.0318 m/s, track ratio 0.3974
```

This is a cleaner negative than the earlier DAgger holds. Bad positive labels
were removed, but the filtered walking manifold is too narrow for the current
128x128 BC student to generalize across all seeds. The next branch needs more
curated complete traces and/or a stabilization phase after BC, not unfiltered
trace accumulation.

A second bounded selector expansion over seeds 16-31 produced more complete
positive traces:

```text
artifact: outputs/analysis/SOURCE_VX_SELECTOR_EXPANSION_SEEDS16_31_FITTED_10S.md
status: HOLD_BC_REPLAY_TERMINATED
complete traces: 11 / 16
filter-kept traces: 8
```

After merging those with the prior curated data:

```text
artifact: outputs/analysis/FILTERED_SOURCE_VX_SELECTOR_DAGGER5_MANIFEST.md
status: PASS_FILTERED_BC_MANIFEST_READY
kept entries: 27
samples: 13500
```

The DAgger-5 128x128 rate-regularized MLP still held:

```text
artifact: outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER5_FILTERED_MLP128_RATE_REG_ONNX_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: HOLD_BC_REPLAY_TERMINATED
duration complete: 5 / 8
terminated: seeds 1, 5, 7
seed 5 vx: -0.1500 m/s
best seed vx: 0.0308 m/s
```

More curated positive windows helped some seeds but did not solve hard-seed
recovery. This is now a BC-only limitation: the policy needs either failure-
state recovery labels or closed-loop fine-tuning from the filtered BC student.
Adding more of the same positive windows is unlikely to be sufficient by itself.

The next branch tested the first recovery-label pass instead of another
positive-window expansion. The DAgger-5 student was replayed with full
observations so the source-VX selector teacher could relabel the states the
student actually visits:

```text
artifact: outputs/analysis/DAGGER5_RECOVERY_TRACE_X008_FITTED_10S.md
status: HOLD_CANDIDATE_TRACKING / HOLD_CANDIDATE_FALL_OR_TERMINATION
trace_full_obs: true
samples: 3066 before terminal-row truncation
```

`tools/relabel_bc_trace_actions.py` now supports `--truncate-before-done` and
preserves seed directories when several inputs are named `trace.jsonl`. The
relabel pass produced:

```text
artifact: outputs/analysis/DAGGER5_RECOVERY_TEACHER_RELABEL.md
status: PASS_BC_TRACE_RELABEL_READY
traces: 8
samples_out: 3064
truncated_traces: 2
```

The failed/early-fall seeds showed much larger teacher/student action
disagreement than the stable-duration seeds:

```text
seed 1 action_delta_p95: 0.3352
seed 7 action_delta_p95: 0.2652
typical duration-complete action_delta_p95: about 0.09-0.11
```

Those relabeled recovery traces were merged with the DAgger-5 curated positive
manifest, with the recovery manifest included twice to make hard-state
correction visible in the supervised fit:

```text
artifact: outputs/analysis/FILTERED_SOURCE_VX_SELECTOR_DAGGER6_RECOVERY_MANIFEST.md
status: PASS_FILTERED_BC_MANIFEST_READY
kept entries: 43
samples: 19628
```

The DAgger-6 128x128 rate-regularized MLP improved the previous hard-seed
distribution but still did not pass:

```text
artifact: outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER6_RECOVERY_MLP128_RATE_REG_ONNX_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: HOLD_BC_REPLAY_TERMINATED
duration complete: 6 / 8
terminated: seeds 1 and 7
seed 5 recovered: duration_complete, vx 0.0338 m/s
mean completed-seed vx: roughly 0.0308 m/s
sent_vel95 on complete seeds: roughly 2.26-2.29 rad/s
```

Compared with DAgger-5, recovery relabeling fixed the seed-5 reverse/fall mode
and raised forward progress on the complete seeds. It did not fix the two
earliest collapse seeds. This narrows the deployable-policy blocker: a single
BC pass with teacher relabels can correct some off-manifold behavior, but the
current MLP still needs either more targeted early-collapse recovery data,
stronger closed-loop fine-tuning from the BC student, or a different deployable
architecture. Do not resume plain positive-window BC expansion as the next
step.

An additional targeted recovery pass tested whether the two remaining
early-collapse seeds simply needed heavier supervised correction. DAgger-6 was
replayed only on seeds 1 and 7 with full observations:

```text
artifact: outputs/analysis/DAGGER6_TARGETED_RECOVERY_TRACE_X008_FITTED_10S.md
status: HOLD_CANDIDATE_FALL_OR_TERMINATION
seed 1: 32 samples, base_height_min 0.0775 m
seed 7: 33 samples, base_height_min 0.0730 m
```

Those states were relabeled by the same source-VX teacher:

```text
artifact: outputs/analysis/DAGGER6_TARGETED_RECOVERY_TEACHER_RELABEL.md
status: PASS_BC_TRACE_RELABEL_READY
samples_out: 63
truncated_traces: 2
seed 1 action_delta_p95: 0.1478
seed 7 action_delta_p95: 0.1743
```

The targeted labels were then upweighted 50x in a DAgger-7 manifest:

```text
artifact: outputs/analysis/FILTERED_SOURCE_VX_SELECTOR_DAGGER7_TARGETED_RECOVERY_MANIFEST.md
status: PASS_FILTERED_BC_MANIFEST_READY
kept entries: 143
samples: 22778
```

DAgger-7 still held:

```text
artifact: outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER7_TARGETED_RECOVERY_MLP128_RATE_REG_ONNX_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: HOLD_BC_REPLAY_TERMINATED
duration complete: 6 / 8
terminated: seeds 1 and 7
seed 1: 32 samples, vx 0.0109 m/s
seed 7: 32 samples, vx 0.0261 m/s
```

Heavy upweighting of the first 30-ish collapse-state labels did not solve the
remaining failure and slightly reduced forward progress on several completed
seeds. This suggests the collapse cannot be corrected by static BC labels at
the onset alone. The next meaningful deployable-policy branch should use
closed-loop fine-tuning from the DAgger-6/DAgger-7 student or collect longer
successful recovery trajectories, not increase the same early-collapse label
weight again.

A follow-up hard-seed analysis split the remaining two failures into different
mechanisms:

```text
artifact: outputs/analysis/DAGGER7_HARD_SEED_FAILURE_DECISION.md
seed 1: HOLD_SEED_FAILURE_CLOSED_LOOP_INSTABILITY
seed 7: HOLD_SEED_FAILURE_ACTION_MISMATCH
```

Seed 1 had nearby DAgger-7 manifest support and modest nearest-action mismatch
(`p95 L1 0.0736`) but collapsed under left single support while lateral
velocity grew to `+1.3568 m/s`. Seed 7 had nearby states but still had high
nearest-action mismatch (`p95 L1 0.1290`) and collapsed under right single
support while lateral velocity grew to `-1.3233 m/s`.

Decision: do not run another uniform-label-weight DAgger pass. Seed 1 needs
closed-loop lateral/height stabilization; seed 7 still needs a better local
right-support action fit or recovery mapping.

## DAgger-8 observation-consistency BC check

DAgger-8 tested a smaller hypothesis after the hard-seed split: maybe the
deployable MLP was too brittle around the demonstrated hard-seed states. The
test reused the DAgger-7 targeted recovery manifest and added local
observation-noise consistency regularization:

```text
artifact: outputs/analysis/DAGGER8_OBS_CONSISTENCY_DECISION.md
gate: outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER8_OBS_CONSISTENCY_MLP128_RATE_REG_FITTED_BRIDGE_BC_GATE_X008_10S.md
status: HOLD_BC_REPLAY_TERMINATED
obs_noise_std: 0.02
obs_consistency_scale: 0.1
```

The result preserved six-seed completion but did not clear the hard seeds:

```text
duration complete: seeds 0, 2, 3, 4, 5, 6
terminated: seed 1 at 33 samples, seed 7 at 32 samples
seed 1 vy95: 1.2433 m/s, base_height_min: 0.0791 m
seed 7 vy95: 1.1534 m/s, base_height_min: 0.0848 m
sent target velocity p95: 2.23-2.55 rad/s
action saturation: 0%
```

Conclusion: observation-consistency regularization alone is not enough. The
remaining blocker is still the two hard support-transition cases: seed 1 needs
closed-loop lateral/height recovery under left support, while seed 7 needs
better right-support pitch-chain action fit or recovery. Do not run another
uniform static-label DAgger pass as the next experiment.

A hard-seed-only initialization screen then tested whether this was a single
unlucky MLP start:

```text
artifact: outputs/analysis/DAGGER8_OBS_CONSISTENCY_INIT_SCREEN.md
mlp seeds: 9, 10, 11
rollout seeds: 1, 7
status: HOLD_STATIC_BC_INIT_SCREEN
```

All three MLP initializations terminated around 32-33 samples on both hard
seeds. Seed 1 remained left-support dominated (`10` contact, `vy95` about
`1.17-1.26 m/s`), and seed 7 remained right-support dominated (`01` contact,
`vy95` about `1.15-1.22 m/s`). Static BC stochasticity is therefore not the
next useful branch. Move to explicit closed-loop support-transition recovery or
PPO/fine-tuning from the best BC student with the fitted bridge active.

## PPO-loc DAgger-7 targeted recovery student

The DAgger-7 targeted recovery manifest was also fit into the PPO actor's
deterministic `tanh(loc)` contract with the standard `[512, 256, 128]` swish
network:

```text
artifact: outputs/analysis/PPO_LOC_DAGGER7_TARGETED_RECOVERY_STUDENT.md
status: PASS_PPO_LOC_BC_FIT_SMOKE
manifest: outputs/analysis/filtered_source_vx_selector_dagger7_targeted_recovery_manifest.json
train p95 abs error: 0.043166
target-rate p95: 2.379108 rad/s
```

The supervised fit is slightly better than the earlier DAgger-6 PPO-loc fit,
but the closed-loop fitted-bridge gate still holds:

```text
artifact: outputs/analysis/PPO_LOC_DAGGER7_TARGETED_RECOVERY_X008_FITTED_10S.md
status: HOLD
duration complete: 6 / 8
falls: seeds 1 and 7
mean track ratio: 0.3343
mean vx: 0.0267 m/s
```

This candidate is not worth promoting into a PPO checkpoint as-is. It improves
the broad distribution relative to the DAgger-6 PPO-loc student, but it still
inherits the same hard support-transition failures and misses the x=0.08
tracking gate on completed seeds. The next PPO branch needs an explicit
closed-loop recovery/stabilization objective; merely switching the DAgger-7
student into the PPO actor shape is not enough.

The DAgger-7 PPO-loc student was then mapped into an actual Brax/PPO step-0
checkpoint/export:

```text
artifact: outputs/analysis/PPO_LOC_DAGGER7_TARGETED_RECOVERY_STEP0_EXPORT_FIDELITY.md
status: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
exported ONNX: outputs/analysis/ppo_loc_dagger7_targeted_recovery_step0.onnx
p95 action error vs PPO-loc BC ONNX: 0.00000013
```

The exported step-0 policy reproduced the same closed-loop hold:

```text
artifact: outputs/analysis/PPO_LOC_DAGGER7_TARGETED_RECOVERY_STEP0_X008_FITTED_10S.md
duration complete: 6 / 8
falls: seeds 1 and 7
mean track ratio: 0.3329
mean vx: 0.0266 m/s
```

This proves the PPO restore/export path is coherent for the DAgger-7 student.
It does not make the checkpoint deployable. Treat it only as a possible
starting checkpoint for a future closed-loop recovery fine-tune.

## Physical start-pose calibration check

The real robot now has both telemetry evidence and operator-confirmed physical
home-pose evidence against a repo-rendered reference.

Canonical gate: [PHYSICAL_START_POSE_CALIBRATION_GATE.md](PHYSICAL_START_POSE_CALIBRATION_GATE.md).

Evidence already collected:

```text
runtime HWI.init_pos == sim scene_flat_terrain.xml home keyframe
home_pose_log_test: stable gyro, +Z dominant accel, small joint tracking errors
live duck_config offsets captured from the RDK-X5
repo-rendered zero/home references generated from the MJCF
Rob confirmed commanded home visually matches the rendered home reference
```

Important caveat:

```text
large live left_knee offset: -1.4880 rad
right_knee offset: 0.0798 rad
```

The audit documents the `scripts/find_soft_offsets.py` zeroing procedure, but I
do not see evidence that we re-ran that physical manual calibration procedure
after the later robot work. However, because commanded home visually matches
the repo-rendered home pose and telemetry tracks the compensated home pose well,
blindly re-running soft-offset calibration is not justified right now. A wrong
mechanical start/home pose can absolutely make a biped policy fail to walk, but
the current evidence downranks it as the leading cause.

Current gate status:

```text
PASS_PHYSICAL_HOME_POSE_VISUAL_CHECK
PASS_HOME_POSE_TELEMETRY_HOLD
HOLD_ZERO_RECALIBRATION_NOT_NEEDED_WITHOUT_VISIBLE_MISMATCH
```

## PPO-compatible BC and tiny fine-tune check

The first deployable-policy branch after DAgger-7 tested whether changing the
student to the PPO actor shape, then exporting a true PPO-compatible checkpoint,
would improve the seed distribution.

The PPO-location BC student fit the DAgger-6 recovery manifest:

```text
artifact: outputs/analysis/PPO_LOC_DAGGER6_RECOVERY_STUDENT.md
status: PASS_PPO_LOC_BC_FIT_SMOKE
manifest: outputs/analysis/filtered_source_vx_selector_dagger6_recovery_manifest.json
train p95 abs error: 0.044702
target-rate p95: 2.351068 rad/s
```

But the ONNX candidate did not improve deployability:

```text
artifact: outputs/analysis/PPO_LOC_DAGGER6_RECOVERY_X008_FITTED_10S.md
status: HOLD
duration complete: 5 / 8
falls: seeds 1, 5, 7
mean track ratio: -0.0967
mean vx: -0.0077 m/s
```

The same weights were then converted into an actual Brax/PPO Orbax checkpoint
and exported as a step-0 ONNX:

```text
artifact: outputs/analysis/PPO_LOC_DAGGER6_RECOVERY_STEP0_EXPORT_FIDELITY.md
status: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
```

The step-0 PPO export reproduced the same failure distribution:

```text
artifact: outputs/analysis/PPO_LOC_DAGGER6_RECOVERY_STEP0_X008_FITTED_10S.md
falls: 3 / 8
duration complete: 5 / 8
mean track ratio: -0.0931
mean vx: -0.0075 m/s
```

A tiny CPU-only PPO fine-tune from that checkpoint completed and exported a
step-1040 ONNX:

```text
source run: /tmp/open_duck_ppo_loc_dagger6_finetune_smoke/smoke_20260626T235852Z_cpu
status: PASS_SMOKE_RUN
step: 1040
reward: 25.527969
```

The step-1040 candidate reduced fall count but collapsed toward low-progress
behavior:

```text
artifact: outputs/analysis/PPO_LOC_DAGGER6_RECOVERY_STEP1040_X008_FITTED_10S.md
falls: 2 / 8
duration complete: 6 / 8
mean track ratio: 0.1379
mean vx: 0.0110 m/s
```

A small behavior-prior PPO smoke also completed, but its interrupted partial
gate covered only seeds 0-2 and showed the same pattern:

```text
artifact: outputs/analysis/PPO_LOC_DAGGER6_BEHAVIOR_PRIOR_STEP1040_PARTIAL_X008_FITTED_10S.md
seed 0: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS, track_ratio 0.1520
seed 1: HOLD_CANDIDATE_FALL_OR_TERMINATION, base_height_min 0.0877 m
seed 2: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS, track_ratio 0.1388
```

Conclusion: the warm-start PPO path is wired and exportable, but a tiny PPO
update from the PPO-compatible DAgger-6 student does not produce a deployable
walker. It trades some falls for the old low-progress/freeze basin. The next
PPO attempt, if pursued, needs a stronger continuity/progress design and a full
8-seed fitted-bridge gate. Do not treat the step-1040 checkpoint as a robot
candidate.

## Gate-Aligned Colab Checkpoint Selection

The later A100 PPO warm-start and behavior-prior fine-tunes showed the same
structural problem at larger scale: reward increased while the gate behavior
regressed. The Colab workflow now has a post-training compact checkpoint sweep
so the latest reward checkpoint is no longer treated as automatically best:

```text
artifact: outputs/analysis/COLAB_CANDIDATE_CHECKPOINT_SWEEP_SELECTION.md
status: PASS_GATE_ALIGNED_SELECTION_PLUMBING_READY
workflow: tools/run_colab_cli_cuda_workflow.py
sweep tool: tools/sweep_candidate_checkpoints.py
default commands: 0.0,0.08
default duration: 1.0 s
default bridge: fitted
```

After candidate training exports ONNX checkpoints, the workflow can sweep all
exports through compact fitted-bridge x=0.0/x=0.08 gates. If one receives
`PASS_PROMOTE_CANDIDATE_CHECKPOINT`, that checkpoint is selected for the normal
final gates. If none promote, the best available checkpoint is documented but
not treated as a robot candidate.

This does not solve the deployable-policy problem by itself. It prevents the
next GPU run from repeating a known selection mistake.

## Command-Conditioned x=0.08 Relabel Diagnostic

After the behavior-prior PPO rejection, a bounded static DAgger follow-up tested
whether the current best command-conditioned student could be improved by
adding relabeled x=0.08 visited states:

```text
decision: outputs/analysis/COMMAND_CONDITIONED_X008_RELABEL_WEIGHT3_DECISION.md
status: HOLD_X008_RELABEL_WEIGHT3_REGRESSES_FORWARD_PROGRESS
```

Two x=0.08 fitted-bridge traces were collected from the current best candidate
with full observations, then relabeled using the existing blend teacher:

```text
trace artifact: outputs/analysis/COMMAND_CONDITIONED_SEED5_X0_X008_TRACE_FOR_DAGGER.md
relabel artifact: outputs/analysis/COMMAND_CONDITIONED_X008_RELABEL_SEED0_SEED5.md
samples: 1000
seed 0 action_delta_p95: 0.0394
seed 5 action_delta_p95: 0.0542
```

The teacher action was only modestly different from the student on these
tracking-limited states. A 3x relabel-upweighted student reduced neither the
gate problem nor the deployability gap:

```text
best compact x=0.08:
  mean vx 0.0223
  track ratio 0.2793

relabel_weight3 compact x=0.08:
  mean vx -0.0172
  track ratio -0.2154
```

Conclusion: this is not a promising static-label branch. The next deployability
attempt needs a stronger mechanism than reweighting nearly identical labels:
gate-selected PPO, actuator/tracking feedback in the objective, or a teacher
that actually changes actions on tracking-limited states.

## Actuator-Tracking Behavior-Prior PPO Probe

The next A100 probe restored from the PPO-compatible step-0 checkpoint, used the
command-conditioned DAgger seed-5/x=0 MLP as a behavior prior, and added explicit
actuator-tracking pressure:

```text
doc: docs/ACTUATOR_TRACKING_BEHAVIOR_PRIOR_PROBE_RESULT.md
status: HOLD_REJECT_CANDIDATE_CHECKPOINT
training: PASS_SMOKE_RUN
robot touched: false
```

Training itself completed and exported two ONNX checkpoints:

```text
step 0 reward: 16.7091
step 40960 reward: 20.6604
```

The Colab GPU sweep wedged during candidate eval after training completed, so
the exported checkpoints were swept locally on CPU under the same compact
fitted-bridge x=0.0/x=0.08 gate.

Results:

```text
step 0 x=0.08:
  mean vx 0.0215
  track ratio 0.2692
  max pitch tracking p95 0.2233
  status HOLD_CANDIDATE_TRACKING

step 40960 x=0.08:
  mean vx 0.0083
  track ratio 0.1043
  max pitch tracking p95 0.2182
  status HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
```

The new `tools/compare_policy_to_behavior_prior.py` check compared the exported
ONNX policies against the behavior-prior MLP on the same manifest states:

```text
samples: 10322
original candidate teacher p95 error: ~0.0000
step 0 teacher p95 error: ~0.0000
step 40960 teacher p95 error: 0.1409
```

Conclusion: this PPO variant did not produce a robot candidate. The trained
checkpoint reduced target velocity and increased reward, but it also moved the
policy back toward low progress and away from the prior action map on the
prior's own states. This is another instance of the same pattern: reward
improvement is not aligned with deployability unless the gate behavior is
preserved directly. The next attempt needs a stronger deployable-policy
mechanism, such as teacher-action continuity during PPO or rollout correction
from the working selector, rather than another small scalar reward tweak.

Infrastructure follow-up: the Colab workflow now defaults the compact
post-training checkpoint sweep to CPU (`--candidate-checkpoint-sweep-jax-platform
cpu`) while keeping training on GPU. This matches the observed behavior: A100
training completed, GPU candidate eval wedged, and the same checkpoint sweep
completed locally on CPU.

## Actuator-Tracking Behavior-Prior Weight Blend Diagnostic

A follow-up offline interpolation diagnostic tested whether the A100
behavior-prior PPO run contained a useful intermediate policy between the
prior-preserving step-0 export and the higher-reward step-40960 export.

```text
doc: docs/ACTUATOR_TRACKING_BEHAVIOR_PRIOR_WEIGHT_BLEND_RESULT.md
status: HOLD_WEIGHT_BLEND_DOES_NOT_FIX_TRACKING
tool: tools/blend_onnx_policy_weights.py
robot touched: false
```

Generated ONNX weight blends:

```text
alpha: 0.05, 0.10, 0.20, 0.35, 0.50
base: step 0 export
target: step 40960 export
```

Compact fitted-bridge CPU sweep result:

```text
best blend: alpha 0.05
x=0.08 mean vx: 0.0253 m/s
x=0.08 track ratio: 0.3158
x=0.08 max pitch tracking p95: 0.2217 rad
x=0.08 max pitch sent velocity p95: 1.8523 rad/s
status: HOLD_CANDIDATE_TRACKING
```

Small blends preserved or slightly improved motion but did not repair the
tracking hold. Larger blends inherited the step-40960 low-progress drift:

```text
step 0 x=0.08 tracking p95:     0.2233 rad
alpha 0.05 x=0.08 tracking p95: 0.2217 rad
alpha 0.20 x=0.08 tracking p95: 0.2206 rad
alpha 0.50 x=0.08 tracking p95: 0.2160 rad

step 0 x=0.08 track ratio:      0.2692
alpha 0.05 x=0.08 track ratio: 0.3158
alpha 0.35 x=0.08 track ratio: 0.2101
alpha 0.50 x=0.08 track ratio: 0.1016
```

Conclusion: post-hoc ONNX weight interpolation is not enough. The next
deployable-policy attempt needs a training mechanism that preserves the working
closed-loop behavior directly while optimizing tracking, such as stronger
teacher-action continuity, rollout correction from the working selector, or a
gate-aware fine-tuning loop.

## Pitch-Chain 4.3 Rate-Limit Curation

A follow-up offline curation applied the `4.3 rad/s` source-trace target-rate
limit to the full pitch chain rather than only the right knee:

```text
result doc: docs/PITCH_CHAIN_RATE_LIMIT_CURATION_RESULT.md
status: HOLD_PITCH_CHAIN_4P3_DOES_NOT_FIX_TRACKING
robot touched: false
```

The curation changed `543` ticks, but almost all changes were still right-knee
changes:

```text
right_knee: 493
right_ankle: 20
left_ankle: 23
left_knee: 7
left_hip_pitch/right_hip_pitch: 0
```

The exact-blend ONNX smoke replay passed, but the strict fitted-backlash x=0.08
8-seed gate still held on tracking:

```text
duration_complete: 8/8
falls: 0/8
mean vx: 0.0477 m/s
mean track ratio: 0.5965
max pitch velocity p95: 4.1935-4.2879 rad/s
max tracking p95: 0.2685-0.2794 rad
status: HOLD_CANDIDATE_TRACKING
```

Compared with the earlier right-knee-only `4.3 rad/s` curation, the metrics
were effectively unchanged:

```text
right-knee-only 4.3 mean velocity p95: 4.2391 rad/s
pitch-chain 4.3 mean velocity p95:     4.2399 rad/s

right-knee-only 4.3 mean tracking p95: 0.2720 rad
pitch-chain 4.3 mean tracking p95:     0.2735 rad
```

Conclusion: simple post-hoc pitch-chain rate limiting at `4.3 rad/s` is not the
missing deployability step. The remaining issue is the right-knee
phase/contact-transition behavior itself, which needs dynamics-aware relabeling
or gate-aware fine-tuning rather than another uniform cap.

## Right-Knee Transition Spike Filter

The next offline curation tested whether transition-adjacent right-knee spikes
could simply be removed from the source-vx selector trace dataset.

```text
result doc: docs/RIGHT_KNEE_TRANSITION_SPIKE_FILTER_RESULT.md
tool: tools/filter_bc_trace_transition_spikes.py
status: HOLD_TRANSITION_SPIKE_FILTER_DOES_NOT_FIX_TRACKING
robot touched: false
```

The diagnostic confirmed the spike/contact coupling:

```text
right-knee action-derived velocity > 3.75 rad/s: 506 / 3992 ticks
within 2 ticks of a contact transition: 404 / 506
```

The filter removed transition-adjacent right-knee spike rows:

```text
input samples: 4000
output samples: 3124
removed samples: 876
dataset_id: 69c1466221e946cc
```

The exact-blend ONNX smoke replay still passed, but strict fitted-backlash
x=0.08 gate metrics worsened on the target-velocity axis:

```text
duration_complete: 8/8
falls: 0/8
mean vx: 0.0449 m/s
mean track ratio: 0.5617
max pitch velocity p95: 4.6244-4.7790 rad/s
max tracking p95: 0.2675-0.2782 rad
status: HOLD_CANDIDATE_TRACKING
```

Conclusion: the transition-adjacent right-knee samples are not disposable
outliers. Dropping them weakens forward motion and the exported exact-blend
model still reconstructs a high-rate transition. The next attempt needs
dynamics-aware relabeling or a student/training mechanism that represents the
transition smoothly, not another deletion or uniform clip.

## Next Deployable Policy Branch Decision

The curation and PPO/weight-blend results are now consolidated in a machine-read
decision artifact:

```text
tool: tools/decide_next_deployable_policy_branch.py
artifact: outputs/analysis/NEXT_DEPLOYABLE_POLICY_BRANCH_DECISION.md
status: PLAN_GATE_AWARE_ROLLOUT_CORRECTION_OR_RECURRENT_STUDENT
robot touched: false
```

Current deployable-candidate comparison:

| candidate | vx mean | track ratio | pitch velocity p95 range | tracking p95 range | result |
|---|---:|---:|---:|---:|---|
| exact selector blend ONNX | 0.0461 | 0.5768 | 4.7355-5.1118 | 0.2679-0.2800 | hold |
| right-knee 4.3 curation | 0.0479 | 0.5992 | 4.1979-4.2994 | 0.2682-0.2773 | hold |
| pitch-chain 4.3 curation | 0.0477 | 0.5965 | 4.1935-4.2879 | 0.2685-0.2794 | hold |
| right-knee transition filter | 0.0449 | 0.5617 | 4.6244-4.7790 | 0.2675-0.2782 | hold |

Interpretation:

```text
The gait survives and moves in all four paths.
The strict tracking plateau remains around 0.27 rad.
The right-knee/contact-transition mechanism is still the deployable-policy blocker.
```

Closed branches:

```text
uniform pitch-chain clipping
transition-adjacent sample deletion
post-hoc ONNX weight interpolation
scalar behavior-prior PPO smoke
```

Recommended next branch:

```text
PLAN_GATE_AWARE_ROLLOUT_CORRECTION_OR_RECURRENT_STUDENT
```

The next attempt must preserve 8/8 duration-complete forward motion while
directly reducing fitted-bridge tracking through the right-knee contact
transition. Do not spend another branch on simple clipping, deletion, or scalar
weight blending unless a new diagnostic identifies a different mechanism.

## Home Pose Contract Audit

The physical calibration discussion exposed a useful distinction:

```text
source-level home contract
vs
physical zero calibration
```

An offline verifier now checks the source-level contract directly:

```text
tool: tools/verify_home_pose_contract.py
artifact: outputs/analysis/HOME_POSE_CONTRACT_AUDIT.md
status: PASS_HOME_POSE_CONTRACT
```

Result:

```text
max_abs_runtime_minus_sim_home_rad: 0.0000
max_abs_runtime_zero_rad: 0.0000
max_abs_raw_bypass_minus_normal_home_rad: 1.4880
```

Interpretation:

```text
runtime HWI.init_pos == Playground sim home keyframe ctrl
runtime zero_pos is all zeros
normal raw home target = joint_dir * sim_home + configured offset
```

This answers what "home" is in the repo: it is the 14-value runtime `init_pos`
vector, exactly matching the sim `home` keyframe `ctrl` vector. It also confirms
that commanding "raw sim-home" directly is unsafe. With the current live
offsets, raw-bypass home would differ from the normal compensated raw home
target by up to `1.4880 rad` at `left_knee`.

The audit does not prove that the real robot's mechanical zero was freshly
calibrated to this contract after later motor work. That remaining proof is
robot-side: either run/audit `find_soft_offsets.py`, or run the read-only raw
home offset audit while the robot is independently placed in the repo-defined
home geometry.

## Pitch-Chain 4.3 PPO-Shape Rate Student

A PPO-shape feed-forward BC student was trained from the pitch-chain `4.3 rad/s`
curated source-vx trace manifest to test whether a deployable neural policy
could smooth the non-deployable selector.

```text
result doc: docs/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT_RESULT.md
fit doc: outputs/analysis/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT.md
gate doc: outputs/analysis/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT_MULTI_SEED_FITTED_BACKLASH.md
status: HOLD_CANDIDATE_TRACKING
```

Strict fitted-backlash x=0.08 8-seed gate:

```text
duration_complete: 8/8
falls: 0/8
mean vx: 0.0393 m/s
mean track ratio: 0.4913
max pitch velocity p95: 3.6035-3.7059 rad/s
max tracking p95: 0.2516-0.2561 rad
```

This is a real but insufficient improvement: target velocity moved inside the
`3.75 rad/s` envelope and tracking improved slightly versus the earlier
PPO-shape BC student, but forward progress dropped and the tracking gate is
still far from deployable. This closes simple feed-forward BC smoothing as a
standalone fix. The next branch still needs gate-aware rollout correction,
phase/recurrent state, or PPO fine-tuning with strict gate feedback.

## Gate-Aware Static Relabel BC

The next bounded probe collected full-observation strict-gate traces from the
pitch-chain `4.3` PPO-shape rate student on the targeted hold seeds:

```text
seed 1: lowest progress
seed 4: worst tracking
artifact: outputs/analysis/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT_GATE_FAILURE_TRACES.md
```

Those states were relabeled with the same source-VX teacher that produced the
in-envelope selector pass:

```text
artifact: outputs/analysis/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT_GATE_FAILURE_RELABEL_SOURCE_VX.md
samples_out: 1000
seed 1 action_delta_p95: 0.0848
seed 4 action_delta_p95: 0.0968
```

The relabeled gate-failure states were merged with the base pitch-chain `4.3`
manifest, upweighted `12x`, and distilled into another PPO-shape feed-forward
student:

```text
result doc: docs/GATE_AWARE_RELABEL_STATIC_BC_RESULT.md
screen: outputs/analysis/PITCH_CHAIN_4P3_GATE_AWARE_RELABEL_PPO_SHAPE_STUDENT_SEED1_SEED4_SCREEN.md
status: HOLD_CANDIDATE_TRACKING
```

Targeted seed screen:

```text
seed 1: vx 0.0372, track ratio 0.4652, vel p95 3.7264, tracking p95 0.2548
seed 4: vx 0.0380, track ratio 0.4747, vel p95 3.6821, tracking p95 0.2536
```

The static relabel preserved stability but barely moved the tracking plateau.
This closes static gate-aware source-VX relabeling as a standalone fix. The
next deployable-policy branch needs closed-loop fine-tuning with gate feedback,
explicit support-transition correction, or recurrent/phase-aware state rather
than another static BC relabel.

## PPO Warm-Start Tracking-Correction Smoke

The pitch-chain `4.3` PPO-shape BC student was converted into a real Brax PPO
checkpoint and exported through the standard Playground ONNX path.

```text
result doc: docs/PPO_WARMSTART_TRACKING_CORRECTION_SMOKE_RESULT.md
step-0 export: outputs/analysis/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT_WARMSTART_STEP0_EXPORT_FIDELITY.md
step-0 gate: outputs/analysis/PITCH_CHAIN_4P3_PPO_SHAPE_RATE_STUDENT_WARMSTART_STEP0_MULTI_SEED_FITTED_BACKLASH.md
status: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
```

The step-0 PPO export preserved the stable-but-held baseline:

```text
duration_complete: 8/8
falls: 0/8
mean vx: 0.0396 m/s
mean track ratio: 0.4944
max pitch velocity p95: 3.6200-3.7078 rad/s
max tracking p95: 0.2522-0.2583 rad
```

A tiny PPO correction smoke then ran from that checkpoint with the fitted
bridge active, fixed `x=0.08`, weak behavior prior, and tracking/target-rate
penalties.

```text
smoke status: PASS_SMOKE_RUN
screen artifact: outputs/analysis/PITCH_CHAIN_4P3_PPO_WARMSTART_TRACKING_CORRECTION_SMOKE_SEED1_SEED4_SCREEN.md
screen status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 1: vx -0.0007, track ratio -0.0082, tracking p95 0.1121
seed 4: vx  0.0031, track ratio  0.0392, tracking p95 0.1078
```

This proves the PPO resume/update/export path is usable, but the naive
tracking-correction recipe is rejected. It reduces tracking error by nearly
freezing the gait. The next PPO branch must preserve forward behavior much more
strictly, likely with a trust-region/behavior-preservation mechanism and
short-run gates that treat progress loss as an immediate failure.

A follow-up behavior-preservation control removed target-rate and
actuator-tracking penalties, lowered the learning rate, and strengthened the
behavior prior:

```text
screen artifact: outputs/analysis/PITCH_CHAIN_4P3_PPO_WARMSTART_BEHAVIOR_PRESERVATION_CONTROL_SEED1_SEED4_SCREEN.md
screen status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 1: vx -0.0008, track ratio -0.0104, tracking p95 0.1213
seed 4: vx  0.0035, track ratio  0.0433, tracking p95 0.1170
```

This means the freeze is not only caused by explicit tracking penalties. The
current PPO resume/reward setup moves the warm-start out of the walking basin
even under a behavior-preservation control. The next attempt needs a stronger
policy-distribution trust region or a different update mechanism, not another
small scalar reward tweak.
