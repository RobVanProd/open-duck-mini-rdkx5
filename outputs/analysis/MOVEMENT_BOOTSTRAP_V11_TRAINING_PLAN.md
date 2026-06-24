# Staged Curriculum Training Plan

Offline-only plan. This does not touch the robot, SSH, deploy, or modify
runtime behavior. Training only runs when the planner is invoked with
`--run`.

status: `DRY_RUN`
platform: `gpu`
recipe: `movement_bootstrap_v11`
output_root: `/tmp/open_duck_staged_curriculum`

## Why

Current candidates are either aggressive and unsafe, or stable and nearly
stationary at `x=0.08`. The staged recipe bootstraps forward motion before
tightening actuator realism.

`movement_bootstrap_v11` starts a fresh hard-progress-floor lineage after V10 hit the pre-committed exit condition. It does not restore from the V7/V9 anchor by default. The recipe removes Huber smoothing from the forward shortfall and command-window shortfall floors so zero or reverse progress is expensive enough to compete with the safe standstill basin.

## Phases

| phase | bridge | timesteps | x command range | shortfall | window progress | delay | tau | velocity limit | purpose |
|---|---|---:|---|---|---|---|---|---|---|
| `phase1_fresh_hard_progress_floor_low_command` | yes | 260000 | `[0.04, 0.06]` | `{'scale': -36.0, 'required_ratio': 0.55}` | `{'scale': 24.0, 'shortfall': -50.0, 'required_ratio': 0.55, 'warmup_steps': 20}` | `[2, 5]` | `[0.05, 0.12]` | `[2.5, 3.75]` | start a fresh lineage instead of restoring the fragile V7/V9/V10 anchor. Use a hard non-Huberized forward-progress floor in the x=0.04-0.06 range so standing still cannot satisfy the objective. |
| `phase2_fresh_expand_command_keep_progress_floor` | yes | 280000 | `[0.04, 0.08]` | `{'scale': -34.0, 'required_ratio': 0.5}` | `{'scale': 22.0, 'shortfall': -48.0, 'required_ratio': 0.5, 'warmup_steps': 20}` | `[3, 6]` | `[0.06, 0.14]` | `[2.5, 3.75]` | expand toward x=0.08 after the hard progress floor has made forward motion dominant. Keep the fitted actuator envelope fixed and retain strong wrong-direction pressure. |
| `phase3_fresh_stability_without_freeze` | yes | 220000 | `[0.04, 0.08]` | `{'scale': -30.0, 'required_ratio': 0.45}` | `{'scale': 18.0, 'shortfall': -42.0, 'required_ratio': 0.45, 'warmup_steps': 20}` | `[3, 6]` | `[0.06, 0.14]` | `[2.5, 3.75]` | add stability margin only after forward motion is established. Keep hard progress and wrong-direction floors active so stability cannot be purchased by freezing or reversing. |

## Commands

### phase1_fresh_hard_progress_floor_low_command

- restore_checkpoint: `None`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/01_phase1_fresh_hard_progress_floor_low_command --platform gpu --timeout-s 3600 --num-timesteps 260000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.001 --actuator-tracking-scale -0.08 --tracking-lin-vel-scale 42 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0009 --forward-progress-scale 18 --forward-shortfall-scale -36 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.55 --forward-overshoot-scale -4 --forward-overshoot-allowed-ratio 1.45 --forward-wrong-direction-scale -20 --forward-wrong-direction-allowed-reverse-ratio 0 --command-progress-scale 24 --command-progress-shortfall-scale -50 --command-progress-required-ratio 0.55 --command-progress-warmup-steps 20 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0 --action-rate-scale -0.01 --action-magnitude-scale -0.0025 --stand-still-scale -1.4 --orientation-scale -0.05 --base-height-scale -0.45 --forward-pitch-scale -0.08 --forward-pitch-rate-scale -0.008 --forward-contact-support-scale -0.2 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0.02 --alive-scale 0.02 --imitation-scale 0.08 --lin-vel-x-min 0.04 --lin-vel-x-max 0.06 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.00012 --ppo-clipping-epsilon 0.12 --ppo-max-grad-norm 0.7 --actuator-bridge-delay-min-ticks 2 --actuator-bridge-delay-max-ticks 5 --actuator-bridge-tau-min-s 0.05 --actuator-bridge-tau-max-s 0.12 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15
```

### phase2_fresh_expand_command_keep_progress_floor

- restore_checkpoint: `<latest_checkpoint_from_phase_1>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/02_phase2_fresh_expand_command_keep_progress_floor --platform gpu --timeout-s 3600 --num-timesteps 280000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0012 --actuator-tracking-scale -0.1 --tracking-lin-vel-scale 40 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0009 --forward-progress-scale 16 --forward-shortfall-scale -34 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.5 --forward-overshoot-scale -5 --forward-overshoot-allowed-ratio 1.35 --forward-wrong-direction-scale -22 --forward-wrong-direction-allowed-reverse-ratio 0 --command-progress-scale 22 --command-progress-shortfall-scale -48 --command-progress-required-ratio 0.5 --command-progress-warmup-steps 20 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0 --action-rate-scale -0.012 --action-magnitude-scale -0.003 --stand-still-scale -1.3 --orientation-scale -0.06 --base-height-scale -0.55 --forward-pitch-scale -0.1 --forward-pitch-rate-scale -0.01 --forward-contact-support-scale -0.25 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0.02 --alive-scale 0.02 --imitation-scale 0.06 --lin-vel-x-min 0.04 --lin-vel-x-max 0.08 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.00008 --ppo-clipping-epsilon 0.08 --ppo-max-grad-norm 0.7 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_1>'
```

### phase3_fresh_stability_without_freeze

- restore_checkpoint: `<latest_checkpoint_from_phase_2>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/03_phase3_fresh_stability_without_freeze --platform gpu --timeout-s 3600 --num-timesteps 220000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0015 --actuator-tracking-scale -0.14 --tracking-lin-vel-scale 36 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.001 --forward-progress-scale 14 --forward-shortfall-scale -30 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.45 --forward-overshoot-scale -6 --forward-overshoot-allowed-ratio 1.3 --forward-wrong-direction-scale -22 --forward-wrong-direction-allowed-reverse-ratio 0 --command-progress-scale 18 --command-progress-shortfall-scale -42 --command-progress-required-ratio 0.45 --command-progress-warmup-steps 20 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0 --action-rate-scale -0.018 --action-magnitude-scale -0.004 --stand-still-scale -1.2 --orientation-scale -0.1 --base-height-scale -0.85 --forward-pitch-scale -0.18 --forward-pitch-rate-scale -0.018 --forward-contact-support-scale -0.4 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0.04 --alive-scale 0.02 --imitation-scale 0.05 --lin-vel-x-min 0.04 --lin-vel-x-max 0.08 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.00005 --ppo-clipping-epsilon 0.05 --ppo-max-grad-norm 0.6 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_2>'
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
