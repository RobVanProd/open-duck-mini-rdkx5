# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This manifest points to ignored full-observation selector replay traces.
It is for offline distillation only and does not include raw trace contents.

## Summary

- dataset_id: `40834b6d7b2a128a`
- entries: `16`
- samples: `721`
- bc_ready_entries: `16`

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| baseline_expansion/seed_008/trace.jsonl | 0-49 | 50 | `True` | 0.0565 | 0.7061 | 1.3966 | 0.1466 | 0.1036 | 0.1475 |
| baseline_expansion/seed_009/trace.jsonl | 0-33 | 34 | `True` | -0.4078 | -5.0975 | 1.3722 | 0.1411 | 1.4223 | 0.0595 |
| baseline_expansion/seed_010/trace.jsonl | 0-49 | 50 | `True` | 0.0599 | 0.7484 | 1.3026 | 0.1306 | 0.0971 | 0.1507 |
| baseline_expansion/seed_011/trace.jsonl | 0-49 | 50 | `True` | 0.0317 | 0.3963 | 1.4055 | 0.1465 | 0.1510 | 0.1560 |
| baseline_expansion/seed_012/trace.jsonl | 0-36 | 37 | `True` | -0.3838 | -4.7970 | 1.2202 | 0.1318 | 1.4148 | 0.0641 |
| baseline_expansion/seed_013/trace.jsonl | 0-49 | 50 | `True` | -0.0825 | -1.0314 | 1.3549 | 0.1300 | 0.2058 | 0.1561 |
| baseline_expansion/seed_014/trace.jsonl | 0-40 | 41 | `True` | -0.0666 | -0.8322 | 1.2689 | 0.1243 | 0.1747 | 0.0885 |
| baseline_expansion/seed_015/trace.jsonl | 0-49 | 50 | `True` | -0.0067 | -0.0843 | 1.3170 | 0.1329 | 0.0720 | 0.1577 |
| baseline_expansion/seed_016/trace.jsonl | 0-49 | 50 | `True` | -0.0696 | -0.8704 | 1.2591 | 0.1176 | 0.2608 | 0.1544 |
| baseline_expansion/seed_017/trace.jsonl | 0-49 | 50 | `True` | 0.0170 | 0.2126 | 1.2583 | 0.1149 | 0.0780 | 0.1527 |
| baseline_expansion/seed_018/trace.jsonl | 0-49 | 50 | `True` | 0.0552 | 0.6896 | 1.3869 | 0.1361 | 0.0874 | 0.1516 |
| baseline_expansion/seed_019/trace.jsonl | 0-31 | 32 | `True` | -0.0801 | -1.0011 | 1.3245 | 0.1767 | 0.1615 | 0.0691 |
| baseline_expansion/seed_020/trace.jsonl | 0-26 | 27 | `True` | 0.0297 | 0.3716 | 1.0492 | 0.1297 | 0.3761 | 0.0985 |
| baseline_expansion/seed_021/trace.jsonl | 0-49 | 50 | `True` | 0.0147 | 0.1837 | 1.2946 | 0.1208 | 0.0826 | 0.1517 |
| baseline_expansion/seed_022/trace.jsonl | 0-49 | 50 | `True` | 0.0398 | 0.4981 | 1.3389 | 0.1315 | 0.0888 | 0.1527 |
| baseline_expansion/seed_023/trace.jsonl | 0-49 | 50 | `True` | -0.0067 | -0.0841 | 1.3089 | 0.1158 | 0.1445 | 0.1554 |

## Gate

- Do not commit raw JSONL traces unless explicitly approved.
- Do not treat this manifest as a deployable policy.
- Use it only as offline seed material for a portable student.
