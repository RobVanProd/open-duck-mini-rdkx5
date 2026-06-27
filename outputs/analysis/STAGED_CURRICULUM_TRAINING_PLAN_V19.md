# Staged Curriculum Training Plan

Offline-only plan. This does not touch the robot, SSH, deploy, or modify
runtime behavior. Training only runs when the planner is invoked with
`--run`.

status: `DRY_RUN`
platform: `gpu`
recipe: `movement_bootstrap_v19`
output_root: `/tmp/open_duck_staged_curriculum`

## Why

Current candidates are either aggressive and unsafe, or stable and nearly
stationary at `x=0.08`. The staged recipe bootstraps forward motion before
tightening actuator realism.

`movement_bootstrap_v19` is the imitation/reference-gait seed experiment after V18 showed the immediate low-command reward signal already prefers forward motion, but cold-start PPO still learned low/reverse progress. V19 activates the upstream polynomial reference-motion imitation reward with vanilla dynamics and gates at x=0.04. If it refines into multi-seed forward motion, cold-start discovery was the blocker. If it degrades into standstill/reverse, the reward/task landscape is actively hostile to forward gait. The reference data's nearest positive dx is about 0.074, so the gait seed is slightly faster than the x=0.04 command and must be judged by command tracking, not just survival.

## Phases

| phase | bridge | gate bridge | timesteps | x command range | shortfall | window progress | failure penalty | delay | tau | velocity limit | purpose |
|---|---|---|---:|---|---|---|---|---|---|---|---|
| `phase1_reference_imitation_seed_x004` | no | `vanilla` | 320000 | `[0.035, 0.045]` | `{'scale': -45.0, 'required_ratio': 0.55}` | `{'scale': 10.0, 'shortfall': -45.0, 'required_ratio': 0.45, 'warmup_steps': 10, 'failure': True, 'failure_min_ratio': 0.2}` | `{'scale': -140.0, 'clip_min': -20.0}` | `[0, 0]` | `[0.0, 0.0]` | `[5.24, 5.24]` | decisive cold-start discovery split after V18: use the upstream polynomial reference-motion imitation path as a gait seed, with vanilla dynamics and the same x=0.04 command gate. The reference data's nearest positive dx is about 0.074, so this phase tests whether reference-gait structure lets PPO refine any coherent low-command forward motion instead of discovering gait from scratch. |

## Commands

### phase1_reference_imitation_seed_x004

- restore_checkpoint: `None`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/01_phase1_reference_imitation_seed_x004 --platform gpu --timeout-s 3600 --num-timesteps 320000 --export-min-step 1 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0002 --actuator-tracking-scale 0 --tracking-lin-vel-scale 24 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0015 --forward-progress-scale 24 --forward-shortfall-scale -45 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.55 --forward-overshoot-scale -2 --forward-overshoot-allowed-ratio 1.7 --forward-wrong-direction-scale -80 --forward-wrong-direction-allowed-reverse-ratio 0 --command-progress-scale 10 --command-progress-shortfall-scale -45 --command-progress-failure-scale -140 --command-progress-required-ratio 0.45 --command-progress-warmup-steps 10 --command-progress-failure-min-ratio 0.2 --command-progress-failure-warmup-steps 70 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0 --reward-clip-min -20 --reward-clip-max 10000 --action-rate-scale -0.006 --action-magnitude-scale -0.001 --stand-still-scale -1 --orientation-scale -0.04 --base-height-scale -0.25 --forward-pitch-scale -0.06 --forward-pitch-rate-scale -0.006 --forward-contact-support-scale -0.12 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0.02 --alive-scale 0 --imitation-scale 4 --lin-vel-x-min 0.035 --lin-vel-x-max 0.045 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.0001 --ppo-entropy-cost 0.012 --ppo-clipping-epsilon 0.1 --ppo-max-grad-norm 0.7 --command-progress-failure-enable --disable-actuator-bridge
```

## Next Gate

V19 is a reference-imitation discovery split, so the first gate is the built-in multi-seed phase gate:

- command_x: `0.04`
- bridge_mode: `vanilla`
- pass condition: coherent positive forward tracking across seeds, not fall-count alone
- hold condition: standstill, reverse, collapse, or command-progress failure across the seed distribution

Do not run x=0.08, fitted bridge, or robot validation until the x=0.04 seeded gait passes across seeds.
