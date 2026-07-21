# Winner-v12 full-calibrator pre-update failure attribution

- Status: `INVALID_PREUPDATE_STAGE1_NORMALIZATION_VALIDATION`
- Decision: `AUTHORIZE_CORRECTED_RUNNER_AND_NEW_ZERO_UPDATE_CPU_CONTRACT_ONLY`
- GitHub run: `29807546004`, attempt `1`
- Commit: `011e68cbc7b687654e502130257ad5b8e7eb0fee`
- Optimizer updates: `0`
- Committed snapshots: `0`
- Formal support/locomotion/robot execution: `0 / 0 / 0`

The first Stage-1 rollout completed, but the pre-loss finite-data guard passed a
mixed-type normalization receipt into `numpy.isfinite`. Its descriptive strings
caused a `TypeError` before loss construction, Adam, or snapshot persistence.
The recovery artifact contains only the exact launch-claim receipt and log.

The correction is limited to a dedicated normalization validator: exact receipt
schema, independent float64 population recomputation, hash equality, float32
array identity, finiteness, and the frozen `1e-6` standard-deviation floor. A
new zero-update CPU contract must pass before any corrected training launch.
