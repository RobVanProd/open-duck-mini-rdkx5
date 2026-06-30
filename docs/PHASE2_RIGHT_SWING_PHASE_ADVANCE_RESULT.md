# Phase 2 Right-Swing Phase-Advance Result

status: `HOLD_RIGHT_SWING_PHASE_ADVANCE_RECIPE`

## Summary

The phase-advance recipe trained and exported cleanly on a fresh A100 Colab
session. It did not produce a promotable candidate against the corrected-bridge
x=0.08 gate.

This was an offline-only run. No robot test, SSH, deploy, grounded replay, or
runtime behavior change was performed.

## Inputs

- Playground commit: `9068192` (`rewards: add swing phase advance ticks`)
- RDK commit: `f78786b` (`tools: add right swing phase-advance workflow`)
- Colab session: `open-duck-a100-phase-advance`
- Artifact bundle:
  `outputs/analysis/colab_cli/open-duck-a100-phase-advance-phase2-right-swing-phase-advance-20260630T203817Z/open_duck_colab_cli_phase2-right-swing-phase-advance_20260630T203924Z_artifacts.tar.gz`
- Artifact sha256:
  `08169f9bad9b0279fe016a352e627e596d5cd25434055a4508267b230c931997`
- Corrected bridge:
  `outputs/analysis/actuator_response_fit_corrected_knee.json`
- Eval:
  `rough_terrain_backlash`, `x=0.08`, fitted bridge, z-scale `0.0024`,
  seeds `0-7`, CPU evaluator.

## Recipe

The recipe kept the phase-primary swing-lift branch and advanced the phase
window used by the swing-side lift/rate costs by the corrected actuator delay:

```text
forward_swing_phase_advance_ticks: 3
forward_phase_swing_lift_scale: -0.0006
forward_phase_swing_lift_target_m: 0.012
forward_swing_advance_scale: -0.001
forward_swing_advance_target_m: 0.004
right pitch-chain target-rate limits: 2.25, 2.75, 2.00 rad/s
```

The deployed policy/sim action contract and corrected per-joint bridge gate were
unchanged.

## Exported Checkpoints

| checkpoint | sha256 |
|---|---|
| `2026_06_30_205154_40960.onnx` | `28454c887b963c4939319bdc83a4a0032b75e8fbc336b4840738e802355b07d1` |
| `2026_06_30_205450_81920.onnx` | `3e50c3c87dbbd6f1b94c8cb8c1118781a88b4c8ce08fd7ea4cc942d7e2ba4d3b` |
| `2026_06_30_205511_122880.onnx` | `752916e306d4ecd96d0c5c4a3be57fd1ed4099d8a973e015ef4942c7c2edfb31` |

## Gate Result

Artifact:
`outputs/analysis/phase2_right_swing_phase_advance_a100_20260630/PHASE2_RIGHT_SWING_PHASE_ADVANCE_A100_X008_GATE.md`

| checkpoint | pass count | falls | duration complete | mean track ratio | mean vx | mean max-velocity excess |
|---|---:|---:|---:|---:|---:|---:|
| `40960` | 0/8 | 0/8 | 8/8 | 0.2494 | 0.0200 m/s | 0.2434 rad/s |
| `81920` | 3/8 | 0/8 | 8/8 | 0.2519 | 0.0202 m/s | 0.1131 rad/s |
| `122880` | 3/8 | 0/8 | 8/8 | 0.2510 | 0.0201 m/s | 0.0861 rad/s |

All checkpoints stayed upright for the full duration, but none reached a robust
forward-walking distribution. The best pass count was still `3/8`, matching the
phase-lift branch rather than improving it.

## Interpretation

Advancing the swing reward/rate window by the fitted 3-tick actuator delay did
not solve the Phase 2 terrain/surface blocker. It reduced mean max-velocity
excess at the late checkpoint, but mean speed stayed near `0.020 m/s` and mean
track ratio stayed near `0.25`.

The binding pattern is now consistent across the structural, phase-lift, and
phase-advance runs:

- no falls;
- full 15 s duration;
- low forward progress;
- local swing subchecks often pass;
- double support remains high, about `85%`;
- single support remains low, about `14-15%`;
- occasional corrected-envelope max target-velocity excess persists.

This closes the phase-advance timing branch as a standalone fix. The next
branch should not add another scalar swing penalty. It should change the swing
strategy/contact pattern while preserving the deployed runtime contract:

- right-leg knee-bend-first swing geometry within the corrected knee/ankle
  envelope;
- stronger contact-transition / single-support shaping only if it avoids
  envelope excess;
- a deployable phase-aware/live-oracle student if feed-forward reward shaping
  continues to preserve double support.
