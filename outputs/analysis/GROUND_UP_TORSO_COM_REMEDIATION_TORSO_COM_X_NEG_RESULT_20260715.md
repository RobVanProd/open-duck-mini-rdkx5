# Ground-Up Torso-COM Remediation TORSO_COM_X_NEG Result

condition: `TORSO_COM_X_NEG`
execution: `CPU_ONLY`

| arm | step | fit | x=0 | moving | worst tracking | min vx | readback | pass |
|---|---:|---|---|---|---:|---:|---|---|
| `U_CURRICULUM` | 512000 | `p30` | `False` | `False` | 0.159075439 | -0.386959755 | `True` | `False` |
| `U_CURRICULUM` | 512000 | `p31_34` | `False` | `False` | 0.161058903 | -0.386552179 | `True` | `False` |
| `U_CURRICULUM` | 1024000 | `p30` | `False` | `False` | 0.161905217 | -0.410234554 | `True` | `False` |
| `U_CURRICULUM` | 1024000 | `p31_34` | `False` | `False` | 0.159153271 | -0.404181959 | `True` | `False` |
| `A05_DIRECT` | 1003520 | `p30` | `False` | `False` | 0.154437423 | -0.363655473 | `True` | `False` |
| `A05_DIRECT` | 1003520 | `p31_34` | `False` | `False` | 0.150843990 | -0.354706634 | `True` | `False` |
| `A05_DIRECT` | 2007040 | `p30` | `False` | `False` | 0.156768489 | -0.345406348 | `True` | `False` |
| `A05_DIRECT` | 2007040 | `p31_34` | `False` | `False` | 0.149229473 | -0.347589047 | `True` | `False` |
| `U05_DIRECT` | 1003520 | `p30` | `False` | `False` | 0.162542030 | -0.405355284 | `True` | `False` |
| `U05_DIRECT` | 1003520 | `p31_34` | `False` | `False` | 0.159208521 | -0.402595765 | `True` | `False` |
| `U05_DIRECT` | 2007040 | `p30` | `False` | `False` | 0.160454929 | -0.388988726 | `True` | `False` |
| `U05_DIRECT` | 2007040 | `p31_34` | `False` | `False` | 0.145186007 | -0.396848205 | `True` | `False` |

condition complete pass: `False`

This result is evidence for the frozen remediation selection only. It does not authorize R2 resumption, R3+, training, runtime work, RDK-X5, or robot access.
