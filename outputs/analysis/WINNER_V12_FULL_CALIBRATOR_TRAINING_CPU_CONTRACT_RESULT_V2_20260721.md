# Winner-v12 corrected full-calibrator CPU-contract result

- Status: `PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_CPU_CONTRACT`
- Decision: `AUTHORIZE_ONE_WINNER_V12_FULL_CALIBRATOR_TRAINING_RUN_ONLY`
- GitHub run: `29808349887` (attempt `1`)
- Commit: `35069ead37433e1b8d98c3082d4b163e06ec5fef`
- Artifact digest: `sha256:f02a902412abf23ef08832c3d73e3faee13f5af53cfe977bb3832c4b13fe853c`
- Raw result SHA-256: `d0d035123122bc37462c2a6e83cb6a8bc82081f34cfdd3317fd79db3fbbc010e`
- Stage-1 attempted/valid: `14113` / `14072`
- Stage-2 attempted/valid: `18251` / `18243`
- Optimizer updates: `0`
- Formal support cells: `0`
- Robot access/clearance: `0` / `false`

Every exact corrected zero-update check passed in the pinned CPU
environment, including the mixed-type normalization proof and strict
snapshot archive/metadata/metric rejection tests. This authorizes only
one separately hash-bound seed-120120 full-calibrator training run.
It does not authorize the 124-cell gate, locomotion training, deployment
selection, Gate 5, or robot access.
