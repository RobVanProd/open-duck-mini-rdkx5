# Phase 2 z=0.005 vs z=0.0024 Seed-5 Trace Decision

status: `HOLD_Z005_TERRAIN_SUPPORT_COLLAPSE`

This is an offline trace decision. It did not run robot tests, SSH, deploy, grounded replay,
or change runtime behavior.

## Inputs

- passing trace: `outputs/analysis/phase2_swing_clearance_trace_x008_z0024/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/seed_005/trace.jsonl`
- failing trace: `outputs/analysis/phase2_stagea2_gain099_z005_seed5_trace_cpu/gain099/seed_005/trace.jsonl`
- candidate: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- command: `x=0.08`
- comparison artifact: `outputs/analysis/phase2_z005_vs_z0024_seed5_trace_compare/PHASE2_Z005_VS_Z0024_SEED5_TRACE_COMPARE.md`

## Result

The same seed and candidate survive the rough `z=0.0024` trace for 15s, but collapse on
`z=0.005` at 1.10s.

| trace | samples | vx_mean | abs_pitch_p95 | base_height_min | double_support_pct | termination |
|---|---:|---:|---:|---:|---:|---|
| `z0024_seed5_pass` | 750 | 0.0303 | 0.1332 | 0.1464 | 77.07 | duration |
| `z005_seed5_fail` | 56 | -0.2654 | 1.2936 | 0.0677 | 91.07 | done |

First divergence appears before the height collapse:

| metric | first divergent tick | time_s | delta |
|---|---:|---:|---:|
| `local_vx` | 24 | 0.48 | -0.0573 |
| `body_pitch` | 24 | 0.48 | -0.0550 |
| `base_height` | 51 | 1.02 | -0.0231 |

The failing trace is therefore not primarily a late action-rate or actuator-envelope excess.
It first loses forward velocity and pitch stability, then collapses vertically.

## Actuator Envelope Read

The failing z=0.005 trace stays below the corrected per-joint pitch-chain velocity limits:

| joint | z005 sent_vel_p95 | corrected limit |
|---|---:|---:|
| `left_hip_pitch` | 1.4333 | 2.50 |
| `left_knee` | 1.9250 | 3.25 |
| `left_ankle` | 1.0470 | 2.75 |
| `right_hip_pitch` | 1.1776 | 2.25 |
| `right_knee` | 1.8148 | 2.75 |
| `right_ankle` | 1.5978 | 2.00 |

Tracking is near the gate edge, but the failure is not caused by over-commanding the
corrected envelope. The z=0.0024 pass actually uses larger pitch-chain target velocities
and survives, which further points away from target-rate clipping as the limiting factor.

## Interpretation

The z=0.005 failure is a terrain/support robustness failure:

- the policy becomes backward-biased early at z=0.005,
- pitch instability starts at roughly the same time as velocity divergence,
- double support rises to 91% before termination,
- base height collapse happens after the motion/pitch divergence,
- the candidate is not asking for illegal corrected-bridge target velocities.

This supports the current Phase 2 status: the scalar support/swing reward branch is
exhausted. Another scalar reward or smoothing run is not justified by this trace.

## Decision

Next offline work should move to a structural/corrected-source path rather than another
scalar support reward:

1. rebuild a corrected-bridge oracle/source for rough-terrain support states, or
2. run the phase-aware/live-oracle student path under the canonical corrected evaluator,
   with terrain/support failures included in the visited-state relabel set.

Do not promote the current candidate for grounded terrain testing. Robot validation remains
blocked until a candidate clears the corrected-bridge z=0.005 robustness gate.
