# Ground-Up Robustness R2 Condition Result

condition: `ARMATURE_LO`
status: `PASS_ROBUSTNESS_R2_CONDITION`
decision: `AUTHORIZE_ARMATURE_HI_ONLY`

| fit | step | x=0 | nominal | tracking | min vx | readback | pass |
|---|---:|---|---|---:|---:|---|---|
| `p30` | 512000 | `True` | `True` | 0.180855995 | 0.086461715 | `True` | `True` |
| `p30` | 1024000 | `True` | `True` | 0.183170038 | 0.097619724 | `True` | `True` |
| `p31_34` | 512000 | `True` | `True` | 0.178732973 | 0.084911748 | `True` | `True` |
| `p31_34` | 1024000 | `True` | `True` | 0.181057256 | 0.096040766 | `True` | `True` |

Only the next frozen condition is authorized after a pass. A failure stops R2 immediately. No R3+, training, RDK-X5, or robot access is authorized.
