# Ground-Up Robustness R2 Condition Result

condition: `ARMATURE_HI`
status: `PASS_ROBUSTNESS_R2_CONDITION`
decision: `AUTHORIZE_TORSO_COM_X_NEG_ONLY`

| fit | step | x=0 | nominal | tracking | min vx | readback | pass |
|---|---:|---|---|---:|---:|---|---|
| `p30` | 512000 | `True` | `True` | 0.180975640 | 0.083785261 | `True` | `True` |
| `p30` | 1024000 | `True` | `True` | 0.183966231 | 0.092567844 | `True` | `True` |
| `p31_34` | 512000 | `True` | `True` | 0.180108523 | 0.089601620 | `True` | `True` |
| `p31_34` | 1024000 | `True` | `True` | 0.182234061 | 0.098036348 | `True` | `True` |

Only the next frozen condition is authorized after a pass. A failure stops R2 immediately. No R3+, training, RDK-X5, or robot access is authorized.
