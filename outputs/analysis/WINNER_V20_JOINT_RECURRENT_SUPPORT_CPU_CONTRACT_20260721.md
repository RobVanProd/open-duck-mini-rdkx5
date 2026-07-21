# Winner-v20 joint recurrent support CPU contract

- Status: `FROZEN_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT`
- Decision: `AUTHORIZE_EXACT_TWO_UPDATE_JOINT_RECURRENT_PPO_PROOF_ONLY`
- Source: identical Winner-v13 Stage-1 update-100 snapshot
- Proof updates / support cells / robot: `2 / 0 / 0`

Update 1 must reproduce the exact zero recurrent gradient imposed by
the source's zero action head. Update 2 is the first possible recurrent
gradient test and must change all nine selected leaves. Replay remains
`<=1e-6` on sampled ticks. No parameter, reward, wrapper, or ABI change
is introduced.
