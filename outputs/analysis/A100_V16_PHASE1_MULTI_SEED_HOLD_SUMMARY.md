# A100 V16 Phase-1 Multi-Seed Hold Summary

status: `HOLD_PHASE_MULTI_SEED_FALLS`

## Context

V16 phase 1 was rerun on a fresh A100 session after hardening
`tools/run_candidate_seed_sweep.py` with per-seed progress markers, subprocess
group cleanup, and partial JSON writes.

Command shape:

```text
recipe: movement_bootstrap_v16
phase: phase1_v5_anchor_mild_bridge_consistency
restore: V5 trainable checkpoint
timesteps: 120000
bridge: mild actuator bridge
gate: x=0.08, vanilla bridge, seeds 0-3, 5 seconds
```

## Training Result

Phase-1 training completed on A100:

```text
training_status: PASS_SMOKE_RUN
platform: gpu
final_step: 122880
final_candidate_onnx:
  /content/open_duck_staged_curriculum_cli/01_phase1_v5_anchor_mild_bridge_consistency/smoke_20260624T130700Z_gpu/2026_06_24_131611_122880.onnx
```

The downloaded artifact bundle includes ONNX exports at:

```text
40960
81920
122880
```

## Multi-Seed Gate Result

The patched gate produced all four seed results:

| seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min |
|---:|---|---:|---|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0060 | 0.0748 | 0.2889 | 0.1494 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 35 | `fall_or_nan` | -0.0504 | -0.6297 | 0.0035 | 0.0775 |
| 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0072 | 0.0898 | 0.2626 | 0.1483 |
| 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | -0.0034 | -0.0426 | 0.2701 | 0.1477 |

Aggregate:

```text
runs: 4
falls: 1
duration_complete: 3
track_ratio_mean: -0.1269
mean_local_vx_mean: -0.0102 m/s
body_pitch_p95_mean: 0.2063 rad
base_height_min_mean: 0.1307 m
```

## Interpretation

V16 fixed the infrastructure path but did not fix the behavior. The V5-anchored
mild-bridge continuation still collapses into low/reverse forward progress
across seeds, with one early fall.

This is not deployable and does not approve robot validation.

Useful next offline checks:

```text
1. Sweep the intermediate ONNX exports at 40960 and 81920.
2. If an intermediate checkpoint has better forward-progress distribution,
   branch from that checkpoint.
3. If all V16 checkpoints are low/reverse progress, stop extending the V5-anchor
   continuation and design the next recipe around hard positive progress from
   the start.
```

## Intermediate Checkpoint Follow-up

The intermediate exports were checked after the A100 run:

| checkpoint | falls | track_ratio_mean | mean_local_vx_mean | conclusion |
|---|---:|---:|---:|---|
| `40960` | 1/4 | -0.0508 | -0.0041 m/s | low/reverse progress |
| `81920` | 1/4 | -0.1072 | -0.0086 m/s | low/reverse progress |
| `122880` | 1/4 | -0.1269 | -0.0102 m/s | low/reverse progress |

The V16 failure is present throughout phase 1. There is no better intermediate
V16 checkpoint to branch from.

Next recipe direction:

```text
Stop extending the V5-anchor continuation.
Use a structural break that makes positive signed progress non-negotiable from
the start, while keeping stability/contact penalties active enough to avoid the
old lunge/collapse modes.
```

No robot tests, SSH, deployment, runtime behavior changes, or policy deployment
were performed.
