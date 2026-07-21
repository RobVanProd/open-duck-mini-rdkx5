# Winner-v20 joint recurrent CPU v2 result

- Status: `PASS_WINNER_V20_JOINT_RECURRENT_SUPPORT_CPU_CONTRACT`
- Decision: `AUTHORIZE_SEPARATE_JOINT_RECURRENT_100_UPDATE_PREREGISTRATION_ONLY`
- GitHub run / artifact: `29853236226` / `8504369891`
- Artifact ZIP SHA-256: `e61cab6412927f11356e35a65a9515417036988b1212d961f7ca8e570401c5c6`
- Raw result SHA-256: `8419e343b9608dafc325619da50f70901286618975d64b854b93ee5d8f647900`
- Sampled replay error update 1 / 2: `2.98e-7 / 3.58e-7`
- Update-2 recurrent gradients/deltas: all nonzero
- Formal support / robot: `0 / 0`

The existing recurrent core is trainable once the exact-zero action head
opens on update 1. Every frozen two-update mechanics check passes. This
authorizes only a separate 100-update training preregistration.
