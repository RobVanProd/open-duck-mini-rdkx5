# Phase 2 z0.005 Motion-Prior Next Recipe

status: `PASS_Z005_MOTION_PRIOR_RECIPE_READY`
stage: `stage_z005_motion_prior`
supersedes_recipe: `phase2-z005-motion-floor`

## Trigger

The `phase2-z005-motion-floor` T4 run completed training but produced no promotable
checkpoint. All checkpoints stayed inside the corrected actuator envelope and preserved
`x=0.0`, but every checkpoint held at `x=0.08` for low forward progress.

Best compact checkpoint:

- step: `81920`
- track ratio: `0.1730`
- mean vx: `0.0138 m/s`
- max pitch sent velocity p95: `1.4369 rad/s`
- max pitch tracking p95: `0.2130 rad`
- envelope excess: `0.0 rad/s`

## Diagnosis

The failure is not actuator excess or instability. The recipe over-preserved posture and
under-produced forward motion on z0.005 terrain. Since the flat Phase A2 candidate was
produced with the command-conditioned behavior-prior teacher, the next z0.005 recipe should
restore direct action-continuity pressure from that teacher while keeping the corrected
bridge and z0.005 terrain rung unchanged.

## Key Change

Enable the existing behavior-prior hook for the z0.005 workflow:

- behavior prior NPZ:
  `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz`
- behavior prior scale: `-0.25`
- behavior prior huber delta: `0.05`

This is weaker than Phase A2's `-0.4` prior and should bias toward the known walking
manifold without fully overriding the z0.005 adaptation.

## Preferred Colab Command

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow phase2-z005-motion-floor \
  --session open-duck-l4 \
  --candidate-name phase2_z005_motion_prior_cuda \
  --candidate-behavior-prior-mlp-npz outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz \
  --candidate-behavior-prior-scale -0.25 \
  --candidate-behavior-prior-huber-delta 0.05 \
  --candidate-checkpoint-sweep \
  --candidate-checkpoint-sweep-commands 0.0,0.08 \
  --candidate-checkpoint-sweep-duration 1.0 \
  --candidate-checkpoint-sweep-jax-platform cpu \
  --candidate-timeout-s 10800 \
  --run
```

## Gate

Use the same corrected-bridge compact checkpoint sweep:

- `x=0.0`: pass candidate gate
- `x=0.08`: track ratio >= `0.25`, mean vx >= `0.020 m/s`
- velocity envelope excess: `0.0`
- no action saturation

If the behavior-prior run remains at the same low-progress plateau, the next change should
not add another scalar reward term. It should move to explicit teacher-action continuity or
live-oracle DAgger under z0.005 terrain.
