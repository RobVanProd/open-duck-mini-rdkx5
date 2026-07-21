# Winner-v15 pitch-margin CPU proof failure attribution

- Status: `INVALID_WINNER_V15_PITCH_MARGIN_CPU_CONTRACT_PROOF`
- Decision: `CORRECT_ONLY_SETTLED_BONUS_REWARD_PROOF_AND_FRESHLY_PREREGISTER`
- GitHub run / artifact: `29836320395 / 8497528079`
- Contract / training updates: `1 / 0`
- Formal support / locomotion / robot access: `0 / 0 / 0`

All substantive mechanics checks passed. The sole failure was a proof
that tried to recover a fractional reward after adding and subtracting
the 250-point float32 terminal bonus. The only permitted change builds
the expected final reward directly and freshly preregisters the same
objective contract. No reward, policy, population, or threshold changes.
