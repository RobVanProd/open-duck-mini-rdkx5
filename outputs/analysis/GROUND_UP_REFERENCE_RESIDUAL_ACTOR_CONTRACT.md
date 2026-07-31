# Ground-Up Reference-Residual Actor Contract

status: `PASS_CPU_REFERENCE_RESIDUAL_ACTOR_CONTRACT`

The reference-anchored residual actor passed its offline software contract on
CPU. This result does not claim walking behavior and does not clear a policy
for the robot.

## Verified contract

- JAX exposed only `TFRT_CPU_0`; the robot, RDK-X5, local iGPU, and onboard GPU
  were not accessed.
- The policy interface is observation `115`, logits `28`, and action `14`.
- At initialization, the deterministic action equals the projected reference
  action with maximum absolute error `2.98e-8`.
- With a zero reference, the initialized deterministic action is exactly zero.
- A sampled PPO action and its log probability are finite.
- The step-zero ONNX graph contains the reference gather, clip, inverse tanh,
  learned residual addition, and final tanh inside the policy graph.
- The step-zero ONNX output equals its reference input with maximum absolute
  error `2.98e-8`.
- A 1,024-step CPU PPO smoke completed and exported the same final-action ONNX
  graph with finite bounded output. Its departure from the reference is
  expected because its residual weights received PPO updates.

## Frozen identities

- projected table SHA-256:
  `8102d9cd139584816d807ca635bcca6d37fa6b3c455848e00395b6d565968212`
- actor source SHA-256:
  `c5c9e7671b2c07af4218a6180ca221547c42d4cc491c76f5e12612b75d58a84e`
- runner patch SHA-256:
  `57bcf2394fa47745e9c26c6933e58a06c3799aba35e7000762befc5fac2f7d3b`
- step-zero ONNX SHA-256:
  `b7adb8981e920d9e690f42256e0a84ab0bf0c2020443fe7979ddbb450d5d43d7`
- trained smoke ONNX SHA-256:
  `c07a71bf8dc84d457c50c6afbc0f5be17f3c6c738c8c7f4c4232ceeaba2eaf9e`

The machine-readable evidence is
`outputs/analysis/ground_up_reference_residual_actor_contract.json`, and the
reproducible checker is `tools/check_ground_up_reference_residual_actor.py`.
