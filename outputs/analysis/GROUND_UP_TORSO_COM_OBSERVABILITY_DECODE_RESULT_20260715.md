# Ground-Up Torso-COM Observability Decode Result

status: `PASS_TORSO_COM_OBSERVABILITY_DECODE_EVIDENCE`
decision: `PASS_INSTANTANEOUS_IMU_COM_DECODE`
earliest passing window: `1`
family-wise permutation p: `0.000999001`

| N ticks | min fold acc | arm F1 | command F1 | fit F1 | min recall | pass |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | `True` |
| 2 | 0.666667 | 0.944056 | 0.888112 | 0.958170 | 0.750000 | `False` |
| 4 | 0.791667 | 0.864490 | 0.944952 | 1.000000 | 0.833333 | `True` |
| 8 | 0.604167 | 0.804564 | 0.887660 | 1.000000 | 0.708333 | `False` |
| 16 | 0.333333 | 0.742313 | 0.817760 | 1.000000 | 0.708333 | `False` |
| 24 | 0.666667 | 0.855155 | 0.915344 | 1.000000 | 0.750000 | `False` |
| 32 | 0.750000 | 0.874510 | 1.000000 | 1.000000 | 0.750000 | `True` |
| 40 | 0.812500 | 0.923203 | 1.000000 | 1.000000 | 0.812500 | `True` |

Only exact `obs0_6` prefixes were used. No telemetry, outcome, reward, policy training, simulator replay, GPU, RDK-X5, or robot data entered the probe.

The exact instantaneous gyro/accelerometer input linearly decodes COM class. This supports a separately preregistered objective/exploitation study; it does not select memory.
