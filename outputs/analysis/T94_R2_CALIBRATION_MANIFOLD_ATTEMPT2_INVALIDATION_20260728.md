# T94 attempt-2 invalidation

- Status: `INVALIDATED_T94_ATTEMPT2_REPORTING_ONLY`
- Two fresh calibration blocks completed. The audit then treated a nonempty 14-value all-zero `action_saturated` list as Boolean true.
- No policy, classifier, or routing result was emitted.
- Neither completed block will be reused. V3 must use a fresh cache and all 40 cells.
- The correction applies `any` elementwise and preserves the exact zero-saturation threshold.
- V3 may execute four independent frozen cells concurrently; matrix contents and decision rules are unchanged.
- Training / Colab / RDK / robot: `0 / 0 / 0 / 0`
