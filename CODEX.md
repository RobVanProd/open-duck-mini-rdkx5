# Codex Notes

Use `AGENTS.md` as the authoritative instruction file for coding agents working in this repository.

Current project mission:

```text
Build a robust reference-motion walking policy for Open Duck Mini through frozen, evidence-selected offline gates. Do not substitute training reward, visual preference, or robot improvisation for preregistered behavior evidence.
```

Current next step:

```text
The preregistered torso-COM remediation behavior evaluation is complete. All
144 requested CPU-only cells have exact policy/configuration identity and
per-run model readback. All six checkpoints pass the nominal R1 matrices, but
every TORSO_COM_X_NEG and TORSO_COM_X_POS checkpoint/fit matrix fails. Each arm
passes 4/12 matrices and 20/48 cells, so U_CURRICULUM, A05_DIRECT, and
U05_DIRECT all fail the frozen advancement rule.

Decision: CLOSE_EXACT_TARGETED_COM_FORMULATION_NO_WINNER. Do not promote a
closest arm. No retry, midpoint, LR, reward, seed, architecture, bridge,
command, reset, or horizon change is authorized from these outcomes. No R2
resumption, R3+, training, Colab, runtime design, RDK-X5, GPU/iGPU, or robot
work is authorized. Any next hypothesis requires a separate preregistration.
```

Robotics operating model:

```text
Use docs/ROBOTICIST_PLAYBOOK.md. Keep search and agent iteration out of the live robot loop, preserve frozen inspectable deployment code, and accept changes only through evidence gates.
```

Documentation rule:

```text
Keep README.md, PROJECT_GOAL.md, ROADMAP.md, evidence docs, and runbooks current with the latest robot state. Do not let important state live only in chat.
```
