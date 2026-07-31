# Phase 2 z=0.00245 On-Policy Support Recovery Recipe

status: `PASS_Z00245_ON_POLICY_SUPPORT_RECIPE_READY`
stage: `stage_z00245_on_policy_support_recovery`
terrain_hfield_z_scale: `0.00245`

This is an offline planning artifact. It did not train, SSH, deploy, or touch the robot.

## Decision Basis

- decision_json: `outputs/analysis/phase2_z00245_support_recovery_next_decision_20260702.json`
- decision_status: `HOLD_Z00245_ONE_SHOT_BC_CLOSED`
- closed_branch: `one_shot_bc_or_direct_relabel_from_z0024_source_to_z00245_failed_states`

## Canonical Inputs

- `corrected_bridge`: `{'path': 'outputs/analysis/actuator_response_fit_corrected_knee.json', 'present': True, 'sha256': '3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0'}`
- `z0024_source_manifest`: `{'path': 'outputs/analysis/phase2_z0024_corrected_terrain_source_manifest.json', 'present': True, 'sha256': 'a44623eeaad22374dc2cc964706dc19041c5f7529ea4792ce685981f0e5179f9', 'role': 'anchor_only_not_direct_failed_state_labels'}`
- `restore_checkpoint`: `{'path': 'outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520', 'present': True, 'file_count': 11, 'tree_sha256': 'df4a570a232fd82c2f5eeccb109bf4f5d8b64f95b9a3424aa7f175bc971cbbbc'}`

## Recipe Intent

- Use the existing on-policy phase2-z0025-boundary workflow, but pin terrain to z=0.00245.
- Warm-start from the Phase A2 checkpoint; do not train from scratch.
- Keep corrected actuator tracking and target-rate costs active during optimization.
- Use the z=0.0024 source manifest only as an anchor/behavior prior if explicitly configured, not as copied labels for failed z=0.00245 states.
- Gate seed 5 at x=0.0 before x=0.08, then expand to 8-seed and z=0.0024 regression gates only if the short gates pass.

## Key Settings

- `workflow`: `phase2-z0025-boundary`
- `terrain_hfield_z_scale`: `0.00245`
- `num_timesteps`: `81920`
- `ppo_num_envs`: `64`
- `target_rate_scale`: `-0.01`
- `actuator_tracking_scale`: `-0.005`
- `command_progress_required_ratio`: `0.45`
- `corrected_bridge_velocity_limit_range_rad_s`: `[2.0, 3.25]`
- `push_enable`: `False`
- `post_training_primary_gate`: `z00245_x000/x008_no_push`

## Package-Only Check

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-z0025-boundary \
    --session \
    open-duck-a100-phase2-z00245 \
    --candidate-name \
    phase2_z00245_on_policy_support_cuda \
    --phase2-terrain-hfield-z-scale \
    0.00245 \
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
    --phase2-target-rate-scale \
    -0.01 \
    --phase2-actuator-tracking-scale \
    -0.005 \
    --phase2-command-progress-required-ratio \
    0.45 \
    --candidate-checkpoint-sweep \
    --candidate-checkpoint-sweep-commands \
    0.0,0.08 \
    --candidate-checkpoint-sweep-duration \
    1.0 \
    --candidate-checkpoint-sweep-jax-platform \
    cpu \
    --candidate-timeout-s \
    10800 \
    --package-only
```

## Preferred Colab GPU Command

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-z0025-boundary \
    --session \
    open-duck-a100-phase2-z00245 \
    --candidate-name \
    phase2_z00245_on_policy_support_cuda \
    --phase2-terrain-hfield-z-scale \
    0.00245 \
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
    --phase2-target-rate-scale \
    -0.01 \
    --phase2-actuator-tracking-scale \
    -0.005 \
    --phase2-command-progress-required-ratio \
    0.45 \
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

## Short Gate Order

### seed5_x000_short

```bash
python3 \
    tools/run_candidate_seed_sweep.py \
    --policy \
    '<candidate.onnx>' \
    --fit-json \
    outputs/analysis/actuator_response_fit_corrected_knee.json \
    --playground-path \
    ../Open_Duck_Playground \
    --env-python \
    ../envs/open-duck-playground/bin/python \
    --task \
    rough_terrain_backlash \
    --command-x \
    0.0 \
    --duration \
    2 \
    --seeds \
    5 \
    --bridge-mode \
    fitted \
    --terrain-hfield-z-scale \
    0.00245 \
    --output-dir \
    outputs/analysis/phase2_z00245_on_policy_seed5_short_x000
```

### seed5_x008_short

```bash
python3 \
    tools/run_candidate_seed_sweep.py \
    --policy \
    '<candidate.onnx>' \
    --fit-json \
    outputs/analysis/actuator_response_fit_corrected_knee.json \
    --playground-path \
    ../Open_Duck_Playground \
    --env-python \
    ../envs/open-duck-playground/bin/python \
    --task \
    rough_terrain_backlash \
    --command-x \
    0.08 \
    --duration \
    2 \
    --seeds \
    5 \
    --bridge-mode \
    fitted \
    --terrain-hfield-z-scale \
    0.00245 \
    --output-dir \
    outputs/analysis/phase2_z00245_on_policy_seed5_short_x008
```

## Acceptance

- seed 5 z=0.00245 x=0.0 short gate passes first: no fall, no action saturation, no corrected-envelope velocity excess, |vx| near zero
- seed 5 z=0.00245 x=0.08 short gate passes second: positive forward motion, no fall, no action saturation, no corrected-envelope velocity excess
- z=0.00245 8-seed x=0.0 and x=0.08 gates pass before any promotion
- known z=0.0024 regression gates remain clear

## Falsifiers

- If seed 5 x=0.0 fails by over-envelope target rate or saturation, stop and do not soften/reweight the same labels again.
- If seed 5 x=0.0 fails by base-height/support collapse without velocity excess, generate a structurally different intermediate support target before more BC.
- If x=0.0 passes but x=0.08 fails by reverse/low progress, adjust on-policy progress/support balance before scaling to 8 seeds.
