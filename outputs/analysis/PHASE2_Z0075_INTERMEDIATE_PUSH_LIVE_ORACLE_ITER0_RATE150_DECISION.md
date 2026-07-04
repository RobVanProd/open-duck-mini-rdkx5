# Phase 2 z=0.0075 Intermediate-Push Live-Oracle Iter0 Rate150 Decision

status: `HOLD_TARGET_VELOCITY_SPIKES_SLOW_PROGRESS`

## Scope

- Offline BC fit and sim screening only.
- No robot tests, SSH, deploy, grounded replay, PPO training, or runtime behavior changes were performed.

## Candidate

- policy: `policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter0_phase_modulated_rate150_20260704/candidate.onnx`
- policy_sha256: `2c56a55ca9757511f2987eaf1dcb145e5f0b1c7e8f85f884a6fd6e36d1636067`
- student_npz_sha256: `b2e2bb9d796d367167b8c0167b12f859bfd485a451f763fc26e91731b7fb2d30`
- fit_report: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter0_student_rate150/PHASE_MODULATED_BC_STUDENT.md`
- curated_manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter0_curated/live_oracle_dagger_curated_aggregate_manifest.json`
- curated_dataset_id: `88de24bcd82435ee`

## Fit Metrics

- samples: `42501`
- action_mae: `0.011686`
- action_p95_abs_error: `0.037589`
- action_max_abs_error: `1.275810`
- target_rate_p95_rad_s: `1.307327`
- target_rate_max_rad_s: `3.626033`
- onnx_verify_max_abs_error: `0.00000021`

## Screens

Both screens used `rough_terrain_backlash`, corrected-knee fitted actuator
bridge, CPU evaluator, 15s duration, hfield z scale `0.0075`, push interval
`1.0-1.5 s`, and push magnitude `0.075-0.125`.

| command | seed | status | samples | termination | mean vx | track ratio | pitch p95 | height min | max p95 excess | max instantaneous excess | tracking p95 | push success |
|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `x=0.08` | 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0223 | 0.2793 | 0.1819 | 0.1527 | 0.0000 | 0.0000 | 0.1856 | 0.9167 |
| `x=0.08` | 7 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | 0.0272 | 0.3399 | 0.1496 | 0.1568 | 0.0000 | 2.6095 | 0.1779 | 0.9000 |
| `x=0.0` | 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | -0.0004 | NA | 0.0061 | 0.1528 | 0.0000 | 0.7594 | 0.0344 | 0.9167 |
| `x=0.0` | 1 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | `duration_complete` | -0.0005 | NA | 0.0662 | 0.1568 | 0.0000 | 3.0346 | 0.0472 | 0.9231 |

## Decision

The curated live-oracle iter0 fit is an improvement over the previous parent
on the targeted z=0.0075 intermediate-push failure states:

- `x=0.08 seed 7` no longer falls.
- `x=0.0 seed 0` no longer collapses or runs backward.
- command semantics are preserved at `x=0.0`.

It is not promotable because strict target-velocity max spikes remain, and
forward progress is slow at `x=0.08` (`track_ratio_mean=0.3096`). Do not run
robot validation from this candidate.

## Next Step

Continue from the curated live-oracle dataset, but address instantaneous spike
events before wider gates. The next offline move should be a spike-aware
curation/refit or live-oracle iteration, not scalar PPO reward tuning.
