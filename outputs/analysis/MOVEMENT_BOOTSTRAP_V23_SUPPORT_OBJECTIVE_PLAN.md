# Staged Curriculum Training Plan

Offline-only plan. This does not touch the robot, SSH, deploy, or modify
runtime behavior. Training only runs when the planner is invoked with
`--run`.

status: `DRY_RUN`
platform: `gpu`
recipe: `movement_bootstrap_v23`
output_root: `/tmp/open_duck_staged_curriculum`

## Why

Current candidates are either aggressive and unsafe, or stable and nearly
stationary at `x=0.08`. The staged recipe bootstraps forward motion before
tightening actuator realism.

`movement_bootstrap_v23` is the first explicit contact/weight-transfer learner after the target-source branch held. The direct rollout and optimizer evidence showed persistent double support when forward stepping needs single support, so V23 removes the soft prior and tests whether rewarding forward single support while penalizing double-support dwell can create low-command weight transfer at x=0.04. It must not progress to x=0.08, fitted bridge, or robot validation unless the multi-seed x=0.04 gate shows coherent forward motion and contact alternation.

## Phases

| phase | bridge | gate bridge | timesteps | x command range | shortfall | window progress | failure penalty | delay | tau | velocity limit | purpose |
|---|---|---|---:|---|---|---|---|---|---|---|---|
| `phase1_explicit_single_support_probe` | no | `vanilla` | 180000 | `[0.035, 0.045]` | `{'scale': -42.0, 'required_ratio': 0.5}` | `{'scale': 8.0, 'shortfall': -42.0, 'required_ratio': 0.4, 'warmup_steps': 10, 'failure': True, 'failure_min_ratio': 0.18}` | `{'scale': -150.0, 'clip_min': -20.0}` | `[0, 0]` | `[0.0, 0.0]` | `[5.24, 5.24]` | diagnostic after the target-source branch held on persistent double-support/contact mismatch. This phase removes soft-prior target chasing and tests whether explicit forward single-support reward plus double-support dwell cost can teach low-command weight transfer before any actuator bridge, x=0.08 expansion, or robot validation. |

## Commands

### phase1_explicit_single_support_probe

- restore_checkpoint: `None`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/01_phase1_explicit_single_support_probe --platform gpu --timeout-s 3600 --num-timesteps 180000 --export-min-step 1 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0002 --actuator-tracking-scale 0 --tracking-lin-vel-scale 22 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0015 --forward-progress-scale 22 --forward-shortfall-scale -42 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.5 --forward-overshoot-scale -2 --forward-overshoot-allowed-ratio 1.6 --forward-wrong-direction-scale -90 --forward-wrong-direction-allowed-reverse-ratio 0 --command-progress-scale 8 --command-progress-shortfall-scale -42 --command-progress-failure-scale -150 --command-progress-required-ratio 0.4 --command-progress-warmup-steps 10 --command-progress-failure-min-ratio 0.18 --command-progress-failure-warmup-steps 70 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0 --reward-clip-min -20 --reward-clip-max 10000 --action-rate-scale -0.004 --action-magnitude-scale -0.0008 --stand-still-scale -1 --orientation-scale -0.04 --base-height-scale -0.25 --forward-pitch-scale -0.05 --forward-pitch-rate-scale -0.005 --forward-contact-support-scale -0.06 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0 --forward-single-support-scale 1 --forward-double-support-scale -1 --alive-scale 0 --imitation-scale 0 --lin-vel-x-min 0.035 --lin-vel-x-max 0.045 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.00007 --ppo-entropy-cost 0.01 --ppo-clipping-epsilon 0.08 --ppo-max-grad-norm 0.65 --command-progress-failure-enable --disable-actuator-bridge
```

## Next Gate

movement_bootstrap_v23 is an x=0.04 discovery split, so the first gate is the built-in multi-seed phase gate:

- command_x: `0.04`
- bridge_mode: `vanilla`
- pass condition: coherent positive forward tracking across seeds, not fall-count alone
- hold condition: standstill, reverse, collapse, or command-progress failure across the seed distribution

Do not run x=0.08, fitted bridge, or robot validation until the x=0.04 seeded gait passes across seeds.
