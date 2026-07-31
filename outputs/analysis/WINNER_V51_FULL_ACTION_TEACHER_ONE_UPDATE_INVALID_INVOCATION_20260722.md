# Winner-v51 full-action teacher one-update invalid invocation

- Status: `INVALID_WINNER_V51_FULL_ACTION_TEACHER_ONE_UPDATE_INVOCATION`
- Decision: `INVALID_PROOF_IMPLEMENTATION_DO_NOT_USE_PARTIAL_ARTIFACTS`
- Formal result JSON: not written
- Failure: `KeyError: 'hidden_bias'` at runner line 433

The frozen runner completed the upstream V50 recomputation and constructed a
single in-memory update, snapshot, and candidate graph. It then failed while
building checks because `full_gradient_max` was assigned the entire
`objective_evidence` dictionary; the following lookup expected the nested
`full_teacher_gradient_max_abs` dictionary.

The partial NPZ and ONNX are hashed in the JSON record solely to prevent later
confusion. They are invalid evidence and must not be used for continuation,
deployment selection, or robot clearance. The V51 source remains frozen. Any
rerun requires a separately preregistered correction.
