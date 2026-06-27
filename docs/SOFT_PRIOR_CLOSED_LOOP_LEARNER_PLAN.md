# Soft-Prior Closed-Loop Learner Plan

Date: 2026-06-25

This is an offline-only plan. It does not authorize robot tests, SSH, deploy,
runtime changes, policy deployment, or a large PPO/A100 run.

## Purpose

Define the next safe learning experiment after the target-generation branch
showed that short low-command motion fragments exist, but are not stable
reusable action labels.

The next learner should use those fragments as a soft motion prior inside
closed-loop simulation, not as hard behavior-cloning targets.

## Current State

The following target paths have been tested:

```text
one-step BC from curated target windows:
  HOLD_BC_REPLAY_LOW_FORWARD_MOTION or HOLD_BC_REPLAY_TERMINATED

sequence replay, 1.2 s:
  HOLD_SEQUENCE_REPLAY_LATERAL_UNSTABLE

sequence replay, 3.0 s:
  HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION

periodic seam correction:
  HOLD_SEQUENCE_REPLAY_TERMINATED

contact_hold / contact_match / state_match adapters:
  HOLD_SEQUENCE_REPLAY_LOW_FORWARD_MOTION

100-150 sample sustained primitive targets:
  HOLD_NO_SEED_ROBUST_TARGETS
```

Interpretation:

```text
The 50-tick fragments contain useful motion hints.
They are not complete gait labels.
Training directly against them teaches freeze, lunge, or low-progress replay.
```

## What Changes

The next experiment should stop asking:

```text
Can this target table be cloned exactly?
```

It should ask:

```text
Can a closed-loop policy use the fragment as a weak gait-shape prior while
still being rewarded for real forward motion, posture, and survival?
```

## Soft Prior Definition

A soft prior is a bounded auxiliary cost computed during closed-loop rollout.
It nudges the policy toward the fragment's gait structure but must not dominate
the task.

Allowed prior terms:

```text
phase-conditioned action-shape prior:
  compare policy action to nearest/selected fragment action

pitch-chain shape prior:
  compare only hip pitch, knee, and ankle pitch structure

left/right phase prior:
  encourage alternating leg structure without forcing exact amplitudes

target-rate prior:
  prefer the fragment's low target-velocity envelope

contact-transition prior:
  encourage at least one safe contact transition over the short window
```

Terms to avoid:

```text
hard action labels
hard target-position tracking
full-body cloning against the aggregate table
uniform trust-region to a fragment that already fails when looped
```

## First Smoke

Before any GPU training, implement a CPU/local smoke that evaluates a candidate
soft-prior objective without fitting a neural policy.

Minimum smoke:

```text
input: target_dataset_manifest_dynamic_roll_lateral_fix_robust_modes.json
duration: 1.2 s and 3.0 s
seeds: 0,2
command_x: 0.04
policy source: existing sequence replay or a simple prior-guided controller
outputs: markdown/json prior-term and rollout metrics
```

The smoke should report:

```text
mean local vx
track ratio
vy_abs_p95
body_pitch_abs_p95
base_height_min
sent target velocity p95
contact dominance
contact transitions
prior cost mean/p95
task reward mean
whether prior cost collapses into freeze
```

## Training Gate

Only the following result permits a small supervised/closed-loop learner:

```text
PASS_SOFT_PRIOR_SMOKE:
  seed0 and seed2 complete 1.2 s with forward motion,
  no lateral/pitch/height hard fail,
  sent target velocity p95 <= 3.75 rad/s,
  and the prior does not reduce mean vx below 0.02 m/s.
```

The following results block training:

```text
HOLD_SOFT_PRIOR_FREEZE:
  prior lowers motion into standstill

HOLD_SOFT_PRIOR_LUNGE:
  prior produces high pitch / high velocity lunge

HOLD_SOFT_PRIOR_LATERAL_UNSTABLE:
  prior preserves forward motion but fails lateral stability

HOLD_SOFT_PRIOR_CONTACT_STUCK:
  prior keeps a single contact pattern dominant

HOLD_SOFT_PRIOR_NOT_IMPLEMENTED:
  objective cannot be evaluated without editing Playground/training code
```

## If Smoke Passes

The first learner should be deliberately small:

```text
one phase only
command_x: 0.04
vanilla dynamics first
soft-prior scale: low and scheduled down
forward-progress floor: still active
reverse-motion penalty: active
fall/height/pitch gates: active
no fitted bridge until low-command vanilla passes
```

Grade by multi-seed rollout, not training reward:

```text
seeds: 0-7
mean local vx > 0.02 m/s
track ratio positive and not above 2.0
falls fewer than target baseline
standstill seeds fewer than target baseline
reverse seeds zero or reduced
target velocity remains in envelope
```

## Stop Rule

If the soft-prior learner still produces freeze/reverse/collapse across the
same seed distribution, stop this branch. Do not keep increasing prior scale.

Next branch after a hold:

```text
change generator structure to produce a longer self-consistent gait,
or import a valid external/reference gait with compatible target-rate/contact
behavior.
```

## Non-Goals

```text
do not run robot validation
do not run x=0.08
do not deploy a candidate
do not change robot runtime behavior
do not relax the actuator envelope
do not treat the short fragments as hard labels
do not launch an A100 PPO run until PASS_SOFT_PRIOR_SMOKE
```

## Implementation Tasks

1. Add an offline prior-signal evaluator for target fragments.
2. Add default-off prior terms to the local eval/training wrapper only after the
   evaluator passes import and shape checks.
3. Run the CPU smoke on seeds 0 and 2.
4. Commit compact markdown/json artifacts only.
5. If and only if `PASS_SOFT_PRIOR_SMOKE`, prepare a tiny one-phase learner
   recipe for review.

## Fragment Config Artifact

The first compact fragment-prior config has been generated:

```text
tool: tools/build_soft_prior_fragment_config.py
status: PASS_SOFT_PRIOR_CONFIG_READY
dataset_id: c4833a96744101d9
entries: 9
source_files: 2
window_len: 50
max pitch-chain target velocity p95: 2.4428 rad/s
```

Artifacts:

```text
outputs/analysis/SOFT_PRIOR_FRAGMENT_CONFIG.md
outputs/analysis/soft_prior_fragment_config.json
```

Interpretation:

```text
The robust target fragments can be distilled into a compact pitch-chain/contact
phase prior inside the measured actuator envelope. This still does not permit
training. It only unblocks the next default-off smoke evaluator.
```

## Prior-Only Smoke Result

The compact prior was replayed as a pitch-chain-only closed-loop controller in
CPU sim. This is still not training; it only tests whether the prior itself is a
usable controller-like target.

Artifacts:

```text
outputs/analysis/SOFT_PRIOR_SMOKE_1P2S.md
outputs/analysis/soft_prior_smoke_1p2s.json
outputs/analysis/SOFT_PRIOR_SMOKE.md
outputs/analysis/soft_prior_smoke.json
```

Results:

```text
1.2 s:
  status: HOLD_SOFT_PRIOR_LATERAL_UNSTABLE
  seed0 vx: 0.0325 m/s, vy95: 0.0981 m/s, pitch95: 0.2734 rad
  seed2 vx: 0.0414 m/s, vy95: 0.1495 m/s, pitch95: 0.2888 rad

3.0 s:
  status: HOLD_SOFT_PRIOR_FREEZE
  seed0 vx: 0.0115 m/s, vy95: 0.0513 m/s, pitch95: 0.2685 rad
  seed2 vx: 0.0143 m/s, vy95: 0.0770 m/s, pitch95: 0.2830 rad
```

Interpretation:

```text
The compact prior is useful motion-shape material, but it is not sufficient as
a direct controller. It creates short forward motion, then decays into low
progress. A learner must use it as a weak auxiliary term while optimizing real
closed-loop progress and posture.
```

Next step:

```text
Implement the soft prior as a default-off auxiliary reward/regularizer in a
tiny one-phase learner. Do not run a large A100 job until that learner has a
reviewed recipe and phase gate.
```
