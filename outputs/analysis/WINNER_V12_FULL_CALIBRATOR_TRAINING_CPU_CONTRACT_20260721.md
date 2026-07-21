# Winner-v12 full calibrator training CPU contract

- Status: `PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT_FROZEN`
- Decision: `AUTHORIZE_ONE_ZERO_UPDATE_FULL_TRAINING_CPU_CONTRACT_RUN_ONLY`
- Contract SHA-256: `5795b079dfc47ab54a7d59faa217f282551fda0bb8c18f1857ceae9b79492eb6`
- Source-manifest SHA-256: `a285a720c98c851bfccf7f95e8a0560a1af7a948e66bcd9950ad6cd208c6993b`

This prospective contract authorizes one CPU-only implementation check with zero optimizer updates. It exercises the complete 80-episode rollout topology, exact terminal masking, snapshot/recovery integrity, and a nonzero recurrent ONNX chain. It does not run formal support cells or train locomotion, and it provides no robot or Gate 5 clearance.

A passing result may authorize only the single frozen full calibrator run described by the preregistration. The trained calibrator would still require its separate 124-cell support/context gate and is not itself a walking policy.
