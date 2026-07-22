# Winner-v51b full-action teacher one-update CPU result

- Status: `PASS_WINNER_V51B_FULL_ACTION_TEACHER_ONE_UPDATE_CPU_PROOF`
- Decision: `AUTHORIZE_BOUNDED_FULL_ACTION_TEACHER_CONTINUATION_PREREGISTRATION_ONLY`
- Optimizer count: `352 → 353`
- Full-action teacher loss: `0.004192190710455179 → 0.004095083102583885`
- Snapshot SHA-256: `e0335fbcc91118b8163e1c6bd245caed2f44535e54bf35e2f07f6ea3e56a276e`
- Candidate ONNX SHA-256: `6d300081d28c1f3c099f2dc8c2aa3b5e1a92b9e86bbdb68d9504323c5486eca2`
- JAX/ONNX maximum error: `1.4551915228366852e-11`
- Formal support / continuation / robot: `0 / 0 / 0`
- Result SHA-256: `9e08a08bd9614fbb31dc5104abb64270e2739157026f9c966e3466578bf92aa7`

Every trainable leaf changed, every frozen parameter leaf stayed bit-exact, the
complete snapshot and Adam state round-tripped exactly, and the candidate graph
retained the stateful hard-bounded `115/14/64` ABI without teacher or training-
only tensors.

This candidate is not selected for deployment and has not run a support gate.
The pass authorizes only preregistration of a bounded full-action continuation.
