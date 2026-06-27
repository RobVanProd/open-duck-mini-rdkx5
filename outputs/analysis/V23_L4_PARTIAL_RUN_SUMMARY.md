# V23 L4 Partial Run Summary

status: `HOLD_V23_SUPPORT_OBJECTIVE_FAILED_GATE`

This is an offline Colab/L4 training result. It does not authorize robot tests,
SSH, deployment, grounded replay, runtime changes, or policy promotion.

## Run

```text
workflow: staged-curriculum
recipe: movement_bootstrap_v23
session: open-duck-l4
run_dir: outputs/analysis/colab_cli/open-duck-l4-staged-curriculum-20260625T143703Z
remote status: HOLD_REMOTE_NO_SENTINEL
```

V23 trained the explicit support-contact objective:

```text
forward_single_support_scale: 1.0
forward_double_support_scale: -1.0
forward_contact_support_scale: -0.06
command_x: 0.035-0.045
actuator bridge: disabled
soft prior: disabled
robot_touched: false
```

## Training Evidence

The remote log reports the training phase completed:

```text
training status: PASS_SMOKE_RUN
checkpoint steps: 61440, 122880, 184320
final ONNX: 2026_06_25_145051_184320.onnx
```

Training reward snapshots:

```text
step 0:      -393.6161
step 61440: -473.6470
step 122880:-464.5394
step 184320:-493.6155
```

## Gate Evidence

The x=0.04 vanilla multi-seed gate started with seeds `0-7`.

Observed before the Colab session disappeared:

```text
seed 0: HOLD_CANDIDATE_FALL_OR_TERMINATION
seed 1: HOLD_CANDIDATE_FALL_OR_TERMINATION
seed 2: HOLD_CANDIDATE_FALL_OR_TERMINATION
seed 3: HOLD_CANDIDATE_FALL_OR_TERMINATION
seed 4: HOLD_CANDIDATE_FALL_OR_TERMINATION
seed 5: HOLD_CANDIDATE_FALL_OR_TERMINATION
seed 6: started, no final status captured
seed 7: not started
```

The full seed distribution is incomplete, but the gate failure is already
decisive because the configured pass condition allowed no failed seeds:

```text
phase_gate_max_fall_fraction: 0.0
```

## Interpretation

V23 did not solve the weight-transfer blocker. Adding explicit single-support
reward and double-support dwell cost was sufficient to run training and export a
candidate, but not sufficient to produce a stable x=0.04 forward policy in the
first six gate seeds.

This result should not be read as a clean eight-seed distribution because the
runtime disappeared during seed 6. It should be read as:

```text
explicit support-contact reward alone failed the required gate
```

## Next Direction

Do not repeat V23 unchanged.

The next branch should test a more structural support/propulsion mechanism:

```text
1. contact-aware curriculum with commanded weight-shift state, or
2. closed-loop teacher/controller that reacts to base height, pitch, lateral
   velocity, and contact state, or
3. a richer horizon optimizer that includes foot placement and stance-side
   propulsion instead of only reward shaping.
```

Before another long cloud run, add a cheap trace/eval tool that reports why the
V23 candidate fell on seed 0:

```text
contact sequence
base height
body pitch / pitch rate
local vx / vy
single-support dwell
double-support dwell
termination tick and reason
```
