# Winner-v30 prefix right-pitch anchor one-update CPU contract

- Status: `PREREGISTERED_WINNER_V30_PREFIX_RIGHT_PITCH_ANCHOR_ONE_UPDATE_CPU_PROOF`
- Decision: `AUTHORIZE_EXACT_ONE_PREFIX_RIGHT_PITCH_ANCHOR_OPTIMIZER_UPDATE_ONLY`
- Source optimizer count: `200`
- Authorized optimizer count: `201`
- Frozen anchor scale: `197.3112030029297`
- Formal support / locomotion / robot: `0 / 0 / 0`

Does exactly one Adam update from Winner-v24 final, using the frozen Winner-v29 prefix-anchor gradient and scale, preserve the complete software contract while reducing the selected same-batch anchor MSE?

This contract authorizes one update only. A pass can authorize only a
separately preregistered bounded training continuation; it cannot authorize
checkpoint selection, deployment, runtime work, Gate 5, or robot access.
