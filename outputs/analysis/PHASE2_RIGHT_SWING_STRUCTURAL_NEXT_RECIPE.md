# Phase 2 Right-Swing Structural Next Recipe

status: `PASS_RIGHT_SWING_STRUCTURAL_RECIPE_READY`
stage: `phase2_right_swing_structural`

This is an offline planning artifact. It did not train, SSH, deploy, or touch the robot.

## Diagnostic Input

- diagnostic: `outputs/analysis/phase2_swing_clearance_diagnostic_z0024.json`
- diagnostic_sha256: `3abae69a1e2f27bcfe7b975de4e1f352519ec40ebc775a376c8c83096588d48e`
- verdict: `MIXED_LEG_MODES`
- side_verdicts: `{'left': 'LATENCY_LIMITED', 'right': 'STRUCTURAL'}`
- side_classification_counts: `{'left': {'LATENCY_LIMITED': 6, 'STRUCTURAL': 2}, 'right': {'STRUCTURAL': 8}}`
- rate_driver_joint_counts: `{'left_ankle': 5, 'left_hip_pitch': 2, 'left_knee': 1, 'right_ankle': 7, 'right_knee': 1}`
- selected_fix_branch: `split fix: structural leg needs gait/geometry or longer swing duration; latency-limited leg may need phase advance`
- candidate: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- candidate_sha256: `209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b`
- corrected_bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- corrected_bridge_sha256: `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0`
- command_x: `0.08`
- terrain_hfield_z_scale: `0.0024`

## Hook Audit

- status: `PASS_TARGET_RATE_HOOK_PRESENT`
- hook_present: `True`
- missing: `[]`
- files: `{'joystick': '/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/joystick.py', 'runner': '/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/runner.py', 'rewards': '/home/lsd/robots/Open_Duck_Playground/playground/common/rewards.py', 'smoke_wrapper': 'tools/run_actuator_bridge_training_smoke.py'}`

## Recipe Intent

- Do not run global smoothing or global phase advance.
- Target only the right pitch chain because the diagnostic shows right R > 1 on all seeds.
- Use the corrected per-joint right pitch-chain limits as the training cost reference.
- Treat the new cost as a small, default-off structural guard, not as a relaxed gate.
- After any training, gate with corrected p95 and max per-joint velocity checks.
- Rerun the swing-clearance diagnostic before promoting any candidate.

## Proposed Training Command

```bash
python3 \
  tools/run_actuator_bridge_training_smoke.py \
  --platform \
  gpu \
  --run \
  --task \
  rough_terrain_backlash \
  --restore-checkpoint-path \
  outputs/phase2_domain_randomization/stage_a2_preserve_narrow_flat_no_push_gpu/smoke_20260628T031553Z_gpu/2026_06_27_232221_491520 \
  --terrain-hfield-z-scale \
  0.0024 \
  --forward-swing-target-rate-limit-scale \
  -0.0025 \
  --forward-swing-target-rate-limit-joint-indices \
  11,12,13 \
  --forward-swing-target-rate-limit-values \
  2.25,2.75,2.00 \
  --forward-swing-target-rate-limit-huber-delta \
  0.05 \
  --forward-swing-clearance-scale \
  -0.00025 \
  --forward-swing-clearance-target-m \
  0.016 \
  --forward-swing-advance-scale \
  -0.001 \
  --forward-swing-advance-target-m \
  0.004
```

## Proposed Colab Workflow Command

```bash
python3 \
  tools/run_colab_cli_cuda_workflow.py \
  --workflow \
  phase2-right-swing-structural \
  --run \
  --timeout-s \
  14400
```

## Acceptance

- x=0.08 z=0.0024 corrected-bridge gate remains 8/8.
- x=0.0 corrected-bridge gate remains 8/8 with command semantics preserved.
- No per-joint corrected envelope excess in p95 or max target velocity.
- Right-leg swing diagnostic no longer reports STRUCTURAL from R > 1.
- Left latency is not made worse; defer left-specific phase advance until right structural excess is gone.

## Falsifiers

- If right R stays > 1, stop right-swing label weighting and change gait duration or geometry.
- If target-rate cost removes forward motion, reject the recipe as another smoothing trap.
- If only p95 passes while max per-joint spikes remain, reject the candidate.
