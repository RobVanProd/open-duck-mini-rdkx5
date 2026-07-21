# Winner-v13 support-controller training preregistration

- Status: `PREREGISTERED_WINNER_V13_SUPPORT_CONTROLLER_TRAINING`
- Decision: `AUTHORIZE_ONE_100_UPDATE_SUPPORT_CONTROLLER_RUN_ONLY`
- Source: exact passing Stage-1 update-100 snapshot
- Training: `100` CPU-only Stage-2 updates, `80 x 250` ticks each
- Frozen: all Stage-1 encoder and response-prediction leaves
- Recovery: atomic snapshot after every update
- Persistent checkpoints: half `50`, final `100`
- Formal support / locomotion / robot: `0 / 0 / 0`

Reward curves are not a success gate. A mechanically valid run only
authorizes the separately frozen 124-cell half/final support gate.
The proposed flat transport kernel remains deferred until evidence
shows that recurrent information transport is the limiting mechanism.
