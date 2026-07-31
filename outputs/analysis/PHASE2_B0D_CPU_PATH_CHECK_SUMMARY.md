# Training Run Summary

status: `INFO_NON_DEPLOYABLE_TRAINING_RUN`
generated_at: `2026-06-29T07:41:53Z`
run_dir: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/phase2_domain_randomization/stage_b0d_tracking_margin_cpu_path_check/smoke_20260629T073934Z_cpu`

## Run

- platform: `cpu`
- returncode: `0`
- elapsed_s: `101.48749947400938`
- actuator_bridge_enabled: `True`
- target_rate_scale: `0.0`
- actuator_tracking_scale: `-0.04`
- non_deployable: `True`

## Latest ONNX

- path: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/phase2_domain_randomization/stage_b0d_tracking_margin_cpu_path_check/smoke_20260629T073934Z_cpu/2026_06_29_034028_80.onnx`
- step: `80`
- sha256: `9bded7475b8dd7af32d193cd6009e83c0affa1ebbf938cac96f30e83f61d8255`
- size_bytes: `883946`

## Reward Steps

| step | reward | reward_std |
|---:|---:|---:|
| 80 | 4.044833 | 1.808803 |

## ONNX Exports

| step | file | sha256 |
|---:|---|---|
| 80 | `2026_06_29_034028_80.onnx` | `9bded7475b8dd7af32d193cd6009e83c0affa1ebbf938cac96f30e83f61d8255` |

## Warning Lines

Actionable warning/error-like stderr lines found: `1`
Known benign/log-noise stderr lines found: `5050`

| known noise category | count |
|---|---:|
| `absl_preinit` | 2 |
| `tensorflow_cuda_stub_cpu` | 2 |
| `tensorflow_onednn` | 2 |
| `xla_cpu_aot_feature_mismatch` | 5044 |

First actionable lines, truncated:

```text
E0000 00:00:1782718776.323495  672436 cuda_platform.cc:52] failed call to cuInit: INTERNAL: CUDA error: Failed call to cuInit: UNKNOWN ERROR (303)
```

## Next Gate

Use `tools/package_candidate_policy.py` on the latest ONNX only after
the run is intended as a candidate and the required sim-gate evidence
exists. This summary does not approve robot testing.
