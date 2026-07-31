# Phase 2 Parent-Pair Prefix Lateral Router Gate

status: `PASS_PREFIX_LATERAL_PARENT_PAIR_ROUTER_COMPACT`

This is an offline eval-only diagnostic. It did not train, SSH, deploy, run robot tests, change runtime behavior, or run grounded replay.

## Rule

`select parent with lower prefix_abs_lateral_v_mean_m_s over the first 100 ticks`

This tests whether the complementary phase-modulated and rich-context parent failures separate by early lateral leak. It is not a deployable policy by itself.

## Routed Gate

| seed | selected policy | selected status | pass | prefix lateral mean | track ratio | mean vx | pitch p95 | base min |
|---:|---|---|---|---:|---:|---:|---:|---:|
| `0` | `rich_context_parent` | `PASS_CANDIDATE_SIM_GATE` | `True` | `0.048679` | `0.2897` | `0.0232` | `0.1661` | `0.1591` |
| `1` | `phase_mod_parent` | `PASS_CANDIDATE_SIM_GATE` | `True` | `0.053831` | `0.3230` | `0.0258` | `0.2077` | `0.1554` |
| `2` | `phase_mod_parent` | `PASS_CANDIDATE_SIM_GATE` | `True` | `0.047961` | `0.3285` | `0.0263` | `0.1764` | `0.1592` |
| `6` | `phase_mod_parent` | `PASS_CANDIDATE_SIM_GATE` | `True` | `0.052760` | `0.3009` | `0.0241` | `0.1850` | `0.1572` |
| `7` | `rich_context_parent` | `PASS_CANDIDATE_SIM_GATE` | `True` | `0.052342` | `0.3302` | `0.0264` | `0.1775` | `0.1589` |

## Candidate Metrics

### Seed `0`

| policy | pass | prefix lateral mean | prefix pitch max | track ratio | mean vx | base min |
|---|---|---:|---:|---:|---:|---:|
| `phase_mod_parent` | `True` | `0.048878` | `0.186448` | `0.2716` | `0.0217` | `0.1573` |
| `rich_context_parent` | `True` | `0.048679` | `0.186906` | `0.2897` | `0.0232` | `0.1591` |

### Seed `1`

| policy | pass | prefix lateral mean | prefix pitch max | track ratio | mean vx | base min |
|---|---|---:|---:|---:|---:|---:|
| `phase_mod_parent` | `True` | `0.053831` | `0.219413` | `0.3230` | `0.0258` | `0.1554` |
| `rich_context_parent` | `False` | `0.053890` | `0.207390` | `1.7276` | `0.1382` | `-0.0090` |

### Seed `2`

| policy | pass | prefix lateral mean | prefix pitch max | track ratio | mean vx | base min |
|---|---|---:|---:|---:|---:|---:|
| `phase_mod_parent` | `True` | `0.047961` | `0.186448` | `0.3285` | `0.0263` | `0.1592` |
| `rich_context_parent` | `True` | `0.047983` | `0.189379` | `0.2972` | `0.0238` | `0.1569` |

### Seed `6`

| policy | pass | prefix lateral mean | prefix pitch max | track ratio | mean vx | base min |
|---|---|---:|---:|---:|---:|---:|
| `phase_mod_parent` | `True` | `0.052760` | `0.258163` | `0.3009` | `0.0241` | `0.1572` |
| `rich_context_parent` | `True` | `0.053120` | `0.226035` | `0.3158` | `0.0253` | `0.1575` |

### Seed `7`

| policy | pass | prefix lateral mean | prefix pitch max | track ratio | mean vx | base min |
|---|---|---:|---:|---:|---:|---:|
| `phase_mod_parent` | `False` | `0.052378` | `0.194119` | `-0.5236` | `-0.0419` | `0.0673` |
| `rich_context_parent` | `True` | `0.052342` | `0.189731` | `0.3302` | `0.0264` | `0.1589` |

## Decision

- pass_count: `5/5`
- The lower-prefix-lateral rule separates the two complementary parent failures on this compact screen.
- This is still parallel-prefix eval evidence, not a single deployable/trainable parent.
- Phase 2 DR remains blocked until this behavior is preserved by a single parent or explicit trainable wrapper objective.
