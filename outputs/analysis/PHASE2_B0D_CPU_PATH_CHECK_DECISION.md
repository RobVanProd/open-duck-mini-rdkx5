# Phase 2 B0D CPU Path Check Decision

status: `PASS_CPU_PATH_CHECK`

## Purpose

Validate that the B0D tracking-margin continuation recipe is structurally executable
outside the failing local ROCm path.

This was a tiny CPU smoke/path check only. It was not intended to train or promote a
candidate.

## Input

- restore checkpoint:
  `outputs/phase2_domain_randomization/stage_b0c_rough_z002_push_tracking_margin_from_b0_gpu/smoke_20260629T062042Z_gpu/2026_06_29_022725_245760`
- platform: `cpu`
- timesteps: `64`
- envs: `8`
- task: `rough_terrain_backlash`
- terrain hfield z scale: `0.002`
- corrected actuator bridge enabled
- actuator tracking scale: `-0.04`
- actuator tracking Huber delta: `0.03`
- restore-policy KL: `1.0`
- behavior prior: enabled, scale `-0.35`

## Result

Output:

`outputs/phase2_domain_randomization/stage_b0d_tracking_margin_cpu_path_check/smoke_20260629T073934Z_cpu`

Summary artifacts:

- `outputs/analysis/PHASE2_B0D_CPU_PATH_CHECK_SUMMARY.md`
- `outputs/analysis/phase2_b0d_cpu_path_check_summary.json`

Observed:

- status: `PASS_SMOKE_RUN`
- return code: `0`
- elapsed: `101.49 s`
- PPO step line: `STEP: 80 reward: 4.0448 reward_std: 1.8088`
- checkpoint/export produced at step `80`
- terrain override restored to original hash
- robot_touched: `false`

## Interpretation

B0D is command-path valid. The recipe can restore the B0C checkpoint, instantiate the
rough-terrain corrected-bridge environment, run PPO, save a checkpoint, export ONNX, and
restore the temporary terrain XML override on CPU.

This does not prove B0D improves the policy. The run is far too small to count as Phase 2
training. The full B0D training verdict still requires a CUDA/Colab/A100 run or a healthy
local GPU runtime, followed by the strict corrected-bridge rough-terrain gates.

## Decision

`PASS_CPU_PATH_CHECK`

Next actionable command when a Colab CLI session is visible:

```bash
python3 tools/run_colab_cli_cuda_workflow.py \
  --workflow phase2-b0d \
  --session open-duck-l4 \
  --candidate-name phase2_b0d_tracking_margin_cuda \
  --candidate-timeout-s 10800 \
  --run
```

No robot test, SSH, deploy, grounded replay, or robot runtime behavior change was
performed.
