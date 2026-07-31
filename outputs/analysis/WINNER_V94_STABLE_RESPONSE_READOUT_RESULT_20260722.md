# Winner-v94 stable-response readout result

- Status: `HOLD_WINNER_V94_STABLE_RESPONSE_READOUT`
- Source support / design rank: `112 / 112` / `65 / 65`
- P30 fitted / frozen / constant MSE: `0.007087 / 0.930858 / 0.866829`
- P31/34 fitted / frozen / constant MSE: `0.006905 / 0.933975 / 0.869110`
- Condition number / float32 amplification: `194311.27 / 0.023164`
- Float64/float32 maximum heldout delta: `0.000707581`
- Maximum coefficient magnitude: `770.397`
- Result SHA-256: `63acd3836b0c37cc83b9aa8cfd1298d2593af2226bc6de042d2c93e9743ff233`

Removing the non-identifiable direct action columns produces a full-rank and
highly predictive hidden-state readout, but it misses both preregistered
float32-stability limits. The coefficients are therefore not selected.

The failure is numerical rather than representational. It authorizes only a
separately preregistered precision-derived rank truncation using the already
frozen condition bound. It does not authorize a policy artifact, training,
deployment, Gate 5, or robot access.
