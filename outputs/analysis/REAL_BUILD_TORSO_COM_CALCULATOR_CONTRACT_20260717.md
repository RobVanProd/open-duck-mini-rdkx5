# Real-Build Torso-COM Calculator Contract

Status: `PASS_CALCULATOR_CONTRACT_HOLD_MEASUREMENT_INPUTS`

The frozen 2026-07-16 weighted-COM and comparison method now has a deterministic
CPU implementation in `tools/evaluate_real_build_torso_com.py`.

Contract evidence:

- evaluator SHA-256:
  `6c43b34a4fb1ffb9f9d84619e1c5c53d7812ecda0050e76bf4d98505b90a213a`;
- test SHA-256:
  `46a0698e70cee90a478914d9ba3b2b1c3512c0c085dd7ebda63c7c10e337577d`;
- v2 null template SHA-256:
  `d9abf072ec2e9123f5214c8678860a7e043e83d4fd6a0400f49c98e2f6f21137`;
- frozen break-radius result SHA-256:
  `6b84b34e7280b0f0d92109a70444d18af7b0196cd3555530b8f42e70dea54e32`;
- incomplete-input contract JSON SHA-256:
  `ad00dc55dedef4c5b909663c8cf8a14a504d471891ae7e46438af47205211493`.

Five CPU unit cases pass: incomplete input fails closed without an estimate,
an exact simulator match passes, a positive outside case holds, the numeric
frame transform is mandatory, and mass/position uncertainty-box extrema enclose
the nominal value. The implementation enumerates every independent mass-bound
vertex, uses the monotone position endpoints, and applies the common datum
uncertainty once.

Running the untouched template produces
`HOLD_REAL_BUILD_COM_INPUTS_INCOMPLETE`, lists 46 missing fields, sets
`numerical_estimate_reported=false`, and emits no `estimate` object. This is the
expected current result, not a build COM measurement. No threshold, certified
bound, margin, simulator value, or authority boundary changed.

