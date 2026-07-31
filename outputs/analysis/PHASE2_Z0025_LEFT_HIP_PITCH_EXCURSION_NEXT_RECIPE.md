# Phase 2 z=0.0025 Left-Hip-Pitch Excursion Next Recipe

status: `PASS_Z0025_LEFT_HIP_PITCH_RECIPE_READY`
stage: `stage_z0025_left_hip_pitch_excursion`
supersedes_recipe: `PHASE2_Z0025_SEED_CONSISTENCY_NEXT_RECIPE.md`

This is an offline planning artifact. It did not train, SSH, deploy, or touch the robot.

## Why This Recipe

The artifact-first z=0.0025 boundary candidate is stable but not promoted:

- x=0.0: `PASS` 8/8, quiet command semantics.
- x=0.08: no falls, duration complete 8/8, but only 4/8 seed statuses pass.

The targeted seed-failure analysis shows the velocity failures are local:

- seed `0`: `left_hip_pitch` max sent velocity `3.0350 rad/s`, limit `2.50 rad/s`.
- seed `4`: `left_hip_pitch` max sent velocity `2.7280 rad/s`, limit `2.50 rad/s`.
- all other pitch-chain joints stay inside their corrected instantaneous limits.
- seeds `3` and `6` have low progress but no velocity excess.

The rejected seed-consistency recipe penalized all six pitch-chain swing joints and
regressed progress (`0.2350 -> 0.1732` compact x=0.08 track ratio). That falsifies broad
scalar rate tuning for this boundary failure.

## Recipe Intent

Apply the smallest plausible correction:

- add a weak swing-window instantaneous rate cost only on `left_hip_pitch`
- leave the rest of the pitch chain unconstrained by the new term
- keep progress pressure close to the boundary recipe
- use artifact-first Colab execution so the candidate is saved before any slow gate

## Key Changes From z=0.0025 Boundary

- Add targeted existing Playground hook:
  - `forward_swing_target_rate_limit_scale = -0.0015`
  - `joint_indices = 2`
  - `values = 2.50`
  - `huber_delta = 0.02`
- Apply only a minimal progress nudge:
  - `forward_progress_scale = 4.1`
  - `command_progress_scale = 3.15`
  - `command_progress_shortfall_scale = -8.25`
  - `command_progress_required_ratio = 0.50`

## Preferred Colab Command

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow phase2-z0025-boundary \
  --session open-duck-l4-z0025-lhp-excursion \
  --candidate-name phase2_z0025_lhp_excursion_l4 \
  --candidate-checkpoint-sweep \
  --candidate-checkpoint-sweep-commands 0.0,0.08 \
  --candidate-checkpoint-sweep-duration 1.0 \
  --candidate-checkpoint-sweep-jax-platform cpu \
  --candidate-timeout-s 10800 \
  --phase2-skip-post-training-gates \
  --phase2-forward-swing-target-rate-limit-scale -0.0015 \
  --phase2-forward-swing-target-rate-limit-joint-indices 2 \
  --phase2-forward-swing-target-rate-limit-values 2.50 \
  --phase2-forward-swing-target-rate-limit-huber-delta 0.02 \
  --phase2-forward-progress-scale 4.1 \
  --phase2-command-progress-scale 3.15 \
  --phase2-command-progress-shortfall-scale -8.25 \
  --phase2-command-progress-required-ratio 0.50 \
  --exec-remote \
  --exec-remote-timeout-s 14400 \
  --run
```

## Acceptance

Compact checkpoint sweep must not regress below the prior boundary candidate:

- x=0.08 compact track ratio `>= 0.2350`
- x=0.08 compact mean vx `>= 0.0188 m/s`
- x=0.0 compact status remains `PASS_CANDIDATE_SIM_GATE`

If compact sweep clears that screen, run full local CPU gates:

- z=0.0025 x=0.08:
  - 8/8 seeds pass
  - zero falls
  - duration complete 8/8
  - no p95 velocity excess
  - no instantaneous max velocity excess
  - tracking p95 stays near the prior `0.19 rad` level
  - track ratio stays at or above `0.25`
- z=0.0025 x=0.0:
  - 8/8 seeds pass
  - zero falls
  - `|mean vx| <= 0.005 m/s`

## Falsifier

If this local left-hip-pitch correction still regresses compact x=0.08 progress, stop
reward-side correction for this boundary. The next branch should use targeted data/teacher
correction or gate-aware relabeling for seeds `0`, `3`, `4`, and `6`, not more scalar
penalty tuning.

Robot validation remains blocked.
