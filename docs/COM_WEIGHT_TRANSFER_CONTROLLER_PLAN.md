# CoM Weight-Transfer Controller Plan

This is the next offline implementation plan after the support-state and
support-loaded probes. It does not authorize robot tests, deployment, training,
SSH, or runtime behavior changes.

## Why This Plan Exists

The target-source campaign has tested these branches:

```text
phase-scheduled teachers
forward-intent teachers
lateral-refined teachers
support-state stance selection
support-loaded stance push
```

All held. The current aggregate status is:

```text
artifact: outputs/analysis/WEIGHT_TRANSFER_TARGET_CAMPAIGN_SUMMARY.md
status: HOLD_FORWARD_LATERAL_SUPPORT_TRADEOFF
```

The most recent probes show:

```text
support-state stance selection:
  improves contact transitions, but misses forward displacement and lateral gate

support-loaded stance push:
  improves support dwell slightly, but still misses forward displacement and
  lateral gate
```

So the missing behavior is not merely:

```text
pick the stance foot from contact
wait for single support before pushing
```

The missing behavior is:

```text
place and regulate the body over the stance foot, then push forward without
creating excessive lateral momentum.
```

## Controller Hypothesis

A useful low-command target source needs an explicit center-of-mass style
controller, even if it is approximate and uses only the MJX state available in
the current tools.

The controller should regulate:

```text
base_y relative to the stance side
local_vy
body_roll if available
body_pitch and pitch rate
base_height
stance-foot contact and dwell time
swing-foot clearance
local forward displacement
```

The key idea is to split a step into three stateful phases:

```text
1. LOAD_STANCE:
   move body laterally toward the intended stance foot while limiting local_vy
   and maintaining height/pitch.

2. UNWEIGHT_SWING:
   lift the swing foot only after stance loading is inside gate.

3. PUSH_FORWARD:
   apply forward stance push only while stance support is stable and lateral
   momentum is bounded.
```

This differs from previous probes because phase time is not the primary
decision variable. Phase can provide a timeout or fallback, but transitions
should be driven by state gates.

## State Variables

Use what the current MJX tools can already log:

```text
local_vx
local_vy
base_y
base_height
body_pitch
foot_contacts
foot_site_z
time in current phase
contact transitions
sent target velocity
joint tracking error
```

Add if easily available without broad refactor:

```text
body_roll
body_pitch_rate
body_roll_rate
stance foot world/site y
base_y relative to stance foot y
```

If body roll or stance-foot-relative base position are not available cheaply,
the first implementation may use `base_y`, `local_vy`, and contact state as a
proxy. The limitation must be documented in the output artifact.

## Control Terms

Start with leg pitch-chain targets from the existing teacher, but move the
decision logic out of a fixed sinusoid.

### Lateral Load Shift

```text
desired_base_y = stance_side * lateral_offset
lateral_error = desired_base_y - base_y
lateral_velocity_error = -local_vy
roll_cmd = kp_y * lateral_error + kd_y * lateral_velocity_error
```

Gate:

```text
LOAD_STANCE complete when:
  abs(lateral_error) <= base_y_gate
  abs(local_vy) <= lateral_velocity_gate
  stance contact is true
  base_height >= min_base_height
```

### Swing Unweighting

```text
swing_lift = knee_lift + ankle_lift
```

Gate:

```text
UNWEIGHT_SWING complete when:
  swing foot contact false or swing foot z >= clearance_gate
  stance contact remains true
  pitch/height remain in gate
```

### Forward Push

```text
forward_error = command_x - local_vx
stance_push = clipped(kp_vx * forward_error + feedforward_push)
```

Gate:

```text
PUSH_FORWARD allowed only when:
  stance contact true
  abs(local_vy) <= lateral_velocity_gate
  abs(base_y - desired_base_y) <= base_y_gate
  body_pitch inside pitch gate
  base_height inside height gate
```

### Recovery

If pitch, height, or lateral velocity leaves gate:

```text
reduce forward push
increase pitch ankle correction
return to LOAD_STANCE or hold double support
```

Recovery is not a pass by itself. A target that survives by staying in recovery
without forward progress still fails the gate.

## Candidate Search

Do not start with a broad random grid. First run a small interpretable grid:

```text
lateral_offset: 0.01, 0.02, 0.03 m
base_y_gate: 0.01, 0.02, 0.03 m
lateral_velocity_gate: 0.06, 0.08, 0.10 m/s
kp_y / kd_y: 2-4 candidate pairs
kp_vx: 0.5, 1.0
feedforward_push: 0.005, 0.01 rad
swing_lift: 0.08, 0.12 rad
clearance_gate: measured from existing foot_site_z traces
phase timeout: 0.25-0.45 s
```

Run seeds `0,2` first. Expand only if the small grid shows a new tradeoff.

## Required Output

The first implementation should produce:

```text
outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_PROBE.md
outputs/analysis/com_weight_transfer_controller_probe.json
outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_PROBE_SCORE_100.md
outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_PROBE_SCORE_150.md
```

Raw JSONL traces should remain ignored.

The output must explicitly report:

```text
phase dwell percentages
phase transition counts
LOAD_STANCE success/fail counts
UNWEIGHT_SWING success/fail counts
PUSH_FORWARD allowed percentage
forward displacement
lateral p95
single/double support percentages
contact transitions
pitch/height gates
target velocity p95
tracking p95
```

## Gate

The same target-source gate applies:

```text
PASS_WEIGHT_TRANSFER_TARGET:
  seeds 0 and 2 both pass 100-150 tick windows with:
    mean_vx >= 0.04 m/s
    local forward displacement >= 0.04 m over 100 ticks
    local forward displacement >= 0.06 m over 150 ticks
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

## Stop Rules

Stop the branch and document the hold if:

```text
HOLD_LOAD_STANCE:
  controller cannot place base_y / local_vy inside gate while preserving height.

HOLD_UNWEIGHT_SWING:
  stance loads but swing foot cannot clear without pitch/height failure.

HOLD_PUSH_FORWARD:
  stance and swing gates pass, but forward push creates lateral velocity or
  pitch collapse.

HOLD_FORWARD_STILL_LOW:
  all gates are stable but forward displacement remains below target.

HOLD_ACTUATOR_ENVELOPE:
  the only passing candidates exceed sent target velocity or tracking gates.
```

Do not convert a hold into a training run. A hold should identify which state
transition failed.

## Non-Goals

```text
do not run robot tests
do not SSH or deploy
do not train PPO/BC
do not run grounded replay
do not change BEST_WALK_ONNX_2
do not relax the actuator envelope
do not treat single support alone as success
do not treat survival without forward displacement as success
```
