# Phase 2 Stage C3 Contact-Timing Decision

status: `HOLD_STAGE_C3_CONTACT_TIMING_NOT_ENOUGH`

## Scope

Offline sim only. No robot, SSH, deploy, grounded replay, or runtime behavior
change was performed.

## Recipe

C3 was a narrow fine-tune from the best C2 checkpoint:

```text
warm-start:
  outputs/phase2_domain_randomization/stage_c2_terrain_z002_targetrate_from_c1_gpu/smoke_20260628T113221Z_gpu/2026_06_28_073829_163840

task:
  rough_terrain_backlash

terrain_hfield_z_scale:
  0.002

added contact timing pressure:
  forward_single_support_scale: 0.15
  forward_double_support_dwell_scale: -0.05
  forward_double_support_dwell_grace_steps: 8
  forward_contact_transition_scale: 0.10
  forward_contact_transition_min_progress_ratio: 0.25

bridge:
  corrected fitted actuator bridge
```

Training completed successfully:

```text
artifact:
  outputs/phase2_domain_randomization/stage_c3_terrain_z002_contact_from_c2_gpu/smoke_20260628T121159Z_gpu

status:
  PASS_SMOKE_RUN

elapsed_s:
  421.11

terrain XML restored:
  true
```

## Screen

Screen artifact:

```text
outputs/analysis/PHASE2_STAGE_C3_TERRAIN_Z002_SCREEN_CPU.md
outputs/analysis/phase2_stage_c3_terrain_z002_screen_cpu.json
```

Configuration:

```text
command_x: 0.08
task: rough_terrain_backlash
terrain_hfield_z_scale: 0.002
seed: 0
duration: 5 s
bridge_mode: fitted
platform: CPU evaluator
```

## Result

| policy | tracking p95 | track ratio | min swing peak | single support | double support |
|---|---:|---:|---:|---:|---:|
| `c3_0` | 0.2044 | 0.3866 | 0.0163 m | 17.2% | 82.8% |
| `c3_81920` | 0.2021 | 0.3923 | 0.0149 m | 17.2% | 82.8% |
| `c3_163840` | 0.2034 | 0.3353 | 0.0163 m | 16.8% | 83.2% |
| `c3_245760` | 0.2046 | 0.4061 | 0.0165 m | 20.8% | 79.2% |

Best support-timing result:

```text
policy:
  c3_245760

onnx:
  outputs/phase2_domain_randomization/stage_c3_terrain_z002_contact_from_c2_gpu/smoke_20260628T121159Z_gpu/2026_06_28_081839_245760.onnx

seed 0:
  status: HOLD_CANDIDATE_TRACKING
  tracking p95: 0.2046 rad
  track ratio: 0.4061
  velocity excess: 0.0000 rad/s
  single support: 20.8%
  double support: 79.2%
```

Per-foot details for `c3_245760`:

```text
left contact: 94.0%, swing samples: 15, peak lift: 0.0197 m
right contact: 85.2%, swing samples: 37, peak lift: 0.0165 m
```

## Interpretation

C3 moved support timing in the intended direction but did not solve terrain
clearance or strict tracking:

- single support improved from about `17%` to `20.8%`,
- double support decreased from about `83%` to `79.2%`,
- track ratio improved to `0.4061`,
- corrected velocity-envelope excess stayed at `0.0000 rad/s`,
- but tracking p95 stayed above the strict `0.20 rad` gate,
- and minimum swing peak lift stayed only about `1.6 cm`.

Contact-timing reward alone is not enough. The next terrain stage needs an
explicit clearance-height objective or target-source change that raises swing
height while preserving the in-envelope gait and command conditioning.
