# Winner-v58b guard-failure attribution result

- Status: `PASS_WINNER_V58B_GUARD_FAILURE_ATTRIBUTION`
- Decision: `DO_NOT_RETRY_WINNER_V58`
- Source / rollout / would-complete: `476 / 476 / 477`
- Sole failed original predicate: `hidden_replay_at_most_1e_6`
- Hidden replay maximum: `1.1250376701355e-6`
- First-tick allowed/observed nonzero gradient leaves: exact `4 / 4`
- First-tick forbidden gradients: exact zero
- Pre-update values: finite
- Optimizer updates / support cells / robot access: `0 / 0 / 0`

The failure is not the first-tick gradient-locality mechanism. The inherited
hidden replay threshold was crossed before the optimizer step. This closes a
blind Winner-v58 retry. A separate numeric-attribution contract is required
before considering any new continuation.
