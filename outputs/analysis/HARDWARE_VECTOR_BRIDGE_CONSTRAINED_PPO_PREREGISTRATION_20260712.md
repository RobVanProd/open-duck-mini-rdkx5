# Hardware-Vector Bridge Constrained PPO Preregistration

status: `PREREGISTERED_CPU_SMOKE_THEN_COLAB`

## Evidence

The fixed-target P30 bridge cross-validates against P31/34 at p95
`0.0074-0.0127 rad` on the six pitch-chain joints. Rate165 retains motion under
that bridge but violates its per-joint velocity limits. Two frozen supervised
rate objectives reduced motion before eliminating excess, so BC tuning is
closed. PPO is a distinct route because it can optimize forward progress and
support jointly with the measured envelope.

## Frozen bridge

Action order is the canonical 14-joint order. Measured pitch-chain entries are
used; non-pitch velocity limits remain neutral at `5.24 rad/s` because their
fixed-target fits hit search bounds or were not the failed gate.

- delay ticks: `3,3,3,3,3,3,2,3,3,3,2,3,2,3`
- tau seconds: `.015,.015,.005,.010,.010,.120,.120,.120,.120,.020,.035,.010,.030,.005`
- velocity limits: `5.24,5.24,1.50,1.50,1.75,5.24,5.24,5.24,5.24,5.24,5.24,1.25,1.00,1.25`

The target-rate excess cost uses indices `2,3,4,11,12,13`, corresponding
limits `1.50,1.50,1.75,1.25,1.00,1.25`, and pseudo-Huber delta `0.05`.
Its scale is frozen at `-1.1830617141938795`, calibrated so its parent-trace
mean contribution equals the existing action-rate contribution at scale
`-0.12` after startup. No scale sweep is authorized.

## Frozen optimization contract

- Warm start: exact rate165 PPO-LOC step-0 checkpoint and behavior prior.
- Preserve the established Stage-A reward/optimizer recipe, including behavior
  prior `-0.08`, restore KL `0.05`, global target rate `-0.04`, actuator
  tracking `-0.03`, and action rate `-0.12`.
- CPU smoke: 1024 timesteps, 4 envs; must instantiate, update, export, report
  the exact bridge vectors, and produce finite target-rate-limit diagnostics.
- Only a passing smoke authorizes one self-cleaning Colab T4 job. No local GPU,
  iGPU, robot, deployment, or grounded action is authorized.

## Candidate gates

Returned checkpoints are screened first on CPU against the unchanged P30
fixed-target bridge. Promotion requires x=.08 and x=0 8/8 duration/no-fall,
zero p95 and max velocity excess, x=.08 vx >=`0.0257 m/s`, ratio >=`0.3213`,
single support >=`20%`, and x=0 max pitch-chain p95 <=`0.07 rad/s`. Do not
weaken gates or tune the frozen scale after results.

