# Relabelled Balanced Selector Manifest

status: `PASS_BALANCED_SELECTOR_SOURCE_READY`

This manifest points to existing BEST_WALK windows and marks relabeled left-stance windows. It does not copy raw samples, train, step simulation, deploy, SSH, run robot tests, or change runtime behavior.

## Filters

- window_samples: `10`
- stride_samples: `2`
- envelope_high: `3.75`
- right_knee_cap: `3.61`
- min_entries: `100`
- min_phase_bins: `6`

## Coverage

- entries: `672`
- covered_phase_bins: `[0, 1, 2, 3, 4, 5, 6, 7]`
- covered_phase_bin_count: `8` / `8`

### By Stance Side

- left_stance: `273`
- double: `264`
- right_stance: `135`

### By Relabel Mode

- right_knee_rate_cap: `343`
- none: `329`

## Interpretation

- Passing this manifest means the source has enough left/right stance and phase coverage to prototype a selector replay.
- It still has not been stepped in sim and is not training-ready by itself.
- The next required artifact is a 25-50 tick continuity/replay score using these entries.
