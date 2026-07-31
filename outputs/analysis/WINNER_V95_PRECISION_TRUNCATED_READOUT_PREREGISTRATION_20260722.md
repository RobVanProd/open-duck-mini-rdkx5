# Winner-v95 precision-truncated readout preregistration

- Frozen source/action/split/features: unchanged from Winner-v94
- Rank selection: condition cap derived from `1e-3 / eps(float32)`
- Condition limit: `8388.608000000`
- Relative singular-value cutoff: `0.000119209289551`
- Required float64/float32 heldout delta: `<= 1e-4`
- Required heldout advantage: below frozen and constant per plant
- Optimizer updates / artifacts / robot access: `0 / 0 / 0`
