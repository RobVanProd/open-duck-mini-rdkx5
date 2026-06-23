# Staged Curriculum Training Plan

Offline-only plan. This does not touch the robot, SSH, deploy, or modify
runtime behavior. Training only runs when the planner is invoked with
`--run`.

status: `DRY_RUN`
platform: `gpu`
recipe: `movement_bootstrap_v6`
output_root: `/tmp/open_duck_staged_curriculum`

## Why

Current candidates are either aggressive and unsafe, or stable and nearly
stationary at `x=0.08`. The staged recipe bootstraps forward motion before
tightening actuator realism.

`movement_bootstrap_v6` starts from the v5 phase-checkpoint finding: in-envelope x=0.08 forward motion exists but falls after about 80 samples. It keeps the fitted actuator envelope active through every phase, adds light orientation/base-height pressure, and lowers PPO update size in later phases so stability pressure is less likely to erase the moving gait.

## Phases

| phase | bridge | timesteps | x command range | shortfall | window progress | delay | tau | velocity limit | purpose |
|---|---|---:|---|---|---|---|---|---|---|
| `phase1_recover_in_envelope_motion` | yes | 350000 | `[0.06, 0.08]` | `{'scale': -5.0, 'required_ratio': 0.45}` | `{'scale': 8.0, 'shortfall': -8.0, 'required_ratio': 0.45, 'warmup_steps': 35}` | `[1, 3]` | `[0.03, 0.08]` | `[2.5, 3.75]` | recover the v5 phase-1 lead inside the measured actuator envelope instead of using a relaxed velocity budget |
| `phase2_stabilize_motion_low_step` | yes | 300000 | `[0.06, 0.08]` | `{'scale': -5.5, 'required_ratio': 0.45}` | `{'scale': 7.0, 'shortfall': -8.0, 'required_ratio': 0.45, 'warmup_steps': 35}` | `[2, 5]` | `[0.05, 0.12]` | `[2.5, 3.75]` | continue from phase 1 with small PPO updates and light orientation/base-height costs so stability cannot be bought by leaving the measured envelope |
| `phase3_hold_motion_fitted_bridge` | yes | 300000 | `[0.06, 0.08]` | `{'scale': -5.5, 'required_ratio': 0.42}` | `{'scale': 6.5, 'shortfall': -8.0, 'required_ratio': 0.42, 'warmup_steps': 35}` | `[3, 6]` | `[0.06, 0.14]` | `[2.5, 3.75]` | hold the same x=0.06-0.08 command window under fitted bridge rather than expanding the task after the gait has not stabilized |

## Commands

### phase1_recover_in_envelope_motion

- restore_checkpoint: `None`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/01_phase1_recover_in_envelope_motion --platform gpu --timeout-s 3600 --num-timesteps 350000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0015 --actuator-tracking-scale -0.12 --tracking-lin-vel-scale 30 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0015 --forward-progress-scale 7 --forward-shortfall-scale -5 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.45 --command-progress-scale 8 --command-progress-shortfall-scale -8 --command-progress-required-ratio 0.45 --command-progress-warmup-steps 35 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0.35 --command-progress-shortfall-huber-delta 0.35 --action-rate-scale -0.016 --action-magnitude-scale -0.004 --stand-still-scale -0.8 --orientation-scale 0 --base-height-scale 0 --alive-scale 0.06 --imitation-scale 0.6 --lin-vel-x-min 0.06 --lin-vel-x-max 0.08 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.0002 --ppo-clipping-epsilon 0.16 --actuator-bridge-delay-min-ticks 1 --actuator-bridge-delay-max-ticks 3 --actuator-bridge-tau-min-s 0.03 --actuator-bridge-tau-max-s 0.08 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15
```

### phase2_stabilize_motion_low_step

- restore_checkpoint: `<latest_checkpoint_from_phase_1>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/02_phase2_stabilize_motion_low_step --platform gpu --timeout-s 3600 --num-timesteps 300000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.002 --actuator-tracking-scale -0.2 --tracking-lin-vel-scale 28 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0015 --forward-progress-scale 6.5 --forward-shortfall-scale -5.5 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.45 --command-progress-scale 7 --command-progress-shortfall-scale -8 --command-progress-required-ratio 0.45 --command-progress-warmup-steps 35 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0.35 --command-progress-shortfall-huber-delta 0.35 --action-rate-scale -0.02 --action-magnitude-scale -0.005 --stand-still-scale -0.7 --orientation-scale -0.15 --base-height-scale -1 --alive-scale 0.08 --imitation-scale 0.55 --lin-vel-x-min 0.06 --lin-vel-x-max 0.08 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.00012 --ppo-clipping-epsilon 0.1 --ppo-max-grad-norm 0.8 --actuator-bridge-delay-min-ticks 2 --actuator-bridge-delay-max-ticks 5 --actuator-bridge-tau-min-s 0.05 --actuator-bridge-tau-max-s 0.12 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_1>'
```

### phase3_hold_motion_fitted_bridge

- restore_checkpoint: `<latest_checkpoint_from_phase_2>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/03_phase3_hold_motion_fitted_bridge --platform gpu --timeout-s 3600 --num-timesteps 300000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0025 --actuator-tracking-scale -0.24 --tracking-lin-vel-scale 26 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0015 --forward-progress-scale 6 --forward-shortfall-scale -5.5 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.42 --command-progress-scale 6.5 --command-progress-shortfall-scale -8 --command-progress-required-ratio 0.42 --command-progress-warmup-steps 35 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0.35 --command-progress-shortfall-huber-delta 0.35 --action-rate-scale -0.022 --action-magnitude-scale -0.006 --stand-still-scale -0.6 --orientation-scale -0.25 --base-height-scale -1.5 --alive-scale 0.1 --imitation-scale 0.5 --lin-vel-x-min 0.06 --lin-vel-x-max 0.08 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.00008 --ppo-clipping-epsilon 0.08 --ppo-max-grad-norm 0.8 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_2>'
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
