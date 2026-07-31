# Phase 2 Right-Swing Structural Result

status: `HOLD_RIGHT_SWING_STRUCTURAL_RECIPE`

## Summary

The right-swing structural recovery recipe trained and exported cleanly on the
A100 after fixing the Playground ONNX exporter. It did not produce a promotable
candidate against the corrected-bridge x=0.08 gate.

This was an offline-only run. No robot test, SSH, deploy, grounded replay, or
runtime behavior change was performed.

## Inputs

- Playground commit: `8c05631` (`fix: make compatibility ONNX export opt-in`)
- RDK commit: `a8b5abc`
- Colab session: `open-duck-a100-rightswing2`
- Artifact bundle:
  `outputs/analysis/colab_cli/open-duck-a100-rightswing2-phase2-right-swing-structural-20260630T172806Z/open_duck_colab_cli_phase2-right-swing-structural_20260630T172834Z_artifacts.tar.gz`
- Artifact sha256:
  `52e9c0e06f5e1fa18f3563fbd89207965b214edd7d42fd50c85dbcf2155c2ba7`
- Corrected bridge:
  `outputs/analysis/actuator_response_fit_corrected_knee.json`
- Eval:
  `rough_terrain_backlash`, `x=0.08`, fitted bridge, z-scale `0.0024`,
  seeds `0-7`, CPU evaluator.

## Exported Checkpoints

| checkpoint | sha256 |
|---|---|
| `2026_06_30_174042_40960.onnx` | `91510a2c82efe10bf3883dc6a3572e48bc217641e7fadefee2ec5258cad9703f` |
| `2026_06_30_174331_81920.onnx` | `da2ff79f997b896a089589d167f2b8f2ec1df9614fc8e431c5c0d231abac0755` |
| `2026_06_30_174353_122880.onnx` | `7d1b747cbd278aa287a8f107477b02c375cbdd9d9227d3259f30ee753ef4e267` |

## Gate Result

Artifact:
`outputs/analysis/phase2_right_swing_structural_a100_20260630/PHASE2_RIGHT_SWING_STRUCTURAL_A100_X008_GATE.md`

| checkpoint | pass count | falls | duration complete | mean track ratio | mean vx | mean max-velocity excess |
|---|---:|---:|---:|---:|---:|---:|
| `40960` | 0/8 | 0/8 | 8/8 | 0.2526 | 0.0202 m/s | 0.4066 rad/s |
| `81920` | 0/8 | 0/8 | 8/8 | 0.2490 | 0.0199 m/s | 0.5401 rad/s |
| `122880` | 1/8 | 0/8 | 8/8 | 0.2498 | 0.0200 m/s | 0.2807 rad/s |

The terrain swing subchecks were not the binding failure. The candidates
generally maintained swing segments, swing lift, and forward foot motion above
the local terrain thresholds, but failed the full candidate gate by either low
forward progress or corrected-envelope target-velocity excess.

## Interpretation

The right-swing target-rate penalty trained, exported, and reduced neither
branch of the tradeoff enough to clear the gate. It preserved stability but
left the policy too slow, while still producing nonzero max velocity excess on
most seeds.

This supports the prior diagnostic: the right-side swing issue is not solved by
a small scalar target-rate penalty on the current recipe. The next branch should
avoid another scalar penalty sweep and instead change the swing strategy itself,
for example longer swing timing or a knee-bend-first right swing that improves
vertical manipulability under the corrected right knee/ankle limits.
