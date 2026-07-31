# Staged Curriculum Training Plan

Offline-only plan. This does not touch the robot, SSH, deploy, or modify
runtime behavior. Training only runs when the planner is invoked with
`--run`.

status: `DRY_RUN`
platform: `gpu`
recipe: `movement_bootstrap_v21`
output_root: `/tmp/open_duck_staged_curriculum`

## Why

Current candidates are either aggressive and unsafe, or stable and nearly
stationary at `x=0.08`. The staged recipe bootstraps forward motion before
tightening actuator realism.

`movement_bootstrap_v21` is the first weak-soft-prior learner. V20 showed that a matched reference did not stay coherent under PPO, and direct fragment targets were too short to use as labels. V21 keeps the fragment data as a small pitch-chain auxiliary cost only, keeps the task at x=0.04, and requires multi-seed real forward motion before any actuator-envelope or x=0.08 expansion.

## Phases

| phase | bridge | gate bridge | timesteps | x command range | shortfall | window progress | failure penalty | delay | tau | velocity limit | purpose |
|---|---|---|---:|---|---|---|---|---|---|---|---|
| `phase1_soft_prior_low_command_probe` | no | `vanilla` | 220000 | `[0.035, 0.045]` | `{'scale': -55.0, 'required_ratio': 0.55}` | `{'scale': 10.0, 'shortfall': -50.0, 'required_ratio': 0.45, 'warmup_steps': 10, 'failure': True, 'failure_min_ratio': 0.2}` | `{'scale': -150.0, 'clip_min': -20.0}` | `[0, 0]` | `[0.0, 0.0]` | `[5.24, 5.24]` | first weak-soft-prior learner after direct reference targets and raw target labels held. This phase keeps vanilla dynamics and x=0.04 only, uses the compact pitch-chain fragment prior as a small auxiliary cost, and still grades by real closed-loop forward motion rather than imitation loss. |
| `phase2_soft_prior_mild_bridge_probe` | yes | `fitted` | 160000 | `[0.035, 0.045]` | `{'scale': -45.0, 'required_ratio': 0.5}` | `{'scale': 8.0, 'shortfall': -42.0, 'required_ratio': 0.45, 'warmup_steps': 10, 'failure': True, 'failure_min_ratio': 0.18}` | `{'scale': -150.0, 'clip_min': -20.0}` | `[1, 3]` | `[0.03, 0.08]` | `[3.6, 4.7]` | only run if phase 1 passes the multi-seed x=0.04 vanilla gate. Keep the same weak prior while adding a mild actuator bridge at the same command before any fitted-envelope or x=0.08 expansion. |

## Commands

### phase1_soft_prior_low_command_probe

- restore_checkpoint: `None`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/01_phase1_soft_prior_low_command_probe --platform gpu --timeout-s 3600 --num-timesteps 220000 --export-min-step 1 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0002 --actuator-tracking-scale 0 --tracking-lin-vel-scale 26 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0015 --forward-progress-scale 28 --forward-shortfall-scale -55 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.55 --forward-overshoot-scale -2 --forward-overshoot-allowed-ratio 1.65 --forward-wrong-direction-scale -90 --forward-wrong-direction-allowed-reverse-ratio 0 --command-progress-scale 10 --command-progress-shortfall-scale -50 --command-progress-failure-scale -150 --command-progress-required-ratio 0.45 --command-progress-warmup-steps 10 --command-progress-failure-min-ratio 0.2 --command-progress-failure-warmup-steps 70 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0 --reward-clip-min -20 --reward-clip-max 10000 --action-rate-scale -0.006 --action-magnitude-scale -0.001 --stand-still-scale -1 --orientation-scale -0.04 --base-height-scale -0.28 --forward-pitch-scale -0.06 --forward-pitch-rate-scale -0.006 --forward-contact-support-scale -0.12 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0.02 --alive-scale 0 --imitation-scale 0 --lin-vel-x-min 0.035 --lin-vel-x-max 0.045 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.0001 --ppo-entropy-cost 0.014 --ppo-clipping-epsilon 0.1 --ppo-max-grad-norm 0.7 --command-progress-failure-enable --enable-soft-prior --soft-prior-config-json outputs/analysis/soft_prior_fragment_config.json --soft-prior-scale -0.025 --soft-prior-huber-delta 0.05 --soft-prior-phase-source imitation_i --disable-actuator-bridge
```

### phase2_soft_prior_mild_bridge_probe

- restore_checkpoint: `<latest_checkpoint_from_phase_1>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/02_phase2_soft_prior_mild_bridge_probe --platform gpu --timeout-s 3600 --num-timesteps 160000 --export-min-step 1 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0006 --actuator-tracking-scale -0.04 --tracking-lin-vel-scale 24 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0015 --forward-progress-scale 24 --forward-shortfall-scale -45 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.5 --forward-overshoot-scale -2.5 --forward-overshoot-allowed-ratio 1.55 --forward-wrong-direction-scale -80 --forward-wrong-direction-allowed-reverse-ratio 0 --command-progress-scale 8 --command-progress-shortfall-scale -42 --command-progress-failure-scale -150 --command-progress-required-ratio 0.45 --command-progress-warmup-steps 10 --command-progress-failure-min-ratio 0.18 --command-progress-failure-warmup-steps 80 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0 --reward-clip-min -20 --reward-clip-max 10000 --action-rate-scale -0.008 --action-magnitude-scale -0.0015 --stand-still-scale -1 --orientation-scale -0.055 --base-height-scale -0.38 --forward-pitch-scale -0.08 --forward-pitch-rate-scale -0.008 --forward-contact-support-scale -0.16 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0.02 --alive-scale 0 --imitation-scale 0 --lin-vel-x-min 0.035 --lin-vel-x-max 0.045 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.00007 --ppo-entropy-cost 0.01 --ppo-clipping-epsilon 0.09 --ppo-max-grad-norm 0.65 --command-progress-failure-enable --enable-soft-prior --soft-prior-config-json outputs/analysis/soft_prior_fragment_config.json --soft-prior-scale -0.015 --soft-prior-huber-delta 0.05 --soft-prior-phase-source imitation_i --actuator-bridge-delay-min-ticks 1 --actuator-bridge-delay-max-ticks 3 --actuator-bridge-tau-min-s 0.03 --actuator-bridge-tau-max-s 0.08 --actuator-bridge-velocity-limit-min-rad-s 3.6 --actuator-bridge-velocity-limit-max-rad-s 4.7 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_1>'
```

## Next Gate

movement_bootstrap_v21 is an x=0.04 discovery split, so the first gate is the built-in multi-seed phase gate:

- command_x: `0.04`
- bridge_mode: `vanilla`
- pass condition: coherent positive forward tracking across seeds, not fall-count alone
- hold condition: standstill, reverse, collapse, or command-progress failure across the seed distribution

Do not run x=0.08, fitted bridge, or robot validation until the x=0.04 seeded gait passes across seeds.
