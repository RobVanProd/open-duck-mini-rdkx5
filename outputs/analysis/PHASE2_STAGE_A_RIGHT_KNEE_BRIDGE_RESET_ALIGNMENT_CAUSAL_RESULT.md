# Right-Knee Bridge Reset-Alignment Causal Result

Status: **FAIL_CAUSAL_SCREEN_EARLY_STOP_ROUTE_CLOSED**

- evaluated: `11/32` seeds (early stopped)
- candidate falls: `[41, 42, 43, 44, 48, 50]`
- new falls: `[50]`
- recovered baseline falls: `[49]`

## Frozen criteria

- `falls_at_most_5`: `False`
- `no_new_falls`: `False`
- `passes_at_least_4`: `None`
- `mean_vx_not_regressed_more_than_0p01`: `None`
- `tracking_decreased_on_at_least_9_of_11_baseline_falls`: `None`

## Decision

Close exact right-knee bridge reset-alignment route without tuning.

The remaining criteria were not evaluated because two already-failed requirements cannot recover with additional seeds.
