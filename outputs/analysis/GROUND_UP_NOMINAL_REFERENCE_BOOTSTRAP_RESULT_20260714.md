# Ground-Up Nominal Reference Bootstrap Result

status: `NO_NOMINAL_REFERENCE_BOOTSTRAP_WINNER`

## Decision

Neither preregistered bootstrap candidate advances. Both candidates tie with
one isolated moving pass, zero persistent moving seeds, and six hard failures
across their 3,010,560/4,014,080 evaluation windows. A tie between failing
candidates is not a winner.

| candidate | start phase | moving passes | persistent moving seeds | hard failures | decision |
|---|---:|---:|---:|---:|---|
| `B0_NOMINAL_PHASE0` | 0 | 1/8 | 0 | 6 | eliminate |
| `B1_NOMINAL_PHASE20` | 20 | 1/8 | 0 | 6 | eliminate |

`B0_NOMINAL_PHASE0` passed only x=.074 seed 100 at 3M. At 4M that pass was
lost; seed 101 fell at both commands/checkpoints and x=.08 exhibited constant
saturated-action behavior.

`B1_NOMINAL_PHASE20` passed only x=.074 seed 100 at 4M. Seed 101 fell at both
commands/checkpoints and x=.08 again exhibited constant saturated-action
behavior. Phase alignment shifted the isolated pass in time but did not create
persistence or remove hard failures.

## Artifact record

- B0 archive SHA-256:
  `a6bae88973162f899577111e3107d2e02bffe08f950cae748caca7111495df84`;
- B1 archive SHA-256:
  `ca126577bf5c8c4bc68365eb655b54471850c8f99ffeb30e033d7479cfd4887f`;
- B0 training seconds: `1020.302910183`;
- B1 training seconds: `821.036871065`;
- combined hosted-job seconds: `1897.214792871`.

Both archives were downloaded and hash-verified. The Colab session was stopped
before behavior evaluation and no Colab sessions remained.

## Interpretation

This was the correct test of whether the missing clean reference stage or reset
phase alone explained the earlier search failure. It did not. Removing domain
randomization, observation noise, reset noise, delay, random head commands,
and pushes did not yield persistent gait. Choosing the deterministic closest
home-compatible double-support reference phase also did not solve it.

The shared-setup audit showed that stationary behavior retains 93.31-98.70% of
the positive alive/angular/linear tracking core across the training range.
Together with the bootstrap result, the next evidence problem is now the
outcome-aligned objective. Per preregistration, do not try more phase choices,
longer bootstrap runs, architecture variants, or scalar tuning.

No policy, Stage-2 continuation, baseline comparison, offline clearance, RDK
runtime work, deployment, or robot validation is authorized. Training reward
was excluded. Evaluation used local CPU only; no local GPU, iGPU, onboard GPU,
RDK-X5, robot, motor, or torque access occurred.
