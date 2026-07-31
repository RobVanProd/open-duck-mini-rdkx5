# Winner-v3 Recurrent-Adapter Normalizer Count Correction — 2026-07-19

Decision: `PASS_READ_ONLY_NORMALIZER_COUNT_CORRECTION`

The initial contract's only failed check used the wrong persistent-checkpoint
count. The hash-bound T2_EQUAL 512K source count is `7,536,640`, not
`8,048,640`. The formal expanded checkpoint contains exactly the source count,
64 zero means, 64 unit standard deviations, and 64 summed-variance values of
`7,536,640`. Every formal artifact hash and every other initial contract
check remains exact. The CPU smoke was not rerun.

The corrected contract decision is
`PASS_WINNER_V3_RECURRENT_ADAPTER_CPU_CONTRACT`. This corrects bookkeeping
only and grants no behavior, runtime, hardware, deployment, or robot clearance.
