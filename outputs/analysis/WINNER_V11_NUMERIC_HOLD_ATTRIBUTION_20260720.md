# Winner-v11 Numeric Hold Attribution

Status: `PASS_WINNER_V11_HOLD_ATTRIBUTED_TO_PROTECTED_BACKEND_COMPARISON`

Decision: `PREREGISTER_DISTINCT_WINNER_V12_DECOMPOSED_BACKEND_CONTRACT_ONLY`

JSON SHA-256: `e1ab186678e19ac36a029db9bba25126ea2b080f5c728fc4bc275ff03e017683`

Winner-v11 remains closed and is not rerun. Its only failed quantity was the full protected-policy JAX/ONNX action comparison on moving chains: `4.76837158203125e-07` (`4.0` float32 epsilons) against the frozen `1e-7` rule. The calibrator, new hidden-state math, exact ONNX wrapper identity, x=0, 27-tick phase, action histories, P30 observer, and all action boundaries passed.

The distinct Winner-v12 hypothesis does not relax that threshold. It separates exact protected ONNX identity from the new response branch's JAX/ONNX comparison, while keeping the deployable ABI and physical bounds unchanged. Only a new zero-PPO mechanics preregistration may be designed next; no run, training, behavior evaluation, runtime, or robot action is authorized.
