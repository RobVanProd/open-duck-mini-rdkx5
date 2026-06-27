# DAgger-8 Observation-Consistency Initialization Screen

status: `HOLD_STATIC_BC_INIT_SCREEN`

## Purpose

The first DAgger-8 observation-consistency MLP preserved six-seed completion
but still failed seeds 1 and 7. This screen tested whether that result was a
single unlucky MLP initialization or a repeatable static-BC failure mode.

The screen reused the same DAgger-7 targeted recovery manifest, 128x128 MLP,
target-rate regularization, fitted actuator bridge, and observation-consistency
settings. It evaluated only the hard seeds to keep the test bounded:

```text
seeds: 1, 7
mlp_seeds: 9, 10, 11
obs_noise_std: 0.02
obs_consistency_scale: 0.1
target_rate_scale: 0.1
target_rate_limit: 3.75 rad/s
command_x: 0.08
duration: 10 s
bridge: fitted
```

## Results

| mlp seed | status | train p95 abs error |
|---:|---|---:|
| 9 | `HOLD_BC_REPLAY_TERMINATED` | 0.0531 |
| 10 | `HOLD_BC_REPLAY_TERMINATED` | 0.0541 |
| 11 | `HOLD_BC_REPLAY_TERMINATED` | 0.0548 |

| mlp seed | rollout seed | samples | mean vx | track ratio | vy95 | base height min | sent vel p95 | tracking p95 | dominant contact |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 9 | 1 | 33 | 0.0089 | 0.1113 | 1.2589 | 0.0695 | 1.9630 | 0.1537 | `10` 90.9% |
| 9 | 7 | 32 | 0.0134 | 0.1673 | 1.1491 | 0.0903 | 2.9420 | 0.1641 | `01` 81.2% |
| 10 | 1 | 32 | 0.0133 | 0.1667 | 1.2096 | 0.0813 | 2.2257 | 0.1657 | `10` 87.5% |
| 10 | 7 | 33 | 0.0144 | 0.1795 | 1.2194 | 0.0702 | 2.2719 | 0.1361 | `01` 75.8% |
| 11 | 1 | 32 | 0.0069 | 0.0859 | 1.1722 | 0.0842 | 2.1777 | 0.1467 | `10` 87.5% |
| 11 | 7 | 32 | 0.0189 | 0.2367 | 1.1833 | 0.0814 | 2.5043 | 0.1540 | `01` 87.5% |

## Decision

The hard-seed failure is repeatable across MLP initializations. Observation
consistency and MLP random seed changes do not rescue seeds 1 and 7. Both seeds
still fail around the first support-transition window, with large lateral
velocity and low base height:

- seed 1 remains a left-support lateral/height-collapse problem
- seed 7 remains a right-support collapse/action-fit problem

This closes the cheap static-BC stochasticity branch. The next useful
deployable-policy work should not be another MLP initialization or uniform
static-label DAgger pass. It should either:

1. add a closed-loop recovery/stabilization objective that directly penalizes
   lateral blowout and height collapse in the hard support states, or
2. switch to PPO/fine-tuning from the best BC student with the fitted bridge
   active and hard-seed recovery explicitly included in the objective.

No robot tests, SSH, deploy, runtime behavior changes, or full PPO training were
performed.
