# Phase 2 Terrain Live-Oracle DAgger Decision

status: `HOLD_TERRAIN_LIVE_ORACLE_DAGGER_TRACKING_PLATEAU`

## Scope

- offline only: no robot, SSH, deploy, grounded replay, runtime change, or training from scratch
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.002`
- seeds: `2,4`
- teacher_manifest: `outputs/analysis/phase2_terrain_safe_hard_step_bc_manifest.json`

## Iteration Summary

| iter | run_status | fit_status | gate result | seed2 vx/ratio/excess/track | seed4 vx/ratio/excess/track | interpretation |
|---:|---|---|---|---|---|---|
| 0 | `PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY` | `PASS_PPO_LOC_BC_FIT_SMOKE` | `HOLD_LOW_PROGRESS` | 0.0033 / 0.0408 / 0.0000 / 0.0907 | 0.0178 / 0.2220 / 0.8751 / 0.2498 | in-envelope freeze on seed 2; seed 4 still over tracking/envelope |
| 1 | `PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY` | `PASS_PPO_LOC_BC_FIT_SMOKE` | `HOLD_TRACKING` | 0.0397 / 0.4968 / 1.1270 / 0.2399 | 0.0459 / 0.5737 / 0.9312 / 0.2411 | progress recovered, but above corrected tracking/envelope |
| 2 | `PASS_LIVE_ORACLE_DAGGER_ITERATION_DATA_READY` | `PASS_PPO_LOC_BC_FIT_SMOKE` | `HOLD_TRACKING` | 0.0526 / 0.6570 / 0.8704 / 0.2533 | 0.0459 / 0.5736 / 0.8938 / 0.2527 | stronger progress, same tracking/envelope plateau |

## Decision

- `PASS_TERRAIN_WINDOW_SOURCE` remains valid: terrain-safe hard-step source windows exist.
- Plain 400-sample BC froze; recurrent small-data BC fell; live-oracle DAgger iterations recovered forward progress.
- The current live-oracle BC path plateaus above the corrected tracking/envelope gate: max pitch velocity excess remains about `0.87-1.13 rad/s`, tracking p95 about `0.24-0.25 rad`.
- Do not promote any iter0-2 student to robot or grounded testing.
- Next offline branch should make the relabel/training target tracking-aware: filter or rate-limit oracle labels, or move to PPO fine-tuning with explicit corrected-envelope penalties.
