# Full-8 MLP Router Separability

status: `PASS_MLP_ROUTER_SEPARABLE`

Offline diagnostic only. It did not train a control policy, deploy, SSH, run robot tests, change runtime behavior, or run grounded replay.

## Inputs

- manifest: `outputs/analysis/phase2_full8_router_source_selected_manifest.json`
- positive_marker: `iter25/seed_005`
- hidden_sizes: `[128, 64]`
- train/test split per trace: `80.0%` / `20.0%`

## Results

| split | samples | positive_selected | negative_false_selected | balanced_accuracy |
|---|---:|---:|---:|---:|
| train | 4800 | 100.00% | 1.98% | 99.01% |
| test | 1200 | 94.67% | 3.05% | 95.81% |

## Logit Separation

| split | positive p05 | positive p50 | negative p50 | negative p95 |
|---|---:|---:|---:|---:|
| train | 4.0732 | 7.8399 | -8.5322 | -1.7698 |
| test | -0.1499 | 7.1691 | -9.1537 | -1.1541 |

## Decision

The branch labels are separable by a nonlinear stateless observation gate on the held-out split.
