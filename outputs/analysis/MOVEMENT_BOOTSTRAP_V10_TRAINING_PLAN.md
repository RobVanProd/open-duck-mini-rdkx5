# Staged Curriculum Training Plan

Offline-only plan. This does not touch the robot, SSH, deploy, or modify
runtime behavior. Training only runs when the planner is invoked with
`--run`.

status: `DRY_RUN`
platform: `gpu`
recipe: `movement_bootstrap_v10`
output_root: `/tmp/open_duck_movement_bootstrap_v10`

## Why

Current candidates are either aggressive and unsafe, or stable and nearly
stationary at `x=0.08`. The staged recipe bootstraps forward motion before
tightening actuator realism.

`movement_bootstrap_v10` is the final planned pass in the V7/V9 moving-checkpoint lineage unless the eight-seed distribution moves materially. The V7/V9 multi-seed baseline showed four regimes: lunge, early contact/base-height collapse, reverse motion, and standstill. V10 keeps the fitted actuator envelope active, keeps forward progress dominant, and adds explicit wrong-direction and support-contact costs so stability cannot be bought by freezing or backing up.

## Phases

| phase | bridge | timesteps | x command range | shortfall | window progress | delay | tau | velocity limit | purpose |
|---|---|---:|---|---|---|---|---|---|---|
| `phase1_v7_seed_consistency_recover` | yes | 160000 | `[0.04, 0.08]` | `{'scale': -8.5, 'required_ratio': 0.3}` | `{'scale': 12.0, 'shortfall': -12.5, 'required_ratio': 0.3, 'warmup_steps': 25}` | `[3, 6]` | `[0.06, 0.14]` | `[2.5, 3.75]` | restart from the v7 moving anchor, but target the four observed V7/V9 seed regimes: lunge, reverse, early support collapse, and standstill. Keep forward progress dominant while adding explicit wrong-direction and no-contact support costs. |
| `phase2_consistency_stability_balance` | yes | 180000 | `[0.04, 0.08]` | `{'scale': -8.5, 'required_ratio': 0.32}` | `{'scale': 11.0, 'shortfall': -12.0, 'required_ratio': 0.32, 'warmup_steps': 25}` | `[3, 6]` | `[0.06, 0.14]` | `[2.5, 3.75]` | preserve the forward-moving family while tightening lunge and collapse margins. Keep the fitted actuator envelope fixed and do not let stability be purchased by freezing. |
| `phase3_consolidate_consistent_forward_gait` | yes | 140000 | `[0.04, 0.08]` | `{'scale': -8.2, 'required_ratio': 0.34}` | `{'scale': 10.0, 'shortfall': -11.0, 'required_ratio': 0.34, 'warmup_steps': 25}` | `[3, 6]` | `[0.06, 0.14]` | `[2.5, 3.75]` | final consolidation pass for one coherent in-envelope forward behavior across seeds. This is the last planned run in the V7/V9 lineage unless the eight-seed distribution moves materially. |

## Commands

### phase1_v7_seed_consistency_recover

- restore_checkpoint: `policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/checkpoint_2026_06_23_213846_184320`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_movement_bootstrap_v10/01_phase1_v7_seed_consistency_recover --platform gpu --timeout-s 3600 --num-timesteps 160000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0012 --actuator-tracking-scale -0.12 --tracking-lin-vel-scale 34 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0012 --forward-progress-scale 8.8 --forward-shortfall-scale -8.5 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.3 --forward-overshoot-scale -1 --forward-overshoot-allowed-ratio 1.8 --forward-wrong-direction-scale -3 --forward-wrong-direction-allowed-reverse-ratio 0.05 --command-progress-scale 12 --command-progress-shortfall-scale -12.5 --command-progress-required-ratio 0.3 --command-progress-warmup-steps 25 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0.35 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0.35 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0.35 --action-rate-scale -0.016 --action-magnitude-scale -0.004 --stand-still-scale -1.1 --orientation-scale -0.06 --base-height-scale -0.75 --forward-pitch-scale -0.12 --forward-pitch-rate-scale -0.012 --forward-contact-support-scale -0.35 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0.05 --alive-scale 0.05 --imitation-scale 0.42 --lin-vel-x-min 0.04 --lin-vel-x-max 0.08 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.000025 --ppo-clipping-epsilon 0.03 --ppo-max-grad-norm 0.45 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path policy/candidates/movement_bootstrap_v7_checkpoint_anchor_20260623/checkpoint_2026_06_23_213846_184320
```

### phase2_consistency_stability_balance

- restore_checkpoint: `<latest_checkpoint_from_phase_1>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_movement_bootstrap_v10/02_phase2_consistency_stability_balance --platform gpu --timeout-s 3600 --num-timesteps 180000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0014 --actuator-tracking-scale -0.14 --tracking-lin-vel-scale 32 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0012 --forward-progress-scale 8.4 --forward-shortfall-scale -8.5 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.32 --forward-overshoot-scale -1.4 --forward-overshoot-allowed-ratio 1.65 --forward-wrong-direction-scale -3.5 --forward-wrong-direction-allowed-reverse-ratio 0.03 --command-progress-scale 11 --command-progress-shortfall-scale -12 --command-progress-required-ratio 0.32 --command-progress-warmup-steps 25 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0.35 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0.35 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0.35 --action-rate-scale -0.018 --action-magnitude-scale -0.0045 --stand-still-scale -1.1 --orientation-scale -0.08 --base-height-scale -0.9 --forward-pitch-scale -0.18 --forward-pitch-rate-scale -0.018 --forward-contact-support-scale -0.45 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0.05 --alive-scale 0.05 --imitation-scale 0.4 --lin-vel-x-min 0.04 --lin-vel-x-max 0.08 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.00002 --ppo-clipping-epsilon 0.025 --ppo-max-grad-norm 0.45 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_1>'
```

### phase3_consolidate_consistent_forward_gait

- restore_checkpoint: `<latest_checkpoint_from_phase_2>`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_movement_bootstrap_v10/03_phase3_consolidate_consistent_forward_gait --platform gpu --timeout-s 3600 --num-timesteps 140000 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0015 --actuator-tracking-scale -0.15 --tracking-lin-vel-scale 30 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0012 --forward-progress-scale 8 --forward-shortfall-scale -8.2 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.34 --forward-overshoot-scale -1.7 --forward-overshoot-allowed-ratio 1.55 --forward-wrong-direction-scale -3.5 --forward-wrong-direction-allowed-reverse-ratio 0.03 --command-progress-scale 10 --command-progress-shortfall-scale -11 --command-progress-required-ratio 0.34 --command-progress-warmup-steps 25 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0.35 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0.35 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0.35 --action-rate-scale -0.02 --action-magnitude-scale -0.005 --stand-still-scale -1 --orientation-scale -0.09 --base-height-scale -0.95 --forward-pitch-scale -0.22 --forward-pitch-rate-scale -0.022 --forward-contact-support-scale -0.5 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0.05 --alive-scale 0.05 --imitation-scale 0.38 --lin-vel-x-min 0.04 --lin-vel-x-max 0.08 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --ppo-learning-rate 0.000018 --ppo-clipping-epsilon 0.025 --ppo-max-grad-norm 0.45 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 6 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 3.75 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path '<latest_checkpoint_from_phase_2>'
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
