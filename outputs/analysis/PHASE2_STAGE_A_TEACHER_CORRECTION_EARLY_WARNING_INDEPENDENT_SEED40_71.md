# Teacher-Correction Early-Warning Analysis

status: `PASS_TEACHER_CORRECTION_EARLY_WARNING_ANALYSIS_READY`

Offline saved-trace analysis only. No simulation, training, robot access,
deployment, GPU, or Colab allocation was performed.

- traces: `32`
- failures/completed: `11` / `21`

## Window Ranking

| window | statistic | ROC AUC | failure mean | completed mean |
|---:|---|---:|---:|---:|
| 1 ticks (0.02s) | `mean` | 0.810 | 0.04631 | 0.02245 |
| 1 ticks (0.02s) | `p95` | 0.814 | 0.10637 | 0.05031 |
| 1 ticks (0.02s) | `max` | 0.797 | 0.12128 | 0.05860 |
| 3 ticks (0.06s) | `mean` | 0.827 | 0.03103 | 0.02080 |
| 3 ticks (0.06s) | `p95` | 0.801 | 0.08464 | 0.05420 |
| 3 ticks (0.06s) | `max` | 0.818 | 0.12975 | 0.07433 |
| 5 ticks (0.10s) | `mean` | 0.749 | 0.03379 | 0.02756 |
| 5 ticks (0.10s) | `p95` | 0.736 | 0.09368 | 0.07701 |
| 5 ticks (0.10s) | `max` | 0.784 | 0.14323 | 0.10572 |
| 10 ticks (0.20s) | `mean` | 0.861 | 0.03679 | 0.02940 |
| 10 ticks (0.20s) | `p95` | 0.823 | 0.09689 | 0.07674 |
| 10 ticks (0.20s) | `max` | 0.870 | 0.16262 | 0.11403 |
| 20 ticks (0.40s) | `mean` | 0.840 | 0.03379 | 0.02750 |
| 20 ticks (0.40s) | `p95` | 0.844 | 0.08928 | 0.07080 |
| 20 ticks (0.40s) | `max` | 0.874 | 0.16408 | 0.11685 |

## Per-Seed First Window

Window: `10` ticks

| seed | failure | mean | p95 | max |
|---:|---:|---:|---:|---:|
| 40 | `False` | 0.02506 | 0.07446 | 0.09277 |
| 41 | `True` | 0.03522 | 0.09094 | 0.19533 |
| 42 | `True` | 0.03036 | 0.07781 | 0.19705 |
| 43 | `True` | 0.03698 | 0.08998 | 0.10181 |
| 44 | `True` | 0.03512 | 0.09354 | 0.14038 |
| 45 | `False` | 0.02428 | 0.05945 | 0.07966 |
| 46 | `False` | 0.02993 | 0.07711 | 0.14576 |
| 47 | `False` | 0.02788 | 0.07034 | 0.09621 |
| 48 | `True` | 0.03448 | 0.09822 | 0.20896 |
| 49 | `True` | 0.04086 | 0.10906 | 0.17817 |
| 50 | `False` | 0.03676 | 0.10184 | 0.17524 |
| 51 | `True` | 0.03633 | 0.08768 | 0.13087 |
| 52 | `False` | 0.02638 | 0.06504 | 0.09893 |
| 53 | `False` | 0.02706 | 0.08396 | 0.10966 |
| 54 | `False` | 0.03280 | 0.08182 | 0.11189 |
| 55 | `False` | 0.02791 | 0.07979 | 0.11503 |
| 56 | `False` | 0.02605 | 0.07260 | 0.10290 |
| 57 | `True` | 0.03274 | 0.08793 | 0.15362 |
| 58 | `True` | 0.03770 | 0.10753 | 0.14685 |
| 59 | `False` | 0.02953 | 0.07981 | 0.11943 |
| 60 | `False` | 0.02564 | 0.06209 | 0.12424 |
| 61 | `False` | 0.02950 | 0.06877 | 0.11255 |
| 62 | `False` | 0.02264 | 0.05584 | 0.06851 |
| 63 | `True` | 0.03095 | 0.07410 | 0.13456 |
| 64 | `False` | 0.02480 | 0.05639 | 0.07031 |
| 65 | `False` | 0.02750 | 0.07823 | 0.10242 |
| 66 | `False` | 0.02873 | 0.08265 | 0.12248 |
| 67 | `False` | 0.02703 | 0.07422 | 0.09198 |
| 68 | `False` | 0.04105 | 0.10312 | 0.12025 |
| 69 | `False` | 0.03124 | 0.06585 | 0.13993 |
| 70 | `False` | 0.04563 | 0.11816 | 0.19450 |
| 71 | `True` | 0.05388 | 0.14903 | 0.20125 |

## Interpretation

Teacher disagreement contains early failure information but is not a recovery target. No operating threshold is selected by this exploratory analysis.

## Limitations

- This is a held-out seed block relative to the frozen discovery metrics, but it contains few failure positives.
- AUC measures ranking, not calibrated probability or a safe threshold.
- Teacher disagreement can identify out-of-distribution states while still proposing unsafe actions.
