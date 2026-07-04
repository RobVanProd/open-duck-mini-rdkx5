# Phase 2 z=0.0075 Next Branch After Motion-Guard Hold

status: `PASS_PHASE2_Z0075_LIVE_ORACLE_RECOVERY_PIVOT_READY`

This is an offline decision artifact. It did not train, SSH, deploy, touch the
robot, run robot tests, or run grounded replay.

## New Evidence

- motion-guarded PPO result:
  `outputs/analysis/PHASE2_Z0075_MOTION_GUARDED_LOCAL_ROCM_RESULT.md`
- result_status: `HOLD_MOTION_GUARD_STILL_COLLAPSES`
- local ROCm run: `PASS_SMOKE_RUN`
- all exported checkpoints failed seed-0 x=0.08 motion screen.
- failure shape: stable, in-envelope, all-double-support standstill.

The command-progress failure controls were wired correctly and the negative
failure penalty was not clipped, but the PPO refinement still converged to
near-zero forward motion.

## Closed Path

Do not run another scalar PPO reward-tuning variant from:

`phase2_limit198_ppo_loc_warmstart_step0_checkpoint`

with the Iter21/Phase2 student only as a soft behavior-prior reward.

This path has now failed in two aligned ways:

1. behavior-prior post-push PPO: stable in-envelope near-standstill.
2. behavior-prior plus motion guard: stable in-envelope all-double-support
   near-standstill.

The failure is no longer a missing scalar command-progress term. The PPO update
is not preserving the moving gait under the z=0.0075 push-recovery objective.

## Better Next Branch

Use live-oracle / state-coverage recovery rather than another PPO reward pass.

Existing live-oracle evidence is closer to the needed failure surface:

- `phase2_z0075_intermediate_push_live_oracle_iter1_rate150_20260704`
  - compact screen improved, but full distribution regressed.
- `phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_rate150_20260704`
  - seed 7 passes the compact z=0.0075 intermediate-push screen.
  - seed 0 remains a late push-window pitchover.
  - this is a motion-preserving failure, not standstill collapse.

That is the right failure to work on. A moving candidate that pitches over under
a push is closer to Phase 2 robustness than a PPO candidate that never leaves
double support.

## Next Run Shape

Run one bounded live-oracle recovery iteration from the moving z=0.0075
intermediate-push student, focused on the seed-0 late push-window failure:

- student_policy:
  `policy/candidates/phase2_z0075_intermediate_push_live_oracle_iter2_failure_recovery_rate150_20260704/candidate.onnx`
- teacher_manifest:
  corrected-bridge z=0.0075 live-oracle aggregate from the previous iter2 run.
- base_manifest:
  previous iter2 aggregate manifest.
- command_x: `0.08`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0075`
- reset_mode: `home-support`
- bridge_mode: `fitted`
- eval pushes: enabled, `0.075-0.125`, interval `1.0-1.5s`
- x0 teacher: `zero_action`
- gate-aware sample weights: enabled

The next candidate should be screened first on:

1. x=0.08 seed 0 with intermediate pushes.
2. x=0.08 seed 7 with intermediate pushes.
3. x=0.0 seeds 0 and 1.

Only if those pass should the full 8-seed z=0.0075 intermediate-push gate run.

## Falsifier

If another live-oracle recovery iteration preserves motion but keeps moving the
failure between seeds instead of improving the distribution, stop and write a
distribution-level decision. Do not return to scalar PPO reward tuning.

## Status

The Phase 2 goal remains active and incomplete. No robot validation is
authorized.
