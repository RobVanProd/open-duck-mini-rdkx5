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

## Decision

Do not continue to `PLAN_STANCE_RELATIVE_LATERAL_DAMPING` as the default next
branch.

The current result is stronger than "teacher needs another damping term":

```text
both the local teacher pushes and the upstream/reference gait fail the same
forward-impulse question in this sim, including when evaluated against
upstream `origin/main` Playground code
```

The morphology/reference-file audit shows the local XML and polynomial
reference file match upstream byte-for-byte, so the current blocker is not a
local MJCF/reference-file edit. The next work should identify the exact
upstream walking checkpoint/export path and any environment/config assumptions
used to make that reference gait walk.

## Next Work

Recommended next offline task:

```text
audit upstream walking setup vs local sim/morphology
```

Minimum questions:

```text
1. Which exact Playground commit/reference file/checkpoint produced the known
   upstream walking behavior?
2. Does that upstream setup use the same MJCF, actuator gains, solver options,
   foot geometry, body masses, friction, and termination rules?
3. Does the upstream reference produce positive push-effectiveness in its own
   expected sim setup?
4. If upstream works there but not locally, what changed in the local sim
   contract?
5. If upstream also fails under the current contract, stop treating another
   teacher variant as the next default move.
```

Robot validation remains blocked.
