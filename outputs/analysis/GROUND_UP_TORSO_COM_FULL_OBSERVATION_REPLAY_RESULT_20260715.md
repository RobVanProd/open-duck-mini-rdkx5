# Ground-Up Torso-COM Full-Observation Replay Result

status: `PASS_EXACT_FULL_OBSERVATION_REPLAY`

- matrices: 36/36;
- behavior cells: 144/144;
- full-observation trace rows: 40,520;
- raw trace bytes: 282,562,344;
- raw replay-manifest SHA-256:
  `ac42abc8a940d97f0c0373ce624eaf2d2f803ac574e0de52c82303c7a759da07`;
- canonical sorted trace-manifest SHA-256:
  `7d7ccbe3b06e3a58546be5da02bdb138a218c08c11a0f10dea74a29d891c9f01`;
- pre-replay contract SHA-256:
  `707e1ebd93259a3579a552f8690e182a9b51b277811d460020ccdb158689bc91`.

Every matrix matches its frozen source exactly after removing only the
preregistered trace path, full-observation reporting flag, and wall-clock
fields. Every accepted trace has contiguous ticks and finite `obs_state[115]`.
All policy, fit, reference, command, reset, seed, outcome, and per-run dynamics
readback fields reproduce exactly. No behavior retry or parameter change was
made.

This pass authorizes only the already-frozen descriptive decode and
identical-state actor sensitivity analysis. It does not authorize training,
Colab, GPU/iGPU, policy or simulator behavior changes, runtime work, RDK-X5,
robot access, deployment, torque, or motors.

