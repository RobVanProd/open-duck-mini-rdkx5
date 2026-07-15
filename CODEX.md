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

The saved-trace decode preserves one deterministic measurement: under the
eval reset protocol, tick-zero gyro is zero and the accelerometer is one exact,
distinct vector for each COM class, repeated across all 48 traces per class.
This proves only that reset-time acceleration encodes COM inside actor input.

The original statistical and selection interpretation is superseded. Effective
tick-zero n is three class prototypes, not 144 independent samples, so the
1/1001 permutation value is not an inferential significance claim. The N>1
prefix table is non-monotone because the fixed ridge reallocates regularized
weight onto later command-dependent nuisance features even though tick zero is
preserved exactly; it cannot select or reject memory. No objective, optimizer,
memory, estimator, explicit-COM, or range-narrowing family is selected.

The next defensible step is a separate preregistration for CPU-only simulator
replay that records full 115-D observations at sliding mid-gait windows and a
contracted sensitivity audit of all six actors to obs[3:6] at reset and
mid-gait states. Do not run replay, sensitivity, training, tuning, Colab,
GPU/iGPU, RDK-X5, runtime, or robot work before that contract.
```

Robotics operating model:

```text
Use docs/ROBOTICIST_PLAYBOOK.md. Keep search and agent iteration out of the live robot loop, preserve frozen inspectable deployment code, and accept changes only through evidence gates.
```

Documentation rule:

```text
Keep README.md, PROJECT_GOAL.md, ROADMAP.md, evidence docs, and runbooks current with the latest robot state. Do not let important state live only in chat.
```
