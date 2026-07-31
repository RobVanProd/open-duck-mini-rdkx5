# Winner-v4 Response Identifiability Result — 2026-07-20

status: `HOLD_RESPONSE73_PRETRAINING_FALSIFICATION_FAILED`

decision: `DO_NOT_IMPLEMENT_OR_TRAIN_RESPONSE73`

result JSON SHA-256: `b7eb0a5d8ccdfa4034fec85fdd98cd21e6888f7d4bd5b106c6e2052a07966730`

## Result

The response73 values are not the blocker in this run: both measured actuator-fit
pairs distinguish torso X = -0.05 m from +0.05 m after physical sensor quantization,
and all four endpoint/fit repeats are bit-exact. The differing field counts are
`60/73` for P30 and
`60/73` for P31/34.

The run still fails its preregistered support boundary. Double-foot contact was absent
for `17` settle ticks at -0.05 m and
`4` settle ticks at +0.05 m. The recorded 2,814-tick
excitation populations later had zero double-contact failures, but the contract required
the complete settle plus excitation population, so that later recovery cannot convert
this run into a pass.

## Decision

Do not implement or train response73 from this evidence. The exact support procedure
must be redesigned and reviewed prospectively; the completed run is not retried or
reclassified. No policy, runtime, robot, or hardware action is authorized.
