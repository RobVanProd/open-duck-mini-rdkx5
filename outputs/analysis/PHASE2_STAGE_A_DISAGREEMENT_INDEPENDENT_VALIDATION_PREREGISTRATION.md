# Independent Disagreement Validation Plan

Date: 2026-07-11

Status: **PRE-REGISTERED; NOT STARTED**

## Evidence basis

The unchanged first-10-tick p95 teacher-disagreement metric transferred as a
fall-ranking signal, while both a fitted universal cutoff and a preregistered
reset-state combination failed stability tests. The next justified work is new
non-interventional evidence for the simpler metric, not feature or policy tuning.

## Frozen first block

- seeds: 40-71, exactly 32 consecutive canonical reset seeds
- original rate175 step-163,840 policy
- x command: 0.08 m/s
- horizon: 1.0 second
- corrected fitted actuator bridge
- 2.0 rad/s pitch-chain action-rate limit on joints 2,3,4,11,12,13
- full observations, CPU/JAX CPU only
- no action change, recovery, threshold gate, training, robot, GPU, or Colab

## Frozen analysis

- primary ranking metric: first-10-tick p95 teacher disagreement ROC AUC
- secondary fixed-cutoff audit: cutoff `0.08247255`, frozen from discovery
- report sensitivity, specificity, balanced accuracy, confusion counts, and
  Wilson 95% intervals for sensitivity and specificity
- do not refit or tune a cutoff
- fewer than five falls makes the block explicitly inconclusive for cutoff
  assessment, regardless of point estimates

## Decision rule

- If ranking reverses below AUC 0.5, reject the detector route.
- Otherwise retain it only as an offline diagnostic unless a later independent
  block supplies enough positives and a separately reviewed safety criterion.
- This block cannot by itself authorize runtime or robot behavior.
