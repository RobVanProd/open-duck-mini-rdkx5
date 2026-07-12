# Rate165 Zero-Command Hold Result

status: `PASS_OFFLINE_STAGE_REVIEW_CANDIDATE`

The preregistered CPU-only diagnostic passed every clause.

- ONNX branch verification: max absolute error `0.0`
- x=0: `8/8` duration-complete, `0` falls, zero pitch-chain velocity,
  zero velocity excess, `0%` single support
- x=.08: `8/8` duration-complete, `0` falls, vx `0.0290809 m/s`,
  command ratio `0.363511`, `22.9333%` single support, zero velocity excess
- x=.08 metrics are numerically identical to the unchanged rate165
  hard-vector projection

This isolates the observed suspended asymmetry to the rate165 policy's
zero-command output. It supports a command-local zero-action hold; it does not
support changing knee calibration, servo gains, or the hard-vector limiter.

The two repeat-only control gaps remain unexplained. Telemetry writes are
line-buffered every tick, but the first otherwise-identical logged run had no
gap, so the evidence does not establish telemetry as the cause. Keep the
control-timing hold separate and instrument stage durations before another
physical run.

This result authorizes only review/staging. It does not authorize deployment,
installation, SSH, or robot motion.
