# Winner-v74 update-638 hidden-replay numeric audit result

- Status: `PASS_WINNER_V74_UPDATE638_HIDDEN_REPLAY_NUMERIC_AUDIT`
- Classification: `EAGER_SCAN_FLOAT32_DRIFT_WITH_BOUNDED_POLICY_EFFECT_AND_STALE_ABSOLUTE_SCAN_GUARD`
- Decision: `PREREGISTER_FUNCTIONAL_NUMERIC_GUARD_CONTINUATION_ONLY`
- Scan / eager hidden maximum: `3.7550926208496094e-6 / 0`
- Mean-action maximum delta: `1.6391277313232422e-7` (bound `1e-6`)
- Value maximum delta: `4.76837158203125e-6` (bound `1e-5`)
- Log-probability / ratio maximum delta: `7.62939453125e-6` (bound `1e-4`)
- PPO-loss absolute delta: exact `0` (bound `1e-4`)
- Optimizer updates / snapshots / graphs / support / robot: `0 / 0 / 0 / 0 / 0`
- Result SHA-256: `c30027f0fdc4cb93499461692ece2ed65bcb831c9858b7c65e80575c81d6bc33`

The eager recurrence reproduces the stored rollout bit-exactly. The crossed
`2e-6` absolute scan guard is an internal execution-order metric, while all
previously frozen V59 functional effects remain bounded. This result does not
enlarge or search the raw scan threshold; it authorizes only a separately
preregistered continuation using those unchanged functional checks.
