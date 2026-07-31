# Phase 2 z=0.0025 Seed-Consistency Next Recipe

status: `PASS_Z0025_SEED_CONSISTENCY_RECIPE_READY`
stage: `stage_z0025_seed_consistency`
supersedes_recipe: `phase2-z0025-boundary`

This is an offline planning artifact. It did not train, SSH, deploy, or touch the robot.

## Why This Recipe

The L4 artifact-first z=0.0025 boundary run recovered a candidate and completed full
local corrected-bridge gates:

- z=0.0025 x=0.0: passes 8/8, no falls, mean vx `0.0006 m/s`
- z=0.0025 x=0.08: no falls, duration complete 8/8, mean track ratio `0.2553`
- z=0.0025 x=0.08 still holds because only 4/8 seed statuses pass:
  - seeds 0 and 4: instantaneous target-velocity excursions
  - seeds 3 and 6: low forward progress

This is no longer the earlier support-collapse diagnosis. The gait is stable on z=0.0025,
but the seed distribution is too close to the gate boundary.

## Recipe Intent

- Keep the same warm-start source as the successful Phase 2 terrain lineage.
- Do not broaden domain randomization yet.
- Add a phase-swing pitch-chain target-rate-limit cost using the corrected per-joint
  envelope to remove seed 0/4 instantaneous excursions without globally smoothing away
  swing.
- Slightly increase command-progress pressure to lift seeds 3/6 above the low-progress
  boundary.
- Preserve x=0.0 command semantics and the no-fall z=0.0025 behavior.

## Key Changes From z=0.0025 Boundary

- Add existing Playground hook:
  - `forward_swing_target_rate_limit_scale = -0.003`
  - `joint_indices = 2,3,4,11,12,13`
  - `values = 2.50,3.25,2.75,2.25,2.75,2.00`
  - `huber_delta = 0.03`
- Keep global target-rate penalty at `0`; the issue is sparse instantaneous swing excess,
  not high p95 target velocity.
- Increase progress pressure modestly:
  - `forward_progress_scale = 4.2`
  - `command_progress_scale = 3.4`
  - `command_progress_shortfall_scale = -9.0`
  - `command_progress_required_ratio = 0.52`

## Preferred Colab Command

Run artifact-first again. Post-training seed gates should stay split from training so the
candidate is not lost if a slow gate drops the Colab transport.

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow phase2-z0025-boundary \
  --session open-duck-l4-z0025-seed-consistency \
  --candidate-name phase2_z0025_seed_consistency_l4 \
  --candidate-checkpoint-sweep \
  --candidate-checkpoint-sweep-commands 0.0,0.08 \
  --candidate-checkpoint-sweep-duration 1.0 \
  --candidate-checkpoint-sweep-jax-platform cpu \
  --candidate-timeout-s 10800 \
  --phase2-skip-post-training-gates \
  --phase2-forward-swing-target-rate-limit-scale -0.003 \
  --phase2-forward-swing-target-rate-limit-joint-indices 2,3,4,11,12,13 \
  --phase2-forward-swing-target-rate-limit-values 2.50,3.25,2.75,2.25,2.75,2.00 \
  --phase2-forward-swing-target-rate-limit-huber-delta 0.03 \
  --phase2-forward-progress-scale 4.2 \
  --phase2-command-progress-scale 3.4 \
  --phase2-command-progress-shortfall-scale -9.0 \
  --phase2-command-progress-required-ratio 0.52 \
  --exec-remote \
  --exec-remote-timeout-s 14400 \
  --run
```

## Acceptance

- z=0.0025 x=0.08 no-push:
  - 8/8 seeds pass
  - zero falls
  - duration complete 8/8
  - no p95 velocity excess
  - no instantaneous max velocity excess
  - tracking p95 stays near the prior `0.19 rad` level
  - track ratio stays at or above `0.25`
- z=0.0025 x=0.0 no-push:
  - 8/8 seeds pass
  - zero falls
  - `|mean vx| <= 0.005 m/s`
- If it passes, run z=0.0024 regression and gentle-push gates separately from the
  downloaded ONNX.

## Falsifier

If the swing target-rate-limit cost removes seed 0/4 excursions but regresses seed 3/6
progress, stop scalar reward tuning. The next branch should use targeted seed-conditioned
data/teacher correction rather than more global penalties.

If seed 0/4 excursions remain, inspect which pitch-chain joint drives the max excess and
move to a per-joint swing-rate diagnostic before more training.
