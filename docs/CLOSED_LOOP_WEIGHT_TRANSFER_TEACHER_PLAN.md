# Closed-Loop Weight-Transfer Teacher Plan

Date: 2026-06-25

This is an offline sim plan. It does not authorize robot tests, SSH,
deployment, runtime changes, policy deployment, or training.

## Purpose

Define the next target-generation step after the primitive family failed to
produce sustained low-command forward motion.

The current blocker is not binary foot-contact detection alone. The latest
target-source evidence says:

```text
raw polynomial reference:
  high contact mismatch, actual sim stays double-support dominated

dynamic-roll lateral-fix fragments:
  low binary contact mismatch in short closed-loop replay
  still low forward velocity and weak sustained transfer

roll/lift primitives:
  more support transitions, near-zero forward progress

stance-push primitives:
  slight forward improvement, still far below 0.04 m/s

velocity-feedback stance push:
  local-vx feedback added to same sinusoid template
  still far below 0.04 m/s
```

So the next generator should stop adding scalar terms to the same open-loop
sinusoid. It should test a state-feedback teacher that couples:

```text
support phase
body/CoM lean
stance-leg loading
swing-side clearance
forward displacement
pitch/height stabilization
```

## Current Evidence

The sustained target gate is still held:

```text
artifact: outputs/analysis/WEIGHT_TRANSFER_TARGET_GATE.md
status: HOLD_NO_SUSTAINED_WEIGHT_TRANSFER_TARGET
```

The most recent probes all failed `PASS_WEIGHT_TRANSFER_TARGET`:

| probe | best 100-tick vx | best 150-tick vx | result |
|---|---:|---:|---|
| weight-transfer roll/lift | 0.0045 / 0.0043 m/s | 0.0018 / 0.0035 m/s | low forward velocity |
| stance push | 0.0089 / 0.0108 m/s | 0.0028 / 0.0061 m/s | low forward velocity |
| velocity-feedback stance push | 0.0070 / 0.0061 m/s | 0.0031 / 0.0058 m/s | low forward velocity |

These probes can create limited support transitions. They do not create
seed-robust forward displacement.

## Hypothesis

The missing mechanism is sustained weight transfer, not another fixed waveform
parameter.

The teacher should actively decide when to:

```text
1. shift load toward the stance side
2. keep base height and pitch inside gates
3. unload the swing side without collapsing
4. push forward from the loaded stance side
5. switch sides only after safe support is established
```

This is different from the current primitive family, which schedules all of
those effects from phase alone and only applies a scalar velocity correction.

## First Teacher Prototype

Add a new offline tool rather than extending
`tools/search_low_command_target_primitives.py` again.

Proposed tool:

```text
tools/probe_closed_loop_weight_transfer_teacher.py
```

Inputs:

```text
--playground-path ../Open_Duck_Playground
--command-x 0.04
--duration-s 3.0
--seeds 0,2
--output-md outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_PROBE.md
--output-json outputs/analysis/closed_loop_weight_transfer_teacher_probe.json
--trace-dir outputs/analysis/closed_loop_weight_transfer_teacher_probe_traces
```

The tool should be CPU-safe and offline-only. It should write raw JSONL traces
under an ignored trace directory and commit only compact markdown/json
summaries.

## Teacher State

The first prototype should use measured sim state, not a fixed phase-only
schedule:

```text
local_vx
local_vy
body_pitch
body_pitch_rate if available
base_height
left/right foot contacts
left/right foot site height
current support side
time since last support transition
```

Derived terms:

```text
forward_error = command_x - local_vx
pitch_error = target_pitch - body_pitch
support_ready = stance contact true and base_height above gate
swing_clear = swing foot z above threshold or swing contact false
transition_allowed = support_ready and minimum dwell elapsed
```

## Teacher Action Structure

Start with the same actuator envelope as the current sim:

```text
action_scale = 0.25
target velocity p95 gate <= 2.5 rad/s for target-source probes
joint tracking p95 gate <= 0.12 rad
```

Use a small set of interpretable target terms:

```text
stance hip pitch push:
  proportional to forward_error, clipped

stance ankle pitch:
  coupled to push and pitch damping

swing knee/ankle lift:
  only active while swing-side contact is expected to release

hip roll / lateral load shift:
  proportional to desired support side, corrected by local_vy

pitch damping:
  reduce push or add ankle correction when body_pitch grows
```

All terms must be clipped before conversion to normalized action. The teacher
must report target velocity, action saturation, and tracking metrics exactly
like the primitive generator.

## Required Gates

The first probe does not need to pass. It must tell us whether a stateful
teacher improves the right metrics compared with the primitive probes.

Primary gate:

```text
PASS_WEIGHT_TRANSFER_TEACHER_PROBE:
  seeds 0 and 2 both have a 100-tick window with:
    mean_vx >= 0.04 m/s
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

Useful hold results:

```text
HOLD_FORWARD_STILL_LOW:
  support transfer improves but vx remains below 0.04 m/s

HOLD_SUPPORT_TRANSFER_FAILED:
  teacher still stays double-support dominated

HOLD_PITCH_OR_HEIGHT_UNSTABLE:
  teacher creates forward/support motion but collapses posture

HOLD_LATERAL_UNSTABLE:
  teacher creates forward/support motion but side drift fails

HOLD_ACTUATOR_ENVELOPE:
  teacher only works by exceeding target-rate/tracking gates
```

## Stop Rule

Do not launch PPO, BC, or another A100 training run from this branch until
there is at least one compact artifact showing either:

```text
PASS_WEIGHT_TRANSFER_TEACHER_PROBE
```

or a specific hold that changes the next design variable.

Do not keep expanding the open-loop sinusoid grid. The latest probes already
show that scalar roll/lift/push/velocity terms do not produce the missing
mechanism.

## First Probe Result

The first implementation is:

```text
tools/probe_closed_loop_weight_transfer_teacher.py
```

It ran a bounded local CPU probe with 24 candidates, seeds `0,2`, and
`command_x=0.04`:

```text
artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_PROBE.md
score_100: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_SCORE_100.md
score_150: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Result:

```text
top aggregate rollout mean vx: 0.0232 m/s
100-tick robust modes: 0
150-tick robust modes: 0
main failures: low_forward_velocity and high_lateral_velocity
```

This is not training permission. The probe shows that state feedback can create
more contact transitions and more raw forward motion than the open-loop
primitive probes, but the first controller couples forward push and lateral
load shift too strongly. The next teacher revision should explicitly damp
local lateral velocity and center the body/CoM while preserving support
transitions.

The second probe added body-y centering and lateral-speed push gating:

```text
flags:
  --body-y-gains
  --push-lateral-gates

artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V2_PROBE.md
score_100: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V2_SCORE_100.md
score_150: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V2_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

V2 raised the best raw rollout mean velocity to `0.0305 m/s`, but robust
objective scoring still found zero passing 100/150 tick modes. The tradeoff is
now explicit: moving candidates fail lateral velocity, and lateral-stable
candidates lose forward displacement. The next teacher design should add an
explicit forward step geometry or foot-placement/CoM planner rather than only
more roll and stance-push feedback.

V3 added explicit step geometry:

```text
flags:
  --swing-hip-reaches
  --stance-retract-scales
  --pitch-targets

artifact: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V3_PROBE.md
score_100: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V3_SCORE_100.md
score_150: outputs/analysis/CLOSED_LOOP_WEIGHT_TRANSFER_TEACHER_V3_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

V3 raised the top raw rollout mean velocity to `0.0337 m/s`, but the best
scored 100-tick window still only reached `0.0104 / 0.0155 m/s` on seeds
`0 / 2`, with lateral p95 around `0.13-0.14 m/s`. The next revision should not
be a larger random grid over these same terms. It should change the structure
to a staged planner or optimizer that first controls lateral balance, then
executes a forward step while preserving the lateral gate.

That staged planner branch was tested in:

```text
tool: tools/probe_staged_weight_transfer_planner.py
doc: docs/STAGED_WEIGHT_TRANSFER_PLANNER.md
artifact: outputs/analysis/STAGED_WEIGHT_TRANSFER_PLANNER_PROBE.md
score_100: outputs/analysis/STAGED_WEIGHT_TRANSFER_PLANNER_SCORE_100.md
score_150: outputs/analysis/STAGED_WEIGHT_TRANSFER_PLANNER_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

The best 100-tick candidate met the lateral gate but had only
`0.0015 / 0.0034 m/s` forward velocity on seeds `0 / 2`. The staged gates were
too conservative: they preserved support transitions and lateral control by
nearly eliminating forward displacement. This confirms the next target-source
work should move to short-horizon optimization or a richer body-state
controller, not another random sweep of hand-shaped periodic/planner terms.

## Next Branch After a Pass

If the teacher probe passes, use its traces as a target source:

```text
1. score 100-150 tick windows with tools/score_target_candidates_objective.py
2. mine/curate target windows if needed
3. build a small target dataset manifest
4. run CPU closed-loop replay before any training
5. only then consider a tiny supervised or soft-prior learner
```

If the teacher produces forward motion only by exceeding the actuator envelope,
the branch should stop and return to the actuator-feasibility conclusion rather
than hiding that violation in training.

## Non-Goals

```text
do not run robot tests
do not SSH
do not deploy
do not train
do not run x=0.08
do not change BEST_WALK_ONNX_2
do not relax target-source gates to make a pass
do not treat contact matching alone as success
```
