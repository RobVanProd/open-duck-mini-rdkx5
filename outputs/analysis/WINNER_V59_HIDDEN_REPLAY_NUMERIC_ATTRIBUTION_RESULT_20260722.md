# Winner-v59 hidden-replay numeric attribution result

- Status: `PASS_WINNER_V59_HIDDEN_REPLAY_NUMERIC_ATTRIBUTION`
- Decision: `AUTHORIZE_REVISED_NUMERIC_GUARD_CONTINUATION_PREREGISTRATION_ONLY`
- Classification: `EAGER_SCAN_FLOAT32_NUMERIC_DRIFT_WITH_BOUNDED_POLICY_EFFECT`
- Source / rollout / would-complete: `476 / 476 / 477`
- Sole failed original predicate: `hidden_replay_at_most_1e_6`
- Eager replay hidden maximum: exact `0`
- Scan replay hidden maximum: `1.125037670135498e-6` (bound `2e-6`)
- Mean-action maximum delta: `1.4901161193847656e-7` (bound `1e-6`)
- Value maximum delta: `1.1920928955078125e-6` (bound `1e-5`)
- Log-probability / ratio maximum delta: `1.1444091796875e-5` (bound `1e-4`)
- PPO-loss absolute delta: exact `0` (bound `1e-4`)
- Optimizer updates / support cells / robot access: `0 / 0 / 0`
- Result SHA-256: `2bc025115d2c2d4eba2aca7e8d0670b2c9e6f90fc2d96507d38034cbc946c39b`

The stored rollout is reproduced bit-exactly by the same eager recurrent path.
Only the eager-versus-`jax.lax.scan` float32 execution order differs, and its
effect on every preregistered downstream policy quantity is bounded. This does
not revive or retry Winner-v58. It authorizes only a separately preregistered
continuation with the exact `2e-6` numeric replay guard and otherwise unchanged
objective, ABI, and evidence gates.
