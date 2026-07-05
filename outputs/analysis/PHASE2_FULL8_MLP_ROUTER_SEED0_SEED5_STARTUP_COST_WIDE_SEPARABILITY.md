# Full-8 MLP Router Separability

status: `PASS_MLP_ROUTER_SEPARABLE`

Offline diagnostic only. It did not train a control policy, deploy, SSH, run robot tests, change runtime behavior, or run grounded replay.

## Inputs

- manifest: `outputs/analysis/phase2_full8_router_source_selected_manifest.json`
- positive_marker: `iter25/seed_005`
- hidden_sizes: `[256, 128, 64]`
- train/test split per trace: `80.0%` / `20.0%`
- branch-A correction traces: `1`
- branch-A correction weight: `50.0`
- branch-B correction traces: `1`
- branch-B correction weight: `50.0`

## Results

| split | samples | positive_selected | negative_false_selected | balanced_accuracy |
|---|---:|---:|---:|---:|
| train | 4960 | 90.88% | 14.04% | 88.42% |
| test | 1200 | 80.67% | 3.62% | 88.52% |

## Logit Separation

| split | positive p05 | positive p50 | negative p50 | negative p95 |
|---|---:|---:|---:|---:|
| train | -1.9503 | 5.1467 | -6.0492 | 3.7807 |
| test | -4.1520 | 3.1991 | -7.8090 | -0.5783 |

## Decision

The branch labels are separable by a nonlinear stateless observation gate on the held-out split.
