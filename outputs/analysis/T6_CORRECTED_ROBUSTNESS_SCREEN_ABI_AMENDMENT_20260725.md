# T6 recurrent-ABI pre-outcome amendment

- Status: `PREREGISTERED_T6_PREOUTCOME_RECURRENT_ABI_CORRECTION`
- Contract SHA-256: `675698f388b94454ab427104ba34d8542375088300d71cde91508bf520392b34`
- Evidence boundary: `0` completed blocks, `0` behavior cells, no result artifact.
- Failure: first inference rejected missing `h_in`; no policy output or behavior outcome was produced.
- Correction: state inputs `previous_action,h_in`; state outputs `previous_action_out,h_out`.
- All eight frozen ONNX files expose exact `[1,115]`, `[1,14]`, and `[1,64]` input/state shapes.
- Candidate population, policies, dynamics condition, matrix, gates, selection rule, and authority are unchanged.
- No training, hosted compute, robot access, Gate 5, torque, or motion is authorized.
