# Phase 2 z=0.002 Teacher-Continuity Next Recipe

status: `PASS_Z002_TEACHER_CONTINUITY_RECIPE_READY`
stage: `stage_z002_teacher_continuity`
supersedes_recipe: `phase2-z002-tracking-margin`
diagnosis_status: `HOLD_Z002_SCALAR_TRACKING_MARGIN_NOT_PROMOTED`

This is an offline planning artifact. It did not train, SSH, deploy, or touch the robot.

## Root Cause Summary

- The A100 scalar tracking-margin run completed training but no checkpoint passed the compact x=0.08 tracking threshold.
- The best compact checkpoint retained motion at x=0.08: track ratio 0.2939, mean vx 0.0235 m/s, max tracking p95 0.2184 rad.
- All compact checkpoints stayed below the corrected velocity envelope, so the hold is tracking margin rather than actuator over-speed.
- The prior recipe's falsifier fired: do not run another scalar reward tweak that may buy tracking by reducing motion.

## Recipe Intent

- Warm-start from the same z=0.002 C0 245760 moving parent, not from scratch.
- Keep terrain at z=0.002 and no pushes; this is parent recovery before terrain escalation.
- Use a teacher-action behavior-prior MLP plus stronger restore-policy KL as a trust region around the moving gait.
- Relax the scalar target-rate penalty relative to tracking-margin so the policy does not recover tracking by freezing.
- Reject any checkpoint that passes smoke but fails the canonical compact x=0/x=0.08 corrected-bridge sweep.

## Required Inputs

- restore_checkpoint: `outputs/phase2_domain_randomization/stage_c0_terrain_z002_preserve_from_a2_gpu/smoke_20260628T103743Z_gpu/2026_06_28_064431_245760` present=`True`
- behavior_prior_mlp: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz` present=`True` sha256=`312f1ef0ba758af5fdeae900ce0a34dab659fe348a9f389988ddaaaa15659497`

## Key Settings

- `workflow`: `phase2-z002-teacher-continuity`
- `terrain_hfield_z_scale`: `0.002`
- `num_timesteps`: `122880`
- `restore_policy_kl_scale`: `7.5`
- `behavior_prior_scale`: `-0.18`
- `behavior_prior_huber_delta`: `0.08`
- `ppo_learning_rate`: `2e-06`
- `ppo_clipping_epsilon`: `0.015`
- `ppo_max_grad_norm`: `0.08`
- `target_rate_scale`: `-0.01`
- `actuator_tracking_scale`: `-0.005`
- `command_progress_scale`: `3.5`
- `command_progress_shortfall_scale`: `-10.0`
- `command_progress_required_ratio`: `0.55`
- `forward_progress_scale`: `4.5`
- `action_rate_scale`: `-0.035`
- `push_enable`: `False`
- `actuator_bridge_velocity_limit_range_rad_s`: `[2.0, 3.25]`

## Preferred Colab GPU Command

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-z002-teacher-continuity \
    --session \
    open-duck-l4 \
    --candidate-name \
    phase2_z002_teacher_continuity_cuda \
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

## Acceptance

- Compact x=0.08 fitted-bridge sweep passes with track ratio >= 0.25 and tracking p95 <= 0.20.
- Compact x=0.0 fitted-bridge sweep remains passing.
- Full z=0.002 x=0.08 and x=0.0 post-training seed gates pass before use as a terrain parent.
- No robot validation is authorized by this recipe.

## Post-Training Decision Command

```bash
python3 \
    tools/report_phase2_z002_tracking_margin_post_training_gates.py \
    '<candidate_name>_post_training_seed_gates.json' \
    --output-md \
    outputs/analysis/PHASE2_Z002_TEACHER_CONTINUITY_POST_TRAINING_GATE_DECISION.md \
    --output-json \
    outputs/analysis/phase2_z002_teacher_continuity_post_training_gate_decision.json
```

## Falsifier

If teacher continuity still holds above 0.20 rad tracking p95 while preserving motion, stop z=0.002 PPO reward/continuity tweaks and inspect the evaluator/teacher-action target manifold before spending another A100 run.
