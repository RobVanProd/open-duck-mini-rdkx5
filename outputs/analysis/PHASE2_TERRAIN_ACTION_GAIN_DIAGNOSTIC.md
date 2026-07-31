# Phase 2 Terrain Action-Gain Diagnostic

status: `HOLD_ACTION_GAIN_NOT_TERRAIN_FIX`

## Purpose

Test whether the C7 `z=0.002` terrain failure is a simple action-amplitude
problem. The diagnostic replays the same C7 checkpoint with small eval-only
policy action gains while keeping the corrected fitted bridge, terrain hfield,
and optional hard terrain swing gate active.

This does not modify the policy file, train, SSH, deploy, or touch the robot.

## Configuration

```text
policy:
  outputs/phase2_domain_randomization/stage_c7_terrain_z002_gate_selected_from_c3_gpu/smoke_20260628T132851Z_gpu/2026_06_28_093051_35120.onnx

task:
  rough_terrain_backlash

terrain_hfield_z_scale:
  0.002

bridge:
  fitted corrected knee

duration:
  5 s

seeds:
  2, 4

terrain swing thresholds:
  min_swing_segments_per_foot >= 1
  min_swing_rel_x_range_p95_m >= 0.003
  min_swing_peak_lift_m >= 0.005
```

Seed `2` was the earlier pass-like C7 trace. Seed `4` was the planted-foot
low-progress trace.

## Results

| gain | seed | status | track_ratio | max_vel_excess | max_tracking_p95 | min_swing_peak | min_swing_segments | min_rel_x_range_p95 | single_support | double_support |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.05 | 2 | `PASS_CANDIDATE_SIM_GATE` | 0.2969 | 0.0000 | 0.1708 | 0.0103 | 2 | 0.0062 | 12.8% | 87.2% |
| 1.05 | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.1209 | 0.0000 | 0.1415 | 0.0016 | 0 | 0.0000 | 0.8% | 99.2% |
| 1.10 | 2 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.2049 | 0.0000 | 0.1471 | 0.0073 | 1 | 0.0065 | 9.2% | 90.8% |
| 1.10 | 4 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0997 | 0.0000 | 0.1246 | 0.0015 | 0 | 0.0000 | 1.2% | 98.8% |

## Interpretation

Global output gain is not the carpet/terrain fix. Increasing action amplitude
does not violate the corrected envelope in this compact test, but it also does
not recover seed `4`: one foot remains effectively planted, swing excursion is
zero, and double support stays near `99%`.

Gain `1.10` also degrades the previously pass-like seed `2` into a low-progress
hold. The terrain blocker is therefore not simply "make the actions larger";
the next branch needs an alternating-step / higher-clearance target manifold or
a hard step-advance constraint that changes the stance-swing structure.

## Artifacts

```text
outputs/analysis/PHASE2_STAGE_C7_35120_GAIN105_TERRAIN_SWING_GATE_CPU.md
outputs/analysis/phase2_stage_c7_35120_gain105_terrain_swing_gate_cpu.json
outputs/analysis/PHASE2_STAGE_C7_35120_GAIN110_TERRAIN_SWING_GATE_CPU.md
outputs/analysis/phase2_stage_c7_35120_gain110_terrain_swing_gate_cpu.json
```

Hashes:

```text
da5a463241ec8c6678b0ea271940b7471a2177a42e7c956ca5971c117da56c24  outputs/analysis/phase2_stage_c7_35120_gain105_terrain_swing_gate_cpu.json
f746091ac5d4a3cdabc3fff232b870a55237d4c83361e30810bb4adf270fa2d2  outputs/analysis/phase2_stage_c7_35120_gain110_terrain_swing_gate_cpu.json
a6e90b8d7d3cc6708433fb618b4e0d6ba15f97dcdbae18515a6053e4c40a1b17  outputs/analysis/PHASE2_STAGE_C7_35120_GAIN105_TERRAIN_SWING_GATE_CPU.md
14eecb8e6cefb41e4b437a285157799df0f009497fa9cab034193d8dbe8155d6  outputs/analysis/PHASE2_STAGE_C7_35120_GAIN110_TERRAIN_SWING_GATE_CPU.md
```
