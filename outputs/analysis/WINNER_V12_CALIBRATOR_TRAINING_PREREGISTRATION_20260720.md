# Winner-v12 Automatic Calibrator Training Preregistration

Status: `PREREGISTERED_IMPLEMENTATION_NOT_RUN`

Decision: `AUTHORIZE_WINNER_V12_CALIBRATOR_IMPLEMENTATION_AND_CPU_SMOKE_CONTRACT_ONLY`

JSON SHA-256: `1ec76a587c6fa50b92866c1632a7046ae0c6687ed17b1636b664bf45c2e8ba34`

This freezes a two-stage automatic calibration design: learn a recurrent next-response encoder from deployable observations only, freeze it, then train only bounded support-action and training-only value heads. No mass, COM, inertia, dimension, component identity, scale, caliper, or other manual per-build input enters the graph.

This v2 artifact supersedes the zero-update v1 artifact: obs[83:97] is always the reviewed fixed P30 runtime observer. P30/P31-34 selection changes only hidden physics and sensor response; it never changes or parameterizes the deployable observation path.

The next permitted action is implementation and review of one CPU smoke contract. This artifact itself runs zero optimizer steps and zero formal support cells and does not authorize full training, locomotion training, runtime implementation, hardware, Gate 5, deployment, checkpoint selection, or robot clearance.
