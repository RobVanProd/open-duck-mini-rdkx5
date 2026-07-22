# Winner-v50b gradient-composition ULP attribution contract

- Status: `PREREGISTERED_WINNER_V50B_GRADIENT_COMPOSITION_ULP_ATTRIBUTION`
- Decision: `AUTHORIZE_ONE_ZERO_UPDATE_GRADIENT_ULP_RECOMPUTATION_ONLY`
- Frozen V50 error / threshold: `4.76837158203125e-6 / 4e-6`
- Existing campaign bound: `8 signed-float32 ULP per element`
- Rerun: `80 x 250 ticks`, CPU-only, zero optimizer updates
- Support / export / locomotion / robot: `0 / 0 / 0 / 0`

V50 remains a hold. This separately tests whether its two equal absolute
misses are bounded float32 evaluation-order variation under the already
established Winner-v31 ULP rule. It does not change V50's threshold.
