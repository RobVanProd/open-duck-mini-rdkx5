# Phase 2 B0D Local GPU 32-Env Decision

status: `HOLD_B0D_32ENV_NO_PROMOTABLE_CHECKPOINT`

## Purpose

Run a bounded local RX 7900 XTX B0D continuation below the 64-env ROCm crash
point, then sweep exported checkpoints with the corrected actuator bridge.

This was offline sim training only. It did not touch the robot.

## Input

- restore checkpoint:
  `outputs/phase2_domain_randomization/stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/smoke_20260629T062042Z_gpu/2026_06_29_022725_245760`
- platform: `gpu`
- JAX platform: `rocm`
- device verified before run: `rocm:0 AMD Radeon RX 7900 XTX`
- timesteps requested: `20480`
- observed PPO steps: `0`, `20480`, `40960`, `61440`
- envs: `32`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.002`
- corrected actuator bridge enabled
- actuator tracking scale: `-0.04`
- restore-policy KL: `1.0`
- behavior prior enabled, scale `-0.35`

## Training Result

Output:

`outputs/phase2_domain_randomization/stage_b0d_tracking_margin_local_gpu_32env/smoke_20260629T075706Z_gpu`

Summary:

- status: `PASS_SMOKE_RUN`
- return code: `0`
- elapsed: `367.13 s`
- checkpoints exported:
  - `2026_06_29_040028_20480.onnx`
  - `2026_06_29_040220_40960.onnx`
  - `2026_06_29_040251_61440.onnx`
- reward moved from `45.35` at step 0 to `61.33` at step 61440
- terrain override restored to original hash
- robot_touched: `false`

## Compact Checkpoint Sweep

Sweep artifact:

`outputs/analysis/PHASE2_B0D_LOCAL_GPU_32ENV_CHECKPOINT_SWEEP.md`

Configuration:

- commands: `0.0,0.08`
- duration: `1.0 s`
- bridge: corrected fitted bridge
- JAX platform: `cpu`
- velocity envelope: `2.0-3.25 rad/s`

Result:

| checkpoint | x=0.0 | x=0.08 | x=0.08 track ratio | x=0.08 max tracking p95 | max pitch vel p95 |
|---|---|---|---:|---:|---:|
| `20480` | PASS | HOLD low progress | 0.2475 | 0.2208 | 1.5725 |
| `40960` | PASS | HOLD low progress | 0.2452 | 0.2189 | 1.5795 |
| `61440` | PASS | HOLD tracking | 0.2575 | 0.2199 | 1.5850 |

The 61,440 checkpoint is the most interesting by compact forward ratio, but it
still fails the compact x=0.08 gate and should not be promoted.

## Interpretation

The local 32-env scale is usable on the RX 7900 XTX, unlike the 64-env scale.
B0D at this local scale did not produce a promotable checkpoint. It preserved
in-envelope behavior and x=0.0 standing in the compact sweep, but did not clear
the x=0.08 tracking/progress gate.

Do not run robot validation from these checkpoints. The next training attempt
should either:

- use the pinned CUDA/A100 B0D workflow when a Colab session is visible, or
- make a deliberate recipe change before another local 32-env continuation.

## Decision

`HOLD_B0D_32ENV_NO_PROMOTABLE_CHECKPOINT`

No robot test, SSH, deploy, grounded replay, or robot runtime behavior change
was performed.
