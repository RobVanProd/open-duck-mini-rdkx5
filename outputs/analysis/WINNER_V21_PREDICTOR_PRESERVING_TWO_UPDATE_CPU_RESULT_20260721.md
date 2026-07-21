# Winner-v21 predictor-preserving two-update CPU result

- Status: `PASS_WINNER_V21_PREDICTOR_PRESERVING_TWO_UPDATE_CPU_PROOF`
- Decision: `AUTHORIZE_SEPARATE_100_UPDATE_PREDICTOR_PRESERVING_TRAINING_PREREGISTRATION_ONLY`
- GitHub run / artifact: `29862894656` / `8508105466`
- Artifact ZIP SHA-256: `9e2ac8d1fdfe669412786800a718b34b72ab12f45de9c4fe1d2aa08f199ad2eb`
- Failed checks: `0`
- Optimizer updates / formal support / robot: `2 / 0 / 0`

The optimizer consumed the explicit per-leaf sum of the frozen PPO
and predictor gradients. A pass authorizes only a separately frozen
100-update CPU training run; it does not authorize locomotion or robot use.
