# Staged Curriculum Training Plan

Offline-only plan. This does not touch the robot, SSH, deploy, or modify
runtime behavior. Training only runs when the planner is invoked with
`--run`.

status: `PASS_STAGED_CURRICULUM_RUN`
platform: `gpu`
recipe: `movement_bootstrap_v8`
output_root: `/content/open_duck_staged_curriculum_cli`

## Why

Current candidates are either aggressive and unsafe, or stable and nearly
stationary at `x=0.08`. The staged recipe bootstraps forward motion before
tightening actuator realism.

`movement_bootstrap_v8` starts from the v7 anchored checkpoint. The v7 x=0.08 trace showed an in-envelope, unsaturated lunge: local forward speed exceeded the command before the large pitch collapse. V8 keeps the fitted actuator bridge active and adds explicit forward-overshoot, pitch, and pitch-rate costs.

## Phases

| phase | bridge | timesteps | x command range | shortfall | window progress | delay | tau | velocity limit | purpose |
|---|---|---:|---|---|---|---|---|---|---|
| `phase1_v7_lunge_damping_fitted_bridge` | yes | 120000 | `[0.04, 0.08]` | `{'scale': -5.0, 'required_ratio': 0.35}` | `{'scale': 6.0, 'shortfall': -7.0, 'required_ratio': 0.35, 'warmup_steps': 35}` | `[3, 6]` | `[0.06, 0.14]` | `[2.5, 3.75]` | continue from the v7 anchor and directly penalize the observed x=0.08 lunge: local forward speed above command, pitch tilt, and pitch-rate growth under the fitted actuator bridge |
| `phase2_v7_lunge_damping_consolidate` | yes | 120000 | `[0.04, 0.08]` | `{'scale': -5.0, 'required_ratio': 0.38}` | `{'scale': 6.5, 'shortfall': -7.0, 'required_ratio': 0.38, 'warmup_steps': 35}` | `[3, 6]` | `[0.06, 0.14]` | `[2.5, 3.75]` | consolidate the damped gait with the same fitted bridge and slightly lower overshoot pressure so forward motion is not erased |

## Commands

### phase1_v7_lunge_damping_fitted_bridge

- restore_checkpoint: `/content/open-duck-mini-rdkx5/policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/checkpoint_2026_06_23_213846_184320`

```bash
/usr/bin/python3 /content/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /content/Open_Duck_Playground --env-python /usr/bin/python3 --output-root /content/open_duck_staged_curriculum_cli/01_phase1_v7_lunge_damping_fitted_bridge --platform gpu --timeout-s 10800 --num-timesteps 120000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0015 --actuator-tracking-scale -0.15 --tracking-lin-vel-scale 28 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0015 --forward-progress-scale 5.5 --forward-shortfall-scale -5 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.35 --forward-overshoot-scale -3 --forward-overshoot-allowed-ratio 1.35 --command-progress-scale 6 --command-progress-shortfall-scale -7 --command-progress-required-ratio 0.35 --command-progress-warmup-steps 35 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0.35 --forward-overshoot-huber-delta 0.5 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0.35 --action-rate-scale -0.02 --action-magnitude-scale -0.005 --stand-still-scale -0.8 --orientation-scale -0.08 --base-height-scale -0.8 --forward-pitch-scale -0.35 --forward-pitch-rate-scale -0.035 --alive-scale 0.06 --imitation-scale 0.48 --lin-vel-x-min 0.04 --lin-vel-x-max 0.08 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.00003 --ppo-clipping-epsilon 0.035 --ppo-max-grad-norm 0.45 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path /content/open-duck-mini-rdkx5/policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/checkpoint_2026_06_23_213846_184320
```

### phase2_v7_lunge_damping_consolidate

- restore_checkpoint: `/content/open_duck_staged_curriculum_cli/01_phase1_v7_lunge_damping_fitted_bridge/smoke_20260623T224239Z_gpu/2026_06_23_225205_122880`

```bash
/usr/bin/python3 /content/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /content/Open_Duck_Playground --env-python /usr/bin/python3 --output-root /content/open_duck_staged_curriculum_cli/02_phase2_v7_lunge_damping_consolidate --platform gpu --timeout-s 10800 --num-timesteps 120000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0015 --actuator-tracking-scale -0.15 --tracking-lin-vel-scale 28 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0015 --forward-progress-scale 6 --forward-shortfall-scale -5 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.38 --forward-overshoot-scale -2.2 --forward-overshoot-allowed-ratio 1.5 --command-progress-scale 6.5 --command-progress-shortfall-scale -7 --command-progress-required-ratio 0.38 --command-progress-warmup-steps 35 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0.35 --forward-overshoot-huber-delta 0.5 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0.35 --action-rate-scale -0.02 --action-magnitude-scale -0.005 --stand-still-scale -0.8 --orientation-scale -0.08 --base-height-scale -0.8 --forward-pitch-scale -0.3 --forward-pitch-rate-scale -0.03 --alive-scale 0.06 --imitation-scale 0.48 --lin-vel-x-min 0.04 --lin-vel-x-max 0.08 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.000025 --ppo-clipping-epsilon 0.03 --ppo-max-grad-norm 0.45 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path /content/open_duck_staged_curriculum_cli/01_phase1_v7_lunge_damping_fitted_bridge/smoke_20260623T224239Z_gpu/2026_06_23_225205_122880
```

## Result

- final_candidate_onnx: `/content/open_duck_staged_curriculum_cli/02_phase2_v7_lunge_damping_consolidate/smoke_20260623T225217Z_gpu/2026_06_23_225832_122880.onnx`
- final_checkpoint: `/content/open_duck_staged_curriculum_cli/02_phase2_v7_lunge_damping_consolidate/smoke_20260623T225217Z_gpu/2026_06_23_225832_122880`

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
