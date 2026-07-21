# Winner-v12 full calibrator training CPU contract

- Status: `PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT_FROZEN`
- Decision: `AUTHORIZE_ONE_ZERO_UPDATE_FULL_TRAINING_CPU_CONTRACT_RUN_ONLY`
- Contract SHA-256: `7ce6fcefdfb38bdbb72ed26b921eac6e135145d630e981c45843a28f463e1f2d`
- Source-manifest SHA-256: `5c511da0fe257e8b1a90510e3e95e38d7837c84d7fda2b586795d74e68a94b89`

This prospective contract authorizes one CPU-only implementation check with zero optimizer updates. It exercises the complete 80-episode rollout topology, exact terminal masking, snapshot/recovery integrity, and a nonzero recurrent ONNX chain. It does not run formal support cells or train locomotion, and it provides no robot or Gate 5 clearance.

A passing result may authorize only the single frozen full calibrator run described by the preregistration. The trained calibrator would still require its separate 124-cell support/context gate and is not itself a walking policy.
