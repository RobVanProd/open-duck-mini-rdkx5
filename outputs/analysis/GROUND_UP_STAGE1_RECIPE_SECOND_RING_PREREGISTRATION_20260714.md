# Ground-Up Stage-One Recipe Second-Ring Preregistration

status: `PREREGISTERED_BEFORE_SECOND_RING_COMPUTE`

## Evidence boundary

The learning-rate, entropy, and imitation first ring produced no full
checkpoint pass and no persistent moving seed. Its longer tie-break also
produced no full pass: the safest candidate had zero moving passes. Therefore
none is a recipe winner and none advances merely because it ranked first.

The first-ring preregistration explicitly reserved discount and unroll length
for a new pre-compute amendment if persistence did not improve. This is that
amendment. It is the final scalar PPO recipe ring before reconsidering the
training mechanism or curriculum.

## Frozen invariants

- Playground commit `b9be205ac64488c23504ca42e5ec790337adeec3`;
- reference, projected reference, corrected velocity frame, stage-one command
  mixture, observation/action ABI, calibrated actuator fit, task, network,
  PPO batch geometry, evaluator, and rollout seeds;
- learning rate `3e-4`, entropy cost `0.005`, imitation scale `1.0`;
- seed `100`, 8,028,160 steps, and 6M/8M CPU evaluations;
- x=`0.00` and x=`0.08`, seeds `100/101`, duration `1.08 s`;
- training reward is recorded but excluded from selection.

## One-factor candidates

| ID | discount | unroll length | changed variable |
|---|---:|---:|---|
| `S1C` | `0.97` | `20` | reused center evidence |
| `S1DISC_LO` | `0.95` | `20` | discount only |
| `S1DISC_HI` | `0.99` | `20` | discount only |
| `S1UNROLL_LO` | `0.97` | `10` | unroll only |
| `S1UNROLL_HI` | `0.97` | `40` | unroll only |

The discount values are a bounded linear bracket around `0.97`; unroll values
are the previously registered half/double bracket around `20`. No factor
combination is trained.

## Ranking and stop rule

Hard failures dominate. Then apply the frozen equal-window ordering: full
checkpoint passes, finite zero-command runs, moving passes, and persistence.
Training reward cannot rank or break ties.

At most two candidates may advance to a separately registered 12M/second-seed
replication only if they have either a full checkpoint pass or a moving pass on
the same seed at both 6M and 8M, with zero hard failures. A recipe may be called
`BEST_RECIPE_TESTED` only under the existing two-consecutive-checkpoint and
two-training-seed replication rule.

If no candidate meets the advancement condition, the result is
`NO_SCALAR_RECIPE_WINNER`; scalar recipe search closes. The next decision must
address the training mechanism or curriculum under a new preregistration. It
may not invent an untested combination or continue scalar tuning post hoc.

No local accelerator, RDK-X5, robot, deployment, torque, or motor access is
authorized.
