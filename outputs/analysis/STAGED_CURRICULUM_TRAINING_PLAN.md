# Staged Curriculum Training Plan

Offline-only plan. This does not touch the robot, SSH, deploy, or modify
runtime behavior. Training only runs when the planner is invoked with
`--run`.

status: `DRY_RUN`
platform: `gpu`
recipe: `movement_bootstrap_v3`
output_root: `/tmp/open_duck_staged_curriculum`

## Why

Current candidates are either aggressive and unsafe, or stable and nearly
stationary at `x=0.08`. The staged recipe bootstraps forward motion before
tightening actuator realism.

The default `movement_bootstrap_v3` recipe is a follow-up to the A100
`movement_bootstrap_v2` result. It adds command-window cumulative
progress terms so the optimizer cannot satisfy a nonzero command with
brief bursts while average displacement remains near zero.

## Phases

| phase | bridge | timesteps | x command range | shortfall | window progress | delay | tau | velocity limit | purpose |
|---|---|---:|---|---|---|---|---|---|---|
| `phase1_window_progress_no_bridge` | no | 450000 | `[0.08, 0.16]` | `{'scale': -6.0, 'required_ratio': 0.65}` | `{'scale': 10.0, 'shortfall': -10.0, 'required_ratio': 0.65, 'warmup_steps': 40}` | `[0, 0]` | `[0.0, 0.0]` | `[5.24, 5.24]` | force sustained command-window displacement before adding actuator constraints |
| `phase2_window_progress_mild_bridge` | yes | 350000 | `[0.07, 0.14]` | `{'scale': -6.0, 'required_ratio': 0.65}` | `{'scale': 8.0, 'shortfall': -8.0, 'required_ratio': 0.6, 'warmup_steps': 40}` | `[1, 2]` | `[0.02, 0.05]` | `[4.5, 5.24]` | preserve sustained displacement while introducing mild actuator delay and target smoothing |
| `phase3_window_progress_fitted_bridge` | yes | 400000 | `[0.06, 0.12]` | `{'scale': -5.0, 'required_ratio': 0.6}` | `{'scale': 6.0, 'shortfall': -8.0, 'required_ratio': 0.6, 'warmup_steps': 40}` | `[3, 6]` | `[0.06, 0.14]` | `[3.0, 4.7]` | train under the fitted actuator envelope while making sustained forward progress a non-negotiable objective |

## Commands

### phase1_window_progress_no_bridge

- restore_checkpoint: `None`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/01_phase1_window_progress_no_bridge --platform gpu --timeout-s 3600 --num-timesteps 450000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale 0 --actuator-tracking-scale 0 --tracking-lin-vel-scale 26 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.00125 --forward-progress-scale 8 --forward-shortfall-scale -6 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.65 --command-progress-scale 10 --command-progress-shortfall-scale -10 --command-progress-required-ratio 0.65 --command-progress-warmup-steps 40 --action-rate-scale -0.003 --action-magnitude-scale -0.001 --stand-still-scale -1 --alive-scale 0.03 --imitation-scale 0.85 --lin-vel-x-min 0.08 --lin-vel-x-max 0.16 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --disable-actuator-bridge
```

### phase2_window_progress_mild_bridge

- restore_checkpoint: `<latest_checkpoint_from_phase_1>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/02_phase2_window_progress_mild_bridge --platform gpu --timeout-s 3600 --num-timesteps 350000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0015 --actuator-tracking-scale -0.1 --tracking-lin-vel-scale 28 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.00125 --forward-progress-scale 7 --forward-shortfall-scale -6 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.65 --command-progress-scale 8 --command-progress-shortfall-scale -8 --command-progress-required-ratio 0.6 --command-progress-warmup-steps 40 --action-rate-scale -0.015 --action-magnitude-scale -0.004 --stand-still-scale -0.8 --alive-scale 0.08 --imitation-scale 0.65 --lin-vel-x-min 0.07 --lin-vel-x-max 0.14 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --actuator-bridge-delay-min-ticks 1 --actuator-bridge-delay-max-ticks 2 --actuator-bridge-tau-min-s 0.02 --actuator-bridge-tau-max-s 0.05 --actuator-bridge-velocity-limit-min-rad-s 4.5 --actuator-bridge-velocity-limit-max-rad-s 5.24 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_1>'
```

### phase3_window_progress_fitted_bridge

- restore_checkpoint: `<latest_checkpoint_from_phase_2>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/03_phase3_window_progress_fitted_bridge --platform gpu --timeout-s 3600 --num-timesteps 400000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.004 --actuator-tracking-scale -0.35 --tracking-lin-vel-scale 26 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.00125 --forward-progress-scale 6 --forward-shortfall-scale -5 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.6 --command-progress-scale 6 --command-progress-shortfall-scale -8 --command-progress-required-ratio 0.6 --command-progress-warmup-steps 40 --action-rate-scale -0.03 --action-magnitude-scale -0.008 --stand-still-scale -0.5 --alive-scale 0.12 --imitation-scale 0.45 --lin-vel-x-min 0.06 --lin-vel-x-max 0.12 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 3 --actuator-bridge-velocity-limit-max-rad-s 4.7 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_2>'
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
