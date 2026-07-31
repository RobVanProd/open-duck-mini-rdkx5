# Winner-v20 joint-recurrent support attribution

- Status: `PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_ATTRIBUTION`
- Decision: `PREREGISTER_ONE_JOINT_RECURRENT_PPO_CPU_CONTRACT`
- New parameters / ABI change: `0 / false`
- Optimizer / robot access now: `0 / 0`

Winner-v15 delivered a dense exact reward and changed every action-head
leaf, yet held the deployable recurrent encoder bit-exact and retained
the same twelve early negative-X failures at both checkpoints. Winner-v16
through Winner-v19 then closed post-policy correction wrappers.

The next causal A/B uses the identical source, population, seed, reward,
and budget as Winner-v15. Its only variable is full-BPTT training of the
existing recurrent core together with the action head. The auxiliary
predictor stays bit-exact and the ONNX ABI does not change.
