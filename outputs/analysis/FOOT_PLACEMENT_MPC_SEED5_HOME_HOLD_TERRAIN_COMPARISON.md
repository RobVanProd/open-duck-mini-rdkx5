# Foot-Placement MPC Seed-5 Home-Hold Terrain Comparison

status: `HOLD_HOME_HOLD_NOT_A_VALID_TERRAIN_SOURCE`

This is an offline source diagnostic. It did not train, SSH, deploy, run robot
tests, grounded replay, or change runtime behavior.

## Purpose

After the z=0.005 seed-5 support hold, the same default/home-target source was
run at `terrain_hfield_z_scale=0.002` to check whether the z=0.005 terrain
height alone caused the collapse.

## Comparison

| terrain z scale | samples | termination | mean vx | body pitch abs p95 | base height min |
|---:|---:|---|---:|---:|---:|
| `0.002` | 43 | `fall_or_nan` | `-0.3643` | `1.3811` | `0.0475` |
| `0.005` | 43 | `fall_or_nan` | `-0.3736` | `1.4007` | `0.0415` |

Initial reset state was effectively identical in both traces:

| terrain z scale | base xyz | pitch | contacts | foot z |
|---:|---|---:|---|---|
| `0.002` | `[-0.0418, -0.0280, 0.1500]` | `-0.0071` | `[0, 0]` | `[0.0235, 0.0554]` |
| `0.005` | `[-0.0418, -0.0280, 0.1500]` | `-0.0071` | `[0, 0]` | `[0.0235, 0.0554]` |

## Interpretation

The default/home target is not a valid rough-terrain support source. It falls on
seed 5 at both z=0.002 and z=0.005 with nearly the same backward/base-height
collapse. This does not contradict the Phase A2 candidate passing z=0.002; it
means Phase A2 survives because of its learned closed-loop behavior, not because
the nominal home target is stable.

## Decision

Do not use home-hold/default-target traces as positive source data for z=0.005.
The next source attempt should be policy-derived or reset/support-pose-derived,
not another nominal-home scripted source.
