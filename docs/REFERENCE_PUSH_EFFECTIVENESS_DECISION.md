# Reference Push-Effectiveness Decision

This is an offline decision note. It does not run robot tests, SSH, deploy,
train, or change runtime behavior.

## Why This Gate Exists

The stance-relative teacher series produced many locally justified holds. The
latest planned branch, `PLAN_STANCE_RELATIVE_LATERAL_DAMPING`, would continue
the same loop by adding more lateral containment around a push primitive whose
measured forward effect is weak.

Before authorizing another teacher variant, the campaign must answer a higher
level question:

```text
Does the upstream/reference gait produce forward CoM acceleration in this sim?
```

If yes, the target-generation work is still a controller design problem. If no,
the blocker is likely upstream of the teacher recipe: sim/morphology/reference
compatibility or a physical feasibility limit.

## Tooling

Added:

```text
tools/analyze_reference_push_effectiveness.py
```

It reads existing `eval_reference_motion_rollout.py` JSONL traces and applies
the same core read used by the teacher push-effectiveness analyzer:

```text
when the reference asks for single support,
does local forward velocity increase 0.1s later?
```

It also reports:

```text
actual-vs-reference contact mismatch
reference-single / actual-double support percentage
lateral velocity during reference single support
pitch-chain target velocity during reference single support
```

`tools/eval_reference_motion_rollout.py` now has two offline-only helpers:

```text
--use-playground-reference
--command-y / --command-yaw
```

These allow testing the original Playground polynomial reference without
temporarily replacing it with the x=0.04 override.

## Evidence

### Matched x=0.04 Override

Artifact:

```text
outputs/analysis/REFERENCE_PUSH_EFFECTIVENESS_V20_MATCHED.md
```

Result:

```text
status: HOLD_REFERENCE_PROPULSION_UNSTABLE
best reference-single future vx delta: +0.0161 m/s
```

The only positive-delta variant was `contact_gated_projected`, but it was not a
usable pass:

```text
contact mismatch: 69.4217%
reference-single vy p95: 0.2688 m/s
reference-single pitch-chain target velocity p95: 5.1133 rad/s
```

Interpretation:

```text
The matched reference can create a small forward impulse only while violating
lateral stability and the measured actuator envelope.
```

### Upstream Playground Reference

Command tested:

```text
x = 0.074
y = -0.037
yaw = -0.074
```

This is the nearest upstream reference key that previously caused the V19
command mismatch.

Artifacts:

```text
outputs/analysis/REFERENCE_MOTION_ROLLOUT_UPSTREAM_NEAREST_RAW.md
outputs/analysis/REFERENCE_MOTION_ROLLOUT_UPSTREAM_NEAREST_cycle_projected.md
outputs/analysis/REFERENCE_MOTION_ROLLOUT_UPSTREAM_NEAREST_contact_synchronized_projected.md
outputs/analysis/REFERENCE_PUSH_EFFECTIVENESS_UPSTREAM_NEAREST.md
```

Result:

```text
status: HOLD_REFERENCE_CONTACT_MISMATCH
best reference-single future vx delta: -0.0099 m/s
```

Summary:

| mode | falls | mean vx | contact mismatch | ref-single future vx delta | ref-single vy p95 | ref-single pitch vel p95 |
|---|---:|---:|---:|---:|---:|---:|
| raw | 8/8 | -0.0870 | 69.5729% | -0.0512 | 0.3332 | 5.2400 |
| cycle projected | 8/8 | -0.0086 | 71.1627% | -0.0276 | 0.3265 | 5.2400 |
| contact synchronized projected | 8/8 | -0.0108 | 14.5439% | -0.0099 | 0.3295 | 5.2400 |

Interpretation:

```text
The upstream reference gait does not produce positive forward push-effectiveness
in this local sim contract. Projection and contact retiming reduce some
secondary failures, but the reference-single support windows still do not
accelerate the body forward.
```

### Upstream Main Playground Code

The same command was also run against a detached `origin/main` Playground
worktree:

```text
/tmp/open_duck_playground_origin_main
origin/main: b9be205ac64488c23504ca42e5ec790337adeec3
```

Artifacts:

```text
outputs/analysis/REFERENCE_MOTION_ROLLOUT_UPSTREAM_MAIN_NEAREST_raw.md
outputs/analysis/REFERENCE_MOTION_ROLLOUT_UPSTREAM_MAIN_NEAREST_cycle_projected.md
outputs/analysis/REFERENCE_MOTION_ROLLOUT_UPSTREAM_MAIN_NEAREST_contact_synchronized_projected.md
outputs/analysis/REFERENCE_PUSH_EFFECTIVENESS_UPSTREAM_MAIN_NEAREST.md
```

Result:

```text
status: HOLD_REFERENCE_CONTACT_MISMATCH
best reference-single future vx delta: -0.0158 m/s
```

Summary:

| mode | falls | mean vx | contact mismatch | ref-single future vx delta | ref-single vy p95 | ref-single pitch vel p95 |
|---|---:|---:|---:|---:|---:|---:|
| raw | 4/8 | -0.0863 | 70.9015% | -0.0527 | 0.3219 | 5.2400 |
| cycle projected | 2/8 | -0.0120 | 71.4134% | -0.0312 | 0.3084 | 5.2400 |
| contact synchronized projected | 2/8 | -0.0127 | 14.6741% | -0.0158 | 0.3192 | 5.2400 |

Interpretation:

```text
The upstream `origin/main` code path improves duration relative to the local
training branch, but it still does not produce net forward acceleration during
reference single-support windows.
```

### Upstream Main Backlash Task

The upstream README documents the current winning training command as:

```bash
uv run playground/open_duck_mini_v2/runner.py \
  --task flat_terrain_backlash \
  --num_timesteps 300000000
```

The same upstream reference key was therefore also tested against the detached
`origin/main` worktree using `flat_terrain_backlash`.

Artifacts:

```text
outputs/analysis/REFERENCE_MOTION_ROLLOUT_UPSTREAM_MAIN_BACKLASH_NEAREST_raw.md
outputs/analysis/REFERENCE_MOTION_ROLLOUT_UPSTREAM_MAIN_BACKLASH_NEAREST_cycle_projected.md
outputs/analysis/REFERENCE_MOTION_ROLLOUT_UPSTREAM_MAIN_BACKLASH_NEAREST_contact_synchronized_projected.md
outputs/analysis/REFERENCE_PUSH_EFFECTIVENESS_UPSTREAM_MAIN_BACKLASH_NEAREST.md
```

Result:

```text
status: HOLD_REFERENCE_CONTACT_MISMATCH
best reference-single future vx delta: -0.0051 m/s
```

Summary:

| mode | falls | mean vx | contact mismatch | ref-single future vx delta | ref-single vy p95 | ref-single pitch vel p95 |
|---|---:|---:|---:|---:|---:|---:|
| raw | 1/8 | -0.0500 | 66.9833% | -0.0390 | 0.1859 | 5.2400 |
| cycle projected | 0/8 | -0.0114 | 72.9500% | -0.0356 | 0.1713 | 5.2400 |
| contact synchronized projected | 1/8 | 0.0301 | 20.1366% | -0.0051 | 0.1696 | 5.2400 |

Interpretation:

```text
The README's backlash task improves some duration/stability metrics, but it
still does not make the upstream reference's single-support windows create net
forward acceleration.
```

## Decision

Do not continue to `PLAN_STANCE_RELATIVE_LATERAL_DAMPING` as the default next
branch.

The current result is stronger than "teacher needs another damping term":

```text
both the local teacher pushes and the upstream/reference gait fail the same
forward-impulse question in this sim, including when evaluated against
upstream `origin/main` Playground code and the README's
`flat_terrain_backlash` task
```

The morphology/reference-file audit shows the local XML and polynomial
reference file match upstream byte-for-byte, so the current blocker is not a
local MJCF/reference-file edit. The next work should identify the exact
upstream walking policy/export path and test whether the published ONNX policy
uses closed-loop feedback to create forward propulsion that the open-loop
reference-target path does not.

## Published-Policy Follow-Up

The recommended published-policy audit has been run:

```text
outputs/analysis/PUBLISHED_POLICY_PROPULSION_AUDIT.md
status: PASS_POLICY_CLOSED_LOOP_FORWARD_MOTION
task: upstream-main flat_terrain_backlash
seeds: 8
duration complete: 8 / 8
moving seeds with track ratio >= 0.5: 7 / 8
mean local vx: 0.0540 m/s
mean single-support 0.1s future vx delta: +0.0042 m/s
```

The policy/reference mechanism comparison then narrowed the difference:

```text
outputs/analysis/POLICY_REFERENCE_MECHANISM_COMPARISON.md
status: PASS_POLICY_REFERENCE_MECHANISM_SPLIT
policy actual single-support fraction: 44.8%
reference contact-synchronized actual single-support fraction: 19.25%
policy single-support 0.1s future vx delta: +0.0042 m/s
reference requested-single 0.1s future vx delta: -0.0051 m/s
policy pitch-chain target velocity p95 mean: 3.0488 rad/s
reference contact-synchronized pitch-chain target velocity p95 mean: 4.9811 rad/s
```

The follow-up command sweep prevents overclaiming:

```text
outputs/analysis/PUBLISHED_POLICY_COMMAND_SWEEP.md
status: WARN_COMMAND_SPECIFIC_PROPULSION_OVER_ENVELOPE
```

Summary:

```text
straight x=0.04:
  moving seeds: 0 / 8
  mean tracking ratio: 0.0468
  max-joint pitch-chain p95 target velocity: 1.2742 rad/s

straight x=0.08:
  moving seeds: 7 / 8
  mean tracking ratio: 0.7998
  max-joint pitch-chain p95 target velocity: 5.1546 rad/s

upstream turning command:
  moving seeds: 7 / 8
  mean tracking ratio: 0.7294
  max-joint pitch-chain p95 target velocity: 4.6157 rad/s
```

So the published policy is a closed-loop movement existence proof, but it is
not yet an envelope-safe robot candidate. Straight `x=0.04` is not cleared by
the published policy either, while the moving command cells exceed the measured
per-joint target-rate envelope.

The compact command-grid screen then checked nearby straight and scaled-turning
cells:

```text
outputs/analysis/PUBLISHED_POLICY_COMMAND_GRID.md
status: HOLD_MOVEMENT_REQUIRES_OVER_ENVELOPE

straight x=0.05:
  moving seeds: 0 / 2
  max-seed pitch-chain p95 target velocity: 2.7422 rad/s

straight x=0.06:
  moving seeds: 0 / 2
  max-seed pitch-chain p95 target velocity: 3.8816 rad/s

straight x=0.07:
  moving seeds: 0 / 2
  max-seed pitch-chain p95 target velocity: 3.6654 rad/s

scaled turning 0.50 -> 0.90:
  moving seeds: 0 / 2 at every tested scale

scaled turning 1.00:
  moving seeds: 2 / 2
  max-seed pitch-chain p95 target velocity: 5.0147 rad/s
```

That search did not find a nearby command cell where the published policy both
moves forward and stays under the measured max-joint pitch-chain velocity
envelope. The current best read is a sharp activation cliff: below the envelope,
the policy mostly stands; when it walks, at least one pitch-chain joint exceeds
the measured envelope.

The teacher-window extraction gives a more useful next target than copying the
whole moving trajectory:

```text
outputs/analysis/CLOSED_LOOP_TEACHER_TEMPLATE.md
status: PASS_HAS_LOW_RATE_MOVING_TEACHER_WINDOWS

straight x=0.08:
  moving + in-envelope ticks: 70.55%
  moving + single-support + in-envelope ticks: 32.80%
  safe moving single-support future vx delta: +0.0039 m/s

upstream turning command:
  moving + in-envelope ticks: 63.70%
  moving + single-support + in-envelope ticks: 28.90%
  safe moving single-support future vx delta: +0.0034 m/s

straight x=0.04:
  moving + single-support + in-envelope ticks: 1.25%
  safe moving single-support future vx delta: -0.0483 m/s
```

So the full moving command cells are not envelope-safe, but they contain
low-rate closed-loop propulsion windows. Those windows are the current best
teacher source.

That source now has a dataset and smoke-test path:

```text
outputs/analysis/CLOSED_LOOP_TEACHER_WINDOW_CURATION.md:
  status: PASS_CURATED_DATASET_SEED_READY
  curated windows: 259 / 301

outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_MANIFEST.md:
  status: PASS_TARGET_DATASET_MANIFEST_READY
  entries: 259
  source rollout dirs: 16

outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_SANITY_CHECK.md:
  status: PASS_TARGET_DATASET_SANITY_CHECK
  bc_readiness_status: PASS_TARGET_DATASET_BC_READY

outputs/analysis/CLOSED_LOOP_TEACHER_DATASET_BC_SMOKE.md:
  status: PASS_BC_FIT_SMOKE_FORWARD_REPLAY
  model: kNN, k=5
  command: straight x=0.08
  seeds: 0, 1
  mean vx: 0.0673-0.0688 m/s
  sent target velocity p95: 2.4224-2.5628 rad/s
```

This does not produce a deployable policy, but it proves the curated low-rate
teacher windows are usable for a toy closed-loop imitation replay.

Answers to the original discriminator:

```text
1. Does BEST_WALK_ONNX_2 produce positive push-effectiveness in upstream-main
   Playground, especially flat_terrain_backlash?
   Yes, in closed loop.
2. If yes, what closed-loop contact/propulsion mechanism does the policy use
   that the reference-target path lacks?
   It creates substantially more actual single-support time and keeps
   pitch-chain target-rate lower while preserving forward motion. The exact
   state/action template still needs extraction.
3. If no, is the sim contract or morphology/feasibility assumption the real
   blocker?
   Not the current read. Published policy locomotion rules out a broad
   impossibility claim for upstream-main sim/morphology.
4. Do not return to local teacher variants until this policy/reference split is
   explained.
```

Recommended next offline task:

```text
design a reviewed imitation/pretraining experiment from the curated low-rate
closed-loop teacher-window manifest; do not train from the full over-envelope
published-policy trajectory
```

Robot validation remains blocked.
