# Ground-Up Command-Conditioned Survival CPU Contract

status: `PASS_CPU_CONTRACT`
execution: `CPU_ONLY`

patch SHA-256: `b00d78a3a7c6f15562cdb14ccfd9129ce0001845bbbca8c343965f98a054dc7f`

| vx / command | expected gate | observed gate |
|---:|---:|---:|
| -1.0 | 0.000 | 0.000 |
| 0.0 | 0.000 | 0.000 |
| 0.5 | 0.500 | 0.500 |
| 1.0 | 1.000 | 1.000 |
| 1.5 | 1.000 | 1.000 |

For positive forward commands, the existing alive and yaw rewards are multiplied by this progress gate. Their scales remain 20 and 6. At x=0, both canonical rewards remain active without conditioning.

Failed checks: `none`.

This is wiring evidence only, not learned behavior or policy clearance.
