# Phase 2 Transition-Preserving PPO Smoke Decision

status: `HOLD_REWARD_PPO_ERODES_SUPPORT_TRANSITION`

## Scope

Offline-only smoke test of reward-side PPO fine-tuning from the
transition-preserving rough-terrain warm-start.

No robot tests, SSH, deploy, grounded replay, runtime behavior changes, or
training from scratch were performed.

## Restore Point

```text
checkpoint: outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_step0_checkpoint
source ONNX: outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_step0.onnx
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
bridge: corrected fitted bridge
command_x: 0.08
```

The restore point preserved rough-terrain transition behavior:

```text
seed 2/4 track ratio: 0.6652 / 0.5947
seed 2/4 single support: 38.4% / 32.0%
seed 2/4 max tracking p95: 0.2598 / 0.2533
seed 2/4 max velocity excess: 0.7987 / 0.8291
```

## Smoke Runs

Two tiny CPU PPO runs were executed to test whether closed-loop reward
fine-tuning can reduce tracking/envelope error without deleting the support
transition.

### Normal Trust Region

```text
timesteps: 80
learning_rate: 1e-5
restore_policy_kl_scale: 2.0
behavior_prior_scale: -0.02
status: PASS_SMOKE_RUN
```

Gate result at step 80:

```text
seed 2/4 status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS / HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 2/4 vx: 0.0041 / 0.0089 m/s
seed 2/4 track ratio: 0.0516 / 0.1115
seed 2/4 single support: 3.2% / 0.8%
seed 2/4 double support: 96.8% / 99.2%
seed 2/4 max tracking p95: 0.2004 / 0.1953
seed 2/4 max velocity excess: 0.6992 / 0.5796
```

### Lockdown Trust Region

```text
timesteps: 80
learning_rate: 1e-6
restore_policy_kl_scale: 100.0
behavior_prior_scale: -0.10
entropy_cost: 0.0
status: PASS_SMOKE_RUN
```

Gate result at step 80:

```text
seed 2/4 status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS / HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
seed 2/4 vx: 0.0044 / 0.0094 m/s
seed 2/4 track ratio: 0.0548 / 0.1181
seed 2/4 single support: 3.2% / 2.0%
seed 2/4 double support: 96.8% / 98.0%
seed 2/4 max tracking p95: 0.1976 / 0.1905
seed 2/4 max velocity excess: 0.7639 / 0.5738
```

## Interpretation

The PPO restore/export path works, but reward-side fine-tuning erased the
support transition after only 80 timesteps. The apparent tracking improvement
came from stopping the step, not from learning a terrain-safe in-envelope gait.

Even a very tight trust region did not preserve forward progress. Longer runs
of this same scalar reward-side PPO recipe are not authorized by this result.

## Decision

Proceed to transition-aware relabeling or an explicit action/parameter-space
correction that preserves double-support preparation and single-support timing.
Do not continue this reward-PPO branch without a structural change to how
transition labels are protected.
