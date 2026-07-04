# Phase 2 z0.0075 Iter23 Startup-Window Left-Hip-Pitch Limit Decision

status: `HOLD_ITER23_STARTUP_WINDOW_RELABEL_DESTABILIZES`

Offline-only analysis. No robot tests, SSH, deploy, grounded replay, runtime
behavior change, or PPO training was performed.

## Purpose

Iter22 showed that a single high-weight startup relabel removed the Iter21
left-hip-pitch max target-velocity spike but destabilized the gait. Iter23
tested a less isolated local correction:

- startup window: ticks `8-13`
- samples: `6`
- sample_weight_each: `30.0`
- changed tick: `11`
- changed joint: `left_hip_pitch`
- old velocity: `2.701429 rad/s`
- new velocity: `2.500000 rad/s`

Neighboring ticks kept their original actions as local anchors.

## Artifacts

- relabel report: `outputs/analysis/PHASE2_Z0075_ITER23_STARTUP_WINDOW_LHP_LIMIT_RELABEL.md`
- merged manifest: `outputs/analysis/phase2_z0075_iter23_startup_window_lhp_limit_merged_manifest.json`
- student report: `outputs/analysis/PHASE2_Z0075_ITER23_STARTUP_WINDOW_LHP_LIMIT_RATE150_STUDENT.md`
- candidate: `policy/candidates/phase2_z0075_iter23_startup_window_lhp_limit_rate150_20260704/candidate.onnx`
- candidate_sha256: `d11572d8794dc2249e0e3e4676cbc591383012b1aa43b40ee7c4590d42e7af43`

## Result

Seed0 full gate, rough terrain z-scale `0.0075`, fitted corrected bridge,
intermediate push schedule:

| metric | value |
|---|---:|
| status | `HOLD_CANDIDATE_FALL_OR_TERMINATION` |
| samples | 113 |
| termination | `fall_or_nan` |
| max target velocity excess | 0.0000 |
| max pitch tracking p95 | 0.2092 |
| body pitch p95 | 1.0225 |
| base height min | 0.0058 |
| track ratio | 2.2495 |

## Interpretation

- The startup-window relabel removed the corrected-envelope max violation.
- It still destabilized into an early lunge/fall.
- Together with Iter22, this closes single-point and short-window startup
  relabeling as the fix for Iter21.
- Iter21 remains the useful near miss: full-duration seeds `0,2,6`, acceptable
  posture/tracking/progress, one startup max spike.

## Next Direction

Do not continue startup relabel variants. The repeated pattern is:

```text
remove the spike directly -> policy leaves the stable gait manifold -> lunge/fall
```

The next branch should target the runtime/evaluator gate mechanism or policy
representation rather than more local BC relabeling:

1. Check whether the tick-11 max spike is caused by startup target/history
   initialization rather than the steady-state policy.
2. If yes, evaluate a documented startup target-history initialization or
   warmup-gate treatment in sim only.
3. If no, move to live-oracle DAgger / phase-memory representation instead of
   more static BC relabels.

The Phase 2 goal remains active.
