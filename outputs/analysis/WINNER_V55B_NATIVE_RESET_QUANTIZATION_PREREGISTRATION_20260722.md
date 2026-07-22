# Winner-v55b native reset-quantization preregistration

- Status: `PREREGISTERED_WINNER_V55B_NATIVE_RESET_QUANTIZATION_ATTRIBUTION`
- Decision: `AUTHORIZE_ONE_READ_ONLY_30_ROW_CPU_ATTRIBUTION_ONLY`
- Preregistration SHA-256:
  `3944cc29cb339663852723d85c12bf04237427f9081297515d5ef7e8066921d2`.
- Population: `15 configurations x 2 plants = 30 reset rows`
- Simulator steps / optimizer / robot: `0 / 0 / 0`

Winner-v55 found 15 distinct raw simulator reset inputs but did not apply the
support gate's already frozen native sensor quantization. This attribution
reconstructs the same 30 reset rows, requires every raw observation hash to
reproduce V55, then applies exactly
`native_quantize_observation`: BNO055 gyro/accelerometer resolution and the
declared servo position/velocity resolution. It adds no noise, delay, fitted
threshold, or physics step.

A deployable collision exists only when one exact quantized
`obs[115] + previous_action[14] + h_in[64]` hash maps to multiple exact bounded
V42 teacher labels. A collision selects only a separately preregistered
universal-first-action feasibility test; separability selects only a separate
first-tick teacher-mapping CPU contract. Neither outcome authorizes an update,
checkpoint selection, deployment, hardware access, or clearance.
