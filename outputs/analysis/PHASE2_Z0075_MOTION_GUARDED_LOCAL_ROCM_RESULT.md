# Phase 2 z=0.0075 Motion-Guarded Local ROCm Result

status: `HOLD_MOTION_GUARD_STILL_COLLAPSES`

This was an offline-only local ROCm training and CPU screening pass. It did not
SSH, deploy, touch the robot, run robot tests, or run grounded replay.

## Source Recipe

- recipe: `outputs/analysis/PHASE2_Z0075_MOTION_GUARDED_BEHAVIOR_PRIOR_RECIPE.md`
- previous_hold: `HOLD_BEHAVIOR_PRIOR_LOW_FORWARD_PROGRESS`
- intended_change: make safe standstill invalid during training by enabling
  command-progress failure and allowing the negative failure penalty through
  `--reward-clip-min -100.0`.

## Training Run

- output_dir: `outputs/phase2_domain_randomization/stage_z0075_motion_guarded_behavior_prior_local_rocm/smoke_20260704T191811Z_gpu`
- manifest: `outputs/phase2_domain_randomization/stage_z0075_motion_guarded_behavior_prior_local_rocm/smoke_20260704T191811Z_gpu/smoke_manifest.final.json`
- manifest_sha256: `4699620ed84da3813b858d90203d523acce47262c8ea36f3cf550b1c3db431ce`
- manifest_status: `PASS_SMOKE_RUN`
- elapsed_s: `570.0265405199898`
- platform: `gpu`
- local_rocm_safe_env: `true`
- command_progress_failure_enable: `true`
- command_progress_failure_min_ratio: `0.30`
- command_progress_failure_warmup_steps: `120`
- command_progress_failure_scale: `-10.0`
- reward_clip_min: `-100.0`

Training reward lines:

| step | reward | reward_std |
|---:|---:|---:|
| 0 | 46.7202 | 62.9184 |
| 40960 | 67.4251 | 85.7493 |
| 81920 | 58.9838 | 77.0155 |
| 122880 | 62.0405 | 76.7619 |

Exported ONNX files:

| step | ONNX | sha256 |
|---:|---|---|
| 40960 | `outputs/phase2_domain_randomization/stage_z0075_motion_guarded_behavior_prior_local_rocm/smoke_20260704T191811Z_gpu/2026_07_04_152300_40960.onnx` | `2f40ec66244e2f837952b583735a6e872ad2f85eee40ab4ca7d4eda2da87da04` |
| 81920 | `outputs/phase2_domain_randomization/stage_z0075_motion_guarded_behavior_prior_local_rocm/smoke_20260704T191811Z_gpu/2026_07_04_152547_81920.onnx` | `c553b34229c4ad538ba9b8f325f4216fe5ca5c290b02ec273dd4e7176dca0157` |
| 122880 | `outputs/phase2_domain_randomization/stage_z0075_motion_guarded_behavior_prior_local_rocm/smoke_20260704T191811Z_gpu/2026_07_04_152655_122880.onnx` | `e7de169d1a70c9b1a404868aa92cb03995977ef534a5c93330d60a857099e263` |

## Seed-0 Motion Screen

Screen artifact:

- markdown: `outputs/analysis/PHASE2_Z0075_MOTION_GUARDED_SEED0_SCREEN.md`
- json: `outputs/analysis/phase2_z0075_motion_guarded_seed0_screen.json`
- json_sha256: `8f48b3066b1ddffbc38368769acafb11e9db577552b7939f28cb3ada0ac96e85`

Screen settings:

- command_x: `0.08`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0075`
- bridge_mode: `fitted`
- corrected_bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- jax_platform: `cpu`
- seed: `0`
- duration_s: `15.0`
- reset_mode: `home-support`
- reset_settle_ticks: `10`
- push: disabled

| checkpoint | status | samples | mean vx m/s | track ratio | max pitch vel p95 rad/s | max vel excess | max tracking p95 rad | single support % | double support % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| step40960 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.0022 | 0.0276 | 0.1858 | 0.0000 | 0.0475 | 0.0 | 100.0 |
| step81920 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.0023 | 0.0286 | 0.1580 | 0.0000 | 0.0489 | 0.0 | 100.0 |
| step122880 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 750 | 0.0023 | 0.0289 | 0.1381 | 0.0000 | 0.0472 | 0.0 | 100.0 |

## Interpretation

The motion guard made no meaningful improvement over the previous behavior-prior
run. All exported checkpoints are stable and in-envelope, but they remain
near-stationary and never enter single support in the seed-0 x=0.08 screen.

This falsifies the local recipe branch:

`old PPO restore checkpoint + behavior-prior reward + command-progress failure`

as a sufficient Phase 2 refinement method. It still optimizes into the same
safe standstill basin. The next Phase 2 recipe should not tune this same path.

## Next Constraint

Do not promote these checkpoints and do not run robot validation.

The next offline attempt should preserve the moving Iter21 policy more directly
than a soft behavior-prior reward against an older PPO restore point. Concrete
options to evaluate next:

1. start PPO from a checkpoint that is already fidelity-matched to the moving
   Iter21 policy, if such a checkpoint can be produced;
2. run live-oracle / DAgger-style relabeling on student-visited states and then
   fine-tune from that deployable student;
3. treat the current result as another data point that scalar PPO rewards are
   not enough to keep the gait out of double-support standstill.

The current Phase 2 goal remains active and incomplete.
