# Ground-Up Signed Progress Objective Preregistration

status: `PREREGISTERED_BEFORE_ACCELERATOR_COMPUTE`

## Question

Can an outcome-aligned signed local-forward-velocity ratio create persistent
nominal reference gait where the otherwise identical Gaussian-tracking control
did not?

## Protected control

`B0_NOMINAL_PHASE0` is the already-completed control. It is not retrained. Its
3,010,560 and 4,014,080 checkpoints produced one isolated moving pass, zero
persistent moving seeds, and six hard failures. Its archive SHA-256 is
`a6bae88973162f899577111e3107d2e02bffe08f950cae748caca7111495df84`.

## New causal arm

`O1_SIGNED_PROGRESS` differs from B0 in exactly one reward function for
positive commands:

- control: `exp(-(command_x - body_local_vx)^2 / 0.01)`;
- O1: `clip(body_local_vx / abs(command_x), -1, 1)`.

The `tracking_lin_vel` scale remains `2.5`. At x=0, the canonical Gaussian
function remains active. The CPU contract produces exact scores
`[-1,0,0.5,1,1]` at velocity ratios `[-1,0,0.5,1,1.5]` and passes a finite
environment step with unchanged observation 101/action 14.

## Frozen implementation and training

- Playground commit `b9be205ac64488c23504ca42e5ec790337adeec3`;
- same base/mechanism and nominal-bootstrap patch stack as B0;
- signed-progress patch SHA-256
  `13ddc699d3a005416a5790152b4a9d4f442216cfec4a991f93be65bde85ffa5b`;
- canonical MLP actor and privileged critic;
- seed `100`, 256 environments, 4,014,080 steps, 5 exports;
- LR `3e-4`, discount `0.97`, entropy `0.005`, imitation `1.0`, unroll `20`;
- exact x=`0.074`, y/yaw/head=`0` training command;
- deterministic home reset, reference start phase `0` with valid phase vector;
- nominal flat backlash only; noise, delay, pushes, and domain randomization
  remain disabled.

No reward scale, alive term, imitation term, action cost, clipping rule,
architecture, phase, reset, command, horizon, or PPO value changes.

## Frozen evaluation and stop rule

Evaluate O1 at 3,010,560 and 4,014,080 on local CPU at x=`0.074/0.08`, seeds
`100/101`, duration `1.08 s`, reference phase `0`, using the same fitted bridge.

O1 advances only if all eight positive-command runs pass moving emergence,
complete the duration, retain the same passing seeds across checkpoints, and
produce zero hard failures or constant saturated action vectors. Training
reward is excluded. Improvement over B0 that falls short of this rule is not a
winner.

If O1 fails, status is `NO_SIGNED_PROGRESS_OBJECTIVE_WINNER`; do not tune its
scale, clip, denominator, command, phase, or horizon post hoc. Return to the
remaining structural objective mechanisms—command-invariant survival terms or
total reward clipping—under a new audit.

A pass authorizes only a separately preregistered Stage-2 x=0 continuation.
It does not authorize randomization, pushes, rough terrain, baseline comparison,
offline clearance, RDK runtime work, deployment, or robot validation.

No local GPU, iGPU, onboard GPU, RDK-X5, robot, torque, or motor access is
authorized.
