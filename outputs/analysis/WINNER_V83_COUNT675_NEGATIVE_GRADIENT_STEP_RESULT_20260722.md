# Winner-v83 count-675 negative-gradient step result

- Status: `PASS_WINNER_V83_COUNT675_NEGATIVE_GRADIENT_STEP`
- Decision: `PREREGISTER_BOUNDED_NEGATIVE_GRADIENT_PITCH_HEAD_CONTINUATION_ONLY`
- Optimizer count: `674 -> 675`
- Accepted fraction: `1/2` (the first strict descent)
- Pitch-teacher loss: `0.0072185365 -> 0.0071995878`
- Predictor loss: bit-exact at `0.4711624682`
- Mutable parameters: six pitch action-weight columns and bias elements only
- Optimizer `m/v`: all elements bit-exact preserved
- Snapshot SHA-256: `cae62d8f...f469827`
- Stateful ONNX SHA-256: `e1bc9fc0...103539`
- Formal support / robot access: `0 / 0`
- Result SHA-256: `1ac6326f6a9b0a703e5035aec186d4bf4601774008ea8b7029629b8f0d22a98d`

The V82-selected direction reproduces exactly and passes as a one-step proof.
The graph retains the frozen `115 + 14 + 64` stateful ABI, JAX/ONNX agreement,
and exact previous-action chain. This result authorizes only preregistration of
a bounded continuation using the same negative-gradient mechanism. It does not
select a checkpoint or authorize support evaluation, deployment, or robot
access.
