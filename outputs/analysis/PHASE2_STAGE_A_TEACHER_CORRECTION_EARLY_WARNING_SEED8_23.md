# Teacher-Correction Early-Warning Analysis

status: `PASS_TEACHER_CORRECTION_EARLY_WARNING_ANALYSIS_READY`

Offline saved-trace analysis only. No simulation, training, robot access,
deployment, GPU, or Colab allocation was performed.

- traces: `16`
- failures/completed: `5` / `11`

## Window Ranking

| window | statistic | ROC AUC | failure mean | completed mean |
|---:|---|---:|---:|---:|
| 1 ticks (0.02s) | `mean` | 0.582 | 0.03530 | 0.02047 |
| 1 ticks (0.02s) | `p95` | 0.582 | 0.09144 | 0.04600 |
| 1 ticks (0.02s) | `max` | 0.600 | 0.10453 | 0.05397 |
| 3 ticks (0.06s) | `mean` | 0.673 | 0.02611 | 0.01915 |
| 3 ticks (0.06s) | `p95` | 0.764 | 0.07872 | 0.05091 |
| 3 ticks (0.06s) | `max` | 0.782 | 0.11933 | 0.07076 |
| 5 ticks (0.10s) | `mean` | 0.636 | 0.03135 | 0.02668 |
| 5 ticks (0.10s) | `p95` | 0.636 | 0.08446 | 0.07659 |
| 5 ticks (0.10s) | `max` | 0.618 | 0.13016 | 0.10952 |
| 10 ticks (0.20s) | `mean` | 0.836 | 0.03264 | 0.02840 |
| 10 ticks (0.20s) | `p95` | 0.909 | 0.08815 | 0.07410 |
| 10 ticks (0.20s) | `max` | 0.745 | 0.14517 | 0.11540 |
| 20 ticks (0.40s) | `mean` | 0.891 | 0.03386 | 0.02685 |
| 20 ticks (0.40s) | `p95` | 0.855 | 0.08759 | 0.06891 |
| 20 ticks (0.40s) | `max` | 0.782 | 0.15330 | 0.11765 |

## Per-Seed First Window

Window: `10` ticks

| seed | failure | mean | p95 | max |
|---:|---:|---:|---:|---:|
| 8 | `False` | 0.02521 | 0.05631 | 0.09054 |
| 9 | `True` | 0.03024 | 0.08614 | 0.11726 |
| 10 | `False` | 0.02870 | 0.07934 | 0.11851 |
| 11 | `False` | 0.03138 | 0.08145 | 0.11999 |
| 12 | `True` | 0.03147 | 0.08268 | 0.12319 |
| 13 | `False` | 0.04463 | 0.12348 | 0.18980 |
| 14 | `True` | 0.03178 | 0.08320 | 0.12186 |
| 15 | `False` | 0.02642 | 0.06947 | 0.11610 |
| 16 | `False` | 0.02562 | 0.06936 | 0.14564 |
| 17 | `False` | 0.02622 | 0.06895 | 0.08189 |
| 18 | `False` | 0.02669 | 0.06416 | 0.07459 |
| 19 | `True` | 0.03001 | 0.08693 | 0.14549 |
| 20 | `True` | 0.03967 | 0.10178 | 0.21806 |
| 21 | `False` | 0.02328 | 0.06010 | 0.08022 |
| 22 | `False` | 0.02303 | 0.06019 | 0.08628 |
| 23 | `False` | 0.03129 | 0.08226 | 0.16583 |

## Interpretation

Teacher disagreement contains early failure information but is not a recovery target. No operating threshold is selected by this exploratory analysis.

## Limitations

- The same 16 traces are used to estimate AUC; no held-out replication exists.
- AUC measures ranking, not calibrated probability or a safe threshold.
- Teacher disagreement can identify out-of-distribution states while still proposing unsafe actions.
