# Phase 2 z=0.0075 Iter21 PPO-Loc Swish Step-0 Decision

status: `HOLD_REJECT_PPO_STEP0_RESTORE_POINT`

Offline-only behavior-cloning, PPO step-0 export, and corrected-bridge smoke
screen. No robot tests, SSH, deploy, grounded replay, runtime behavior change,
or PPO update training was performed.

## Inputs

- source manifest: `outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_merged_manifest.json`
- corrected bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- BC NPZ: `outputs/analysis/phase2_z0075_iter21_ppo_loc_swish_rate150_candidate/candidate_mlp.npz`
- BC NPZ sha256: `152b02a756f4e2de9aebef17c02c89a6b6b4afb53cc2872c1ffc02a5973bc104`
- BC ONNX: `policy/candidates/phase2_z0075_iter21_ppo_loc_swish_rate150_20260704/candidate.onnx`
- BC ONNX sha256: `0986bc78f6b7b262e1b04177d7d728fb4c7ace25046bfcc5d9b2e3b8f9928f1e`
- PPO step-0 checkpoint: `outputs/analysis/phase2_z0075_iter21_ppo_loc_swish_rate150_step0_checkpoint`
- PPO step-0 ONNX: `policy/candidates/phase2_z0075_iter21_ppo_loc_swish_rate150_step0_20260704/candidate.onnx`
- PPO step-0 ONNX sha256: `7241c37b438e9267220a4f1296600a07ff21bd85e815176fa67d85cf5c68a41c`

## Fit And Export

- BC fit status: `PASS_PPO_LOC_BC_FIT_SMOKE`
- samples: `53130`
- weighted samples: `157111.6562`
- hidden sizes: `[512, 256, 128]`
- activation: `swish`
- BC p95 abs error: `0.031326`
- BC target-rate p95: `1.361154 rad/s`

PPO step-0 export fidelity passed:

- status: `PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY`
- checked samples: `512`
- p95 abs error: `0.00000012`
- max abs error: `0.00000030`

This proves the PPO parameter/checkpoint construction and ONNX export can
reproduce the deterministic swish PPO-loc BC policy.

## Closed-Loop Smoke

Smoke gate:

- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0075`
- command_x: `0.08`
- bridge_mode: `fitted`
- push: enabled
- push_interval_s: `1.0-1.5`
- push_magnitude: `0.075-0.125`
- reset_mode: `home-support`
- reset_settle_ticks: `10`
- seeds: `0,1,5`
- jax_platform: `cpu`

| seed | status | samples | termination | track_ratio | mean_vx | base_height_min | max_vel_excess |
|---:|---|---:|---|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 667 | `fall_or_nan` | -0.0042 | -0.0003 | 0.0653 | 0.0000 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3243 | 0.0259 | 0.1580 | 0.0000 |
| 5 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3450 | 0.0276 | 0.1580 | 0.0000 |

Distribution:

- pass: `2/3`
- fall/termination hold: `1/3`
- mean track_ratio: `0.2217`
- mean local vx: `0.0177 m/s`
- p95/max corrected velocity excess: `0.0000 / 0.0000 rad/s`

## Decision

Do not use `outputs/analysis/phase2_z0075_iter21_ppo_loc_swish_rate150_step0_checkpoint`
as the next Phase 2 DR/PPO restore point.

The step-0 export is numerically valid, but the closed-loop smoke shows that
the PPO-compatible compression changes the behavior enough to lose the gait on
seed 0. A valid export is not enough; Phase 2 continuation needs a behavior-safe
restore point.

next_recommendation: `preserve Iter21 as the current behavior anchor; investigate PPO-compatible compression or use a stronger continuity/teacher-action objective before any further DR training from this checkpoint`
