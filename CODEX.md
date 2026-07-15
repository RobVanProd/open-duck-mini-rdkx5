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
scores agree within 2.14e-14 and the corrected tool is re-contracted.

The frozen analysis is complete. ACCEL3 and FULL115 both pass only at tick zero;
no current-state tick 24-40 or one fixed local-window width passes the
persistence rule, yielding a probe-limited reset-transient label. In contrast,
all six actors show substantial identical-state response when only obs[3:6] is
forked along the measured COM direction; mid-gait p95 maximum action differences
are .07206-.12575 normalized action and baseline replay error is exactly zero.

The exact CPU signed causal-response study is complete. Across 144 nominal
moving-state cells it finds 67 corrective, 55 amplifying, 22 intermediate, and
zero negligible responses. Every one of the six checkpoints is
`MIXED_POLICY_RESPONSE`; none meets the frozen systematic-sign rule. The frozen
decision is therefore `MIXED_SIGN_NO_POLICY_FAMILY_SELECTED`—no checkpoint,
arm, memory/estimator, objective-sign, or actuator-effect family advances.

The sign mixture localizes most strongly by fork time: corrective/amplifying
counts are 19/7 at tick 0, 21/9 at tick 24, 16/15 at tick 32, and 11/24 at tick
40. The physical COM pitch effect remains positive in every cell; the actor
effect changes sign, but the current diagonal study cannot separate a changing
actor response from changing plant-phase authority.

The exact 576-cell crossed target-state x donor-response study is complete and
valid. All 144 diagonal cells reproduce the prior pitch/alignment result with
zero error. Counts are 303 corrective, 207 amplifying, 66 intermediate, and
zero negligible. Every checkpoint is `DISTRIBUTED_OR_UNRESOLVED`.

Interaction is the largest descriptive fraction for all six checkpoints
(.453109-.572954), but no checkpoint reaches the frozen .60 and 2x dominance
rule. The grid shows real coupling: donor tick 40 is mostly corrective at target
ticks 0/24/32 but amplifying at target tick 40. The frozen decision remains
`CROSSED_LOCALIZATION_UNRESOLVED_NO_FAMILY_SELECTED`; do not promote the
closest fraction or choose actor-action, plant-phase, joint-phase, objective,
memory, estimator, policy, or training work. A new evidence question requires
a separate preregistration. Training, tuning, Colab, GPU/iGPU, RDK-X5, runtime,
and robot work remain unauthorized.

The matched accelerometer-map attempt is complete but invalid. The prior forks reused
the reset-derived accelerometer COM vector at all phases; they never proved
that vector equals the physical matched-state sensor difference mid-gait. The
native static method then fails both frozen validity checks: reconstructed
nominal sensor error reaches 7.427465 m/s^2 and tick-zero direction error
reaches .173359 m/s^2, against 1e-3 tolerances. Its apparent cell classes have
no authority and must not be interpreted.

The failure shows that reporting-only `qpos/qvel/ctrl` is insufficient to
reconstruct the MJX actor observation through native `mj_forward`. The next
valid evidence boundary requires a separate preregistration for exact CPU MJX
replay and state cloning, preserving observation-generation and solver state.
Do not relax tolerances, reuse invalid classes, run actor branches, or start
training, Colab, GPU/iGPU, RDK-X5, runtime, or robot work.

The exact correction is now preregistered: add default-off append-only map
fields to the existing CPU evaluator, replay the same 12 nominal matrices/36
moving runs exactly, and at ticks 0/24/32/40 call `mjx.forward` on COM +/-
models cloned from the live pre-policy MJX state. Every baseline trace must
remain field-for-field identical after stripping only new reporting fields.
The next boundary is the instrumentation/default-off regression contract; no
formal COM branch may be read before it passes.

That contract now passes. One complete 600-tick default-off CPU replay is
field-for-field and byte-for-byte identical to the prior exact trace, with zero
map fields; all new code is guarded and COM branches are `mjx.forward`-only.
Post-instrumentation evaluator and study hashes are locked. The next boundary
is the exact 12-matrix/36-run/144-cell formal replay. No outcome-dependent code
or threshold change is permitted.
```

Robotics operating model:

```text
Use docs/ROBOTICIST_PLAYBOOK.md. Keep search and agent iteration out of the live robot loop, preserve frozen inspectable deployment code, and accept changes only through evidence gates.
```

Documentation rule:

```text
Keep README.md, PROJECT_GOAL.md, ROADMAP.md, evidence docs, and runbooks current with the latest robot state. Do not let important state live only in chat.
```
