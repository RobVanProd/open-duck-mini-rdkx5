# Training Run Summary

status: `HOLD_NO_ONNX_EXPORT`
generated_at: `2026-06-29T07:55:33Z`
run_dir: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/phase2_domain_randomization/stage_b0d_tracking_margin_local_gpu_scale/smoke_20260629T075435Z_gpu`

## Run

- platform: `gpu`
- returncode: `-6`
- elapsed_s: `47.88841063300788`
- actuator_bridge_enabled: `True`
- target_rate_scale: `0.0`
- actuator_tracking_scale: `-0.04`
- non_deployable: `True`

## Reward Steps

| step | reward | reward_std |
|---:|---:|---:|

## ONNX Exports

| step | file | sha256 |
|---:|---|---|

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
E0000 00:00:1782719678.406779  682259 cuda_platform.cc:52] failed call to cuInit: INTERNAL: CUDA error: Failed call to cuInit: UNKNOWN ERROR (303)
```

## Next Gate

Use `tools/package_candidate_policy.py` on the latest ONNX only after
the run is intended as a candidate and the required sim-gate evidence
exists. This summary does not approve robot testing.
