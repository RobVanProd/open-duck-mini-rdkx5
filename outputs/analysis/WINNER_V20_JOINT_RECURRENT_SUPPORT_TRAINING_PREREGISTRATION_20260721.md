# Winner-v20 joint recurrent support training preregistration

- Status: `PREREGISTERED_WINNER_V20_JOINT_RECURRENT_SUPPORT_TRAINING`
- Decision: `AUTHORIZE_ONE_100_UPDATE_JOINT_RECURRENT_CAUSAL_AB_ONLY`
- Source: identical Winner-v13 Stage-1 update-100 snapshot
- Updates / checkpoint updates: `100 / 50,100`
- Formal support / robot now: `0 / 0`

This is a one-variable causal A/B against Winner-v15. Population, seed,
reward, optimizer constants, horizon, action bounds, and checkpoints are
unchanged. Only the existing recurrent core joins the PPO gradient through
full 250-tick BPTT. The auxiliary predictor and ONNX ABI remain frozen.

Training metrics cannot select a checkpoint. A passing artifact authorizes
only a separately frozen unchanged 124-cell gate over both checkpoints.
