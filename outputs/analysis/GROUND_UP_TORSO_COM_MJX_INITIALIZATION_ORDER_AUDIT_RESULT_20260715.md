# Ground-Up Torso-COM MJX Initialization-Order Audit Result

status: `INVALID_MJX_INITIALIZATION_ORDER_AUDIT`

decision: `INVALID_MJX_INITIALIZATION_ORDER_AUDIT`

This is one deterministic tick-zero reset state (effective n=1); it is a methods audit, not a statistical result.

| variant | endpoint class | NEG max error | POS max error | half-direction error |
|---|---:|---:|---:|---:|
| `FRESH_INIT_REFERENCE` | `MATCH_ENDPOINT_ORACLE` | 0 | 0 | 0 |
| `LIVE_FORWARD_REPRODUCTION` | `MATCH_ENDPOINT_ORACLE` | 0 | 0 | 0 |
| `LIVE_ZERO_WARMSTART` | `MATCH_ENDPOINT_ORACLE` | 0 | 0 | 0 |
| `LIVE_FRESH_IMPL` | `MATCH_ENDPOINT_ORACLE` | 0 | 0 | 0 |
| `LIVE_ZERO_WARMSTART_FRESH_IMPL` | `MATCH_ENDPOINT_ORACLE` | 0 | 0 | 0 |
| `FRESH_PRIMARY_COPY` | `MATCH_ENDPOINT_ORACLE` | 0 | 0 | 0 |
| `FRESH_PRIMARY_COPY_ZERO_WARMSTART` | `MATCH_ENDPOINT_ORACLE` | 0 | 0 | 0 |

Fresh nominal maximum error: `0` m/s^2. Prior-invalid reproduction error: `0.0133886337` m/s^2.

The decision selects only the named initialization mechanism for a separately preregistered correction. It does not authorize the 144-cell map, policy work, training, hardware, or deployment.

## Interpretation boundary

Fresh nominal and `FRESH_INIT_REFERENCE` reproduce the frozen oracle exactly,
but `LIVE_FORWARD_REPRODUCTION` also reproduces it exactly instead of
reproducing the prior invalid half-direction. Consequently all seven variant
outcomes are non-selective. The reconstruction removed the discrepancy before
the frozen resets could distinguish a cause.

The only supported localization is that the missing factor lies between the
standalone `live_nominal_data` construction frozen here and the evaluator's
actual tick-zero `mjx.Data` propagation. This result does not identify
`qacc_warmstart`, `_impl`, or fresh-derived-data reconstruction as sufficient.
