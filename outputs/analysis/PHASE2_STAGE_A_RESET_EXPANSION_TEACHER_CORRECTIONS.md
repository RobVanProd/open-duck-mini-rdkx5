# Phase 2 Stage A On-Policy Teacher Corrections

status: `PASS_ONPOLICY_TEACHER_CORRECTION_ANALYSIS_READY`
data_gate_pass: `False`

Offline analysis only. No training, deployment, SSH, local GPU, or robot operation was performed.

## Aggregate

- traces: `16`
- samples: `721`
- pitch-chain-dominant traces: `14/16`
- teacher correction mean/p95/max: `0.0264` / `0.0739` / `0.2481` normalized action
- teacher target-rate p95/max: `1.4506` / `3.9247` rad/s

## Per Trace

| source | top correction joint | pitch chain | correction p95 | correction max | teacher rate p95 | teacher rate max |
|---|---|---:|---:|---:|---:|---:|
| `baseline_expansion/seed_008/trace.jsonl` | `left_knee` | `True` | 0.0568 | 0.0905 | 1.5282 | 2.5490 |
| `baseline_expansion/seed_009/trace.jsonl` | `left_ankle` | `True` | 0.1382 | 0.2189 | 1.2849 | 2.5402 |
| `baseline_expansion/seed_010/trace.jsonl` | `left_ankle` | `True` | 0.0537 | 0.1185 | 1.4861 | 2.4754 |
| `baseline_expansion/seed_011/trace.jsonl` | `right_ankle` | `True` | 0.0619 | 0.1200 | 1.5485 | 2.3983 |
| `baseline_expansion/seed_012/trace.jsonl` | `head_roll` | `False` | 0.1251 | 0.2481 | 1.1797 | 2.2452 |
| `baseline_expansion/seed_013/trace.jsonl` | `left_knee` | `True` | 0.0948 | 0.1898 | 1.4906 | 2.9091 |
| `baseline_expansion/seed_014/trace.jsonl` | `head_yaw` | `False` | 0.0976 | 0.2110 | 1.4010 | 2.2534 |
| `baseline_expansion/seed_015/trace.jsonl` | `left_ankle` | `True` | 0.0503 | 0.1161 | 1.4642 | 2.3422 |
| `baseline_expansion/seed_016/trace.jsonl` | `left_knee` | `True` | 0.0648 | 0.1456 | 1.3883 | 2.2805 |
| `baseline_expansion/seed_017/trace.jsonl` | `left_knee` | `True` | 0.0528 | 0.0859 | 1.3863 | 1.9916 |
| `baseline_expansion/seed_018/trace.jsonl` | `left_ankle` | `True` | 0.0532 | 0.0883 | 1.5676 | 2.2795 |
| `baseline_expansion/seed_019/trace.jsonl` | `right_hip_pitch` | `True` | 0.0965 | 0.1790 | 1.7456 | 3.9247 |
| `baseline_expansion/seed_020/trace.jsonl` | `right_ankle` | `True` | 0.1096 | 0.2181 | 1.2697 | 2.5935 |
| `baseline_expansion/seed_021/trace.jsonl` | `right_knee` | `True` | 0.0510 | 0.0802 | 1.3846 | 2.0454 |
| `baseline_expansion/seed_022/trace.jsonl` | `left_knee` | `True` | 0.0523 | 0.0934 | 1.4639 | 2.2965 |
| `baseline_expansion/seed_023/trace.jsonl` | `left_knee` | `True` | 0.0583 | 0.1658 | 1.3391 | 2.0317 |

## Decision

The pre-registered data gate did not pass. Do not allocate a GPU or train this branch.
