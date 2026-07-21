# Winner-v14 support-action diagnostic preregistration

- Status: `PREREGISTERED_WINNER_V14_SUPPORT_ACTION_DIAGNOSTIC`
- Decision: `AUTHORIZE_ONE_CPU_ONLY_FIVE_SCALE_SUPPORT_DIAGNOSTIC`
- Scales: `0 / .25 / .50 / .75 / 1.0`
- Main / repeat cells: `1,240 / 320`
- Training / locomotion / robot access: `0 / 0 / 0`

This is one finite causal screen, not post-hoc tuning. Each scale
runs the complete unchanged support/context gate at both persistent
checkpoints. The source action is scaled and rebound against the same
graph limits, with the realized final action returned as state.

Predictor scoring is corrected for the normalized Stage-1 head without
rewriting the frozen Winner-v13 HOLD. The largest complete-pass scale
advances only to a separate graph-transform contract. If no scale passes,
the entire inference-scale repair closes.
