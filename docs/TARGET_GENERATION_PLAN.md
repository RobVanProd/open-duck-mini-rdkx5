# Target Generation Plan

Date: 2026-06-25

## Purpose

Define the next offline path for creating low-command walking target data after
the V20 reference and realized-window audits.

This is not a robot-test plan and not a training launch plan.

## Current Evidence

The following paths have been tested and are not sufficient:

```text
raw matched polynomial reference:
  fails rollout, high contact mismatch, exceeds action/rate envelope

cycle-projected reference:
  reduces action/rate stress, still terminates, contact mismatch stays ~68%

home-near projected phases:
  still terminate, contact mismatch stays ~67-68%

contact-gated projected reference:
  small mismatch improvement only, actual double support rises to 84.95%

contact-synchronized projected reference:
  contact mismatch drops to 4.36% aggregate
  forward velocity becomes negative/near-zero
  7/8 seeds terminate

existing trace archive:
  94 compatible mined windows
  1 curated seed-quality window

V5/V7 low-command replay:
  no realized target windows at x=0.04
```

## Conclusion

The blocker is no longer simply:

```text
reward weights
reference command mismatch
reference phase offset
contact-bit encoding
target-rate envelope
old moving-policy replay
```

The current blocker is:

```text
target generation that jointly preserves:
  positive forward velocity
  low lateral velocity
  safe body pitch and base height
  real contact transitions
  actuator/action envelope compliance
```

## Non-Goals

```text
do not run robot tests
do not deploy
do not change runtime behavior
do not launch another reward-only PPO variant
do not train BC from the current mined-window manifest
do not train directly against raw polynomial joint targets
do not treat contact matching alone as success
```

## Next Offline Experiment

Build a deliberate low-command target generator that searches or optimizes
short horizon target windows in sim, then grades the result with the existing
curation gate.

The generator should produce candidate windows, not a policy.

Minimum target window:

```text
command_x: 0.04
window length: 25-50 samples
mean vx >= 0.04 m/s
vy_abs_p95 <= 0.12 m/s
pitch_abs_p95 <= 0.35 rad
base_height_min >= 0.145 m
action_saturation <= 1.0%
sent_target_velocity_p95 <= 2.5 rad/s
joint_tracking_p95 <= 0.12 rad
post-window done margin >= 50 ticks if termination occurs
contact dominance <= 95%
```

## Candidate Generator Designs

Ranked options:

1. **Short-horizon target search around projected reference**
   - Start from the projected reference target cycle.
   - Search phase, amplitude, lateral scale, and cadence over short windows.
   - Score only realized sim motion.
   - Keep windows that pass the curation gate.

2. **Contact-transition constrained search**
   - Add explicit pressure for at least one safe contact transition.
   - Reject windows that remain in double support for the whole segment.
   - Keep forward velocity and lateral velocity in the score.

3. **Low-dimensional gait primitive search**
   - Parameterize hip/knee/ankle pitch waveforms directly.
   - Search cadence, phase offsets, amplitude, and stance timing.
   - Use the actuator envelope and curation gate as hard constraints.

4. **Reference adaptation with forward objective**
   - Use contact synchronization only as one term.
   - Add forward displacement and lateral stability requirements.
   - Do not optimize contact matching alone.

## Stop/Go Gates

Do not proceed to supervised pretraining until:

```text
curated_seed_windows >= 8
windows span at least 2 seeds or generator initializations
windows are not all from one contact pattern
no window is within 50 ticks of a later termination unless explicitly labeled review-only
```

Proceed to supervised seed only if:

```text
PASS_CURATED_DATASET_SEED_READY
```

Hold if:

```text
HOLD_INSUFFICIENT_CURATED_WINDOWS
HOLD_CONTACT_MATCH_ONLY_NO_FORWARD_MOTION
HOLD_FORWARD_WITH_HIGH_LATERAL_OR_PITCH
HOLD_ACTION_OR_TARGET_RATE_ENVELOPE
```

## Required Artifacts

For the next generator PR, produce:

```text
outputs/analysis/TARGET_GENERATOR_SEARCH.md
outputs/analysis/target_generator_search.json
outputs/analysis/TARGET_GENERATOR_WINDOW_MINE.md
outputs/analysis/target_generator_window_mine.json
outputs/analysis/TARGET_GENERATOR_WINDOW_CURATION.md
outputs/analysis/target_generator_window_curation.json
```

Do not commit raw trace slices unless explicitly approved. Commit compact
manifests and summaries only.

## First Primitive Search Result

A bounded low-dimensional sine primitive search was run as the first generator
implementation:

```text
tool: tools/search_low_command_target_primitives.py
command_x: 0.04
duration: 3 s
seeds: 0
candidates: 12
```

Result:

```text
search status: PASS_TARGET_SEARCH_RAN
best mean vx: 0.0018 m/s
window mine: HOLD_NO_REALIZED_WINDOWS
curated seed windows: 0
```

Interpretation:

```text
Small anti-phase hip/knee/ankle pitch sine primitives are stable but behave like
standstill. They do not produce low-command target windows. The next primitive
search must add a stronger mechanism for forward displacement, such as stance
asymmetry, body pitch bias, foot clearance/placement terms, or an optimizer that
scores forward progress directly instead of only sweeping symmetric waveforms.
```

Artifacts:

```text
outputs/analysis/TARGET_GENERATOR_SEARCH.md
outputs/analysis/target_generator_search.json
outputs/analysis/TARGET_GENERATOR_WINDOW_MINE.md
outputs/analysis/target_generator_window_mine.json
outputs/analysis/TARGET_GENERATOR_WINDOW_CURATION.md
outputs/analysis/target_generator_window_curation.json
```
