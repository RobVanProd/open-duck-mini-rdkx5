# T95 FiLM CPU attempt 1 preexecution invalidation

Status: `INVALID_T95_FILM_CPU_ATTEMPT1_PREEXECUTION`

The runner stopped before environment construction because its identity
recomputation omitted the already-frozen `architecture_contract` field.
There were zero optimizer steps, simulator behavior cells, hosted compute
units, and robot/RDK-X5 accesses.

The V2 correction includes that field in the identity recomputation and
refreshes the runner receipt. It changes no mechanism, input, threshold, or
decision rule.
