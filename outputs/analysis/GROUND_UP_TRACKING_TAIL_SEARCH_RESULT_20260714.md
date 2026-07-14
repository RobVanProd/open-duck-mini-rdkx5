# Ground-Up Tracking-Tail Search Result

status: `PASS_TRACKING_TAIL_SEARCH_NO_WINNER`
decision: `CLOSE_EXACT_TRACKING_TAIL_EXCEEDANCE_FORMULATION`

| arm | half worst p95 | final worst p95 | arm pass |
|---|---:|---:|---|
| `T1_QUARTER` | 0.228834200 | 0.232423872 | `False` |
| `T2_EQUAL` | 0.215051454 | 0.209724891 | `False` |
| `T3_FOUR` | 0.220476371 | 0.204100531 | `False` |

protected source 1M worst p95: `0.22317498326301574`
no-tail control 2M worst p95: `0.23112906813621517`
closest nonpassing arm: `T2_EQUAL` at `0.21505145430564881`
excess over .20 rad: `0.015051454305648804`

Every arm retained 12-second gait, bilateral support, zero saturation, and zero measured rate excess, but no arm passed tracking at both half and final checkpoints. The preregistered rule therefore closes this exact tail-exceedance formulation without selecting the closest checkpoint.
