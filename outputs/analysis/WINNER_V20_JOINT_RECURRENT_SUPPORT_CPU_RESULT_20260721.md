# Winner-v20 joint recurrent CPU result

- Status: `HOLD_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT`
- Decision: `DO_NOT_TRAIN_JOINT_RECURRENT_SUPPORT_ARM`
- GitHub run / artifact: `29852380511` / `8503945380`
- Artifact ZIP SHA-256: `b603de1cbefd8212bf9a8d467c0e6c715f56f6cf4baa82ab71c7fdbd34998def`
- Raw result SHA-256: `025f61a7ffa118e6f023d737e6ab0ac19cf6cbe3b1a8c718e01faa5b49c57d40`
- Recurrent gradient / delta at update 1: exact zero on all four leaves
- Action-head gradient / delta at update 1: nonzero on both leaves
- Formal support / robot: `0 / 0`

The shared source intentionally has an exact-zero action head, so the
first joint gradient cannot reach the recurrent core. The one-update
contract therefore holds and grants no training authority.
