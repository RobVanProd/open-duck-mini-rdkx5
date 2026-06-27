# Staged Curriculum Training Plan

Offline-only plan. This does not touch the robot, SSH, deploy, or modify
runtime behavior. Training only runs when the planner is invoked with
`--run`.

status: `PASS_STAGED_CURRICULUM_RUN`
platform: `cpu`
output_root: `/tmp/open_duck_staged_curriculum_smoke`

## Why

Current candidates are either aggressive and unsafe, or stable and nearly
stationary at `x=0.08`. The staged recipe bootstraps forward motion before
tightening actuator realism.

## Phases

| phase | bridge | timesteps | x command range | delay | tau | velocity limit | purpose |
|---|---|---:|---|---|---|---|---|
| `phase1_locomotion_bootstrap_no_bridge` | no | 300000 | `[0.06, 0.14]` | `[0, 0]` | `[0.0, 0.0]` | `[5.24, 5.24]` | force forward intent before actuator constraints make standing easy |
| `phase2_mild_bridge_transition` | yes | 250000 | `[0.05, 0.13]` | `[1, 3]` | `[0.02, 0.06]` | `[4.0, 5.24]` | keep forward motion while introducing mild delay/lag/velocity limits |
| `phase3_fitted_bridge_consolidation` | yes | 300000 | `[0.04, 0.12]` | `[3, 8]` | `[0.06, 0.14]` | `[2.5, 4.7]` | train under the fitted actuator envelope used by the candidate gates |

## Commands

### phase1_locomotion_bootstrap_no_bridge

- restore_checkpoint: `None`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum_smoke/01_phase1_locomotion_bootstrap_no_bridge --platform cpu --timeout-s 900 --num-timesteps 300 --ppo-num-envs 8 --ppo-num-evals 1 --ppo-episode-length 80 --ppo-unroll-length 5 --ppo-batch-size 8 --ppo-num-minibatches 1 --ppo-num-updates-per-batch 1 --target-rate-scale 0 --actuator-tracking-scale 0 --tracking-lin-vel-scale 35 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0025 --forward-progress-scale 6 --forward-progress-deadband 0.02 --action-rate-scale -0.02 --action-magnitude-scale -0.005 --stand-still-scale -0.6 --alive-scale 0.2 --imitation-scale 0.1 --lin-vel-x-min 0.06 --lin-vel-x-max 0.14 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --disable-actuator-bridge
```

### phase2_mild_bridge_transition

- restore_checkpoint: `/tmp/open_duck_staged_curriculum_smoke/01_phase1_locomotion_bootstrap_no_bridge/smoke_20260623T122231Z_cpu/2026_06_23_082313_320`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum_smoke/02_phase2_mild_bridge_transition --platform cpu --timeout-s 900 --num-timesteps 250 --ppo-num-envs 8 --ppo-num-evals 1 --ppo-episode-length 80 --ppo-unroll-length 5 --ppo-batch-size 8 --ppo-num-minibatches 1 --ppo-num-updates-per-batch 1 --target-rate-scale -0.004 --actuator-tracking-scale -0.25 --tracking-lin-vel-scale 30 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0025 --forward-progress-scale 5 --forward-progress-deadband 0.02 --action-rate-scale -0.04 --action-magnitude-scale -0.01 --stand-still-scale -0.5 --alive-scale 0.25 --imitation-scale 0.15 --lin-vel-x-min 0.05 --lin-vel-x-max 0.13 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --actuator-bridge-delay-min-ticks 1 --actuator-bridge-delay-max-ticks 3 --actuator-bridge-tau-min-s 0.02 --actuator-bridge-tau-max-s 0.06 --actuator-bridge-velocity-limit-min-rad-s 4 --actuator-bridge-velocity-limit-max-rad-s 5.24 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path /tmp/open_duck_staged_curriculum_smoke/01_phase1_locomotion_bootstrap_no_bridge/smoke_20260623T122231Z_cpu/2026_06_23_082313_320
```

### phase3_fitted_bridge_consolidation

- restore_checkpoint: `/tmp/open_duck_staged_curriculum_smoke/02_phase2_mild_bridge_transition/smoke_20260623T122332Z_cpu/2026_06_23_082411_280`

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python /home/lsd/robots/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /home/lsd/robots/Open_Duck_Playground --env-python /home/lsd/robots/envs/open-duck-playground/bin/python --output-root /tmp/open_duck_staged_curriculum_smoke/03_phase3_fitted_bridge_consolidation --platform cpu --timeout-s 900 --num-timesteps 300 --ppo-num-envs 8 --ppo-num-evals 1 --ppo-episode-length 80 --ppo-unroll-length 5 --ppo-batch-size 8 --ppo-num-minibatches 1 --ppo-num-updates-per-batch 1 --target-rate-scale -0.01 --actuator-tracking-scale -0.75 --tracking-lin-vel-scale 25 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0025 --forward-progress-scale 4 --forward-progress-deadband 0.02 --action-rate-scale -0.08 --action-magnitude-scale -0.02 --stand-still-scale -0.4 --alive-scale 0.3 --imitation-scale 0.2 --lin-vel-x-min 0.04 --lin-vel-x-max 0.12 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0.05 --head-range-factor 0.25 --actuator-bridge-delay-min-ticks 3 --actuator-bridge-delay-max-ticks 8 --actuator-bridge-tau-min-s 0.06 --actuator-bridge-tau-max-s 0.14 --actuator-bridge-velocity-limit-min-rad-s 2.5 --actuator-bridge-velocity-limit-max-rad-s 4.7 --actuator-bridge-per-joint-variation 0.15 --restore-checkpoint-path /tmp/open_duck_staged_curriculum_smoke/02_phase2_mild_bridge_transition/smoke_20260623T122332Z_cpu/2026_06_23_082411_280
```

## Result

- final_candidate_onnx: `/tmp/open_duck_staged_curriculum_smoke/03_phase3_fitted_bridge_consolidation/smoke_20260623T122430Z_cpu/2026_06_23_082509_320.onnx`
- final_checkpoint: `/tmp/open_duck_staged_curriculum_smoke/03_phase3_fitted_bridge_consolidation/smoke_20260623T122430Z_cpu/2026_06_23_082509_320`

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
