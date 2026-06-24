# Staged Curriculum Training Plan

Offline-only plan. This does not touch the robot, SSH, deploy, or modify
runtime behavior. Training only runs when the planner is invoked with
`--run`.

status: `HOLD_PHASE_MULTI_SEED_FALLS`
platform: `gpu`
recipe: `movement_bootstrap_v18`
output_root: `/content/open_duck_staged_curriculum_cli`

## Why

Current candidates are either aggressive and unsafe, or stable and nearly
stationary at `x=0.08`. The staged recipe bootstraps forward motion before
tightening actuator realism.

`movement_bootstrap_v18` follows the V17 reward/sign audit. V17 used the intended reward config and a consistent local-forward sign convention, but still failed at x=0.04, the easiest command it trained on. V18 therefore stops treating x=0.08 as the first target and runs a minimal x=0.04 discovery experiment: no restore, no actuator bridge, dense per-step signed progress, immediate wrong-direction pressure, and phase gates at the same low command as training. Do not expand to x=0.08 until low-command motion passes across seeds.

## Phases

| phase | bridge | gate bridge | timesteps | x command range | shortfall | window progress | failure penalty | delay | tau | velocity limit | purpose |
|---|---|---|---:|---|---|---|---|---|---|---|---|
| `phase1_x004_dense_progress_discovery` | no | `vanilla` | 260000 | `[0.035, 0.045]` | `{'scale': -120.0, 'required_ratio': 0.65}` | `{'scale': 12.0, 'shortfall': -80.0, 'required_ratio': 0.6, 'warmup_steps': 5, 'failure': True, 'failure_min_ratio': 0.25}` | `{'scale': -160.0, 'clip_min': -20.0}` | `[0, 0]` | `[0.0, 0.0]` | `[5.24, 5.24]` | minimal low-command discovery after V17 failed even at x=0.04. Train and gate on the same easy positive command, with no restore and no actuator bridge, so the run answers only whether dense signed-progress pressure can discover coherent forward motion. |

## Commands

### phase1_x004_dense_progress_discovery

- restore_checkpoint: `None`

```bash
/usr/bin/python3 /content/open-duck-mini-rdkx5/tools/run_actuator_bridge_training_smoke.py --run --playground-path /content/Open_Duck_Playground --env-python /usr/bin/python3 --output-root /content/open_duck_staged_curriculum_cli/01_phase1_x004_dense_progress_discovery --platform gpu --timeout-s 10800 --num-timesteps 260000 --export-min-step 1 --ppo-num-envs 256 --ppo-num-evals 4 --ppo-episode-length 600 --ppo-unroll-length 10 --ppo-batch-size 256 --ppo-num-minibatches 4 --ppo-num-updates-per-batch 4 --target-rate-scale -0.0002 --actuator-tracking-scale 0 --tracking-lin-vel-scale 42 --tracking-ang-vel-scale 0.0 --tracking-sigma 0.0012 --forward-progress-scale 60 --forward-shortfall-scale -120 --forward-progress-deadband 0.02 --forward-shortfall-required-ratio 0.65 --forward-overshoot-scale -3 --forward-overshoot-allowed-ratio 1.7 --forward-wrong-direction-scale -120 --forward-wrong-direction-allowed-reverse-ratio 0 --command-progress-scale 12 --command-progress-shortfall-scale -80 --command-progress-failure-scale -160 --command-progress-required-ratio 0.6 --command-progress-warmup-steps 5 --command-progress-failure-min-ratio 0.25 --command-progress-failure-warmup-steps 50 --action-rate-huber-delta 0.08 --action-magnitude-huber-delta 0.5 --target-rate-huber-delta 1 --actuator-tracking-huber-delta 0.08 --forward-shortfall-huber-delta 0 --forward-overshoot-huber-delta 0.5 --forward-wrong-direction-huber-delta 0 --forward-pitch-huber-delta 0.25 --forward-pitch-rate-huber-delta 1 --command-progress-shortfall-huber-delta 0 --reward-clip-min -20 --reward-clip-max 10000 --action-rate-scale -0.003 --action-magnitude-scale -0.0005 --stand-still-scale -1 --orientation-scale -0.035 --base-height-scale -0.25 --forward-pitch-scale -0.06 --forward-pitch-rate-scale -0.006 --forward-contact-support-scale -0.1 --forward-contact-support-no-contact-weight 1 --forward-contact-support-asymmetry-weight 0.02 --alive-scale 0 --imitation-scale 0 --lin-vel-x-min 0.035 --lin-vel-x-max 0.045 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --command-resample-steps 600 --zero-command-probability 0 --head-range-factor 0.25 --jax-platforms cuda --ppo-learning-rate 0.00015 --ppo-entropy-cost 0.02 --ppo-clipping-epsilon 0.14 --ppo-max-grad-norm 0.8 --command-progress-failure-enable --disable-actuator-bridge
```

## Result

- final_candidate_onnx: `/content/open_duck_staged_curriculum_cli/01_phase1_x004_dense_progress_discovery/smoke_20260624T153357Z_gpu/2026_06_24_154301_276480.onnx`
- final_checkpoint: `/content/open_duck_staged_curriculum_cli/01_phase1_x004_dense_progress_discovery/smoke_20260624T153357Z_gpu/2026_06_24_154301_276480`

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

Then repeat with `--command-x 0.04`. Robot validation remains blocked until both gates pass.
