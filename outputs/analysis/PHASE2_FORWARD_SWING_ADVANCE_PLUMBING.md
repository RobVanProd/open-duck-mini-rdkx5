# Phase 2 Forward Swing-Advance Plumbing

status: `PASS_FORWARD_SWING_ADVANCE_PLUMBING`

## Purpose

The C7/C8 terrain diagnostics show a carpet-relevant failure where one foot can
remain effectively planted: low or zero swing segments, zero relative-x swing
excursion, and near-total double support. Existing hooks can price clearance,
contact transitions, double-support dwell, and left/right swing balance, but no
training reward directly priced whether the swing foot advanced forward relative
to the body during swing.

This change adds a default-off `forward_swing_advance` hook for the next
offline terrain branch.

## Implementation

Playground:

```text
playground/common/rewards.py
playground/open_duck_mini_v2/joystick.py
playground/open_duck_mini_v2/runner.py
```

RDK wrapper/planner:

```text
tools/run_actuator_bridge_training_smoke.py
tools/plan_staged_curriculum_training.py
```

New runner controls:

```text
--forward_swing_advance_scale
--forward_swing_advance_target_m
--forward_swing_advance_huber_delta
```

New RDK wrapper controls:

```text
--forward-swing-advance-scale
--forward-swing-advance-target-m
--forward-swing-advance-huber-delta
```

The hook tracks each foot's forward position in the body/IMU frame at stance,
then tracks the peak commanded-direction advance while the foot is in swing. On
touchdown, it penalizes shortfall below `forward_swing_advance_target_m` when a
forward command is active.

Default scale is `0.0`, so existing runs are unchanged.

## Smoke

Tiny CPU smoke:

```text
output:
  outputs/analysis/forward_swing_advance_plumbing_smoke/smoke_20260628T152500Z_cpu

status:
  PASS_SMOKE_RUN

task:
  rough_terrain_backlash

terrain_hfield_z_scale:
  0.002

restore checkpoint:
  outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint

forward_swing_advance_scale:
  -0.001

forward_swing_advance_target_m:
  0.005

forward_swing_advance_huber_delta:
  0.002

terrain XML restored:
  true
```

This is a plumbing smoke only. It is not a candidate and does not approve robot
validation.

## Next Use

The next C-stage terrain branch should test this hook as a direct step-advance
pressure, preferably with gate-selected checkpointing and the hard terrain swing
gate enabled. It should not be interpreted as another global scalar fix: if the
policy again retreats into double support or low progress, the next target needs
a higher-clearance alternating-step demonstration or a hard step-advance
constraint rather than stronger scalar pressure.
