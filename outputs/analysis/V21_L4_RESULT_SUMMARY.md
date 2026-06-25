# V21 L4 Result Summary

status: `HOLD_PHASE_MULTI_SEED_FALLS`
timestamp: `20260625T094804Z`

V21 was launched through `google-colab-cli` on a Colab L4 session using the
pinned CUDA/JAX stack:

```text
jax: 0.7.2
jaxlib: 0.7.2
backend: gpu / cuda:0
workflow: staged-curriculum
recipe: movement_bootstrap_v21
```

The first launch attempt failed before training because the Colab upload
allowlist omitted `outputs/analysis/soft_prior_fragment_config.json`. That was
fixed in `tools/run_colab_cli_cuda_workflow.py`, and the second launch reached
training and the phase-1 gate.

## Artifact

```text
bundle: outputs/analysis/colab_cli/open-duck-l4-staged-curriculum-20260625T090247Z/open_duck_colab_cli_staged-curriculum_20260625T090314Z_artifacts.tar.gz
sha256: bec61ef4142e033f3fc20f3bbae4f2eded241d889896ab91aa35d83dbf57e609
import_summary: outputs/analysis/cuda_imports/v21_l4_20260625T090314Z/CUDA_ARTIFACT_IMPORT_SUMMARY.md
```

The large bundle and imported ONNX/checkpoint artifacts remain untracked.

## Phase 1 Training

```text
phase: phase1_soft_prior_low_command_probe
dynamics: vanilla
command_x: 0.035-0.045 during training
gate_command_x: 0.04
soft_prior_scale: -0.025
timesteps requested: 220000
final exported ONNX: 2026_06_25_091710_245760.onnx
final ONNX sha256: 5d5c788fc7b131b5a544cd25453f55650885de054dc109024b4f93e39047101c
```

## Phase 1 Gate

The x=0.04 vanilla multi-seed gate failed on every seed:

| seed | status | samples | termination | mean_local_vx_m_s | track_ratio | body_pitch_p95_rad | base_height_min_m | max_tracking_p95_rad |
|---:|---|---:|---|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | `fall_or_nan` | -0.0005 | -0.0116 | 0.0516 | 0.1536 | 0.0641 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 34 | `fall_or_nan` | -0.0853 | -2.1326 | 0.0084 | 0.1006 | 0.2147 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | `fall_or_nan` | 0.0060 | 0.1503 | 0.0174 | 0.1526 | 0.0858 |
| 3 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | `fall_or_nan` | -0.0172 | -0.4292 | 0.0812 | 0.1588 | 0.1036 |

Distribution:

```text
runs: 4
falls: 4
duration_complete: 0
samples_mean: 61.0
samples_min/max: 34 / 70
track_ratio_mean: -0.6058
mean_local_vx_m_s: -0.0242
body_pitch_p95_mean_rad: 0.0397
base_height_min_mean_m: 0.1414
```

## Decision

V21 does not pass the low-command discovery gate. Phase 2 is blocked. This is
not a deployable policy and does not approve robot validation.

The soft-prior path is technically wired and trainable, but this weak
soft-prior V21 recipe still converged to fragile/incorrect low-command behavior:
short falls, near-zero or backward forward velocity, and no completed seed.

This is not an actuator-envelope failure. Across the failed seeds, action
saturation stayed at `0%` and sent pitch-chain target velocity p95 stayed below
`0.67 rad/s`, far under the fitted actuator envelope. The blocker remains
low-command behavior discovery/stability, not target velocity.

## Trace Follow-Up

Four CPU replay traces were generated from the final V21 phase-1 ONNX for seeds
0-3. The compact trace summaries are tracked; the raw per-tick trace JSONL files
remain local generated evidence.

```text
trace_summary: outputs/analysis/V21_TRACE_SET_SUMMARY.md
status: HOLD_TRACE_SET_LOW_COMMAND_FAILURES
failure_surfaces:
  LOW_PROGRESS_TERMINATION: 3
  REVERSE_HEIGHT_COLLAPSE: 1
track_ratio_mean: -0.6216
mean_local_vx: -0.0249 m/s
action_saturation_pct_mean: 0.0
soft_prior_abs_error_mean: 0.2609
```

The trace follow-up confirms V21 is not failing from action saturation or target
velocity. The learned behavior mostly fails to make progress; one seed reverses
immediately, loses height, and terminates. It also does not closely match the
soft-prior pitch-chain action pattern, so the weak prior did not lock the final
policy into the intended low-command gait basin.
