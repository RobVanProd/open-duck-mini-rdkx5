# Training Run Summary

status: `INFO_NON_DEPLOYABLE_TRAINING_RUN`
generated_at: `2026-06-29T08:03:26Z`
run_dir: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/phase2_domain_randomization/stage_b0d_tracking_margin_local_gpu_32env/smoke_20260629T075706Z_gpu`

## Run

- platform: `gpu`
- returncode: `0`
- elapsed_s: `367.12779717300145`
- actuator_bridge_enabled: `True`
- target_rate_scale: `0.0`
- actuator_tracking_scale: `-0.04`
- non_deployable: `True`

## Latest ONNX

- path: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/phase2_domain_randomization/stage_b0d_tracking_margin_local_gpu_32env/smoke_20260629T075706Z_gpu/2026_06_29_040251_61440.onnx`
- step: `61440`
- sha256: `db1c78cf15cc19c63d530b0eba9734f8785e71a3369c5636e1abe5a9f4e3f80b`
- size_bytes: `884094`

## Reward Steps

| step | reward | reward_std |
|---:|---:|---:|
| 0 | 45.351303 | 38.684513 |
| 20480 | 56.486187 | 37.402966 |
| 40960 | 55.713261 | 37.787453 |
| 61440 | 61.326267 | 34.673069 |

## ONNX Exports

| step | file | sha256 |
|---:|---|---|
| 20480 | `2026_06_29_040028_20480.onnx` | `852841badfefe5fb44416f1ea16aeeada2d5ba38ef36d56e9a9fa675a3a756e7` |
| 40960 | `2026_06_29_040220_40960.onnx` | `e16a06316192cce33cf0d5c0468936b0b1b11a7d94a7495d17933981e245ef82` |
| 61440 | `2026_06_29_040251_61440.onnx` | `db1c78cf15cc19c63d530b0eba9734f8785e71a3369c5636e1abe5a9f4e3f80b` |

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
E0000 00:00:1782719828.746048  683854 cuda_platform.cc:52] failed call to cuInit: INTERNAL: CUDA error: Failed call to cuInit: UNKNOWN ERROR (303)
```

## Next Gate

Use `tools/package_candidate_policy.py` on the latest ONNX only after
the run is intended as a candidate and the required sim-gate evidence
exists. This summary does not approve robot testing.
