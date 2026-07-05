# Full-8 MLP Router Separability

status: `HOLD_MLP_ROUTER_OVERLAP`

Offline diagnostic only. It did not train a control policy, deploy, SSH, run robot tests, change runtime behavior, or run grounded replay.

## Inputs

- manifest: `outputs/analysis/phase2_full8_router_source_selected_manifest.json`
- positive_marker: `iter25/seed_005`
- hidden_sizes: `[128, 64]`
- train/test split per trace: `80.0%` / `20.0%`
- branch-A correction traces: `1`
- branch-A correction weight: `50.0`
- branch-B correction traces: `1`
- branch-B correction weight: `50.0`

## Results

| split | samples | positive_selected | negative_false_selected | balanced_accuracy |
|---|---:|---:|---:|---:|
| train | 4960 | 83.82% | 22.59% | 80.62% |
| test | 1200 | 66.00% | 7.52% | 79.24% |

## Logit Separation

| split | positive p05 | positive p50 | negative p50 | negative p95 |
|---|---:|---:|---:|---:|
| train | -1.8878 | 1.7655 | -1.7028 | 4.2744 |
| test | -1.6761 | 0.6839 | -2.4160 | 0.3092 |

## Decision

Do not assume a stateless nonlinear router is sufficient. The held-out branch classifier does not meet the false-selection and balanced-accuracy thresholds needed before composing a two-policy deployable router.
