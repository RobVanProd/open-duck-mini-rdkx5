# Phase 2 z=0.0075 Motion-Guarded Behavior-Prior Recipe

status: `PASS_PHASE2_Z0075_MOTION_GUARDED_RECIPE_READY`

This is an offline planning artifact. It did not train, SSH, deploy, touch the
robot, run robot tests, or run grounded replay.

## Source Result

- source_result: `HOLD_BEHAVIOR_PRIOR_LOW_FORWARD_PROGRESS`
- source_result_artifact: `outputs/analysis/PHASE2_Z0075_BEHAVIOR_PRIOR_LOCAL_ROCM_RESULT.md`
- source_result_sha256: `2f945c72d32cc38e20a198ce128fa633c0d33d500e546bec1f34370f2f47b421`
- local_rocm_run_status: `PASS_SMOKE_RUN`
- local_rocm_manifest_sha256: `09619f3adb31584b752b3228919b4d6c30e013959df8c36d026642c49705c268`

The previous behavior-prior run proved that local ROCm can complete this bounded
Phase 2 training/export path, but every triaged checkpoint collapsed to
near-standstill:

| checkpoint | triage result | track ratio | mean vx m/s | max sent target velocity p95 rad/s |
|---|---|---:|---:|---:|
| step40960 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0238 | 0.0019 | 0.2199 |
| step81920 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0284 | 0.0023 | 0.1823 |
| step122880 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0276 | 0.0022 | 0.1522 |

Repeating the same recipe is rejected. It preserves safety by suppressing
motion.

## Inputs

- corrected_bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- corrected_bridge_sha256: `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0`
- moving_anchor_policy: `policy/candidates/phase2_z0075_iter21_early_lunge_gain095_rate150_20260704/candidate.onnx`
- moving_anchor_policy_sha256: `72aa93c2ab249d2e9b22bb5415ef6c96c7407833fbfd21233892b6daa6afda14`
- behavior_prior_mlp_npz: `outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_rate150_candidate/candidate_mlp.npz`
- behavior_prior_mlp_sha256: `71f520712a10613d3e2304a33cbcd641f6bb59fb0d5c1dc3e34a5c8fe93569b2`
- restore_checkpoint: `outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0075`
- command_x_training_range: `0.06-0.10`
- canonical_gate_command_x: `0.08`
- canonical_gate_reset_mode: `home-support`
- canonical_gate_reset_settle_ticks: `10`

## Diagnosis

The latest run did not fail because of ROCm, export, policy contract, or the
corrected actuator bridge. It failed because PPO found a low-action optimum:
stable, in-envelope, and almost stationary.

The Playground runner and wrapper already expose a default-off cumulative
command-progress failure:

- `--command-progress-failure-enable`
- `--command-progress-failure-min-ratio`
- `--command-progress-failure-warmup-steps`
- `--command-progress-failure-scale`

The environment computes cumulative signed local forward progress over the
command window. If positive-command progress remains below the configured floor
after warmup, the episode terminates. The reward scale is only meaningful if
`--reward-clip-min` is below zero; the default reward clip minimum is `0.0`.

## Recipe Change

Make safe standstill invalid during training while preserving the Iter21 moving
behavior:

- Enable command-progress failure.
- Set `command_progress_failure_min_ratio=0.30`.
  - This is far above the failed checkpoints' `~0.02` track ratio.
  - This remains below the Iter21 rough/push moving seeds' `~0.30-0.40` track
    ratios, so it does not demand a fast gait.
- Set `command_progress_failure_warmup_steps=120`.
  - This gives 2.4 seconds at the 50 Hz control loop before no-progress
    termination can fire.
- Set `command_progress_failure_scale=-10.0`.
- Set `reward_clip_min=-100.0` so the signed failure penalty is not clipped away.
- Keep the behavior prior, but do not trust behavior-prior loss alone to
  preserve motion.
- Keep corrected per-joint actuator-envelope gates strict.

## Local ROCm Diagnostic Command

This is the next bounded run. It is backend evidence unless the exported
checkpoints clear the canonical CPU gates.

```bash
../envs/open-duck-playground/bin/python \
    tools/run_actuator_bridge_training_smoke.py \
    --playground-path ../Open_Duck_Playground \
    --env-python ../envs/open-duck-playground/bin/python \
    --output-root outputs/phase2_domain_randomization/stage_z0075_motion_guarded_behavior_prior_local_rocm \
    --run \
    --platform gpu \
    --local-rocm-safe-env \
    --timeout-s 7200 \
    --task rough_terrain_backlash \
    --num-timesteps 122880 \
    --export-min-step 1 \
    --ppo-num-envs 16 \
    --ppo-num-evals 4 \
    --ppo-episode-length 750 \
    --ppo-unroll-length 20 \
    --ppo-batch-size 128 \
    --ppo-num-minibatches 1 \
    --ppo-num-updates-per-batch 2 \
    --restore-checkpoint-path outputs/analysis/phase2_limit198_ppo_loc_warmstart_step0_checkpoint \
    --terrain-hfield-z-scale 0.0075 \
    --push-enable \
    --push-interval-min-s 1.0 \
    --push-interval-max-s 1.5 \
    --push-magnitude-min 0.075 \
    --push-magnitude-max 0.125 \
    --push-recovery-actuator-tracking-scale -0.025 \
    --push-recovery-actuator-tracking-huber-delta 0.03 \
    --push-recovery-tracking-window-steps 60 \
    --push-recovery-tracking-joint-indices 2,3,4,11,12,13 \
    --base-height-scale -0.9 \
    --forward-pitch-scale -0.55 \
    --forward-pitch-rate-scale -0.12 \
    --actuator-tracking-scale -0.012 \
    --restore-policy-kl-scale 4.5 \
    --tracking-lin-vel-scale 3 \
    --tracking-sigma 0.01 \
    --forward-progress-scale 2.8 \
    --command-progress-scale 1.7 \
    --command-progress-shortfall-scale -4.5 \
    --command-progress-required-ratio 0.45 \
    --command-progress-failure-enable \
    --command-progress-failure-min-ratio 0.30 \
    --command-progress-failure-warmup-steps 120 \
    --command-progress-failure-scale -10.0 \
    --reward-clip-min -100.0 \
    --action-rate-scale -0.07 \
    --action-magnitude-scale -0.004 \
    --lin-vel-x-min 0.06 \
    --lin-vel-x-max 0.10 \
    --lin-vel-y-min 0 \
    --lin-vel-y-max 0 \
    --ang-vel-yaw-min 0 \
    --ang-vel-yaw-max 0 \
    --zero-command-probability 0.15 \
    --enable-behavior-prior \
    --behavior-prior-mlp-npz outputs/analysis/phase2_z0075_iter21_early_lunge_gain095_rate150_candidate/candidate_mlp.npz \
    --behavior-prior-scale -0.22 \
    --behavior-prior-huber-delta 0.06
```

## Required Checkpoint Selection

Do not run a full 8-seed gate on every exported checkpoint if the checkpoint
already fails the motion floor.

For each exported ONNX:

1. Run a cheap seed-0 x=0.08 corrected-bridge gate on CPU with
   `reset-mode=home-support`, `reset-settle-ticks=10`, `z=0.0075`.
2. Reject immediately if track ratio is `< 0.25`.
3. Only run the full 8-seed x=0.08 rough/intermediate-push gate for checkpoints
   that clear the seed-0 motion screen.
4. Only after x=0.08 passes, run the x=0.0 command-semantics gate.

## Promotion Gate

A checkpoint is promotable only if it clears the canonical corrected-bridge CPU
gates:

- x=0.08 rough terrain, z=0.0075, intermediate pushes, seeds 0-7.
- duration complete: 8/8.
- no corrected per-joint target-velocity excess.
- command-conditioned motion preserved: mean track ratio must remain meaningful
  and each seed must clear the motion floor.
- x=0.0 command-semantics gate: no drift, no fall, no envelope excess.

## Falsifiers

- If all exported checkpoints fail seed-0 x=0.08 with track ratio `< 0.25`,
  report `HOLD_MOTION_GUARD_STILL_COLLAPSES`.
- If any checkpoint preserves motion but violates the corrected per-joint
  actuator envelope, report `HOLD_MOTION_GUARD_OVER_ENVELOPE`.
- If motion and envelope pass but push robustness still fails, report
  `HOLD_PUSH_RECOVERY_REMAINS`.

No robot validation is authorized from this artifact.
