# T1 accelerometer-bias dose-response v3 preregistration

- Status: `PREREGISTERED_T1_ACCEL_BIAS_DOSE_RESPONSE`
- Contract SHA-256: `63c0df92cf4a22230a954dcd9413ac7d91ad6ac9b19f8b19e3ea8a6ec96e82ab`
- Matrix SHA-256: `28fd9995bfec0682f0baeea507409a8abba9d85d83256039056a4bdd1d0b2fbe`
- Frozen cells: `440` (11 biases x 5 commands x 8 seeds)
- Primary decision: compare +1.6 m/s^2 against zero at x=0.08.
- No policy, normalizer, simulator model, actuator bridge, or gate is changed.
- V2 is superseded because the matrix serializer rejected a legitimate Infinity lag sentinel before saving its first cell. V3 encodes diagnostic sentinels losslessly and enables a persistent JAX compilation cache; the scientific contract is unchanged.
- The zero-bias equivalence contract must pass before the matrix.
