# Winner-v94 stable-response readout preregistration

- Frozen source/action/split: unchanged from Winner-v93
- Readout: `[h_out(64), bias] -> next response(50)`
- Direct action weights: exact zero
- Required rank: `65 / 65`
- Required `condition × eps(float32)`: `<= 1e-3`
- Required float64/float32 heldout delta: `<= 1e-4`
- Required heldout advantage: below frozen and constant per plant
- Optimizer updates / artifacts / robot access: `0 / 0 / 0`
