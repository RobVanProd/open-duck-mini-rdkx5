# Phase 2 z=0.0025 Boundary Seed Failure Analysis

status: `PASS_TARGETED_FAILURE_ANALYSIS`

## Executive Summary

The z=0.0025 boundary candidate remains the best Phase 2 reference point. Its x=0.08
failures are local, not broad:

- seeds `0` and `4` fail only by instantaneous target-velocity excursions.
- both excursions are driven by `left_hip_pitch`.
- seeds `3` and `6` fail by low forward progress with no target-velocity excess.
- all eight seeds complete the full 15 second horizon with no falls.
- x=0.0 command semantics already pass 8/8.

The later seed-consistency recipe is rejected because its global pitch-chain swing-rate
penalty removed the visible target-velocity failure but reduced forward progress. The next
correction should be targeted, not another scalar reward sweep.

## Inputs

- prior decision:
  `outputs/analysis/PHASE2_Z0025_BOUNDARY_L4_ARTIFACT_FIRST_DECISION_20260701.md`
- rejected scalar recipe decision:
  `outputs/analysis/PHASE2_Z0025_SEED_CONSISTENCY_L4_DECISION_20260701.md`
- seed gate:
  `outputs/analysis/phase2_z0025_boundary_l4_artifact_first_z0025_x008_seed_gate/candidate_seed_sweep.json`
- selected ONNX sha256:
  `b65ee4675bd6c7df97e4a7a1ecfcec48c7afee9f67c203464d2d91fb5eabac90`
- corrected bridge:
  `outputs/analysis/actuator_response_fit_corrected_knee.json`

Corrected pitch-chain instantaneous limits used here:

| joint | limit rad/s |
|---|---:|
| `left_hip_pitch` | 2.50 |
| `left_knee` | 3.25 |
| `left_ankle` | 2.75 |
| `right_hip_pitch` | 2.25 |
| `right_knee` | 2.75 |
| `right_ankle` | 2.00 |

## Per-Seed Failure Surface

| seed | status | vx | track ratio | max excess | driver | left_hip_pitch max | left_knee max | left_ankle max | right_hip_pitch max | right_knee max | right_ankle max |
|---:|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 0.0211 | 0.2641 | 0.5350 | `left_hip_pitch` | 3.0350 | 2.0183 | 2.0494 | 1.6361 | 1.9603 | 1.6778 |
| 1 | `PASS_CANDIDATE_SIM_GATE` | 0.0215 | 0.2692 | 0.0000 | `none` | 2.1306 | 2.0678 | 1.8924 | 1.7503 | 2.0874 | 1.6478 |
| 2 | `PASS_CANDIDATE_SIM_GATE` | 0.0218 | 0.2723 | 0.0000 | `none` | 2.2153 | 2.1096 | 1.8935 | 1.7184 | 1.8652 | 1.4665 |
| 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0169 | 0.2110 | 0.0000 | `none` | 2.2549 | 2.0876 | 1.9837 | 1.6852 | 1.8821 | 1.4650 |
| 4 | `HOLD_CANDIDATE_TARGET_VELOCITY` | 0.0215 | 0.2691 | 0.2280 | `left_hip_pitch` | 2.7280 | 1.9938 | 2.0276 | 1.7237 | 1.9289 | 1.5029 |
| 5 | `PASS_CANDIDATE_SIM_GATE` | 0.0203 | 0.2535 | 0.0000 | `none` | 2.2173 | 2.2645 | 1.8758 | 1.6943 | 1.9406 | 1.6144 |
| 6 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0197 | 0.2465 | 0.0000 | `none` | 2.4524 | 1.9557 | 2.0119 | 1.7308 | 1.8519 | 1.4723 |
| 7 | `PASS_CANDIDATE_SIM_GATE` | 0.0205 | 0.2565 | 0.0000 | `none` | 2.0942 | 2.2205 | 2.0200 | 1.7026 | 1.8525 | 1.4955 |

## Interpretation

The velocity failures are not caused by a generally over-aggressive pitch chain. They are
isolated instantaneous `left_hip_pitch` spikes:

- seed `0`: `left_hip_pitch` reaches `3.0350 rad/s`, `0.5350 rad/s` over limit.
- seed `4`: `left_hip_pitch` reaches `2.7280 rad/s`, `0.2280 rad/s` over limit.

The low-progress seeds are different:

- seed `3`: no velocity excess, but vx is `0.0169 m/s`.
- seed `6`: no velocity excess, but vx is `0.0197 m/s`, just below the gate.

The rejected seed-consistency recipe penalized all swing pitch-chain joints and made the
compact x=0.08 track ratio worse (`0.2350 -> 0.1732`). That falsifies broad scalar
rate-penalty tuning for this boundary issue.

## Next Recommendation

Use the prior boundary candidate as the reference. The next correction should:

1. Target only the `left_hip_pitch` instantaneous excursion on seeds `0` and `4`.
2. Avoid global all-pitch-chain swing-rate penalties.
3. Preserve x=0.0 quiet behavior and full-horizon no-fall behavior.
4. Add only a minimal progress correction for seeds `3` and `6`, because they are
   stable and already close to the forward-progress threshold.

Robot validation remains blocked.
