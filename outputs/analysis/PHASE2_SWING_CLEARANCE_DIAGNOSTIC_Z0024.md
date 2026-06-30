# Phase 2 Swing-Clearance Diagnostic

status: `PASS_SWING_CLEARANCE_DIAGNOSTIC_REPORTED`
aggregate_verdict: `LATENCY_LIMITED`
selected_fix_branch: phase-advance swing commands relative to the corrected 3-tick actuator delay

## Scope

- Offline sim/analysis only.
- No robot, SSH, deploy, grounded replay, training, relabeling, or candidate modification.
- Swing segmentation is phase-primary; contact is reported only as the achieved outcome.

## Inputs

- candidate: `policy/candidates/phase2_stagea2_seed5_recovery_command_gated_gain099_20260629/candidate.onnx`
- candidate_sha256: `209b85a75cf9cbbcf10df573c1b530921943a72e81082111889c15f63a9a2c7b`
- corrected_bridge: `outputs/analysis/actuator_response_fit_corrected_knee.json`
- corrected_bridge_sha256: `3661543d0745073b561eb4fa2ae8f9616368ee8b72cb397f8b953dada532c8c0`
- command_x: `0.08`
- task: `rough_terrain_backlash`
- terrain_hfield_z_scale: `0.0024`
- seeds: `[0, 1, 2, 3, 4, 5, 6, 7]`

## Audit

- MJCF: `/home/lsd/robots/Open_Duck_Playground/playground/open_duck_mini_v2/xmls/scene_rough_terrain_backlash.xml`
- nq/nv/nu: `31/30/14`
- foot sites: `{'left': {'site_name': 'left_foot', 'site_id': 2, 'body_id': 7, 'body_name': 'foot_assembly'}, 'right': {'site_name': 'right_foot', 'site_id': 4, 'body_id': 16, 'body_name': 'foot_assembly_2'}}`
- pitch-chain dof indices: `{'left_hip_pitch': 10, 'left_knee': 12, 'left_ankle': 14, 'right_hip_pitch': 24, 'right_knee': 26, 'right_ankle': 28}`
- backlash joints present: `True`
- phase convention: `phase01=atan2(obs[100], obs[99])/(2*pi); phase<0.5 is left stance/right swing, phase>=0.5 is right stance/left swing`

## Corrected Limits

| joint | limit_rad_s |
|---|---:|
| `left_hip_pitch` | 2.5000 |
| `left_knee` | 3.2500 |
| `left_ankle` | 2.7500 |
| `right_hip_pitch` | 2.2500 |
| `right_knee` | 2.7500 |
| `right_ankle` | 2.0000 |

## Per-Seed Classification

| seed | status | aggregate | left class | left R | left planted | left ceiling | left achieved/ceiling | right class | right R | right planted | right ceiling | right achieved/ceiling |
|---:|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| 0 | `PASS_SWING_CLEARANCE_ANALYZED` | `LATENCY_LIMITED` | `LATENCY_LIMITED` | 0.9594 | 83.5196 | 0.2284 | 0.3808 | `STRUCTURAL` | 1.3246 | 91.3265 | 0.1980 | 0.8319 |
| 1 | `PASS_SWING_CLEARANCE_ANALYZED` | `LATENCY_LIMITED` | `LATENCY_LIMITED` | 0.9750 | 83.2402 | 0.2007 | 0.3729 | `LATENCY_LIMITED` | 1.3463 | 92.3469 | 0.1751 | 2.7066 |
| 2 | `PASS_SWING_CLEARANCE_ANALYZED` | `LATENCY_LIMITED` | `LATENCY_LIMITED` | 0.9918 | 83.2402 | 0.2001 | 0.4230 | `LATENCY_LIMITED` | 1.1546 | 93.1122 | 0.2993 | 0.5121 |
| 3 | `PASS_SWING_CLEARANCE_ANALYZED` | `LATENCY_LIMITED` | `LATENCY_LIMITED` | 0.9602 | 83.5196 | 0.2489 | 0.3924 | `LATENCY_LIMITED` | 1.7950 | 92.0918 | 0.1932 | 2.5368 |
| 4 | `PASS_SWING_CLEARANCE_ANALYZED` | `LATENCY_LIMITED` | `LATENCY_LIMITED` | 0.9304 | 84.6369 | 0.2344 | 0.4077 | `LATENCY_LIMITED` | 1.2254 | 90.8163 | 0.2407 | 0.5117 |
| 5 | `PASS_SWING_CLEARANCE_ANALYZED` | `LATENCY_LIMITED` | `LATENCY_LIMITED` | 0.9579 | 87.9888 | 0.3429 | 0.3735 | `LATENCY_LIMITED` | 1.1713 | 91.0714 | 0.5460 | 0.5280 |
| 6 | `PASS_SWING_CLEARANCE_ANALYZED` | `LATENCY_LIMITED` | `LATENCY_LIMITED` | 1.1583 | 83.5196 | 0.1992 | 0.3577 | `LATENCY_LIMITED` | 1.7789 | 90.8163 | 0.4248 | 0.5047 |
| 7 | `PASS_SWING_CLEARANCE_ANALYZED` | `LATENCY_LIMITED` | `LATENCY_LIMITED` | 1.2813 | 86.5922 | 0.2007 | 0.4193 | `LATENCY_LIMITED` | 1.2261 | 91.3265 | 0.1716 | 1.2614 |

## Interpretation

- Lift is commanded but achieved lift lags by the corrected actuator delay into or beyond the useful swing window. The next branch should phase-advance swing commands.

## Trace Collection

- trace_sweep_status: `PASS_EXISTING_TRACES_USED`
- trace_dir: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_swing_clearance_trace_x008_z0024`
