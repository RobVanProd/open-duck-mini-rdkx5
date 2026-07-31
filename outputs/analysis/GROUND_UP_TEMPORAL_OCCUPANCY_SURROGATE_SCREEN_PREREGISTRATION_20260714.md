# Ground-Up Temporal-Occupancy Surrogate Screen Preregistration

status: `PREREGISTERED_CPU_DIAGNOSTIC_ONLY`

## Evidence boundary

The full-horizon gate fails on temporal occupancy: a pitch-chain joint may
exceed `0.20 rad` on at most 30 of 600 ticks. The closed squared-hinge reward
instead optimized exceedance magnitude and loses gradient as the residual
approaches the boundary. Linear hinge ranked the frozen gate worse and was
rejected. The stateful pitch-rate screen then changed endpoint behavior but
produced no persistent half/final winner.

This screen asks one narrower unresolved question before any more training:
whether a smooth approximation to the boundary indicator ranks the exact
occupancy quantity better than both existing hinge diagnostics.

## Frozen candidates

For pitch-chain absolute error `e`, threshold `h = 0.20`, and temperature
`tau`, the diagnostic is:

`mean(sigmoid((e - h) / tau))`

The maximum conditional RMS excess in the strongest T3-final frozen traces is
exactly `0.01345617569523898 rad`. Before surrogate outcomes are calculated,
the only candidates are frozen at 1/4, 1/2, and 1 times that value:

| candidate | temperature (rad) |
|---|---:|
| `S1_QUARTER_RMS` | 0.003364043923809745 |
| `S2_HALF_RMS` | 0.00672808784761949 |
| `S3_FULL_RMS` | 0.01345617569523898 |

## Frozen scoring and advancement

The 18 unique seed-100 policy/checkpoint/command traces determine rankings;
seed 101 must reproduce every diagnostic value exactly. Primary scoring is
ordered-pair discordance against the exact maximum-joint exceedance fraction.
Secondary scoring repeats the prior maximum-joint-p95 comparison. Ties in the
target quantity are excluded.

A candidate advances only if its primary and secondary discordance counts are
both strictly lower than both squared- and linear-hinge baselines, all 36
traces and input hashes validate, and seed reproduction is exact. Selection is
lower primary discordance, lower secondary discordance, higher exact-occupancy
correlation, then larger temperature. Passing authorizes only a CPU
implementation contract. It does not authorize a training run.

No Colab, local GPU, RDK-X5, robot, deployment, torque, or motor access is
authorized by this preregistration.
