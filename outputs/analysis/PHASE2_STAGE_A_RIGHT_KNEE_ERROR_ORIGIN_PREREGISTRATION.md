# Right-Knee Error-Origin Preregistration

Date: 2026-07-11

Status: **FROZEN BEFORE RESULT COMPUTATION**

Using existing seeds 8-71 traces, distinguish reset-initialized right-knee
mismatch from mismatch that grows after control begins. For each independent
seed block, compute fall-ranking AUC for:

1. absolute applied-target minus actual-position error at tick 0;
2. error growth from tick 0 to the maximum over ticks 0-9;
3. error remaining at tick 9 divided by tick-0 error (epsilon 1e-6).

Larger values mean hypothesized risk. A reset-origin mechanism is supported if
tick-0 absolute error has AUC >= 0.70 in every block. A control-growth mechanism
is supported if error growth has AUC >= 0.70 in every block. Report both even
if neither passes. This is associative evidence only and authorizes no reset,
gain, target, limiter, training, deployment, robot, GPU, or Colab change.
