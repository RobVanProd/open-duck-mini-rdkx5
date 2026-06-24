# A100 V17 Phase-1 Multi-Seed Hold Summary

status: `HOLD_PHASE_MULTI_SEED_FALLS`

## Context

V17 was launched as a structural break after the V5/V16 anchor lineage failed
to produce consistent forward progress. Unlike V16, V17 did not restore from
the V5 checkpoint.

Command shape:

```text
recipe: movement_bootstrap_v17
phase: phase1_hard_signed_progress_discovery
restore: none
training bridge: disabled
command range: x=0.04-0.06
gate: x=0.08, vanilla bridge, seeds 0-3, 5 seconds
```

## Training Result

Phase-1 training completed on A100:

```text
training_status: PASS_SMOKE_RUN
platform: gpu
final_step: 276480
final_candidate_onnx:
  /content/open_duck_staged_curriculum_cli/01_phase1_hard_signed_progress_discovery/smoke_20260624T141603Z_gpu/2026_06_24_142512_276480.onnx
```

The downloaded artifact bundle includes ONNX exports at:

```text
92160
184320
276480
```

## Multi-Seed Gate Result

The phase gate produced all four seed results:

| seed | status | samples | termination | mean_local_vx | track_ratio | body_pitch_p95 | base_height_min |
|---:|---|---:|---|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0029 | 0.0358 | 0.1559 | 0.1536 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 33 | `fall_or_nan` | -0.0982 | -1.2270 | 0.0015 | 0.1026 |
| 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | 0.0045 | 0.0560 | 0.1185 | 0.1525 |
| 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 250 | `duration_complete` | -0.0012 | -0.0152 | 0.1279 | 0.1551 |

Aggregate:

```text
runs: 4
falls: 1
duration_complete: 3
track_ratio_mean: -0.2876
mean_local_vx_mean: -0.0230 m/s
body_pitch_p95_mean: 0.1009 rad
base_height_min_mean: 0.1409 m
```

## Interpretation

V17 changed the lineage but did not escape the core low/reverse-progress
failure. Three seeds survived by barely moving, and one seed failed early with
reverse motion and a base-height collapse.

This is not deployable and does not approve robot validation.

The useful conclusion is narrower:

```text
hard signed progress + no phase-1 bridge + no V5 restore is still insufficient
to produce coherent positive forward locomotion across seeds
```

The next offline step should not be a small V17 phase-2 continuation. Phase 1
already failed the required discovery gate. Before another large A100 recipe,
inspect why the phase-1 reward still permits near-zero or reverse motion:

```text
1. replay V17 phase-1 rollout reward components for seeds 0-3
2. compare commanded progress penalty magnitude against posture/contact terms
3. verify local velocity sign convention in the reward and evaluator
4. check whether the policy is learning a crouched support behavior that scores
   better than stepping
5. only then design the next recipe
```

No robot tests, SSH, deployment, runtime behavior changes, or policy deployment
were performed.
