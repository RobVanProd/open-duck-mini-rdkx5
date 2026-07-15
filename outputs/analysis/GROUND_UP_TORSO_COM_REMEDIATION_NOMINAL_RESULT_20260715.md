# Ground-Up Torso-COM Remediation NOMINAL Result

condition: `NOMINAL`
execution: `CPU_ONLY`

| arm | step | fit | x=0 | moving | worst tracking | min vx | readback | pass |
|---|---:|---|---|---|---:|---:|---|---|
| `U_CURRICULUM` | 512000 | `p30` | `True` | `True` | 0.181036043 | 0.082604651 | `True` | `True` |
| `U_CURRICULUM` | 512000 | `p31_34` | `True` | `True` | 0.179808843 | 0.085516324 | `True` | `True` |
| `U_CURRICULUM` | 1024000 | `p30` | `True` | `True` | 0.181958497 | 0.078055398 | `True` | `True` |
| `U_CURRICULUM` | 1024000 | `p31_34` | `True` | `True` | 0.181723797 | 0.078470439 | `True` | `True` |
| `A05_DIRECT` | 1003520 | `p30` | `True` | `True` | 0.182503945 | 0.075511779 | `True` | `True` |
| `A05_DIRECT` | 1003520 | `p31_34` | `True` | `True` | 0.180747604 | 0.076356020 | `True` | `True` |
| `A05_DIRECT` | 2007040 | `p30` | `True` | `True` | 0.179557443 | 0.077583333 | `True` | `True` |
| `A05_DIRECT` | 2007040 | `p31_34` | `True` | `True` | 0.180334890 | 0.077266282 | `True` | `True` |
| `U05_DIRECT` | 1003520 | `p30` | `True` | `True` | 0.179638028 | 0.085034688 | `True` | `True` |
| `U05_DIRECT` | 1003520 | `p31_34` | `True` | `True` | 0.179207653 | 0.088500255 | `True` | `True` |
| `U05_DIRECT` | 2007040 | `p30` | `True` | `True` | 0.179710203 | 0.073316405 | `True` | `True` |
| `U05_DIRECT` | 2007040 | `p31_34` | `True` | `True` | 0.178139526 | 0.073945710 | `True` | `True` |

condition complete pass: `True`

This result is evidence for the frozen remediation selection only. It does not authorize R2 resumption, R3+, training, runtime work, RDK-X5, or robot access.
