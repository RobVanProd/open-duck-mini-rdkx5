# Phase 2 B0D GPU Recovery Smoke Decision

status: `PASS_GPU_RECOVERY_SMOKE`

## Purpose

Check whether the local ROCm backend can execute the B0D rough-terrain,
corrected-bridge PPO path after the workstation firmware/reset work.

This was intentionally tiny. It was not Phase 2 training and it does not
produce a candidate policy.

## Input

- restore checkpoint:
  `outputs/phase2_domain_randomization/stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/smoke_20260629T062042Z_gpu/2026_06_29_022725_245760`
- platform: `gpu`
- JAX platform: `rocm`
- timesteps: `64`
- envs: `8`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.002`
- corrected actuator bridge enabled
- actuator tracking scale: `-0.04`
- actuator tracking Huber delta: `0.03`
- restore-policy KL: `1.0`
- behavior prior enabled, scale `-0.35`

## Result

Output:

`outputs/phase2_domain_randomization/stage_b0d_gpu_recovery_smoke/smoke_20260629T074910Z_gpu`

Summary artifacts:

- `outputs/analysis/PHASE2_B0D_GPU_RECOVERY_SMOKE_SUMMARY.md`
- `outputs/analysis/phase2_b0d_gpu_recovery_smoke_summary.json`

Observed:

- status: `PASS_SMOKE_RUN`
- return code: `0`
- elapsed: `189.48 s`
- PPO step line: `STEP: 160 reward: 45.06843185424805 reward_std: 38.61678695678711`
- checkpoint produced at step `160`
- terrain override restored to original hash
- robot_touched: `false`

## Interpretation

The local ROCm path is no longer failing at startup for a tiny B0D-shaped PPO
run. This supersedes the earlier startup-only `HOLD_ROCM_RUNTIME` as an
infrastructure datapoint, but it does not validate the B0D recipe as a policy.

The next valid policy result still requires a real B0D continuation, followed
by the corrected-bridge rough-terrain gentle-push 8-seed gates.

## Decision

`PASS_GPU_RECOVERY_SMOKE`

Proceed with one of:

- run a longer local B0D continuation if the workstation remains stable, or
- run the pinned CUDA/A100 B0D workflow when a Colab session is visible.

No robot test, SSH, deploy, grounded replay, or robot runtime behavior change
was performed.
