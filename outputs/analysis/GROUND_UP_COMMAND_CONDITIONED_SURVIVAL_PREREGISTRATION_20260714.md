# Ground-Up Command-Conditioned Survival Preregistration

status: `PREREGISTERED_BEFORE_ACCELERATOR_COMPUTE`

## Evidence selection

The reward-accounting audit reconstructed logged evaluation return from every
recorded B0 and O1 reward/cost component. Across all mature checkpoints, the
largest absolute reconstruction gap was `0.00002823`; there is no observed
evaluation evidence that lower total-reward clipping explains the failed gait.

At the final checkpoints, alive plus zero-yaw tracking contributed `81.55%` of
B0 and `79.81%` of O1 positive-scaled reward mass. Both are invariant to
forward progress in this exact-yaw-zero nominal stage. This selects one
remaining structural factor: condition those existing rewards on measured
forward progress.

## Protected control

`O1_SIGNED_PROGRESS` is the completed control and is not retrained. It passed
x=`0.074`, seed `100` at both 3M and 4M, but had six hard failures, constant
saturated action vectors at x=`0.08`, and zero full checkpoint passes. Its
archive SHA-256 is
`55ee6f33fc2a396c61a2ad19b37dea9fd9cd9bb7c2a4d58ca815f5ad1f1ef11b`.

## New causal arm

`O2_PROGRESS_CONDITIONED_SURVIVAL` retains O1 signed linear progress and changes
one structural mechanism for positive forward commands. Existing alive and
yaw-tracking rewards are multiplied by:

`clip(body_local_vx / abs(command_x), 0, 1)`.

The exact gate at velocity ratios `[-1, 0, 0.5, 1, 1.5]` is
`[0, 0, 0.5, 1, 1]`. This introduces no new scale: alive remains `20`, yaw
tracking remains `6`, and signed linear progress remains `2.5`. At x=0, alive
and canonical yaw tracking remain unconditioned for a later stationary stage.

Patch SHA-256:
`b00d78a3a7c6f15562cdb14ccfd9129ce0001845bbbca8c343965f98a054dc7f`.
The CPU contract passed the exact gate, positive-command conditioning, x=0
preservation, finite step, observation `101`, action `14`, and CPU-only checks.

## Frozen training

- Playground commit `b9be205ac64488c23504ca42e5ec790337adeec3`;
- same base/mechanism, nominal-bootstrap, and signed-progress patch stack as O1;
- canonical MLP actor and privileged critic;
- seed `100`, 256 environments, 4,014,080 steps, 5 exports;
- LR `3e-4`, discount `0.97`, entropy `0.005`, imitation `1.0`, unroll `20`;
- exact x=`0.074`, y/yaw/head=`0` training command;
- deterministic home reset, reference start phase `0`;
- nominal flat backlash; noise, delay, pushes, and domain randomization off.

No reward scale, signed-progress function, imitation term, action cost, total
clipping rule, architecture, PPO value, phase, reset, command, or horizon
changes.

## Frozen evaluation and stop rule

Evaluate O2 at 3,010,560 and 4,014,080 on local CPU at x=`0.074/0.08`, seeds
`100/101`, duration `1.08 s`, reference phase `0`, with the same fitted bridge.

O2 advances only if all eight runs pass moving emergence, complete duration,
retain both passing seeds across checkpoints, and produce zero hard failures or
constant saturated action vectors. Training reward is excluded. A rank
improvement over O1 that falls short is not a winner.

If O2 fails, status is `NO_PROGRESS_CONDITIONED_SURVIVAL_WINNER`; do not tune
the gate, scales, command, phase, or horizon post hoc. Close the current
objective family and audit a materially different reference-learning
formulation before further accelerator use.

A pass authorizes only a separately preregistered Stage-2 x=0 continuation.
It does not authorize randomization, pushes, terrain, baseline comparison,
offline clearance, RDK runtime work, deployment, or robot validation.

No local GPU, iGPU, onboard GPU, RDK-X5, robot, torque, or motor access is
authorized.
