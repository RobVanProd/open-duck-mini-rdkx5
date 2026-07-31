# Phase 2 Stage A On-Policy Teacher Corrections

status: `PASS_ONPOLICY_TEACHER_CORRECTION_ANALYSIS_READY`
data_gate_pass: `False`

Offline analysis only. No training, deployment, SSH, local GPU, or robot operation was performed.

## Aggregate

- traces: `8`
- samples: `400`
- pitch-chain-dominant traces: `7/8`
- teacher correction mean/p95/max: `0.0219` / `0.0580` / `0.1563` normalized action
- teacher target-rate p95/max: `1.5146` / `2.6084` rad/s

## Per Trace

| source | top correction joint | pitch chain | correction p95 | correction max | teacher rate p95 | teacher rate max |
|---|---|---:|---:|---:|---:|---:|
| `seed_000/trace.jsonl` | `left_knee` | `True` | 0.0524 | 0.1107 | 1.4989 | 1.9960 |
| `seed_001/trace.jsonl` | `left_knee` | `True` | 0.0515 | 0.1015 | 1.5349 | 2.1104 |
| `seed_002/trace.jsonl` | `left_ankle` | `True` | 0.0536 | 0.0937 | 1.5305 | 2.0058 |
| `seed_003/trace.jsonl` | `left_knee` | `True` | 0.0674 | 0.1563 | 1.5363 | 2.6084 |
| `seed_004/trace.jsonl` | `left_hip_pitch` | `True` | 0.0509 | 0.1046 | 1.4337 | 2.3705 |
| `seed_005/trace.jsonl` | `left_knee` | `True` | 0.0770 | 0.1396 | 1.5588 | 2.6052 |
| `seed_006/trace.jsonl` | `right_hip_pitch` | `True` | 0.0550 | 0.1373 | 1.5125 | 2.0881 |
| `seed_007/trace.jsonl` | `head_yaw` | `False` | 0.0532 | 0.0889 | 1.4962 | 1.9265 |

## Decision

The pre-registered data gate did not pass. Do not allocate a GPU or train this branch.
