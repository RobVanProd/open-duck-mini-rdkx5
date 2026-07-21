# Winner-v12 full-calibrator training launch contract

- Status: `PASS_WINNER_V12_FULL_CALIBRATOR_TRAINING_LAUNCH_FROZEN`
- Decision: `AUTHORIZE_EXACTLY_ONE_LOGICAL_TRAINING_RUN`
- Logical run: `winner-v12-full-calibrator-seed-120120`
- Work root: `/tmp/winner-v12-full-calibrator-training-work`
- Runner LF SHA-256: `8cd2c9267f356adba1127f8fb837138bbe6e39b5c3326300eeed9fdd5b524610`
- CPU-result SHA-256: `a0bb68bf88cefa1069fec732a89547029020fa017cd87b7f3c16e02a3adca9d7`
- Claim LF SHA-256: `514aefab71ab7fa1cca4ec60c437f15b06ea5855ac23c8c4dcfb707cbab6f183`
- Source-manifest SHA-256: `ce9a4d99e84e6a18ccf2b3658c62f8dfdffd3f43b09511d322d871d116bced88`
- Optimizer updates before launch: `0`
- Formal support/locomotion/robot execution: `0 / 0 / 0`

The prior launch is formally superseded because it stopped after its
first rollout but before loss construction, every optimizer update, and
every snapshot. The corrected zero-update contract then passed on Linux.

This freezes one corrected CPU-only seed-120120 logical training run with 100
Stage-1 and 100 Stage-2 updates. Every update commits an immutable
hash-verified recovery snapshot. The complete work root is uploaded even
if the process fails. No retry or alternate work root is authorized.

A successful artifact still must pass the separate 124-cell support/context
gate before response-conditioned locomotion may be preregistered.
