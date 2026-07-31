# Winner-v93 universal-response readout result

- Status: `PASS_WINNER_V93_UNIVERSAL_RESPONSE_READOUT`
- Classification: `FROZEN_RECURRENT_STATE_HAS_HELDOUT_LINEAR_RESPONSE_SIGNAL`
- Source support: `112 / 112`
- Fit / heldout transitions: `19,920 / 7,968`
- P30 fitted / frozen / constant MSE: `0.383592 / 0.930858 / 0.866829`
- P31/34 fitted / frozen / constant MSE: `0.373733 / 0.933975 / 0.869110`
- Design rank / width: `70 / 79`
- Maximum coefficient magnitude: `2.90354176e8`
- Coefficient SHA-256: `2a9ba80b...ce128888`
- Result SHA-256: `6990cd76c61b18405bbf9e5edff46d2533e281553aa077780470912d7a4a3cf2`

One predeclared linear readout from the frozen recurrent state cuts heldout
prediction error below both the stale Winner-v22 head and the constant
comparator on both actuator plants. The recurrent observer therefore contains
transferable response information under the universal action.

The raw 79-column fit is rank-deficient and its float32 coefficients are too
large to select directly. This pass authorizes only a separately preregistered
CPU observer contract with an explicit numerical-stability requirement. It
does not select a policy artifact or authorize training, deployment, Gate 5,
or robot access.
