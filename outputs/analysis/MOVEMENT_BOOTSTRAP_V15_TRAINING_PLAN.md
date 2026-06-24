# Staged Curriculum Training Plan

Offline-only plan. This does not touch the robot, SSH, deploy, or modify
runtime behavior. Training only runs when the planner is invoked with
`--run`.

status: `DRY_RUN`
platform: `gpu`
recipe: `movement_bootstrap_v15`
output_root: `/tmp/open_duck_staged_curriculum`

## Why

Current candidates are either aggressive and unsafe, or stable and nearly
stationary at `x=0.08`. The staged recipe bootstraps forward motion before
tightening actuator realism.

`movement_bootstrap_v15` responds to the incomplete V14 A100 phase-1 run: the recovered step-102400 checkpoint was still low-motion even under a mild bridge. V15 therefore separates gait discovery from actuator transfer. Phase 1 removes the actuator bridge, alive reward, and imitation reward while raising entropy and progress pressure. If it cannot produce vanilla forward motion, later actuator-transfer phases should not run. If it does, phase 2 and phase 3 reintroduce the mild and fitted actuator envelopes.

## Phases

| phase | bridge | gate bridge | timesteps | x command range | shortfall | window progress | failure penalty | delay | tau | velocity limit | purpose |
|---|---|---|---:|---|---|---|---|---|---|---|---|
| `phase1_no_bridge_high_entropy_gait_discovery` | no | `vanilla` | 320000 | `[0.06, 0.1]` | `{'scale': -34.0, 'required_ratio': 0.5}` | `{'scale': 28.0, 'shortfall': -48.0, 'required_ratio': 0.5, 'warmup_steps': 20, 'failure': True, 'failure_min_ratio': 0.3}` | `{'scale': -180.0, 'clip_min': -12.0}` | `[0, 0]` | `[0.0, 0.0]` | `[5.24, 5.24]` | V14's partial A100 checkpoint was still low-motion under a mild bridge. Remove actuator-bridge pressure for the first phase, remove alive/imitation crutches, and raise entropy so PPO has a cleaner chance to discover any coherent positive-command gait before actuator realism is reintroduced. |
| `phase2_mild_bridge_gait_transfer` | yes | `fitted` | 260000 | `[0.05, 0.08]` | `{'scale': -34.0, 'required_ratio': 0.48}` | `{'scale': 24.0, 'shortfall': -48.0, 'required_ratio': 0.48, 'warmup_steps': 20, 'failure': True, 'failure_min_ratio': 0.3}` | `{'scale': -180.0, 'clip_min': -12.0}` | `[1, 3]` | `[0.03, 0.08]` | `[3.6, 5.24]` | Only after vanilla discovery survives, reintroduce a mild actuator bridge while preserving the progress floor. This should reveal whether the discovered gait is structurally portable before the full fitted envelope is applied. |
| `phase3_fitted_bridge_gait_consolidation` | yes | `fitted` | 240000 | `[0.04, 0.08]` | `{'scale': -34.0, 'required_ratio': 0.45}` | `{'scale': 22.0, 'shortfall': -52.0, 'required_ratio': 0.45, 'warmup_steps': 20, 'failure': True, 'failure_min_ratio': 0.32}` | `{'scale': -200.0, 'clip_min': -12.0}` | `[3, 6]` | `[0.06, 0.14]` | `[2.5, 3.75]` | Consolidate only a gait that has survived discovery and mild-bridge transfer. Keep the fitted actuator envelope, progress failure, and wrong-direction pressure active so the final policy cannot buy stability by freezing or backing up. |

## Commands

### phase1_no_bridge_high_entropy_gait_discovery

- restore_checkpoint: `None`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/01_phase1_no_bridge_high_entropy_gait_discovery --platform gpu --timeout-s 3600 --num-timesteps 320000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0002 --actuator-tracking-scale 0 --tracking-lin-vel-scale 42 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.001 --forward-progress-scale 22 --forward-shortfall-scale -34 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.5 --forward-overshoot-scale -2 --forward-overshoot-allowed-ratio 1.8 --forward-wrong-direction-scale -28 --forward-wrong-direction-allowed-reverse-ratio 0 --command-progress-scale 28 --command-progress-shortfall-scale -48 --command-progress-failure-scale -180 --command-progress-required-ratio 0.5 --command-progress-warmup-steps 20 --command-progress-failure-min-ratio 0.3 --command-progress-failure-warmup-steps 100 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0 --reward-clip-min -12 --reward-clip-max 10000 --action-rate-scale -0.003 --action-magnitude-scale -0.0005 --stand-still-scale -1.8 --orientation-scale -0.02 --base-height-scale -0.2 --forward-pitch-scale -0.03 --forward-pitch-rate-scale -0.003 --forward-contact-support-scale -0.06 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0.01 --alive-scale 0 --imitation-scale 0 --lin-vel-x-min 0.06 --lin-vel-x-max 0.1 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.00015 --ppo-entropy-cost 0.02 --ppo-clipping-epsilon 0.14 --ppo-max-grad-norm 0.8 --command-progress-failure-enable --disable-actuator-bridge
```

### phase2_mild_bridge_gait_transfer

- restore_checkpoint: `<latest_checkpoint_from_phase_1>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/02_phase2_mild_bridge_gait_transfer --platform gpu --timeout-s 3600 --num-timesteps 260000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0008 --actuator-tracking-scale -0.04 --tracking-lin-vel-scale 40 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.001 --forward-progress-scale 20 --forward-shortfall-scale -34 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.48 --forward-overshoot-scale -3 --forward-overshoot-allowed-ratio 1.6 --forward-wrong-direction-scale -26 --forward-wrong-direction-allowed-reverse-ratio 0 --command-progress-scale 24 --command-progress-shortfall-scale -48 --command-progress-failure-scale -180 --command-progress-required-ratio 0.48 --command-progress-warmup-steps 20 --command-progress-failure-min-ratio 0.3 --command-progress-failure-warmup-steps 100 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0 --reward-clip-min -12 --reward-clip-max 10000 --action-rate-scale -0.006 --action-magnitude-scale -0.0015 --stand-still-scale -1.5 --orientation-scale -0.04 --base-height-scale -0.35 --forward-pitch-scale -0.06 --forward-pitch-rate-scale -0.006 --forward-contact-support-scale -0.12 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0.02 --alive-scale 0 --imitation-scale 0.04 --lin-vel-x-min 0.05 --lin-vel-x-max 0.08 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.0001 --ppo-entropy-cost 0.01 --ppo-clipping-epsilon 0.1 --ppo-max-grad-norm 0.7 --command-progress-failure-enable --actuator-bridge-delay-min-ticks 1 --actuator-bridge-delay-max-ticks 3 --actuator-bridge-tau-min-s 0.03 --actuator-bridge-tau-max-s 0.08 --actuator-bridge-velocity-limit-min-rad-s 3.6 --actuator-bridge-velocity-limit-max-rad-s 5.24 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_1>'
```

### phase3_fitted_bridge_gait_consolidation

- restore_checkpoint: `<latest_checkpoint_from_phase_2>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum/03_phase3_fitted_bridge_gait_consolidation --platform gpu --timeout-s 3600 --num-timesteps 240000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0012 --actuator-tracking-scale -0.1 --tracking-lin-vel-scale 38 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.001 --forward-progress-scale 18 --forward-shortfall-scale -34 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.45 --forward-overshoot-scale -5 --forward-overshoot-allowed-ratio 1.35 --forward-wrong-direction-scale -28 --forward-wrong-direction-allowed-reverse-ratio 0 --command-progress-scale 22 --command-progress-shortfall-scale -52 --command-progress-failure-scale -200 --command-progress-required-ratio 0.45 --command-progress-warmup-steps 20 --command-progress-failure-min-ratio 0.32 --command-progress-failure-warmup-steps 120 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0 --reward-clip-min -12 --reward-clip-max 10000 --action-rate-scale -0.012 --action-magnitude-scale -0.003 --stand-still-scale -1.3 --orientation-scale -0.08 --base-height-scale -0.65 --forward-pitch-scale -0.14 --forward-pitch-rate-scale -0.014 --forward-contact-support-scale -0.3 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0.03 --alive-scale 0 --imitation-scale 0.04 --lin-vel-x-min 0.04 --lin-vel-x-max 0.08 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.00006 --ppo-entropy-cost 0.004 --ppo-clipping-epsilon 0.07 --ppo-max-grad-norm 0.65 --command-progress-failure-enable --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_2>'
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
