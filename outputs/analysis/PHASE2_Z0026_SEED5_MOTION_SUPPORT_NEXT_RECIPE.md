# Phase 2 z=0.0026 Seed-5 Motion-Support Next Recipe

status: `PASS_Z0026_SEED5_MOTION_SUPPORT_RECIPE_READY`
stage: `stage_z0026_seed5_motion_support_repair`
diagnosis_status: `HOLD_Z0026_MOVING_COMMAND_SUPPORT_TRANSFER`
terrain_hfield_z_scale: `0.0026`

This is an offline planning artifact. It did not train, SSH, deploy, touch the robot, or run grounded replay.

## Root Cause Summary

- At z=0.0026, the preserved teacher-continuity 81920 checkpoint is a near-miss: full x=0.08 gate is 7/8, with seed 5 as the only fall.
- Seed 5 fails by reverse velocity and base-height collapse while the pitch-chain sent target rates remain inside the corrected actuator envelope.
- The current z=0.0025 target-limited support candidate transfers to z=0.0026 at x=0.0 in a short screen, but fails the moving x=0.08 seed-5 screen by the same reverse-height collapse.
- The broad phase2-z005-support recovery direction stabilized the short screen by moving backward in double support, so broad support shaping is closed for this failure.

## Recipe Intent

- Warm-start from the preserved z=0.0026 teacher-continuity 81920 checkpoint; do not train from scratch.
- Keep terrain at z=0.0026 and keep pushes disabled; this isolates support transfer before adding new perturbations.
- Preserve the 7 passing seeds with teacher-continuity restore KL and small PPO updates.
- Add narrow anti-reverse and base-height pressure only; do not add broad double-support dwell/contact-shaping terms.
- Select by compact checkpoint sweep, then require full x=0.0 and x=0.08 8-seed gates before promoting.

## Canonical Inputs

- corrected_bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json` present=`True` sha256=`3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0`
- restore_checkpoint: `outputs/analysis/phase2_restore_checkpoints/phase2_z0026_teacher_continuity_81920` present=`True` tree_sha256=`4646f7d84260f7f4669e1cbfdc9b677da8999fea9df2d7a6651e184da0d8ae0c`

## Key Settings

- `workflow`: `phase2-z002-teacher-continuity`
- `terrain_hfield_z_scale`: `0.0026`
- `num_timesteps`: `81920`
- `ppo_num_envs`: `64`
- `restore_policy_kl_scale`: `7.5`
- `ppo_learning_rate`: `2e-06`
- `ppo_clipping_epsilon`: `0.015`
- `ppo_max_grad_norm`: `0.08`
- `target_rate_scale`: `-0.01`
- `actuator_tracking_scale`: `-0.005`
- `forward_progress_scale`: `4.5`
- `command_progress_scale`: `3.5`
- `command_progress_shortfall_scale`: `-10.0`
- `command_progress_required_ratio`: `0.55`
- `action_rate_scale`: `-0.035`
- `base_height_scale`: `-0.45`
- `forward_pitch_scale`: `-0.35`
- `forward_pitch_rate_scale`: `-0.07`
- `forward_wrong_direction_scale`: `-6.0`
- `forward_wrong_direction_allowed_reverse_ratio`: `0.005`
- `push_enable`: `False`

## Preferred Colab GPU Command

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-z002-teacher-continuity \
    --session \
    open-duck-a100-phase2-z0026 \
    --candidate-name \
    phase2_z0026_seed5_motion_support_cuda \
    --phase2-restore-checkpoint-path \
    outputs/analysis/phase2_restore_checkpoints/phase2_z0026_teacher_continuity_81920 \
    --phase2-terrain-hfield-z-scale \
    0.0026 \
    --phase2-num-timesteps \
    81920 \
    --phase2-ppo-num-envs \
    64 \
    --phase2-ppo-batch-size \
    512 \
    --phase2-ppo-num-minibatches \
    4 \
    --phase2-ppo-num-updates-per-batch \
    2 \
    --artifact-checkpoint-mode \
    all \
    --phase2-final-training-args-json \
    '["--forward-wrong-direction-scale", "-6.0", "--forward-wrong-direction-allowed-reverse-ratio", "0.005", "--base-height-scale", "-0.45", "--forward-pitch-scale", "-0.35", "--forward-pitch-rate-scale", "-0.07"]' \
    --candidate-checkpoint-sweep \
    --candidate-checkpoint-sweep-commands \
    0.0,0.08 \
    --candidate-checkpoint-sweep-duration \
    1.0 \
    --candidate-checkpoint-sweep-jax-platform \
    cpu \
    --candidate-timeout-s \
    10800 \
    --run
```

## Detached Colab GPU Command

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-z002-teacher-continuity \
    --session \
    open-duck-a100-phase2-z0026 \
    --candidate-name \
    phase2_z0026_seed5_motion_support_cuda \
    --phase2-restore-checkpoint-path \
    outputs/analysis/phase2_restore_checkpoints/phase2_z0026_teacher_continuity_81920 \
    --phase2-terrain-hfield-z-scale \
    0.0026 \
    --phase2-num-timesteps \
    81920 \
    --phase2-ppo-num-envs \
    64 \
    --phase2-ppo-batch-size \
    512 \
    --phase2-ppo-num-minibatches \
    4 \
    --phase2-ppo-num-updates-per-batch \
    2 \
    --artifact-checkpoint-mode \
    all \
    --phase2-final-training-args-json \
    '["--forward-wrong-direction-scale", "-6.0", "--forward-wrong-direction-allowed-reverse-ratio", "0.005", "--base-height-scale", "-0.45", "--forward-pitch-scale", "-0.35", "--forward-pitch-rate-scale", "-0.07"]' \
    --candidate-checkpoint-sweep \
    --candidate-checkpoint-sweep-commands \
    0.0,0.08 \
    --candidate-checkpoint-sweep-duration \
    1.0 \
    --candidate-checkpoint-sweep-jax-platform \
    cpu \
    --candidate-timeout-s \
    10800 \
    --no-poll \
    --run
```

## Post-Training Seed-5 Short Gate

```bash
../envs/open-duck-playground/bin/python \
    tools/run_candidate_seed_sweep.py \
    --policies \
    'repair=<downloaded_or_exported_repair_candidate.onnx>' \
    --fit-json \
    outputs/analysis/actuator_response_fit_corrected_knee.json \
    --playground-path \
    ../Open_Duck_Playground \
    --env-python \
    ../envs/open-duck-playground/bin/python \
    --duration \
    2 \
    --bridge-mode \
    fitted \
    --task \
    rough_terrain_backlash \
    --jax-platform \
    cpu \
    --terrain-hfield-z-scale \
    0.0026 \
    --command-x \
    0.08 \
    --seeds \
    5 \
    --trace-seeds \
    5 \
    --trace-full-obs \
    --output-dir \
    outputs/analysis/phase2_z0026_seed5_motion_support_repair_seed5_short \
    --output-md \
    outputs/analysis/PHASE2_Z0026_SEED5_MOTION_SUPPORT_REPAIR_SEED5_SHORT.md \
    --output-json \
    outputs/analysis/phase2_z0026_seed5_motion_support_repair_seed5_short.json \
    --run
```

## Post-Training Full Gates

### x000

```bash
../envs/open-duck-playground/bin/python \
    tools/run_candidate_seed_sweep.py \
    --policies \
    'repair=<downloaded_or_exported_repair_candidate.onnx>' \
    --fit-json \
    outputs/analysis/actuator_response_fit_corrected_knee.json \
    --playground-path \
    ../Open_Duck_Playground \
    --env-python \
    ../envs/open-duck-playground/bin/python \
    --duration \
    15 \
    --bridge-mode \
    fitted \
    --task \
    rough_terrain_backlash \
    --jax-platform \
    cpu \
    --terrain-hfield-z-scale \
    0.0026 \
    --command-x \
    0.0 \
    --seeds \
    0,1,2,3,4,5,6,7 \
    --output-dir \
    outputs/analysis/phase2_z0026_seed5_motion_support_repair_full_x000 \
    --output-md \
    outputs/analysis/PHASE2_Z0026_SEED5_MOTION_SUPPORT_REPAIR_FULL_X000.md \
    --output-json \
    outputs/analysis/phase2_z0026_seed5_motion_support_repair_full_x000.json \
    --run
```

### x008

```bash
../envs/open-duck-playground/bin/python \
    tools/run_candidate_seed_sweep.py \
    --policies \
    'repair=<downloaded_or_exported_repair_candidate.onnx>' \
    --fit-json \
    outputs/analysis/actuator_response_fit_corrected_knee.json \
    --playground-path \
    ../Open_Duck_Playground \
    --env-python \
    ../envs/open-duck-playground/bin/python \
    --duration \
    15 \
    --bridge-mode \
    fitted \
    --task \
    rough_terrain_backlash \
    --jax-platform \
    cpu \
    --terrain-hfield-z-scale \
    0.0026 \
    --command-x \
    0.08 \
    --seeds \
    0,1,2,3,4,5,6,7 \
    --output-dir \
    outputs/analysis/phase2_z0026_seed5_motion_support_repair_full_x008 \
    --output-md \
    outputs/analysis/PHASE2_Z0026_SEED5_MOTION_SUPPORT_REPAIR_FULL_X008.md \
    --output-json \
    outputs/analysis/phase2_z0026_seed5_motion_support_repair_full_x008.json \
    --run
```

## Acceptance

- Seed 5 x=0.08 short screen must complete duration with positive mean vx and no velocity-envelope excess.
- Full z=0.0026 x=0.08 gate must improve from 7/8 to 8/8 duration complete without reducing the passing seeds into standstill.
- Full z=0.0026 x=0.0 gate must remain 8/8 duration complete with command semantics preserved.
- No candidate is promotable if mean x=0.08 track ratio improves only by over-envelope target velocity or x=0.0 drift.
- No robot validation is authorized by this recipe.

## Falsifiers

- If seed 5 remains reverse/height-collapse while velocity stays in envelope, stop narrow scalar repair and inspect the seed-5 state/contact manifold.
- If the recipe removes the seed-5 fall by lowering motion or reversing, stop this direction; it repeats the broad support-recovery failure.
- If any passing seed regresses to fall/standstill, reduce or abandon the anti-reverse/base-height terms rather than escalating terrain.
