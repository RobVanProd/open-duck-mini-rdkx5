# T184 gait-period contract recovery

- Status: `INVALIDATE_T184_PERIOD_CONTRACT_BEFORE_T185`
- Error: `20` was the control period in milliseconds, not the reference gait
  period in ticks.
- Correct reference period: `27` ticks (`0.54 s` at `50 Hz`)
- Correct terminal window: `54` ticks
- New behavior / optimizer / hosted compute / robot: `0/0/0/0`
- T184's T185-authorization decision is withdrawn pending a corrected T184B
  saved-trace rerun.
