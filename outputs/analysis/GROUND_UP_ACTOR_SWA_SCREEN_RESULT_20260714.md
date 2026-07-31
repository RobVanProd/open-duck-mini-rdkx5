# Ground-Up Actor-SWA Screen Result

status: `PASS_ACTOR_SWA_SCREEN_NO_WINNER`
decision: `CLOSE_ACTOR_SWA_STABILIZATION_FORMULATION`

| rate | tail | cumulative half worst p95 | cumulative final worst p95 | pass |
|---|---|---:|---:|---|
| `U0_UNCHANGED` | `T2_EQUAL` | 0.217668366 | 0.215297848 | `False` |
| `U0_UNCHANGED` | `T3_FOUR` | 0.224038136 | 0.214923376 | `False` |
| `R3_FOUR_GAP` | `T2_EQUAL` | 0.221020448 | 0.217614633 | `False` |
| `R3_FOUR_GAP` | `T3_FOUR` | 0.221891606 | 0.211410439 | `False` |

closest nonpassing combination: `U0_UNCHANGED/T2_EQUAL` at `0.2176683664321899` rad

All 48 preregistered CPU cells were full-duration walks with bilateral support, zero saturation, and zero measured rate excess. No cumulative actor-average checkpoint clears the 0.20 rad tracking gate, so actor SWA is closed without selecting the closest endpoint.

This result authorizes no training, x=0 gate, Colab, RDK-X5, or robot access.
