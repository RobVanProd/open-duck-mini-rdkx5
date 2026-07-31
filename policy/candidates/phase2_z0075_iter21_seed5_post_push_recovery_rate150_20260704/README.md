# Phase 2 z0.0075 Iter21 Seed5 Post-Push Recovery Rate150

status: `HOLD_SEED5_RECOVERY_TRANSFERRED_BUT_OTHER_SEEDS_REGRESSED`

Candidate:

- `candidate.onnx`
- sha256: `e4ea65621cc641e00fafdf6b78d94fd730c22188e8b8ce3ed8f0a7f668d7592b`

This is an offline supervised student trained from the Iter21 near-miss
manifest plus one source-VX-oracle relabeled seed5 late post-push recovery
snippet. It did not involve robot tests, SSH, deployment, grounded replay, or
runtime behavior changes.

Focused seed0/seed5 screening passed and showed that the seed5 recovery signal
transferred. The full x=0.08 rough/intermediate-push gate remained a hold:

- pass: `5/8`
- falls: `3/8` (`seeds 2, 3, 6`)
- corrected-envelope p95/max velocity excess: `0.0000 / 0.0000`

Do not promote this candidate. Full decision:

- `outputs/analysis/PHASE2_Z0075_ITER21_SEED5_POST_PUSH_RECOVERY_RATE150_DECISION.md`
