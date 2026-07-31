# Winner-v50c gradient backward-error attribution contract

- Status: `PREREGISTERED_WINNER_V50C_GRADIENT_BACKWARD_ERROR_ATTRIBUTION`
- Decision: `AUTHORIZE_ONE_ZERO_UPDATE_SCALE_AWARE_GRADIENT_RECOMPUTATION_ONLY`
- Float32 epsilon: `1.1920928955078125e-07`
- Relative bound, sqrt(epsilon): `0.00034526698300124393`
- Rerun: `80 x 250 ticks`, CPU-only, zero optimizer updates
- Support / export / locomotion / robot: `0 / 0 / 0 / 0`

V50 and V50b remain holds. This test asks whether every gradient leaf
is backward-stable relative to its own magnitude; it does not widen or
rewrite either prior absolute or ULP gate.
