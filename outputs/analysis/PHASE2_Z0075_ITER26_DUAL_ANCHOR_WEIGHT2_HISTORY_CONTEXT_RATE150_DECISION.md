# Phase 2 z0.0075 Iter26 Dual-Anchor Weight2 History-Context Rate150 Decision

status: `HOLD_ITER26_DUAL_ANCHOR_WEIGHT2_BROAD_REGRESSION`

## Context

Iter25 used a dual-anchor anti-regression manifest with entry sample weight
`4.0`. It preserved seeds2 and6 but regressed seeds0 and7. Iter26 repeated the
same dual-anchor strategy with a lower entry sample weight of `2.0`.

No robot tests, SSH, deploy, runtime behavior changes, grounded replay, or PPO
training were performed.

## Candidate

- path: `policy/candidates/phase2_z0075_iter26_dual_anchor_weight2_history_context_rate150_20260704/candidate.onnx`
- ONNX sha256: `c7e859c94cf1ff155927619b9c99481b71fe878f7174d27537a76fe94565dc53`
- NPZ sha256: `47860855424eee2d2282a80d07d90e50fc5d37e00a7f7fa29e68832375fb9ba6`
- aggregate manifest: `outputs/analysis/phase2_z0075_iter26_dual_anchor_weight2_aggregate_manifest.json`
- aggregate manifest sha256: `a26a8d0dd1dcdd4e0a244def7768e5ef0d74962c84880e2966bae8f2949f90ef`
- x=0.08 screen JSON sha256: `d07e2d2c95b7c040a6c6e46e33a4b3506e9a9609e141b5e771d1750ae2d37c67`
- training status: `PASS_PHASE_MODULATED_BC_FIT_SMOKE`

## Fit Metrics

- samples: `68719`
- target-rate p95: `1.368372 rad/s`
- target-rate max: `9.230712 rad/s`

## Compact x=0.08 Screen

| seed | status | samples | termination | track_ratio | mean_local_vx | body_pitch_p95 | base_height_min | max_pitch_vel_p95 | max_tracking_p95 | max_vel_excess |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 554 | `fall_or_nan` | 0.7815 | 0.0625 | 0.3381 | 0.0121 | 1.5573 | 0.1806 | 0.0000 |
| 1 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 593 | `fall_or_nan` | -0.0009 | -0.0001 | 0.2058 | 0.0655 | 1.5513 | 0.1813 | 0.0000 |
| 2 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 286 | `fall_or_nan` | -0.5101 | -0.0408 | 0.1768 | 0.0726 | 1.5622 | 0.1813 | 0.0000 |
| 6 | `PASS_CANDIDATE_SIM_GATE` | 750 | `duration_complete` | 0.3491 | 0.0279 | 0.1906 | 0.1582 | 1.5642 | 0.1887 | 0.0000 |
| 7 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 397 | `fall_or_nan` | 0.9271 | 0.0742 | 0.4199 | -0.0040 | 1.5609 | 0.1872 | 0.0000 |

## Interpretation

Weight2 did not soften the dual-anchor failure. It produced a broad regression:
only seed6 passed, while seeds0, 1, 2, and 7 fell or terminated. Like iter25,
the failures have zero corrected velocity-envelope excess.

This rules out simple global dual-anchor sample weighting as a viable
anti-regression method for the current BC student.

## Decision

Do not promote this candidate and do not run x=0.0 or robot validation.

Recommended next step:

- stop the scalar anchor-weight sweep;
- return to distribution-aware candidate selection or change the training
  objective/class rather than adding more global manifest weight;
- use iter24, not iter25 or iter26, as the latest useful live-oracle baseline.
