# Phase 2 Transition-Preserving Terrain Branch

status: `HOLD_REWARD_PPO_ERODES_SUPPORT_TRANSITION`

## Objective

Recover rough-terrain / carpet robustness without deleting the support
transition that creates forward motion.

This branch is offline-only. It does not authorize robot tests, SSH, deploy,
grounded replay, runtime behavior changes, or training from scratch.

## Evidence

The live-oracle terrain DAgger student recovered forward progress on
`rough_terrain_backlash` at `z=0.002`, but held on corrected tracking/envelope:

```text
iter2 seed 2: vx 0.0526 m/s, track ratio 0.6570, tracking p95 0.2533
iter2 seed 4: vx 0.0459 m/s, track ratio 0.5736, tracking p95 0.2527
```

A simple tracking-aware label filter then clipped pitch-chain oracle labels to
`2.25 rad/s`. It lowered the supervised target rate and reduced closed-loop
tracking pressure, but collapsed the terrain gait:

```text
tracking-aware seed 2: vx 0.0107 m/s, track ratio 0.1335, double support 90%
tracking-aware seed 4: vx 0.0105 m/s, track ratio 0.1314, double support 96%
```

Trace comparison shows the mechanism:

```text
iter2 single support: about 30-35%
tracking-aware single support: about 4-10%
```

The global label cap mostly damped the double-support preparation into
single-support transition. It made the gait calmer by removing the step.

## Hypothesis

The next student needs the iter2 support-transition structure, but with
closed-loop correction of the excess pitch-chain tracking/rate. Offline label
clipping is too blunt because the labels that look aggressive are also the
transition labels that create single support.

## Required Method

Use one of these mechanisms, in order:

1. Closed-loop PPO fine-tune from `iter2_live_oracle_bc` with a strong restore
   prior and explicit corrected per-joint envelope/tracking penalties.
2. Transition-aware relabeling that preserves double-support preparation and
   single-support timing, only editing labels whose closed-loop rollout
   actually exceeds the corrected per-joint envelope.
3. Phase/contact-conditioned student that can represent different actions for
   double-support preparation, left support, and right support, with the hard
   swing gate active.

Do not run another simple global label-rate filter or scalar terrain reward
sweep as the next branch.

Method 1 has now been smoke-tested and held for this scalar reward-side recipe
family. The PPO restore/export plumbing works, but tiny updates erased the
support transition even under a tight trust region. The next branch should move
to method 2 unless method 1 is structurally changed to protect transition
actions directly.

## Warm-Start Artifact

The transition-preserving PPO warm-start now exists locally:

```text
decision: outputs/analysis/PHASE2_TERRAIN_PPO_SHAPE_WARMSTART_DECISION.md
checkpoint: outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_step0_checkpoint
step0 ONNX: outputs/analysis/phase2_terrain_live_oracle_dagger_iter2_ppo_shape_step0.onnx
fidelity: PASS_PPO_BC_WARMSTART_STEP0_EXPORT_FIDELITY
```

It is not a candidate policy. Its rough-terrain `z=0.002` gate preserves
forward transition behavior but still holds on corrected tracking/envelope:

```text
seed 2/4 track ratio: 0.6652 / 0.5947
seed 2/4 max tracking p95: 0.2598 / 0.2533
seed 2/4 max velocity excess: 0.7987 / 0.8291
```

This is the restore point for branch method 1.

## PPO Smoke Result

Artifact:

```text
decision: outputs/analysis/PHASE2_TRANSITION_PRESERVING_PPO_SMOKE_DECISION.md
status: HOLD_REWARD_PPO_ERODES_SUPPORT_TRANSITION
```

Two tiny CPU PPO runs were tested from the restore checkpoint.

Normal trust-region smoke:

```text
timesteps: 80
learning_rate: 1e-5
restore_policy_kl_scale: 2.0
behavior_prior_scale: -0.02
seed 2/4 track ratio: 0.0516 / 0.1115
seed 2/4 single support: 3.2% / 0.8%
seed 2/4 double support: 96.8% / 99.2%
```

Lockdown trust-region smoke:

```text
timesteps: 80
learning_rate: 1e-6
restore_policy_kl_scale: 100.0
behavior_prior_scale: -0.10
seed 2/4 track ratio: 0.0548 / 0.1181
seed 2/4 single support: 3.2% / 2.0%
seed 2/4 double support: 96.8% / 98.0%
```

Both runs completed and exported ONNX models, but both collapsed to low-progress
double support. The apparent tracking improvement came from stopping the step,
not from learning a terrain-safe in-envelope gait. Do not launch longer runs of
this same scalar reward-PPO recipe.

## Transition-Protected Relabeling Result

Artifact:

```text
decision: outputs/analysis/PHASE2_TRANSITION_PROTECTED_RATE_LIMIT_DECISION.md
status: PARTIAL_PASS_TRACKING_PLATEAU_BROKEN_HOLD_SEED4_SWING
```

The next method protected all non-double-support samples and a 6-tick window
around foot-contact transitions, then rate-limited only sustained
double-support pitch-chain labels:

```text
protected samples: 488 / 500
changed ticks: 13
changed contact counts: {'11': 13}
```

The resulting diagnostic student moved the rough-terrain blocker forward:

```text
seed 2: PASS_CANDIDATE_SIM_GATE
  track ratio: 0.3641
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1876 rad
  single support: 22.8%

seed 4: HOLD_CANDIDATE_TERRAIN_SWING
  track ratio: 0.3184
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1914 rad
  single support: 10.8%
```

This breaks the prior tracking/envelope plateau on both seeds, but it is not a
deployable pass because seed 4 still fails swing/advance. The next branch should
keep transition-protected rate limiting and add seed-4 swing/advance weighting
or contact-phase-balanced labels.

Simple seed-4 sample weighting was tested next and held:

```text
decision: outputs/analysis/PHASE2_TRANSITION_PROTECTED_SEED4_WEIGHTED_DECISION.md
status: HOLD_SEED_WEIGHTING_REINTRODUCES_TRACKING_EXCESS
seed 2/4 track ratio: 0.5112 / 0.4184
seed 2/4 max velocity excess: 0.2465 / 0.2935 rad/s
seed 2/4 max tracking p95: 0.2202 / 0.2222 rad
seed 2/4 min swing segments: 7 / 6
```

The weighting recovered swing/advance but reintroduced corrected-envelope and
tracking failures. Do not continue naive seed weighting. The remaining branch
needs contact-phase-balanced labels or an explicit action-space correction that
keeps the swing gain while rejecting pitch-chain labels that exceed the
corrected bridge gate.

A scalar supervised rate-penalty sweep on the same seed-weighted manifest also
held:

```text
decision: outputs/analysis/PHASE2_TRANSITION_PROTECTED_SEED4_WEIGHTED_RATE_SWEEP_DECISION.md
status: HOLD_RATE_REGULARIZATION_SWING_TRACKING_TRADEOFF

rate 0.08 seed 2/4:
  max velocity excess: 0.0822 / 0.1252 rad/s
  max tracking p95: 0.2024 / 0.2067 rad
  min swing segments: 7 / 0

rate 0.20 seed 2/4:
  max velocity excess: 0.0314 / 0.0943 rad/s
  max tracking p95: 0.2083 / 0.2113 rad
  min swing segments: 4 / 0
```

Higher rate pressure reduces excess but again erodes seed-4 swing. The simple
sample-weight plus scalar rate-penalty family is closed.

## Action-Space Correction / Command Conditioning

Artifact:

```text
decision: outputs/analysis/PHASE2_ACTION_SPACE_COMMAND_CONDITIONING_DECISION.md
status: PARTIAL_PASS_ACTION_SPACE_CORRECTION_HOLD_COMMAND_CONDITIONED_SWING
```

Per-joint action-space correction on the seed-weighted traces capped:

```text
right_knee: 2.25 rad/s
right_ankle: 2.00 rad/s
left_knee: 2.25 rad/s
```

The plain feed-forward student trained from those corrected x=0.08 labels
passed the rough `z=0.002` diagnostic gate on seeds 2 and 4:

```text
seed 2/4 track ratio: 0.4784 / 0.4738
seed 2/4 max velocity excess: 0.0000 / 0.0000 rad/s
seed 2/4 max tracking p95: 0.1989 / 0.1913 rad
seed 2/4 min swing segments: 6 / 6
```

That same feed-forward student failed command semantics at x=0.0:

```text
seed 2/4 mean vx at x=0.0: 0.0442 / 0.0369 m/s
```

Adding x=0 labels to a plain feed-forward BC student collapsed the x=0.08 gait,
even without extra x0 weighting. A phase/command-modulated student preserved
x=0 semantics:

```text
phasecmd x=0.0 seed 2/4 mean vx: -0.0008 / 0.0032 m/s
```

but still held on seed-4 swing at x=0.08:

```text
phasecmd x=0.08 seed 2: PASS_CANDIDATE_SIM_GATE
phasecmd x=0.08 seed 4: HOLD_CANDIDATE_TERRAIN_SWING
```

The next branch should be command/phase-conditioned or phase/contact-conditioned
and should recover seed-4 swing while preserving x=0.0 command semantics.

## Gate

Minimum rough-terrain diagnostic gate before any wider 8-seed run:

```text
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
bridge: corrected fitted bridge
command_x: 0.08
duration: 5 s
seeds: 2,4
falls: 0
track ratio: >= 0.50
max corrected velocity excess: 0
max tracking p95: <= 0.20 rad
min per-foot swing segments: >= 1
min per-foot rel-x range p95: >= 0.003 m
min per-foot swing peak lift: >= 0.005 m
double support: not above the live-oracle iter2 baseline by more than 10 percentage points
```

Promotion still requires the canonical corrected-bridge flat and rough gates,
including `x=0.0` command preservation, ONNX fidelity, and review. Robot
validation remains blocked.

## Falsifier

If a transition-preserving fine-tune keeps swing support structure but cannot
reduce tracking below `0.20 rad` or corrected-envelope excess to zero, the
terrain blocker is not label smoothing. Revisit the corrected bridge/terrain
contact model or accept that this gait needs a different support strategy.

## Phase/Command Seed-4 Weighting Follow-Up

Artifact:

```text
decision: outputs/analysis/PHASE2_PHASECMD_SEED4_WEIGHTING_DECISION.md
status: HOLD_SCALAR_SEED4_WEIGHTING_EXHAUSTED
```

The operator's hardware surface notes match the current rough-terrain sim
blocker:

```text
office-chair plastic mat: too slippery
medium carpet: stepping, but not enough foot lift/forward advance
```

The phase/command-modulated student preserves `x=0.0` command semantics, so a
focused seed-4 moving-label weighting sweep was run:

```text
seed4x25 x=0.08 seed 2: PASS
  vx: 0.0352 m/s
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1881 rad
  min swing segments: 4
  min rel-x range p95: 0.0048 m

seed4x25 x=0.08 seed 4: HOLD_CANDIDATE_TERRAIN_SWING
  vx: 0.0329 m/s
  max velocity excess: 0.0000 rad/s
  max tracking p95: 0.1887 rad
  min swing segments: 3
  min rel-x range p95: 0.0029 m

seed4x25 x=0.0 seed 2/4 vx: -0.0015 / 0.0026 m/s
```

The x2.5 variant is the best command-conditioned near miss so far, but still
misses the rough swing/advance threshold by a small margin. Increasing the same
scalar seed-4 weight to x4.0 did not fix it:

```text
seed4x40 x=0.08 seed 2: PASS
seed4x40 x=0.08 seed 4: HOLD_CANDIDATE_TERRAIN_SWING
  min swing segments: 0
  min rel-x range p95: 0.0000 m
```

Scalar seed-4 weighting is therefore closed. The next branch should target the
actual missing mechanism: seed-4 right-foot swing/advance during the moving
phase, while preserving zero-command behavior. Reasonable next mechanisms are a
right-foot swing-phase relabel, a contact/phase-conditioned head, or a
phase/contact-specific sample weighting rule. Do not repeat global seed
weighting or plain mixed-command feed-forward BC for this blocker.

## Targeted Right-Swing Weighting

Artifact:

```text
decision: outputs/analysis/PHASE2_RIGHT_SWING_TARGETED_WEIGHTING_DECISION.md
status: PASS_LOCAL_RIGHT_SWING_TARGETED_DIAGNOSTIC
tool: tools/weight_bc_trace_samples.py
```

The next test weighted only the seed-4 right-foot swing rows:

```text
contact code: 10
meaning: left stance, right swing
matched rows: 18 / 250
sample weight: 6.0
```

This recovered the missing local rough-terrain swing without breaking
zero-command behavior:

```text
x=0.08 rough z=0.002 seed 2: PASS
  vx: 0.0409 m/s
  track ratio: 0.5114
  velocity excess: 0.0000 rad/s
  tracking p95: 0.1922 rad
  min swing segments: 6
  rel-x p95: 0.0131 m

x=0.08 rough z=0.002 seed 4: PASS
  vx: 0.0341 m/s
  track ratio: 0.4269
  velocity excess: 0.0000 rad/s
  tracking p95: 0.1952 rad
  min swing segments: 2
  rel-x p95: 0.0064 m

x=0.0 rough z=0.002 seed 2/4 vx: -0.0013 / 0.0032 m/s
```

This is not a promoted candidate yet. It is a local diagnostic pass showing
that the carpet-like "steps but does not advance the foot enough" failure is
addressed by contact-phase-specific right-foot swing weighting, not by global
seed weighting. The next gate is the same rough `z=0.002` diagnostic across
seeds 0-7 at both x=0.08 and x=0.0.

## Live-Oracle Iteration 1

Artifact:

```text
decision: outputs/analysis/PHASE2_LIVE_ORACLE_RIGHT_SWING_ITER1_DECISION.md
status: HOLD_LIVE_ORACLE_ITER1_MIXED_IMPROVEMENT
```

The targeted right-swing candidate was then evaluated across the rough
`z=0.002` 8-seed x=0.08 diagnostic:

```text
passes: seeds 2,4,6
low-progress holds: seeds 0,1,5,7
target-velocity hold: seed 3
falls: 0/8
```

A live-oracle DAgger data iteration relabeled the student's own rough-terrain
states:

```text
x=0.08 relabel data: 8 entries / 2000 samples
x=0.0 relabel data: 2 entries / 500 samples
aggregate manifest: 13 entries / 3250 samples
```

The follow-up phase/command student improved the distribution but did not pass:

```text
passes: seeds 1,2,3,6,7
terrain-swing holds: seeds 0,4
fall/reverse hold: seed 5
```

This confirms the live-oracle mechanism is useful: it fixed seed 1, seed 3, and
seed 7. It also regressed seed 4 and created a seed-5 reverse/fall. The next
iteration must be selective rather than a flat aggregate:

```text
preserve the targeted seed-4 right-swing labels
inspect/filter seed-5 reverse/fall labels
retain live-oracle relabels for seeds 1,3,7
```

Do not promote the live-oracle iter1 candidate. Robot validation remains
blocked.

## Live-Oracle Iteration 1 Selective Aggregate

Artifact:

```text
decision: outputs/analysis/PHASE2_LIVE_ORACLE_RIGHT_SWING_ITER1_SELECTIVE_DECISION.md
status: HOLD_SELECTIVE_AGGREGATE_NOT_SUFFICIENT
```

A selective aggregate was tested to preserve the targeted seed-4 right-swing
labels and remove the most suspicious live-oracle sources:

```text
base: targeted right-swing command manifest
live x=0.08 relabels: exclude live seed 4 and live seed 5
live x=0.0 relabels: keep seeds 0 and 4
kept entries: 11
```

This did not pass:

```text
passes: seeds 1,2
terrain-swing hold: seed 0
target-velocity hold: seed 3
tracking holds: seeds 4,6,7
fall/reverse hold: seed 5
```

Conclusion: flat aggregate entry selection is not local enough. The next branch
must directly inspect/cap/filter the seed-5 reverse/fall action sequence and
preserve the targeted seed-4 right-swing rows with per-record/per-phase
weighting. Do not continue plain aggregate variants.

## Seed5-Capped Live-Oracle Relabel Test

Artifact:

```text
decision: outputs/analysis/PHASE2_LIVE_ORACLE_RIGHT_SWING_ITER1_SEED5_CAPPED_DECISION.md
status: HOLD_SEED5_CAPPED_NOT_SUFFICIENT
```

A more local curation was tested:

```text
base: targeted right-swing command manifest
live x=0.08 seed 4: dropped, preserving the original targeted seed-4 rows
live x=0.08 seed 5: retained, but right_ankle action deltas capped at 2.25 rad/s equivalent
live x=0.08 seed 5: reverse/fall-tail rows weight-clamped to 0.25
aggregate entries: 12
```

The x=0.08 rough z=0.002 fitted-bridge gate improved:

```text
passes: seeds 1,2,3,4,6,7
terrain-swing hold: seed 0
fall/reverse hold: seed 5
```

This is better than flat selective aggregation because seed 3 no longer trips
the target-velocity gate and seed 4 preserves the targeted right-swing fix.
However, the candidate is not promotable:

```text
x=0.08: seed 5 still falls/reverses
x=0.0: seed 5 also falls
```

Conclusion: the seed-5 right-ankle burst is a symptom, not the whole mechanism.
The next branch should collect full-observation traces for seed 5 at both
x=0.0 and x=0.08, compare against passing seeds 4 and 6, and emphasize early
seed-5 divergent states before the fall tail. Do not continue tail-only caps.

## Seed5 Neighbor Trace Divergence

Artifact:

```text
decision: outputs/analysis/PHASE2_SEED5_CAPPED_NEIGHBOR_TRACE_DIVERGENCE.md
status: PASS_TRACE_DIVERGENCE_CHARACTERIZED
```

Full-observation traces were collected for passing seeds 4 and 6 and failing
seed 5 at both x=0.08 and x=0.0.

At x=0.08, seed 5 diverges before the height collapse:

```text
tick 0: contact/support differs from both passing neighbors
tick 1: pitch-chain sent-target/action velocity exceeds 2.5 rad/s
tick 10: local vx becomes negative
tick 25: body pitch differs from neighbor mean by >0.20 rad
tick 51: base height finally drops below 0.13 m
```

At x=0.0, the same seed also fails:

```text
tick 0: vx is negative and contact/support differs from neighbors
tick 1: pitch-chain sent-target/action velocity exceeds 2.5 rad/s
tick 18: body pitch differs from neighbor mean by >0.20 rad
tick 37: base height drops below 0.13 m
```

Conclusion: seed 5 is a command-independent early-state stability mode. The
tail right-ankle burst is not the root cause. The next live-oracle correction
should emphasize seed-5 early states before pitch divergence and downweight or
exclude only the unrecoverable late fall tail.
