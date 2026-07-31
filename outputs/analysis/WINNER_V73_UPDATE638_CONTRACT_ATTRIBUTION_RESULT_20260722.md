# Winner-v73 update-638 contract attribution result

- Status: `PASS_WINNER_V73_UPDATE638_CONTRACT_ATTRIBUTION`
- Classification: `SAMPLED_HIDDEN_REPLAY_TOLERANCE_CROSSED`
- Decision: `PREREGISTER_HIDDEN_REPLAY_TOLERANCE_CAUSAL_AUDIT_ONLY`
- Last durable / attempted count: `637 / 638`
- Sole failed invariant: sampled hidden replay `3.7550926208496094e-6 > 2e-6`
- Stored successor transitions: exact `18490 / 18490`
- Anchor selected elements: exact `384 / 384`
- Teacher rows / elements: exact `22 / 59626`
- Teacher, anchor, and reset gradient supports: exact
- Optimizer updates / snapshots / graphs / support / robot: `0 / 0 / 0 / 0 / 0`
- Result SHA-256: `7d3a0dd6a528e18d7a1f6503abdae1b13864e4a013ea7bd981605096565b1a18`

The count-638 stop is isolated to recurrent hidden replay's numeric tolerance.
No teacher-table, mask, transition, gradient-support, or objective-contract
change occurred. The result authorizes only a zero-update causal audit against
the previously reviewed eager-versus-`lax.scan` float32 mechanism; it does not
authorize relaxing the threshold or continuing training.
