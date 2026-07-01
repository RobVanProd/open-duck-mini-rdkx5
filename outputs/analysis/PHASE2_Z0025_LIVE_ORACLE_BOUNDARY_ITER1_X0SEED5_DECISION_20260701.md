# Phase 2 z=0.0025 Iter1 x0 Seed-5 Recovery Decision

status: `HOLD_ITER1_X0SEED5_CORRECTION_INSUFFICIENT`

## Objective

Patch the rate1p9 candidate's only full-gate blocker: x=0.0 seed 5 reverse/collapse.
The correction used a live-oracle DAgger iteration with:

- x=0.08 preservation seeds: `0,3`
- x=0.0 correction seed: `5`
- x=0.0 teacher: `zero_action`
- base manifest: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0/live_oracle_dagger_aggregate_manifest.json`
- aggregate dataset: `17 entries / 12043 samples`

## Refit

- candidate: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter1_x0seed5_contactphase_rate1p9_bc_candidate/candidate.onnx`
- architecture: contact+phase modulated BC
- target-rate scale: `1.5`
- scalar target-rate limit: `1.9 rad/s`
- fit p95 abs error: `0.031287`
- fit max abs error: `0.841390`
- fit target-rate p95: `1.623082 rad/s`
- fit target-rate max: `2.956879 rad/s`

## Targeted Screen

command: `x=0.0`, seed: `5`, task: `rough_terrain_backlash`, terrain z-scale: `0.0025`

result: `HOLD_CANDIDATE_FALL_OR_TERMINATION`

- samples: `44`
- termination: `fall_or_nan`
- mean_local_vx: `-0.3620 m/s`
- base_height_min: `0.0441 m`
- max_tracking_p95: `0.2291 rad`
- p95 velocity excess: `0.0000 rad/s`
- max velocity excess: `0.0000 rad/s`

## Interpretation

The 43-sample x=0.0 seed-5 zero-action relabel was not enough to move the student out of
the seed-5 reverse/collapse basin. It also made the targeted seed slightly worse on base
height and tracking.

Do not full-gate or promote this iter1 student. The next attempt needs a stronger
zero-command mechanism than one short failed-trace relabel, while preserving the previous
rate1p9 x=0.08 8/8 pass.

No robot test, SSH, deploy, grounded replay, runtime behavior change, PPO training, or
policy deployment was performed.
