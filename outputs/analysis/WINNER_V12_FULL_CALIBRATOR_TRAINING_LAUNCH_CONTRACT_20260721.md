# Winner-v12 full-calibrator training launch contract

- Status: `PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_LAUNCH_FROZEN`
- Decision: `AUTHORIZE_EXACTLY_ONE_LOGICAL_TRAINING_RUN`
- Logical run: `winner-v12-full-calibrator-seed-120120`
- Work root: `/tmp/winner-v12-full-calibrator-training-work`
- Runner LF SHA-256: `37a52a038322a9b1dc781ccf67d4e73bd4e300d7aae9e462d10057881b58ce71`
- CPU-result SHA-256: `a3bf0075a713bc51d1fc608d276f3c90b244126e779870b8d761af8810448664`
- Claim LF SHA-256: `aeee93ab587f589e89827e57303c68a769e6fd346cdadff207cac948ea06bfd7`
- Source-manifest SHA-256: `cda1f130f5b9061d9a7c73cf2fc60d98ae2935c866c0c3cee9b5520b8f5b7259`
- Optimizer updates before launch: `0`
- Formal support/locomotion/robot execution: `0 / 0 / 0`

This freezes one CPU-only seed-120120 logical training run with 100
Stage-1 and 100 Stage-2 updates. Every update commits an immutable
hash-verified recovery snapshot. The complete work root is uploaded even
if the process fails. No retry or alternate work root is authorized.

A successful artifact still must pass the separate 124-cell support/context
gate before response-conditioned locomotion may be preregistered.
