# Full-8 MLP Router Separability

status: `PASS_MLP_ROUTER_SEPARABLE`

Offline diagnostic only. It did not train a control policy, deploy, SSH, run robot tests, change runtime behavior, or run grounded replay.

## Inputs

- manifest: `outputs/analysis/phase2_full8_router_source_selected_manifest.json`
- positive_marker: `iter25/seed_005`
- hidden_sizes: `[256, 128, 64]`
- train/test split per trace: `80.0%` / `20.0%`
- branch-A correction traces: `2`
- branch-A correction weight: `50.0`
- branch-B correction traces: `1`
- branch-B correction weight: `50.0`

## Results

| split | samples | positive_selected | negative_false_selected | balanced_accuracy |
|---|---:|---:|---:|---:|
| train | 5040 | 90.29% | 12.68% | 88.81% |
| test | 1200 | 80.00% | 3.14% | 88.43% |

## Logit Separation

| split | positive p05 | positive p50 | negative p50 | negative p95 |
|---|---:|---:|---:|---:|
| train | -2.2245 | 5.4358 | -8.0952 | 3.6856 |
| test | -5.8879 | 2.7347 | -9.8094 | -0.9096 |

## Decision

The branch labels are separable by a nonlinear stateless observation gate on the held-out split.
