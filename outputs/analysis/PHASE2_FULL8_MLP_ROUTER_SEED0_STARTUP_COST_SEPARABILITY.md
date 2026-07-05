# Full-8 MLP Router Separability

status: `PASS_MLP_ROUTER_SEPARABLE`

Offline diagnostic only. It did not train a control policy, deploy, SSH, run robot tests, change runtime behavior, or run grounded replay.

## Inputs

- manifest: `outputs/analysis/phase2_full8_router_source_selected_manifest.json`
- positive_marker: `iter25/seed_005`
- hidden_sizes: `[128, 64]`
- train/test split per trace: `80.0%` / `20.0%`
- correction traces: `1`
- correction weight: `50.0`

## Results

| split | samples | positive_selected | negative_false_selected | balanced_accuracy |
|---|---:|---:|---:|---:|
| train | 4880 | 87.17% | 3.11% | 92.03% |
| test | 1200 | 76.67% | 2.38% | 87.14% |

## Logit Separation

| split | positive p05 | positive p50 | negative p50 | negative p95 |
|---|---:|---:|---:|---:|
| train | -2.3701 | 3.0262 | -4.8589 | -0.4397 |
| test | -2.5701 | 1.4424 | -5.3820 | -0.6876 |

## Decision

The branch labels are separable by a nonlinear stateless observation gate on the held-out split.
