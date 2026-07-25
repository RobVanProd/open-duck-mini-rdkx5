# T1 accelerometer-bias dose-response v4 preregistration

- Status: `PREREGISTERED_T1_ACCEL_BIAS_DOSE_RESPONSE`
- Contract SHA-256: `cff8844075066091f5ac60ad9d270aa991fd2e7aaf0154c64295288dc3cdc388`
- Matrix SHA-256: `28fd9995bfec0682f0baeea507409a8abba9d85d83256039056a4bdd1d0b2fbe`
- Frozen cells: `440` (11 biases x 5 commands x 8 seeds)
- Primary decision: compare +1.6 m/s^2 against zero at x=0.08.
- No policy, normalizer, simulator model, actuator bridge, or gate is changed.
- V3 measured about 82 seconds per CPU cell. V4 freezes a disjoint three-way index-modulo shard and reuses the two hash-valid V3 cells; the scientific contract is unchanged.
- The zero-bias equivalence contract must pass before the matrix.
