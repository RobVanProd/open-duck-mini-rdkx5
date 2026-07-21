# Winner-v13 support-controller CPU contract

- Status: `FROZEN_WINNER_V13_SUPPORT_CONTROLLER_CPU_CONTRACT`
- Decision: `AUTHORIZE_ONE_RESTORED_STAGE2_UPDATE_ONLY`
- Source Stage-1 snapshot: `8c1392c7…6f163af`
- Stage-2 updates: `1`
- Formal support / locomotion / robot: `0 / 0 / 0`

The CPU proof restores the exact passing encoder, performs one PPO
support update, freezes all Stage-1 leaves, and validates the bounded
stateful ONNX graph. A pass authorizes only training preregistration.
