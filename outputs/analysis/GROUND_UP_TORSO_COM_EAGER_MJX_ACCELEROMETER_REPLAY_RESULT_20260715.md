# Ground-Up Torso-COM Eager-MJX Accelerometer-Replay Result

status: `PASS_EAGER_MJX_ACCELEROMETER_MAP_COMPLETE`
decision: `SUPPORT_PREREGISTERED_MATCHED_SENSOR_ACTOR_RESPONSE_STUDY`

| tick | fixed compatible | weak | nonlinear center | rotated | tick class |
|---:|---:|---:|---:|---:|---|
| 0 | 36 | 0 | 0 | 0 | `FIXED_COMPATIBLE_TICK` |
| 24 | 3 | 23 | 10 | 0 | `NON_FIXED_TICK` |
| 32 | 2 | 13 | 18 | 3 | `NON_FIXED_TICK` |
| 40 | 7 | 19 | 10 | 0 | `NON_FIXED_TICK` |

Validity:

- baseline row mismatches after stripping map fields: 0;
- nominal actor observation maximum error: 0 m/s^2;
- tick-zero direction maximum error: 0 m/s^2;
- all values finite: true.

No p-value or training reward is used. The frozen result authorizes at most its named next preregistration.

## Evidence interpretation

Tick zero is uniformly fixed-direction compatible (36/36) with exact anchor
reproduction. The mid-gait signature is not persistent: tick 24 has 23 weak
and 10 nonlinear-center cells; tick 32 has 13 weak, 18 nonlinear-center, and 3
rotated cells; tick 40 has 19 weak and 10 nonlinear-center cells. The frozen
third rule fires at tick 32, selecting
`SUPPORT_PREREGISTERED_MATCHED_SENSOR_ACTOR_RESPONSE_STUDY`.

That named study already exists in the artifact chain. Its six actors are all
materially accelerometer-responsive, but the signed study is mixed and the
crossed target-state x donor-response localization is distributed or
unresolved. This valid map therefore confirms the evidence ordering; it does
not promote a policy family or authorize rerunning those completed studies.
