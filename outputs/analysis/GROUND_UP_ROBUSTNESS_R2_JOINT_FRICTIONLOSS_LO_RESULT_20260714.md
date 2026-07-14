# Ground-Up Robustness R2 Condition Result

condition: `JOINT_FRICTIONLOSS_LO`
status: `PASS_ROBUSTNESS_R2_CONDITION`
decision: `AUTHORIZE_JOINT_FRICTIONLOSS_HI_ONLY`

| fit | step | x=0 | nominal | tracking | min vx | readback | pass |
|---|---:|---|---|---:|---:|---|---|
| `p30` | 512000 | `True` | `True` | 0.179715067 | 0.084560309 | `True` | `True` |
| `p30` | 1024000 | `True` | `True` | 0.182504302 | 0.097961669 | `True` | `True` |
| `p31_34` | 512000 | `True` | `True` | 0.179247910 | 0.085901587 | `True` | `True` |
| `p31_34` | 1024000 | `True` | `True` | 0.180774349 | 0.100234755 | `True` | `True` |

Only the next frozen condition is authorized after a pass. A failure stops R2 immediately. No R3+, training, RDK-X5, or robot access is authorized.
