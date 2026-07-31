# Winner-v84 negative-gradient pitch-head continuation result

- Status: `PASS_WINNER_V84_NEGATIVE_GRADIENT_PITCH_HEAD_CONTINUATION`
- Decision: `AUTHORIZE_UNCHANGED_PERSISTENCE_GATE_FOR_COUNTS_705_AND_755_ONLY`
- Source / half / final counts: `675 / 705 / 755`
- Accepted updates / snapshots: `80 / 80`
- Fractions: `69 × 1`, `11 × 1/2`
- Optimizer `m/v`: bit-exact across the complete arm
- Half snapshot / ONNX: `a39e76e0...1849e05c / f2f6d6ac...0c644727`
- Final snapshot / ONNX: `45528bb2...d8c2de1e / de20542d...5b489173`
- Formal support / robot access: `0 / 0`
- Result SHA-256: `f720361087d4188b7d65a3da76e53bb93c1fd4774918dd4d4da7b10516764bae`

All 80 updates take the first strict same-batch descent on the frozen grid,
preserve the predictor and every non-pitch output parameter, preserve every
Adam `m/v` element, round-trip their snapshots, and export valid stateful
`115 + 14 + 64` ONNX graphs at the two original persistence boundaries. The
two checkpoints are evidence only. This result authorizes the unchanged full
`248 + 64` offline persistence gate and does not select a policy or authorize
deployment or robot access.
