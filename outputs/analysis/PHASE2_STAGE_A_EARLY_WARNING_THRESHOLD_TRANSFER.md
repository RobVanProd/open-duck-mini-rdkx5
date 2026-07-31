# Early-Warning Threshold Transfer Check

Status: **THRESHOLD_TRANSFER_ASYMMETRIC_NO_RUNTIME_GATE**

Offline saved-JSON analysis only; no simulation, training, robot access, GPU, or Colab use.

Metric: first `10` ticks `p95` teacher disagreement.

| fit → test | threshold | fit TP/FN/TN/FP | test TP/FN/TN/FP | test sensitivity | test specificity | test balanced accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|
| discovery → heldout | 0.08247255 | 5/0/10/1 | 2/0/14/0 | 1.000 | 1.000 | 1.000 |
| heldout → discovery | 0.08765778 | 2/0/14/0 | 1/4/10/1 | 0.200 | 0.909 | 0.555 |

## Decision

Do not select or implement a runtime start-paused threshold.

The discovery-derived cutoff transfers to the held-out block, but the held-out-derived cutoff misses lower-disagreement failures in discovery. This asymmetric result is not evidence for a stable universal operating threshold.

## Limitations

- Only seven failures are present across 32 traces, including two in the held-out block.
- This evaluates seed-block transfer, not probability calibration or robot safety.
- Thresholds and performance are based on saved simulation traces only.
