# Policy vs Behavior Prior

status: `PASS_POLICY_TEACHER_CLOSE`

Offline comparison only. No training, SSH, deploy, robot test, or runtime
behavior change was performed.

## Inputs

- manifest: `outputs/analysis/phase2_stage_a_rate175_step163840_x008_seed0_fullobs_manifest.json`
- behavior prior NPZ: `outputs/analysis/command_conditioned_hard_seed_recovery_dagger_seed5_x0_rate175_candidate/candidate_mlp.npz`
- samples: `50`

## Policy Summary

| policy | teacher L1 mean | teacher L1 p95 | manifest L1 p95 | action abs p95 | saturation % |
|---|---:|---:|---:|---:|---:|
| `candidate` | 0.0000 | 0.0000 | 0.0524 | 0.7622 | 0.00 |
| `2026_07_11_021603_163840` | 0.0197 | 0.0524 | 0.0000 | 0.7698 | 0.00 |

## Teacher Delta By Joint

| policy | joint | mean | p95 | max |
|---|---|---:|---:|---:|
| `candidate` | `right_ankle` | 0.0000 | 0.0000 | 0.0000 |
| `candidate` | `right_hip_pitch` | 0.0000 | 0.0000 | 0.0000 |
| `candidate` | `left_hip_pitch` | 0.0000 | 0.0000 | 0.0000 |
| `candidate` | `neck_pitch` | 0.0000 | 0.0000 | 0.0000 |
| `candidate` | `left_ankle` | 0.0000 | 0.0000 | 0.0000 |
| `candidate` | `right_hip_roll` | 0.0000 | 0.0000 | 0.0000 |
| `candidate` | `head_yaw` | 0.0000 | 0.0000 | 0.0000 |
| `candidate` | `left_hip_roll` | 0.0000 | 0.0000 | 0.0000 |
| `candidate` | `left_knee` | 0.0000 | 0.0000 | 0.0000 |
| `candidate` | `head_pitch` | 0.0000 | 0.0000 | 0.0000 |
| `candidate` | `left_hip_yaw` | 0.0000 | 0.0000 | 0.0000 |
| `candidate` | `right_knee` | 0.0000 | 0.0000 | 0.0000 |
| `candidate` | `right_hip_yaw` | 0.0000 | 0.0000 | 0.0000 |
| `candidate` | `head_roll` | 0.0000 | 0.0000 | 0.0000 |
| `2026_07_11_021603_163840` | `left_knee` | 0.0253 | 0.0632 | 0.0718 |
| `2026_07_11_021603_163840` | `right_knee` | 0.0215 | 0.0603 | 0.0859 |
| `2026_07_11_021603_163840` | `left_hip_roll` | 0.0267 | 0.0580 | 0.1051 |
| `2026_07_11_021603_163840` | `left_ankle` | 0.0281 | 0.0562 | 0.1107 |
| `2026_07_11_021603_163840` | `right_ankle` | 0.0231 | 0.0510 | 0.0607 |
| `2026_07_11_021603_163840` | `head_yaw` | 0.0213 | 0.0503 | 0.0624 |
| `2026_07_11_021603_163840` | `right_hip_roll` | 0.0201 | 0.0452 | 0.0562 |
| `2026_07_11_021603_163840` | `left_hip_pitch` | 0.0197 | 0.0443 | 0.0625 |
| `2026_07_11_021603_163840` | `right_hip_pitch` | 0.0143 | 0.0426 | 0.0812 |
| `2026_07_11_021603_163840` | `head_pitch` | 0.0198 | 0.0407 | 0.0593 |
| `2026_07_11_021603_163840` | `right_hip_yaw` | 0.0154 | 0.0398 | 0.0568 |
| `2026_07_11_021603_163840` | `head_roll` | 0.0145 | 0.0303 | 0.0528 |
| `2026_07_11_021603_163840` | `neck_pitch` | 0.0126 | 0.0285 | 0.0312 |
| `2026_07_11_021603_163840` | `left_hip_yaw` | 0.0125 | 0.0264 | 0.0399 |

## Interpretation

The compared policies remain close to the behavior-prior teacher on the teacher dataset; gate regression is more likely closed-loop instability than offline teacher mismatch.
