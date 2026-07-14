# Ground-Up Stage-One Mechanism Screen Preregistration

status: `PREREGISTERED_BEFORE_MECHANISM_COMPUTE`

## Why the search changes level

Two bounded scalar-recipe rings bracketed learning rate, entropy, imitation
scale, discount, and unroll length around the upstream PPO center. None
produced persistent forward gait or a full checkpoint pass. The center is a
protected control, not a selected recipe. Repeating scalar tuning or combining
the least-bad factors would be post-hoc and is closed.

The remaining preregistered question is structural: can a policy mechanism
learn the feedback correction around the reference that the upstream MLP does
not learn under this stage-one curriculum? This amendment permits that fair
screen while retaining the canonical scalar center for every family. It does
not call the center optimal.

## Eligible mechanisms

| ID | actor mechanism | actor input | critic input |
|---|---|---:|---:|
| `M0_UPSTREAM` | canonical MLP final action | 101 | privileged 212 |
| `M1_REFCOND` | projected-reference-conditioned MLP final action | 115 | privileged 226 |
| `M2_PHASE_MOE` | smooth command/phase mixture of experts final action | 101 | privileged 212 |
| `M3_RECURRENT` | 64-state recurrent final action | 101 + state 64 | privileged 212 |
| `M4_SYMCRIT` | canonical MLP final action | 101 | canonical 101 |

All five implementation/export paths have CPU contract coverage. Imitation
decay is excluded from this rung because its frozen planner may decay only
after two real consecutive gait-emergence passes; no such pair exists.

## Frozen training and evaluation

- Playground commit `b9be205ac64488c23504ca42e5ec790337adeec3`;
- corrected reference-velocity frame and stage-one command mixture;
- composed mechanism-stack patch SHA-256
  `cf5155dfd54a4699865b9823e8bf090f9f54b0e53df5583eb448e315d60053dc`;
- reference and projected-reference-table hashes already frozen by the parent
  search;
- seed `100`, 8,028,160 environment steps, 256 environments;
- learning rate `3e-4`, discount `0.97`, entropy `0.005`, imitation `1.0`,
  unroll `20`, and unchanged PPO batch/update geometry;
- evaluate 6,021,120 and 8,028,160 on CPU at x=`0.00/0.08`, rollout seeds
  `100/101`, duration `1.08 s`, using the same actuator fit and gate;
- recurrent evaluation uses the frozen `h_in -> h_out` ABI; reference-
  conditioned evaluation uses the frozen 115-value observation contract.

The 6M/8M window is reused from the scalar screen because it includes the
earliest observed partial emergence while bounding equal compute. Training
reward is excluded.

## Advancement and stop rule

Hard failures dominate. Then rank full checkpoint passes, finite x=0 runs,
moving passes, and persistence, with exact ties retained.

At most two mechanisms advance to a separately preregistered 12M/second-
training-seed replication only if they produce either a full checkpoint pass
or the same moving seed passing at both checkpoints with zero hard failures.
No architecture advances merely by being least bad.

If none qualifies, the result is `NO_STAGE1_MECHANISM_WINNER`; the evidence
then points to the shared reference/command curriculum or objective rather than
scalar PPO settings or these policy topologies. No new architecture or
curriculum is invented post hoc.

No local GPU, iGPU, onboard GPU, RDK-X5, robot, deployment, torque, or motor
access is authorized.
