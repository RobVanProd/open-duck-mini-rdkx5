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

## Proposed Tool

Add a future tool:

```text
tools/build_contact_timed_reference_snippets.py
```

Inputs:

```text
--source-traces outputs/analysis/target_generator_dynamic_roll_lateral_fix_traces/*/seed_*.jsonl
--curation-json outputs/analysis/target_generator_dynamic_roll_lateral_fix_window_curation_50.json
--playground-path ../Open_Duck_Playground
--seeds 0,2
--command-x 0.04
--duration-s 3.0
--output-md outputs/analysis/CONTACT_TIMED_REFERENCE_SNIPPETS.md
--output-json outputs/analysis/contact_timed_reference_snippets.json
--trace-dir outputs/analysis/contact_timed_reference_snippets_traces
```

Behavior:

```text
1. read curated 50-tick dynamic-roll windows
2. extract contact timing, support side, roll phase, foot clearance, and local dx
3. build a longer snippet by stitching or phase-warping contact-timed cycles
4. replace exact joint targets with bounded, envelope-aware targets
5. replay the generated snippet through the normal MJX/rate-limit path
6. score with the existing 100/150 tick objective gate
```

This should be a target-source generator, not a training job.

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
