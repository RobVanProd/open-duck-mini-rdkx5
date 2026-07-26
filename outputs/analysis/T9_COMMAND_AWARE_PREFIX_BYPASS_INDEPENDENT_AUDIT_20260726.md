# T9 command-aware prefix-bypass independent audit

- Status: `HOLD_T9_COMMAND_AWARE_PREFIX_BYPASS_INDEPENDENT_AUDIT`
- New passing cells: `4/4`
- Reused T8 moving cells: `12/12`
- Combined cells: `16/16`
- Issues: `4`
- Audit SHA-256: `12e376c1f681f6008cf4929cdc028d6e57a50feba031014ed79bc22a3ce1ef58`

The auditor independently rehashed and recomputed the four new x=0 traces, context/state/action/applied-target chains, stationary and tracking gates, corrected servo-duration rules, and exact readbacks. It also revalidated the immutable audited T8 moving-cell evidence.

This audit does not authorize hosted training, robot/RDK-X5 access, Gate 5, torque, motion, deployment, or grounded replay.

## Issues

- bypass_checks:('V121_TRAIN_MATCHED_HALF', 'p30')
- bypass_checks:('V121_TRAIN_MATCHED_HALF', 'p31_34')
- bypass_checks:('V121_TRAIN_MATCHED_FINAL', 'p30')
- bypass_checks:('V121_TRAIN_MATCHED_FINAL', 'p31_34')
