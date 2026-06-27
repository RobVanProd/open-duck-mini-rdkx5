# Contact Physics Audit

status: `HOLD_CONTACT_FRICTION_SOLVER_NOT_SUFFICIENT`

This is an offline artifact. It does not train, deploy, SSH, or run robot
tests.

## Compiled Contact Parameters

| setup | floor friction | foot friction | iterations | ls_iterations | noslip_iterations |
|---|---|---|---:|---:|---:|
| Playground `flat_terrain_backlash` | `[0.6, 0.005, 0.0001]` | `[1.0, 0.005, 0.0001]` | 1 | 5 | 0 |
| Open_Duck_Mini `scene.xml` | `[1.5, 0.01, 0.0006]` | inherited/default scene contact | 100 | 50 | 0 |

## Temporary Contact Probe

Temporary path:

```text
/tmp/open_duck_playground_origin_main_contact_probe
```

Temporary changes:

```text
floor friction: 0.6 -> 1.5 0.01 0.0006
solver iterations: 1/5 -> 100/50
```

No repository XML was modified.

## Result

Artifact:

```text
outputs/analysis/REFERENCE_PUSH_EFFECTIVENESS_CONTACT_PROBE_BACKLASH_NEAREST.md
```

| mode | baseline falls | probe falls | baseline mean vx | probe mean vx | baseline contact mismatch | probe contact mismatch | baseline ref-single dvx | probe ref-single dvx |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| raw | 1/8 | 3/8 | -0.0500 | 0.0208 | 66.9833% | 67.2202% | -0.0390 | -0.0198 |
| cycle projected | 0/8 | 0/8 | -0.0114 | -0.0120 | 72.9500% | 66.9500% | -0.0356 | -0.0397 |
| contact synchronized projected | 1/8 | 1/8 | 0.0301 | -0.0375 | 20.1366% | 4.6415% | -0.0051 | -0.0182 |

## Interpretation

The stronger contact settings improved contact matching in the synchronized
mode but did not improve forward impulse. Low floor friction / low solver
iterations are not sufficient to explain the reference push-effectiveness
failure.

## Next Gate

Run the published-policy sim audit:

```text
BEST_WALK_ONNX_2 closed-loop on upstream-main Playground, especially
flat_terrain_backlash.
```
