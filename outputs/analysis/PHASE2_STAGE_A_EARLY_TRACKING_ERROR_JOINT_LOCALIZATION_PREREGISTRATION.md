# Early Tracking-Error Joint Localization Preregistration

Date: 2026-07-11

Status: **FROZEN BEFORE RESULT COMPUTATION**

The preregistered physical-signature analysis identified first-0.20-second
actuator tracking error as a replicated fall correlate. This saved-trace-only
analysis localizes that signal across the fixed 14-actuator order recorded by
the simulator contract.

For each actuator and each of seed blocks 8-23, 24-39, and 40-71, compute the
ROC AUC of its first-10-tick 95th-percentile absolute applied-target minus
actual-position error for later fall versus duration completion. Larger error
means greater risk. Report all 14 joints without selection or adjustment.

A joint is a localized candidate only if AUC is at least 0.70 in every block.
Passing remains associative and authorizes no limiter, gain change,
intervention, training, deployment, robot access, GPU, or Colab use. If no
joint passes, the aggregate tracking-error signal is distributed and must not
be converted into a guessed joint correction.
