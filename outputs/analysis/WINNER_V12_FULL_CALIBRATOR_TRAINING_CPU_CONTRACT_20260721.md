# Winner-v12 full calibrator training CPU contract

- Status: `PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT_FROZEN`
- Decision: `AUTHORIZE_ONE_ZERO_UPDATE_FULL_TRAINING_CPU_CONTRACT_RUN_ONLY`
- Contract SHA-256: `72d115ba7772a378f331045e4dcda8f7742cf0138f5d7779b200e36e37ffd521`
- Source-manifest SHA-256: `6a79eb4e752b18b12d63122feb636fa42f6955d36dfc8daed755abfa90803e29`

This prospective contract authorizes one CPU-only implementation check with zero optimizer updates. It exercises the complete 80-episode rollout topology, exact terminal masking, snapshot/recovery integrity, and a nonzero recurrent ONNX chain. It does not run formal support cells or train locomotion, and it provides no robot or Gate 5 clearance.

A passing result may authorize only the single frozen full calibrator run described by the preregistration. The trained calibrator would still require its separate 124-cell support/context gate and is not itself a walking policy.
