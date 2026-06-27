# V11 Forward Reward Landscape

status: `SUMMARY_ONLY`

This file summarizes the offline scalar check produced by
`tools/analyze_forward_reward_landscape.py` for the V11 reward scales. The full
grid JSON is intentionally not committed because the conclusion is simple.

## Setup

```text
command_x: 0.08 m/s
dt: 0.02 s
tracking_sigma: 0.0009-0.001
tracking_lin_vel_scale: 42, 40, 36
forward_progress_scale: 18, 16, 14
forward_shortfall_scale: -36, -34, -30
forward_shortfall_required_ratio: 0.55, 0.50, 0.45
alive_scale checked: 0.02 and 20.0
```

The scalar check uses:

```text
tracking = exp(-square(command_x - local_vx) / tracking_sigma)
progress = clip(signed_local_vx / abs(command_x), 0, 1)
shortfall = square(max(abs(command_x) * required_ratio - signed_local_vx, 0) / abs(command_x))
scaled_total_no_alive =
  tracking * tracking_scale
  + progress * progress_scale
  + shortfall * shortfall_scale
```

## Key Result

For the intended V11 phase scales, zero velocity is worse than target-speed
motion in the scalar per-tick reward formula.

Example phase-1-like row:

```text
command_x: 0.08
tracking_sigma: 0.0009
tracking_scale: 42
progress_scale: 18
shortfall_scale: -36
required_ratio: 0.55

zero velocity:
  raw tracking: ~0.000816
  scaled total without alive: ~-10.856
  per-tick total without alive: ~-0.217

target velocity:
  raw tracking: 1.0
  progress: 1.0
  shortfall: 0.0
  scaled total without alive: 60.0
  per-tick total without alive: 1.2
```

So V11's no-motion result is not cleanly explained by one small shortfall
coefficient. The staged PPO task still found a stable no-motion basin despite a
scalar reward landscape that prefers forward progress.

## Interpretation

Treat V11 as a task-mechanics/optimization failure before launching another
coefficient-only training recipe.

The next experiment should make low-progress positive-command behavior invalid
at the episode/task level, for example through command-progress truncation or a
failure condition after warmup, and should add per-phase freeze detection before
later A100 phases run.
