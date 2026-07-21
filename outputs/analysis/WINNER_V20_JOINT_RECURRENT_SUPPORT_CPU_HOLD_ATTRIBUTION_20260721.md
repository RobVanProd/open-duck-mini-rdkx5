# Winner-v20 joint recurrent CPU hold attribution

- Status: `PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_HOLD_ATTRIBUTION`
- Decision: `PREREGISTER_EXACT_TWO_UPDATE_JOINT_RECURRENT_CPU_CONTRACT`
- Classification: `ZERO_ACTION_HEAD_CHAIN_RULE_GATE`
- Training arm / support cells / robot: `0 / 0 / 0`

The recurrent core is not shown dead. Its gradient is necessarily zero
on update 1 because the shared action weight starts exactly zero. Update 1
moves both action-head leaves; update 2 is the first causal test of recurrent
trainability. Replay equality remains `<=1e-6`, but is correctly measured
only on sampled ticks rather than excluded post-terminal padding.
