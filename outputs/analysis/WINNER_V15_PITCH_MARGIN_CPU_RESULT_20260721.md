# Winner-v15 pitch-margin CPU result

- Status: `PASS_WINNER_V15_PITCH_MARGIN_CPU_CONTRACT`
- Decision: `AUTHORIZE_PITCH_MARGIN_SUPPORT_TRAINING_PREREGISTRATION_ONLY`
- GitHub run / artifact: `29836822343` / `8497744413`
- Artifact ZIP SHA-256: `27f1c4776a5cb58aa73a2f17dad8e993b71e3c6ef768f2e3841c707587af0db1`
- Sampled / valid transitions: `18251 / 18243`
- Nonzero pitch penalties / settled bonuses: `5911 / 36`
- One-update graph / snapshot SHA-256: `c05abb9fc0e302c2733433eeeb4945dfb998e465865ee33eb2fa0939b979ee8c / 7e6115e80fbfddf3b4b73af30fd46c0c2474f9207e267512bc74b98d8c1ca651`
- Default-off / reward-only transition identity: `bit exact / bit exact`
- Stage-1 tree: `bit exact frozen`
- Stage-2 leaves: `all nonzero-gradient and all changed`
- Formal support / locomotion / robot access: `0 / 0 / 0`

This pass authorizes only a separate 100-update pitch-margin support
training preregistration. It does not authorize training execution,
formal support evaluation, locomotion, deployment, or robot access.
