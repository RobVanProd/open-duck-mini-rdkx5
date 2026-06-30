# Phase 2 Right-Swing Phase-Single-Support Result

status: `HOLD_RIGHT_SWING_PHASE_SINGLE_SUPPORT_RECIPE`

## Summary

The phase-primary single-support recipe trained and exported cleanly on a fresh
A100 Colab session. It did not produce a promotable candidate against the
corrected-bridge x=0.08 gate.

This was an offline-only run. No robot test, SSH, deploy, grounded replay, or
runtime behavior change was performed.

## Inputs

- Playground commit: `f2294eb` (`rewards: add phase single-support cost`)
- RDK commit: `d669d9a` (`chore: clean phase single-support recipe whitespace`)
- Colab session: `open-duck-a100-phase-single-support`
- Artifact bundle:
  `outputs/analysis/colab_cli/open-duck-a100-phase-single-support-phase2-right-swing-phase-single-support-20260630T221120Z/open_duck_colab_cli_phase2-right-swing-phase-single-support_20260630T221147Z_artifacts.tar.gz`
- Artifact sha256:
  `6f531eb27cd3bf62ad85d149117996fc7d2c44524ec6df10c8477279afd14aab`
- Corrected bridge:
  `outputs/analysis/actuator_response_fit_corrected_knee.json`
- Eval:
  `rough_terrain_backlash`, `x=0.08`, fitted bridge, z-scale `0.0024`,
  seeds `0-7`, CPU evaluator.

## Recipe

The recipe added a default-off phase-primary contact objective to penalize
commanded swing windows where the swing foot stayed planted and commanded
stance windows where the stance foot unloaded:

```text
forward_phase_single_support_scale: -0.004
forward_phase_single_support_swing_contact_weight: 1.0
forward_phase_single_support_stance_no_contact_weight: 2.0
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
| `2026_06_30_222327_40960.onnx` | `e5817dc7f4e3e89d55c2faf855d38c172273afbb6c4685ec430d9e395fe35a3d` |
| `2026_06_30_222609_81920.onnx` | `a613b6a923a56a4124557297e9418497bc4aa5adadf7ff794a4cd0c085bcaccb` |
| `2026_06_30_222630_122880.onnx` | `cafacac915603b92171367e68a52f3857a834f19c8228a237fc508c40ccd9345` |

## Gate Result

Artifact:
`outputs/analysis/phase2_right_swing_phase_single_support_a100_20260630/PHASE2_RIGHT_SWING_PHASE_SINGLE_SUPPORT_A100_X008_GATE.md`

| checkpoint | pass count | falls | duration complete | mean track ratio | mean vx | mean max-velocity excess | mean single support | mean double support |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `40960` | 1/8 | 0/8 | 8/8 | 0.2480 | 0.0198 m/s | 0.2681 rad/s | 14.5667% | 85.3833% |
| `81920` | 3/8 | 0/8 | 8/8 | 0.2532 | 0.0203 m/s | 0.2697 rad/s | 14.4167% | 85.5333% |
| `122880` | 0/8 | 0/8 | 8/8 | 0.2554 | 0.0204 m/s | 0.2046 rad/s | 14.9167% | 85.0333% |

All checkpoints stayed upright for the full duration, but none reached a robust
forward-walking distribution. The best pass count was `3/8` at checkpoint
`81920`, with the same low-progress / target-velocity split seen in the
phase-lift and phase-advance branches.

## Interpretation

Phase-primary single-support reward shaping did not solve the Phase 2
terrain/surface blocker. The policy remained near `0.020 m/s`, with mean track
ratio near `0.25`, double support near `85%`, and persistent per-seed corrected
target-velocity holds.

This closes the scalar phase-contact reward branch as a standalone fix. The
same pattern has now survived phase-lift, phase-advance, and phase-primary
single-support variants:

- no falls;
- full 15 s duration;
- low forward progress;
- local swing subchecks often pass;
- double support remains high, about `85%`;
- occasional corrected-envelope max target-velocity excess persists.

The next branch should not be another scalar reward tweak over the same
feed-forward student. It should move to a structural representation/oracle path:
canonical evaluator reconciliation, then a live-oracle DAgger or phase-aware
student that can preserve the working selector's state-conditioned swing/contact
transition without exceeding the corrected per-joint envelope.
