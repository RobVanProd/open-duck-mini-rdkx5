# T1 accelerometer-bias dose-response v2 preregistration

- Status: `PREREGISTERED_T1_ACCEL_BIAS_DOSE_RESPONSE`
- Contract SHA-256: `d8abf9a32d81d413fa3d8c2fa1f2d57c2a032d1525eef8d3cd627820e75994bd`
- Matrix SHA-256: `28fd9995bfec0682f0baeea507409a8abba9d85d83256039056a4bdd1d0b2fbe`
- Frozen cells: `440` (11 biases x 5 commands x 8 seeds)
- Primary decision: compare +1.6 m/s^2 against zero at x=0.08.
- No policy, normalizer, simulator model, actuator bridge, or gate is changed.
- V1 is superseded because its comparison serializer rejected a legitimate Infinity summary sentinel before producing any result; the scientific contract is unchanged.
- The zero-bias equivalence contract must pass before the matrix.
