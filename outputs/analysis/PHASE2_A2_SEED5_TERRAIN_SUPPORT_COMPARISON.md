# Phase 2 A2 Seed-5 Terrain Support Comparison

status: `HOLD_Z005_RECOVERY_MARGIN_BOUNDARY`

This is an offline corrected-bridge candidate diagnostic. It did not train,
SSH, deploy, run robot tests, grounded replay, or change runtime behavior.

## Purpose

The nominal home-hold source falls on rough-terrain seed 5 at both z=0.002 and
z=0.005. This comparison checks the actual Phase A2 candidate, because that
candidate is known to survive lower rough-terrain rungs through learned
closed-loop behavior.

## Candidate

```text
policy:
  policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx

sha256:
  209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b

bridge:
  outputs/analysis/actuator_response_fit_corrected_knee.json
```

## Gate Comparison

Both runs used `rough_terrain_backlash`, seed `5`, `command_x=0.0`, fitted
corrected bridge, CPU MJX, and a 2-second horizon.

| terrain z scale | status | samples | termination | mean vx | base height min | body pitch p95 | max pitch tracking p95 |
|---:|---|---:|---|---:|---:|---:|---:|
| `0.002` | `PASS_CANDIDATE_SIM_GATE` | 100 | `duration_complete` | `0.0271` | `0.1462` | `0.0606` | `0.1412` |
| `0.005` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 61 | `fall_or_nan` | `-0.2589` | `0.0512` | `0.0759` | `0.1953` |

The z=0.005 failure remains inside the corrected actuator envelope:

| terrain z scale | max sent target p95 | max velocity excess | action saturation |
|---:|---:|---:|---:|
| `0.002` | `1.1797 rad/s` | `0.0000` | `0.00%` |
| `0.005` | `1.2575 rad/s` | `0.0000` | `0.00%` |

## Early Divergence

The two traces are nearly identical through the initial contact transient, then
z=0.005 drifts into backward pitch while z=0.002 recenters and settles.

| tick | z scale | pitch | base height | local vx | contacts |
|---:|---:|---:|---:|---:|---|
| 20 | `0.002` | `-0.173` | `0.171` | `0.035` | `[1, 1]` |
| 20 | `0.005` | `-0.196` | `0.174` | `0.008` | `[1, 1]` |
| 30 | `0.002` | `-0.179` | `0.170` | `-0.002` | `[1, 1]` |
| 30 | `0.005` | `-0.253` | `0.175` | `-0.093` | `[1, 1]` |
| 40 | `0.002` | `-0.110` | `0.171` | `0.110` | `[1, 1]` |
| 40 | `0.005` | `-0.346` | `0.181` | `-0.184` | `[1, 1]` |
| 50 | `0.002` | `0.021` | `0.161` | `0.108` | `[1, 1]` |
| 50 | `0.005` | `-0.699` | `0.170` | `-0.605` | `[1, 1]` |
| 60 | `0.002` | `0.061` | `0.160` | `-0.037` | `[1, 1]` |
| 60 | `0.005` | `-1.407` | `0.051` | `-1.519` | `[0, 0]` |

Pitch-chain action deltas between z=0.005 and z=0.002 stay small through the
early divergence. At tick 40, pitch-chain action deltas are roughly:

```text
left_hip_pitch -0.0017
left_knee       0.0011
left_ankle      0.0026
right_hip_pitch -0.0166
right_knee      0.0060
right_ankle     0.0192
```

This suggests the z=0.005 terrain perturbation drives the body state out of the
Phase A2 support basin before the policy produces a sufficiently different
recovery action.

## Decision

Do not return to nominal-home scripted sources. Do not fit another student on
the current z=0.005 aggregate. The next source should be policy-derived from
the Phase A2 closed-loop recovery behavior, with an explicit objective to widen
the seed-5 recovery basin between z=0.002 and z=0.005.

Recommended next source direction:

1. mine or generate recovery labels around the tick 20-60 divergence window;
2. bias labels toward the z=0.002 settling behavior while preserving corrected
   velocity limits;
3. test a short seed-5 support gate before any 8-seed source gate;
4. only then resume DAgger/student fitting.
