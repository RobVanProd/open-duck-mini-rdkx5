# Codex Notes

Use `AGENTS.md` as the authoritative instruction file for coding agents working in this repository.

Current project mission:

```text
Build a robust reference-motion walking policy for Open Duck Mini through frozen, evidence-selected offline gates. Do not substitute training reward, visual preference, or robot improvisation for preregistered behavior evidence.
```

Current next step:

```text
The preregistered oracle COM viability-funnel study is complete through its
frozen Stage-B hard stop. Stage A localized all 24 failing moving endpoint
cells and committed 298 exact four-tick states; 49 formed the fixed P30,
x=.077, two-checkpoint/two-sign sequence-design subset. X_NEG meets the
backward-velocity rule at tick 0 in every cell; X_POS meets the runaway rule at
ticks 23-26, before the recorded fall.

The deterministic bounded screen finds valid sequences from only 5/49 states
at 8 ticks, 4/49 at 16 ticks, and 0/49 at 32 ticks. X_NEG loses all valid
sequences by tick 4 and X_POS by tick 12. No single frozen horizon works from
every state, so the online planner and 48-cell Stage-C matrix were not run.

Decision: HOLD_LOCAL_AUTHORITY_NOT_COMPOSABLE. The evidence preserves the
earlier local pulse-authority finding but rejects an auditable viability funnel
under this exact six-joint, +/-0.08 residual formulation. No closest sequence,
sign, checkpoint or horizon is promoted. Any gait-retraining or broader
controller branch requires a separate preregistration. Training, Colab, local
GPU/iGPU, RDK-X5, deployment, and robot use remain unauthorized; robot
clearance is NO.
```

Robotics operating model:

```text
Use docs/ROBOTICIST_PLAYBOOK.md. Keep search and agent iteration out of the live robot loop, preserve frozen inspectable deployment code, and accept changes only through evidence gates.
```

Documentation rule:

```text
Keep README.md, PROJECT_GOAL.md, ROADMAP.md, evidence docs, and runbooks current with the latest robot state. Do not let important state live only in chat.
```
