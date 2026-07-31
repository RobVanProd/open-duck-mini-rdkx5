# Ground-Up Reset Feasibility Audit Result

status: `RESET_CONTRACT_MISMATCH_FOUND`

| seed | fixed feasible | bank feasible | bank size | finite-bank conclusion |
|---:|---:|---:|---:|---|
| 100 | 4 / 4 | 2,489 | 4,096 | viable horizons are common |
| 101 | 0 / 4 | 0 | 4,096 | none found; not proof of infeasibility |

For seed 101, height stayed at least `0.15 m`; tilt was the limiting condition.
The best bank candidate reached `0.3152 rad` tilt against the frozen `0.25 rad`
limit. The bank therefore did not establish a viable seed-101 sequence, but a
finite bank cannot prove continuous-space infeasibility.

## Contract audit

The diagnostic exposed a higher-priority implementation mismatch. The oracle
and feasibility tools initialized directly from `Joystick.reset()`. That reset
multiplies actuator joint positions independently by uniform `[0.5, 1.5]` and
samples six base velocities from `[-0.05, 0.05]`. The ground-up nominal and
reference-residual preregistrations instead freeze deterministic home reset and
zero base velocity.

`tools/evaluate_ground_up_policy.py` also constructed `ClosedLoopConfig`
without a reset mode, inheriting `playground` rather than the already-supported
`home-support` mode. Consequently:

- the H8, H16, viability-command, and reset-feasibility outputs characterize a
  randomized-reset diagnostic, not the intended nominal source gate;
- ground-up policy evaluations produced by this wrapper did not implement the
  documented deterministic-home evaluation contract;
- their negative conclusions cannot be used as final evidence until the saved
  policies are re-evaluated with the correct reset.

This is a correctness repair, not permission to tune or retrain. The next step
is to expose and freeze `home-support` in the ground-up evaluator, validate the
reset state, and re-run the latest causal A/B saved policies on CPU. No Colab,
GPU, RDK-X5, or robot access is authorized.
