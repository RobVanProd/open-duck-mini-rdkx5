# Staged Curriculum Training Plan

Offline-only plan. This does not touch the robot, SSH, deploy, or modify
runtime behavior. Training only runs when the planner is invoked with
`--run`.

status: `DRY_RUN`
platform: `gpu`
recipe: `movement_bootstrap_v14`
output_root: `/tmp/open_duck_staged_curriculum`

## Why

Current candidates are either aggressive and unsafe, or stable and nearly
stationary at `x=0.08`. The staged recipe bootstraps forward motion before
tightening actuator realism.

`movement_bootstrap_v14` responds to the corrected V13 replay: V13's signed progress failure and negative reward were active, but PPO still learned a short-lived low-motion behavior under the fitted bridge from step zero. V14 therefore uses a mild-bridge motion-discovery phase first, then transfers to the fitted actuator envelope only if the phase gate shows real forward progress.

## Phases

| phase | bridge | timesteps | x command range | shortfall | window progress | failure penalty | delay | tau | velocity limit | purpose |
|---|---|---:|---|---|---|---|---|---|---|---|
| `phase1_mild_bridge_motion_discovery` | yes | 280000 | `[0.04, 0.06]` | `{'scale': -24.0, 'required_ratio': 0.45}` | `{'scale': 18.0, 'shortfall': -32.0, 'required_ratio': 0.45, 'warmup_steps': 20, 'failure': True, 'failure_min_ratio': 0.2}` | `{'scale': -80.0, 'clip_min': -8.0}` | `[1, 3]` | `[0.03, 0.08]` | `[3.8, 5.24]` | V13 proved signed progress failure works but did not discover motion under the fitted bridge from step zero. Start with a mild bridge so PPO can find low-command forward motion before the full measured actuator envelope is enforced. |
| `phase2_fitted_bridge_motion_transfer` | yes | 260000 | `[0.04, 0.06]` | `{'scale': -28.0, 'required_ratio': 0.45}` | `{'scale': 20.0, 'shortfall': -38.0, 'required_ratio': 0.45, 'warmup_steps': 20, 'failure': True, 'failure_min_ratio': 0.25}` | `{'scale': -120.0, 'clip_min': -10.0}` | `[2, 5]` | `[0.05, 0.12]` | `[2.5, 3.75]` | Transfer the discovered low-command gait into the fitted actuator envelope while keeping progress failure active. This phase should be skipped automatically if phase 1 freezes or fails its gate. |
| `phase3_expand_command_with_fitted_bridge` | yes | 220000 | `[0.04, 0.08]` | `{'scale': -30.0, 'required_ratio': 0.42}` | `{'scale': 18.0, 'shortfall': -42.0, 'required_ratio': 0.42, 'warmup_steps': 20, 'failure': True, 'failure_min_ratio': 0.3}` | `{'scale': -150.0, 'clip_min': -10.0}` | `[3, 6]` | `[0.06, 0.14]` | `[2.5, 3.75]` | Expand toward x=0.08 only after low-command fitted-bridge motion survives. Keep progress failure and wrong-direction pressure active so stability cannot be bought by freezing or backing up. |

## Commands

### phase1_mild_bridge_motion_discovery

- restore_checkpoint: `None`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/01_phase1_mild_bridge_motion_discovery --platform gpu --timeout-s 3600 --num-timesteps 280000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0008 --actuator-tracking-scale -0.05 --tracking-lin-vel-scale 36 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0012 --forward-progress-scale 16 --forward-shortfall-scale -24 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.45 --forward-overshoot-scale -3 --forward-overshoot-allowed-ratio 1.6 --forward-wrong-direction-scale -18 --forward-wrong-direction-allowed-reverse-ratio 0 --command-progress-scale 18 --command-progress-shortfall-scale -32 --command-progress-failure-scale -80 --command-progress-required-ratio 0.45 --command-progress-warmup-steps 20 --command-progress-failure-min-ratio 0.2 --command-progress-failure-warmup-steps 120 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0 --reward-clip-min -8 --reward-clip-max 10000 --action-rate-scale -0.006 --action-magnitude-scale -0.0015 --stand-still-scale -1.2 --orientation-scale -0.04 --base-height-scale -0.35 --forward-pitch-scale -0.06 --forward-pitch-rate-scale -0.006 --forward-contact-support-scale -0.12 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0.02 --alive-scale 0.01 --imitation-scale 0.2 --lin-vel-x-min 0.04 --lin-vel-x-max 0.06 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.00012 --ppo-clipping-epsilon 0.12 --ppo-max-grad-norm 0.7 --command-progress-failure-enable --actuator-bridge-delay-min-ticks 1 --actuator-bridge-delay-max-ticks 3 --actuator-bridge-tau-min-s 0.03 --actuator-bridge-tau-max-s 0.08 --actuator-bridge-velocity-limit-min-rad-s 3.8 --actuator-bridge-velocity-limit-max-rad-s 5.24 --actuator-bridge-per-joint-variation 0.15
```

### phase2_fitted_bridge_motion_transfer

- restore_checkpoint: `<latest_checkpoint_from_phase_1>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/02_phase2_fitted_bridge_motion_transfer --platform gpu --timeout-s 3600 --num-timesteps 260000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.001 --actuator-tracking-scale -0.08 --tracking-lin-vel-scale 38 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.001 --forward-progress-scale 16 --forward-shortfall-scale -28 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.45 --forward-overshoot-scale -4 --forward-overshoot-allowed-ratio 1.45 --forward-wrong-direction-scale -20 --forward-wrong-direction-allowed-reverse-ratio 0 --command-progress-scale 20 --command-progress-shortfall-scale -38 --command-progress-failure-scale -120 --command-progress-required-ratio 0.45 --command-progress-warmup-steps 20 --command-progress-failure-min-ratio 0.25 --command-progress-failure-warmup-steps 100 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0 --reward-clip-min -10 --reward-clip-max 10000 --action-rate-scale -0.009 --action-magnitude-scale -0.002 --stand-still-scale -1.2 --orientation-scale -0.05 --base-height-scale -0.45 --forward-pitch-scale -0.08 --forward-pitch-rate-scale -0.008 --forward-contact-support-scale -0.18 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0.02 --alive-scale 0.01 --imitation-scale 0.14 --lin-vel-x-min 0.04 --lin-vel-x-max 0.06 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.00008 --ppo-clipping-epsilon 0.08 --ppo-max-grad-norm 0.65 --command-progress-failure-enable --actuator-bridge-delay-min-ticks 2 --actuator-bridge-delay-max-ticks 5 --actuator-bridge-tau-min-s 0.05 --actuator-bridge-tau-max-s 0.12 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_1>'
```

### phase3_expand_command_with_fitted_bridge

- restore_checkpoint: `<latest_checkpoint_from_phase_2>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/03_phase3_expand_command_with_fitted_bridge --platform gpu --timeout-s 3600 --num-timesteps 220000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0013 --actuator-tracking-scale -0.12 --tracking-lin-vel-scale 36 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.001 --forward-progress-scale 14 --forward-shortfall-scale -30 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.42 --forward-overshoot-scale -5 --forward-overshoot-allowed-ratio 1.35 --forward-wrong-direction-scale -22 --forward-wrong-direction-allowed-reverse-ratio 0 --command-progress-scale 18 --command-progress-shortfall-scale -42 --command-progress-failure-scale -150 --command-progress-required-ratio 0.42 --command-progress-warmup-steps 20 --command-progress-failure-min-ratio 0.3 --command-progress-failure-warmup-steps 120 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0 --reward-clip-min -10 --reward-clip-max 10000 --action-rate-scale -0.014 --action-magnitude-scale -0.003 --stand-still-scale -1.1 --orientation-scale -0.08 --base-height-scale -0.65 --forward-pitch-scale -0.14 --forward-pitch-rate-scale -0.014 --forward-contact-support-scale -0.3 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0.03 --alive-scale 0.01 --imitation-scale 0.1 --lin-vel-x-min 0.04 --lin-vel-x-max 0.08 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.00005 --ppo-clipping-epsilon 0.06 --ppo-max-grad-norm 0.6 --command-progress-failure-enable --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_2>'
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
