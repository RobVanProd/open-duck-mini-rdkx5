# Winner-v83 count-675 negative-gradient step preregistration

- Source / target count: `674 / 675`
- Direction: instantaneous negative pitch-teacher gradient, norm-matched to V82 Adam delta
- Frozen fractions: `1` through `1/4096`; first strict descent only
- Mutable parameters: six pitch action-weight columns and bias elements
- Optimizer `m/v`: bit-exact preserved; count alone advances
- Snapshot / non-selected ONNX: `1 / 1`
- Continuation / support / selection / robot authorized now: `0 / 0 / 0 / 0`
