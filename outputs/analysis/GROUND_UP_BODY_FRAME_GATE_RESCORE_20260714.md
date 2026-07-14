# Ground-Up Body-Frame Gate Rescore

status: `NO_HISTORICAL_FULL_POSITIVE_CHECKPOINT_AFTER_FRAME_REPAIR`

The positive command is body-local, but the historical displacement clause was
world-X. A read-only rescore replaced only that clause with integrated
body-local forward velocity; historical JSON files were not modified.

- evaluations rescored: `62`
- positive runs whose classification changed: `2`
- corrected full positive checkpoints: `0`

The changed runs are B0 nominal phase-0 at 4M, x=`0.074`, seed `100`, and
S1IMIT_HI_T12 at 12M, x=`0.08`, seed `100`. Both become isolated positive
runs, but neither creates a full checkpoint or persistent two-seed result.

Therefore the frame repair is required for future evaluation, but it does not
retroactively create a winner or change the A0/A1 reference-residual decision.
World displacement remains a diagnostic; body-local integrated progress is the
positive-command hard-gate quantity.

Execution was read-only and CPU-only. No robot or GPU was accessed.
