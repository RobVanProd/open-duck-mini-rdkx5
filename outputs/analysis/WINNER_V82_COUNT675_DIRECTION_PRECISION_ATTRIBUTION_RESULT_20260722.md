# Winner-v82 count-675 direction/precision attribution result

- Status: `PASS_WINNER_V82_COUNT675_DIRECTION_PRECISION_ATTRIBUTION`
- Classification: `ADAM_GEOMETRY_STALLED_NEGATIVE_GRADIENT_DESCENDS`
- Decision: `PREREGISTER_ONE_COUNT675_NEGATIVE_GRADIENT_STEP_PROOF`
- Source / attempted count: `674 / 675`
- Exact V81 stop reproduction: `pass`
- Existing + extended Adam fractions: no descent through `1/1,048,576`
- Norm-matched negative gradient: strict descent at `1/2` through `1/4096`
- Best diagnostic fraction: `1/2`, loss `0.0072185365 -> 0.0071995878`
- Float32 loss ULP: `4.6566129e-10`
- Committed updates / snapshots / graphs / support / robot: `0 / 0 / 0 / 0 / 0`
- Result SHA-256: `5d7a3b646fa191b8c46c90173e08ef77177e8a5d06455a39273b5dbf415ebc37`

The inherited Adam proposal remains a first-order descent direction, but none
of 21 representable fractions descends the actual float32 objective. This is
not a general loss plateau: the norm-matched instantaneous negative gradient
strictly descends over 12 consecutive fractions. The frozen classification
therefore selects exactly one separately preregistered negative-gradient step
proof. It does not authorize a continuation, support gate, checkpoint
selection, deployment, or robot access.
