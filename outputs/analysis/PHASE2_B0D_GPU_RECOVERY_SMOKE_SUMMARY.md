# Training Run Summary

status: `INFO_NON_DEPLOYABLE_TRAINING_RUN`
generated_at: `2026-06-29T07:52:27Z`
run_dir: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/phase2_domain_randomization/stage_b0d_gpu_recovery_smoke/smoke_20260629T074910Z_gpu`

## Run

- platform: `gpu`
- returncode: `0`
- elapsed_s: `189.47566220800218`
- actuator_bridge_enabled: `True`
- target_rate_scale: `0.0`
- actuator_tracking_scale: `-0.04`
- non_deployable: `True`

## Latest ONNX

- path: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/phase2_domain_randomization/stage_b0d_gpu_recovery_smoke/smoke_20260629T074910Z_gpu/2026_06_29_035056_160.onnx`
- step: `160`
- sha256: `78ee232980a86e6081690cd055b54117eb2f97f9cb72253d7b0f3df97295275c`
- size_bytes: `883946`

## Reward Steps

| step | reward | reward_std |
|---:|---:|---:|
| 160 | 45.068432 | 38.616787 |

## ONNX Exports

| step | file | sha256 |
|---:|---|---|
| 160 | `2026_06_29_035056_160.onnx` | `78ee232980a86e6081690cd055b54117eb2f97f9cb72253d7b0f3df97295275c` |

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
E0000 00:00:1782719352.931533  679894 cuda_platform.cc:52] failed call to cuInit: INTERNAL: CUDA error: Failed call to cuInit: UNKNOWN ERROR (303)
```

## Next Gate

Use `tools/package_candidate_policy.py` on the latest ONNX only after
the run is intended as a candidate and the required sim-gate evidence
exists. This summary does not approve robot testing.
