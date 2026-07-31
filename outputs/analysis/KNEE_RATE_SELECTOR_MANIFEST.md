# Knee-Rate-Aware Closed-Loop Selector Manifest

status: `HOLD_SELECTOR_MISSING_STANCE_SIDE`

This manifest points to existing BEST_WALK full-observation windows. It does not copy raw samples, train, deploy, SSH, run robot tests, or change runtime behavior.

## Filters

- window_samples: `10`
- stride_samples: `2`
- envelope_high: `3.75`
- max_right_knee_p95: `3.61`
- min_mean_vx: `0.04`
- min_single_support_pct: `20.0`
- min_moving_in_envelope_pct: `40.0`
- min_moving_single_in_envelope_pct: `10.0`

## Coverage

- entries: `313`
- covered_phase_bins: `[1, 2, 3, 4, 5]`
- covered_phase_bin_count: `5` / `8`

### By Stance Side

- double: `178`
- right_stance: `135`

### By Command Cell

| command_cell | left_stance | right_stance | double | other |
|---|---:|---:|---:|---:|
| straight_x004 | 0 | 0 | 5 | 0 |
| straight_x008 | 0 | 54 | 141 | 0 |
| turning_x0074_yneg0037_yawneg0074 | 0 | 81 | 32 | 0 |

## Interpretation

- The source is not balanced enough for selector training: at least one stance side is missing.
- Do not train from this manifest. Investigate why safe BEST_WALK windows collapse to one stance side plus double support.
- The next branch should either recover the missing stance side or use a different closed-loop mechanism source.
