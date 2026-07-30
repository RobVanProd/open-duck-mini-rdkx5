# T185 JIT phase diagnostic recovery

- Status: `INVALIDATE_T185_PHASE_VECTOR_DIAGNOSTIC_BEFORE_OPTIMIZER`
- Classification: pre-optimizer eager-vs-JIT checker mismatch
- Observed maximum difference: `2.384185791015625e-07`
- Passed environment checks: `9/10`
- Failed environment check: `reference_phase_vectors_exact`
- Actual anchor indices and reference contact targets: exact
- Correction: construct the expected vector through the same JIT/vmap path
  and retain exact equality (`tolerance = 0`)
- Environment transitions / optimizer / behavior / hosted / robot:
  `7,168 / 0 / 0 / 0 / 0`
- Authority earned: T185B recovery preregistration only
- Recovery SHA-256:
  `bd7f5c565239ea0579005e8a01665b9f2e0493a83cd18182ae98382c1865a23c`

This recovery changes no curriculum, policy, simulator transition, reward,
phase, action, observation, decision, or authority contract.
