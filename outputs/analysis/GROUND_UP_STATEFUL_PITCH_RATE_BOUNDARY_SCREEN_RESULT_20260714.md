# Ground-Up Stateful Pitch-Rate Boundary Screen Result

status: `PASS_STATEFUL_PITCH_RATE_BOUNDARY_NO_WINNER`
decision: `CLOSE_STATEFUL_PITCH_RATE_BOUNDARY_SCREEN`

| rate arm | tail arm | half worst p95 | final worst p95 | combination pass |
|---|---|---:|---:|---|
| `R1_GATE_GAP` | `T2_EQUAL` | 0.214928150 | 0.208866525 | `False` |
| `R1_GATE_GAP` | `T3_FOUR` | 0.219846791 | 0.200735447 | `False` |
| `R2_DOUBLE_GAP` | `T2_EQUAL` | 0.212139380 | 0.204302067 | `False` |
| `R2_DOUBLE_GAP` | `T3_FOUR` | 0.213173205 | 0.199306667 | `False` |
| `R3_FOUR_GAP` | `T2_EQUAL` | 0.207894796 | 0.210703784 | `False` |
| `R3_FOUR_GAP` | `T3_FOUR` | 0.212980503 | 0.198522979 | `False` |

closest nonpassing combination: `R3_FOUR_GAP/T2_EQUAL` at `0.2107037842273712` rad

All 72 preregistered CPU cells were valid 600-tick walks with bilateral support, zero action saturation, and zero measured pitch-chain rate excess. No rate/tail combination passed the 0.20 rad tracking gate at both its half and final checkpoints, so the screen is closed without promoting the closest result.

This result authorizes no training, x=0 preservation gate, RDK deployment, or robot motion.
