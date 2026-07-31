# Phase 2 z0.0075 Iter22 Startup Left-Hip-Pitch Limit Decision

status: `HOLD_ITER22_STARTUP_LIMIT_RELABEL_DESTABILIZES`

Offline-only analysis. No robot tests, SSH, deploy, grounded replay, runtime
behavior change, or PPO training was performed.

## Purpose

Iter21 rate150 completed focused seeds `0,2,6` but held on one repeated
left-hip-pitch max target-velocity spike at startup tick 11:

- previous target: `-0.797172 rad`
- old target: `-0.743143 rad`
- old velocity: `2.701429 rad/s`
- corrected limit: `2.500000 rad/s`

Iter22 added a one-row high-weight relabel at that exact full-observation state:

- new target: `-0.747172 rad`
- new velocity: `2.500000 rad/s`
- old action: `-0.452573`
- new action: `-0.468687`
- sample_weight: `120.0`

## Artifacts

- relabel report: `outputs/analysis/PHASE2_Z0075_ITER22_STARTUP_LHP_LIMIT_RELABEL.md`
- merged manifest: `outputs/analysis/phase2_z0075_iter22_startup_lhp_limit_merged_manifest.json`
- student report: `outputs/analysis/PHASE2_Z0075_ITER22_STARTUP_LHP_LIMIT_RATE150_STUDENT.md`
- candidate: `policy/candidates/phase2_z0075_iter22_startup_lhp_limit_rate150_20260704/candidate.onnx`
- candidate_sha256: `a0e123f9bdcd1779434bd2df52222ea3b15dbae84ae5a8bb067f9805626a0841`

## Result

Seed0 full gate, rough terrain z-scale `0.0075`, fitted corrected bridge,
intermediate push schedule:

| metric | value |
|---|---:|
| status | `HOLD_CANDIDATE_FALL_OR_TERMINATION` |
| samples | 145 |
| termination | `fall_or_nan` |
| max target velocity excess | 0.0000 |
| max pitch tracking p95 | 0.2007 |
| body pitch p95 | 0.9096 |
| base height min | 0.0078 |
| track ratio | 1.8875 |

## Interpretation

- The one-row relabel successfully removed the target-velocity max violation.
- It destabilized the policy into a lunge/fall, similar to the stronger
  rate-regularized reg02 branch.
- The startup spike is not an isolated label that can be patched independently
  with a single high-weight sample.
- Iter21 remains the better near-miss candidate: full-duration focused seeds,
  acceptable tracking/posture/progress, but one startup left-hip-pitch max spike.

## Next Direction

Do not continue single-row startup relabels. The remaining fix likely needs a
small startup-window continuity treatment, not a single-point correction:

1. Use a short window around ticks `8-13`.
2. Preserve the local action trajectory shape while capping the one illegal
   target step.
3. Avoid global gain and broad target-rate retraining, both already rejected.
4. Re-test seed0 before seeds `2,6`.

The Phase 2 goal remains active.
