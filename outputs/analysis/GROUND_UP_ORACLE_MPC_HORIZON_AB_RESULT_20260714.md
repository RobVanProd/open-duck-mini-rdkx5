# Ground-Up Oracle MPC Horizon A/B Result

status: `NO_ORACLE_SHOOTING_MPC_SOURCE_WINNER`

## Frozen comparison

| arm | seed | duration | body dx | mean body vx | contacts L/R | max action | rate excess | result |
|---|---:|---|---:|---:|---:|---:|---:|---|
| C0 H8 | 100 | complete | +0.08993 m | +0.08326 m/s | 5 / 6 | 1.0000 | 0 | hold: saturation |
| C0 H8 | 101 | fall at tick 20 | -0.02911 m | -0.06930 m/s | 1 / 1 | 0.9179 | 0 | hold: fall/reverse |
| C1 H16 | 100 | fall at tick 46 | +0.21035 m | +0.22377 m/s | 9 / 8 | 0.9578 | 0 | hold: pitch/height fall |
| C1 H16 | 101 | fall at tick 31 | +0.09528 m | +0.14887 m/s | 3 / 1 | 1.0000 | 0 | hold: pitch/height fall and saturation |

H16 changed only the horizon from 8 to 16 ticks. It did not produce either of
the two required source passes. Both H16 trajectories generated positive
body-forward propulsion and remained inside the measured action-rate envelope,
but terminated with pitch near `0.81 rad`. Final body-local x velocity was
`0.6837 m/s` for seed 100 and `0.6562 m/s` for seed 101, far above the requested
`0.074 m/s` command.

## Decision

The preregistered prediction that horizon alone could expose a recoverable
sequence is falsified. Per the preregistration, horizon and weight tuning for
this fixed shooting formulation are closed. It is not an eligible corrective
teacher and authorizes neither data collection nor policy training.

The traces isolate a structural defect in the source objective: it rewards
unbounded forward displacement and terminal forward speed instead of bounded
command tracking, while stability remains a soft tradeoff until the discrete
fall penalty is crossed. A future experiment, if authorized by a new
preregistration, must be a materially new viability/command-tracking
formulation rather than another numeric sweep. Its first gate remains two of
two randomized CPU seeds completing without fall, saturation, or rate excess.

No Colab, GPU, RDK-X5, or robot access occurred.
