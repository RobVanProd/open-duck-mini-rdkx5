# Right-Knee Tracking Mechanism Preregistration

Date: 2026-07-11

Status: **FROZEN BEFORE RESULT COMPUTATION**

This saved-trace analysis tests whether the replicated first-0.20-second
right-knee tracking error is explained by excessive policy target demand or by
the existing 2.0 rad/s target-rate limiter. It performs no simulation,
intervention, training, robot access, GPU use, or Colab allocation.

The right knee is actuator index 12 in the recorded 14-actuator contract. For
ticks 0-9 in each of seed blocks 8-23, 24-39, and 40-71, compute:

1. `applied_target_rate_p95_rad_s`: p95 absolute consecutive applied-target
   change divided by 0.02 seconds.
2. `rate_saturation_fraction`: fraction of consecutive applied-target changes
   at least 95% of the 2.0 rad/s bound.
3. `limiter_clip_gap_p95_rad`: p95 absolute pre-rate-limit target minus applied
   target.
4. `prelimit_target_rate_p95_rad_s`: p95 absolute consecutive pre-rate-limit
   target change divided by 0.02 seconds.

Larger values always mean greater hypothesized risk. Report fall-ranking ROC
AUC separately in each block and Pearson correlation with per-trace right-knee
p95 tracking error. A demand mechanism is supported only if at least one demand
feature has AUC >= 0.70 and positive correlation >= 0.50 in every block.
Otherwise do not lower or alter the right-knee rate limiter based on this route.
