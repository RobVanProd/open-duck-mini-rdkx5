# Winner-v85 integrated support-gate result

- Status: `HOLD_WINNER_V85_INTEGRATED_SUPPORT_GATE`
- Decision: `DO_NOT_SELECT_WINNER_V84_DEPLOYMENT_POLICY`
- Main cells / heldout repeats: `248 / 64`
- Half count `705`: `4` roll/pitch failures; predictor fails both plants
- Final count `755`: `8` roll/pitch failures; predictor fails both plants
- Repeatability / context separation / JAX-ONNX / action chain: all pass
- Selected checkpoint: `none`
- Robot clearance: `false`
- Result SHA-256: `ea25f93a79157e0dac380d3c2f6d7ddf596ae4cfd1c951245cb4cb4b2ddcc4e4`

Relative to Winner-v76, the half endpoint rescues six of ten prior locomotion
failures and creates none; the final endpoint rescues both COM_CORNER_07 plant
failures but adds one P30 COM_X_NEG failure, leaving eight. Every remaining
locomotion failure is exclusively the unchanged roll/pitch terminal. The
frozen predictor remains worse than the constant comparator on both plants at
both endpoints. The all-or-nothing rule therefore selects neither checkpoint
and grants no deployment or robot clearance. The next selected work is a
separately preregistered, read-only residual diagnostic on the 12 remaining
endpoint/plant failures.
