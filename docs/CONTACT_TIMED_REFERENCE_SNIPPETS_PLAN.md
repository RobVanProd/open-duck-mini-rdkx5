# Contact-Timed Reference Snippets Plan

This is the next offline target-source direction after the dynamic-roll,
optimizer, and CoM controller campaigns. It does not authorize training, robot
tests, SSH, deployment, grounded replay, or runtime changes.

## Current Decision

The target-source campaign is still held:

```text
artifact: outputs/analysis/WEIGHT_TRANSFER_TARGET_CAMPAIGN_SUMMARY.md
status: HOLD_FORWARD_LATERAL_SUPPORT_TRADEOFF
```

The evidence now rules out several nearby fixes:

```text
dynamic-roll lateral-fix:
  finds 50-tick seed-robust fragments
  fails 100/150-tick sustained gates

forward-intent teachers:
  can create forward displacement
  usually buy it with excessive lateral velocity

world/base-y CoM controller:
  keeps lateral velocity low
  rarely permits push

stance-foot-relative controller:
  improves contact and lateral quality
  still fails forward displacement

sagittal/ankle push-off additions:
  do not beat the aggressive stance-relative baseline
```

So the remaining issue is not a missing scalar gate, push sign, or simple
stance-foot-relative correction. The next source should combine:

```text
dynamic-roll contact timing
  plus
state-aware stance/swing sequencing
  plus
sustained-window scoring
```

## Why Contact-Timed Snippets

The dynamic-roll lateral-fix family is still the best motion evidence:

```text
50-sample curation: PASS_CURATED_DATASET_SEED_READY
50-sample curated windows: 70
curated source files: 2
robust curated modes: 3
```

But the same trace family fails sustained checks:

```text
100-sample curation: curated_seed_windows=0
150-sample objective: HOLD_NO_SEED_ROBUST_TARGETS
150-sample curation: curated_seed_windows=0
```

The useful thing in those fragments is probably not the exact joint target
sequence. It is the timing relationship between:

```text
roll/load shift
single-support transition
swing clearance
small forward displacement
```

The next experiment should preserve that timing while generating a longer,
state-aware target sequence that can be scored over 100-150 ticks.

## Implemented First-Pass Audit Tool

The first-pass audit tool is now available:

```text
tools/build_contact_timed_reference_snippets.py
```

Inputs:

```text
--curation-json outputs/analysis/target_generator_dynamic_roll_lateral_fix_window_curation_50.json
--output-md outputs/analysis/CONTACT_TIMED_REFERENCE_SNIPPETS.md
--output-json outputs/analysis/contact_timed_reference_snippets.json
--manifest-json outputs/analysis/contact_timed_reference_snippets_manifest.json
```

Behavior:

```text
1. read curated 50-tick dynamic-roll windows
2. extract contact timing, support side, roll phase, foot clearance, and local dx
3. classify whether source fragments contain usable single-support alternation
4. write a compact manifest for review/replay
5. block training if the source fragments are double-support dominated
```

This is an audit and manifest builder, not a training job.

## First-Pass Result

The robust dynamic-roll fragments do not contain enough single-support timing
to justify BC/PPO seeding:

```text
artifact: outputs/analysis/CONTACT_TIMED_REFERENCE_SNIPPETS.md
status: HOLD_SOURCE_FRAGMENTS_DOUBLE_SUPPORT
entries: 9
pass_entries: 0
double_support_hold_entries: 9
single_support_pct_mean: 7.33%
double_support_pct_mean: 92.67%
```

The aggregate sequence replay also held:

```text
artifact: outputs/analysis/CONTACT_TIMED_REFERENCE_SEQUENCE_REPLAY.md
status: HOLD_SEQUENCE_REPLAY_TERMINATED
seed_000: terminated at 85 samples after forward lunge/pitch
seed_002: duration complete but low forward motion
```

Objective scoring over replay traces confirms no seed-robust target:

```text
100-tick score: outputs/analysis/CONTACT_TIMED_REFERENCE_SEQUENCE_SCORE_100.md
150-tick score: outputs/analysis/CONTACT_TIMED_REFERENCE_SEQUENCE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

Interpretation:

```text
the current "good" 50-tick fragments are stable mostly because they stay in
double support; they are not clean stepping snippets that the policy merely
fails to execute.
```

Therefore the next generator must explicitly search for or synthesize
single-support / weight-transfer timing. Do not train from the current
dynamic-roll 50-tick fragments.

The replay smoke tool now supports default-off trace export:

```text
tools/run_target_sequence_replay_smoke.py --trace-dir <path>
```

Those traces can be scored with `tools/score_target_candidates_objective.py`.

## Single-Support Primitive Probe

A bounded probe tried to force single support using the existing open-loop
primitive family:

```text
artifact: outputs/analysis/TARGET_GENERATOR_SINGLE_SUPPORT_PROBE.md
score_100: outputs/analysis/TARGET_GENERATOR_SINGLE_SUPPORT_PROBE_SCORE_100.md
score_150: outputs/analysis/TARGET_GENERATOR_SINGLE_SUPPORT_PROBE_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

The best scored windows still remained double-support dominated:

```text
100 ticks:
  seed0 vx: ~0.022 m/s
  seed2 vx: ~0.027 m/s
  double support: 95-96%

150 ticks:
  seed0 vx: ~0.016 m/s
  seed2 vx: ~0.019 m/s
  double support: 96.7-97.3%
```

Decision:

```text
do not keep expanding nearby open-loop lift-pulse / roll-assist / stance-push
grids as the main path.
```

The next source should be state-aware: it must confirm body-over-stance support
before swing, and should score support transfer as a first-class objective.

## Support-Gated State Controller Result

The CoM controller now has a default-off swing readiness gate:

```text
tools/probe_com_weight_transfer_controller.py --gate-swing-on-ready
```

The first support-gated probe held:

```text
artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SUPPORT_GATED_PROBE.md
score_100: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SUPPORT_GATED_SCORE_100.md
score_150: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_SUPPORT_GATED_SCORE_150.md
status: HOLD_NO_SEED_ROBUST_TARGETS
```

It improved contact discipline but froze forward motion:

```text
100 ticks:
  seed0 vx: -0.0019 m/s
  seed2 vx: 0.0009 m/s
  single support: 20-26%
  double support: 73-78%

150 ticks:
  seed0 vx: -0.0053 m/s
  seed2 vx: 0.0002 m/s
  single support: ~20.7%
  double support: 77.3-78.7%
```

Decision:

```text
hard readiness gating is too passive. The next support-transfer source must
actively drive the body into the ready state before requesting swing/push.
```

## Stateful Support-Phase Result

The CoM controller now supports default-off stateful phase progression:

```text
tools/probe_com_weight_transfer_controller.py --stateful-support-phase
```

Strict and timeout-transition variants were tested:

```text
strict:
  artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_STRICT_PROBE.md
  score_100: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_STRICT_SCORE_100.md
  score_150: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_STRICT_SCORE_150.md
  status: HOLD_NO_SEED_ROBUST_TARGETS

timeout:
  artifact: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_TIMEOUT_PROBE.md
  score_100: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_TIMEOUT_SCORE_100.md
  score_150: outputs/analysis/COM_WEIGHT_TRANSFER_CONTROLLER_STATEFUL_TIMEOUT_SCORE_150.md
  status: HOLD_NO_SEED_ROBUST_TARGETS
```

The strict variant sometimes advanced phases, and the timeout variant forced
more transitions, but both remained essentially non-moving:

```text
strict top aggregate:
  mean_vx: ~-0.0007 m/s
  push_allowed_mean: ~0.33%

timeout top aggregate:
  mean_vx: ~-0.0010 m/s
  push_allowed_mean: ~1.33%
```

Decision:

```text
stateful phase mechanics are not enough. The next target source must change the
propulsion primitive or contact/foot-placement model, not just the phase
transition logic around the same pitch-chain stance push.
```

## Candidate Generation Rules

The generated snippet should keep:

```text
left/right support alternation from the curated fragment
contact transition timing
roll/load timing relative to support side
swing clearance timing
target velocity envelope
```

It should be allowed to change:

```text
hip pitch reach magnitude
stance push magnitude
ankle push-off coupling
cycle duration
cycle-to-cycle forward bias
cycle-to-cycle lateral damping
```

It should not copy:

```text
above-envelope target spikes
excess lateral velocity
single-seed-only windows
short 50-tick snippets as if they were sustained gaits
```

## Required Metrics

Report per generated source and seed:

```text
mean_vx
local forward displacement
vy_abs_p95
body_pitch_abs_p95
base_height_min
double_support_pct
single_support_pct
left/right single-support pct
contact transitions
foot_site_z_p95
sent_target_velocity_p95
joint_tracking_p95
done margin
```

Also report snippet-specific diagnostics:

```text
source curated window id
source seed
source mode
snippet stitch count
cycle duration
contact timing mismatch vs source
support-side dwell timing
forward displacement per cycle
lateral displacement per cycle
```

## Gate

The first pass must use the same gate as the current target-source campaign:

```text
PASS_CONTACT_TIMED_SNIPPETS:
  seeds 0 and 2 both have a 100-tick window with:
    mean_vx >= 0.04 m/s
    local forward displacement >= 0.04 m
    vy_abs_p95 <= 0.12 m/s
    body_pitch_abs_p95 <= 0.35 rad
    base_height_min >= 0.145 m
    double_support_pct <= 90%
    single_support_pct >= 8%
    min_each_single_support_pct >= 2%
    contact_transitions >= 3
    sent_target_velocity_p95 <= 2.5 rad/s
    joint_tracking_p95 <= 0.12 rad
```

Preferred before dataset building:

```text
same gate over 150 ticks
local forward displacement >= 0.06 m
```

Passing this target-source gate still does not authorize robot validation. It
only authorizes a reviewed target dataset or imitation-smoke branch.

## Stop Rules

Stop this branch if:

```text
the generated snippets only pass by increasing lateral velocity
the generated snippets only pass for one seed
the generated snippets require target velocity above 2.5 rad/s p95
the generated snippets collapse to double support
the best 100-tick displacement stays below the aggressive stance-relative 0.025 m baseline
```

If those holds repeat, the next branch should move away from target snippets and
toward a closed-loop teacher/controller that observes body/contact state at
runtime.

## Non-Goals

```text
do not train PPO/BC yet
do not run robot tests
do not run grounded replay
do not deploy
do not relax the actuator envelope
do not treat 50-tick fragments as walking
do not keep expanding scalar CoM gates
```
