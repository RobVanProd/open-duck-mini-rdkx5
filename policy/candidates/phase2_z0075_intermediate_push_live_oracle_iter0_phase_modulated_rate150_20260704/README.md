# Phase 2 z=0.0075 Intermediate-Push Live-Oracle Iter0 Phase-Modulated Rate150 Candidate

status: `HOLD_TARGET_VELOCITY_SPIKES_SLOW_PROGRESS`

This is an offline phase/command-modulated BC student fit from the curated
z=0.0075 intermediate-push live-oracle DAgger iter0 aggregate. It is not a
grounded-test authorization.

Contract:

`obs[1,101] -> continuous_actions[1,14]`

## Files

- `candidate.onnx`
  - sha256: `2c56a55ca9757511f2987eaf1dcb145e5f0b1c7e8f85f884a6fd6e36d1636067`
- `student.npz`
  - sha256: `b2e2bb9d796d367167b8c0167b12f859bfd485a451f763fc26e91731b7fb2d30`

## Fit

- manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter0_curated/live_oracle_dagger_curated_aggregate_manifest.json`
- dataset_id: `88de24bcd82435ee`
- samples: `42501`
- action MAE: `0.011686`
- action p95 abs error: `0.037589`
- action max abs error: `1.275810`
- target-rate p95: `1.307327 rad/s`
- target-rate max: `3.626033 rad/s`
- ONNX verify max abs error: `0.00000021`

## z=0.0075 Intermediate-Push Screen

Both screens used `rough_terrain_backlash`, corrected-knee fitted bridge, CPU,
15s duration, hfield z scale `0.0075`, push interval `1.0-1.5 s`, and push
magnitude `0.075-0.125`.

| command | seeds | falls | mean vx | track ratio | max p95 excess | max instantaneous excess | max tracking p95 | push success |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `x=0.08` | 2 | 0 | 0.0248 | 0.3096 | 0.0000 | 2.6095 | 0.1856 | 0.9083 |
| `x=0.0` | 2 | 0 | -0.0005 | NA | 0.0000 | 3.0346 | 0.0472 | 0.9199 |

## Decision

This fit is a useful stability improvement over the raw parent under the same
z=0.0075 intermediate-push condition: seed 7 no longer falls at `x=0.08`, and
seed 0 no longer collapses at `x=0.0`. It is still not promotable because the
strict gate sees instantaneous target-velocity excess and `x=0.08` progress is
slow.

Next step: keep the curated live-oracle path, but reduce instantaneous spike
events without returning to scalar PPO reward tuning.
