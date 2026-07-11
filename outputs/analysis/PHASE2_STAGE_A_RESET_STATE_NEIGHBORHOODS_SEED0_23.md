# Reset-State Neighborhood Analysis

status: `PASS_RESET_STATE_NEIGHBORHOOD_ANALYSIS_READY`

Offline saved-trace analysis only. No simulation, training, robot access,
deployment, GPU, or Colab allocation was performed by this analysis.

## Dataset

- resets: `24` (seeds 0-23)
- duration complete: `19`
- falls/terminations: `5`
- outcome counts: `{'fall_or_termination': 5, 'low_forward_progress': 8, 'pass': 2, 'tracking_hold': 9}`
- mean/median vx: `-0.02387` / `0.02136` m/s
- min/max vx: `-0.40780` / `0.05987` m/s

## Leave-One-Out Neighborhood Prediction

| predictor | RMSE (m/s) | Pearson | Spearman |
|---|---:|---:|---:|
| `global_mean` | 0.12087 | nan | nan |
| `knn_1` | 0.03245 | 0.967 | 0.832 |
| `knn_1_duration_complete_only` | 0.03119 | 0.698 | 0.734 |
| `knn_3` | 0.11665 | 0.339 | 0.503 |

## Target Seed 6 Neighborhood

Target outcome: `low_forward_progress`, vx `0.01138` m/s

| neighbor | distance | vx (m/s) | outcome |
|---:|---:|---:|---|
| 15 | 1.4913 | -0.00674 | `low_forward_progress` |
| 11 | 2.2740 | 0.03170 | `tracking_hold` |
| 16 | 2.3461 | -0.06963 | `low_forward_progress` |
| 7 | 2.4072 | 0.03579 | `tracking_hold` |
| 18 | 2.8267 | 0.05517 | `tracking_hold` |

## Closest Pair per Seed

| seed | vx | outcome | nearest seed | distance | nearest vx | nearest outcome |
|---:|---:|---|---:|---:|---:|---|
| 0 | 0.03460 | `tracking_hold` | 22 | 1.6101 | 0.03985 | `tracking_hold` |
| 1 | 0.02572 | `tracking_hold` | 23 | 0.9239 | -0.00673 | `low_forward_progress` |
| 2 | 0.05173 | `tracking_hold` | 5 | 1.3471 | 0.05828 | `tracking_hold` |
| 3 | -0.04549 | `low_forward_progress` | 23 | 1.1819 | -0.00673 | `low_forward_progress` |
| 4 | 0.05436 | `pass` | 17 | 0.7897 | 0.01701 | `low_forward_progress` |
| 5 | 0.05828 | `tracking_hold` | 10 | 0.8885 | 0.05987 | `pass` |
| 6 | 0.01138 | `low_forward_progress` | 15 | 1.4913 | -0.00674 | `low_forward_progress` |
| 7 | 0.03579 | `tracking_hold` | 18 | 1.6301 | 0.05517 | `tracking_hold` |
| 8 | 0.05648 | `tracking_hold` | 10 | 0.9494 | 0.05987 | `pass` |
| 9 | -0.40780 | `fall_or_termination` | 12 | 0.9009 | -0.38376 | `fall_or_termination` |
| 10 | 0.05987 | `pass` | 5 | 0.8885 | 0.05828 | `tracking_hold` |
| 11 | 0.03170 | `tracking_hold` | 18 | 1.5482 | 0.05517 | `tracking_hold` |
| 12 | -0.38376 | `fall_or_termination` | 9 | 0.9009 | -0.40780 | `fall_or_termination` |
| 13 | -0.08252 | `low_forward_progress` | 14 | 1.9239 | -0.06658 | `fall_or_termination` |
| 14 | -0.06658 | `fall_or_termination` | 13 | 1.9239 | -0.08252 | `low_forward_progress` |
| 15 | -0.00674 | `low_forward_progress` | 6 | 1.4913 | 0.01138 | `low_forward_progress` |
| 16 | -0.06963 | `low_forward_progress` | 11 | 1.6073 | 0.03170 | `tracking_hold` |
| 17 | 0.01701 | `low_forward_progress` | 22 | 0.6182 | 0.03985 | `tracking_hold` |
| 18 | 0.05517 | `tracking_hold` | 22 | 1.2808 | 0.03985 | `tracking_hold` |
| 19 | -0.08009 | `fall_or_termination` | 15 | 2.3329 | -0.00674 | `low_forward_progress` |
| 20 | 0.02973 | `fall_or_termination` | 11 | 3.0839 | 0.03170 | `tracking_hold` |
| 21 | 0.01469 | `low_forward_progress` | 17 | 1.3154 | 0.01701 | `low_forward_progress` |
| 22 | 0.03985 | `tracking_hold` | 17 | 0.6182 | 0.01701 | `low_forward_progress` |
| 23 | -0.00673 | `low_forward_progress` | 1 | 0.9239 | 0.02572 | `tracking_hold` |

## Interpretation

Nearby reset observations sometimes share sharply similar outcomes,
including the seed-6/15 low-progress neighborhood and seed-9/12 fall
neighborhood. The reset state is therefore behaviorally relevant. It is
not sufficient as a universal classifier: falls occupy multiple
neighborhoods and some close states have different gate outcomes.

The evidence supports reset-state robustness as the next problem, not a
global phase teacher or a deployment router. Temporal recovery trajectories
for each recurrent failure neighborhood are required before another
intervention can be specified.

## Limitations

- Nearest-neighbor association is not a causal recovery policy.
- One-second mean velocity from terminated traces is truncated by the fall.
- The teacher normalization weights observation dimensions according to its dataset, not an independently validated reset-state metric.
- Twenty-four resets remain too few to define a deployment or training router.
