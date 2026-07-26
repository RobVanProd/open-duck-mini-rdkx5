# T8 recurrent-ABI pre-outcome amendment

- Status: `PREREGISTERED_T8_PREOUTCOME_ABI_ORDER_CORRECTION`
- Contract SHA-256: `a3f1141d761352f493dafd7416a36c62703b8c4d4489cc76fefff04be1ce2a04`
- Evidence boundary: `0` simulator modes, `0` JSONL traces, `0` completed blocks, `0` behavior cells, and no result artifact.
- Failure: the worker declared the recurrent state tuple in the reverse order from the already-frozen response-conditioned evaluator ABI.
- Correction: inputs `h_in,previous_action`; outputs `h_out,previous_action_out`.
- Both wrapped V121 graphs retain the exact frozen input/output name sets, shapes, hashes, and 1,024-tick bit-exact source parity.
- Candidate, policies, support prefix, physical handoff semantics, matrix, gates, decision rule, and authority are unchanged.

This amendment permits only resumption of the exact T8 CPU screen. It does not authorize training, hosted compute, robot/RDK-X5 access, Gate 5, torque, motion, deployment, or grounded replay.
