# Foot-Placement MPC Teacher Spec

This is an offline implementation spec. It does not authorize robot tests, SSH,
deployment, runtime changes, policy deployment, PPO/BC training, grounded
replay, or `x=0.08`.

## Purpose

The current target-source branch is held at:

```text
outputs/analysis/NEXT_WEIGHT_TRANSFER_BRANCH.md
status: PLAN_FOOT_PLACEMENT_MPC_TEACHER
```

The next implementation should build a finite-horizon state-feedback
teacher/optimizer that generates a 100-150 tick target source with:

```text
forward progress
useful left/right single-support alternation
low lateral velocity
stable pitch and base height
actuator-safe target velocities
seed robustness across at least seeds 0 and 2
```

This is not another scalar expansion of the existing support-state teacher. It
must couple stance side, lateral body placement, swing-foot placement, and
forward push timing in one scored horizon.

## Why This Branch

The current evidence says:

```text
checked target score artifacts: 58
passing target sources: 0
failure analysis rows scanned: 2872
stable + actuator-safe rows: 1250
support-ready rows: 789
forward-ready rows: 15
stable + support rows: 9
stable + forward rows: 0
support + forward rows: 1
all three rows: 0
```

The latest stance leg-extension probe also held:

```text
100-tick robust modes: 0 / 18
150-tick robust modes: 0 / 18
dominant failures: low_forward_velocity and high_lateral_velocity
```

So the missing mechanism is not binary contact labels, phase-state plumbing,
hip-pitch stance push, or local knee/ankle push-off in the current teacher. The
missing mechanism is coordinated weight transfer plus propulsion.

## Proposed Tool

```text
tools/probe_foot_placement_mpc_teacher.py
```

Default behavior:

```text
offline only
CPU platform by default
no training
no robot access
no deployment
write raw traces under ignored trace directories
commit compact markdown/json summaries only
```

Required flags:

```text
--playground-path ../Open_Duck_Playground
--task flat_terrain
--command-x 0.04
--duration-s 3.0
--seeds 0,2
--jax-platform cpu
--initial-stance-sides=-1.0,1.0
--max-candidates 8
--trace-dir outputs/analysis/foot_placement_mpc_teacher_smoke_v3_traces
--output-md outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_PROBE.md
--output-json outputs/analysis/foot_placement_mpc_teacher_probe.json
```

## State Inputs

The teacher must read sim state every tick:

```text
local_vx
local_vy
base_x
base_y
base_height
body_pitch
body_pitch_rate if available
left/right foot contacts
left/right foot site xyz
current support side
time in current support state
previous motor targets
```

It should derive:

```text
base_y_relative_to_stance
base_x_relative_to_stance
swing_foot_clearance
stance_loaded
lateral_ready
pitch_ready
height_ready
push_window
transition_allowed
```

## Candidate Parameters

Each finite-horizon candidate should choose at least:

```text
cycle_ticks
stance_side_sequence
load_shift_y_m
stance_body_x_offset_m
swing_foot_x_target_m
swing_foot_z_clearance_m
stance_push_hip_rad
stance_push_knee_rad
stance_push_ankle_rad
push_start_fraction
push_end_fraction
lateral_damping_gain
base_y_gain
pitch_damping_gain
height_guard_m
max_target_velocity_rad_s
```

The search should mutate these parameters between iterations rather than
randomly sampling unrelated action tables forever.

## Control Structure

Each candidate rollout should use a small state machine:

```text
LOAD_STANCE:
  move body laterally toward stance foot
  keep pitch and height within gates
  do not request swing until stance is loaded

UNWEIGHT_SWING:
  lift swing foot and place it slightly forward
  keep lateral velocity bounded
  abort/hold if base height or pitch leaves gate

PUSH_FORWARD:
  apply forward push only after stance loading
  push with coordinated hip/knee/ankle terms
  reduce push when lateral velocity or pitch grows

RECOVER_OR_SWITCH:
  switch sides only after useful support transition or safe timeout
  otherwise recover base-y/pitch/height before another push
```

This differs from the existing teacher because stance selection, foot placement,
and push timing are optimized/scored as a horizon, not just phase-scheduled
from a scalar grid.

## Scoring

The tool should emit JSONL traces compatible with:

```bash
python3 tools/score_target_candidates_objective.py
```

Primary gate:

```text
PASS_WEIGHT_TRANSFER_TARGET:
  seeds 0 and 2
  100-150 tick window
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

Secondary diagnostics:

```text
phase occupancy
stance_loaded_pct
lateral_ready_pct
push_allowed_pct
push_used_pct
transition_count
forced_transition_count
forward_displacement_per_cycle
lateral_displacement_per_cycle
support side dwell times
```

## Status Results

The probe should output exactly one top-level status:

```text
PASS_FOOT_PLACEMENT_MPC_TARGET
  At least one candidate passes PASS_WEIGHT_TRANSFER_TARGET.

HOLD_FORWARD_IMPULSE_LOW
  Support/lateral gates are acceptable, but forward velocity remains low.

HOLD_LATERAL_UNSTABLE
  Forward motion exists, but lateral velocity/base-y fails.

HOLD_SUPPORT_TRANSFER_FAILED
  Candidate remains double-support dominated or misses one support side.

HOLD_PITCH_OR_HEIGHT_UNSTABLE
  Candidate moves/supports but loses pitch or base height.

HOLD_ACTUATOR_ENVELOPE
  Candidate only works by exceeding target velocity or tracking gates.

HOLD_NO_CANDIDATES
  Tool did not evaluate any candidate.
```

## Current Probe Findings

The first probe family has been useful as a diagnostic, but it has not produced
`PASS_WEIGHT_TRANSFER_TARGET`.

```text
corrected stance-interleaved smoke:
  robust 100/150 tick modes: 0 / 8

stronger push:
  robust 100/150 tick modes: 0 / 16

swing-foot advance:
  robust 100/150 tick modes: 0 / 16

wide swing-foot advance:
  robust 100/150 tick modes: 0 / 16

lateral/yaw push attenuation:
  robust 100/150 tick modes: 0 / 64

higher swing clearance:
  robust 100/150 tick modes: 0 / 16

hip-yaw heading support:
  robust 100/150 tick modes: 0 / 72

relative-yaw recovery gating:
  robust 100/150 tick modes: 0 / 16
```

The latest stability probe added default-off fields:

```text
push_lateral_soft_gate_m_s
push_yaw_soft_gate_rad
push_min_scale
```

Those fields are useful for diagnosis and trace logging, but the result was a
hold: attenuation reduced push aggressiveness and kept target velocity low, but
it reduced forward velocity to roughly `0.003-0.008 m/s` in the best windows.

The high-clearance probe shows that larger swing lift can create more
single-support time, but the useful windows then fail on lateral velocity,
forward velocity, and sometimes target velocity. Conclusion: the next revision
should not keep widening this scalar grid. It needs an active lateral/heading
support controller that creates a pushable stance, then applies propulsion
without losing the support state. A simple hip-yaw overlay did not provide that
controller; it either suppresses motion back toward double-support or allows the
same lateral/yaw drift when support transfer improves.

The relative-yaw recovery probe corrected an important diagnostic bug: switch
readiness must be computed from yaw error relative to the rollout's initial
heading, not from absolute world yaw. After that fix, switch readiness is high
in the leading candidates, about `75-97%`, so yaw recovery is not the current
primary blocker. The probe still fails because local forward velocity is far
below the `0.04 m/s` gate and seed 2 remains laterally unstable. Do not spend
the next branch on another yaw gate or recovery hold. The missing piece is
forward impulse coupled to lateral/stance support.

## Stop Rules

Stop the branch and do not train if:

```text
100-150 tick windows still have zero robust modes
forward motion only appears with vy_abs_p95 > 0.12 m/s
one support side is missing
target velocity exceeds the measured actuator envelope
the best candidates repeat the existing double-support shuffle
```

## Training Re-Entry Rule

Only after `PASS_WEIGHT_TRANSFER_TARGET`:

```text
1. build a compact reviewed target manifest
2. run CPU closed-loop replay
3. run a small supervised/imitation smoke
4. gate x=0.04 vanilla across seeds
5. reintroduce mild/fitted actuator bridge only after coherent motion exists
```

Robot validation remains blocked until offline low-command multi-seed gates
pass.

## First Implementation Smoke

The first implementation is available as:

```text
tool: tools/probe_foot_placement_mpc_teacher.py
```

It is a bounded CPU state-feedback probe, not a full nonlinear MPC solver. It
reads sim state each tick, selects a stance side, shifts the body laterally,
places the swing foot forward with joint-space approximations, times a stance
push, and writes traces compatible with:

```bash
python3 tools/score_target_candidates_objective.py
```

The first one-sided smoke and corrected stance-interleaved smoke both held:

```text
artifacts:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_SMOKE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_SMOKE_SCORE_150.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_SMOKE_V3_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_SMOKE_V3_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
stance-interleaved modes: 8
stance-interleaved robust modes: 0
```

The corrected probe interleaves initial left/right stance candidates before
`--max-candidates` truncation. It removed the initial-stance ambiguity but
still failed for low forward velocity on both seeds. Seed 2 produced partial
forward motion and some single-support windows; seed 0 remained near stationary
and mostly double-support. This means the tool is a useful probe, but the first
candidate set is not a target source and does not authorize BC, PPO, x=0.08, or
robot validation.

A stronger-push / relaxed-readiness diagnostic also held:

```text
artifacts:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_PUSH_PROBE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_PUSH_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
modes: 16
robust modes: 0
```

That probe increased seed 2 forward motion and single-support occupancy, but
seed 0 remained near-zero or backward and lateral velocity rose. This rules out
"just push harder" as a sufficient local fix. The next useful revision needs a
better coupled stance-load / foot-placement / lateral-balance controller, not
only larger stance hip/knee/ankle pushes.

The probe and scorer now also log orientation diagnostics:

```text
trace fields:
  body_roll_rad
  body_pitch_rad
  body_yaw_rad
score metrics:
  body_roll_abs_p95_rad
  body_yaw_change_abs_p95_rad
  world_x_displacement_m
```

The first orientation smoke held:

```text
artifact: outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ORIENTATION_SMOKE_SCORE_100.md
status: HOLD_NO_SEED_ROBUST_TARGETS
modes: 2
robust modes: 0
```

It confirmed that local-forward progress can diverge from world-x displacement
when heading changes. Future teacher revisions should preserve both local
forward velocity and heading/lateral stability rather than optimizing one in
isolation.

A swing-foot minimum-advance diagnostic was also tested:

```text
artifacts:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ADVANCE_PROBE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ADVANCE_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
modes: 16
robust modes: 0
```

This addressed a concrete seed-0 issue where `stance_foot_x + foot_place_x`
could ask the swing foot to move backward when the stance foot started behind
the swing foot. The best 100-tick candidate improved seed 0 to small positive
local vx, but it still failed the forward gate and introduced lateral/yaw
tradeoffs. Keep `--swing-min-advance` as a useful parameter, but do not treat it
as sufficient without better lateral/heading stabilization.

A wider swing-advance probe also held:

```text
artifacts:
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ADVANCE_WIDE_PROBE_SCORE_100.md
  outputs/analysis/FOOT_PLACEMENT_MPC_TEACHER_ADVANCE_WIDE_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
modes: 16
robust modes: 0
```

The best 100-tick wide-advance candidate improved the worst-seed score and kept
seed 0 positive, but both seeds stayed well below the 0.04 m/s forward gate.
This suggests foot advance has useful signal but saturates quickly without
better lateral/heading stabilization.
