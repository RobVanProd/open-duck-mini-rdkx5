# Phase 2 Stage A Warm-Start DR Tiny CPU Smoke

status: `PASS_SMOKE_RUN`

This was an offline integration smoke only. It was not a candidate policy run,
did not SSH, did not deploy, did not run robot tests, and did not move the
robot.

## Purpose

Verify that Phase 2 can start from the verified `rate175` trainable checkpoint
and that the new Stage A domain-randomization flags are accepted by the
Playground runner before launching a real GPU training stage.

## Inputs

- restore checkpoint: `outputs/analysis/ppo_bc_command_conditioned_rate175_step0_checkpoint`
- behavior prior NPZ: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz`
- task: `flat_terrain_backlash`
- platform: `cpu`
- timesteps requested: `20`
- output dir: `outputs/analysis/phase2_stage_a_warmstart_dr_tiny_cpu/smoke_20260628T015226Z_cpu`

## Stage A DR Settings Checked

- friction: `0.7-1.0`
- frictionloss scale: `0.97-1.03`
- armature scale: `1.0-1.03`
- mass scale: `0.97-1.03`
- COM jitter: `0.015 m`
- torso mass delta: `-0.03 to 0.03`
- qpos jitter: `0.01 rad`
- actuator gain scale: `0.97-1.03`
- leg geometry jitter scale: `0.005`
- push enabled: `False`
- noise level: `0.5`

## Result

- return code: `0`
- elapsed: `64.86 s`
- runner step line: `STEP: 40 reward: 1.3708782196044922 reward_std: 0.7979176044464111`
- checkpoint line: `Saving checkpoint (step: 40): outputs/analysis/phase2_stage_a_warmstart_dr_tiny_cpu/smoke_20260628T015226Z_cpu/2026_06_27_215310_40`

## Interpretation

The trainable warm-start, restore-policy KL, corrected actuator bridge, Stage A
domain-randomization flags, push/noise overrides, and default-off leg geometry
jitter path are wired well enough to execute a minimal PPO update. This smoke
does not replace the real Stage A GPU run or the corrected-bridge seed gates.
