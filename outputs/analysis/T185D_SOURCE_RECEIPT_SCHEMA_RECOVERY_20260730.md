# T185D source-receipt schema recovery

- Status: `INVALIDATE_T185D_SOURCE_RECEIPT_SCHEMA_BEFORE_EXECUTION`
- Classification: pre-execution receipt-schema mismatch
- Missing field: `kind=file` on four new file receipts
- Existing receipt path, byte count, and SHA-256: retained
- Artifact reads / simulator / optimizer / behavior / hosted / robot:
  `0 / 0 / 0 / 0 / 0 / 0`
- Authority earned: T185E receipt-only recovery preregistration
- Recovery SHA-256:
  `8fad7622ea1f34902ef292864a78d71b1b920f120ce2657edca5eacf4b00206b`

This recovery changes no metric rule, curriculum, policy, simulator,
optimizer, decision, or authority contract.
