# Training Run Summary

status: `INFO_NON_DEPLOYABLE_TRAINING_RUN`
generated_at: `2026-06-29T13:27:02Z`
run_dir: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/phase2_domain_randomization/stage_b0g_push_recovery_local_rocm_smoke/smoke_20260629T130541Z_gpu`

## Run

- platform: `gpu`
- returncode: `0`
- elapsed_s: `204.93788960800157`
- actuator_bridge_enabled: `True`
- target_rate_scale: `0.0`
- actuator_tracking_scale: `0.0`
- non_deployable: `True`

## Latest ONNX

- path: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/phase2_domain_randomization/stage_b0g_push_recovery_local_rocm_smoke/smoke_20260629T130541Z_gpu/2026_06_29_090758_20480.onnx`
- step: `20480`
- sha256: `70fde5e93cfe7252ef14d8c953e9015051cde1747806f24adf2274f022491473`
- size_bytes: `883946`

## Reward Steps

| step | reward | reward_std |
|---:|---:|---:|
| 20480 | 7.416734 | 4.264737 |

## ONNX Exports

| step | file | sha256 |
|---:|---|---|
| 20480 | `2026_06_29_090758_20480.onnx` | `70fde5e93cfe7252ef14d8c953e9015051cde1747806f24adf2274f022491473` |

## Warning Lines

Actionable warning/error-like stderr lines found: `1`
Known benign/log-noise stderr lines found: `6`

| known noise category | count |
|---|---:|
| `absl_preinit` | 2 |
| `tensorflow_cuda_stub_cpu` | 2 |
| `tensorflow_onednn` | 2 |

First actionable lines, truncated:

```text
E0000 00:00:1782738343.826374  769604 cuda_platform.cc:52] failed call to cuInit: INTERNAL: CUDA error: Failed call to cuInit: UNKNOWN ERROR (303)
```

## Next Gate

Use `tools/package_candidate_policy.py` on the latest ONNX only after
the run is intended as a candidate and the required sim-gate evidence
exists. This summary does not approve robot testing.
