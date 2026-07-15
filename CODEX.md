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

That CPU-only study is now frozen in
`GROUND_UP_TORSO_COM_FULL_OBSERVATION_REPLAY_SENSITIVITY_PREREGISTRATION_20260715.md`.
Its exact-source/device/graph/replay contract passes, and the reporting-only
replay now reproduces all 36 matrices/144 cells exactly with 40,520 full 115-D
rows. Before analysis outcomes, the oversized primal window solve was replaced
by its algebraically identical dual form when features exceed samples; fixed
scores agree within 2.14e-14 and the corrected tool is re-contracted. The next
step is the frozen descriptive instantaneous/local-window decode and
identical-state obs[3:6] actor forks. Do not run training, tuning, Colab,
GPU/iGPU, RDK-X5, runtime, or robot work.
```

Robotics operating model:

```text
Use docs/ROBOTICIST_PLAYBOOK.md. Keep search and agent iteration out of the live robot loop, preserve frozen inspectable deployment code, and accept changes only through evidence gates.
```

Documentation rule:

```text
Keep README.md, PROJECT_GOAL.md, ROADMAP.md, evidence docs, and runbooks current with the latest robot state. Do not let important state live only in chat.
```
