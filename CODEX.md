# Codex Notes

Use `AGENTS.md` as the authoritative instruction file for coding agents working in this repository.

Current project mission:

```text
Build a robust reference-motion walking policy for Open Duck Mini through frozen, evidence-selected offline gates. Do not substitute training reward, visual preference, or robot improvisation for preregistered behavior evidence.
```

Current next step:

```text
The RESET_EST_LATCH_U05 arm is closed by its frozen CPU behavior evaluation.
All 12 matrices and 48 cells are present with exact policy, fit, CPU, command,
seed, horizon, transform, and per-run body-2 model-readback contracts. Training
reward was not used for selection.

Both checkpoints pass all four nominal checkpoint/fit matrices. Neither
checkpoint passes either signed COM endpoint: X_NEG fails x=0 and moving cells
with backward reversal, while X_POS preserves all four x=0 cells but fails all
moving cells with forward runaway. The arm therefore passes 4/12 matrices and
20/48 cells. Worst endpoint tracking p95 remains 0.186236 rad, so the closure is
behavioral rather than a relaxed tracking decision.

Decision: CLOSE_RESET_EST_LATCH_U05_NO_PASS. No checkpoint is promoted, no
retry or midpoint is allowed, and no new training family is selected. Any new
evidence question requires a separate preregistration. Training, Colab, local
GPU/iGPU, RDK-X5, runtime work, and robot use remain unauthorized.
```

Robotics operating model:

```text
Use docs/ROBOTICIST_PLAYBOOK.md. Keep search and agent iteration out of the live robot loop, preserve frozen inspectable deployment code, and accept changes only through evidence gates.
```

Documentation rule:

```text
Keep README.md, PROJECT_GOAL.md, ROADMAP.md, evidence docs, and runbooks current with the latest robot state. Do not let important state live only in chat.
```
