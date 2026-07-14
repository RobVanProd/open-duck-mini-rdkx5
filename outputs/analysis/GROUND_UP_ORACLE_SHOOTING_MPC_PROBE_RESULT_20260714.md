# Ground-Up Oracle Shooting MPC Probe Result

status: `HOLD_ORACLE_SHOOTING_MPC_SOURCE_PROBE`

The original implementation optimized world-X and absolute world yaw under a
body-local command. It is invalid implementation evidence and is superseded by
the preregistered body-frame correction.

## Corrected result

| seed | duration | body dx | mean body vx | contacts L/R | max action | rate excess | result |
|---:|---|---:|---:|---:|---:|---:|---|
| 100 | complete | +0.08993 m | +0.08326 m/s | 5 / 6 | 1.0000 | 0 | hold: saturation |
| 101 | fall at tick 20 | -0.02911 m | -0.06930 m/s | 1 / 1 | 0.9179 | 0 | hold: fall/reverse |

This recipe is not a teacher source and does not authorize training. It is,
however, the first eligible ground-up controller in the current branch to
produce sustained, bilateral, rate-compliant forward gait in one randomized
seed under the fitted bridge.

The seed-101 trace shows roll failure. With an eight-tick (`0.16 s`) horizon,
the optimizer begins predicting terminal failure only after the state is
already inside the unrecoverable sequence. This selects one bounded causal
test: extend only the horizon to 16 ticks. Objective weights, population,
elite count, iterations, variance, seeds, constraints, and duration remain
unchanged.

No Colab, GPU, RDK-X5, or robot access occurred.
