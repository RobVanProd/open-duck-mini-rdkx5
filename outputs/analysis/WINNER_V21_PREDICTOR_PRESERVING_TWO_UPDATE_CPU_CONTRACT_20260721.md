# Winner-v21 predictor-preserving two-update CPU contract

- Status: `FROZEN_WINNER_V21_PREDICTOR_PRESERVING_TWO_UPDATE_CPU_CONTRACT`
- Decision: `AUTHORIZE_EXACT_TWO_UPDATE_EXPLICIT_GRADIENT_PROOF_ONLY`
- Optimizer updates now / in proof: `0 / 2`
- Formal support / locomotion / robot: `0 / 0 / 0`
- Predictor scale: frozen once; no recomputation or sweep
- Flat-transport equation: `not used`

The optimizer consumes the explicit per-leaf sum of the separately
differentiated PPO and predictor gradients. This addresses only the
observed float32 accumulation-order discrepancy. A pass authorizes
a separate 100-update training preregistration, nothing further.
