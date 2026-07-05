# Phase 2 Gate-Aware Parent Next Branch

status: `PLAN_GATE_AWARE_ON_POLICY_PARENT`

This is an offline planning artifact. It did not train, SSH, deploy,
run robot tests, run grounded replay, or change robot runtime behavior.

## Executive Summary

BC-only compression is closed for the current live-oracle iter2 aggregate.
The next authorized branch is a bounded gate-aware/on-policy parent
iteration from the live-oracle iter2 PPO-loc step-0 checkpoint.

Do not train from scratch. Do not launch long domain randomization until
the compact corrected-bridge behavior-preservation gates pass.

## Restore Point

- checkpoint: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_step0_checkpoint`
- checkpoint exists: `True`
- ONNX: `outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_step0.onnx`
- ONNX sha256: `d7af39a6255f7303a742b07ac87333c503534c73bd5b16766fa2ad3f4ae1e28f`
- fidelity status: `PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY`

## Compact Gate Evidence

### x=0.08 moving gate

- pass count: `3/5`
- fall count: `1`
- mean vx: `0.046054641749676814`
- mean track ratio: `0.5756830218709601`
- max p95 velocity excess: `0.0`
- max instantaneous velocity excess: `0.26517319679260254`

| seed | status | samples | mean vx | track ratio | max vel excess |
|---:|---|---:|---:|---:|---:|
| `0` | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0259 | 0.3240459992630349 | 0.0000 |
| `1` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 164 | 0.1334 | 1.6671817254441188 | 0.0000 |
| `2` | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0229 | 0.2860647649450887 | 0.0000 |
| `6` | `PASS_CANDIDATE_SIM_GATE` | 750 | 0.0221 | 0.27642290748141624 | 0.0000 |
| `7` | `HOLD_CANDIDATE_TARGET_VELOCITY` | 750 | 0.0260 | 0.324699712221142 | 0.2652 |

### x=0.0 command-semantics gate

- pass count: `5/5`
- fall count: `0`
- mean vx: `0.0007887222692524803`
- max p95 velocity excess: `0.0`
- max instantaneous velocity excess: `0.0`

## Closed Branches

- `ppo_loc_live_oracle_iter2`: `HOLD_PPO_LOC_STEP0_MOVING_GATE`
- `phase_contact_modulated`: `HOLD_PHASE_CONTACT_MODULATED_MOVING_GATE`
- `recurrent_h64_s32`: `HOLD_RECURRENT_BC_OVER_ENVELOPE_COLLAPSE`

## Next Branch

Run a bounded gate-aware/on-policy parent iteration from the live-oracle iter2 PPO-loc step-0 checkpoint. Do not train from scratch and do not repeat one-shot BC compression on this aggregate.

Success gate:

- x=0.08: 5/5 PASS_CANDIDATE_SIM_GATE, zero p95 and max corrected velocity excess
- x=0.0: 5/5 PASS_CANDIDATE_SIM_GATE, mean |vx| <= 0.005 m/s, zero corrected velocity excess

Stop conditions:

- Any checkpoint with x=0.0 command-semantics regression is rejected.
- Any checkpoint with corrected velocity-envelope excess is rejected.
- If the first bounded on-policy iteration lowers x=0.08 pass count below the step-0 3/5 baseline, stop and change objective structure.
- Do not launch long DR until a step-0 or short on-policy parent clears the compact x=0.08 and x=0.0 gates.

## Local Smoke Command

```bash
../envs/open-duck-playground/bin/python tools/run_actuator_bridge_training_smoke.py --playground-path ../Open_Duck_Playground --env-python ../envs/open-duck-playground/bin/python --output-root outputs/phase2_domain_randomization/gate_aware_parent_iter0_local_smoke --platform gpu --local-rocm-safe-env --timeout-s 7200 --task rough_terrain_backlash --restore-checkpoint-path outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_step0_checkpoint --restore-policy-kl-scale 8.0 --num-timesteps 40960 --export-min-step 1 --ppo-num-envs 16 --ppo-num-evals 4 --ppo-episode-length 750 --ppo-unroll-length 20 --ppo-batch-size 128 --ppo-num-minibatches 1 --ppo-num-updates-per-batch 2 --lin-vel-x-min 0.06 --lin-vel-x-max 0.10 --lin-vel-y-min 0.0 --lin-vel-y-max 0.0 --ang-vel-yaw-min 0.0 --ang-vel-yaw-max 0.0 --zero-command-probability 0.15 --command-resample-steps 600 --terrain-hfield-z-scale 0.0075 --push-enable --push-interval-min-s 1.0 --push-interval-max-s 1.5 --push-magnitude-min 0.075 --push-magnitude-max 0.125 --tracking-lin-vel-scale 2.5 --tracking-sigma 0.015 --forward-progress-scale 2.0 --command-progress-scale 1.2 --command-progress-shortfall-scale -2.0 --command-progress-required-ratio 0.35 --command-progress-warmup-steps 30 --command-progress-failure-enable --command-progress-failure-min-ratio 0.12 --command-progress-failure-warmup-steps 80 --target-rate-scale -0.015 --target-rate-huber-delta 0.08 --actuator-tracking-scale -0.015 --actuator-tracking-huber-delta 0.04 --action-rate-scale -0.07 --action-magnitude-scale -0.004 --forward-pitch-scale -0.5 --forward-pitch-rate-scale -0.10 --base-height-scale -0.6 --imitation-scale 0.0 --run
```

## Colab A100 Command

```bash
python3 \
    tools/run_colab_cli_cuda_workflow.py \
    --workflow \
    phase2-b0g \
    --session \
    open-duck-a100-gate-aware-parent \
    --candidate-name \
    phase2_gate_aware_parent_iter0 \
    --phase2-restore-checkpoint-path \
    outputs/analysis/phase2_command_gated_zero0020_live_oracle_iter2_ppo_loc_step0_checkpoint \
    --phase2-terrain-hfield-z-scale \
    0.0075 \
    --phase2-num-timesteps \
    122880 \
    --phase2-ppo-num-envs \
    64 \
    --phase2-ppo-batch-size \
    512 \
    --candidate-checkpoint-sweep \
    --candidate-checkpoint-sweep-commands \
    0.0,0.08 \
    --candidate-checkpoint-sweep-duration \
    1.0 \
    --candidate-checkpoint-sweep-jax-platform \
    cpu \
    --staged-phase-gate-freeze-check \
    --staged-phase-gate-command-x \
    0.08 \
    --staged-phase-gate-duration-s \
    5.0 \
    --staged-phase-gate-bridge-mode \
    fitted \
    --staged-phase-gate-platform \
    cpu \
    --staged-phase-gate-seeds \
    0,1,2,6,7 \
    --staged-phase-gate-max-fall-fraction \
    0.0 \
    --staged-phase-gate-min-track-ratio-mean \
    0.25 \
    --staged-phase-gate-min-vx-mean \
    0.02 \
    --phase2-final-training-args-json \
    '["--restore-policy-kl-scale", "8.0", "--num-timesteps", "40960", "--export-min-step", "1", "--ppo-num-envs", "16", "--ppo-num-evals", "4", "--ppo-episode-length", "750", "--ppo-unroll-length", "20", "--ppo-batch-size", "128", "--ppo-num-minibatches", "1", "--ppo-num-updates-per-batch", "2", "--lin-vel-x-min", "0.06", "--lin-vel-x-max", "0.10", "--lin-vel-y-min", "0.0", "--lin-vel-y-max", "0.0", "--ang-vel-yaw-min", "0.0", "--ang-vel-yaw-max", "0.0", "--zero-command-probability", "0.15", "--command-resample-steps", "600", "--terrain-hfield-z-scale", "0.0075", "--push-enable", "--push-interval-min-s", "1.0", "--push-interval-max-s", "1.5", "--push-magnitude-min", "0.075", "--push-magnitude-max", "0.125", "--tracking-lin-vel-scale", "2.5", "--tracking-sigma", "0.015", "--forward-progress-scale", "2.0", "--command-progress-scale", "1.2", "--command-progress-shortfall-scale", "-2.0", "--command-progress-required-ratio", "0.35", "--command-progress-warmup-steps", "30", "--command-progress-failure-enable", "--command-progress-failure-min-ratio", "0.12", "--command-progress-failure-warmup-steps", "80", "--target-rate-scale", "-0.015", "--target-rate-huber-delta", "0.08", "--actuator-tracking-scale", "-0.015", "--actuator-tracking-huber-delta", "0.04", "--action-rate-scale", "-0.07", "--action-magnitude-scale", "-0.004", "--forward-pitch-scale", "-0.5", "--forward-pitch-rate-scale", "-0.10", "--base-height-scale", "-0.6", "--imitation-scale", "0.0"]' \
    --run
```
