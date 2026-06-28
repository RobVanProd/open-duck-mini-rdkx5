# Phase 2 Stage C9 Swing-Advance Decision

status: `HOLD_STAGE_C9_SWING_ADVANCE_RETREATS_TO_LOW_PROGRESS`

## Purpose

C9 tested the new default-off `forward_swing_advance` hook as a direct
step-advance pressure on the C7 terrain lineage. The goal was to see whether
penalizing a touchdown after insufficient forward foot advance could recover
the planted-foot terrain failure without exceeding the corrected actuator
envelope.

No robot, SSH, deploy, or grounded replay was performed.

## Training

```text
output:
  outputs/phase2_domain_randomization/stage_c9_terrain_z002_swing_advance_from_c7_gpu/smoke_20260628T152931Z_gpu

status:
  PASS_SMOKE_RUN

platform:
  local GPU / ROCm

warm start:
  outputs/phase2_domain_randomization/stage_c7_terrain_z002_gate_selected_from_c3_gpu/smoke_20260628T132851Z_gpu/2026_06_28_093051_35120

task:
  rough_terrain_backlash

terrain_hfield_z_scale:
  0.002

num_timesteps:
  81920

exported checkpoints:
  0
  27360
  54720
  82080
```

Recipe changes relative to C7:

```text
forward_swing_advance_scale: -0.01
forward_swing_advance_target_m: 0.005
forward_swing_advance_huber_delta: 0.002
```

The existing C7 terrain/contact settings were otherwise preserved.

## Screen

```text
report:
  outputs/analysis/PHASE2_STAGE_C9_TERRAIN_Z002_SCREEN_CPU.md

json:
  outputs/analysis/phase2_stage_c9_terrain_z002_screen_cpu.json

seeds:
  2, 4

duration:
  5 s

terrain swing gate:
  min_swing_segments_per_foot >= 1
  min_swing_rel_x_range_p95_m >= 0.003
  min_swing_peak_lift_m >= 0.005
```

| checkpoint | seed 2 status | seed 2 track ratio | seed 2 min swing segments | seed 4 status | seed 4 track ratio | seed 4 min swing segments |
|---|---|---:|---:|---|---:|---:|
| c9_0 | `PASS_CANDIDATE_SIM_GATE` | 0.3577 | 3 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1918 | 0 |
| c9_27360 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1713 | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1012 | 0 |
| c9_54720 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1125 | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0735 | 0 |
| c9_82080 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1959 | 1 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0964 | 0 |

All screened checkpoints preserved corrected-envelope compliance:

```text
max velocity excess: 0.0000 rad/s
falls: 0/8 screened rollouts
```

## Interpretation

The hook is useful plumbing, but this scalar setting does not fix the terrain
failure. Training with `forward_swing_advance_scale=-0.01` reduced the
pass-like seed's forward progress and did not recover the planted-foot seed.
Seed 4 remained at zero minimum swing segments for every checkpoint and stayed
near-total double support.

Do not promote C9. Do not simply increase scalar swing-advance pressure. The
terrain/carpet blocker is now consistently a target-manifold problem: the next
branch needs a higher-clearance alternating-step demonstration or a hard
step-advance constraint that preserves commanded forward motion while requiring
both feet to swing.
