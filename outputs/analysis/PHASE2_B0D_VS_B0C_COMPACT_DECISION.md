# Phase 2 B0D vs B0C Compact Decision

status: `HOLD_B0D_REGRESSED_MOTION_NO_TRACKING_GAIN`

## Purpose

Compare the local 32-env B0D continuation against its B0C parent using the same
compact corrected-bridge checkpoint sweep.

This is an offline sim comparison only. It did not touch the robot.

## Inputs

B0C parent:

`outputs/phase2_domain_randomization/stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/smoke_20260629T062042Z_gpu/2026_06_29_022725_245760.onnx`

B0D local 32-env exports:

- `outputs/phase2_domain_randomization/stage_b0d_tracking_margin_local_gpu_32env/smoke_20260629T075706Z_gpu/2026_06_29_040028_20480.onnx`
- `outputs/phase2_domain_randomization/stage_b0d_tracking_margin_local_gpu_32env/smoke_20260629T075706Z_gpu/2026_06_29_040220_40960.onnx`
- `outputs/phase2_domain_randomization/stage_b0d_tracking_margin_local_gpu_32env/smoke_20260629T075706Z_gpu/2026_06_29_040251_61440.onnx`

Sweep configuration:

- commands: `0.0,0.08`
- duration: `1.0 s`
- bridge: corrected fitted bridge
- JAX platform: `cpu`
- velocity envelope: `2.0-3.25 rad/s`

## Result

| policy | x=0.08 status | track ratio | mean vx | max tracking p95 | max pitch vel p95 |
|---|---|---:|---:|---:|---:|
| B0C parent | HOLD tracking | 0.3035 | 0.0243 | 0.2199 | 1.5503 |
| B0D 20480 | HOLD low progress | 0.2475 | 0.0198 | 0.2208 | 1.5725 |
| B0D 40960 | HOLD low progress | 0.2452 | 0.0196 | 0.2189 | 1.5795 |
| B0D 61440 | HOLD tracking | 0.2575 | 0.0206 | 0.2199 | 1.5850 |

All rows pass the compact `x=0.0` check. None promote.

## Interpretation

B0D did not improve the compact tracking blocker versus B0C. It mainly reduced
forward motion while leaving tracking p95 around the same `0.219 rad` level.

Do not continue B0D as-is. The next recipe should preserve B0C's forward motion
more strongly while attacking tracking margin, or wait for the CUDA/A100 route
to test the original scale without local ROCm constraints.

## Decision

`HOLD_B0D_REGRESSED_MOTION_NO_TRACKING_GAIN`

No robot test, SSH, deploy, grounded replay, or robot runtime behavior change
was performed.
