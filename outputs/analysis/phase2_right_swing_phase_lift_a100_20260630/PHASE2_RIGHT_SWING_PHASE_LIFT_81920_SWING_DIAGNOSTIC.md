# Phase 2 Swing-Clearance Diagnostic

status: `PASS_SWING_CLEARANCE_DIAGNOSTIC_REPORTED`
aggregate_verdict: `LATENCY_LIMITED`
selected_fix_branch: phase-advance swing commands relative to the corrected 3-tick actuator delay
side_verdicts: `{'left': 'LATENCY_LIMITED', 'right': 'LATENCY_LIMITED'}`
rate_driver_joint_counts: `{'left_hip_pitch': 8, 'right_ankle': 7, 'right_knee': 1}`

## Scope

- Offline sim/analysis only.
- No robot, SSH, deploy, grounded replay, training, relabeling, or candidate modification.
- Swing segmentation is phase-primary; contact is reported only as the achieved outcome.

## Inputs

- candidate: `outputs/analysis/colab_cli/open-duck-a100-phase-lift-phase2-right-swing-phase-lift-20260630T185346Z/extracted/open_duck_colab_cli_phase2-right-swing-phase-lift_20260630T185443Z/open_duck_training_phase2_right_swing_phase_lift_cli/smoke_20260630T185805Z_gpu/2026_06_30_190949_81920.onnx`
- candidate_sha256: `10f6b35d697cc21646376544ecd5df799117bae531071f4e64f72b060bce8c1a`
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
| 0 | `PASS_SWING_CLEARANCE_ANALYZED` | `LATENCY_LIMITED` | `LATENCY_LIMITED` | 0.8181 | `left_hip_pitch` | 96.6480 | 0.4647 | `LATENCY_LIMITED` | 0.8926 | `right_ankle` | 93.3673 | 0.8794 |
| 1 | `PASS_SWING_CLEARANCE_ANALYZED` | `STRUCTURAL` | `LATENCY_LIMITED` | 0.9206 | `left_hip_pitch` | 92.4581 | 0.4185 | `STRUCTURAL` | 0.7690 | `right_knee` | 88.7755 | 2.7735 |
| 2 | `PASS_SWING_CLEARANCE_ANALYZED` | `LATENCY_LIMITED` | `LATENCY_LIMITED` | 0.7923 | `left_hip_pitch` | 96.9274 | 0.4021 | `LATENCY_LIMITED` | 0.7356 | `right_ankle` | 88.2653 | 0.5848 |
| 3 | `PASS_SWING_CLEARANCE_ANALYZED` | `STRUCTURAL` | `LATENCY_LIMITED` | 0.8130 | `left_hip_pitch` | 96.0894 | 0.4250 | `STRUCTURAL` | 0.7672 | `right_ankle` | 89.0306 | 2.5584 |
| 4 | `PASS_SWING_CLEARANCE_ANALYZED` | `LATENCY_LIMITED` | `LATENCY_LIMITED` | 0.8916 | `left_hip_pitch` | 93.5754 | 0.4528 | `LATENCY_LIMITED` | 0.7495 | `right_ankle` | 89.7959 | 0.5887 |
| 5 | `PASS_SWING_CLEARANCE_ANALYZED` | `LATENCY_LIMITED` | `LATENCY_LIMITED` | 0.8184 | `left_hip_pitch` | 94.9721 | 0.4201 | `LATENCY_LIMITED` | 0.8191 | `right_ankle` | 90.3061 | 0.5693 |
| 6 | `PASS_SWING_CLEARANCE_ANALYZED` | `LATENCY_LIMITED` | `LATENCY_LIMITED` | 0.8641 | `left_hip_pitch` | 94.4134 | 0.4439 | `LATENCY_LIMITED` | 0.7574 | `right_ankle` | 91.3265 | 0.5175 |
| 7 | `PASS_SWING_CLEARANCE_ANALYZED` | `STRUCTURAL` | `LATENCY_LIMITED` | 0.7974 | `left_hip_pitch` | 94.6927 | 0.4739 | `STRUCTURAL` | 0.7358 | `right_ankle` | 91.3265 | 1.3048 |

## Per-Seed Structural Reasons

| seed | left reasons | right reasons | right per-joint R peak |
|---:|---|---|---|
| 0 | `['planted_phase_swing_near_rate_limit']` | `['planted_phase_swing_near_rate_limit']` | `{'right_hip_pitch': 0.652158260345459, 'right_knee': 0.7072383707219904, 'right_ankle': 0.8925840258598328}` |
| 1 | `['planted_phase_swing_near_rate_limit']` | `['achieved_vertical_velocity_exceeds_in_envelope_ceiling']` | `{'right_hip_pitch': 0.6701615121629503, 'right_knee': 0.769010457125577, 'right_ankle': 0.7542550563812256}` |
| 2 | `[]` | `[]` | `{'right_hip_pitch': 0.6687906053331163, 'right_knee': 0.6687857887961648, 'right_ankle': 0.7356032729148865}` |
| 3 | `['planted_phase_swing_near_rate_limit']` | `['achieved_vertical_velocity_exceeds_in_envelope_ceiling']` | `{'right_hip_pitch': 0.6876667340596517, 'right_knee': 0.6960868835449219, 'right_ankle': 0.7672086358070374}` |
| 4 | `['planted_phase_swing_near_rate_limit']` | `[]` | `{'right_hip_pitch': 0.6920774777730306, 'right_knee': 0.6853385405106978, 'right_ankle': 0.7494598627090454}` |
| 5 | `['planted_phase_swing_near_rate_limit']` | `['planted_phase_swing_near_rate_limit']` | `{'right_hip_pitch': 0.7074303097195096, 'right_knee': 0.7611361416903409, 'right_ankle': 0.8190736174583435}` |
| 6 | `['planted_phase_swing_near_rate_limit']` | `[]` | `{'right_hip_pitch': 0.7496886783175998, 'right_knee': 0.6843068382956765, 'right_ankle': 0.7573708891868591}` |
| 7 | `[]` | `['achieved_vertical_velocity_exceeds_in_envelope_ceiling']` | `{'right_hip_pitch': 0.6768610742357042, 'right_knee': 0.6960348649458452, 'right_ankle': 0.7358178496360779}` |

## Interpretation

- Lift is commanded but achieved lift lags by the corrected actuator delay into or beyond the useful swing window. The next branch should phase-advance swing commands.

## Trace Collection

- trace_sweep_status: `PASS_TRACE_SWEEP`
- trace_dir: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/phase2_right_swing_phase_lift_a100_20260630/swing_clearance_trace_81920`
