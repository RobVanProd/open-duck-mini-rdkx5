# Ground-Up Torso-COM Remediation TORSO_COM_X_POS Result

condition: `TORSO_COM_X_POS`
execution: `CPU_ONLY`

| arm | step | fit | x=0 | moving | worst tracking | min vx | readback | pass |
|---|---:|---|---|---|---:|---:|---|---|
| `U_CURRICULUM` | 512000 | `p30` | `True` | `False` | 0.174626374 | 0.400965536 | `True` | `False` |
| `U_CURRICULUM` | 512000 | `p31_34` | `True` | `False` | 0.175107884 | 0.410225349 | `True` | `False` |
| `U_CURRICULUM` | 1024000 | `p30` | `True` | `False` | 0.179093403 | 0.395053681 | `True` | `False` |
| `U_CURRICULUM` | 1024000 | `p31_34` | `True` | `False` | 0.179574585 | 0.399658953 | `True` | `False` |
| `A05_DIRECT` | 1003520 | `p30` | `True` | `False` | 0.179997325 | 0.327373996 | `True` | `False` |
| `A05_DIRECT` | 1003520 | `p31_34` | `True` | `False` | 0.183277678 | 0.312732655 | `True` | `False` |
| `A05_DIRECT` | 2007040 | `p30` | `True` | `False` | 0.181867480 | 0.292249887 | `True` | `False` |
| `A05_DIRECT` | 2007040 | `p31_34` | `True` | `False` | 0.179091907 | 0.254247576 | `True` | `False` |
| `U05_DIRECT` | 1003520 | `p30` | `True` | `False` | 0.179570889 | 0.360959041 | `True` | `False` |
| `U05_DIRECT` | 1003520 | `p31_34` | `True` | `False` | 0.177845818 | 0.381265094 | `True` | `False` |
| `U05_DIRECT` | 2007040 | `p30` | `True` | `False` | 0.179979193 | 0.323186272 | `True` | `False` |
| `U05_DIRECT` | 2007040 | `p31_34` | `True` | `False` | 0.180909431 | 0.318930357 | `True` | `False` |

condition complete pass: `False`

This result is evidence for the frozen remediation selection only. It does not authorize R2 resumption, R3+, training, runtime work, RDK-X5, or robot access.
