# Winner-v22 normalized-predictor CPU contract

- Status: `FROZEN_WINNER_V22_NORMALIZED_PREDICTOR_CPU_CONTRACT`
- Decision: `AUTHORIZE_ONE_ZERO_UPDATE_NORMALIZED_SEMANTICS_PROOF_ONLY`
- Source: identical Winner-v13 Stage-1 update-100 snapshot
- Correct formula: `prediction_normalized - ((raw - mean) / std)`
- Optimizer updates / support cells / locomotion / robot: `0 / 0 / 0 / 0`
- Corrected scale evaluations / sweeps: `1 / 0`
- Flat-transport equation: `not used`

A pass authorizes only a separate two-update CPU proof. It does not
authorize support training, response-conditioned locomotion, or hardware.
