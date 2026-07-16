# Tail-Scale Family Closure

Date: 2026-07-16 (America/New_York)

Status: `CLOSE_TAIL_SCALE_FAMILY_NO_PERSISTENT_WINNER`

Phase A was already evidence-complete before this program began. The recovered
tracking-tail archive is 24,480,277 bytes with SHA-256
`ae4c631a6ce1c0b36c3231113740acc6c1b8a463c0911ce7cad30b8f8d8ca60f`.
The hosted manifest passes, the session was stopped, and all 36 preregistered
CPU behavior cells are present.

All half/final checkpoints completed 600 ticks with bilateral transitions,
zero saturation and zero measured rate excess. None passes the unchanged
tracking threshold at both checkpoints:

| arm | half worst p95 (rad) | final worst p95 (rad) | persistent pass |
|---|---:|---:|---|
| T1_QUARTER | .22883 | .23242 | no |
| T2_EQUAL | .21505 | .20972 | no |
| T3_FOUR | .22048 | .20410 | no |

Decision: the tail-scale family is closed. T1/T2/T3 were the complete frozen
scalar family for this defect. A fourth scale, checkpoint cherry-pick, relaxed
tracking threshold, or reward-based selection is forbidden. The Phase-A pass
fork (x=0 evaluation and command-support-extension preregistration) is not
entered because no arm passed persistence.

This closure spends no new compute and authorizes only the requested CPU-only
contract-closure and viability-prevention program. Robot, RDK-X5, GPU/iGPU,
deployment and clearance remain blocked; robot clearance is `NO`.

