# Contact Physics Audit

This is an offline sim audit. It does not train, deploy, SSH, or run robot
tests.

## Executive Summary

The reference push-effectiveness failure suggested a contact/friction problem:
the reference asks for single support, but the body often stays in double
support or fails to convert stance motion into forward CoM acceleration.

The first cheap contact-physics probe tested the highest-priority explanation:
floor friction/contact solver settings.

Result:

```text
HOLD_CONTACT_FRICTION_SOLVER_NOT_SUFFICIENT
```

The local/current Playground XML matches upstream Playground XML byte-for-byte,
so there is no local Playground foot-friction drift relative to upstream
Playground. However, the older `Open_Duck_Mini` MuJoCo scene uses stronger
global contact parameters:

```text
Open_Duck_Mini scene default geom friction: 1.5 0.01 0.0006
Open_Duck_Mini solver iterations / ls_iterations: 100 / 50

Open_Duck_Playground flat/backlash floor friction: 0.6 0.005 0.0001
Open_Duck_Playground solver iterations / ls_iterations: 1 / 5
```

A temporary contact probe copied upstream-main Playground to `/tmp`, changed
the flat/backlash floor friction to `1.5 0.01 0.0006`, changed robot solver
iterations to `100/50`, and reran the reference push-effectiveness test on
`flat_terrain_backlash`.

The probe did not rescue forward propulsion:

```text
baseline best reference-single future-vx delta:      -0.0051 m/s
contact-probe best reference-single future-vx delta: -0.0182 m/s
```

## Compiled Contact Parameters

Compiled with MuJoCo from the current upstream-main Playground worktree:

```text
scene_flat_terrain_backlash.xml
  option iterations: 1
  option ls_iterations: 5
  noslip_iterations: 0
  floor friction: [0.6, 0.005, 0.0001]
  floor condim: 3
  floor priority: 1
  foot TPU friction: [1.0, 0.005, 0.0001]
  foot TPU condim: 3
  default solref: [0.02, 1.0]
  default solimp: [0.9, 0.95, 0.001, 0.5, 2.0]
```

Compiled from the older `Open_Duck_Mini` scene:

```text
scene.xml
  option iterations: 100
  option ls_iterations: 50
  noslip_iterations: 0
  floor friction: [1.5, 0.01, 0.0006]
  floor condim: 3
  default solref: [0.02, 1.0]
  default solimp: [0.9, 0.95, 0.001, 0.5, 2.0]
```

## Contact Probe

Temporary probe path:

```text
/tmp/open_duck_playground_origin_main_contact_probe
```

Temporary changes:

```text
scene_flat_terrain.xml floor friction:
  0.6 -> 1.5 0.01 0.0006

scene_flat_terrain_backlash.xml floor friction:
  0.6 -> 1.5 0.01 0.0006

open_duck_mini_v2.xml option:
  iterations=1 ls_iterations=5 -> iterations=100 ls_iterations=50

open_duck_mini_v2_backlash.xml option:
  iterations=1 ls_iterations=5 -> iterations=100 ls_iterations=50
```

No repository XML was modified.

Artifact:

```text
outputs/analysis/REFERENCE_PUSH_EFFECTIVENESS_CONTACT_PROBE_BACKLASH_NEAREST.md
```

Result:

```text
status: HOLD_REFERENCE_CONTACT_MISMATCH
best reference-single future vx delta: -0.0182 m/s
```

Comparison against baseline upstream-main `flat_terrain_backlash`:

| mode | baseline falls | probe falls | baseline mean vx | probe mean vx | baseline contact mismatch | probe contact mismatch | baseline ref-single dvx | probe ref-single dvx |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| raw | 1/8 | 3/8 | -0.0500 | 0.0208 | 66.9833% | 67.2202% | -0.0390 | -0.0198 |
| cycle projected | 0/8 | 0/8 | -0.0114 | -0.0120 | 72.9500% | 66.9500% | -0.0356 | -0.0397 |
| contact synchronized projected | 1/8 | 1/8 | 0.0301 | -0.0375 | 20.1366% | 4.6415% | -0.0051 | -0.0182 |

## Interpretation

The contact probe moved contact matching in the expected direction for the
contact-synchronized mode:

```text
contact mismatch: 20.1366% -> 4.6415%
reference-single / actual-double: 9.8006% -> 1.9558%
```

But forward impulse did not improve:

```text
reference-single future-vx delta: -0.0051 -> -0.0182 m/s
```

This means low floor friction or low solver iterations alone are not the
missing mechanism. Stronger contact can make the contact labels line up better,
but the reference target still does not convert single-support windows into net
forward acceleration in this sim contract.

## Decision

Do not treat floor friction/solver iteration mismatch as the root cause by
itself.

The next discriminator remains the published-policy sim audit:

```text
Does BEST_WALK_ONNX_2 closed-loop feedback produce forward propulsion where
the open-loop reference target does not?
```

If the published policy does produce positive push-effectiveness, mine its
closed-loop contact/CoM mechanism. If it does not, continue up the physical
chain toward morphology/inertia/geometry or the feasibility assumption rather
than returning to local teacher scalar tuning.

## Non-Goals

- robot tests
- SSH or deployment
- training or retraining
- committed XML contact parameter changes
- changing runtime behavior
- changing policy files
