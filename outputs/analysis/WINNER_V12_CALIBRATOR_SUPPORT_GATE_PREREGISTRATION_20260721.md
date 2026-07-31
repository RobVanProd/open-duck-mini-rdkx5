# Winner-v12 calibrator support-gate preregistration

- Status: `PREREGISTERED_WINNER_V12_CALIBRATOR_SUPPORT_GATE`
- Decision: `AUTHORIZE_SUPPORT_GATE_CPU_CONTRACT_ONLY`
- Main cells: `124 per checkpoint × 2 = 248`
- Heldout deterministic repeat cells: `32 per checkpoint × 2 = 64`
- Duration: `250 ticks per cell`
- Training/robot execution now: `0 / 0`

Both half and final must pass every support cell, every heldout repeat,
the per-plant learned-vs-constant prediction test, and all 16 hidden-plant
context separations. There is no closest-result selection.

The population, seeds, duration, simulator, thresholds, and selection
rule remain byte-for-byte semantic carryovers from the preregistration
frozen before training results. This revision only corrects the
pre-execution Episode input binding attributed in run 29815413956.
It authorizes only a new zero-cell CPU contract. The formal gate remains blocked
until the complete training artifact and checkpoint hashes pass independent
verification.
