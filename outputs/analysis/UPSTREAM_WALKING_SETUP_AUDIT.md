# Upstream Walking Setup Audit

status: `HOLD_PUBLISHED_POLICY_SIM_AUDIT_NEEDED`

This is an offline provenance artifact. It does not train, deploy, SSH, or run
robot tests.

## Provenance

| item | value |
|---|---|
| upstream Playground worktree | `/tmp/open_duck_playground_origin_main` |
| upstream Playground commit | `b9be205ac64488c23504ca42e5ec790337adeec3` |
| README current-win task | `flat_terrain_backlash` |
| README current-win timesteps | `300000000` |
| runner default task | `flat_terrain` |
| runner default timesteps | `150000000` |
| deployment policy repo | `apirrone/Open_Duck_Mini` branch `v2` |
| deployment policy file | `BEST_WALK_ONNX_2.onnx` |
| upstream policy blob sha | `7e4536d90e35f9a3a886fb7584d489ad4894dfe0` |
| upstream policy size | `884177` |
| local policy sha256 | `3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067` |

## Key Evidence

| artifact | status | note |
|---|---|---|
| `REFERENCE_PUSH_EFFECTIVENESS_UPSTREAM_MAIN_NEAREST.md` | `HOLD_REFERENCE_CONTACT_MISMATCH` | upstream-main `flat_terrain` reference has no positive ref-single future-vx delta |
| `REFERENCE_PUSH_EFFECTIVENESS_UPSTREAM_MAIN_BACKLASH_NEAREST.md` | `HOLD_REFERENCE_CONTACT_MISMATCH` | upstream-main `flat_terrain_backlash` reference still has no positive ref-single future-vx delta |
| `UPSTREAM_SIM_MORPHOLOGY_AUDIT.md` | `PASS_MORPHOLOGY_MATCHES_UPSTREAM_CODE_DRIFT_ONLY` | XML/reference assets match upstream byte-for-byte |

## Backlash Reference Result

Command:

```text
x = 0.074
y = -0.037
yaw = -0.074
```

| mode | falls | mean vx | contact mismatch | ref-single future vx delta | ref-single vy p95 | ref-single pitch vel p95 |
|---|---:|---:|---:|---:|---:|---:|
| raw | 1/8 | -0.0500 | 66.9833% | -0.0390 | 0.1859 | 5.2400 |
| cycle projected | 0/8 | -0.0114 | 72.9500% | -0.0356 | 0.1713 | 5.2400 |
| contact synchronized projected | 1/8 | 0.0301 | 20.1366% | -0.0051 | 0.1696 | 5.2400 |

## Decision

The next useful branch is not another local teacher damping variant. The next
gate is a published-policy sim audit:

```text
Run BEST_WALK_ONNX_2 in upstream-main Playground, especially
flat_terrain_backlash, and analyze whether the closed-loop policy produces
forward push-effectiveness where the reference-target path does not.
```

If the published policy produces positive forward impulse, mine that closed-loop
mechanism. If it does not, treat the sim contract or morphology/feasibility
assumption as the blocker before more teacher tuning.
