# Phase 2 z0.005 Motion-Floor T4 Partial Decision

status: `HOLD_NO_PROMOTABLE_CHECKPOINT`
generated_at: `2026-06-29T21:02:00Z`

## Summary

The `phase2-z005-motion-floor` Colab/T4 training run completed and exported three ONNX
checkpoints, but the remote Colab `/content` state disappeared during the post-training
checkpoint sweep. A partial artifact bundle had already been downloaded, so the ONNX
checkpoints were recovered and re-evaluated locally on CPU with the project Playground env.

Result: no checkpoint is promotable. All three checkpoints pass the compact `x=0.0`
candidate smoke, but all three hold at `x=0.08` for low forward progress. There is no
velocity-envelope excess and no action saturation. The failure is under-moving, not unsafe
target dynamics.

## Training Artifact

- workflow: `phase2-z005-motion-floor`
- Colab session hardware: `T4`
- training status: `returncode=0`
- training duration: `952.86 s`
- training steps: `122880`
- recovered partial artifact:
  `outputs/analysis/colab_cli/open-duck-l4-phase2-z005-motion-floor-20260629T200911Z/open_duck_colab_cli_phase2-z005-motion-floor_20260629T200935Z_artifacts.tar.gz.partial`
- partial artifact sha256:
  `445166ea1f0678cb3fc331e208a6b4565910c7eb2b0356161d8fcdf5a8837ba2`

## Exported Checkpoints

| step | sha256 |
|---:|---|
| 40960 | `e6a3c71f72b1c359afac2573a898ee9f912a5d6c42519c2030444012382317d4` |
| 81920 | `6914cc3c9486e412d5ca82849488c4e77a6e5a886d19379ccad3e7bb96210f8d` |
| 122880 | `1b2187d7d8e92c3d00bdddb249e4f96cab41fd6ca41269108cdb87106797f9f8` |

## Local Recovery Sweep

Command family:

```bash
/home/lsd/robots/envs/open-duck-playground/bin/python tools/sweep_candidate_checkpoints.py \
  --fit-json outputs/analysis/actuator_response_fit_corrected_knee.json \
  --playground-path ../Open_Duck_Playground \
  --env-python /home/lsd/robots/envs/open-duck-playground/bin/python \
  --commands 0.0,0.08 \
  --duration 1 \
  --bridge-mode fitted \
  --mode-name fitted \
  --jax-platform cpu \
  --output-dir outputs/analysis/phase2_z005_motion_floor_cuda_checkpoint_sweep_local_cpu_env \
  --run
```

Aggregate reports:

- `outputs/analysis/phase2_z005_motion_floor_cuda_checkpoint_sweep_local_cpu_env/CANDIDATE_CHECKPOINT_SWEEP.md`
- `outputs/analysis/phase2_z005_motion_floor_cuda_checkpoint_sweep_local_cpu_env/candidate_checkpoint_sweep.json`
- sweep json sha256:
  `1c1bfb12060e2798356177e0426b91ce6d4fb11d802a21c151300ce8f360f275`
- sweep markdown sha256:
  `54ff64c1b59a07c65dcbc7972e57e4c1b14fa9f5c549a8cdd7edf8fe8c3034f1`

## Compact Gate Results

| checkpoint | x=0.0 | x=0.08 | track ratio @ x=0.08 | mean vx @ x=0.08 | max pitch tracking p95 | max pitch vel p95 | envelope excess |
|---|---|---|---:|---:|---:|---:|---:|
| 40960 | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1663 | 0.0133 | 0.2132 | 1.4355 | 0.0 |
| 81920 | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1730 | 0.0138 | 0.2130 | 1.4369 | 0.0 |
| 122880 | `PASS_CANDIDATE_SIM_GATE` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1699 | 0.0136 | 0.2132 | 1.4361 | 0.0 |

The best compact checkpoint is `81920`, but it is still below the promotion thresholds:
track ratio `0.1730 < 0.25` and mean vx `0.0138 < 0.0200 m/s`.

## Decision

`HOLD_NO_PROMOTABLE_CHECKPOINT`

Do not run robot validation. Do not promote any checkpoint from this run.

Interpretation: the z0.005 motion-floor recipe kept the policy inside the corrected actuator
envelope and preserved `x=0.0` behavior, but it suppressed forward progress at `x=0.08`.
The next Phase 2 recipe should restore motion continuity from the Phase 1 candidate or
teacher-action prior while keeping the corrected-bridge envelope gate unchanged.
