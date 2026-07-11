# Multivariate Reset-Health Transfer Result

Status: **FAIL_MULTIVARIATE_TRANSFER_ROUTE_CLOSED**

Offline existing-trace analysis only. No simulation, training, robot access, GPU, or Colab use.

| train → test | failures | disagreement AUC | reset AUC | combined AUC | combined improvement |
|---|---:|---:|---:|---:|---:|
| discovery → heldout | 2/16 | 1.000 | 0.750 | 1.000 | +0.000 |
| heldout → discovery | 5/16 | 0.909 | 0.764 | 0.818 | -0.091 |

## Frozen pass rule

combined ROC AUC strictly exceeds disagreement ROC AUC in both directions.

## Decision

Close this nearest-neighbor/equal-weight multivariate route; do not tune it post hoc.

No threshold or runtime gate is authorized by this analysis.
