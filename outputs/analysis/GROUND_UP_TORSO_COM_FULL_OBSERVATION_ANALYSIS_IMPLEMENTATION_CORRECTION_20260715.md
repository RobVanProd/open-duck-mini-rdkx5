# Ground-Up Torso-COM Full-Observation Analysis Implementation Correction

status: `PASS_ANALYSIS_IMPLEMENTATION_CORRECTION_BEFORE_OUTCOMES`

After the exact replay completed but before any decode or sensitivity outcome
was run or inspected, a computational scaling defect was found in the frozen
analysis implementation. The 16-tick FULL115 probe would form a
1,841-dimensional primal ridge system even though each training fold has at
most 96 rows.

The implementation now uses the algebraically equivalent dual ridge solve only
when features exceed samples. The observation features, standardization,
unpenalized intercept, L2 coefficient 1.0, labels, folds, windows, thresholds,
and decisions are unchanged. Fixed deterministic fixtures covering both
primal and dual paths agree with the original augmented primal solve to
`2.1326690413658866e-14` maximum absolute score error.

The source/device/graph/refusal contract was rerun with zero simulator cells
and all 15 checks pass. The corrected analysis tool SHA-256 is
`6997624fa3aa865b71f9777607baa0b92e48016c377ab88ac072ffadcfec2685`;
the correction-contract JSON SHA-256 is
`cbe2776518c58ed193b2242f2b8de7a44eb769bc0a4e9c81f3807e5b28569d3a`.

This is an outcome-blind implementation correction, not a new probe, retry,
or hyperparameter change. It authorizes only execution of the already-frozen
analysis against the passing exact replay.

