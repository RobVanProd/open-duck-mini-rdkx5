# T3 observation z-score v2 preregistration

- Status: `PREREGISTERED_T3_V2_OBSERVATION_ZSCORE_AUDIT`
- Contract SHA-256: `38facbe2b789db908f57a424766cc87d7fcbc4b9df7a37df82c5700b5d42c139`
- V1 is invalid because it included a mock auto-config trace; its draft result has zero decision weight.
- Every Gate 3 source is hash-frozen and independently verifies `backend: x5`, 250 samples, no policy, no servo bus, and no torque.
- Missing policy fields remain unavailable and are never synthesized.
