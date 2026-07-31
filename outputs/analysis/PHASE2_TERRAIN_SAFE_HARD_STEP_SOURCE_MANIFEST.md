# Phase 2 Terrain-Safe Hard-Step Source Manifest

status: `PASS_TERRAIN_SAFE_HARD_STEP_SOURCE_MANIFEST`

source_policy: `outputs/analysis/live_oracle_dagger_phase_student_iter0_candidate/candidate.onnx`
source_policy_sha256: `f3492159a775b0e0f73a25cf528b84ae202c16d5b2ba2f1344f7b7256e4e7261`

## Gate

- seeds: `[2, 4]`
- terrain_hfield_z_scale: `[0.001, 0.002]`
- min_mean_vx_m_s: `0.04`
- max_sent_velocity_p95_rad_s: `2.5`
- max_joint_tracking_p95_rad: `0.2`
- min_swing_segments_per_foot: `1`
- min_swing_rel_x_range_p95_m: `0.003`
- min_swing_peak_lift_m: `0.005`

## Curated Windows

| terrain_z | seed | start | end | mean_vx | sent_vel_p95 | tracking_p95 | single_support | double_support | min_swing_segments | min_rel_x_range | min_peak_lift | trace_sha256 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 0.001 | 2 | 80 | 180 | 0.0560 | 2.1892 | 0.1764 | 41.0 | 59.0 | 3 | 0.0085 | 0.0120 | `95016381c670` |
| 0.001 | 4 | 90 | 190 | 0.0493 | 1.9976 | 0.1714 | 39.0 | 61.0 | 3 | 0.0168 | 0.0112 | `15991cab24f2` |
| 0.002 | 2 | 60 | 160 | 0.0558 | 2.0902 | 0.1788 | 40.0 | 60.0 | 3 | 0.0098 | 0.0116 | `5d4b2efef4a4` |
| 0.002 | 4 | 140 | 240 | 0.0532 | 2.2194 | 0.1704 | 38.0 | 62.0 | 3 | 0.0156 | 0.0111 | `cf0c78200b30` |

## Interpretation

- These are terrain-safe source windows, not a deployable policy pass.
- The raw source policy still exceeds corrected velocity/tracking limits over the full rough-terrain rollout.
- Next action: build a terrain-window relabel/BC/DAgger pass from this manifest, then evaluate the resulting candidate with the full corrected terrain gate.
- No robot, SSH, deploy, grounded replay, runtime change, or training was performed.
