# Staged Curriculum Training Plan

Offline-only plan. This does not touch the robot, SSH, deploy, or modify
runtime behavior. Training only runs when the planner is invoked with
`--run`.

status: `DRY_RUN`
platform: `gpu`
recipe: `movement_bootstrap_v9`
output_root: `/tmp/open_duck_staged_curriculum`

## Why

Current candidates are either aggressive and unsafe, or stable and nearly
stationary at `x=0.08`. The staged recipe bootstraps forward motion before
tightening actuator realism.

`movement_bootstrap_v9` starts from the v7 anchored checkpoint again, because v8 overcorrected into standstill. It keeps the fitted actuator bridge and velocity envelope active, but uses lighter overshoot/pitch damping and stronger command-window progress pressure to search the narrow region between v7's lunge and v8's no-motion solution.

## Phases

| phase | bridge | timesteps | x command range | shortfall | window progress | delay | tau | velocity limit | purpose |
|---|---|---:|---|---|---|---|---|---|---|
| `phase1_v7_progress_recovery_light_damping` | yes | 140000 | `[0.04, 0.06]` | `{'scale': -8.0, 'required_ratio': 0.28}` | `{'scale': 11.0, 'shortfall': -12.0, 'required_ratio': 0.28, 'warmup_steps': 30}` | `[3, 6]` | `[0.06, 0.14]` | `[2.5, 3.75]` | restart from the v7 moving anchor with fitted actuator dynamics, but use much lighter overshoot/pitch damping than v8 so forward motion is not erased |
| `phase2_expand_x008_moderate_damping` | yes | 160000 | `[0.04, 0.08]` | `{'scale': -8.0, 'required_ratio': 0.3}` | `{'scale': 10.0, 'shortfall': -12.0, 'required_ratio': 0.3, 'warmup_steps': 30}` | `[3, 6]` | `[0.06, 0.14]` | `[2.5, 3.75]` | expand back to x=0.08 while increasing damping only enough to avoid the v7 lunge, keeping command-window progress dominant |
| `phase3_consolidate_progress_no_lunge` | yes | 120000 | `[0.04, 0.08]` | `{'scale': -8.0, 'required_ratio': 0.32}` | `{'scale': 9.0, 'shortfall': -11.0, 'required_ratio': 0.32, 'warmup_steps': 30}` | `[3, 6]` | `[0.06, 0.14]` | `[2.5, 3.75]` | consolidate the middle ground between v7 and v8: measurable forward progress, no lunge, no relaxation of the actuator envelope |

## Commands

### phase1_v7_progress_recovery_light_damping

- restore_checkpoint: `policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/checkpoint_2026_06_23_213846_184320`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/01_phase1_v7_progress_recovery_light_damping --platform gpu --timeout-s 3600 --num-timesteps 140000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0012 --actuator-tracking-scale -0.12 --tracking-lin-vel-scale 34 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0012 --forward-progress-scale 8.5 --forward-shortfall-scale -8 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.28 --forward-overshoot-scale -0.9 --forward-overshoot-allowed-ratio 1.9 --command-progress-scale 11 --command-progress-shortfall-scale -12 --command-progress-required-ratio 0.28 --command-progress-warmup-steps 30 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0.35 --forward-overshoot-huber-delta 0.5 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0.35 --action-rate-scale -0.016 --action-magnitude-scale -0.004 --stand-still-scale -1 --orientation-scale -0.06 --base-height-scale -0.6 --forward-pitch-scale -0.1 --forward-pitch-rate-scale -0.01 --alive-scale 0.05 --imitation-scale 0.45 --lin-vel-x-min 0.04 --lin-vel-x-max 0.06 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.00003 --ppo-clipping-epsilon 0.035 --ppo-max-grad-norm 0.45 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/checkpoint_2026_06_23_213846_184320
```

### phase2_expand_x008_moderate_damping

- restore_checkpoint: `<latest_checkpoint_from_phase_1>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/02_phase2_expand_x008_moderate_damping --platform gpu --timeout-s 3600 --num-timesteps 160000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0013 --actuator-tracking-scale -0.13 --tracking-lin-vel-scale 32 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0012 --forward-progress-scale 8 --forward-shortfall-scale -8 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.3 --forward-overshoot-scale -1.3 --forward-overshoot-allowed-ratio 1.7 --command-progress-scale 10 --command-progress-shortfall-scale -12 --command-progress-required-ratio 0.3 --command-progress-warmup-steps 30 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0.35 --forward-overshoot-huber-delta 0.5 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0.35 --action-rate-scale -0.018 --action-magnitude-scale -0.0045 --stand-still-scale -1 --orientation-scale -0.07 --base-height-scale -0.7 --forward-pitch-scale -0.16 --forward-pitch-rate-scale -0.016 --alive-scale 0.05 --imitation-scale 0.44 --lin-vel-x-min 0.04 --lin-vel-x-max 0.08 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.000025 --ppo-clipping-epsilon 0.03 --ppo-max-grad-norm 0.45 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_1>'
```

### phase3_consolidate_progress_no_lunge

- restore_checkpoint: `<latest_checkpoint_from_phase_2>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/03_phase3_consolidate_progress_no_lunge --platform gpu --timeout-s 3600 --num-timesteps 120000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0015 --actuator-tracking-scale -0.15 --tracking-lin-vel-scale 30 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0012 --forward-progress-scale 7.5 --forward-shortfall-scale -8 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.32 --forward-overshoot-scale -1.6 --forward-overshoot-allowed-ratio 1.6 --command-progress-scale 9 --command-progress-shortfall-scale -11 --command-progress-required-ratio 0.32 --command-progress-warmup-steps 30 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0.35 --forward-overshoot-huber-delta 0.5 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0.35 --action-rate-scale -0.02 --action-magnitude-scale -0.005 --stand-still-scale -1 --orientation-scale -0.08 --base-height-scale -0.8 --forward-pitch-scale -0.2 --forward-pitch-rate-scale -0.02 --alive-scale 0.05 --imitation-scale 0.43 --lin-vel-x-min 0.04 --lin-vel-x-max 0.08 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.00002 --ppo-clipping-epsilon 0.025 --ppo-max-grad-norm 0.45 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_2>'
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
