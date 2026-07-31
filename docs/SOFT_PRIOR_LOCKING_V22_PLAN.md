# Soft-Prior Locking V22 Plan

## Purpose

`movement_bootstrap_v22` is a diagnostic follow-up to V21.

V21 proved the default-off soft-prior training path is wired and trainable, but
the final policy did not stay near the curated pitch-chain prior:

```text
V21 x=0.04 vanilla gate:
  falls: 4/4
  mean_local_vx: -0.0249 m/s
  track_ratio_mean: -0.6216
  action_saturation_pct_mean: 0.0
  soft_prior_abs_error_mean: 0.2609
```

That means the weak prior did not lock the policy into the intended
low-command gait basin. V22 tests the next narrower question:

```text
Can PPO be held near the curated low-command gait shape at all if the prior is
strong and step-phased?
```

## Recipe

Planner:

```bash
python3 tools/plan_staged_curriculum_training.py \
  --recipe movement_bootstrap_v22 \
  --output-md outputs/analysis/STAGED_CURRICULUM_TRAINING_PLAN_V22.md \
  --output-json outputs/analysis/staged_curriculum_training_plan_v22.json
```

Phase 1:

```text
name: phase1_strong_step_prior_lock_probe
dynamics: vanilla
x command: 0.035-0.045
phase gate: x=0.04 vanilla
soft_prior_config_json: outputs/analysis/soft_prior_fragment_config.json
soft_prior_scale: -0.50
soft_prior_phase_source: step
```

Differences from V21:

```text
V21 soft_prior_scale: -0.025
V22 soft_prior_scale: -0.50

V21 soft_prior_phase_source: imitation_i
V22 soft_prior_phase_source: step
```

## Required Gate

The first gate is still the x=0.04 vanilla multi-seed gate.

Do not run phase 2, x=0.08, fitted bridge, deployment, or robot validation
unless V22 passes both:

```text
1. behavior gate:
   - coherent positive forward tracking across seeds
   - no reverse seed
   - no low-progress termination distribution
   - no height-collapse seed

2. prior-lock gate:
   - trace soft_prior_abs_error_mean materially below V21's 0.2609
   - target threshold: < 0.12 preferred
   - < 0.18 is useful but still a hold for robot work
```

## Interpretations

If V22 locks to the prior and moves forward:

```text
The soft-prior mechanism can hold the gait basin. Next work is stabilizing and
then reintroducing mild actuator bridge.
```

If V22 locks to the prior but still fails:

```text
The curated fragment/gait itself is not a stable closed-loop policy seed.
Next work is reference/gait quality, contact timing, or a different seed.
```

If V22 does not lock to the prior:

```text
The soft-prior reward path is not strong enough as an imitation mechanism.
Next work should move to explicit supervised pretraining / behavior cloning or
an imitation mechanism that constrains the policy update directly.
```

## Non-Goals

```text
no robot tests
no SSH
no deploy
no x=0.08
no fitted bridge
no policy deployment
do not make V22 the default recipe
```
