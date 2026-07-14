# Ground-Up Reference-Residual A/B Preregistration

status: `PREREGISTERED_BEFORE_ACCELERATOR_COMPUTE`

## Evidence selection

The projected reference table is numerically valid, but direct execution is
not a valid behavior-cloning label: raw reference rollouts fell in 4/8 runs and
moved backward on average; contact-synchronized projected rollouts still fell
in 2/8 and moved backward on average. A randomly initialized actor that merely
received the reference as an observation produced one isolated moving run,
zero persistent moving seeds, and no full checkpoint pass.

This selects a different hypothesis: put the projected reference at the
actor's initial deterministic final action and let PPO learn state-feedback
residuals. The composition stays inside the exported ONNX policy; it is not a
runtime action wrapper. Its CPU software contract passed before accelerator
use.

## Causal pair

Two fresh arms are required because the earlier reference-conditioned M1 used
a different, fully randomized training setup and is not a clean control.

- `A0_CURRENT_REFCOND`: canonical randomly initialized MLP, with the projected
  reference appended to the observation.
- `A1_REFERENCE_ANCHORED_RESIDUAL`: identical data, observations, critic,
  objective, PPO recipe, seed, and horizon; only the policy parameterization
  changes. Its initial deterministic final action equals the projected
  reference, and its network learns the residual correction.

## Frozen shared training

- Playground commit `b9be205ac64488c23504ca42e5ec790337adeec3`;
- seed `100`, 256 environments, 4,014,080 steps, 5 exports;
- LR `3e-4`, discount `0.97`, entropy `0.005`, imitation `1.0`, unroll `20`;
- signed linear progress objective selected in O1;
- exact x=`0.074`, y/yaw/head=`0` command;
- deterministic home reset, reference start phase `0`;
- nominal flat backlash with noise, delay, pushes, and domain randomization off;
- privileged critic and projected reference table SHA-256
  `8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212`.

O2's progress-conditioned survival mechanism is excluded: it tied O1 exactly,
so the simpler signed-progress objective is retained. No reward scale, command,
phase, reset, curriculum, environment, critic, seed, horizon, or evaluation
change is permitted between A0 and A1.

## Frozen evaluation and decision

Evaluate both arms at 3,010,560 and 4,014,080 on local CPU at x=`0.074/0.08`,
seeds `100/101`, duration `1.08 s`, reference phase `0`, with the same fitted
bridge and existing behavior gate. Training reward is excluded.

`A1_REFERENCE_ANCHORED_RESIDUAL` advances only if all eight of its runs pass
moving emergence, complete duration, retain both seeds across checkpoints, and
produce zero hard failures or constant saturated action vectors. It must also
outperform A0 on the frozen score ordering. Any lesser result is not a winner
and does not authorize post-hoc tuning.

A pass authorizes only design of a separately preregistered Stage-2 x=0 test.
It does not authorize randomization, pushes, terrain, baseline superiority,
offline clearance, RDK work, deployment, or robot validation.

No local GPU, iGPU, onboard GPU, RDK-X5, robot, torque, or motor access is
authorized.
