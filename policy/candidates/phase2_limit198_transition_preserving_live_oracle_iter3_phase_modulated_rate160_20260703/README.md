# Phase 2 Limit198 Transition-Preserving Iter3 Phase-Modulated Rate160 Candidate

status: `PASS_PHASE2_RATE160_GENTLE_PUSH_GATES`

This is the current Phase 2 offline robustness candidate. It is a behavior-
cloned, feed-forward phase/command-modulated student with the deployed policy
contract:

`obs[1,101] -> continuous_actions[1,14]`

It is slower than the `rate180` no-push candidate but clears the gentle-push
screen that held `rate180`:

- x=0.08 no-push: `8/8` seeds, `0` falls, `0` velocity excess
- x=0.08 gentle-push: `8/8` seeds, `0` falls, `0` velocity excess
- x=0.0 no-push: `8/8` seeds, `0` falls, `0` velocity excess

This candidate is not a grounded-test authorization by itself. Robot validation
remains a separate operator-approved step.

## Files

- `candidate.onnx`
  - sha256: `870242baa5f12555f4595479d74289256a0200d9733f58c63ca161203fa5bb06`
- `student.npz`
  - sha256: `c3e930600f8cd8245a4c44166a9b435462720b562295071e276f0a81587eba9d`

## Gate Summary

### x=0.08 no-push

- mean vx: `0.031384 m/s`
- track ratio: `0.392299`
- max pitch vel p95: `1.607294 rad/s`
- max velocity excess: `0.0 rad/s`
- max tracking p95: `0.185876 rad`
- min swing peak lift: `0.012210 m`
- single support: `25.3333%`

### x=0.08 gentle-push

- mean vx: `0.030462 m/s`
- track ratio: `0.380778`
- max pitch vel p95: `1.634139 rad/s`
- max velocity excess: `0.0 rad/s`
- max tracking p95: `0.187862 rad`
- min swing peak lift: `0.012667 m`
- push success: `0.9704`

### x=0.0 no-push

- mean vx: `0.000237 m/s`
- max pitch vel p95: `0.043135 rad/s`
- max velocity excess: `0.0 rad/s`
- max tracking p95: `0.033672 rad`
- double support: `100.0%`

## Source

- manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json`
- fit report: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_student_rate160/PHASE_MODULATED_BC_STUDENT.md`
- decision: `outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_RATE160_DECISION.md`
