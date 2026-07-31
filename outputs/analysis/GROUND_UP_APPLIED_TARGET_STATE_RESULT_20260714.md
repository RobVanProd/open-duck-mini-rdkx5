# Ground-Up Applied-Target-State Continuation Result

status: `REJECT_EXACT_ARM_PERSISTENCE_FAILURE`

## Hosted artifact contract

The single preregistered T4 continuation completed at requested steps
0/1,003,520/2,007,040. The recovered archive is 8,161,319 bytes with SHA-256
`3b7457fe945a9d19d01616e77a28cd4f1175d8f81cf2f6eb12f30035ae52c9e7`,
exactly matching the downloaded manifest. Colab was stopped after verification
and reports zero active sessions. Training reward was not used for selection.

## Frozen nominal gate

All values below are the maximum pitch-chain tracking p95 across fitted-bridge
rollouts. Each command has deterministic home-reset seeds 100 and 101; both
seeds produced the same result. Every one of the 12 runs completed 1.08 s,
walked forward, had bilateral contact transitions, finite nonconstant actions,
zero saturation, and zero target-rate excess.

| checkpoint | x=.074 | x=.077 | x=.080 | full cells |
|---|---:|---:|---:|---:|
| 1,003,520 | .18877 | .18502 | .17679 | 6/6 |
| 2,007,040 | .21617 | .21694 | .20817 | 0/6 |

The 1M checkpoint is the first policy in this ground-up route to pass the full
nominal gate across all commands and both seeds. It is not promoted because the
preregistration requires both post-update checkpoints to pass. The 2M
checkpoint exceeds the fixed `.20 rad` tracking threshold in every cell, so the
exact arm fails persistence and closes without checkpoint selection or tuning.

## Evidence-selected next work

The causal-state repair solved the previous nominal gate at 1M and the failure
appears only with additional optimization. The next authorized work is a
read-only 1M-to-2M drift audit of normalization, policy parameters, actions,
tracking by joint, and training metrics. It must identify a measured mechanism
before any retention recipe is preregistered. No additional training, x=0 gate,
robot, RDK-X5, local GPU, iGPU, onboard GPU, deployment, torque, or motor access
is authorized by this result.
