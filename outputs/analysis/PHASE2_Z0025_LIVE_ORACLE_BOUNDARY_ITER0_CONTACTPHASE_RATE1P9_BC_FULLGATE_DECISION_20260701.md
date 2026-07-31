# Phase 2 z=0.0025 Rate1p9 Full Gate Decision

status: `HOLD_RATE1P9_ZERO_COMMAND_SEED5`

## Candidate

- policy: `outputs/analysis/phase2_z0025_live_oracle_boundary_iter0_contactphase_rate1p9_bc_candidate/candidate.onnx`
- policy_sha256: `f00ba8a89f4e24e7c393309acd434cbc95132473aa3df562dacf4fe527049822`
- weights_sha256: `713c58e1600d6da4e7519c61e50ff0870166da88415b645cfd78c7436e188aeb`
- bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0025`
- bridge_mode: `fitted`
- duration: `15s`
- seeds: `0-7`

## x=0.08 Full Gate

result: `PASS_X008_FULL_GATE`

- runs: `8`
- falls: `0`
- duration_complete: `8`
- track_ratio_mean: `0.3742`
- mean_local_vx_mean: `0.0299 m/s`
- body_pitch_p95_mean: `0.1153 rad`
- base_height_min_mean: `0.1526 m`
- max_pitch_vel_p95_mean: `1.9160 rad/s`
- p95_velocity_excess_mean: `0.0000 rad/s`
- max_velocity_excess_mean: `0.0000 rad/s`
- max_tracking_p95_mean: `0.1937 rad`
- single_support_mean: `21.37%`
- double_support_mean: `78.58%`

## x=0.0 Full Gate

result: `HOLD_X0_SEED5_FALL_OR_TERMINATION`

- runs: `8`
- falls: `1`
- duration_complete: `7`
- passing seeds: `0, 1, 2, 3, 4, 6, 7`
- failing seed: `5`
- x=0.0 aggregate mean vx: `-0.0438 m/s`
- x=0.0 p95_velocity_excess_mean: `0.0000 rad/s`
- x=0.0 max_velocity_excess_mean: `0.0000 rad/s`

### Seed 5 Failure

- status: `HOLD_CANDIDATE_FALL_OR_TERMINATION`
- samples: `43`
- termination: `fall_or_nan`
- mean_local_vx: `-0.3468 m/s`
- base_height_min: `0.0575 m`
- max_tracking_p95: `0.2106 rad`
- max_pitch_vel_p95: `0.5823 rad/s`
- velocity_excess: `0.0000 rad/s`

## Interpretation

The rate1p9 contact+phase student is the strongest boundary candidate so far on the
z=0.0025 rough-terrain corrected-bridge gate: it passes x=0.08 across all eight seeds
with zero corrected-envelope excess and tracking just below the 0.20 rad threshold.

It is not promotable because command-conditioning is not seed-robust. At x=0.0, seed 5
falls or terminates after 43 samples with a strong reverse velocity and low base height.
The next fix should target zero-command seed-5 stability while preserving the x=0.08
in-envelope pass. This is not evidence to relax the corrected bridge envelope.

No robot test, SSH, deploy, grounded replay, or runtime behavior change was performed.
