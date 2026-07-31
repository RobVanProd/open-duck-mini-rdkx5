# T9 command-aware x=0 prefix-bypass preregistration

- Status: `PREREGISTERED_T9_COMMAND_AWARE_PREFIX_BYPASS`
- Contract SHA-256: `7efdd08003c0096c7fab5bba4208b0369880b0feca836444030067b233d15195`
- New cells: `4` (`2 checkpoints × 2 fits × x=0`)
- Reused T8 moving cells: `12`
- Training: `0 steps`
- Robot/RDK-X5 access: `forbidden`

## Question

Does bypassing response excitation only while paused/x=0 eliminate T8's single transition-rate failure while preserving the immutable 12/12 green moving handoff evidence?

## One-variable mechanism

At paused/x=0, stay at home, skip response excitation, and pass an immutable zero context to the unchanged context-ABI V121 graph. At moving commands, change nothing and reuse the twelve audited T8 cells.

## Decision

- Pass: earn one separately preregistered response-conditioned V121 continuation CPU software contract; do not authorize hosted training yet.
- Fail: close the command-aware prefix-bypass mechanism and do not train.

A pass does not authorize hosted training, robot/RDK-X5 access, Gate 5, torque, motion, deployment, or grounded replay.
