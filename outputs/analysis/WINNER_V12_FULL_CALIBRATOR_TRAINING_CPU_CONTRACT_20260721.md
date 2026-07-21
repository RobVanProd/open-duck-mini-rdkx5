# Winner-v12 full calibrator training CPU contract

- Status: `PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT_FROZEN`
- Decision: `AUTHORIZE_ONE_ZERO_UPDATE_FULL_TRAINING_CPU_CONTRACT_RUN_ONLY`
- Contract SHA-256: `6288b4f9bc1919ecb2638fe1bc1f6908f7e720f40f7721b4677c81f151cb9505`
- Source-manifest SHA-256: `30b0bf166aaa83ee500eb0b3536579a6d5c58ffd1e9c797d3269541c0f503808`

This prospective contract authorizes one CPU-only implementation check with zero optimizer updates. It exercises the complete 80-episode rollout topology, exact terminal masking, snapshot/recovery integrity, and a nonzero recurrent ONNX chain. It does not run formal support cells or train locomotion, and it provides no robot or Gate 5 clearance.

A passing result may authorize only the single frozen full calibrator run described by the preregistration. The trained calibrator would still require its separate 124-cell support/context gate and is not itself a walking policy.
