# Codex Notes

Use `AGENTS.md` as the authoritative instruction file for coding agents working in this repository.

Current project mission:

```text
Build a robust reference-motion walking policy for Open Duck Mini through frozen, evidence-selected offline gates. Do not substitute training reward, visual preference, or robot improvisation for preregistered behavior evidence.
```

Current next step:

```text
The targeted-COM remediation is closed with no winner, and its causal audit
rejects zero axis exposure as a sufficient explanation: corrected full-range
training reproduces the pre-remediation X_NEG reversal magnitude, while X_POS
fails with the opposite signed runaway and nominal remains fully preserved.

The preregistered read-only decode then finds the decisive observation fact:
COM class is linearly decoded from the exact tick-zero gyro/accelerometer actor
input with 100% accuracy in every held-out arm, command, and fit fold
(family-wise p=1/1001). Gyro is zero; the tick-zero accelerometer is an exact,
distinct class signature repeated across all 48 traces per class. History is
not required by this evidence, so do not select recurrence or a memory arm.

The next defensible work is a separately preregistered objective/exploitation
study of why the policy fails to use this instantaneous signal. Do not train,
tune, replay the simulator, add an explicit COM input, narrow the certified
range, or change architecture before that preregistration. R2 resumption, R3+,
Colab, runtime design, RDK-X5, GPU/iGPU, and robot work remain unauthorized.
```

Robotics operating model:

```text
Use docs/ROBOTICIST_PLAYBOOK.md. Keep search and agent iteration out of the live robot loop, preserve frozen inspectable deployment code, and accept changes only through evidence gates.
```

Documentation rule:

```text
Keep README.md, PROJECT_GOAL.md, ROADMAP.md, evidence docs, and runbooks current with the latest robot state. Do not let important state live only in chat.
```
