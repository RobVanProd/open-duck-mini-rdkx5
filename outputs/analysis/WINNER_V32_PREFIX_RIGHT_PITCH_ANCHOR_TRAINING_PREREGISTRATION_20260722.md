# Winner-v32 prefix right-pitch anchor training preregistration

- Status: `PREREGISTERED_WINNER_V32_PREFIX_RIGHT_PITCH_ANCHOR_TRAINING`
- Decision: `AUTHORIZE_ONE_100_UPDATE_PREFIX_RIGHT_PITCH_ANCHOR_ARM_ONLY`
- Source / half / final optimizer count: `201 / 251 / 301`
- Continuation: `100 updates`, `80 x 250` scheduled slots per update
- Predictor / prefix-anchor scales: `380.9135437011719 / 197.3112030029297`
- Formal support / locomotion / robot in training: `0 / 0 / 0`

Winner-v27 localized negative-X failure to ticks 4-8, Winner-v28 isolated the right pitch chain, Winner-v29 proved the exact anchor gradient, Winner-v30 reduced same-batch anchor error in one update, and Winner-v31 proved its two HOLD checks were only bounded cross-worker float replay. One unchanged continuation now tests persistence.

No checkpoint is selected from training metrics. A passing artifact
authorizes only a separately frozen half/final support gate.
