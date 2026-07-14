# Colab Ground-Up Compute Ledger

status: `USER_REPORTED_ACCOUNT_SNAPSHOT_WITH_MEASURED_JOB_TIMES`

## Account snapshot

At the user's 2026-07-14 project update, the Colab UI reported:

- available compute units: `91.29`;
- current usage rate: approximately `1.07 units/hour`;
- active sessions: `1`.

This is user-reported UI evidence. The Colab CLI itself does not expose an
exact compute-unit balance, so this snapshot must not be silently replaced by
the older conservative planning ledger.

## Live local-search projection

The completed `S1LR_LO` broad-rung candidate measured `1416.415229113 s` of
training for 8,028,160 steps. If all six candidates take the same time, the
training-only projection is:

- session time: `2.360692048521667 hours`;
- compute at the displayed rate: approximately `2.5259404919181837 units`.

This is a linear planning estimate, not an observed charge. Setup, artifact
transfer, evaluation, rate changes, and Colab scheduling can change the final
debit. Completed candidate wall times and a new user-visible account snapshot
take precedence over this projection.

No local accelerator, RDK-X5, robot, torque, or motor access is authorized by
this ledger.
