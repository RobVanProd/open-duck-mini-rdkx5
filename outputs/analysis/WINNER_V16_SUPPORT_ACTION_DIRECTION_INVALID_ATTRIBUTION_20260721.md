# Winner-v16 invalid direction-diagnostic attribution

- Status: `INVALID_WINNER_V16_SUPPORT_ACTION_DIRECTION_DIAGNOSTIC_ATTRIBUTED`
- Decision: `CORRECT_ONLY_BASELINE_DERIVED_FLOAT_COMPARATOR_AND_FRESHLY_PREREGISTER`
- GitHub run / attempt: `29845904251 / 1`
- Completed / interpreted cells: `168 / 0`
- Optimizer / robot access: `0 / 0`

All 24 baseline observation, action, prediction, and hidden-state hashes
reproduced exactly. Gate-setting results and all other compared fields
also reproduced exactly. Only finite derived JSON doubles in `terminal`
and `episode` differed, by at most `4.339e-13`.

The only permitted correction is a fresh preregistration retaining exact
trace and categorical comparisons while bounding those derived floats at
`1.0e-12` absolute. The invalid intervention
results remain uninterpreted.
