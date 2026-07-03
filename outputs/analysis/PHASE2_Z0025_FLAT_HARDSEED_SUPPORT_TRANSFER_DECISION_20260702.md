# Phase 2 z=0.0025 Flat Hard-Seed Support Transfer Decision

status: `HOLD_FLAT_HARDSEED_SUPPORT_DOES_NOT_TRANSFER`

## Summary

The older flat-terrain hard-seed zero-command recovery candidate does not
transfer to the current rough-terrain `z=0.0025` unsupported seed-5 reset
pocket.

This was tested offline only with the corrected knee actuator bridge. No robot
test, SSH, deploy, grounded replay, training, or runtime behavior change was
performed.

## Inputs

- candidate: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_candidate/candidate.onnx`
- candidate_sha256: `dde8d20b464ad1e748cb620ce45fd0651d8e36a3ad35ba553aa64eed5229dd6d`
- bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- bridge_sha256: `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0025`
- bridge_mode: `fitted`
- jax_platform: `cpu`
- command_x: `0.0`
- seed: `5`
- duration_s: `2.0`

## Result

Source artifact:

- `outputs/analysis/PHASE2_Z0025_FLAT_HARDSEED_SUPPORT_TRANSFER_X0_SEED5.md`
- `outputs/analysis/phase2_z0025_flat_hardseed_support_transfer_x0_seed5.json`

Seed-5 result:

- status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
- samples: `59`
- termination: `fall_or_nan`
- mean_local_vx_m_s: `-0.2490`
- base_height_min_m: `0.0647`
- body_pitch_p95_rad: `0.0704`
- max_pitch_vel_p95_rad_s: `1.5783`
- max_pitch_vel_limit_excess_rad_s: `0.0000`
- max_tracking_p95_rad: `0.2098`
- single_support_pct: `6.7797`
- double_support_pct: `88.1356`

## Decision

Do not use the older flat-terrain hard-seed recovery candidate as the support
source for the current rough `z=0.0025` seed-5 repair.

The candidate remains in-envelope during the short failed rollout, but it does
not stabilize the unsupported/partial-contact reset pocket. The next repair
still needs a zero-command support source or teacher that is generated in the
current rough-terrain corrected-bridge reset distribution rather than imported
from the older flat-terrain branch.

Because the required `x=0.0` support-transfer gate failed, the matching
`x=0.08` transfer comparison was not run.
