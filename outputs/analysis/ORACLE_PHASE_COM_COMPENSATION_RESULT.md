# Oracle Phase-Conditioned COM Compensation Result

status: `PASS_ORACLE_PHASE_COM_MATRIX_COMPLETE`
decision: `HOLD_ORACLE_PARTIAL`

| condition | cells passed | worst tracking p95 | minimum mean vx | pass |
|---|---:|---:|---:|---|
| NOMINAL | 16/16 | 0.106452147 | -0.000657920 | `True` |
| X_NEG | 0/16 | 0.078375251 | -0.401211662 | `False` |
| X_POS | 4/16 | 0.115031187 | 0.000171074 | `False` |

Final explicit decision token: `HOLD_ORACLE_PARTIAL`

The result is CPU-only feasibility evidence. It does not authorize deployment, training, RDK-X5 or robot access. Robot clearance remains `NO`.
