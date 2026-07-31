# Ground-Up Robustness R2 Condition Result

condition: `TORSO_COM_X_NEG`
status: `PASS_ROBUSTNESS_R2_CONDITION_NO_ADVANCE`
decision: `STOP_R2_AT_FIRST_FAILED_CONDITION`

| fit | step | x=0 | nominal | tracking | min vx | readback | pass |
|---|---:|---|---|---:|---:|---|---|
| `p30` | 512000 | `False` | `False` | 0.160103977 | -0.402549115 | `True` | `False` |
| `p30` | 1024000 | `False` | `False` | 0.159585547 | -0.404190434 | `True` | `False` |
| `p31_34` | 512000 | `False` | `False` | 0.159523487 | -0.392947291 | `True` | `False` |
| `p31_34` | 1024000 | `False` | `False` | 0.161376953 | -0.410971326 | `True` | `False` |

Only the next frozen condition is authorized after a pass. A failure stops R2 immediately. No R3+, training, RDK-X5, or robot access is authorized.
