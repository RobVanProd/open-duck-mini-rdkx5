# Rate165 Hard-Vector Suspended x=0 Repeat Result

status: `HOLD_CONTROL_IMPACT_AND_VISUAL_ASYMMETRY`

The operator requested one identical x=0 repeat because the first run's motion
was difficult to see. No parameter changed.

- samples: `743`
- CRC/read/write/reset errors: `0/0/0/0`
- action saturation: `0%`
- tracking spikes above `0.05 rad`: `0`
- left hip/knee p95: `0.0086 / 0.0143 rad`
- right hip/knee p95: `0.0069 / 0.0060 rad`
- cleanup: torque-off marker, no runtime, no serial owner

The repeat has two isolated timing holds:

- tick 250: dt `0.06212 s`
- tick 540: dt `0.06087 s`
- terminal control-budget warnings: `2`

The events are separated from the largest tracking error, have no bus event,
and caused no >0.05 rad tracking spike. They are nevertheless above the
unchanged control-timing gate, so the repeat is `HOLD_CONTROL_IMPACT`.

The operator reported that the left leg moved noticeably more than the right.
Telemetry confirms this, especially at the knee: left/right actual range
`0.023/0.003 rad`, with policy target range `0.02766/0.00697 rad`. Left/right
ankle actual range is `0.027/0.018 rad`.

The same asymmetry predates this candidate: the ID13-last baseline x=0 trace
has knee target range `0.02769/0.00806 rad` and actual range `0.023/0.000 rad`.
The original Gate-3 trace is similar. The hard-vector limiter made zero target
changes at x=0, so the evidence rejects a new limiter regression or a new
right-knee fault. It identifies intrinsic rate165 zero-command policy dither.

Do not proceed to suspended x=.08. Resolve the zero-command contract digitally
and diagnose the repeat-only timing events before any further movement.
