# Winner-v62 residual-teacher causal result

- Status: `PASS_WINNER_V62_RESIDUAL_TEACHER_CAUSAL_DIAGNOSTIC`
- Decision: `SELECT_NEXT_MECHANISM_FROM_FROZEN_RESIDUAL_CLASSIFICATION_ONLY`
- Arm support: `{"full_teacher": 13, "graph": 0, "nonpitch_zero": 0, "pitch_teacher": 12}`
- Classification: `{"either_single_intervention_rescues": 0, "nonpitch_output_causal": 0, "pitch_nonpitch_interaction": 1, "pitch_output_causal": 12, "teacher_insufficient": 0}`
- First/post-first pitch RMS means: `0.07728285739495369 / 0.0817888110754449`
- Optimizer / locomotion / robot: `0 / 0 / 0`
- Result SHA-256: `2da0c48a257e0bace9506998db95a9a7bbf8f736448a78db651742e5235251f5`

The full frozen teacher stabilizes every failed pair, and the pitch-only
intervention stabilizes 12 of 13. The actor remains farther from the stabilizing
pitch target after tick zero than at tick zero, so the Winner-v60 hold is not a
reset-only mapping defect. The evidence selects a persistent pre-fall pitch
alignment mechanism for separate preregistration. It does not authorize that
mechanism, training, checkpoint selection, or robot execution by itself.
