# Rate165 Hard-Vector Projection Result

status: `PASS_OFFLINE_ARCHITECTURE_WORK_ONLY`

The exact preregistered rate projection passes both unchanged fixed-target P30
bridge gates. This was offline only; the robot and deployed runtime were not
touched.

## x=.08 full eight

- pass: `8/8`, 750/750 samples each, no falls
- mean vx: `0.0291 m/s` (floor `0.0257`)
- tracking ratio: `0.3635` (floor `0.3213`)
- single support: `22.9333%` (floor `20%`)
- p95/max velocity excess: `0 / 0`
- max pitch tracking p95: `0.1909 rad` (gate `0.20`)

## x=0 full eight

- pass: `8/8`, 750/750 samples each, no falls
- mean vx: approximately `0 m/s`
- max pitch-chain velocity p95: `0.0642 rad/s` (gate `0.07`)
- max tracking p95: `0.0317 rad`
- p95/max velocity excess: `0 / 0`

## Interpretation

The trajectory is compatible with the hardware-calibrated envelope when the
constraint is enforced exactly. Learned BC and PPO penalties failed because
they changed the behavior globally and converged toward standing; this is not
evidence that walking itself is infeasible.

Per the frozen preregistration, this pass authorizes architecture work only.
It does not authorize a runtime limiter review, deployment, staging, or motor
test. A policy candidate must internalize the measured envelope while passing
the frozen x=0 and x=.08 gates before any robot-clearance process begins.
