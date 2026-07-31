# Foot-Placement MPC z=0.005 Seed-5 Support Decision

status: `HOLD_Z005_SEED5_SUPPORT_NOT_SOLVED`

This is an offline source-generation diagnostic. It did not train, SSH, deploy,
run robot tests, grounded replay, or change runtime behavior.

## Purpose

The z=0.005 source-rebuild branch is blocked by seed 5 collapsing before a
useful source window exists. Before trying another student fit, two small
support-only probes tested whether seed 5 can be held upright on
`rough_terrain_backlash` with `terrain_hfield_z_scale=0.005`.

## Inputs

- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.005`
- seed: `5`
- duration target: `2.0s`
- JAX platform: `cpu`
- robot/runtime: not touched

## Probes

### Default/Home Hold

Report:

```text
outputs/analysis/FOOT_PLACEMENT_MPC_Z005_SEED5_HOME_HOLD.md
```

Result:

| metric | value |
|---|---:|
| samples | 43 |
| termination | `fall_or_nan` |
| mean vx | `-0.3736 m/s` |
| body pitch abs p95 | `1.4007 rad` |
| base height min | `0.0415 m` |

The default/home target does not survive seed 5 on z=0.005, even at
`command_x=0.0`.

### Pitch/Roll/Yaw Support Grid

Report:

```text
outputs/analysis/FOOT_PLACEMENT_MPC_Z005_SEED5_SUPPORT_GRID.md
```

Result:

| metric | best value |
|---|---:|
| candidates | 24 |
| samples | 44 |
| termination | `fall_or_nan` |
| mean vx | `-0.3424 m/s` |
| body pitch abs p95 | `1.3138 rad` |
| base height min | `0.0613 m` |

Small stance feedback over roll, lateral velocity, body-y, yaw, and pitch did
not produce a 2-second seed-5 support source.

## Decision

Do not use these traces as source data. Do not run live-oracle DAgger iteration
1 from this source. Do not spend more compute fitting students to the current
z=0.005 source aggregate.

The z=0.005 seed-5 issue is now a support/reset-source design problem:

- seed 5 collapses without forward command,
- a default/home target is not stable on this terrain sample,
- simple joint-space stance feedback is not enough,
- the failure remains backward/base-height dominated.

## Next

The next offline step should change the source/reset problem before returning
to distillation:

1. inspect seed-5 terrain contact geometry at reset and compare z=0.002 vs
   z=0.005;
2. identify whether the initial feet are on a local bump/edge or starting with
   poor support/contact;
3. test a reset/support pose or terrain curriculum rung that first holds seed 5
   upright for `>=2s` without envelope excess;
4. only then reintroduce walking/source motion and the 8-seed source gate.

Until a z=0.005 seed-5 support source exists, the active Phase 2 blocker remains
`PLAN_Z005_SOURCE_REBUILD_REQUIRED`.
