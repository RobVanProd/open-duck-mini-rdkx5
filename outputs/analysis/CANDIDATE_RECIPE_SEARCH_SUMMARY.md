# Candidate Recipe Search Summary

Offline-only summary of candidate sim gates. No robot motion, SSH,
deployment, or runtime behavior change is implied by this report.

## Status Counts

| status | count |
|---|---:|
| `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 10 |
| `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 32 |
| `HOLD_CANDIDATE_POSTURE` | 1 |
| `HOLD_CANDIDATE_TRACKING` | 3 |
| `PASS_CANDIDATE_SIM_GATE` | 12 |

## Best x=0.08 Forward-Progress Attempts

Sorted by minimum forward command tracking ratio. These are still
offline sim gates only; high progress with falls/posture failures is
not deployable.

| candidate | status | track ratio | mean vx | pitch p95 | target vel p95 | body pitch p95 | min height |
|---|---|---:|---:|---:|---:|---:|---:|
| `open_duck_mini_actuator_bridge_cli_20260623T000344Z` | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 0.0524 | 0.0042 | 0.1583 | 3.0004 | 1.0477 | 0.0159 |
| `mild_bridge_candidate_x008_cpu` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0268 | 0.0021 | 0.1213 | 0.5712 | 0.2742 | 0.1442 |
| `movement_phase_b_retry` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0215 | 0.0017 | 0.1304 | 3.9634 | 0.2994 | 0.1433 |
| `l4b_614400_x008` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0170 | 0.0019 | 0.0823 | 0.4153 | 0.2151 | 0.1417 |
| `local_cpu_forward_mid_bridge_steady` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0092 | 0.0007 | 0.0751 | 0.2962 | 0.1284 | 0.1506 |
| `local_cpu_forced_forward_moderated_no_bridge` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0075 | 0.0006 | 0.0566 | 0.1994 | 0.0868 | 0.1535 |
| `local_cpu_forward_imitation_bridge_steady` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0067 | 0.0008 | 0.0695 | 0.3085 | 0.1076 | 0.1521 |
| `best_walk_vmax_3p2_x008_cpu` | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0061 | 0.0473 | 0.2093 | 3.2000 | 0.0703 | 0.1536 |

## Gate Outcomes

| candidate | cmd x | status | track ratio | mean vx | pitch p95 | target vel p95 | action sat % | body pitch p95 | min height | terminations |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| `2026_06_02_175758_983040` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0082 | -0.0006 | 0.0652 | 0.1919 | 0.0000 | 0.1320 | 0.1527 | `duration_complete/duration_complete/duration_complete` |
| `2026_06_02_175858_1474560` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0095 | -0.0006 | 0.0787 | 0.2603 | 0.0000 | 0.1442 | 0.1516 | `duration_complete/duration_complete/duration_complete` |
| `2026_06_02_175919_1638400` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0100 | -0.0007 | 0.0837 | 0.2893 | 0.0000 | 0.1444 | 0.1514 | `duration_complete/duration_complete/duration_complete` |
| `2026_06_02_180000_1966080` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0109 | -0.0007 | 0.0902 | 0.3293 | 0.0000 | 0.1504 | 0.1509 | `duration_complete/duration_complete/duration_complete` |
| `2026_06_02_180020_2129920` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0097 | -0.0007 | 0.0976 | 0.3731 | 0.0000 | 0.1504 | 0.1508 | `duration_complete/duration_complete/duration_complete` |
| `2026_06_22_205118_0_x0` | 0.0000 | `PASS_CANDIDATE_SIM_GATE` | NA | -0.0006 | 0.0671 | 0.0980 | 0.0000 | 0.1459 | 0.1533 | `duration_complete/duration_complete/duration_complete` |
| `2026_06_22_205427_153600_x0` | 0.0000 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | NA | -0.1332 | 0.2309 | 1.1829 | 0.0000 | 1.3916 | 0.0461 | `fall_or_nan/fall_or_nan/duration_complete` |
| `2026_06_22_205720_307200_x0` | 0.0000 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | NA | -0.1464 | 0.1586 | 2.5505 | 0.0000 | 1.3720 | 0.0416 | `fall_or_nan/fall_or_nan/fall_or_nan` |
| `2026_06_22_205731_460800_x0` | 0.0000 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | NA | -0.1710 | 0.1892 | 2.1586 | 0.0000 | 1.3539 | 0.0414 | `fall_or_nan/fall_or_nan/fall_or_nan` |
| `2026_06_22_205742_614400_x0` | 0.0000 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | NA | -0.1841 | 0.2810 | 2.3500 | 0.0000 | 1.4088 | 0.0329 | `fall_or_nan/fall_or_nan/fall_or_nan` |
| `balanced_probe_x0` | 0.0000 | `PASS_CANDIDATE_SIM_GATE` | NA | 0.0005 | 0.0689 | 0.1767 | 0.0000 | 0.1511 | 0.1521 | `duration_complete/duration_complete/duration_complete` |
| `balanced_probe_x008` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0045 | -0.0004 | 0.0526 | 0.1460 | 0.0000 | 0.1024 | 0.1537 | `duration_complete/duration_complete/duration_complete` |
| `baseline_best_x008` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0028 | 0.0435 | 0.2159 | 5.2400 | 0.0000 | 0.0683 | 0.1536 | `duration_complete/duration_complete/duration_complete` |
| `baseline_best_x008_candidate_gate_check` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.4140 | -0.0331 | 0.2159 | 5.2400 | 0.0000 | 0.0683 | 0.1536 | `duration_complete/duration_complete/duration_complete` |
| `best_walk_action_gain_0p4_x008_cpu` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0058 | -0.0005 | 0.1153 | 1.6885 | 0.0000 | 0.0157 | 0.1536 | `duration_complete/duration_complete/duration_complete` |
| `best_walk_action_gain_0p6_x008_cpu` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0006 | 0.0004 | 0.1707 | 2.5761 | 0.0000 | 0.0301 | 0.1536 | `duration_complete/duration_complete/duration_complete` |
| `best_walk_action_gain_0p8_x008_cpu` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0022 | 0.0067 | 0.2237 | 4.6203 | 0.0000 | 0.0501 | 0.1536 | `duration_complete/duration_complete/duration_complete` |
| `best_walk_vmax_2p5_x008_cpu` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0046 | 0.0443 | 0.1952 | 2.5000 | 0.0000 | 0.0749 | 0.1537 | `duration_complete/duration_complete/duration_complete` |
| `best_walk_vmax_3p2_x008_cpu` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0061 | 0.0473 | 0.2093 | 3.2000 | 0.0000 | 0.0703 | 0.1536 | `duration_complete/duration_complete/duration_complete` |
| `best_walk_vmax_4p0_x008_cpu` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0057 | 0.0455 | 0.2164 | 4.0000 | 0.0000 | 0.0688 | 0.1536 | `duration_complete/duration_complete/duration_complete` |
| `candidate` | 0.0000 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | NA | -0.1841 | 0.2810 | 2.3500 | 0.0000 | 1.4088 | 0.0329 | `fall_or_nan/fall_or_nan/fall_or_nan` |
| `candidate` | 0.0000 | `PASS_CANDIDATE_SIM_GATE` | NA | -0.0003 | 0.0689 | 0.1767 | 0.0000 | 0.1511 | 0.1521 | `duration_complete/duration_complete/duration_complete` |
| `candidate` | 0.0000 | `HOLD_CANDIDATE_POSTURE` | NA | -0.0012 | 0.0773 | 0.1619 | 0.0000 | 0.4108 | 0.1392 | `duration_complete/duration_complete/duration_complete` |
| `candidate` | 0.0000 | `PASS_CANDIDATE_SIM_GATE` | NA | -0.0002 | 0.0719 | 0.2826 | 0.0000 | 0.0840 | 0.1536 | `duration_complete/duration_complete/duration_complete` |
| `candidate` | 0.0000 | `HOLD_CANDIDATE_TRACKING` | NA | -0.0005 | 0.0988 | 0.3858 | 0.0000 | 0.1404 | 0.1513 | `duration_complete/duration_complete/duration_complete` |
| `candidate` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0096 | -0.0004 | 0.0823 | 0.4153 | 0.0000 | 0.2151 | 0.1417 | `duration_complete/duration_complete/duration_complete` |
| `candidate` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0080 | 0.0009 | 0.0526 | 0.1460 | 0.0000 | 0.1024 | 0.1537 | `duration_complete/duration_complete/duration_complete` |
| `candidate` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0035 | -0.0001 | 0.0458 | 0.1992 | 0.0000 | 0.0826 | 0.1535 | `duration_complete/duration_complete/duration_complete` |
| `candidate` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0040 | -0.0003 | 0.0885 | 0.2856 | 0.0000 | 0.0991 | 0.1536 | `duration_complete/duration_complete/duration_complete` |
| `candidate` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0101 | -0.0007 | 0.0975 | 0.3724 | 0.0000 | 0.1501 | 0.1508 | `duration_complete/duration_complete/duration_complete` |
| `forward_bootstrap_no_bridge` | 0.0000 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | NA | 0.2771 | 0.3789 | 0.0000 | 100.0000 | 1.3087 | 0.0064 | `fall_or_nan/fall_or_nan/fall_or_nan` |
| `forward_mild_bridge_push` | 0.0000 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | NA | 0.2918 | 0.2196 | 1.3625 | 0.0000 | 1.3760 | 0.0378 | `fall_or_nan/fall_or_nan/fall_or_nan` |
| `forward_moderated_no_bridge` | 0.0000 | `PASS_CANDIDATE_SIM_GATE` | NA | 0.0008 | 0.0638 | 0.2536 | 0.0000 | 0.1128 | 0.1535 | `duration_complete/duration_complete/duration_complete` |
| `l4b_614400_x008` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0170 | 0.0019 | 0.0823 | 0.4153 | 0.0000 | 0.2151 | 0.1417 | `duration_complete/duration_complete/duration_complete` |
| `local_cpu_forced_forward_moderated_no_bridge` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0075 | 0.0006 | 0.0566 | 0.1994 | 0.0000 | 0.0868 | 0.1535 | `duration_complete/duration_complete/duration_complete` |
| `local_cpu_forward_imitation_bridge_steady` | 0.0000 | `PASS_CANDIDATE_SIM_GATE` | NA | 0.0001 | 0.0517 | 0.2295 | 0.0000 | 0.0337 | 0.1538 | `duration_complete/duration_complete/duration_complete` |
| `local_cpu_forward_imitation_bridge_steady` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0067 | 0.0008 | 0.0695 | 0.3085 | 0.0000 | 0.1076 | 0.1521 | `duration_complete/duration_complete/duration_complete` |
| `local_cpu_forward_mid_bridge_steady` | 0.0000 | `PASS_CANDIDATE_SIM_GATE` | NA | 0.0003 | 0.0616 | 0.2097 | 0.0000 | 0.0665 | 0.1537 | `duration_complete/duration_complete/duration_complete` |
| `local_cpu_forward_mid_bridge_steady` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0092 | 0.0007 | 0.0751 | 0.2962 | 0.0000 | 0.1284 | 0.1506 | `duration_complete/duration_complete/duration_complete` |
| `mild_bridge_candidate_x008_cpu` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0268 | 0.0021 | 0.1213 | 0.5712 | 0.0000 | 0.2742 | 0.1442 | `duration_complete/duration_complete/duration_complete` |
| `movement_phase_b_retry` | 0.0000 | `HOLD_CANDIDATE_TRACKING` | NA | 0.0018 | 0.1341 | 1.8605 | 0.0000 | 0.2729 | 0.1449 | `duration_complete/duration_complete/duration_complete` |
| `movement_phase_b_retry` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0215 | 0.0017 | 0.1304 | 3.9634 | 0.0000 | 0.2994 | 0.1433 | `duration_complete/duration_complete/duration_complete` |
| `movement_probe_x0` | 0.0000 | `PASS_CANDIDATE_SIM_GATE` | NA | 0.0003 | 0.0719 | 0.2826 | 0.0000 | 0.0840 | 0.1536 | `duration_complete/duration_complete/duration_complete` |
| `movement_probe_x008` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0051 | 0.0005 | 0.0885 | 0.2856 | 0.0000 | 0.0991 | 0.1536 | `duration_complete/duration_complete/duration_complete` |
| `open_duck_mini_actuator_bridge_cli_20260622T153734Z` | 0.0000 | `PASS_CANDIDATE_SIM_GATE` | NA | -0.0001 | 0.0492 | 0.0899 | 0.0000 | 0.0313 | 0.1537 | `duration_complete/duration_complete/duration_complete` |
| `open_duck_mini_actuator_bridge_cli_20260622T153734Z` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0020 | -0.0002 | 0.0469 | 0.0826 | 0.0000 | 0.0428 | 0.1537 | `duration_complete/duration_complete/duration_complete` |
| `open_duck_mini_actuator_bridge_cli_20260622T164611Z` | 0.0000 | `PASS_CANDIDATE_SIM_GATE` | NA | -0.0003 | 0.0689 | 0.2110 | 0.0000 | 0.1053 | 0.1532 | `duration_complete/duration_complete/duration_complete` |
| `open_duck_mini_actuator_bridge_cli_20260622T164611Z` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0071 | -0.0006 | 0.0587 | 0.2249 | 0.0000 | 0.1177 | 0.1526 | `duration_complete/duration_complete/duration_complete` |
| `open_duck_mini_actuator_bridge_cli_20260622T190944Z` | 0.0000 | `PASS_CANDIDATE_SIM_GATE` | NA | 0.0002 | 0.0536 | 0.2176 | 0.0000 | 0.0581 | 0.1537 | `duration_complete/duration_complete/duration_complete` |
| `open_duck_mini_actuator_bridge_cli_20260622T190944Z` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0004 | 0.0001 | 0.0565 | 0.2616 | 0.0000 | 0.0489 | 0.1537 | `duration_complete/duration_complete/duration_complete` |
| `open_duck_mini_actuator_bridge_cli_20260622T202101Z` | 0.0000 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | NA | -0.1043 | 0.1402 | 1.5387 | 0.0000 | 1.3069 | 0.0444 | `fall_or_nan/duration_complete/duration_complete` |
| `open_duck_mini_actuator_bridge_cli_20260622T202101Z` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0053 | -0.0002 | 0.0623 | 0.2494 | 0.0000 | 0.1109 | 0.1536 | `duration_complete/duration_complete/duration_complete` |
| `open_duck_mini_actuator_bridge_cli_20260622T230127Z` | 0.0000 | `PASS_CANDIDATE_SIM_GATE` | NA | 0.0002 | 0.0463 | 0.1909 | 0.0000 | 0.0464 | 0.1535 | `duration_complete/duration_complete/duration_complete` |
| `open_duck_mini_actuator_bridge_cli_20260622T230127Z` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | 0.0027 | 0.0004 | 0.0509 | 0.1523 | 0.0000 | 0.0643 | 0.1536 | `duration_complete/duration_complete/duration_complete` |
| `open_duck_mini_actuator_bridge_cli_20260623T000344Z` | 0.0000 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | NA | 0.0038 | 0.1629 | 2.7775 | 0.0000 | 0.9294 | 0.0147 | `duration_complete/fall_or_nan/fall_or_nan` |
| `open_duck_mini_actuator_bridge_cli_20260623T000344Z` | 0.0800 | `HOLD_CANDIDATE_FALL_OR_TERMINATION` | 0.0524 | 0.0042 | 0.1583 | 3.0004 | 0.0000 | 1.0477 | 0.0159 | `duration_complete/fall_or_nan/fall_or_nan` |
| `open_duck_mini_actuator_bridge_cli_20260623T003841Z` | 0.0000 | `HOLD_CANDIDATE_TRACKING` | NA | 0.0017 | 0.1219 | 0.5971 | 0.0000 | 0.2473 | 0.1457 | `duration_complete/duration_complete/duration_complete` |
| `playground_onnx_x008_cpu` | 0.0800 | `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` | -0.0076 | -0.0006 | 0.0429 | 0.1173 | 0.0000 | 0.0111 | 0.1537 | `duration_complete/duration_complete/duration_complete` |

## Interpretation

- `PASS_CANDIDATE_SIM_GATE` means the candidate passed the configured
  offline sim gate only. It is not robot approval.
- `HOLD_CANDIDATE_LOW_FORWARD_PROGRESS` means the candidate stayed
  stable but did not meaningfully track the commanded forward speed.
- Fall/termination and high saturation candidates are not deployable.
- A useful next recipe should improve x=0.08 tracking ratio while
  keeping action saturation, target velocity, pitch tracking, body
  pitch, and base height inside the current gate thresholds.

## Source Files

- `outputs/analysis/colab_cli/phase_b_eval_20260622T173551Z/final/phase_b_checkpoint_sweep_20260622T173551Z/2026_06_02_175758_983040_gate_x008/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/phase_b_eval_20260622T173551Z/final/phase_b_checkpoint_sweep_20260622T173551Z/2026_06_02_175858_1474560_gate_x008/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/phase_b_eval_20260622T173551Z/final/phase_b_checkpoint_sweep_20260622T173551Z/2026_06_02_175919_1638400_gate_x008/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/phase_b_eval_20260622T173551Z/final/phase_b_checkpoint_sweep_20260622T173551Z/2026_06_02_180000_1966080_gate_x008/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/phase_b_eval_20260622T173551Z/final/phase_b_checkpoint_sweep_20260622T173551Z/2026_06_02_180020_2129920_gate_x008/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/open-duck-l4b-candidate-only-20260622T204511Z/local_cpu_checkpoint_scan/2026_06_22_205118_0_x0/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/open-duck-l4b-candidate-only-20260622T204511Z/local_cpu_checkpoint_scan/2026_06_22_205427_153600_x0/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/open-duck-l4b-candidate-only-20260622T204511Z/local_cpu_checkpoint_scan/2026_06_22_205720_307200_x0/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/open-duck-l4b-candidate-only-20260622T204511Z/local_cpu_checkpoint_scan/2026_06_22_205731_460800_x0/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/open-duck-l4b-candidate-only-20260622T204511Z/local_cpu_checkpoint_scan/2026_06_22_205742_614400_x0/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/local_velocity_gate_recheck/balanced_probe_x0/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/local_velocity_gate_recheck/balanced_probe_x008/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/local_velocity_gate_recheck/baseline_best_x008/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/baseline_best_x008_candidate_gate_check/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/best_walk_action_gain_0p4_x008_cpu/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/best_walk_action_gain_0p6_x008_cpu/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/best_walk_action_gain_0p8_x008_cpu/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/best_walk_vmax_2p5_x008_cpu/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/best_walk_vmax_3p2_x008_cpu/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/best_walk_vmax_4p0_x008_cpu/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/open-duck-l4b-candidate-only-20260622T204511Z/local_cpu_gates/candidate_gate_x0/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/open-duck-l4c-balanced-probe-20260622T215118Z/cpu_gates/candidate_gate_x0.json`
- `outputs/analysis/colab_cli/open-duck-l4c-candidate-only-20260622T213104Z/recovered_checkpoint_153600_cpu_gates/candidate_gate_x0.json`
- `outputs/analysis/colab_cli/open-duck-l4c-movement-probe-20260622T220728Z/cpu_gates/candidate_gate_x0.json`
- `outputs/analysis/phase_b_2129920_cpu_gates/candidate_gate_x0.json`
- `outputs/analysis/colab_cli/open-duck-l4b-candidate-only-20260622T204511Z/local_cpu_gates/candidate_gate_x008/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/open-duck-l4c-balanced-probe-20260622T215118Z/cpu_gates/candidate_gate_x008.json`
- `outputs/analysis/colab_cli/open-duck-l4c-candidate-only-20260622T213104Z/recovered_checkpoint_153600_cpu_gates/candidate_gate_x008.json`
- `outputs/analysis/colab_cli/open-duck-l4c-movement-probe-20260622T220728Z/cpu_gates/candidate_gate_x008.json`
- `outputs/analysis/phase_b_2129920_cpu_gates/candidate_gate_x008.json`
- `outputs/analysis/colab_cli/open-duck-l4h-candidate-only-20260623T023215Z/artifact/open_duck_colab_cli_candidate-only_20260623T023259Z/forward_bootstrap_no_bridge_candidate_gate_x0.json`
- `outputs/analysis/colab_cli/open-duck-l4i-candidate-only-20260623T033957Z/extracted_partial/open_duck_colab_cli_candidate-only_20260623T034008Z/forward_mild_bridge_push_candidate_gate_x0.json`
- `outputs/analysis/colab_cli/open-duck-l4h-candidate-only-20260623T030701Z/partial_extract/open_duck_colab_cli_candidate-only_20260623T030712Z/forward_moderated_no_bridge_candidate_gate_x0.json`
- `outputs/analysis/local_velocity_gate_recheck/l4b_614400_x008/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/open-duck-l4h-candidate-only-20260623T030701Z/local_cpu_forced_forward_moderated_no_bridge_gate_x008/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/open-duck-l4j-candidate-only-20260623T043228Z/local_cpu_forward_imitation_bridge_steady_gate_x0/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/open-duck-l4j-candidate-only-20260623T043228Z/local_cpu_forward_imitation_bridge_steady_gate_x008/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/open-duck-l4i-candidate-only-20260623T040647Z/local_cpu_forward_mid_bridge_steady_gate_x0/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/open-duck-l4i-candidate-only-20260623T040647Z/local_cpu_forward_mid_bridge_steady_gate_x008/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/mild_bridge_candidate_x008_cpu/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/open-duck-l4g-candidate-only-20260623T013026Z/artifact/open_duck_colab_cli_candidate-only_20260623T013038Z/movement_phase_b_retry_candidate_gate_x0.json`
- `outputs/analysis/colab_cli/open-duck-l4g-candidate-only-20260623T013026Z/artifact/open_duck_colab_cli_candidate-only_20260623T013038Z/movement_phase_b_retry_candidate_gate_x008.json`
- `outputs/analysis/local_velocity_gate_recheck/movement_probe_x0/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/local_velocity_gate_recheck/movement_probe_x008/closed_loop_actuator_bridge_eval.json`
- `outputs/analysis/colab_cli/open-duck-l4-candidate-only-20260622T152234Z/result/extracted/open_duck_colab_cli_candidate-only_20260622T152244Z/open_duck_mini_actuator_bridge_cli_20260622T153734Z_candidate_gate_x0.json`
- `outputs/analysis/colab_cli/open-duck-l4-candidate-only-20260622T152234Z/result/extracted/open_duck_colab_cli_candidate-only_20260622T152244Z/open_duck_mini_actuator_bridge_cli_20260622T153734Z_candidate_gate_x008.json`
- `outputs/analysis/colab_cli/open-duck-l4-candidate-only-20260622T162729Z/artifact/open_duck_colab_cli_candidate-only_20260622T162818Z/open_duck_mini_actuator_bridge_cli_20260622T164611Z_candidate_gate_x0.json`
- `outputs/analysis/colab_cli/open-duck-l4-candidate-only-20260622T162729Z/artifact/open_duck_colab_cli_candidate-only_20260622T162818Z/open_duck_mini_actuator_bridge_cli_20260622T164611Z_candidate_gate_x008.json`
- `outputs/analysis/colab_cli/open-duck-l4-candidate-only-20260622T185306Z/artifact_final/open_duck_colab_cli_candidate-only_20260622T185328Z/open_duck_mini_actuator_bridge_cli_20260622T190944Z_candidate_gate_x0.json`
- `outputs/analysis/colab_cli/open-duck-l4-candidate-only-20260622T185306Z/artifact_final/open_duck_colab_cli_candidate-only_20260622T185328Z/open_duck_mini_actuator_bridge_cli_20260622T190944Z_candidate_gate_x008.json`
- `outputs/analysis/colab_cli/open-duck-l4b-candidate-only-20260622T200431Z/artifact_final/open_duck_colab_cli_candidate-only_20260622T200442Z/open_duck_mini_actuator_bridge_cli_20260622T202101Z_candidate_gate_x0.json`
- `outputs/analysis/colab_cli/open-duck-l4b-candidate-only-20260622T200431Z/artifact_final/open_duck_colab_cli_candidate-only_20260622T200442Z/open_duck_mini_actuator_bridge_cli_20260622T202101Z_candidate_gate_x008.json`
- `outputs/analysis/colab_cli/open-duck-l4e-candidate-only-20260622T224929Z/artifact_final/open_duck_colab_cli_candidate-only_20260622T224933Z/open_duck_mini_actuator_bridge_cli_20260622T230127Z_candidate_gate_x0.json`
- `outputs/analysis/colab_cli/open-duck-l4e-candidate-only-20260622T224929Z/artifact_final/open_duck_colab_cli_candidate-only_20260622T224933Z/open_duck_mini_actuator_bridge_cli_20260622T230127Z_candidate_gate_x008.json`
- `outputs/analysis/cuda_imports/open-duck-l4f-restore-finetune-20260623T000344Z/open_duck_colab_cli_candidate-only_20260622T235118Z/open_duck_mini_actuator_bridge_cli_20260623T000344Z_candidate_gate_x0.json`
- `outputs/analysis/cuda_imports/open-duck-l4f-restore-finetune-20260623T000344Z/open_duck_colab_cli_candidate-only_20260622T235118Z/open_duck_mini_actuator_bridge_cli_20260623T000344Z_candidate_gate_x008.json`
- `outputs/analysis/colab_cli/open-duck-l4f-candidate-only-20260623T002728Z/partial_extract/open_duck_colab_cli_candidate-only_20260623T002739Z/open_duck_mini_actuator_bridge_cli_20260623T003841Z_candidate_gate_x0.json`
- `outputs/analysis/playground_onnx_x008_cpu/closed_loop_actuator_bridge_eval.json`
