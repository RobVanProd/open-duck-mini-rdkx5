# Phase 2 Terrain Boundary Decision: z=0.0024

decision_status: `PASS_PHASE2_TERRAIN_RUNG_Z0024`
candidate: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
candidate_sha256: `209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b`
canonical_bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
canonical_bridge_sha256: `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0`

## Executive Summary

- `z=0.0024` is the next confirmed Phase 2 rough-terrain rung for the gain099 corrected-bridge candidate.
- The full matrix passed at `z=0.0024`: `x=0.08` no-push, `x=0.0` no-push, `x=0.08` gentle-push, and `x=0.0` gentle-push all cleared 8/8 seeds for 15 seconds.
- The critical terrain cliff starts at `z=0.0025`: seed 5 falls by backward support collapse, not by corrected actuator-envelope excess.
- Next training should ramp from `z=0.0024` toward `z=0.0025/0.0026` and target seed-5 support collapse. Do not jump directly to `z=0.0035` or `z=0.005`.
- This is offline sim evidence only: no robot tests, SSH, deploy, grounded replay, or runtime behavior changes were performed.

## Full z=0.0024 Gate Matrix

| gate | status | runs | falls | vx_mean | track_ratio_mean | max_vel_p95 | max_vel_excess | max_tracking_p95 | push_success_mean | single_support_mean | double_support_mean |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `x=0.08`, no push | `PASS` | 8 | 0 | 0.0323 | 0.4044 | 2.3999 | 0.0000 | 0.1953 | NA | 25.1833 | 74.7667 |
| `x=0.0`, no push | `PASS` | 8 | 0 | 0.0006 | NA | 0.4125 | 0.0000 | 0.0662 | NA | 0.7333 | 99.2167 |
| `x=0.08`, gentle push | `PASS` | 8 | 0 | 0.0329 | 0.4113 | 2.4084 | 0.0000 | 0.1964 | 0.9704 | 25.2333 | 74.7167 |
| `x=0.0`, gentle push | `PASS` | 8 | 0 | 0.0006 | NA | 0.4027 | 0.0000 | 0.0688 | 0.9704 | 0.7333 | 99.2167 |

## Seed-5 Terrain Boundary

The terrain-height probe used seed 5 at `x=0.08`, no pushes, fitted corrected bridge. Seed 5 is the known limiting seed for this terrain transition.

| z_scale | status | samples | termination | vx | track_ratio | max_vel_p95 | max_vel_excess | max_tracking_p95 | base_height_min |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| 0.0021 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0320 | 0.3998 | 2.4043 | 0.0000 | 0.1966 | 0.1464 |
| 0.0022 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0314 | 0.3929 | 2.3555 | 0.0000 | 0.1937 | 0.1464 |
| 0.0023 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0313 | 0.3913 | 2.3631 | 0.0000 | 0.1943 | 0.1464 |
| 0.0024 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.0303 | 0.3794 | 2.3999 | 0.0000 | 0.1953 | 0.1464 |
| 0.0025 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 70 | `fall_or_nan` | -0.2067 | -2.5832 | 2.7745 | 0.0000 | 0.1698 | 0.0736 |
| 0.0030 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 57 | `fall_or_nan` | -0.2731 | -3.4133 | 1.8114 | 0.0000 | 0.1928 | 0.0547 |
| 0.0035 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 59 | `fall_or_nan` | -0.2581 | -3.2259 | 2.4037 | 0.1259 | 0.1913 | 0.0591 |
| 0.0040 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 58 | `fall_or_nan` | -0.2530 | -3.1628 | 2.0409 | 0.0000 | 0.1839 | 0.0692 |
| 0.0045 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 59 | `fall_or_nan` | -0.2382 | -2.9770 | 2.0598 | 0.0000 | 0.1837 | 0.0792 |
| 0.0050 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 56 | `fall_or_nan` | -0.2654 | -3.3180 | 1.9250 | 0.0000 | 0.1968 | 0.0677 |

## Decision

`z=0.0024` is now the confirmed Phase 2 rough-terrain/push rung. It should be used as the next stable curriculum base for narrow physics randomization and for any training intended to cross the terrain cliff.

The immediate failing mechanism above this rung is seed-5 backward support collapse at `z=0.0025+`; the evidence does not point to actuator-envelope excess. Future work should target support timing and recovery around this boundary rather than repeating broad scalar support/behavior-prior variants already shown to hold at `z=0.005`.

## Scope

No robot tests, SSH, deploy, grounded replay, policy overwrite, or runtime behavior changes were performed for this decision.
