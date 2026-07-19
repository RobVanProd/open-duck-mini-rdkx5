# Winner-v2 Offline Asset-Lock Policy Review — 2026-07-19

Decision: `HOLD_STALE_OFFLINE_ASSET_LOCK`

The runtime asset lock is checked against the current policy result, corrected
handoff package, runtime sources, formal evidence and frozen offline authority.
It is not accepted unless every identity matches and the reduced artifact uses
the preregistered exact-zero teacher-forced observation gate.

## Current issues

- `current_policy_acceptance_hash_exact`
- `reduced_observation_gate_exact_zero`

Locked policy result: `fab1feaa8d136fed0ab33d5590d0eec88ef90d8f` /
`17ddae42b67cd17c559ca28be07f8e9439140c371745f37018a3d9eedbabf06a`.

Current policy result SHA-256:
`852b71085db8458f53a71b5964bbb9a2038c7d9fcd8ffae5e2a4e3fd1ef8f667`.

The present hold does not change the accepted recursive CPU outcome. It blocks
freezing a stale deployment asset set. No formal outcome rerun, threshold
change, robot, RDK-X5, motor, torque, deployment, GPU or iGPU action is
authorized by this review. Robot clearance remains `NO`.
