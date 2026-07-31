# Winner-v12 formal-result import failure attribution

- Status: `ATTRIBUTED_WINNER_V12_FORMAL_RESULT_IMPORT_FAILURE`
- Formal run/artifact: `29816212367 / 8489512924`
- Raw result: `HOLD_WINNER_V12_CALIBRATOR_SUPPORT_GATE`
- Additional gate cells / locomotion / robot access: `0 / 0 / 0`

The immutable raw result correctly records the full-training preregistration
hash used by the gate runner. The read-only importer incorrectly compared that
field with the distinct support-gate preregistration hash. The authorized
correction changes only that source alias and records its own hash in the
imported attribution. It cannot change, rerun, or reinterpret the HOLD result.
