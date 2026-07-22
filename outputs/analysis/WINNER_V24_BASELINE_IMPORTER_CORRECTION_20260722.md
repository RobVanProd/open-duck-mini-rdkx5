# Winner-v24 baseline-anchored importer correction

- Status: `FROZEN_WINNER_V24_BASELINE_IMPORTER_CORRECTION`
- Scope: importer gradient-key inventory only
- Frozen importer expected: an obsolete six-key set
- Frozen runner emitted: the exact twelve-key Winner-v21 trainable tree
- Raw artifact / result rewritten: `no / no`
- Workflow rerun / optimizer update / robot access: `no / no / no`

The strict importer stopped before writing a result. A separately versioned
wrapper may replace only the expected gradient-key inventory and then run every
other check from the frozen importer against the unchanged first-attempt ZIP.
