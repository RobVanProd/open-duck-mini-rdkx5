# Policy Command Sensitivity

Offline ONNX probe using a synthetic upright observation. This report
does not run MuJoCo, train, SSH, deploy, or touch the robot.

The purpose is to separate command insensitivity from closed-loop
locomotion failure. A policy can react to `obs[6]` and still fail to
produce useful forward motion in sim.

## Summary

| policy | status | action dim | base norm | x=0.08 delta L2 | x=0.08 delta max | x=0.08 action max | x=0.08 sat % |
|---|---|---:|---:|---:|---:|---:|---:|
| `best` | `PASS_COMMAND_SENSITIVITY_ANALYSIS` | 14 | 1.0008 | 0.2709 | 0.1380 | 0.6016 | 0.0000 |
| `forward_mild_bridge_push` | `PASS_COMMAND_SENSITIVITY_ANALYSIS` | 14 | 3.0054 | 0.4228 | 0.3247 | 0.9890 | 14.2857 |
| `forward_mid_bridge_steady` | `PASS_COMMAND_SENSITIVITY_ANALYSIS` | 14 | 2.1137 | 0.4357 | 0.2982 | 0.8911 | 0.0000 |
| `forward_imitation_bridge_steady` | `PASS_COMMAND_SENSITIVITY_ANALYSIS` | 14 | 2.3180 | 0.4717 | 0.2326 | 0.9404 | 0.0000 |
| `forward_moderated_no_bridge` | `PASS_COMMAND_SENSITIVITY_ANALYSIS` | 14 | 2.4016 | 0.3819 | 0.2928 | 0.9711 | 0.0000 |

## Top x=0.08 Action Changes

### best

- status: `PASS_COMMAND_SENSITIVITY_ANALYSIS`
- path: `/home/lsd/robots/open-duck-mini-rdkx5/policy/BEST_WALK_ONNX_2.onnx`
- sha256: `3c606f9381a1710cc8fecdb7442787dcbfce3ee9bc02a6f1224774ab2b3a1067`

| joint | index | action@0 | action@0.08 | delta |
|---|---:|---:|---:|---:|
| `left_hip_yaw` | 0 | -0.0160 | 0.1220 | 0.1380 |
| `left_hip_pitch` | 2 | -0.2993 | -0.3958 | -0.0965 |
| `left_knee` | 3 | -0.1434 | -0.2346 | -0.0912 |
| `right_ankle` | 13 | -0.0583 | 0.0254 | 0.0838 |
| `left_ankle` | 4 | 0.3844 | 0.4642 | 0.0798 |
| `left_hip_roll` | 1 | 0.2712 | 0.1923 | -0.0789 |

### forward_mild_bridge_push

- status: `PASS_COMMAND_SENSITIVITY_ANALYSIS`
- path: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/colab_cli/open-duck-l4i-candidate-only-20260623T040647Z/recovered/open_duck_colab_cli_candidate-only_20260623T040701Z/open_duck_training_runs_cli/smoke_20260623T034037Z_gpu/2026_06_23_035336_430080.onnx`
- sha256: `47a65976cecebbfba217b6f9638b737b25bd1b6217044ee041d24fd89edd9444`

| joint | index | action@0 | action@0.08 | delta |
|---|---:|---:|---:|---:|
| `right_hip_yaw` | 9 | -0.6024 | -0.2777 | 0.3247 |
| `left_knee` | 3 | -0.5379 | -0.3250 | 0.2129 |
| `head_pitch` | 6 | -0.7569 | -0.6264 | 0.1305 |
| `head_roll` | 8 | -0.1736 | -0.2427 | -0.0691 |
| `head_yaw` | 7 | -0.8509 | -0.9080 | -0.0570 |
| `right_hip_roll` | 10 | -0.3445 | -0.3099 | 0.0346 |

### forward_mid_bridge_steady

- status: `PASS_COMMAND_SENSITIVITY_ANALYSIS`
- path: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/colab_cli/open-duck-l4i-candidate-only-20260623T040647Z/recovered/open_duck_colab_cli_candidate-only_20260623T040701Z/open_duck_training_runs_cli/smoke_20260623T040716Z_gpu/2026_06_23_041921_430080.onnx`
- sha256: `1e89b5ea8845659d7434294af145e14d272a2331dc5f13282eb1a15753926866`

| joint | index | action@0 | action@0.08 | delta |
|---|---:|---:|---:|---:|
| `head_yaw` | 7 | -0.2362 | -0.5345 | -0.2982 |
| `head_pitch` | 6 | -0.3308 | -0.5568 | -0.2260 |
| `right_hip_yaw` | 9 | -0.1133 | 0.0508 | 0.1641 |
| `left_hip_pitch` | 2 | 0.7495 | 0.8378 | 0.0884 |
| `head_roll` | 8 | -0.1681 | -0.0804 | 0.0878 |
| `left_hip_yaw` | 0 | -0.2578 | -0.2113 | 0.0465 |

### forward_imitation_bridge_steady

- status: `PASS_COMMAND_SENSITIVITY_ANALYSIS`
- path: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/colab_cli/open-duck-l4j-candidate-only-20260623T043228Z/partial_extract/open_duck_colab_cli_candidate-only_20260623T043239Z/open_duck_training_runs_cli/smoke_20260623T043310Z_gpu/2026_06_23_044644_430080.onnx`
- sha256: `308d39b74b13137424b9f25cce3d457e715221df1fa58bed73f19af196b54ebf`

| joint | index | action@0 | action@0.08 | delta |
|---|---:|---:|---:|---:|
| `head_yaw` | 7 | -0.1563 | -0.3889 | -0.2326 |
| `head_pitch` | 6 | -0.3081 | -0.5309 | -0.2227 |
| `right_knee` | 12 | 0.3058 | 0.4819 | 0.1761 |
| `right_hip_yaw` | 9 | -0.0123 | 0.1449 | 0.1573 |
| `head_roll` | 8 | 0.2067 | 0.3524 | 0.1457 |
| `left_knee` | 3 | 0.0971 | -0.0220 | -0.1191 |

### forward_moderated_no_bridge

- status: `PASS_COMMAND_SENSITIVITY_ANALYSIS`
- path: `/home/lsd/robots/open-duck-mini-rdkx5/outputs/analysis/colab_cli/open-duck-l4h-candidate-only-20260623T030701Z/partial_extract/open_duck_colab_cli_candidate-only_20260623T030712Z/open_duck_training_runs_cli/smoke_20260623T030751Z_gpu/2026_06_23_032041_307200.onnx`
- sha256: `6780f540d4cab33d0f4541834b0ee21d9ef74c02bb12640f6ffc05165d158d3f`

| joint | index | action@0 | action@0.08 | delta |
|---|---:|---:|---:|---:|
| `right_hip_yaw` | 9 | -0.5173 | -0.2245 | 0.2928 |
| `left_knee` | 3 | 0.0195 | 0.1709 | 0.1513 |
| `right_knee` | 12 | 0.4546 | 0.3417 | -0.1129 |
| `right_hip_roll` | 10 | -0.7036 | -0.6239 | 0.0797 |
| `neck_pitch` | 5 | 0.4583 | 0.5277 | 0.0695 |
| `head_yaw` | 7 | -0.7238 | -0.7868 | -0.0631 |

## Interpretation

- Nonzero `x=0.08 delta L2` means the ONNX policy changes its action
  when `command_x` changes in the synthetic observation.
- A command-sensitive policy can still fail the closed-loop gate if the
  action sequence does not generate effective locomotion under the
  actuator bridge and environment dynamics.
- This probe uses one synthetic upright observation, so it is evidence
  about static command dependence, not a replacement for closed-loop
  MuJoCo gates.
