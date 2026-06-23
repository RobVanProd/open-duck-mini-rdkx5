# Staged Curriculum Training Plan

Offline-only plan. This does not touch the robot, SSH, deploy, or modify
runtime behavior. Training only runs when the planner is invoked with
`--run`.

status: `DRY_RUN`
platform: `gpu`
recipe: `movement_bootstrap_v4`
output_root: `/tmp/open_duck_staged_curriculum`

## Why

Current candidates are either aggressive and unsafe, or stable and nearly
stationary at `x=0.08`. The staged recipe bootstraps forward motion before
tightening actuator realism.

The default `movement_bootstrap_v4` recipe follows the A100
`movement_bootstrap_v3` result. V3 completed training but failed the
fitted-bridge `x=0.0` gate, so V4 first recovers fitted-bridge
zero-command stability before reintroducing low positive commands.

## Phases

| phase | bridge | timesteps | x command range | shortfall | window progress | delay | tau | velocity limit | purpose |
|---|---|---:|---|---|---|---|---|---|---|
| `phase1_fitted_bridge_x0_stability` | yes | 300000 | `[0.0, 0.0]` | `{'scale': 0.0, 'required_ratio': 0.0}` | `{'scale': 0.0, 'shortfall': 0.0, 'required_ratio': 0.0, 'warmup_steps': 50}` | `[3, 6]` | `[0.06, 0.14]` | `[3.0, 4.7]` | recover zero-command stability under the fitted actuator bridge before asking for forward motion |
| `phase2_low_command_mild_bridge` | yes | 350000 | `[0.04, 0.1]` | `{'scale': -4.0, 'required_ratio': 0.45}` | `{'scale': 5.0, 'shortfall': -5.0, 'required_ratio': 0.45, 'warmup_steps': 50}` | `[1, 3]` | `[0.02, 0.06]` | `[4.2, 5.24]` | introduce low positive commands after the stable x0 prior, while using only mild actuator constraints |
| `phase3_fitted_bridge_stable_progress` | yes | 450000 | `[0.04, 0.1]` | `{'scale': -4.0, 'required_ratio': 0.45}` | `{'scale': 4.0, 'shortfall': -5.0, 'required_ratio': 0.45, 'warmup_steps': 50}` | `[3, 6]` | `[0.06, 0.14]` | `[3.0, 4.7]` | restore the fitted actuator envelope while preserving both x0 stability and low-command forward progress |

## Commands

### phase1_fitted_bridge_x0_stability

- restore_checkpoint: `None`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/01_phase1_fitted_bridge_x0_stability --platform gpu --timeout-s 3600 --num-timesteps 300000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.004 --actuator-tracking-scale -0.45 --tracking-lin-vel-scale 12 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0025 --forward-progress-scale 0 --forward-shortfall-scale 0 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0 --command-progress-scale 0 --command-progress-shortfall-scale 0 --command-progress-required-ratio 0 --command-progress-warmup-steps 50 --action-rate-scale -0.04 --action-magnitude-scale -0.012 --stand-still-scale -1.5 --alive-scale 0.25 --imitation-scale 0.8 --lin-vel-x-min 0 --lin-vel-x-max 0 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 1 --head-range-factor 0.25 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 3 --actuator-bridge-velocity-limit-max-rad-s 4.7 --actuator-bridge-per-joint-variation 0.15
```

### phase2_low_command_mild_bridge

- restore_checkpoint: `<latest_checkpoint_from_phase_1>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/02_phase2_low_command_mild_bridge --platform gpu --timeout-s 3600 --num-timesteps 350000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.002 --actuator-tracking-scale -0.18 --tracking-lin-vel-scale 24 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0015 --forward-progress-scale 5 --forward-shortfall-scale -4 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.45 --command-progress-scale 5 --command-progress-shortfall-scale -5 --command-progress-required-ratio 0.45 --command-progress-warmup-steps 50 --action-rate-scale -0.02 --action-magnitude-scale -0.006 --stand-still-scale -0.6 --alive-scale 0.12 --imitation-scale 0.65 --lin-vel-x-min 0.04 --lin-vel-x-max 0.1 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --actuator-bridge-delay-min-ticks 1 --actuator-bridge-delay-max-ticks 3 --actuator-bridge-tau-min-s 0.02 --actuator-bridge-tau-max-s 0.06 --actuator-bridge-velocity-limit-min-rad-s 4.2 --actuator-bridge-velocity-limit-max-rad-s 5.24 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_1>'
```

### phase3_fitted_bridge_stable_progress

- restore_checkpoint: `<latest_checkpoint_from_phase_2>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/03_phase3_fitted_bridge_stable_progress --platform gpu --timeout-s 3600 --num-timesteps 450000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.004 --actuator-tracking-scale -0.35 --tracking-lin-vel-scale 22 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0015 --forward-progress-scale 4 --forward-shortfall-scale -4 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.45 --command-progress-scale 4 --command-progress-shortfall-scale -5 --command-progress-required-ratio 0.45 --command-progress-warmup-steps 50 --action-rate-scale -0.035 --action-magnitude-scale -0.01 --stand-still-scale -0.6 --alive-scale 0.16 --imitation-scale 0.55 --lin-vel-x-min 0.04 --lin-vel-x-max 0.1 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0.1 --head-range-factor 0.25 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 3 --actuator-bridge-velocity-limit-max-rad-s 4.7 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_2>'
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
