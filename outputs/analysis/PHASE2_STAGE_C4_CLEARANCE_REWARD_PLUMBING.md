# Phase 2 Stage C4 Clearance Reward Plumbing

status: `PASS_CLEARANCE_REWARD_PLUMBING`

## Scope

Offline sim/training plumbing only. No robot, SSH, deploy, grounded replay, or
runtime behavior change was performed.

## Why

Stage C terrain screens and the carpet hardware observation point at the same
failure mode: the current corrected-bridge candidate is actuator-trackable and
steps, but it is a low-clearance shuffle. Stage C3 contact timing moved support
timing slightly but did not raise swing height enough to clear the strict
terrain gate.

## Change

The Playground training environment now has a default-off forward
swing-clearance cost:

```text
term:
  forward_swing_clearance

measurement:
  per-foot swing peak lift above that foot's last stance height

active only when:
  abs(command_x) > forward_progress_deadband

cost event:
  touchdown after a swing whose peak lift is below target

default scale:
  0.0
```

New Playground runner flags:

```text
--forward_swing_clearance_scale
--forward_swing_clearance_target_m
--forward_swing_clearance_huber_delta
```

The RDK training wrapper and reward-override evaluator map the same settings
through:

```text
--forward-swing-clearance-scale
--forward-swing-clearance-target-m
--forward-swing-clearance-huber-delta
```

## Validation

Python compile checks passed for the touched RDK and Playground files.

Tiny CPU training plumbing smoke:

```text
output:
  outputs/analysis/clearance_reward_plumbing_smoke/smoke_20260628T123616Z_cpu

status:
  PASS_SMOKE_RUN

elapsed_s:
  111.81

command excerpt:
  --task rough_terrain_backlash
  --terrain-hfield-z-scale 0.002
  --num-timesteps 128
  --ppo-num-envs 16
  --forward-swing-clearance-scale -0.05
  --forward-swing-clearance-target-m 0.03
  --forward-swing-clearance-huber-delta 0.01
```

Direct one-step env activation check:

```text
has_metric: true
metric: cost/forward_swing_clearance
diagnostic: diagnostic/swing_peak_lift
```

The smoke is not a candidate and should not be promoted.

## Next

Run a C4 terrain fine-tune from the best C2/C3 lineage with a mild clearance
cost, corrected fitted bridge active, and the same strict `z=0.002` terrain
screen. The target is to raise swing peak without breaking corrected-envelope
compliance, `x=0.0` stillness, or flat-ground command conditioning.
