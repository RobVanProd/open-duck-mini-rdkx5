# Winner-v19 feedback-magnitude hold attribution

- Status: `PASS_WINNER_V19_IMU_ANKLE_FEEDBACK_MAGNITUDE_HOLD_ATTRIBUTION`
- Decision: `CLOSE_POST_POLICY_ACTION_WRAPPERS_PREREGISTER_TRAINING_SIDE_CAUSAL_REPAIR`
- Full passes: `0 / 6` non-baseline interventions
- Optimizer / robot access: `0 / 0`

More correction does not solve the negative-support failures. The
constant arm worsens to `12/12` failures at `0.06 rad`; deployable
state feedback plateaus at `10/8` failures at both `0.06` and `0.09 rad`
despite larger action deviation.

Winner-v16 through Winner-v19 therefore close post-policy action
wrappers. The next admissible mechanism is a separately contracted
training-side recovery learned in the failed support contexts. This
attribution grants no training run and no robot authority.
