# Phase 2 Swing-Clearance Diagnostic

status: `PASS_SWING_CLEARANCE_DIAGNOSTIC_REPORTED`
aggregate_verdict: `MIXED_LEG_MODES`
selected_fix_branch: split fix: structural leg needs gait/geometry or longer swing duration; latency-limited leg may need phase advance
side_verdicts: `{'left': 'LATENCY_LIMITED', 'right': 'STRUCTURAL'}`
rate_driver_joint_counts: `{'left_hip_pitch': 2, 'right_ankle': 7, 'left_ankle': 5, 'left_knee': 1, 'right_knee': 1}`

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

| seed | status | aggregate | left class | left R | left driver | left planted | left achieved/ceiling | right class | right R | right driver | right planted | right achieved/ceiling |
|---:|---|---|---|---:|---|---:|---:|---|---:|---|---:|---:|
| 0 | `PASS_SWING_CLEARANCE_ANALYZED` | `STRUCTURAL` | `LATENCY_LIMITED` | 0.9594 | `left_hip_pitch` | 83.5196 | 0.3808 | `STRUCTURAL` | 1.3246 | `right_ankle` | 91.3265 | 0.8319 |
| 1 | `PASS_SWING_CLEARANCE_ANALYZED` | `STRUCTURAL` | `LATENCY_LIMITED` | 0.9750 | `left_ankle` | 83.2402 | 0.3729 | `STRUCTURAL` | 1.3463 | `right_ankle` | 92.3469 | 2.7066 |
| 2 | `PASS_SWING_CLEARANCE_ANALYZED` | `STRUCTURAL` | `LATENCY_LIMITED` | 0.9918 | `left_ankle` | 83.2402 | 0.4230 | `STRUCTURAL` | 1.1546 | `right_ankle` | 93.1122 | 0.5121 |
| 3 | `PASS_SWING_CLEARANCE_ANALYZED` | `STRUCTURAL` | `LATENCY_LIMITED` | 0.9602 | `left_ankle` | 83.5196 | 0.3924 | `STRUCTURAL` | 1.7950 | `right_ankle` | 92.0918 | 2.5368 |
| 4 | `PASS_SWING_CLEARANCE_ANALYZED` | `STRUCTURAL` | `LATENCY_LIMITED` | 0.9304 | `left_ankle` | 84.6369 | 0.4077 | `STRUCTURAL` | 1.2254 | `right_ankle` | 90.8163 | 0.5117 |
| 5 | `PASS_SWING_CLEARANCE_ANALYZED` | `STRUCTURAL` | `LATENCY_LIMITED` | 0.9579 | `left_ankle` | 87.9888 | 0.3735 | `STRUCTURAL` | 1.1713 | `right_ankle` | 91.0714 | 0.5280 |
| 6 | `PASS_SWING_CLEARANCE_ANALYZED` | `STRUCTURAL` | `STRUCTURAL` | 1.1583 | `left_hip_pitch` | 83.5196 | 0.3577 | `STRUCTURAL` | 1.7789 | `right_ankle` | 90.8163 | 0.5047 |
| 7 | `PASS_SWING_CLEARANCE_ANALYZED` | `STRUCTURAL` | `STRUCTURAL` | 1.2813 | `left_knee` | 86.5922 | 0.4193 | `STRUCTURAL` | 1.2261 | `right_knee` | 91.3265 | 1.2614 |

## Per-Seed Structural Reasons

| seed | left reasons | right reasons | right per-joint R peak |
|---:|---|---|---|
| 0 | `['planted_phase_swing_near_rate_limit']` | `['rate_utilization_exceeds_corrected_limit', 'planted_phase_swing_near_rate_limit']` | `{'right_hip_pitch': 1.0534697108798556, 'right_knee': 0.9893092242154208, 'right_ankle': 1.3246089220046997}` |
| 1 | `['planted_phase_swing_near_rate_limit']` | `['rate_utilization_exceeds_corrected_limit', 'achieved_vertical_velocity_exceeds_in_envelope_ceiling', 'planted_phase_swing_near_rate_limit']` | `{'right_hip_pitch': 1.150642500983344, 'right_knee': 1.0328639637340198, 'right_ankle': 1.346305012702942}` |
| 2 | `['planted_phase_swing_near_rate_limit']` | `['rate_utilization_exceeds_corrected_limit', 'planted_phase_swing_near_rate_limit']` | `{'right_hip_pitch': 0.9767399893866645, 'right_knee': 1.0024417530406604, 'right_ankle': 1.1546090245246887}` |
| 3 | `['planted_phase_swing_near_rate_limit']` | `['rate_utilization_exceeds_corrected_limit', 'achieved_vertical_velocity_exceeds_in_envelope_ceiling', 'planted_phase_swing_near_rate_limit']` | `{'right_hip_pitch': 1.0256568590799968, 'right_knee': 1.0027842088179155, 'right_ankle': 1.7949730157852173}` |
| 4 | `['planted_phase_swing_near_rate_limit']` | `['rate_utilization_exceeds_corrected_limit', 'planted_phase_swing_near_rate_limit']` | `{'right_hip_pitch': 1.0573612319098578, 'right_knee': 1.0502858595414595, 'right_ankle': 1.2253910303115845}` |
| 5 | `['planted_phase_swing_near_rate_limit']` | `['rate_utilization_exceeds_corrected_limit', 'planted_phase_swing_near_rate_limit']` | `{'right_hip_pitch': 0.9793877601623535, 'right_knee': 1.0119199752807617, 'right_ankle': 1.1712700128555298}` |
| 6 | `['rate_utilization_exceeds_corrected_limit', 'planted_phase_swing_near_rate_limit']` | `['rate_utilization_exceeds_corrected_limit', 'planted_phase_swing_near_rate_limit']` | `{'right_hip_pitch': 1.5106929673088922, 'right_knee': 1.0368932377208362, 'right_ankle': 1.778876781463623}` |
| 7 | `['rate_utilization_exceeds_corrected_limit', 'planted_phase_swing_near_rate_limit']` | `['rate_utilization_exceeds_corrected_limit', 'achieved_vertical_velocity_exceeds_in_envelope_ceiling', 'planted_phase_swing_near_rate_limit']` | `{'right_hip_pitch': 1.1897338761223688, 'right_knee': 1.226065375588157, 'right_ankle': 1.168590784072876}` |

## Interpretation

- The legs have different limiting modes. The structural leg is over the corrected envelope and must not be treated as a pure latency problem; the latency-limited leg may still benefit from phase advance.

## Trace Collection

- trace_sweep_status: `PASS_EXISTING_TRACES_USED`
- trace_dir: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_swing_clearance_trace_x008_z0024`
