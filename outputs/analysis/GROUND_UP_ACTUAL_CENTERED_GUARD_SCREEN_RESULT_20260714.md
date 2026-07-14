# Ground-Up Actual-Centered Guard Screen Result

status: `PASS_ACTUAL_CENTERED_GUARD_WITH_WINNER`
decision: `ADVANCE_G1_EXACT_BOUNDARY_T2_EQUAL_TO_PREREGISTERED_X0_GATE`

| guard | tail | half worst p95 | final worst p95 | min vx | pass |
|---|---|---:|---:|---:|---|
| `G1_EXACT_BOUNDARY` | `T2_EQUAL` | 0.180822033 | 0.181667066 | 0.083376151 | `True` |
| `G1_EXACT_BOUNDARY` | `T3_FOUR` | 0.182989806 | 0.179285967 | 0.075169638 | `True` |
| `G2_HALF_TICK_BUFFER` | `T2_EQUAL` | 0.171371931 | 0.171765870 | 0.080844407 | `False` |
| `G2_HALF_TICK_BUFFER` | `T3_FOUR` | 0.169793421 | 0.166580373 | 0.072076240 | `True` |
| `G3_FULL_TICK_BUFFER` | `T2_EQUAL` | 0.156643009 | 0.157857758 | 0.072196866 | `True` |
| `G3_FULL_TICK_BUFFER` | `T3_FOUR` | 0.157981157 | 0.156147319 | 0.067254501 | `True` |

winner: `G1_EXACT_BOUNDARY/T2_EQUAL`

The actual-position-centered invariant repairs the measured compound lag failure. The least restrictive 0.20 rad guard passes both half and final checkpoints for T2 and T3; the frozen tie-break selects T2. This is the first persistent full-horizon nominal winner in the ground-up route, but it requires a separately preregistered x=0 gate.

This authorizes only preregistration of an x=0 preservation gate. It does not authorize that gate before preregistration, training, Colab, RDK-X5, or robot access.
