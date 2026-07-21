# Winner-v21 predictor-preserving joint CPU contract

- Status: `FROZEN_WINNER_V21_PREDICTOR_PRESERVING_JOINT_CPU_CONTRACT`
- Decision: `AUTHORIZE_EXACT_ZERO_UPDATE_GRADIENT_BALANCE_PROOF_ONLY`
- Source: identical Winner-v13 Stage-1 update-100 snapshot
- Optimizer updates / support cells / robot access: `0 / 0 / 0`
- Candidate scale evaluations: `1`; sweeps: `0`
- Flat-transport equation: `not used`

The proof measures PPO and next-response gradients separately, freezes
one head-gradient RMS ratio, and requires all twelve combined gradients
to open without changing a parameter. A pass authorizes only a separate
two-update CPU proof, not support training or locomotion.
