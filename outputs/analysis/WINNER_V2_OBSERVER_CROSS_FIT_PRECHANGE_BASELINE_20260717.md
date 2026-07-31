# Winner-v2 Observer Cross-Fit Pre-change Baseline

Status: `PASS_PRECHANGE_DEFAULT_OFF_BASELINE_CAPTURED`

After preregistration and before modifying the evaluator, the frozen
512000/P30/x=.077/seed167931544 cell was rerun for 600 CPU ticks with the normal
applied-target observation path.

- evaluator SHA-256:
  `f35d35789d50baf557d3b2427dfe326ccc60c7607e79069e5a9dd51f2f01f8d6`;
- raw 600-row trace SHA-256:
  `a6e675ccb56f09031b1db174e68249a2d9ea5a9703e91135d9ad8e5b938b8d38`;
- canonical result SHA-256 after removing only wall-clock and trace-path
  reporting fields:
  `bf03f082bcb8cbd02eaa917a6d33a5a930eedc148ad7005a78aee03863769fb9`;
- status: `PASS_GAIT_EMERGENCE_CHECKPOINT`;
- termination: `duration_complete`;
- tracking p95: `0.18085599541664124` rad;
- mean local vx: `0.09353398881144434` m/s;
- action saturation: `0.0`%;
- measured rate excess: `0.0` rad/s.

The raw baseline remains at
`/tmp/winner_v2_crossfit_baseline_20260717/` for the immediate post-change
byte-identity check and is not committed as a duplicate multi-megabyte trace.
The hashes and exact canonicalization rule are frozen here before code changes.
