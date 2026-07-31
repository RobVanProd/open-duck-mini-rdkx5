# Winner v2 Bridge-Observer Home-Key Correction

Status: `PRE_OUTCOME_SCHEMA_KEY_CORRECTION`

Before rerunning the formal replay, inspection showed the committed checker
addressed `contract.home_target_rad`; the frozen source stores the same field at
`guard_contract.home_target_rad`. No trace or outcome row was read by that
invocation. Change only this JSON key. All formulas, inputs and thresholds stay
frozen by the preceding correction.

