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
checked score artifacts: 56
passing target sources: 0
```

The failure-mode analysis scans the same compact score family:

```text
outputs/analysis/WEIGHT_TRANSFER_GATE_FAILURE_ANALYSIS.md
status: HOLD_FORWARD_IMPULSE_PRIMARY
seed rows scanned: 2808
```

It found:

```text
stable + actuator-safe rows: 964
support-ready rows: 492
forward-ready rows: 15
stable + support rows: 7
stable + forward rows: 0
support + forward rows: 1
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

The next branch decision is now explicit:

```text
tool: tools/decide_next_weight_transfer_branch.py
artifact: outputs/analysis/NEXT_WEIGHT_TRANSFER_BRANCH.md
status: PLAN_FOOT_PLACEMENT_MPC_TEACHER
```

That means the next offline implementation should be a finite-horizon
state-feedback teacher/optimizer that chooses stance side, lateral body
placement, swing-foot placement, and push timing together. Do not launch PPO/BC
or robot validation from current target sources.

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
