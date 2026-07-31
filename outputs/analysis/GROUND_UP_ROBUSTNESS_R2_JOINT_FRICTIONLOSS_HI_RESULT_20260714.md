# Ground-Up Robustness R2 Condition Result

condition: `JOINT_FRICTIONLOSS_HI`
status: `PASS_ROBUSTNESS_R2_CONDITION`
decision: `AUTHORIZE_ARMATURE_LO_ONLY`

| fit | step | x=0 | nominal | tracking | min vx | readback | pass |
|---|---:|---|---|---:|---:|---|---|
| `p30` | 512000 | `True` | `True` | 0.182750005 | 0.083507029 | `True` | `True` |
| `p30` | 1024000 | `True` | `True` | 0.181891280 | 0.092889360 | `True` | `True` |
| `p31_34` | 512000 | `True` | `True` | 0.180432379 | 0.082995802 | `True` | `True` |
| `p31_34` | 1024000 | `True` | `True` | 0.180834180 | 0.096287008 | `True` | `True` |

Only the next frozen condition is authorized after a pass. A failure stops R2 immediately. No R3+, training, RDK-X5, or robot access is authorized.
