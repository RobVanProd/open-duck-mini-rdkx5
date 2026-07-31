# Teacher-Correction Early-Warning Analysis

status: `PASS_TEACHER_CORRECTION_EARLY_WARNING_ANALYSIS_READY`

Offline saved-trace analysis only. No simulation, training, robot access,
deployment, GPU, or Colab allocation was performed.

- traces: `16`
- failures/completed: `2` / `14`

## Window Ranking

| window | statistic | ROC AUC | failure mean | completed mean |
|---:|---|---:|---:|---:|
| 1 ticks (0.02s) | `mean` | 0.929 | 0.05454 | 0.02714 |
| 1 ticks (0.02s) | `p95` | 0.929 | 0.13367 | 0.05949 |
| 1 ticks (0.02s) | `max` | 1.000 | 0.16782 | 0.06674 |
| 3 ticks (0.06s) | `mean` | 1.000 | 0.03667 | 0.02097 |
| 3 ticks (0.06s) | `p95` | 1.000 | 0.10732 | 0.05695 |
| 3 ticks (0.06s) | `max` | 1.000 | 0.17178 | 0.07629 |
| 5 ticks (0.10s) | `mean` | 0.929 | 0.03656 | 0.02631 |
| 5 ticks (0.10s) | `p95` | 1.000 | 0.12220 | 0.06879 |
| 5 ticks (0.10s) | `max` | 1.000 | 0.17283 | 0.10217 |
| 10 ticks (0.20s) | `mean` | 1.000 | 0.04171 | 0.02743 |
| 10 ticks (0.20s) | `p95` | 1.000 | 0.11041 | 0.06761 |
| 10 ticks (0.20s) | `max` | 1.000 | 0.17283 | 0.10671 |
| 20 ticks (0.40s) | `mean` | 1.000 | 0.03967 | 0.02506 |
| 20 ticks (0.40s) | `p95` | 1.000 | 0.10954 | 0.06174 |
| 20 ticks (0.40s) | `max` | 1.000 | 0.18917 | 0.10824 |

## Per-Seed First Window

Window: `10` ticks

| seed | failure | mean | p95 | max |
|---:|---:|---:|---:|---:|
| 24 | `False` | 0.02873 | 0.07032 | 0.12234 |
| 25 | `False` | 0.02493 | 0.05973 | 0.08684 |
| 26 | `False` | 0.02606 | 0.06991 | 0.10353 |
| 27 | `False` | 0.02598 | 0.06562 | 0.14123 |
| 28 | `False` | 0.03285 | 0.07857 | 0.12095 |
| 29 | `False` | 0.02526 | 0.06888 | 0.11263 |
| 30 | `False` | 0.02656 | 0.06432 | 0.08281 |
| 31 | `False` | 0.02442 | 0.06318 | 0.08994 |
| 32 | `False` | 0.02728 | 0.07066 | 0.10503 |
| 33 | `False` | 0.03009 | 0.06981 | 0.09995 |
| 34 | `False` | 0.02977 | 0.07225 | 0.10928 |
| 35 | `False` | 0.03127 | 0.07434 | 0.14271 |
| 36 | `True` | 0.04669 | 0.12407 | 0.16279 |
| 37 | `True` | 0.03674 | 0.09675 | 0.18287 |
| 38 | `False` | 0.02397 | 0.05089 | 0.07379 |
| 39 | `False` | 0.02682 | 0.06810 | 0.10294 |

## Interpretation

Teacher disagreement contains early failure information but is not a recovery target. No operating threshold is selected by this exploratory analysis.

## Limitations

- This is a held-out seed block relative to the frozen discovery metrics, but it contains few failure positives.
- AUC measures ranking, not calibrated probability or a safe threshold.
- Teacher disagreement can identify out-of-distribution states while still proposing unsafe actions.
