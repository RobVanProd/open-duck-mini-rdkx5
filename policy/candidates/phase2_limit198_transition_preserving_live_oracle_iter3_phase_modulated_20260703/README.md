# Phase 2 Limit198 Transition-Preserving Iter3 Phase-Modulated Student

status: `HOLD_PHASE_MODULATED_STUDENT_TARGET_VELOCITY`

This candidate was trained offline from the iter3 live-oracle aggregate
manifest. It is a behavior-cloned, feed-forward phase/command-modulated student
with the deployed policy contract:

`obs[1,101] -> continuous_actions[1,14]`

It is **not promoted**. The x=0.08 corrected-bridge screen was stopped after
three consecutive seeds held on target velocity. The repeated failure was a
right-ankle max target-rate excess:

- right_ankle max sent target velocity: `2.10934579372406 rad/s`
- corrected right_ankle limit: `2.0 rad/s`
- excess: `0.10934579372406006 rad/s`

No robot test, SSH, deploy, grounded replay, or PPO training was performed.

## Files

- `candidate.onnx`
  - sha256: `0387e8f072cb6e2558b8eeee687331c0d8cae6e548a8a3291c2ab7509f9d0801`
- `student.npz`
  - sha256: `f42e7714a0abaabc1148b7bcb42d5cd6df5aed4b30538c15fb70a7f542eadf73`

## Source

- manifest: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_run/live_oracle_dagger_aggregate_manifest.json`
- fit report: `outputs/analysis/phase2_limit198_transition_preserving_live_oracle_iter3_student/PHASE_MODULATED_BC_STUDENT.md`
- gate decision: `outputs/analysis/PHASE2_LIMIT198_TRANSITION_PRESERVING_LIVE_ORACLE_ITER3_PHASE_MODULATED_DECISION.md`
