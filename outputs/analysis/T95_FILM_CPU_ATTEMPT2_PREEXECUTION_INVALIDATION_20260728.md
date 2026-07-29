# T95 FiLM CPU attempt 2 preexecution invalidation

Status: `INVALID_T95_FILM_CPU_ATTEMPT2_PREEXECUTION`

The composed prefix wrapper still pinned the older V22 calibrator while T95
and its T94 causal evidence pin the V96 universal calibrator. The process
stopped after one environment construction and before reset: zero simulator
ticks, optimizer steps, behavior cells, hosted compute units, or robot/RDK-X5
accesses occurred.

The correction uses a T95-specific wrapper pinned to the exact V96 hash,
recomposes into a fresh source root, and rebuilds step-zero assets. It changes
no policy mechanism, training parameter, threshold, or decision rule.
