# Staged Curriculum Training Plan

Offline-only plan. This does not touch the robot, SSH, deploy, or modify
runtime behavior. Training only runs when the planner is invoked with
`--run`.

status: `DRY_RUN`
platform: `gpu`
recipe: `movement_bootstrap_v5`
output_root: `/tmp/open_duck_staged_curriculum`

## Why

Current candidates are either aggressive and unsafe, or stable and nearly
stationary at `x=0.08`. The staged recipe bootstraps forward motion before
tightening actuator realism.

The default `movement_bootstrap_v5` recipe follows the command
feasibility curve: `BEST_WALK_ONNX_2` stays below the actuator target
velocity envelope through roughly `x=0.06`, then crosses it at `x=0.08`.
V5 therefore learns low-command motion first, using Huber-shaped
smoothness costs, before expanding toward `x=0.08`.

## Phases

| phase | bridge | timesteps | x command range | shortfall | window progress | delay | tau | velocity limit | purpose |
|---|---|---:|---|---|---|---|---|---|---|
| `phase1_feasible_low_command_mild_bridge` | yes | 350000 | `[0.04, 0.06]` | `{'scale': -5.0, 'required_ratio': 0.5}` | `{'scale': 7.0, 'shortfall': -7.0, 'required_ratio': 0.5, 'warmup_steps': 40}` | `[1, 3]` | `[0.02, 0.06]` | `[4.0, 5.24]` | learn visible forward motion in the target-rate-feasible x=0.04-0.06 range before pushing toward x=0.08 |
| `phase2_feasible_low_command_fitted_bridge` | yes | 450000 | `[0.04, 0.06]` | `{'scale': -5.0, 'required_ratio': 0.5}` | `{'scale': 6.0, 'shortfall': -7.0, 'required_ratio': 0.5, 'warmup_steps': 40}` | `[3, 6]` | `[0.06, 0.14]` | `[2.5, 3.75]` | preserve low-command forward progress while moving to the robust fitted actuator envelope |
| `phase3_expand_toward_x008_fitted_bridge` | yes | 450000 | `[0.04, 0.08]` | `{'scale': -5.0, 'required_ratio': 0.45}` | `{'scale': 5.0, 'shortfall': -7.0, 'required_ratio': 0.45, 'warmup_steps': 40}` | `[3, 6]` | `[0.06, 0.14]` | `[2.5, 3.75]` | expand the command window toward x=0.08 only after the lower feasible range has a moving gait |

## Commands

### phase1_feasible_low_command_mild_bridge

- restore_checkpoint: `None`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/01_phase1_feasible_low_command_mild_bridge --platform gpu --timeout-s 3600 --num-timesteps 350000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0015 --actuator-tracking-scale -0.12 --tracking-lin-vel-scale 28 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0015 --forward-progress-scale 6 --forward-shortfall-scale -5 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.5 --command-progress-scale 7 --command-progress-shortfall-scale -7 --command-progress-required-ratio 0.5 --command-progress-warmup-steps 40 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0.35 --command-progress-shortfall-huber-delta 0.35 --action-rate-scale -0.018 --action-magnitude-scale -0.004 --stand-still-scale -0.8 --alive-scale 0.08 --imitation-scale 0.6 --lin-vel-x-min 0.04 --lin-vel-x-max 0.06 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --actuator-bridge-delay-min-ticks 1 --actuator-bridge-delay-max-ticks 3 --actuator-bridge-tau-min-s 0.02 --actuator-bridge-tau-max-s 0.06 --actuator-bridge-velocity-limit-min-rad-s 4 --actuator-bridge-velocity-limit-max-rad-s 5.24 --actuator-bridge-per-joint-variation 0.15
```

### phase2_feasible_low_command_fitted_bridge

- restore_checkpoint: `<latest_checkpoint_from_phase_1>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/02_phase2_feasible_low_command_fitted_bridge --platform gpu --timeout-s 3600 --num-timesteps 450000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.003 --actuator-tracking-scale -0.28 --tracking-lin-vel-scale 26 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0015 --forward-progress-scale 5 --forward-shortfall-scale -5 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.5 --command-progress-scale 6 --command-progress-shortfall-scale -7 --command-progress-required-ratio 0.5 --command-progress-warmup-steps 40 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0.35 --command-progress-shortfall-huber-delta 0.35 --action-rate-scale -0.026 --action-magnitude-scale -0.006 --stand-still-scale -0.6 --alive-scale 0.12 --imitation-scale 0.5 --lin-vel-x-min 0.04 --lin-vel-x-max 0.06 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_1>'
```

### phase3_expand_toward_x008_fitted_bridge

- restore_checkpoint: `<latest_checkpoint_from_phase_2>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/03_phase3_expand_toward_x008_fitted_bridge --platform gpu --timeout-s 3600 --num-timesteps 450000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.004 --actuator-tracking-scale -0.32 --tracking-lin-vel-scale 24 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0015 --forward-progress-scale 4.5 --forward-shortfall-scale -5 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.45 --command-progress-scale 5 --command-progress-shortfall-scale -7 --command-progress-required-ratio 0.45 --command-progress-warmup-steps 40 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0.35 --command-progress-shortfall-huber-delta 0.35 --action-rate-scale -0.03 --action-magnitude-scale -0.008 --stand-still-scale -0.5 --alive-scale 0.14 --imitation-scale 0.45 --lin-vel-x-min 0.04 --lin-vel-x-max 0.08 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_2>'
```

## Next Gate

After a staged run, evaluate the final ONNX with:

```bash
JAX_PLATFORMS=cpu ../envs/open-duck-playground/bin/python tools/eval_policy_with_actuator_bridge.py \
  --mode closed-loop-sim --eval-role candidate \
  --policy <final_candidate.onnx> \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --command-x 0.0 --duration 15 --bridge-mode all --jax-platform cpu \
  --output-dir outputs/analysis/<candidate>_gate_x0
```

Then repeat with `--command-x 0.08`. Robot validation remains blocked until
both gates pass.
