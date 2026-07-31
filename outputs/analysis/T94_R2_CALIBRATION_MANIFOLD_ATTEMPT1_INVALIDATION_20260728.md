# T94 attempt-1 invalidation

- Status: `INVALIDATED_T94_ATTEMPT1_REPORTING_ONLY`
- One calibration block completed, then the read-only audit compared a 14-value rate-excess vector directly with a scalar.
- No policy, classifier, or routing result was emitted.
- The completed block will not be reused. V2 must use a fresh cache and all 40 cells.
- The correction only reduces each vector with `max` before applying the unchanged zero threshold.
- Training / Colab / RDK / robot: `0 / 0 / 0 / 0`
