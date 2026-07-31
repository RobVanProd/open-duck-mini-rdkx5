# T8 state-coherent support-to-locomotion handoff result

- Status: `HOLD_T8_STATE_COHERENT_HANDOFF`
- Decision: `CLOSE_DIRECT_STATE_COHERENT_V121_HANDOFF_WITHOUT_TRAINING`
- Cells: `12/16`
- Result SHA-256: `a94768bf5a431f491f0190064152cf414f933937106da1506fb660ce78f33bf9`

| checkpoint | fit | green | worst tracking | min moving vx | overcurrent run | overload run |
|---|---|---:|---:|---:|---:|---:|
| `V121_TRAIN_MATCHED_HALF` | `p30` | 3/4 | 0.15001326799392697 | 0.0836095046486298 | 8 | 9 |
| `V121_TRAIN_MATCHED_HALF` | `p31_34` | 3/4 | 0.14861901402473449 | 0.08069842182211384 | 9 | 9 |
| `V121_TRAIN_MATCHED_FINAL` | `p30` | 3/4 | 0.15152554512023925 | 0.08295455652764455 | 9 | 10 |
| `V121_TRAIN_MATCHED_FINAL` | `p31_34` | 3/4 | 0.14975844025611879 | 0.08350452361123947 | 8 | 8 |

T8 performs 250 unscored universal-support ticks and then starts the frozen V121 locomotion graph directly: no zero-action home-return interval, no optimizer update, and no behavior wrapper. The final support action, applied-target observer state, 64-D response context, and recurrent chains are audited at the boundary.

A pass earns only the separately preregistered CPU software contract for a response-conditioned V121 continuation. It does not authorize hosted training, robot/RDK-X5 access, Gate 5, torque, motion, deployment, or grounded replay.
