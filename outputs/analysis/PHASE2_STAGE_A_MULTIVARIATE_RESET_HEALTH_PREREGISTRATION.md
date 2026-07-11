# Multivariate Reset-Health Saved-Trace Preregistration

Date: 2026-07-11

Status: **FROZEN BEFORE RESULT COMPUTATION**

This is an offline CPU-only analysis of existing traces. It authorizes no new
simulation, training, action modification, runtime monitor, deployment, robot
access, GPU use, or Colab allocation.

## Question

Does the initial reset observation add seed-block-transferable fall ranking to
the already frozen first-10-tick p95 teacher-disagreement score?

## Frozen data split

- discovery: seeds 8-23
- held-out: seeds 24-39
- outcome: termination before the one-second horizon
- evaluate both discovery-to-held-out and held-out-to-discovery transfer

## Frozen features and scores

1. `disagreement`: the existing first-10-tick p95 absolute teacher-policy
   disagreement; no recomputation or window selection.
2. `reset`: the first saved 101-element policy observation, normalized by the
   existing behavior-teacher mean and standard deviation. For each test reset,
   compute RMS distance to the nearest training failure and nearest training
   completion. Reset risk is `nearest_complete - nearest_failure`; larger is
   riskier.
3. `combined`: equal-weight mean of the disagreement and reset-risk z-scores.
   Each mean and population standard deviation is estimated from the training
   block only. No fitted coefficient, feature selection, or hyperparameter.

## Frozen evaluation

- Report test ROC AUC for all three scores in both transfer directions.
- The multivariate hypothesis passes only if `combined` AUC is strictly greater
  than `disagreement` AUC in both directions.
- Ties fail. No threshold will be fitted.
- With only seven failures, any pass remains exploratory and cannot authorize a
  runtime gate. A failure closes this exact nearest-neighbor/equal-weight route.
