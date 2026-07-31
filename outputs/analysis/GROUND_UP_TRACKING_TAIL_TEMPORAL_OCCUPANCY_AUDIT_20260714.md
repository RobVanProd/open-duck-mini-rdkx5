# Ground-Up Tracking-Tail Temporal Occupancy Audit

status: `PASS_TEMPORAL_OCCUPANCY_AUDIT`
decision: `SELECT_TEMPORAL_OCCUPANCY_QUANTITY_NO_SURROGATE`

| x | gate joint | p95 | exceed ticks | ticks over 30 | conditional RMS excess |
|---:|---|---:|---:|---:|---:|
| 0.074 | `left_knee` | 0.200147891 | 31 | 1 | 0.013409160 |
| 0.077 | `left_ankle` | 0.204100531 | 37 | 7 | 0.012052781 |
| 0.080 | `left_ankle` | 0.202661139 | 33 | 3 | 0.013456176 |

squared-cost/gate rank-discordant pairs: `17`
linear-cost/gate rank-discordant pairs: `21`

The strongest final checkpoint is no longer failing on large errors: its gate-setting joint exceeds 0.20 rad by only 1, 7, and 3 ticks beyond the 30-tick five-percent boundary, with conditional RMS excess below 0.014 rad. Squared hinge has vanishing pressure as those residuals approach the boundary and its ranking disagrees with the external p95 gate. Linear hinge is not selected: it has more rank-discordant pairs on the same frozen rows (21 vs 17), so constant gradient alone is insufficient evidence. Temporal occupancy is the supported causal quantity, but no trainable surrogate is uniquely supported and no training run is authorized.
