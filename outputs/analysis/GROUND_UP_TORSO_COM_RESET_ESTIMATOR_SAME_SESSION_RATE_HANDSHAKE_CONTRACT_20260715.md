# Ground-Up Torso-COM Reset-Estimator Same-Session Rate Handshake Contract — 2026-07-15

## Result

`PASS_RESET_COM_ESTIMATOR_SAME_SESSION_RATE_HANDSHAKE_CONTRACT`

All 20 frozen checks pass with zero Colab sessions, remote bytes, training
processes, or PPO steps. The dry run preserves the exact 19 assets, named T4,
2,400-second wall ceiling, 2.0-CU ceiling, 120-second stop reserve, cleanup,
recovery, and no-resume/no-retry rules.

The corrected order is exact: allocate, verify named idle T4/GPU, emit one
rate request and wait at most 120 seconds, validate the live operator values,
then and only then upload and train. The wait consumes the existing total wall
budget. Timeout or invalid evidence stops the session before upload/training.

Rate 1.07/hour with 79.36 available projects to .7133333333333334 units. Rate
3.0 passes exactly at 2.0; 3.000001 fails. Exact 120-second-old and 60-second-
future timestamps pass; values outside those bounds fail. Zero/nonfinite rate,
balance below 2.0, wrong session/source/schema, and timeout controls all fail.

Launcher SHA-256:
`afb5acc580239f729d4d0832dd29a0c7163e87b63856ff6b1111eb393683e241`.
Contract JSON SHA-256:
`ce32401e77e855e9731fc6aeb63e501d79a143f94d6e4624079d19d8966f15dc`.

## Authority

The operator explicitly approved one interactive corrected launch. After the
request marker, only the live Resources-UI rate and available-unit values are
required. Training begins automatically only if the frozen gate passes. No
behavior evaluation, local GPU/iGPU, RDK-X5, runtime, or robot action is
authorized.
