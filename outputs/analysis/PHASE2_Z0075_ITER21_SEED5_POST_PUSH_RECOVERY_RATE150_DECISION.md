# Phase 2 z0.0075 Iter21 Seed5 Post-Push Recovery Rate150 Decision

status: `HOLD_SEED5_RECOVERY_TRANSFERRED_BUT_OTHER_SEEDS_REGRESSED`

Offline-only analysis, relabeling, supervised fitting, and sim screening. No
robot tests, SSH, deploy, grounded replay, runtime behavior changes, or PPO
training were performed.

## Inputs

- base_manifest: `outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_merged_manifest.json`
- recovery_snippet_manifest: `outputs/analysis/phase2_z0075_iter21_seed5_late_push_recovery_relabel_manifest.json`
- merged_manifest: `outputs/analysis/phase2_z0075_iter21_seed5_post_push_recovery_merged_manifest.json`
- merged_manifest_sha256: `c97c873d2c99401d3d5004cabb37923359161158bd93ca68f9d5ef09d8ebf383`
- candidate: `policy/candidates/phase2_z0075_iter21_seed5_post_push_recovery_rate150_20260704/candidate.onnx`
- candidate_sha256: `e4ea65621cc641e00fafdf6b78d94fd730c22188e8b8ce3ed8f0a7f668d7592b`
- student_npz: `outputs/analysis/phase2_z0075_iter21_seed5_post_push_recovery_rate150_student/candidate_mlp.npz`
- student_npz_sha256: `9363f242d84235f9418d0cec0a5b27321bdd9d7d5f73fd86c28897aaf70675ae`
- corrected_bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`

## Recovery Data

The seed5 late post-push failure was extracted from the Iter21 reset-settle10
full-observation trace and relabeled with the same source-VX oracle used for
the prior seed0 recovery path:

- teacher_manifest: `outputs/analysis/phase2_z0075_intermediate_push_live_oracle_iter3_seed0_recovery_run/live_oracle_dagger_aggregate_manifest.json`
- teacher_model_kind: `source_vx_blend`
- blend_alpha: `0.8`
- vx/source-vx threshold: `0.02 m/s`
- alt model: excludes `seed_004`
- snippets: `1`
- samples: `79`
- relabel action_delta_p50/p95/max: `0.0204 / 0.0869 / 0.3296`
- sample_weight_p50/p95/max: `8.0 / 8.0 / 8.0`

The relabeled rows mostly cover reverse/low-progress double-support drift after
the late push, not startup.

## Fit

Phase-modulated BC fit:

- samples: `53209`
- context indices: `[6, 97, 98, 99, 100]`
- trunk/context hidden sizes: `[512, 256]` / `[64]`
- target_rate_scale: `0.1`
- target_rate_limit_rad_s: `1.5`
- fit MAE: `0.013113`
- fit p95 abs error: `0.039310`
- fit target-rate p95: `1.342554 rad/s`
- fit target-rate max: `7.594885 rad/s`
- ONNX p95/max verification error: `0.00000018 / 0.00000036`

The fit-level max target rate is high, so closed-loop screening is authoritative.

## Focused Seed0/Seed5 Screen

The targeted screen passed both the previously stable seed0 and the previously
failing seed5:

| seed | status | samples | track_ratio | max_vel_excess | push_success |
|---:|---|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.4129 | 0.0000 | 0.9167 |
| 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.4644 | 0.0000 | 0.9231 |

This confirms the seed5 recovery signal transferred locally.

## Full x=0.08 Rough/Intermediate-Push Gate

Gate settings:

- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0075`
- command_x: `0.08`
- bridge: fitted corrected bridge
- reset_mode: `home-support`
- reset_settle_ticks: `10`
- pushes: enabled, interval `1.0-1.5s`, magnitude `0.075-0.125`

| seed | status | samples | track_ratio | max_vel_excess | base_height_min | push_success |
|---:|---|---:|---:|---:|---:|---:|
| 0 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.4129 | 0.0000 | 0.1595 | 0.9167 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.4093 | 0.0000 | 0.1587 | 0.9231 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 455 | 0.8843 | 0.0000 | -0.0068 | 0.8571 |
| 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 491 | -0.0747 | 0.0000 | 0.0725 | 0.7778 |
| 4 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.3418 | 0.0000 | 0.1597 | 0.9167 |
| 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.4644 | 0.0000 | 0.1581 | 0.9231 |
| 6 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 180 | 1.5672 | 0.0000 | 0.0043 | 0.3333 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.4170 | 0.0000 | 0.1592 | 0.9000 |

Distribution:

- pass: `5/8`
- falls/terminations: `3/8`
- p95/max corrected-envelope velocity excess: `0.0000 / 0.0000`
- mean track_ratio: `0.5528`
- mean local vx: `0.0442 m/s`

## Decision

`HOLD_SEED5_RECOVERY_TRANSFERRED_BUT_OTHER_SEEDS_REGRESSED`

Do not promote this candidate. Do not run robot validation.

The single seed5 post-push recovery snippet successfully fixes seed5 and clears
the remaining target-velocity excess, but it also moves the policy off the
stable manifold for seeds `2`, `3`, and `6`.

The next offline branch should not add a stronger version of this same snippet
or apply global smoothing. It should collect matched failure-state coverage for
the newly regressed seeds and train a balanced recovery set, or use a
state-conditioned recovery model that can distinguish seed5 late post-push
collapse from the seed2/3/6 stable-recovery states.

x=0.0 was not run for this candidate because the x=0.08 promotion gate already
failed.

The Phase 2 goal remains active and incomplete.
