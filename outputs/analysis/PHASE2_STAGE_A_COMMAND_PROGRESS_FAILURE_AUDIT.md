# Stage A Command-Progress Failure Audit

Date: 2026-07-11

Status: **ONE-FACTOR OBJECTIVE HYPOTHESIS SUPPORTED**

The existing default-off positive-command progress-failure termination was
audited at exactly 30 ticks and ratio 0.25 on the 64 saved canonical-reset
x=0.08 baseline traces.

- 4/18 falls occurred before tick 30 and were already terminated physically;
- among the remaining traces, the condition flagged 13/14 later falls;
- it flagged 28/29 eventual low-forward-progress holds;
- it flagged 1/10 eventual tracking holds;
- it flagged 1/7 eventual passes (seed 55 at ratio 0.249, just below cutoff).

Thus the frozen condition targets 41/43 measured fall-or-low-progress episodes
that survive to tick 30, with two false-positive non-low-progress outcomes. It
is evaluated only for nonzero commands in the environment implementation, so
x=0 standing episodes are not terminated by this rule.

This is a direct outcome-aligned training signal already present in the
environment, unlike the rejected diagnostic correlates and teacher actions.
