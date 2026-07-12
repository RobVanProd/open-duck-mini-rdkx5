# Rate165 Hard-Vector Suspended x=0 Result

status: `PASS_NUMERIC_AWAIT_VISUAL`

The explicitly approved suspended x=0 run completed once for 15 seconds with
the exact hard-vector limits.

- samples: `747/747`, ticks `0..746`
- command: x=`0.0`, unique command count `1`
- vector telemetry: exact
  `5.24,5.24,1.50,1.50,1.75,5.24,5.24,5.24,5.24,5.24,5.24,1.25,1.00,1.25`
- CRC/read/write/reset errors: `0/0/0/0`
- dt p95/max: `0.02009 / 0.02212 s`
- action saturation: `0%`
- post-startup tracking spikes above `0.05 rad`: `0`
- left hip/knee p95: `0.0088 / 0.0143 rad`
- right hip/knee p95: `0.0072 / 0.0060 rad`
- largest p95 values are neck/head yaw `0.0219/0.0280 rad`; warning only,
  below the `0.05 rad` hold threshold and without timing/bus correlation
- analyzer holds: none
- cleanup: torque-off terminal marker, no runtime process, no serial owner

The numeric x=0 gate passes. Visual symmetry, normal phase relation, and lack
of jerk/oscillation remain pending. Suspended x=.08 is not authorized by this
result and must not run until visual x=0 review and separate approval.

