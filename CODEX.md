# Codex Notes

Use `AGENTS.md` as the authoritative instruction file for coding agents working in this repository.

Current project mission:

```text
Build a safe, repeatable sim-to-real diagnostic bridge for Open Duck Mini RDK-X5 before tuning or retraining.
```

Current next step:

```text
Hold the rate175 temporally bounded behavior-teacher branch. Its registered
2026-07-11 causal smoke emitted checkpoints at 40,960, 81,920, and 122,880,
but all failed the compact corrected-bridge x=0.08 acceptance gate. Do not run
the extended seed suite, train this branch further, deploy it, or perform
robot-side validation. The saved-trace diagnosis found that the bounded teacher
was causally too weak: at matched step 81,920 its policy differed from the
original by only 0.0028 mean / 0.0079 p95 normalized action on identical
observations, while forward progress slightly regressed. The next offline task
is to define and screen a teacher/objective that materially changes the measured
x=0.08 failure states while preserving x=0 and the actuator envelope. Do not
assume another scalar behavior-prior or support-reward adjustment is adequate;
past matched evidence rejected both. A matched CPU causal screen also rejected
the global high-minus-low phase correction: it improved seeds 1/3 but sharply
regressed seed 6 and every high-progress seed. The next offline task is to
separate the observed failure modes and determine whether a state-conditioned
correction has measured support; do not tune the global phase-delta scale. Any
new training hypothesis must be separately pre-registered and authorized.

The expanded reset evidence now takes priority: seeds 8-39 produced 7/32 falls
within one second and only 3/32 passes. Frozen teacher disagreement replicated
as an early failure-ranking diagnostic on held-out seeds (0.20-second p95 AUC
1.0), but with only two held-out falls it is not threshold-calibrated and must
not drive runtime behavior. The next reviewed task should compare safe reset /
settling contracts against these exact failure seeds while preserving forward
motion; do not resume teacher-action tuning. A matched settle-10 screen on all
seven observed fall seeds made every failure occur sooner, so passive settling
is rejected. The evidence now supports a start-paused/reset-health decision
problem or a separately sourced active-recovery target; neither threshold nor
recovery action is currently calibrated or authorized. An offline bidirectional
threshold-transfer audit confirmed why: the discovery-derived p95 cutoff
transferred perfectly to the held-out block, while the held-out-derived cutoff
found only 1/5 discovery failures. This asymmetric small-sample result rejects
a universal runtime cutoff from the current 32 traces. The next defensible
evidence task is independent failure-positive collection or a pre-registered
multivariate reset-health study; do not implement a robot or simulator gate.
The preregistered multivariate study subsequently failed: reset risk alone was
weaker, and its equal-weight combination reduced heldout-to-discovery AUC from
0.909 to 0.818. That exact route is closed without post-hoc tuning. New,
independent failure positives for the unchanged disagreement metric are now the
only supported detector-calibration step; active recovery still lacks a safe,
outcome-aligned target.

The independent seeds 40-71 block is now complete. It produced 11/32 falls and
only 4/32 passes; combined seeds 8-71 produced 18/64 falls and 7/64 passes.
Disagreement ranking replicated at AUC 0.823, but the frozen cutoff missed 2/11
falls and falsely flagged 5/21 completed runs. Threshold-only calibration is
therefore closed: retain disagreement for offline diagnosis only. The next
substantive question is what safe, outcome-aligned recovery target exists in
the recurrent fall traces, or what preregistered objective change can learn
one. Do not implement a gate, use the teacher action as recovery, or tune reset
features post hoc.

Saved-trajectory evidence has now narrowed the recovery question. Across all
three independent blocks, early absolute pitch growth and aggregate actuator
tracking error predict later falls. The tracking signal localizes only to the
right knee (block A/B/C AUC 0.727/0.929/0.753), with materially larger failure
error. Treat right-knee tracking as the next mechanistic variable, not an
authorized correction. First determine from saved traces whether excessive
target demand or rate saturation explains the mismatch; only then define a
single preregistered matched CPU causal screen. Do not guess a gain or limiter.

The mechanism audit now rejects demand/rate saturation and supports reset-
origin mismatch: tick-0 right-knee absolute error replicates across blocks,
whereas later error growth does not. The next registered CPU causal screen may
change only the bridge's initial actuator-12 applied target to the measured
reset knee position, default off, on seeds 40-71 against their saved controls.
Use the frozen five-part pass rule. Do not alter the 2 rad/s limiter, gains,
other joints, reset distribution, policy, or robot runtime.

That causal screen failed at the frozen early-stop boundary: 6 falls by seed
50, including a new fall on a baseline-complete seed, versus only one recovered
fall. Tracking error often decreased without outcome recovery. Close bridge
reset alignment and all post-hoc variants. The collected evidence has now
rejected teacher correction, global phase correction, passive settling,
threshold gating, reset-neighborhood routing, rate-limiter changes, and local
right-knee alignment. The next defensible route is a separately preregistered
training objective that optimizes canonical randomized-reset survival and
forward outcome directly; do not use these diagnostic correlates as pseudo-
labels or recovery actions.

The one-factor no-behavior-prior Colab test is complete and rejected. All
checkpoints passed x=0, but none passed x=0.08; the best step reached only
0.02227 m/s with tracking p95 0.21644 rad. Do not run its 32-seed expansion or
tune KL/timesteps on that branch. Training reward increased while gate outcome
did not, confirming objective mismatch. The next separable hypothesis is the
existing default-off positive-command progress-failure termination, configured
to the measured compact threshold and warmup, from the original prior-enabled
baseline recipe—not another teacher or diagnostic-correlate loss.

The one-factor command-progress failure test is also complete and rejected.
Step 81,920 preserved x=0 but reached only 0.0104 m/s (ratio 0.1295) at x=0.08.
Step 163,840 reached 0.0230 m/s (ratio 0.2870) but failed tracking at both x=0
and x=0.08. Step 245,760 failed x=0 tracking and reached only 0.0155 m/s at
x=0.08. No checkpoint passed both compact gates, so do not run seeds 40-71 or
tune the termination threshold/warmup. The direct termination did not solve
the reset-robustness objective mismatch. Preserve this negative result and
require a new, separately preregistered hypothesis before further training.

The next hypothesis is now evidence-backed and preregistered. Across the two
direct-outcome experiments, 8/12 evaluations passed the training bridge-error
surrogate while failing the actual-joint compact gate; the gate p95 was about
2.04-2.25 times the surrogate. The new default-off reward directly measures
six-pitch-joint sent-target versus actual-position error. CPU contract checks
passed with both GPUs hidden. Its fixed scale -0.007914891239136222 was derived
from frozen x=0/x=0.08 traces to match the existing bridge penalty magnitude.
Run only the registered one-factor compact-gated experiment; do not tune its
scale, delta, joints, aggregation, KL, or training length after outcomes.

That direct joint-target experiment is now complete and rejected. All three
checkpoints passed x=0. Step 81,920 failed x=0.08 progress; steps 163,840 and
245,760 met progress but failed tracking at 0.21784 and 0.21703 rad. Do not run
the 32-seed expansion or increase the cost after seeing this result. The exact
mean pitch-chain tracking surrogate at the calibrated equal-contribution scale
is closed. Preserve the default-off implementation for auditability, but do
not promote it into a canonical recipe.

The compact-gate feasibility audit is also complete. The rate-bounded teacher
passed only 1/8 discovery and 1/16 independent one-second playground resets;
the independent block had 5/16 falls, exactly the same seeds as the Stage A
baseline. It is not a stable oracle and does not justify changing the gate.
Suspend further scalar training on broad randomized starts. Re-anchor normal
walking work to the explicit `home-support` contract and treat unsupported
`playground` reset recovery as a separate research objective.

Normal-start work is now re-anchored to the preserved corrected live-oracle
iter1 rate165 candidate. Its hashes match, the authoritative `home-support`
gates remain 8/8 pass at both commands, and current-tool seed-0 regressions
reproduce the old metrics exactly (x=0.08 ratio 0.3400, tracking 0.1827; x=0
tracking 0.0317; zero velocity excess). This is the current offline grounded-
start candidate. It is not unsupported-reset recovery and is not robot approval.

An operator approval packet now defines the remaining hardware path. Do not
skip to candidate replay: first capture a read-only snapshot and freshly verify
the supported physical home pose. The historical left-knee offset of -1.4880
rad was corrected to 0.0371 rad on June 27 and must not be called current.
Paused policy
staging, suspended x=0, suspended x=0.08, and grounded replay each require a
separate explicit approval. No SSH, copy, configuration write, or motion is
authorized by the offline package.
```

Robotics operating model:

```text
Use docs/ROBOTICIST_PLAYBOOK.md. Keep search and agent iteration out of the live robot loop, preserve frozen inspectable deployment code, and accept changes only through evidence gates.
```

Documentation rule:

```text
Keep README.md, PROJECT_GOAL.md, ROADMAP.md, evidence docs, and runbooks current with the latest robot state. Do not let important state live only in chat.
```
