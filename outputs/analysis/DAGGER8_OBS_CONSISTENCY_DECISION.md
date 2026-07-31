# DAgger-8 Observation-Consistency BC Decision

status: `HOLD_BC_REPLAY_TERMINATED`

## Purpose

DAgger-7 showed that uniformly upweighting the two hard-seed relabel traces was
not sufficient: seeds 1 and 7 still terminated early under the fitted actuator
bridge. The split hard-seed analysis found two different mechanisms:

- seed 1: left-support closed-loop lateral/height instability despite nearby
  manifest support
- seed 7: right-support local action mismatch near the teacher

DAgger-8 tested whether a deployable 128x128 MLP could be made less brittle
around the demonstrated states by adding observation-noise consistency
regularization while keeping the DAgger-7 dataset and target-rate penalty.

## Command

```bash
../envs/open-duck-playground/bin/python tools/run_target_dataset_bc_smoke.py \
  --manifest outputs/analysis/filtered_source_vx_selector_dagger7_targeted_recovery_manifest.json \
  --output-md outputs/analysis/SOURCE_VX_SELECTOR_TRACE_DAGGER8_OBS_CONSISTENCY_MLP128_RATE_REG_FITTED_BRIDGE_BC_GATE_X008_10S.md \
  --output-json outputs/analysis/source_vx_selector_trace_dagger8_obs_consistency_mlp128_rate_reg_fitted_bridge_bc_gate_x008_10s.json \
  --playground-path ../Open_Duck_Playground \
  --task flat_terrain \
  --command-x 0.08 \
  --duration-s 10 \
  --seeds 0,1,2,3,4,5,6,7 \
  --model-kind mlp \
  --mlp-hidden-sizes 128,128 \
  --mlp-steps 5000 \
  --mlp-batch-size 512 \
  --mlp-learning-rate 0.001 \
  --mlp-seed 8 \
  --mlp-target-rate-scale 0.1 \
  --mlp-target-rate-limit-rad-s 3.75 \
  --mlp-obs-noise-std 0.02 \
  --mlp-obs-consistency-scale 0.1 \
  --save-mlp-npz outputs/analysis/source_vx_selector_trace_dagger8_obs_consistency_mlp128_rate_reg_candidate/candidate_mlp.npz \
  --export-mlp-onnx outputs/analysis/source_vx_selector_trace_dagger8_obs_consistency_mlp128_rate_reg_candidate/candidate.onnx \
  --trace-dir outputs/analysis/source_vx_selector_trace_dagger8_obs_consistency_mlp128_rate_reg_fitted_bridge_bc_gate_x008_10s_traces \
  --actuator-bridge-mode fitted \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --jax-platform cpu
```

## Fit

```text
samples: 22778
train RMSE: 0.02665
train MAE: 0.01741
train p95 abs error: 0.05335
action saturation: 0%
target-rate scale: 0.1
obs_noise_std: 0.02
obs_consistency_scale: 0.1
ONNX verification max abs error: 0
```

## Eight-Seed Gate

| seed | status | samples | mean vx | track ratio | vy95 | base height min | sent vel p95 | tracking p95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `PASS_ROLLOUT_COMPLETED` | 500 | 0.0311 | 0.3889 | 0.1059 | 0.1536 | 2.2585 | 0.1764 |
| 1 | `HOLD_ROLLOUT_TERMINATED` | 33 | 0.0067 | 0.0836 | 1.2433 | 0.0791 | 2.2362 | 0.1577 |
| 2 | `PASS_ROLLOUT_COMPLETED` | 500 | 0.0316 | 0.3952 | 0.1090 | 0.1525 | 2.2285 | 0.1777 |
| 3 | `PASS_ROLLOUT_COMPLETED` | 500 | 0.0297 | 0.3709 | 0.1165 | 0.1590 | 2.2430 | 0.1784 |
| 4 | `PASS_ROLLOUT_COMPLETED` | 500 | 0.0305 | 0.3813 | 0.1105 | 0.1515 | 2.2955 | 0.1803 |
| 5 | `PASS_ROLLOUT_COMPLETED` | 500 | 0.0321 | 0.4014 | 0.1105 | 0.1469 | 2.2591 | 0.1779 |
| 6 | `PASS_ROLLOUT_COMPLETED` | 500 | 0.0254 | 0.3180 | 0.1176 | 0.1587 | 2.2793 | 0.1809 |
| 7 | `HOLD_ROLLOUT_TERMINATED` | 32 | 0.0202 | 0.2524 | 1.1534 | 0.0848 | 2.5541 | 0.1703 |

## Decision

Observation-consistency regularization does not clear the two hard seeds. It
preserves the same broad shape as DAgger-7: six seeds complete with low,
in-envelope forward motion, while seeds 1 and 7 still terminate around the
first support-transition window with large lateral velocity.

This makes a broad "more robust BC" explanation less likely. The remaining
deployable-policy work should stay split:

- seed 1 needs closed-loop lateral/height recovery during left support
- seed 7 still needs better right-support pitch-chain action fit/recovery

Do not run another uniform static-label DAgger pass as the next experiment.
The next useful deployable-policy branch should add an explicit closed-loop
recovery/stabilization mechanism or move to a fine-tune objective that starts
from the best BC student but directly optimizes the hard support transitions.

No robot tests, SSH, deploy, PPO training, or runtime behavior changes were
performed.
