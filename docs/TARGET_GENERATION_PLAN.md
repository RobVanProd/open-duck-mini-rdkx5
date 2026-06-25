# Target Generation Plan

Date: 2026-06-25

## Purpose

Define the next offline path for creating low-command walking target data after
the V20 reference and realized-window audits.

This is not a robot-test plan and not a training launch plan.

Current target-source decision:

```text
docs/TARGET_SOURCE_DECISION.md
```

## Current Evidence

The following paths have been tested and are not sufficient:

```text
raw matched polynomial reference:
  fails rollout, high contact mismatch, exceeds action/rate envelope

cycle-projected reference:
  reduces action/rate stress, still terminates, contact mismatch stays ~68%

home-near projected phases:
  still terminate, contact mismatch stays ~67-68%

contact-gated projected reference:
  small mismatch improvement only, actual double support rises to 84.95%

contact-synchronized projected reference:
  contact mismatch drops to 4.36% aggregate
  forward velocity becomes negative/near-zero
  7/8 seeds terminate

existing trace archive:
  94 compatible mined windows
  1 curated seed-quality window

V5/V7 low-command replay:
  no realized target windows at x=0.04
```

## Conclusion

The blocker is no longer simply:

```text
reward weights
reference command mismatch
reference phase offset
contact-bit encoding
target-rate envelope
old moving-policy replay
```

The current blocker is:

```text
target generation that jointly preserves:
  positive forward velocity
  low lateral velocity
  safe body pitch and base height
  real contact transitions
  actuator/action envelope compliance
```

## Non-Goals

```text
do not run robot tests
do not deploy
do not change runtime behavior
do not launch another reward-only PPO variant
do not train BC from the current mined-window manifest
do not train directly against raw polynomial joint targets
do not treat contact matching alone as success
```

## Next Offline Experiment

Build a deliberate low-command target generator that searches or optimizes
short horizon target windows in sim, then grades the result with the existing
curation gate.

The generator should produce candidate windows, not a policy.

Minimum target window:

```text
command_x: 0.04
window length: 25-50 samples
mean vx >= 0.04 m/s
vy_abs_p95 <= 0.12 m/s
pitch_abs_p95 <= 0.35 rad
base_height_min >= 0.145 m
action_saturation <= 1.0%
sent_target_velocity_p95 <= 2.5 rad/s
joint_tracking_p95 <= 0.12 rad
post-window done margin >= 50 ticks if termination occurs
contact dominance <= 95%
```

## Candidate Generator Designs

Ranked options:

1. **Short-horizon target search around projected reference**
   - Start from the projected reference target cycle.
   - Search phase, amplitude, lateral scale, and cadence over short windows.
   - Score only realized sim motion.
   - Keep windows that pass the curation gate.

2. **Contact-transition constrained search**
   - Add explicit pressure for at least one safe contact transition.
   - Reject windows that remain in double support for the whole segment.
   - Keep forward velocity and lateral velocity in the score.

3. **Low-dimensional gait primitive search**
   - Parameterize hip/knee/ankle pitch waveforms directly.
   - Search cadence, phase offsets, amplitude, and stance timing.
   - Use the actuator envelope and curation gate as hard constraints.

4. **Reference adaptation with forward objective**
   - Use contact synchronization only as one term.
   - Add forward displacement and lateral stability requirements.
   - Do not optimize contact matching alone.

## Stop/Go Gates

Do not proceed to supervised pretraining until:

```text
curated_seed_windows >= 8
windows span at least 2 seeds or generator initializations
windows are not all from one contact pattern
no window is within 50 ticks of a later termination unless explicitly labeled review-only
```

Proceed to supervised seed only if:

```text
PASS_CURATED_DATASET_SEED_READY
```

Hold if:

```text
HOLD_INSUFFICIENT_CURATED_WINDOWS
HOLD_CONTACT_MATCH_ONLY_NO_FORWARD_MOTION
HOLD_FORWARD_WITH_HIGH_LATERAL_OR_PITCH
HOLD_ACTION_OR_TARGET_RATE_ENVELOPE
```

## Required Artifacts

For the next generator PR, produce:

```text
outputs/analysis/TARGET_GENERATOR_SEARCH.md
outputs/analysis/target_generator_search.json
outputs/analysis/TARGET_GENERATOR_WINDOW_MINE.md
outputs/analysis/target_generator_window_mine.json
outputs/analysis/TARGET_GENERATOR_WINDOW_CURATION.md
outputs/analysis/target_generator_window_curation.json
```

## Biased Primitive Search Result

The next bounded search added common hip/knee/ankle pitch biases and then a
small opposite hip-roll bias probe around the most promising family:

```text
command_x: 0.04
duration: 3 s
best common pitch/ankle pattern:
  hip_pitch_bias: +0.06 rad
  hip_pitch_amp: 0.05 rad
  knee_amp: 0.08 rad
  ankle_bias: +0.04 rad
  ankle_amp: -0.025 rad
hip_roll_bias probe: -0.04, 0.0, +0.04 rad
```

Result:

```text
biased search:
  curated seed windows: 5
  status: HOLD_INSUFFICIENT_CURATED_WINDOWS

biased multiseed search:
  seeds: 0,1,2,3
  curated seed windows: 5
  seed 2 produced review-only motion hints
  status: HOLD_INSUFFICIENT_CURATED_WINDOWS

roll-bias probe:
  seeds: 0,2
  curated seed windows: 12
  curated source/mode pairs: 12
  curated source files: 1
  status: HOLD_INSUFFICIENT_CURATED_DIVERSITY
```

Interpretation:

```text
Forward-biased pitch-chain primitives can now produce short curated low-command
target windows. Opposite hip-roll bias increases source/mode diversity, but all
curated windows are still from seed_000. Seed_002 remains review-only because
lateral velocity or contact dominance fails. Treat this as target-generator
proof of progress, not as a complete BC dataset launch.
```

Next step:

```text
convert the roll-bias probe into a deliberate target dataset builder, then add
either seed-diversity search or lateral/contact objective terms before any
supervised pretraining run.
```

## Seed-2 Rescue Search Result

A targeted rescue grid attempted to convert seed_002 review-only motion hints
into curated windows by sweeping stronger opposite hip-roll bias and finer phase
offsets around the best biased primitive family:

```text
seed: 2
periods: 0.7, 0.9 s
hip_roll_bias: -0.16, -0.12, -0.08, -0.04, 0.0 rad
phase_offsets: 0.0, 0.3927, 0.7854, 1.1781, 1.5708 rad
candidates: 50
```

Result:

```text
search status: PASS_TARGET_SEARCH_RAN
window mine: PASS_REALIZED_WINDOWS_AVAILABLE
curated windows: 0
review hints: 80
rejected windows: 11
status: HOLD_INSUFFICIENT_CURATED_WINDOWS
```

Interpretation:

```text
Hand-swept roll and phase offsets are not enough to make seed_002 pass the
curation gate. Early windows fail lateral velocity; later windows reduce lateral
velocity but become single-contact dominated. The next generator should score
lateral/contact criteria directly rather than continue expanding this manual
grid.
```

## Shuffled Broad Primitive Search Result

The primitive search was extended with deterministic candidate shuffling so a
large grid can be sampled without inheriting nested-loop ordering bias.

Run:

```text
seeds: 0,2
candidates sampled: 40
grid_seed: 20260625
periods: 0.55, 0.7, 0.85, 1.0 s
varied: hip roll bias, hip pitch bias/amplitude, knee bias/amplitude,
        ankle bias/scale, phase offset
```

Result:

```text
search status: PASS_TARGET_SEARCH_RAN
window mine: PASS_REALIZED_WINDOWS_AVAILABLE
curation status: PASS_CURATED_DATASET_SEED_READY
curated windows: 11
curated source files: 2
curated source/mode pairs: 11
seed distribution: seed_000=10, seed_002=1
```

Interpretation:

```text
This is the first compact target-generation pass that satisfies the stricter
curation gate with more than one seed file. The dataset is still skewed toward
seed_000, so it should be treated as a seed dataset candidate, not a final
walking corpus. The next step is to build a compact target-dataset manifest from
these curated windows and run a no-training sanity check before supervised
pretraining.
```

## Target Dataset Manifest

The curated windows were converted into a compact manifest without copying raw
trace contents:

```text
tool: tools/build_target_dataset_manifest.py
dataset_id: e84d27e27fd73419
status: PASS_TARGET_DATASET_MANIFEST_READY
entries: 11
source files: 2
source/mode pairs: 11
source distribution: seed_000=10, seed_002=1
mean vx: 0.0718 m/s
vx p95: 0.0994 m/s
sent target velocity p95: 0.6138 rad/s
tracking p95 max: 0.0709 rad
```

Interpretation:

```text
This manifest is acceptable as a small seed-material candidate for review, but
the 10:1 source skew is still real. The next step is a no-training dataset
sanity check and, if accepted, a tiny supervised/imitation smoke run before any
larger PPO or bridge curriculum work.
```

## Target Dataset Sanity Check

The compact manifest was checked against the local ignored source traces without
copying raw trace contents:

```text
tool: tools/check_target_dataset_manifest.py
dataset_id: e84d27e27fd73419
status: WARN_TARGET_DATASET_SANITY_SOURCE_SKEW
entries checked: 11
entries with errors: 0
bc readiness: HOLD_TARGET_DATASET_BC_OBSERVATIONS_MISSING
bc ready entries: 0
source files: 2
max source fraction: 0.9091
warning: source_distribution_skew
```

Interpretation:

```text
The manifest entries match the source traces and all compact metrics recompute
cleanly. The compact target evidence is valid, but the source traces do not
contain the 101-element policy observation vector needed for behavior cloning.
Before any supervised/imitation smoke run, rerun or extend the target generator
to record `obs[101]` alongside the action/target fields.
```

## Observation-Ready Target Dataset

The shuffled broad target search was rerun after extending the primitive
generator to write the policy observation vector:

```text
trace field added: observation[101]
dataset_id: 6c43c18e8f2b72ec
curation status: PASS_CURATED_DATASET_SEED_READY
manifest status: PASS_TARGET_DATASET_MANIFEST_READY
sanity status: WARN_TARGET_DATASET_SANITY_SOURCE_SKEW
bc readiness: PASS_TARGET_DATASET_BC_READY
entries: 11
source files: 2
source distribution: seed_000=10, seed_002=1
```

Interpretation:

```text
The dataset is now technically usable for a tiny supervised/imitation smoke
experiment because each curated window has obs[101] and action[14]. The source
skew remains the only warning, so the next experiment must stay tiny and must be
graded on whether it preserves low-command forward motion rather than reducing
loss alone.
```

Do not commit raw trace slices unless explicitly approved. Commit compact
manifests and summaries only.

## Target Dataset BC Smoke

The observation-ready manifest was tested with deliberately small behavior
cloning smokes:

```text
tool: tools/run_target_dataset_bc_smoke.py
dataset_id: 6c43c18e8f2b72ec
samples: 275
fit types: linear ridge and KNN, obs[101] -> action[14]
closed-loop replay: CPU, x=0.04, seeds 0 and 2, 3 s
status: HOLD_BC_REPLAY_LOW_FORWARD_MOTION
```

Result:

```text
supervised train error: near zero
sample/parameter ratio: 0.1926
linear seed_000 closed-loop vx: -0.0023 m/s
linear seed_002 closed-loop vx: +0.0014 m/s
linear rollout action_abs_mean: about 0.0001
KNN seed_000 closed-loop vx: +0.0139 m/s, ratio 0.3463
KNN seed_002 closed-loop vx: +0.0072 m/s, ratio 0.1798
```

Interpretation:

```text
The current target dataset is schema-ready but too small/skewed for a standalone
BC seed. Linear BC reconstructs the short snippets but freezes in rollout. KNN
produces weak forward motion, which suggests the dataset has motion hints but
not enough closed-loop coverage. Future target generation should increase
source diversity and temporal coverage, or move to a sequence-aware imitation
design that keeps the target motion alive during rollout.
```

## Longer Window Remine

The same observation-ready shuffled broad traces were remined for 50-sample
windows:

```text
tool: tools/mine_realized_target_windows.py
window_samples: 50
mine status: PASS_REALIZED_WINDOWS_AVAILABLE
curation status: HOLD_INSUFFICIENT_CURATED_WINDOWS
mined windows: 5
curated seed windows: 0
review motion hints: 5
```

All longer review hints came from `seed_002` and failed curation because of
high lateral velocity, single-contact dominance, or both:

```text
best review vx range: 0.0401-0.0595 m/s
pitch_abs_p95 range: 0.2157-0.3240 rad
base_height_min range: 0.1456-0.1468 m
contact patterns: mostly 90-100% double support
```

Interpretation:

```text
The current trace set has short motion snippets but no longer seed-quality
windows. The next generator change should explicitly optimize lateral velocity
and contact alternation over longer horizons before another BC/PPO attempt.
```

## Targeted Lateral/Contact Search Result

A follow-up primitive search reduced hip-roll bias and sampled around the
families that produced longer review hints:

```text
tool: tools/search_low_command_target_primitives.py
command_x: 0.04
duration: 4 s
seeds: 0,2
candidates: 48
```

Result:

```text
25-sample mine: PASS_REALIZED_WINDOWS_AVAILABLE
25-sample curation: HOLD_INSUFFICIENT_CURATED_DIVERSITY
25-sample curated windows: 25

50-sample mine: PASS_REALIZED_WINDOWS_AVAILABLE
50-sample curation: HOLD_INSUFFICIENT_CURATED_DIVERSITY
50-sample curated windows: 8
50-sample curated modes: 5
curated source files: 1
```

Interpretation:

```text
The target generator can now produce longer seed-quality windows by count, but
only on seed_000. Seed_002 mostly appears as review-only hints failing
high_lateral_velocity or single_contact_pattern_dominates. The next generator
iteration should preserve the seed_000 50-sample families while adding a
seed_002-specific lateral/contact correction.
```

## Seed 2 Balance Search Result

A second search used finer phase offsets and smaller hip-roll bias around the
seed_2 review-only families:

```text
tool: tools/search_low_command_target_primitives.py
command_x: 0.04
duration: 4 s
seeds: 0,2
candidates: 80
```

Result:

```text
25-sample curated windows: 45
50-sample curated windows: 23
status: HOLD_INSUFFICIENT_CURATED_DIVERSITY
curated source files: 1
curated source: seed_000
```

Interpretation:

```text
More random/finer grid sampling improves seed_000 counts but does not make
seed_002 pass. Seed_002 repeatedly appears as review-only forward motion that
fails high_lateral_velocity or single_contact_pattern_dominates. The next target
generator should become objective-driven: score candidates across seeds and
optimize for worst-seed lateral velocity/contact alternation, not just generate
more candidates.
```

## Seed Robustness Audit

The two latest 50-sample curation outputs were grouped by primitive mode and
source seed:

```text
tool: tools/analyze_target_seed_robustness.py
status: HOLD_SEED2_LATERAL_CONTACT
robust modes: 0
seed0-curated / seed2-review near misses: 12
```

Seed 2 failure counts:

```text
single_contact_pattern_dominates: 64
high_lateral_velocity: 40
```

Interpretation:

```text
The next target generator should optimize against the measured near-miss
metrics. Two concrete correction targets are:

1. reduce seed2 lateral p95 from about 0.16-0.18 m/s toward <=0.12 m/s
2. reduce seed2 contact dominance from 100% toward <=95%

Do not continue broad random grid expansion unless it is wrapped in a
worst-seed score that directly rewards those two improvements.
```

Detailed next-step spec:

```text
docs/TARGET_OBJECTIVE_GENERATOR_SPEC.md
```

## Target Objective Score

The new objective scorer ranked existing trace sets by worst-seed score:

```text
tool: tools/score_target_candidates_objective.py
window_samples: 50
latest seed2-balance trace set: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0
```

Best current near pass:

```text
mode: primitive_p0p6_hrb0_hb0p08_h0p03_kb0p06_k0p12_ab0p04_am0p009_ph0p3927
seed0: pass, vx=0.0565 m/s
seed2: vx=0.0515 m/s
seed2 vy95: 0.0507 m/s
seed2 contact_dominance: 98%
failure: single_contact_pattern_dominates
```

Interpretation:

```text
For the best candidate, seed2 forward velocity and lateral velocity already
pass. The immediate generator target is therefore to create one safe contact
transition in seed2 and bring contact dominance from 98% to <=95%, while
preserving the seed0 pass.
```

## Contact-Break Search Result

A focused search around the best objective-scored near pass attempted to reduce
seed2 contact dominance without changing the broader primitive family:

```text
tool: tools/search_low_command_target_primitives.py
command_x: 0.04
duration: 4 s
seeds: 0,2
candidates: 96
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0
```

Best current near pass from this search:

```text
mode: primitive_p0p66_hrb0p005_hb0p08_h0p035_kb0p06_k0p1_ab0p04_am0p014_ph0p3927
seed0: pass, vx=0.0531 m/s
seed2: vx=0.0453 m/s
seed2 vy95: 0.1028 m/s
seed2 contact_dominance: 98%
failure: single_contact_pattern_dominates
```

Curation result:

```text
25-sample curated windows: 82
50-sample curated windows: 70
50-sample curated modes: 38
status: HOLD_INSUFFICIENT_CURATED_DIVERSITY
curated source files: 1
curated source: seed_000
```

Interpretation:

```text
The search created many more seed0-quality windows, but did not solve the
seed2 contact-dominance blocker. The best seed2 candidate remains at 98%
contact dominance, and the broad seed2 failure distribution remains dominated
by single-contact-pattern failures. This suggests the current sine primitive
family is not creating enough seed-robust contact alternation. The next
generator should add an explicit contact-lift/contact-transition mechanism or a
different primitive parameterization, rather than another local micro-grid.
```

## Lift-Pulse Search Result

The generator now supports optional swing-lift pulse controls:

```text
--lift-duties
--lift-scales
```

When `--lift-scales=0.0`, the old sine primitive is unchanged. A bounded search
tested narrow lift pulses as a first explicit contact-lift mechanism:

```text
tool: tools/search_low_command_target_primitives.py
command_x: 0.04
duration: 4 s
seeds: 0,2
candidates: 96
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0
```

Best lift-pulse near pass:

```text
mode: primitive_p0p64_hrb0_hb0p08_h0p035_kb0p06_k0p14_ab0p04_am0p0035_ph0p47_ld0p3_ls0p35
seed0: pass, vx=0.0508 m/s
seed2: vx=0.0519 m/s
seed2 vy95: 0.0937 m/s
seed2 contact_dominance: 98%
seed2 contact pattern: 98% double contact, 2% single contact
failure: single_contact_pattern_dominates
```

Curation result:

```text
25-sample curated windows: 87
50-sample curated windows: 59
50-sample curated modes: 46
status: HOLD_INSUFFICIENT_CURATED_DIVERSITY
curated source files: 1
curated source: seed_000
```

Interpretation:

```text
The lift pulse improved target-rate smoothness and kept some seed2 near misses
inside the forward/lateral envelope, but every seed2 mode still failed contact
dominance. This is not training permission. The next generator needs to
explicitly change contact timing or foot clearance, not just narrow the lift
waveform.
```

## Foot-Clearance Probe Result

After adding `foot_site_z_m` to generator traces, a smaller probe tested
stronger lift pulses and scored contact transitions explicitly:

```text
tool: tools/search_low_command_target_primitives.py
command_x: 0.04
duration: 4 s
seeds: 0,2
candidates: 48
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0
min_contact_transitions: 3
```

Best probe near pass:

```text
mode: primitive_p0p52_hrb0_hb0p08_h0p035_kb0p06_k0p18_ab0p04_a0_ph0p47_ld0p3_ls0p65
seed0: pass, vx=0.0475 m/s
seed2: vx=0.0565 m/s
seed2 vy95: 0.1166 m/s
seed2 contact_dominance: 98%
seed2 contact_transitions: 2
seed2 foot_site_z_p95: 0.0159 m
failure: high_body_pitch, short_done_margin, single_contact_pattern_dominates, too_few_contact_transitions
```

Curation result:

```text
25-sample curated windows: 42
50-sample curated windows: 23
50-sample curated modes: 19
status: HOLD_INSUFFICIENT_CURATED_DIVERSITY
curated source files: 1
curated source: seed_000
```

Interpretation:

```text
The current joint-space primitive does not convert stronger knee/ankle lift
into reliable seed2 foot clearance or contact alternation. The best windows
still only show about 1-2 cm foot-site p95 height and two contact transitions in
50 samples. The next generator should use measured foot clearance/contact
timing as a primary objective, or switch to a different reference/IK-style
primitive.
```

## First Primitive Search Result

A bounded low-dimensional sine primitive search was run as the first generator
implementation:

```text
tool: tools/search_low_command_target_primitives.py
command_x: 0.04
duration: 3 s
seeds: 0
candidates: 12
```

Result:

```text
search status: PASS_TARGET_SEARCH_RAN
best mean vx: 0.0018 m/s
window mine: HOLD_NO_REALIZED_WINDOWS
curated seed windows: 0
```

Interpretation:

```text
Small anti-phase hip/knee/ankle pitch sine primitives are stable but behave like
standstill. They do not produce low-command target windows. The next primitive
search must add a stronger mechanism for forward displacement, such as stance
asymmetry, body pitch bias, foot clearance/placement terms, or an optimizer that
scores forward progress directly instead of only sweeping symmetric waveforms.
```

Artifacts:

```text
outputs/analysis/TARGET_GENERATOR_SEARCH.md
outputs/analysis/target_generator_search.json
outputs/analysis/TARGET_GENERATOR_WINDOW_MINE.md
outputs/analysis/target_generator_window_mine.json
outputs/analysis/TARGET_GENERATOR_WINDOW_CURATION.md
outputs/analysis/target_generator_window_curation.json
```

## Dynamic Hip-Roll Search Result

The primitive generator was extended with default-off dynamic hip-roll terms:

```text
--hip-roll-amps
--hip-roll-phase-offsets
```

A bounded CPU search used those terms with lift pulses and the seed-robust
objective:

```text
tool: tools/search_low_command_target_primitives.py
command_x: 0.04
duration: 4 s
seeds: 0,2
candidates: 72
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0
```

Best same-mode near pass:

```text
mode: primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p035_kb0p06_k0p14_ab0p04_a0p007_ph0p3927_ld0p3_ls0p65
seed0: vx=0.0413 m/s, vy95=0.1234 m/s, contact_dominance=92%, contact_transitions=3
seed2: vx=0.0417 m/s, vy95=0.1110 m/s, contact_dominance=94%, contact_transitions=4
remaining failure: seed0 high_lateral_velocity
```

Curation result:

```text
50-sample curation: PASS_CURATED_DATASET_SEED_READY
50-sample curated windows: 42
curated source files: 2
curated modes: 36
25-sample curated windows: 80
```

Interpretation:

```text
Dynamic hip-roll is the first primitive axis to create source-diverse
50-sample curated target windows. It also produced the closest same-mode
near-pass so far: seed2 fully passes and seed0 misses only the lateral gate by
about 0.0034 m/s. This is strong target-source evidence, but not training
permission under the current same-mode robust gate.
```

## Dynamic Hip-Roll Refinement

A narrower follow-up around the best near-pass tested finer roll amplitude,
roll phase, pitch, knee, ankle, lift-duty, and lift-scale values:

```text
candidates: 96
objective score: HOLD_NO_SEED_ROBUST_TARGETS
robust modes: 0
```

Best refined mode:

```text
mode: primitive_p0p52_hrb0_hra0p04_hrphm0p7854_hb0p08_h0p03_kb0p06_k0p16_ab0p04_a0p006_ph0p3927_ld0p26_ls0p75
seed0: vx=0.0365 m/s
seed2: vx=0.0403 m/s, vy95=0.1122 m/s, contact_dominance=94%, contact_transitions=4
remaining failure: seed0 low_forward_velocity
```

Curation result:

```text
50-sample curation: HOLD_INSUFFICIENT_CURATED_WINDOWS
50-sample curated windows: 3
25-sample curation: PASS_CURATED_DATASET_SEED_READY
25-sample curated windows: 207
```

Interpretation:

```text
The refinement improved some short-window behavior but lost the 50-sample
coverage that made the broader search useful. The next search should not
over-narrow around one mode. Keep the broad dynamic-roll family, but explicitly
score seed0 lateral reduction without sacrificing seed0 forward velocity or
seed2 contact transitions.
```

## Dynamic Hip-Roll Lateral-Fix Search Result

A follow-up CPU-only search stayed broad in the dynamic-roll family and targeted
the remaining seed0 lateral miss.

```text
tool: tools/search_low_command_target_primitives.py
command_x: 0.04
duration: 4 s
seeds: 0,2
candidates: 160
objective score: PASS_SEED_ROBUST_TARGETS
robust modes: 2
```

Best robust objective-scored mode:

```text
mode: primitive_p0p58_hrb0_hra0p048_hrphm1p05_hb0p08_h0p038_kb0p06_k0p14_ab0p04_a0_ph0p47_ld0p36_ls0p55
seed0: vx=0.0416 m/s, vy95=0.0716 m/s, contact_dominance=90%, contact_transitions=3
seed2: vx=0.0437 m/s, vy95=0.0736 m/s, contact_dominance=94%, contact_transitions=4
remaining failures: none
```

Curation and robustness:

```text
50-sample curation: PASS_CURATED_DATASET_SEED_READY
50-sample curated windows: 70
curated source files: 2
curated modes: 63
seed robustness audit: PASS_SEED_ROBUST_TARGETS
robust curated modes: 3
25-sample curated windows: 318
```

Interpretation:

```text
The dynamic-roll lateral-fix search is the first target-source pass under the
strict same-mode seed-robust gate. It authorizes the next offline step: a small
reviewed imitation/BC smoke against these target windows. It does not authorize
robot validation or skipping candidate replay gates.
```

## Sustained Target Branch Conclusion

The direct-label path has now been tested after the dynamic-roll lateral-fix
source pass:

```text
one-step BC:
  fails closed-loop replay

sequence replay:
  short forward fragments, but no stable loop

seam correction:
  worsens seed0 into lunge/fall

contact/state phase adapters:
  do not recover forward progress

100-150 sample sustained primitive search:
  no seed-robust longer gait
```

Conclusion:

```text
The current primitive target family is exhausted as a direct target-label
source. The short windows are evidence and soft-prior material, not BC/PPO
labels.
```

Next planning artifact:

```text
docs/SOFT_PRIOR_CLOSED_LOOP_LEARNER_PLAN.md
```

Do not run another BC/PPO launch from these target tables unless the soft-prior
smoke gate in that plan passes first.
