# Winner-v22 normalized-predictor training preregistration

- Status: `PREREGISTERED_WINNER_V22_NORMALIZED_PREDICTOR_TRAINING`
- Decision: `AUTHORIZE_ONE_100_UPDATE_NORMALIZED_PREDICTOR_ARM_ONLY`
- Source: identical Winner-v13 Stage-1 update-100 snapshot
- Updates / checkpoints: `100 / 50,100`
- Corrected normalized predictor scale: `380.9135437011719`
- Predictor-scale evaluations / sweeps: `0 / 0`
- Formal support / locomotion / robot: `0 / 0 / 0`
- Flat-transport equation: `not used`

This is one causal arm. It changes only the target coordinates used by
the existing response-predictor loss, using the formula proven by the
zero- and two-update CPU contracts. No support gate, checkpoint
selection, locomotion evaluation, manual measurement, or robot access occurs.
