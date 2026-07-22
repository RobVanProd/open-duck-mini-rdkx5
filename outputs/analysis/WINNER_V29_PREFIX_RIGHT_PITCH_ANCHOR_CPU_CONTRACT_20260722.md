# Winner-v29 prefix right-pitch anchor CPU contract

- Status: `PREREGISTERED_WINNER_V29_PREFIX_RIGHT_PITCH_ANCHOR_CPU_CONTRACT`
- Decision: `AUTHORIZE_ONE_ZERO_UPDATE_PREFIX_RIGHT_PITCH_ANCHOR_CPU_PROOF_ONLY`
- Candidate/source: `Winner-v24 final@200 / Winner-v22 final@100`
- Selected mechanism: `ticks 0-7, action indices 11-13`
- Selected training cells: `16 episodes / 384 action elements`
- Optimizer / support / locomotion / robot: `0 / 0 / 0 / 0`

Can the exact V28 right-pitch-chain ticks-0-7 intervention be represented as a finite, localized, default-off-exact differentiable objective before any optimizer update is allowed?

The proof calibrates one analytic gradient-RMS scale but executes no update.
A pass can authorize only a separately frozen one-update CPU proof.
It cannot authorize training, checkpoint selection, runtime work, or robot access.
