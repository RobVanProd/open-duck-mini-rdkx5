# Winner-v66 failed-step attribution result

- Status: `PASS_WINNER_V66_FAILED_STEP_ATTRIBUTION`
- Classification: `INHERITED_ADAM_FULL_STEP_OVERSHOOT`
- Teacher loss before / full inherited-Adam proposal: `0.0033518366981 / 0.0033521873411`
- Full-step loss delta: `+3.5064295e-7`
- Teacher-gradient dot inherited-Adam delta: `-3.1431696e-7` (the direction is locally descending)
- Inherited-Adam fractions `1/16, 1/8, 1/4` descend; `1/2, 3/4, 1` do not.
- The frozen largest-first halving rule would therefore accept exactly `1/4`.
- Committed updates / snapshots / ONNX / support cells / robot access: `0 / 0 / 0 / 0 / 0`
- Result SHA-256: `dc25ee23ecfaa7910c39e3a3ff4c00b7f97f52a9a0b11d630e9d0dff3cfc25de`
- Decision: preregister one deterministic backtracked-Adam step proof only.
