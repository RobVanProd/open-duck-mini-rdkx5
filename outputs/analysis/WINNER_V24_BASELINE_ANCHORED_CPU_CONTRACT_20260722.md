# Winner-v24 baseline-anchored CPU contract

- Status: `FROZEN_WINNER_V24_BASELINE_ANCHORED_CPU_CONTRACT`
- Decision: `AUTHORIZE_ONE_ZERO_UPDATE_BASELINE_ANCHORED_OBJECTIVE_PROOF_ONLY`
- Baseline anchor: `recorded returns + rederived values`
- New observed roll/pitch terminal delta: `-250`
- Baseline GAE reconstruction / old threshold relaxation: `no / no`
- Policy inputs / rollout actions / physics changes: `0 / 0 / 0`
- Optimizer / formal support / locomotion / robot: `0 / 0 / 0 / 0`
- Manual mass/COM measurements: `not required`

A pass authorizes only a separately preregistered one-update CPU proof.
It does not authorize training, checkpoint selection, or robot access.
