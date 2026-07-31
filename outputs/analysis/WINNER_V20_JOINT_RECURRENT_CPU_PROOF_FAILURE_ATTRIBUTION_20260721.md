# Winner-v20 CPU proof failure attribution

- Status: `INVALID_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT_PROOF`
- Decision: `CORRECT_ONLY_JOINT_SNAPSHOT_READER_AND_FRESHLY_PREREGISTER`
- Failed run / artifact: `29851858965 / 8503746957`
- Formal result: absent
- Training arm / support cells / robot: `0 / 0 / 0`

The proof reached snapshot readback, then the inherited loader rejected
the new stage label before it could encounter its also-incompatible
five-leaf optimizer assumption. The correction adds an exact Winner-v20
nine-leaf reader; it changes no rollout, objective, or threshold. A fresh
run is required and the failed run remains invalid evidence.
