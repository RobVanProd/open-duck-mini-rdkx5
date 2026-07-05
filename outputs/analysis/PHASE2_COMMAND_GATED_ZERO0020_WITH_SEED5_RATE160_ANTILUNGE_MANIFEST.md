# BC Trace Manifest

status: `PASS_BC_TRACE_MANIFEST_READY`

This merged manifest is for one bounded offline trainable-compression test.
It does not include raw trace contents and does not deploy, SSH, run robot tests, or change runtime behavior.

## Merge

- dataset_id: `b9d5821e5727ac77`
- base_manifest: `outputs/analysis/phase2_command_gated_zero0020_bc_manifest.json`
- anti_lunge_manifest: `outputs/analysis/phase2_command_gated_seed5_rate160_antilunge_manifest.json`
- entries: `11`
- samples: `7524`
- bc_ready_entries: `11`
- intent: preserve the command-gated source while adding the small seed-5 rate160 anti-lunge correction set.

## Entries

| source | ticks | samples | bc_ready | vx | ratio | sent_vel95 | track95 | pitch95 | height |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0008 | 0.0094 | 0.0000 | 0.0349 | 0.0633 | 0.1614 |
| seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0009 | 0.0107 | 0.0000 | 0.0346 | 0.0667 | 0.1609 |
| seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0008 | 0.0100 | 0.0000 | 0.0346 | 0.0647 | 0.1614 |
| seed_006/trace.jsonl | 0-749 | 750 | `True` | 0.0007 | 0.0089 | 0.0000 | 0.0367 | 0.0699 | 0.1611 |
| seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0009 | 0.0106 | 0.0000 | 0.0341 | 0.0657 | 0.1613 |
| seed_000/trace.jsonl | 0-749 | 750 | `True` | 0.0272 | 0.3403 | 1.4505 | 0.1402 | 0.1737 | 0.1581 |
| seed_001/trace.jsonl | 0-749 | 750 | `True` | 0.0254 | 0.3170 | 1.4478 | 0.1417 | 0.1876 | 0.1581 |
| seed_002/trace.jsonl | 0-749 | 750 | `True` | 0.0269 | 0.3367 | 1.4433 | 0.1409 | 0.1894 | 0.1581 |
| seed_006/trace.jsonl | 0-749 | 750 | `True` | 0.0232 | 0.2896 | 1.4399 | 0.1405 | 0.1917 | 0.1581 |
| seed_007/trace.jsonl | 0-749 | 750 | `True` | 0.0265 | 0.3311 | 1.4524 | 0.1411 | 0.1724 | 0.1581 |
| analysis/phase2_command_gated_seed5_rate160_antilunge_relabel/seed_005/trace.jsonl | 80-157 | 24 | `True` | 0.3357 | 4.1966 | 1.5479 | 0.1464 | 1.3837 | -0.0058 |

## Gate

- Do not treat this manifest as a deployable policy.
- Use it only for the bounded seed-5 anti-lunge transfer student.
- Raw JSONL traces remain local analysis inputs.
