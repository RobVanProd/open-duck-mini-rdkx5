# Local V15 CPU Gate After JAX_PLATFORMS Fix

status: `PASS_GATE_PLUMBING_HOLD_CANDIDATE_LOW_FORWARD_PROGRESS`

## Context

The local V15 CPU smoke trained a tiny phase-1 candidate, but its first phase
gate originally failed before policy evaluation because JAX still probed the
blocked ROCm backend while the evaluator only set:

```text
JAX_PLATFORM_NAME=cpu
```

The evaluator now also constrains:

```text
JAX_PLATFORMS=cpu
```

when `--jax-platform cpu` is requested.

Robot touched: `false`.

## Command

```bash
../envs/open-duck-playground/bin/python tools/eval_policy_with_actuator_bridge.py \
  --mode closed-loop-sim \
  --eval-role candidate \
  --policy outputs/analysis/local_v15_cpu_smoke/01_phase1_no_bridge_high_entropy_gait_discovery/smoke_20260624T075516Z_cpu/2026_06_24_035554_320.onnx \
  --fit-json outputs/analysis/actuator_response_fit.json \
  --playground-path ../Open_Duck_Playground \
  --env-python ../envs/open-duck-playground/bin/python \
  --command-x 0.08 \
  --duration 1 \
  --bridge-mode vanilla \
  --jax-platform cpu \
  --output-dir outputs/analysis/local_v15_cpu_smoke/phase1_gate_x008_after_jax_platforms_fix
```

## Result

The Playground contract instantiated and the candidate gate ran on CPU:

```text
jax: cpu ['TFRT_CPU_0']
overall_status: HOLD_CANDIDATE_LOW_FORWARD_PROGRESS
worker_returncode: 0
```

Candidate metrics:

```text
mean_local_vx: -0.0083 m/s
track_ratio: -0.1033
max_pitch_tracking_p95_rad: 0.1371
max_sent_target_velocity_p95_rad_s: 0.5000
max_abs_body_pitch_p95_rad: 0.0452
min_base_height_m: 0.1538
action_saturation: 0.0%
```

## Interpretation

The evaluator/platform plumbing is fixed for local CPU candidate gates. This
specific 320-step V15 smoke candidate is not meaningful as a walking candidate;
it remains a low-forward-progress hold, as expected from a tiny smoke run.

The next useful training work is a full-length recipe run or a stable GPU
runtime, not robot validation.
