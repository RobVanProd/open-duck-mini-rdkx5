# Winner-v20 joint-recurrent support failure attribution

- Status: `PASS_WINNER_V20_SUPPORT_FAILURE_ATTRIBUTION`
- Decision: `AUTHORIZE_PREDICTOR_PRESERVING_JOINT_OBJECTIVE_CPU_CONTRACT_ONLY`
- Support failures, half/final: `16 / 20` of 124; every terminal failure is roll/pitch only
- Failure ticks, half/final: `26-43 / 27-103`
- Predictor MSE range: learned `4.44323e+10` to `4.84637e+10`; constant baseline remains below `0.58`
- Heldout repeats: bit-exact; plant context: noncollapsed but much weaker
- Flat-transport equation: `not selected`
- New simulation / optimizer updates / robot access: `0 / 0 / 0`

The next authorized work is only a zero-update CPU contract for a
predictor-preserving joint recurrent objective. Response-conditioned
locomotion training, deployment, Gate 5, and robot access remain blocked.
