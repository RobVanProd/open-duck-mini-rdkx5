# Ground-Up Hard-Vector Command-Support CPU Contract

status: `PASS_CPU_HARD_VECTOR_COMMAND_SUPPORT_CONTRACT`

runner patch SHA-256: `900e65beaa4aa714ec352a527bf3f1a85888c0c76dab8d4cbef2352fa4986875`
network source SHA-256: `546f375fa3c2f34158f49f1ac07cdc5ff6dc41d1a94322f4334bd48835911630`

failed checks: `none`

## Measured contract

- 4,096 sampled forward commands stayed inside `[0.074, 0.080)` with standard
  deviation `0.00174425`; all other command axes were exactly zero.
- Reset motor targets equal home, reset velocity and applied-action history are
  zero, and the first aggressive transition hits (without exceeding) every one
  of the 14 measured target-rate bounds.
- `state.info`, reward inputs, and the returned actor observation all carry the
  realized bounded action/targets rather than the unachievable raw request.
- Stateful ONNX inputs are `obs` and `previous_action`; outputs are
  `continuous_actions` and `previous_action_out`. An eight-tick alternating
  reference chain measured zero per-joint bound excess and exact state output.
- The initial export attempt correctly failed because ONNX opset-12 `Clip`
  requires scalar bounds. The final graph uses broadcast-safe elementwise
  `Min` then `Max`, and its JAX/ONNX first-action error is `1.49e-8`.

This proves the CPU software transition and stateful export contract only. It is not training evidence, policy qualification, or robot clearance.
